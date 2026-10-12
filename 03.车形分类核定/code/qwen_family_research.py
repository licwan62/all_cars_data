"""用千问 API 推进车型族 SHAPE 研究：领取车型族 → 联网检索抽样年份 → 生成规则 → 校验写入 family_cache.csv。

与 codex 研究（run_shape_family_research.ps1）共用领取表与校验：每路并发使用独立 worker 名 qwen-family-N，
可与 codex worker 同时运行。连接参数在配置文件（默认 research_queue/qwen_config.yaml，样例同目录
qwen_config.example.yaml）；密钥默认取环境变量，不写入日志。来源 URL 只取检索返回的结果，不接受模型编造。

    python code/qwen_family_research.py --dry-run --families f:ad9d43ead9864400f181   # 只看结论不写入
    python code/qwen_family_research.py --limit 50                                    # 研究 50 个族
    python code/qwen_family_research.py                                               # 一直跑到没有可领取的族
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shape_family_research as fam
from cover_shape.family_cache import family_id, natural, read_cache, sample_years
from cover_shape.family_cache import haystack as fam_haystack

PROJECT = fam.PROJECT
DEFAULT_CONFIG = PROJECT / "research_queue/qwen_config.yaml"
LOG_DIR = PROJECT / "work/qwen_runner"
SKIPS = LOG_DIR / "skipped.jsonl"
TAVILY_CACHE = PROJECT / "cache/tavily/search_cache.jsonl"
# 写入规则的车型族同时留存检索证据（来源摘要 + 模型回复），随 data/ 版本化，供以后新规则离线复判。
EVIDENCE = fam.DATA / "family_evidence.jsonl"
LABELS = """\
LOW_FASTBACK 低矮车身，车顶后部长而连续地下降到车尾
LOW_NOTCHBACK 低矮车身，后窗之后有明显独立尾箱台阶
SPORT_LIFTBACK 运动化乘员舱，倾斜的掀背/溜背尾门
STANDARD_SEDAN 常规三厢比例，明显行李厢
COMPACT_HATCH 车长较短、车头短、乘员舱较高、尾部短
TALL_BOX 高且长的车顶、尾部近乎直立（厢式车、MPV、Kia Soul 类）
WAGON 长车顶、载物舱连续延伸、尾部较直立的旅行车
SLOPED_CROSSOVER 较高车体、车顶向车尾倾斜的跨界/轿跑 SUV
BOXY_SUV 较高车体、直立车尾、长而高的车顶
PICKUP 独立驾驶室 + 开放货箱
OTHER 以上都不合适"""

SYSTEM_PROMPT = f"""你是汽车外形研究员，为车罩外形分类研究一个“车型族”（同市场、同品牌车型、同车身结构）。
按原厂侧面轮廓（车顶、尾部、座舱比例）分类，不要按车身类型名称直接映射。可选标签：
{LABELS}

工作方式：
- 不要逐年研究。每个代际只看给出的抽样年份（通常一个就够；仅在改款可能改变车顶/车尾时看第二个）。
- 多个代际外形同属一类时，写一条不带 generation 的规则即可覆盖；外形确实变化时才按 generation、年份（year_start/year_end）
  或版本（match_pattern）拆分。代际用 generation 字段（填记录里的 GEN 值），年份用 year_start/year_end；
  match_pattern 只用于区分同代内的版本（如 VERSION=SportsRoof），不要在其中写 GEN 或 STRUCTURE。
  match_pattern 是正则，匹配文本形如 "ID | MAKE= | MODEL= | VERSION= | STRUCTURE= | YEAR= | CAB= | BED= | GEN="。
- 车身结构已固定为给出的结构（如 Sedan 就是三厢版），不要按同名车型其他车身版本（掀背、旅行版）判断。
- 规则必须覆盖列出的每一条记录；sample_years 填你实际依据的年份，且必须落在该规则覆盖的记录年份内。
- 证据不完美时也给出合理判断，在 note 中说明；后部形态介于两类之间时用 alternates 给出备选。
- sources 只能填检索结果的编号（如 [1,3]），不得编造网址。

只输出一个 JSON 对象，不要其他文字：
{{"rules": [{{"generation": "", "year_start": "", "year_end": "", "match_pattern": "", "shape": "LABEL",
  "alternates": [], "sample_years": [2019], "sources": [1], "note": "简短中文依据"}}]}}"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class FatalApiError(RuntimeError):
    """鉴权/配置类错误，所有并发路立即停止。"""


class QwenClient:
    def __init__(self, config: dict):
        self.config = config
        self.style = config.get("api_style", "dashscope")
        if self.style not in {"dashscope", "openai"}:
            raise SystemExit(f"api_style 只能是 dashscope 或 openai：{self.style}")
        if str(config.get("api_key_env", "")).startswith("sk-"):
            raise SystemExit("api_key_env 应填环境变量名（如 DASHSCOPE_API_KEY），密钥请写在 api_key 或该环境变量里")
        self.key = config.get("api_key") or os.environ.get(config.get("api_key_env", "DASHSCOPE_API_KEY"), "")
        if not self.key:
            raise SystemExit(f"缺少 API 密钥：请设置环境变量 {config.get('api_key_env', 'DASHSCOPE_API_KEY')}，或在本地 qwen_config.yaml 写 api_key")
        self.usage = Counter()
        self._usage_lock = threading.Lock()

    def chat(self, messages: list[dict], search: bool) -> tuple[str, list[dict]]:
        """返回 (回复文本, 检索来源[{index,title,url,site_name}])。"""
        c = self.config
        base = c["base_url"].rstrip("/")
        if self.style == "dashscope":
            # 推理模型默认深度思考，单个车型族可耗时 5 分钟以上并触发超时重试；默认关闭。
            parameters = {"result_format": "message", "temperature": c.get("temperature", 0.2),
                          "enable_thinking": bool(c.get("enable_thinking", False))}
            if search and c.get("enable_search", True):
                parameters.update(enable_search=True, search_options={
                    "forced_search": bool(c.get("forced_search", True)), "enable_source": True,
                    "search_strategy": c.get("search_strategy", "turbo")})
            data = self._dashscope(base, messages, parameters)
        else:
            url = base + "/chat/completions"
            body = {"model": c["model"], "messages": messages, "temperature": c.get("temperature", 0.2),
                    **((c.get("extra_body") or {}) if search else {})}
            data = self._post(url, body)
        if self.style == "dashscope":
            output = data.get("output", {})
            text = output["choices"][0]["message"]["content"]
            sources = (output.get("search_info") or {}).get("search_results") or []
            usage = data.get("usage", {})
            tokens = (usage.get("input_tokens", 0), usage.get("output_tokens", 0))
        else:
            text = data["choices"][0]["message"]["content"]
            sources = (data.get("search_info") or {}).get("search_results") or []
            usage = data.get("usage", {})
            tokens = (usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
        with self._usage_lock:
            self.usage.update(requests=1, input_tokens=tokens[0], output_tokens=tokens[1])
        if isinstance(text, list):  # 多模态格式
            text = "".join(part.get("text", "") for part in text if isinstance(part, dict))
        return text, [s for s in sources if s.get("url")]

    def _dashscope(self, base: str, messages: list[dict], parameters: dict) -> dict:
        """百炼原生接口：较新的千问模型（如 qwen3.x）只走多模态路径。dashscope_endpoint=auto 时先试文本路径，
        收到 url error 后改走多模态并记住；也可在配置中直接指定 text / multimodal。"""
        with self._usage_lock:
            if not hasattr(self, "endpoint"):
                self.endpoint = self.config.get("dashscope_endpoint", "auto")
            endpoint = self.endpoint
        if endpoint in ("auto", "text"):
            try:
                body = {"model": self.config["model"], "input": {"messages": messages}, "parameters": parameters}
                data = self._post(base + "/api/v1/services/aigc/text-generation/generation", body)
                with self._usage_lock:
                    self.endpoint = "text"
                return data
            except RuntimeError as error:
                if endpoint == "text" or "url error" not in str(error):
                    raise
                with self._usage_lock:
                    self.endpoint = "multimodal"
        multimodal = [{"role": m["role"], "content": m["content"] if isinstance(m["content"], list) else [{"text": m["content"]}]}
                      for m in messages]
        body = {"model": self.config["model"], "input": {"messages": multimodal}, "parameters": parameters}
        return self._post(base + "/api/v1/services/aigc/multimodal-generation/generation", body)

    def _post(self, url: str, body: dict) -> dict:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        attempts = int(self.config.get("max_retries", 4)) + 1
        for attempt in range(attempts):
            request = urllib.request.Request(url, data=payload, method="POST", headers={
                "Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(request, timeout=float(self.config.get("timeout_seconds", 180))) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                detail = error.read().decode("utf-8", "replace")[:500]
                if error.code in (401, 403, 404):
                    raise FatalApiError(f"HTTP {error.code}: {detail}") from None
                if error.code == 400:  # 单个请求内容问题（如内容审核），只影响当前车型族
                    raise RuntimeError(f"HTTP 400: {detail}") from None
                reason = f"HTTP {error.code}: {detail}"
            except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
                reason = f"{type(error).__name__}: {error}"
            if attempt + 1 < attempts:
                time.sleep(min(60, 2 ** attempt * 3))
        raise RuntimeError(f"请求失败（已重试 {attempts - 1} 次）：{reason}")


def extract_json(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else text[text.find("{"): text.rfind("}") + 1]
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise ValueError(f"回复不是合法 JSON：{error}") from None
    if not isinstance(value, dict) or not isinstance(value.get("rules"), list) or not value["rules"]:
        raise ValueError('JSON 必须是 {"rules": [...]} 且至少一条规则')
    return value


def family_prompt(target: dict, pending: list[dict], policy: dict) -> str:
    by_generation = defaultdict(list)
    for record in pending:
        by_generation[record.get("generation", "")].append(record)
    lines = [f"车型族：{target['market']} 市场 {target['make']} {target['model']}，车身结构 {target['body_type']}", "", "代际与建议抽样年份："]
    for generation, items in sorted(by_generation.items(), key=lambda item: natural(item[0])):
        span = sorted({y for r in items for y in r["covered_years"]})
        lines.append(f"- GEN={generation or '(空)'}：{span[0]}-{span[-1]}，抽样 {sample_years(span, policy)}，{len(items)} 条")
    lines += ["", "需覆盖的记录（ID | 代际 | 版本 | CAB | BED | 长x宽x高 mm）："]
    for record in pending:
        dims = "x".join("?" if record.get(k) is None else str(round(record[k])) for k in ("length_mm", "width_mm", "height_mm"))
        lines.append(" | ".join([record["source_record_id"], f"GEN={record.get('generation', '')}", f"VERSION={record.get('trim', '')}",
                                 f"CAB={record['CAB']}", f"BED={record['BED']}", dims]))
    return "\n".join(lines)


def sources_text(sources: list[dict]) -> str:
    return "\n".join(f"[{s.get('index')}] {s.get('title', '')} {s['url']}" for s in sources) or "（无检索结果）"


def to_items(fid: str, answer: dict, sources: list[dict], config: dict) -> list[dict]:
    """模型规则 → apply 条目；来源编号映射为检索 URL。"""
    by_index = {int(s["index"]): s["url"] for s in sources if str(s.get("index", "")).isdigit()}
    items = []
    for number, rule in enumerate(answer["rules"], 1):
        cited = rule.get("sources") or []
        urls = [by_index[int(i)] for i in cited if str(i).isdigit() and int(i) in by_index]
        note = str(rule.get("note", "")).strip()
        if not urls and not by_index and config.get("allow_unverified_urls") and rule.get("urls"):
            urls = [str(u) for u in rule["urls"] if str(u).startswith("http")]
            note += "（来源由模型给出，未经检索核对）"
        if not urls:
            raise ValueError(f"第 {number} 条规则没有引用有效的检索来源编号（可用编号：{sorted(by_index) or '无'}）")
        items.append({"family_id": fid, "generation": rule.get("generation", ""), "year_start": rule.get("year_start", ""),
                      "year_end": rule.get("year_end", ""), "match_pattern": rule.get("match_pattern", ""),
                      "shape": rule.get("shape", ""), "alternates": rule.get("alternates") or [],
                      "sample_years": rule.get("sample_years") or [], "source_url": urls,
                      "note": f"{note}（千问 {config["model"]} + {"Tavily" if config.get("search_provider") == "tavily" else "百炼"} 检索）"})
    return items


class TavilyClient:
    """Tavily 搜索 REST API（https://api.tavily.com/search）：英文网页检索，返回真实 URL 与摘要。"""

    def __init__(self, config: dict):
        self.config = config
        env_name = str(config.get("api_key_env", "TAVILY_API_KEY"))
        if env_name.startswith("tvly-"):  # 密钥误填在变量名处：不回显内容
            raise SystemExit("tavily.api_key_env 应填环境变量名（如 TAVILY_API_KEY），密钥请写在 tavily.api_key")
        self.key = config.get("api_key") or os.environ.get(env_name, "")
        if not self.key:
            raise SystemExit("缺少 Tavily 密钥：请设置 tavily.api_key_env 指定的环境变量，或在本地 qwen_config.yaml 的 tavily.api_key 填写")
        self.usage = Counter()
        self._lock = threading.Lock()
        # 本地搜索缓存：相同请求直接复用结果，重跑/新规则复判不再消耗额度。
        self.cache_path = Path(config.get("cache_file") or TAVILY_CACHE)
        self.cache = {}
        if self.cache_path.is_file():
            for line in self.cache_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    self.cache[item["key"]] = item["results"]

    def search(self, query: str) -> list[dict]:
        body = {"query": query, "search_depth": self.config.get("search_depth", "basic"),
                "max_results": int(self.config.get("max_results", 6)), "include_answer": False}
        if self.config.get("include_domains"):
            body["include_domains"] = list(self.config["include_domains"])
        if self.config.get("exclude_domains"):
            body["exclude_domains"] = list(self.config["exclude_domains"])
        key = json.dumps(body, sort_keys=True, ensure_ascii=False)
        with self._lock:
            if key in self.cache:
                self.usage.update(cache_hits=1)
                return self.cache[key]
        results = self._request(body)
        with self._lock:
            self.cache[key] = results
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with self.cache_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"key": key, "query": query, "at": utc_now(), "results": results}, ensure_ascii=False) + "\n")
        return results

    def _request(self, body: dict) -> list[dict]:
        attempts = int(self.config.get("max_retries", 3)) + 1
        for attempt in range(attempts):
            request = urllib.request.Request("https://api.tavily.com/search", method="POST",
                                             data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                             headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(request, timeout=float(self.config.get("timeout_seconds", 60))) as response:
                    data = json.loads(response.read().decode("utf-8"))
                with self._lock:
                    self.usage.update(searches=1)
                return [r for r in data.get("results", []) if r.get("url")]
            except urllib.error.HTTPError as error:
                detail = error.read().decode("utf-8", "replace")[:300]
                if error.code in (400, 401, 403, 432, 433):  # 参数/鉴权/额度用尽：不重试
                    raise FatalApiError(f"Tavily HTTP {error.code}: {detail}") from None
                reason = f"Tavily HTTP {error.code}: {detail}"
            except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
                reason = f"{type(error).__name__}: {error}"
            if attempt + 1 < attempts:
                time.sleep(min(30, 2 ** attempt * 2))
        raise RuntimeError(f"Tavily 请求失败：{reason}")


def search_queries(target: dict, pending: list[dict], policy: dict, limit: int) -> list[str]:
    """英文检索词：整个车型族一条，再按代际抽样年份补充，总数不超过 limit。"""
    years = sorted({y for r in pending for y in r["covered_years"]})
    name = f"{target['make']} {target['model']} {target['body_type']}"
    queries = [f"{name} generations history body style side profile {years[0]}-{years[-1]}"]
    by_generation = defaultdict(list)
    for record in pending:
        by_generation[record.get("generation", "")].append(record)
    for _, items in sorted(by_generation.items(), key=lambda item: natural(item[0])):
        span = sorted({y for r in items for y in r["covered_years"]})
        sample = sample_years(span, policy)[0]
        queries.append(f"{sample} {name} side view roofline rear design")
    return queries[:max(1, limit)]


def gather_sources(tavily: TavilyClient, queries: list[str], snippet_chars: int) -> list[dict]:
    seen, sources = set(), []
    for query in queries:
        for result in tavily.search(query):
            url = result["url"].split("#")[0]
            if url in seen:
                continue
            seen.add(url)
            sources.append({"index": len(sources) + 1, "title": result.get("title", ""), "url": url,
                            "snippet": re.sub(r"\s+", " ", result.get("content", ""))[:snippet_chars], "query": query})
    return sources


class Runner:
    def __init__(self, config: dict, args):
        self.config, self.args = config, args
        self.client = QwenClient(config)
        self.provider = config.get("search_provider", "dashscope")
        if self.provider not in {"dashscope", "tavily"}:
            raise SystemExit(f"search_provider 只能是 dashscope 或 tavily：{self.provider}")
        self.tavily = TavilyClient(config.get("tavily") or {}) if self.provider == "tavily" else None
        self.policy = yaml.safe_load((fam.DATA / "research_queue.yaml").read_text(encoding="utf-8"))
        self.families = fam.load_records()
        self.queue = {r["family_id"]: r for r in fam.queue_order()}
        self.stats = Counter()
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.skipped = self._read_skips() if not args.retry_skipped else set()
        self.budget = args.limit
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.log_path = LOG_DIR / f"log-{datetime.now():%Y%m%d}.jsonl"

    def _read_skips(self) -> set[str]:
        if not SKIPS.is_file():
            return set()
        return {json.loads(line)["family_id"] for line in SKIPS.read_text(encoding="utf-8").splitlines() if line.strip()}

    def _log(self, entry: dict) -> None:
        with self.lock, self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _record_evidence(self, target: dict, entry: dict, rules: list[dict], reply: str) -> None:
        keep = ("generation", "year_start", "year_end", "match_pattern", "shape", "alternates", "sample_years", "source_url", "note")
        record = {"family_id": entry["family_id"], **{k: target[k] for k in ("market", "make", "model", "body_type")},
                  "researched_at": utc_now(), "worker": entry["worker"], "llm_model": self.config["model"],
                  "search_provider": self.provider, "queries": entry.get("queries", []),
                  "sources": [{k: s.get(k, "") for k in ("index", "title", "url", "snippet")} for s in entry.get("sources", [])],
                  "rules": [{k: r[k] for k in keep} for r in rules], "reply": reply}
        with fam.lock(), EVIDENCE.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _take_budget(self) -> bool:
        with self.lock:
            if self.budget is None:
                return True
            if self.budget <= 0:
                return False
            self.budget -= 1
            return True

    def research(self, fid: str, target: dict, pending: list[dict], worker: str, write: bool) -> dict:
        """研究一个车型族；校验失败时把错误反馈给模型修正。返回日志条目。"""
        prompt = family_prompt(target, pending, self.policy)
        entry = {"family_id": fid, "family": f"{target['market']} {target['make']} {target['model']} {target['body_type']}",
                 "worker": worker, "model": self.config["model"], "search_provider": self.provider, "started_at": utc_now(), "turns": []}
        sources = []
        if self.tavily is not None:
            # 先用英文网页检索，结果编号后随提示提供；模型只引用编号，不再使用百炼内置搜索。
            options = self.config.get("tavily") or {}
            queries = search_queries(target, pending, self.policy, int(options.get("queries_per_family", 3)))
            sources = gather_sources(self.tavily, queries, int(options.get("snippet_chars", 500)))
            entry.update(queries=queries, sources=sources)
            if not sources:
                entry["outcome"] = "NO_SOURCES"
                return entry
            prompt += "\n\n检索结果（sources 只能引用这些编号）：\n" + "\n".join(
                f"[{s['index']}] {s['title']} | {s['url']}\n    {s['snippet']}" for s in sources)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
        for turn in range(int(self.config.get("max_fix_attempts", 2)) + 1):
            started = time.monotonic()
            text, found = self.client.chat(messages, search=(turn == 0 and self.tavily is None))
            if turn == 0 and self.tavily is None:
                sources = found
                entry["sources"] = sources
            entry["turns"].append({"reply": text, "seconds": round(time.monotonic() - started, 1)})
            if self.args.verbose:
                print(f"  [{worker}] {entry['family']} 第{turn + 1}轮 {entry['turns'][-1]['seconds']}s 来源{len(sources)}", flush=True)
            try:
                items = to_items(fid, extract_json(text), sources, self.config)
                fresh = fam.build_rules(items, {fid: target}, worker, utc_now())
                if write:
                    fam.apply_items(items, worker, self.families)
                    self._record_evidence(target, entry, fresh, text)
                else:
                    others = [r for r in read_cache(fam.CACHE) if family_id(r) != fid]
                    fam.verify_rules(fresh, others, {fid}, self.families)
                entry.update(outcome="APPLIED" if write else "VALID_DRY_RUN", rules=fresh)
                return entry
            except (ValueError, SystemExit) as error:
                message = str(error)
                entry["turns"][-1]["error"] = message
                if self.args.verbose:
                    print(f"  [{worker}] 校验未通过：{message[:200]}", flush=True)
                examples = "\n".join(fam_haystack(r) for r in pending[:3])
                if "冲突" in message:
                    message += "\n（同一条记录被两条同样具体的规则命中且分类不同：请合并成一条，或用不重叠的年份/版本把范围分开；版本例外规则加 match_pattern 会自动优先。）"
                messages += [{"role": "assistant", "content": text},
                             {"role": "user", "content": f"校验未通过：{message}\n\nmatch_pattern 的实际匹配文本示例：\n{examples}\n\n"
                                                         f"可引用的检索来源：\n{sources_text(sources)}\n\n"
                                                         "请修正后重新输出完整 JSON（覆盖全部记录，sources 只用上述编号）。"}]
        entry["outcome"] = "INVALID"
        return entry

    def worker_loop(self, index: int) -> None:
        worker = f"qwen-family-{index}"
        fam.release(worker)  # 清理上次中断残留的同名领取
        while not self.stop.is_set() and self._take_budget():
            chosen = fam.claim_families(1, worker, [self.config.get("market", "US")], self.families, exclude=self.skipped)
            if not chosen:
                break
            row, _, pending = chosen[0]
            fid = row["family_id"]
            try:
                entry = self.research(fid, row, pending, worker, write=True)
            except FatalApiError as error:
                fam.release(worker)
                self.stop.set()
                print(f"[{worker}] 接口错误，全部停止：{error}", flush=True)
                return
            except Exception as error:  # 网络重试耗尽等：释放领取，留待下次
                fam.release(worker)
                entry = {"family_id": fid, "worker": worker, "outcome": "ERROR", "error": f"{type(error).__name__}: {error}"}
            if entry["outcome"] != "APPLIED":
                fam.release(worker)
                if entry["outcome"] in ("INVALID", "NO_SOURCES"):
                    with self.lock:
                        self.skipped.add(fid)
                        with SKIPS.open("a", encoding="utf-8") as handle:
                            handle.write(json.dumps({"family_id": fid, "at": utc_now(), "family": entry.get("family", "")}, ensure_ascii=False) + "\n")
            self._log({**entry, "finished_at": utc_now()})
            with self.lock:
                self.stats[entry["outcome"]] += 1
            shapes = ",".join(sorted({r["shape"] for r in entry.get("rules", [])}))
            print(f"[{worker}] {entry.get('family', fid)} -> {entry['outcome']} {shapes}", flush=True)

    def run(self) -> None:
        concurrency = max(1, int(self.args.concurrency or self.config.get("concurrency", 6)))
        print(f"千问研究：模型 {self.config['model']}，并发 {concurrency}，市场 {self.config.get('market', 'US')}", flush=True)
        with ThreadPoolExecutor(concurrency) as pool:
            for future in [pool.submit(self.worker_loop, i) for i in range(1, concurrency + 1)]:
                future.result()
        print(json.dumps({"results": self.stats, "usage": self.client.usage, "tavily": self.tavily.usage if self.tavily else {}}, ensure_ascii=False), flush=True)
        if self.stop.is_set():
            raise SystemExit(2)

    def dry_run(self, fids: list[str]) -> None:
        """不领取、不写入：研究指定车型族全部记录，并与现有缓存结论对照。"""
        existing = defaultdict(list)
        for rule in read_cache(fam.CACHE):
            existing[family_id(rule)].append(rule)
        for fid in fids:
            row, records = self.queue.get(fid), self.families.get(fid)
            if not row or not records:
                print(f"{fid}: 不在当前队列/源表中")
                continue
            entry = self.research(fid, row, records, "qwen-dry-run", write=False)
            self._log({**entry, "dry_run": True, "finished_at": utc_now()})
            print(f"\n== {entry['family']} -> {entry['outcome']}")
            for rule in entry.get("rules", []):
                print(f"  qwen  {rule['generation'] or '*'} {rule['year_start']}-{rule['year_end']} {rule['match_pattern']} -> "
                      f"{rule['shape']} alt={rule['alternates']} 抽样={rule['sample_years']} | {rule['note'][:80]}")
            for rule in existing.get(fid, []):
                print(f"  cache {rule['generation'] or '*'} {rule['year_start']}-{rule['year_end']} {rule['match_pattern']} -> "
                      f"{rule['shape']} ({rule['worker']})")
            if entry["outcome"] == "INVALID":
                print("  最后错误：" + entry["turns"][-1].get("error", ""))
        print(json.dumps({"usage": self.client.usage, "tavily": self.tavily.usage if self.tavily else {}}, ensure_ascii=False))


def load_config(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"找不到配置 {path}；请复制 research_queue/qwen_config.example.yaml 为 qwen_config.yaml 后修改")
    config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    missing = [k for k in ("base_url", "model") if not config.get(k)]
    if missing:
        raise SystemExit(f"配置缺少 {missing}")
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--limit", type=int, help="本次最多研究的车型族数；默认直到没有可领取的族")
    parser.add_argument("--concurrency", type=int, help="覆盖配置中的并发数")
    parser.add_argument("--model", help="覆盖配置中的模型")
    parser.add_argument("--dry-run", action="store_true", help="只研究 --families 指定的族并打印结论，不领取不写入")
    parser.add_argument("--families", nargs="+", default=[], help="dry-run 研究的 family_id")
    parser.add_argument("--retry-skipped", action="store_true", help="重新研究以前校验失败而跳过的族")
    parser.add_argument("--verbose", action="store_true", help="打印每轮请求耗时与来源数")
    args = parser.parse_args()
    if args.limit is not None and args.limit <= 0:
        parser.error("--limit 必须为正数")
    config = load_config(args.config)
    if args.model:
        config["model"] = args.model
    runner = Runner(config, args)
    if args.dry_run:
        if not args.families:
            parser.error("--dry-run 需要 --families")
        runner.dry_run(args.families)
    else:
        runner.run()


if __name__ == "__main__":
    main()
