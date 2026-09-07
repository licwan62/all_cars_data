from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
DEFAULT_SOURCE = ROOT / "public" / "尺寸库.csv"
SOURCE = Path(os.environ.get("SHAPE_SOURCE", DEFAULT_SOURCE)).resolve()
CACHE = PROJECT / "cache" / "model_shape_cache.csv"
QUEUE = PROJECT / "research_queue" / "queue.csv"
RESULT = PROJECT / "artifacts" / "record_shape.csv"
REFERENCE = ROOT / "public" / "参考尺寸计算.csv"
LOCK_FILE = PROJECT / "research_queue" / ".shape_project.lock"
CACHE_FIELDS = ["MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end", "shape", "source_url", "note", "updated_at"]
QUEUE_FIELDS = ["queue_key", "MAKE", "MODEL", "record_count", "year_ranges", "example_reference", "status", "worker", "updated_at"]
STATUSES = {"pending", "in_progress", "done", "blocked"}


def reference_shape_ids() -> set[str]:
    """Load legal shape IDs from public/参考尺寸计算.csv."""

    if not REFERENCE.exists():
        raise RuntimeError(f"找不到车形规则源: {REFERENCE}")
    with REFERENCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    shape_ids = {row.get("车身号", "").strip() for row in rows}
    shape_ids.discard("")
    if not shape_ids:
        raise RuntimeError("reference.csv 没有有效的车身号")
    return shape_ids


ALLOWED_SHAPES = reference_shape_ids()


@contextmanager
def project_lock():
    """Serialize queue/cache mutations across parallel Windows workers."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_FILE.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0"); handle.flush()
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

# SOP 自带的典型车型属于项目规则，不需要再次联网确认。
SOP_SEEDS = {
    "Dodge": {"Challenger": "dodge-challenger"},
    "Ford": {"F-150": "P0", "Ranger": "P1", "F-250": "P1", "F-350": "P1", "Mustang": "SD0", "Transit": "V1", "Bronco": "JP", "Bronco Sport": "SU2", "Expedition": "SU2", "Focus": "H0"},
    "Chevrolet": {"Silverado 1500": "P0", "Colorado": "P1", "Silverado 2500HD": "P1", "Silverado 3500HD": "P1", "Express": "V1", "Tahoe": "SU2", "Malibu": "SD1"},
    "GMC": {"Sierra 1500": "P0", "Terrain": "SU1", "Yukon": "SU2"},
    "Ram": {"1500": "P0", "2500": "P1", "3500": "P1", "ProMaster": "V1"},
    "Toyota": {"Tacoma": "P1", "Sienna": "V0", "Camry": "SD1", "GR86": "SD0", "4Runner": "SU2", "RAV4": "SU1", "Highlander": "SU1", "Corolla": "H0"},
    "Honda": {"Odyssey": "V0", "Accord": "SD1", "CR-V": "SU1", "Civic": "H0"},
    "Chrysler": {"Pacifica": "V0"}, "Kia": {"Carnival": "V0", "Soul": "H1"},
    "Volkswagen": {"Golf": "H0"}, "Mazda": {"Mazda3": "H0", "CX-5": "SU1"},
    "Nissan": {"Altima": "SD1", "Rogue": "SU1", "Cube": "H1"}, "Genesis": {"G80": "SD1"},
    "Tesla": {"Model 3": "SD1", "Model X": "SU0", "Model Y": "SU0"}, "Porsche": {"Taycan": "SD0"},
    "Mercedes-Benz": {"CLA": "SD1", "GLB": "SU2", "G-Class": "JP", "Sprinter": "V1"},
    "Audi": {"A5 Sportback": "SD1", "Q8": "SU1", "RS6": "H2"}, "BMW": {"X6": "SU1", "XM": "SU1"},
    "Jeep": {"Wrangler": "JP"}, "Land Rover": {"Defender": "JP", "Range Rover Velar": "SU1"},
    "Cadillac": {"Escalade": "SU2"}, "Acura": {"ADX": "SU1", "RDX": "SU1"},
    "Scion": {"xB": "H1"},
}
SOP_SPECIAL_SEEDS = [
    ("Ford", "F-150", r"\bRaptor\b", "P2", "reference.csv 原厂 Wide-body 例外"),
    ("Ford", "Ranger", r"\bRaptor\b", "P2", "reference.csv 原厂 Wide-body 例外"),
    ("Chevrolet", "Silverado 1500", r"\bZR2\s+Bison\b", "P2", "reference.csv 原厂 Wide-body 例外"),
    ("Ram", "1500", r"\b(?:TRX|RHO)\b", "P2", "reference.csv 原厂 Wide-body 例外"),
    ("Ford", "F-350", r"\b(?:DRW|Dually|Dual Rear Wheel)\b", "DUAL", "reference.csv DRW 优先规则"),
    ("Chevrolet", "Silverado 3500HD", r"\b(?:DRW|Dually|Dual Rear Wheel)\b", "DUAL", "reference.csv DRW 优先规则"),
    ("GMC", "Sierra 3500HD", r"\b(?:DRW|Dually|Dual Rear Wheel)\b", "DUAL", "reference.csv DRW 优先规则"),
    ("Ram", "3500", r"\b(?:DRW|Dually|Dual Rear Wheel)\b", "DUAL", "reference.csv DRW 优先规则"),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_csv(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def atomic_write(path: Path, fields: list[str], rows: list[dict[str, str]], delimiter: str = ",") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=delimiter, extrasaction="ignore", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    for attempt in range(16):
        try:
            os.replace(temp, path); return
        except PermissionError:
            if attempt == 15:
                raise PermissionError(f"文件持续被占用，请关闭编辑器中的文件后重试: {path}")
            time.sleep(.15 * (attempt + 1))


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def queue_key(make: str, model: str) -> str:
    return hashlib.sha256(f"{norm(make)}\x1f{norm(model)}".encode()).hexdigest()[:20]


def years(value: str) -> tuple[int | None, int | None]:
    found = [int(x) for x in re.findall(r"(?:19|20)\d{2}", value or "")]
    return (min(found), max(found)) if found else (None, None)


def specificity(item: dict[str, str]) -> int:
    return 4 * bool(item.get("match_pattern")) + 2 * bool(item.get("generation")) + bool(item.get("year_start") or item.get("year_end"))


def matches(item: dict[str, str], row: dict[str, str]) -> bool:
    if norm(item.get("MAKE", "")) != norm(row.get("MAKE", "")) or norm(item.get("MODEL", "")) != norm(row.get("MODEL", "")): return False
    if item.get("generation") and norm(item["generation"]) != norm(row.get("代际", "")): return False
    lo, hi = years(row.get("YEAR", "")); start = int(item["year_start"]) if item.get("year_start") else None; end = int(item["year_end"]) if item.get("year_end") else None
    if start is not None and hi is not None and hi < start: return False
    if end is not None and lo is not None and lo > end: return False
    pattern = item.get("match_pattern", "")
    # DIMENSION-ID is intentionally display-oriented and no longer contains
    # field labels. Keep a separate labeled identity string so existing cache
    # rules remain explicit and do not parse the public ID format.
    haystack = " | ".join(
        [
            row.get("DIMENSION-ID", ""),
            f"MAKE={row.get('MAKE', '')}",
            f"MODEL={row.get('MODEL', '')}",
            f"VERSION={row.get('版本', '')}",
            f"STRUCTURE={row.get('结构', '')}",
            f"YEAR={row.get('YEAR', '')}",
            f"CAB={row.get('CAB', '')}",
            f"BED={row.get('BED', '')}",
            f"结构={row.get('结构', '')}",
        ]
        + [row.get(x, "") for x in ("版本", "CAB", "BED", "参考车型", "备注")]
    )
    return not pattern or re.search(pattern, haystack, re.IGNORECASE) is not None


def select_cache(row: dict[str, str], cache: list[dict[str, str]]) -> dict[str, str] | None:
    candidates = [item for item in cache if matches(item, row)]
    if not candidates: return None
    candidates.sort(key=specificity, reverse=True)
    top = specificity(candidates[0]); shapes = {x["shape"] for x in candidates if specificity(x) == top}
    if len(shapes) != 1: raise ValueError(f"缓存冲突: {row['MAKE']} {row['MODEL']} -> {sorted(shapes)}")
    return candidates[0]


def index_cache(
    cache: list[dict[str, str]],
) -> dict[tuple[str, str], list[dict[str, str]]]:
    """Index rules by normalized make/model before record-level matching."""

    indexed: dict[tuple[str, str], list[dict[str, str]]] = {}
    for item in cache:
        key = (norm(item.get("MAKE", "")), norm(item.get("MODEL", "")))
        indexed.setdefault(key, []).append(item)
    return indexed


def select_indexed_cache(
    row: dict[str, str],
    indexed: dict[tuple[str, str], list[dict[str, str]]],
) -> dict[str, str] | None:
    key = (norm(row.get("MAKE", "")), norm(row.get("MODEL", "")))
    return select_cache(row, indexed.get(key, []))


def seed_cache() -> list[dict[str, str]]:
    rows = read_csv(CACHE); existing = {(norm(x["MAKE"]), norm(x["MODEL"]), x.get("match_pattern", ""), x.get("generation", ""), x.get("year_start", ""), x.get("year_end", "")) for x in rows}
    source_pairs = {(norm(x["MAKE"]), norm(x["MODEL"])): (x["MAKE"], x["MODEL"]) for x in read_csv(SOURCE)}
    for make, models in SOP_SEEDS.items():
        for model, shape in models.items():
            actual = source_pairs.get((norm(make), norm(model)))
            if not actual: continue
            if shape in {"SD0", "SD1", "SD2"} and any(
                norm(row.get("MAKE", "")) == norm(actual[0])
                and norm(row.get("MODEL", "")) == norm(actual[1])
                and row.get("note", "").startswith("按新版 AGENT 代际复用")
                for row in rows
            ):
                continue
            key = (norm(actual[0]), norm(actual[1]), "", "", "", "")
            if key not in existing:
                rows.append({"MAKE": actual[0], "MODEL": actual[1], "match_pattern": "", "generation": "", "year_start": "", "year_end": "", "shape": shape, "source_url": "", "note": "SOP 典型车型", "updated_at": now()}); existing.add(key)
    for make, model, pattern, shape, note in SOP_SPECIAL_SEEDS:
        actual = source_pairs.get((norm(make), norm(model)))
        if not actual: continue
        key = (norm(actual[0]), norm(actual[1]), pattern, "", "", "")
        if key not in existing:
            rows.append({"MAKE": actual[0], "MODEL": actual[1], "match_pattern": pattern, "generation": "", "year_start": "", "year_end": "", "shape": shape, "source_url": "", "note": note, "updated_at": now()}); existing.add(key)
    atomic_write(CACHE, CACHE_FIELDS, sorted(rows, key=lambda x: (norm(x["MAKE"]), norm(x["MODEL"]), -specificity(x))))
    return rows


def sync_queue() -> tuple[int, int]:
    source = read_csv(SOURCE); cache = read_csv(CACHE); cache_index = index_cache(cache); old = {x["queue_key"]: x for x in read_csv(QUEUE)}; groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in source:
        if select_indexed_cache(row, cache_index) is None: groups.setdefault((row["MAKE"], row["MODEL"]), []).append(row)
    fresh = []
    for (make, model), items in groups.items():
        key = queue_key(make, model); prior = old.get(key, {})
        fresh.append({"queue_key": key, "MAKE": make, "MODEL": model, "record_count": str(len(items)), "year_ranges": "; ".join(sorted({x.get("YEAR", "") for x in items if x.get("YEAR")})), "example_reference": items[0].get("参考车型", ""), "status": prior.get("status", "pending") if prior.get("status") != "done" else "pending", "worker": prior.get("worker", ""), "updated_at": prior.get("updated_at", now())})
    atomic_write(QUEUE, QUEUE_FIELDS, sorted(fresh, key=lambda x: (x["status"], norm(x["MAKE"]), norm(x["MODEL"]))))
    return len(source), len(fresh)


def init() -> None:
    with project_lock():
        if not SOURCE.exists(): raise SystemExit(f"找不到源文件: {SOURCE}")
        cache = seed_cache(); total, unresolved = sync_queue()
        if unresolved and RESULT.exists():
            RESULT.unlink()
    print(f"项目已初始化：源记录 {total}，缓存 {len(cache)}，待研究车型 {unresolved}")


def claim(limit: int, worker: str) -> None:
    with project_lock():
        rows = read_csv(QUEUE); claimed = []
        for row in rows:
            if row["status"] == "pending" and len(claimed) < limit:
                row.update(status="in_progress", worker=worker, updated_at=now()); claimed.append(row)
        atomic_write(QUEUE, QUEUE_FIELDS, rows)
    compact_fields = ["queue_key", "MAKE", "MODEL", "record_count"]
    writer = csv.DictWriter(sys.stdout, fieldnames=compact_fields, delimiter="\t", extrasaction="ignore", lineterminator="\n"); writer.writeheader(); writer.writerows(claimed)


def compact_records(worker: str) -> None:
    """Print only canonical DIMENSION-ID strings for a worker's active claims."""
    claimed = {
        (norm(row["MAKE"]), norm(row["MODEL"]))
        for row in read_csv(QUEUE)
        if row["status"] == "in_progress" and row.get("worker") == worker
    }
    for row in read_csv(SOURCE):
        if (norm(row["MAKE"]), norm(row["MODEL"])) in claimed:
            print(row["DIMENSION-ID"])


def release(worker: str) -> None:
    """Return a stopped worker's unfinished claims to the pending queue."""
    with project_lock():
        rows = read_csv(QUEUE); released = 0
        for row in rows:
            if row["status"] == "in_progress" and row.get("worker") == worker:
                row.update(status="pending", worker="", updated_at=now()); released += 1
        atomic_write(QUEUE, QUEUE_FIELDS, rows)
    print(f"已释放 {released} 条 {worker} 的未完成领取")


def update(args: argparse.Namespace) -> None:
    with project_lock():
        if args.shape not in ALLOWED_SHAPES: raise SystemExit(f"非法车形号码: {args.shape}")
        queue = read_csv(QUEUE); target = next((x for x in queue if x["queue_key"] == args.key), None)
        if target is None: raise SystemExit(f"找不到 queue_key: {args.key}")
        cache = read_csv(CACHE); new = {"MAKE": target["MAKE"], "MODEL": target["MODEL"], "match_pattern": args.match_pattern or "", "generation": args.generation or "", "year_start": args.year_start or "", "year_end": args.year_end or "", "shape": args.shape, "source_url": args.source_url or "", "note": args.note or "", "updated_at": now()}
        identity = tuple(new[x] for x in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end")); cache = [x for x in cache if tuple(x.get(k, "") for k in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end")) != identity]; cache.append(new)
        atomic_write(CACHE, CACHE_FIELDS, cache); sync_queue()
    print(f"已缓存：{target['MAKE']} {target['MODEL']} -> {args.shape}")


def batch_update(path: Path, worker: str | None = None) -> None:
    """Apply many researched cache decisions, then rebuild the queue once."""
    items = json.loads(path.read_text(encoding="utf-8"))
    with project_lock():
        queue = {row["queue_key"]: row for row in read_csv(QUEUE)}
        if worker:
            allowed = {key for key, row in queue.items() if row["status"] == "in_progress" and row.get("worker") == worker}
            submitted = {str(item.get("queue_key", "")) for item in items}
            if submitted != allowed:
                raise SystemExit(f"批次领取不匹配: worker={worker}, expected={sorted(allowed)}, submitted={sorted(submitted)}")
        cache = read_csv(CACHE)
        changed = []
        reset_models: set[tuple[str, str]] = set()
        for item in items:
            shape = str(item.get("shape", ""))
            if shape not in ALLOWED_SHAPES:
                raise SystemExit(f"非法车形号码: {shape}")
            target = queue.get(item.get("queue_key", ""))
            if target is None:
                raise SystemExit(f"找不到 queue_key: {item.get('queue_key', '')}")
            new = {"MAKE": target["MAKE"], "MODEL": target["MODEL"], "match_pattern": str(item.get("match_pattern", "")), "generation": str(item.get("generation", "")), "year_start": str(item.get("year_start", "")), "year_end": str(item.get("year_end", "")), "shape": shape, "source_url": str(item.get("source_url", "")), "note": str(item.get("note", "")), "updated_at": now()}
            if not new["source_url"] or not new["note"]:
                raise SystemExit(f"缺少 source_url 或 note: {target['MAKE']} {target['MODEL']}")
            model_key = (norm(new["MAKE"]), norm(new["MODEL"]))
            if model_key not in reset_models:
                cache = [row for row in cache if (norm(row.get("MAKE", "")), norm(row.get("MODEL", ""))) != model_key]
                reset_models.add(model_key)
            identity = tuple(new[x] for x in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end"))
            cache = [row for row in cache if tuple(row.get(k, "") for k in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end")) != identity]
            cache.append(new); changed.append(f"{target['MAKE']} {target['MODEL']} -> {shape}")
        submitted_models = {
            (norm(queue[str(item["queue_key"])]["MAKE"]), norm(queue[str(item["queue_key"])]["MODEL"]))
            for item in items
        }
        unmatched = []
        cache_index = index_cache(cache)
        for source_row in read_csv(SOURCE):
            model_key = (norm(source_row["MAKE"]), norm(source_row["MODEL"]))
            if model_key in submitted_models and select_indexed_cache(source_row, cache_index) is None:
                unmatched.append(source_row["DIMENSION-ID"])
        if unmatched:
            details = "\n".join(unmatched)
            raise SystemExit(
                f"批次规则尚未覆盖 {len(unmatched)} 条紧凑记录；请修正完整 JSON 后重试：\n{details}"
            )
        atomic_write(CACHE, CACHE_FIELDS, cache)
        _, unresolved = sync_queue()
    print(f"已批量缓存 {len(changed)} 条，待研究车型 {unresolved}")


def build() -> None:
    with project_lock():
        source = read_csv(SOURCE); cache = read_csv(CACHE); cache_index = index_cache(cache); result = []; unresolved = []
        for row in source:
            item = select_indexed_cache(row, cache_index)
            if item is None: unresolved.append(row)
            else: result.append({"DIMENSION-ID": row["DIMENSION-ID"], "车形": item["shape"]})
        sync_queue()
        if unresolved:
            if RESULT.exists():
                RESULT.unlink()
            raise SystemExit(f"尚有 {len(unresolved)} 条记录（{len({(x['MAKE'], x['MODEL']) for x in unresolved})} 个车型）未核定；未生成最终结果")
        atomic_write(RESULT, ["DIMENSION-ID", "车形"], result)
    print(f"已生成 {RESULT}：{len(result)} 条")


def main() -> None:
    parser = argparse.ArgumentParser(description="车型车形号码缓存与结果生成")
    sub = parser.add_subparsers(dest="command", required=True); sub.add_parser("init"); sub.add_parser("build")
    p = sub.add_parser("claim"); p.add_argument("--limit", type=int, default=10); p.add_argument("--worker", required=True)
    p = sub.add_parser("compact-records"); p.add_argument("--worker", required=True)
    p = sub.add_parser("release"); p.add_argument("--worker", required=True)
    p = sub.add_parser("update"); p.add_argument("--key", required=True); p.add_argument("--shape", required=True); p.add_argument("--worker", required=True); p.add_argument("--source-url", required=True); p.add_argument("--note", required=True); p.add_argument("--match-pattern"); p.add_argument("--generation"); p.add_argument("--year-start"); p.add_argument("--year-end")
    p = sub.add_parser("batch-update"); p.add_argument("--file", type=Path, required=True); p.add_argument("--worker")
    args = parser.parse_args()
    if args.command == "init": init()
    elif args.command == "claim": claim(args.limit, args.worker)
    elif args.command == "compact-records": compact_records(args.worker)
    elif args.command == "release": release(args.worker)
    elif args.command == "update": update(args)
    elif args.command == "batch-update": batch_update(args.file, args.worker)
    else: build()


if __name__ == "__main__": main()
