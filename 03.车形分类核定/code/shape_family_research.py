"""车型族 SHAPE 研究：领取车型族 → 抽样年份研究 → 批量写入 data/cover_shape/family_cache.csv。

参照旧车身研究缓存（shape_project.py claim/batch-update）：一次研究一个 市场/品牌/车型/结构 族，
每个代际只看少数年份；结论写成可按代际/年份/模式细分的缓存规则，整族继承。写完后运行
build_cover_shape_output.py 重建 output/COVER_SHAPE.csv 与研究队列。
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import threading
import time
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cover_shape.family_cache import (CACHE_FIELDS, FamilyCache, family_id, int_years, matches, natural, read_cache, sample_years,
                                      validate_rules, write_cache)
from cover_shape.ingest import normalize, read_table, years

SOURCE = ROOT / "02.分类结构审核/output/车型结构.csv"
DATA = PROJECT / "data/cover_shape"
CACHE = DATA / "family_cache.csv"
QUEUE = PROJECT / "output/shape_research_queue.jsonl"
SHAPES = PROJECT / "output/COVER_SHAPE.csv"
CLAIMS = PROJECT / "research_queue/family_claims.csv"
LOCK = PROJECT / "research_queue/.family_research.lock"
CLAIM_FIELDS = ["family_id", "market", "make", "model", "body_type", "worker", "claimed_at", "kind"]
REVIEW_PREFIX = "codex-review"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


_THREAD_LOCK = threading.RLock()


@contextmanager
def lock():
    """串行化并行 worker（进程间文件锁 + 进程内线程锁）对领取表和缓存的修改。"""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with _THREAD_LOCK, LOCK.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def read_claims() -> list[dict]:
    if not CLAIMS.is_file():
        return []
    with CLAIMS.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_claims(rows: list[dict]) -> None:
    temp = CLAIMS.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLAIM_FIELDS, lineterminator="\n", restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(CLAIMS)


def load_records() -> dict[str, list[dict]]:
    """按车型族归集上游记录（与正式构建相同的字段映射与年份展开）。"""
    mapping = yaml.safe_load((DATA / "column_map.yaml").read_text(encoding="utf-8"))
    _, source = read_table(SOURCE)
    families = defaultdict(list)
    for row in source:
        span = years(row, mapping)
        record = normalize([{**row, "YEAR": str(span[(len(span) - 1) // 2])}], mapping, "family-research")[0]
        record.update({"raw_fields": row, "covered_years": span, "CAB": row.get("CAB", ""), "BED": row.get("BED", "")})
        families[family_id(record)].append(record)
    return families


def uncovered(records: list[dict], cache: FamilyCache) -> list[dict]:
    return [r for r in records if cache.select(r)[1] != "same_market"]


def queue_order() -> list[dict]:
    from cover_shape.research_queue import read_queue
    queue = read_queue(QUEUE)
    if not queue:
        raise SystemExit("请先运行 python code/build_cover_shape_output.py 生成车型族研究队列")
    return queue


def describe(family: dict, records: list[dict], pending: list[dict]) -> str:
    by_generation = defaultdict(list)
    for record in pending:
        by_generation[record.get("generation", "")].append(record)
    policy = yaml.safe_load((DATA / "research_queue.yaml").read_text(encoding="utf-8"))
    parts = []
    for generation, items in sorted(by_generation.items(), key=lambda item: natural(item[0])):
        span = sorted({y for r in items for y in r["covered_years"]})
        parts.append(f"{generation or '-'}:{span[0]}-{span[-1]} 抽样{sample_years(span, policy)} {len(items)}条")
    return "\t".join([family["family_id"], family["market"], family["make"], family["model"], family["body_type"],
                      f"{len(pending)}/{len(records)}", "; ".join(parts)])


def claim(limit: int, worker: str, markets: list[str]) -> None:
    chosen = claim_families(limit, worker, markets)
    print("family_id\tmarket\tmake\tmodel\tbody_type\t待研究/记录\t代际:年份 抽样年 条数")
    for row, records, pending in chosen:
        print(describe(row, records, pending))


def claim_families(limit: int, worker: str, markets: list[str], families: dict | None = None,
                   exclude: set[str] = frozenset()) -> list[tuple[dict, list[dict], list[dict]]]:
    """按队列顺序领取未覆盖车型族；返回 (队列行, 全部记录, 未覆盖记录)。families 可复用以省去重复读源表。"""
    families = families if families is not None else load_records()
    with lock():
        cache = FamilyCache(read_cache(CACHE))
        claims = read_claims()
        taken = {c["family_id"] for c in claims}
        chosen = []
        for row in queue_order():
            fid = row["family_id"]
            if len(chosen) >= limit:
                break
            if fid in taken or fid in exclude or row["market"] not in markets or row["state"] == "BLOCKED_INPUT":
                continue
            records = families.get(fid, [])
            pending = uncovered(records, cache)
            if not pending:
                continue
            chosen.append((row, records, pending))
            claims.append({"family_id": fid, "market": row["market"], "make": row["make"], "model": row["model"],
                           "body_type": row["body_type"], "worker": worker, "claimed_at": now()})
        write_claims(claims)
    return chosen


SHAPE_VERSION_PATTERN = (r"fast\s*back|sports?\s*roof|notch\s*back|hatch|lift\s*back|sport\s*back|wagon|estate|touring|avant|"
                         r"shooting|hard\s*top|targa|\bgt\b|coupe|cabrio|swb|lwb|\blong\b|\bshort\b|\bel\b|\bmax\b|extended|"
                         r"\b[2-5]\s*-?\s*d(?:oo)?r\b|wide|narrow|svo")


def review_candidates(families: dict, min_versions: int = 2, pattern: str = SHAPE_VERSION_PATTERN) -> list[tuple[str, dict, list[str]]]:
    """待复核的多版本车型族：规则全部由千问写入、记录含 ≥min_versions 个不同版本（含空版本），
    且至少一个版本名暗示车顶/车尾/车长/门数/宽体差异（pattern）；排除全为 PICKUP 的族。"""
    import re
    shape_hint = re.compile(pattern, re.IGNORECASE)
    by_family = defaultdict(list)
    for rule in read_cache(CACHE):
        by_family[family_id(rule)].append(rule)
    result = []
    for fid, rules in by_family.items():
        if not all(r["worker"].startswith("qwen-family") for r in rules) or all(r["shape"] == "PICKUP" for r in rules):
            continue
        versions = sorted({r.get("trim", "") for r in families.get(fid, [])})
        if len(versions) >= min_versions and any(shape_hint.search(v) for v in versions):
            result.append((fid, rules[0], versions))
    result.sort(key=lambda item: (-len(item[2]), item[1]["make"], item[1]["model"], item[1]["body_type"]))
    return result


def write_review_list(path: Path, min_versions: int, pattern: str) -> None:
    candidates = review_candidates(load_records(), min_versions, pattern)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{fid}\t{r['make']} {r['model']} {r['body_type']}\t{'|'.join(v or '(空)' for v in versions)}\n"
                            for fid, r, versions in candidates), encoding="utf-8")
    print(f"已写入 {len(candidates)} 个待复核多版本车型族：{path}")


def review_state(list_path: Path) -> dict:
    listed = [line.split("\t")[0] for line in list_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    reviewed = {family_id(r) for r in read_cache(CACHE) if r["worker"].startswith(REVIEW_PREFIX)}
    claimed = {c["family_id"] for c in read_claims()}
    return {"listed": listed, "reviewed": reviewed, "claimed": claimed,
            "unclaimed": [fid for fid in listed if fid not in reviewed and fid not in claimed]}


def claim_review(limit: int, worker: str, list_path: Path) -> None:
    """按复核清单领取（即使已被缓存覆盖）；领取类型记为 review，records 会列出全部记录与现有规则。"""
    queue = {r["family_id"]: r for r in queue_order()}
    with lock():
        state = review_state(list_path)
        chosen = [fid for fid in state["unclaimed"] if fid in queue][:limit]
        claims = read_claims()
        claims += [{**{k: queue[fid][k] for k in ("market", "make", "model", "body_type")}, "family_id": fid,
                    "worker": worker, "claimed_at": now(), "kind": "review"} for fid in chosen]
        write_claims(claims)
    print("family_id\tmarket\tmake\tmodel\tbody_type\t(复核)")
    for fid in chosen:
        print("\t".join([fid, *(queue[fid][k] for k in ("market", "make", "model", "body_type"))]))


def compact_records(worker: str) -> None:
    """列出领取车型族中尚未被缓存覆盖的记录；复核领取则列出全部记录及待复核的现有规则。"""
    families = load_records()
    cache = FamilyCache(read_cache(CACHE))
    current = {}
    if SHAPES.is_file():
        _, rows = read_table(SHAPES)
        current = {r["DIMENSION-ID"]: r["SHAPE"] for r in rows}
    rules_by_family = defaultdict(list)
    for rule in cache.rules:
        rules_by_family[family_id(rule)].append(rule)
    for claim_row in read_claims():
        if claim_row["worker"] != worker:
            continue
        review = claim_row.get("kind") == "review"
        print(f"## {claim_row['family_id']} {claim_row['market']} {claim_row['make']} {claim_row['model']} {claim_row['body_type']}"
              + ("  [复核：整族重写]" if review else ""))
        if review:
            for rule in rules_by_family.get(claim_row["family_id"], []):
                print(f"  现有规则 GEN={rule['generation'] or '*'} {rule['year_start']}-{rule['year_end']} pattern={rule['match_pattern'] or '-'} "
                      f"-> {rule['shape']} alt={rule['alternates'] or '-'} 抽样={rule['sample_years']} | {rule['note'][:120]}")
        records = families.get(claim_row["family_id"], [])
        for record in (records if review else uncovered(records, cache)):
            dims = "x".join("?" if record.get(k) is None else str(round(record[k])) for k in ("length_mm", "width_mm", "height_mm"))
            print(" | ".join([record["source_record_id"], f"GEN={record.get('generation', '')}", f"VERSION={record.get('trim', '')}",
                              f"CAB={record['CAB']}", f"BED={record['BED']}", f"LxWxH_mm={dims}",
                              f"当前推断={current.get(record['source_record_id'], '')}"]))


def release(worker: str) -> None:
    with lock():
        claims = read_claims()
        kept = [c for c in claims if c["worker"] != worker]
        write_claims(kept)
    print(f"已释放 {len(claims) - len(kept)} 个 {worker} 的车型族领取")


def apply(path: Path, worker: str) -> None:
    rules, submitted = apply_items(json.loads(path.read_text(encoding="utf-8")), worker)
    print(f"已写入 {rules} 条规则，覆盖 {submitted} 个车型族；运行 python code/build_cover_shape_output.py 重建输出")


def apply_items(items: list, worker: str, families: dict | None = None) -> tuple[int, int]:
    """校验并写入一个 worker 全部领取车型族的规则；不合格时抛 SystemExit（消息可直接反馈给研究者）。"""
    if not isinstance(items, list) or not items:
        raise SystemExit("规则文件必须是非空 JSON 列表")
    families = families if families is not None else load_records()
    with lock():
        claims = {c["family_id"]: c for c in read_claims() if c["worker"] == worker}
        submitted = {str(item.get("family_id", "")) for item in items}
        if submitted != set(claims):
            raise SystemExit(f"提交车型族与领取不一致：缺少 {sorted(set(claims) - submitted)}，多出 {sorted(submitted - set(claims))}")
        # 与旧缓存 batch-update 一致：提交的车型族整族重写，旧规则不残留。
        others = [r for r in read_cache(CACHE) if family_id(r) not in submitted]
        fresh = build_rules(items, claims, worker, now())
        rules = verify_rules(fresh, others, submitted, families)
        write_cache(CACHE, rules)
        write_claims([c for c in read_claims() if c["family_id"] not in submitted])
    return len(fresh), len(submitted)


def build_rules(items: list, targets: dict, worker: str, stamp: str) -> list[dict]:
    """把研究者提交的条目转成缓存规则行；targets 为 family_id → 含 market/make/model/body_type 的身份。"""
    fresh = []
    for item in items:
        target = targets[item["family_id"]]
        alternates = item.get("alternates", [])
        fresh.append({**{k: "" for k in CACHE_FIELDS}, "market": target["market"], "make": target["make"], "model": target["model"],
                      "body_type": target["body_type"], "generation": str(item.get("generation", "") or ""),
                      "year_start": str(item.get("year_start", "") or ""), "year_end": str(item.get("year_end", "") or ""),
                      "match_pattern": str(item.get("match_pattern", "") or ""), "shape": str(item.get("shape", "")),
                      "alternates": ";".join(alternates) if isinstance(alternates, list) else str(alternates),
                      "sample_years": ";".join(str(y) for y in (item.get("sample_years") or [])),
                      "source_url": "; ".join(item["source_url"]) if isinstance(item.get("source_url"), list) else str(item.get("source_url", "")),
                      "note": str(item.get("note", "")), "worker": worker, "updated_at": stamp})
    return fresh


def verify_rules(fresh: list[dict], others: list[dict], submitted: set[str], families: dict) -> list[dict]:
    """不写盘的完整校验：抽样年份在范围内、规则合法无冲突、提交的车型族整族被覆盖。返回合并后的全部规则。"""
    # 研究过的年份必须落在该规则实际覆盖的记录内，避免拿其他代际/结构的资料冒充。
    for rule in fresh:
        scoped = [r for r in families[family_id(rule)] if matches(rule, r)]
        if not scoped:
            raise SystemExit(f"规则没有匹配任何记录：{json.dumps(rule, ensure_ascii=False)}")
        covered = {y for r in scoped for y in r["covered_years"]}
        outside = [y for y in int_years(rule["sample_years"]) if y not in covered]
        if outside:
            raise SystemExit(f"sample_years {outside} 不在规则覆盖年份内：{rule['make']} {rule['model']} {rule['generation']}")
    rules = others + fresh
    try:
        validate_rules(rules)
        cache = FamilyCache(rules)
        missing = [r["source_record_id"] for fid in submitted for r in uncovered(families[fid], cache)]
    except ValueError as error:
        raise SystemExit(str(error))
    if missing:
        raise SystemExit(f"规则尚未覆盖 {len(missing)} 条记录，请补充规则后重试：\n" + "\n".join(missing))
    return rules


def status() -> None:
    families = load_records()
    cache = FamilyCache(read_cache(CACHE))
    summary = defaultdict(Counter)
    claimed = {c["family_id"] for c in read_claims()}
    for fid, records in families.items():
        market = records[0]["market"]
        pending = len(uncovered(records, cache))
        summary[market]["families"] += 1
        summary[market]["records"] += len(records)
        summary[market]["covered_families"] += pending == 0
        summary[market]["covered_records"] += len(records) - pending
        # 可领取 = 未覆盖、未被领取且有尺寸（与 claim 的 BLOCKED_INPUT 排除一致）
        blocked = all(any(r.get(k) is None for k in ("length_mm", "width_mm", "height_mm")) for r in records)
        summary[market]["unclaimed_open"] += bool(pending) and fid not in claimed and not blocked
    claims = Counter(c["worker"] for c in read_claims())
    print(json.dumps({"by_market": summary, "rules": len(cache.rules), "claims": claims}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("claim")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--worker", required=True)
    p.add_argument("--market", nargs="+", default=["US"], choices=["US", "EU", "RU"])
    p = sub.add_parser("records")
    p.add_argument("--worker", required=True)
    p = sub.add_parser("release")
    p.add_argument("--worker", required=True)
    p = sub.add_parser("apply")
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--worker", required=True)
    sub.add_parser("status")
    p = sub.add_parser("review-list", help="生成多版本车型族复核清单")
    p.add_argument("--out", type=Path, default=PROJECT / "research_queue/review_families.tsv")
    p.add_argument("--min-versions", type=int, default=2)
    p.add_argument("--pattern", default=SHAPE_VERSION_PATTERN, help="版本名关键词正则（暗示外形差异）")
    p = sub.add_parser("claim-review", help="按复核清单领取")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--worker", required=True)
    p.add_argument("--list", type=Path, default=PROJECT / "research_queue/review_families.tsv")
    p = sub.add_parser("review-status")
    p.add_argument("--list", type=Path, default=PROJECT / "research_queue/review_families.tsv")
    args = parser.parse_args()
    if args.command == "review-list":
        return write_review_list(args.out, args.min_versions, args.pattern)
    if args.command == "claim-review":
        return claim_review(args.limit, args.worker, args.list)
    if args.command == "review-status":
        state = review_state(args.list)
        return print(json.dumps({"listed": len(state["listed"]), "reviewed": len(set(state["listed"]) & state["reviewed"]),
                                 "claimed": len(set(state["listed"]) & state["claimed"]), "unclaimed_open": len(state["unclaimed"])}))
    if args.command == "claim":
        if args.limit <= 0:
            parser.error("--limit 必须为正数")
        claim(args.limit, args.worker, args.market)
    elif args.command == "records":
        compact_records(args.worker)
    elif args.command == "release":
        release(args.worker)
    elif args.command == "apply":
        apply(args.file, args.worker)
    else:
        status()


if __name__ == "__main__":
    main()
