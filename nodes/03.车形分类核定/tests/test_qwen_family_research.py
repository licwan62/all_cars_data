import json
import sys
import threading
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT.parents[1] / "lib"))
sys.path.insert(0, str(PROJECT / "code"))
import qwen_family_research as qwen
from cover_shape.family_cache import read_cache
from test_shape_family_research import env  # noqa: F401  复用临时源表/领取/缓存夹具

SOURCES = [{"index": 1, "title": "Spec", "url": "https://example.org/spec"}, {"index": 2, "title": "Photo", "url": "https://example.org/photo"}]
CONFIG = {"model": "qwen-test", "max_fix_attempts": 1, "market": "US", "base_url": "https://example.invalid"}


class FakeClient:
    def __init__(self, replies):
        self.replies, self.calls, self.usage = list(replies), [], Counter()

    def chat(self, messages, search):
        self.calls.append({"messages": [dict(m) for m in messages], "search": search})
        return self.replies.pop(0), SOURCES if search else []


def runner(replies, limit=None):
    instance = object.__new__(qwen.Runner)
    instance.config, instance.client = CONFIG, FakeClient(replies)
    instance.args = SimpleNamespace(limit=limit, verbose=False)
    instance.policy = {"long_span_years": 9, "max_samples_per_span": 2}
    instance.families = qwen.fam.load_records()
    instance.queue = {r["family_id"]: r for r in qwen.fam.queue_order()}
    instance.stats, instance.lock, instance.stop = Counter(), threading.Lock(), threading.Event()
    instance.skipped, instance.budget = set(), limit
    instance.log_path = qwen.LOG_DIR / "test.jsonl"
    instance.provider, instance.tavily = "dashscope", None
    return instance


class FakeTavily:
    def __init__(self):
        self.queries, self.usage = [], Counter()

    def search(self, query):
        self.queries.append(query)
        return [{"title": "Wiki", "url": "https://en.wikipedia.org/wiki/Test#History", "content": "fastback  roof"},
                {"title": "Brochure", "url": f"https://example.org/{len(self.queries)}", "content": "notchback"}]


def test_tavily_sources_are_numbered_in_prompt_and_builtin_search_off(env, monkeypatch, tmp_path):  # noqa: F811
    root, families = env
    monkeypatch.setattr(qwen, "LOG_DIR", tmp_path)
    run = runner([reply({"shape": "COMPACT_HATCH", "sample_years": [2012, 2017], "sources": [1, 3], "note": "x"})])
    run.provider, run.tavily = "tavily", FakeTavily()
    run.config = {**CONFIG, "search_provider": "tavily", "tavily": {"queries_per_family": 2}}
    fid = families["Hatchback"]
    entry = run.research(fid, run.queue[fid], run.families[fid], "qwen-dry-run", write=False)
    assert entry["outcome"] == "VALID_DRY_RUN" and len(run.tavily.queries) == 2
    assert [s["url"] for s in entry["sources"]] == ["https://en.wikipedia.org/wiki/Test", "https://example.org/1", "https://example.org/2"]
    call = run.client.calls[0]
    assert not call["search"] and "[3] Brochure | https://example.org/2" in call["messages"][-1]["content"]
    assert entry["rules"][0]["source_url"] == "https://en.wikipedia.org/wiki/Test; https://example.org/2"
    assert "Tavily 检索" in entry["rules"][0]["note"]


def test_no_tavily_results_is_reported_without_calling_model(env, monkeypatch, tmp_path):  # noqa: F811
    root, families = env
    run = runner([])
    run.provider, run.tavily = "tavily", SimpleNamespace(search=lambda q: [], usage=Counter())
    run.config = {**CONFIG, "search_provider": "tavily", "tavily": {}}
    fid = families["Hatchback"]
    assert run.research(fid, run.queue[fid], run.families[fid], "w", write=False)["outcome"] == "NO_SOURCES"
    assert not run.client.calls


def reply(*rules):
    return "```json\n" + json.dumps({"rules": list(rules)}, ensure_ascii=False) + "\n```"


def test_extract_json_and_source_mapping():
    answer = qwen.extract_json("说明文字 " + reply({"shape": "COMPACT_HATCH", "sample_years": [2012], "sources": [2, 9], "note": "x"}))
    items = qwen.to_items("f:1", answer, SOURCES, CONFIG)
    assert items[0]["source_url"] == ["https://example.org/photo"] and "千问 qwen-test" in items[0]["note"]
    with pytest.raises(ValueError, match="检索来源"):
        qwen.to_items("f:1", {"rules": [{"shape": "WAGON", "sources": [], "urls": ["https://made.up"]}]}, SOURCES, CONFIG)
    with pytest.raises(ValueError, match="JSON"):
        qwen.extract_json("没有 JSON")


def test_worker_fixes_invalid_reply_then_applies(env, monkeypatch, tmp_path):  # noqa: F811
    root, families = env
    monkeypatch.setattr(qwen, "LOG_DIR", tmp_path)
    monkeypatch.setattr(qwen, "SKIPS", tmp_path / "skipped.jsonl")
    monkeypatch.setattr(qwen, "EVIDENCE", tmp_path / "family_evidence.jsonl")
    partial = reply({"generation": "gen1", "shape": "COMPACT_HATCH", "sample_years": [2012], "sources": [1], "note": "一代"})
    full = reply({"shape": "COMPACT_HATCH", "sample_years": [2012, 2017], "sources": [1, 2], "note": "两代同形"})
    run = runner([partial, full], limit=1)
    run.worker_loop(1)
    rules = read_cache(root / "family_cache.csv")
    assert run.stats == Counter(APPLIED=1) and len(rules) == 1
    assert rules[0]["worker"] == "qwen-family-1" and rules[0]["source_url"] == "https://example.org/spec; https://example.org/photo"
    assert run.client.calls[0]["search"] and not run.client.calls[1]["search"]
    assert "尚未覆盖 1 条" in run.client.calls[1]["messages"][-1]["content"] and not qwen.fam.read_claims()
    evidence = [json.loads(line) for line in (tmp_path / "family_evidence.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(evidence) == 1 and evidence[0]["rules"][0]["shape"] == "COMPACT_HATCH" and evidence[0]["sources"][0]["url"]


def test_invalid_family_is_skipped_and_released(env, monkeypatch, tmp_path):  # noqa: F811
    root, families = env
    monkeypatch.setattr(qwen, "LOG_DIR", tmp_path)
    monkeypatch.setattr(qwen, "SKIPS", tmp_path / "skipped.jsonl")
    bad = reply({"shape": "Hatchback", "sample_years": [2012], "sources": [1], "note": "非法标签"})
    run = runner([bad, bad], limit=1)
    run.worker_loop(1)
    assert run.stats == Counter(INVALID=1) and not (root / "family_cache.csv").exists()
    assert families["Hatchback"] in run.skipped and not qwen.fam.read_claims()
    assert json.loads((tmp_path / "skipped.jsonl").read_text(encoding="utf-8"))["family_id"] == families["Hatchback"]


def test_tavily_cache_reuses_results_without_request(tmp_path, monkeypatch):
    client = qwen.TavilyClient({"api_key": "tvly-test", "cache_file": str(tmp_path / "cache.jsonl")})
    calls = []
    monkeypatch.setattr(client, "_request", lambda body: calls.append(body) or [{"url": "https://a.example", "title": "A"}])
    assert client.search("q")[0]["url"] == "https://a.example" and client.search("q") and len(calls) == 1
    again = qwen.TavilyClient({"api_key": "tvly-test", "cache_file": str(tmp_path / "cache.jsonl")})
    monkeypatch.setattr(again, "_request", lambda body: calls.append(body) or [])
    assert again.search("q")[0]["url"] == "https://a.example" and len(calls) == 1 and again.usage["cache_hits"] == 1
