from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import time
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from common import OVERRIDE_FIELDS, load_config, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research_queue" / "allocation_weight_queue.csv"
REVIEWS = ROOT / "cache" / "research" / "allocation_weight_reviews.csv"
LOCK_FILE = ROOT / "research_queue" / ".allocation_weight_review.lock"

QUEUE_FIELDS = [
    "queue_key", "MAKE", "MODEL", "YEAR", "DIFF_TYPE", "ATOM_COUNT", "ATOM_KEYS",
    "MODEL_YEAR_US_SALES", "PRIORITY_TIER", "status", "worker", "updated_at",
]
REVIEW_FIELDS = [
    "queue_key", "MAKE", "MODEL", "YEAR", "outcome", "SALES_ATOM_KEY", "ALLOCATION_WEIGHT",
    "ALLOCATION_METHOD", "SALES_CONFIDENCE", "SOURCE_URL", "review_note", "reviewed_at",
]

# Tier policy (the granularity the queue advances at):
#   TIER1 - 版本(trim) 不同, 且 MODEL_YEAR_US_SALES >= HIGH_VOLUME_THRESHOLD: 均分误差风险最大, 优先研究 trim 级占比。
#   TIER2 - 版本(trim) 不同, 但销量体量较小: 仍需 trim 占比, 但误差绝对值有限, 靠后处理。
#   TIER3 - 仅 结构(body) 不同: 通常有独立可查的车身销量口径, 但误差风险低于 trim, 排在 trim 差异之后。
# 组内销量总数缺失(尚未研究到 MAKE+MODEL+YEAR 级别)的组不进队列, 因为没有可分配的总量。
HIGH_VOLUME_THRESHOLD = 5000


@contextmanager
def project_lock():
    """Serialize allocation-weight queue, review log, and override cache writes."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_FILE.open("a+b") as handle:
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


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def norm(value: str) -> str:
    return " ".join((value or "").strip().casefold().split())


def queue_key(make: str, model: str, year: str) -> str:
    return hashlib.sha256(f"alloc-v1\x1f{norm(make)}\x1f{norm(model)}\x1f{norm(year)}".encode()).hexdigest()[:20]


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def diff_type(group: list[dict[str, str]]) -> str:
    versions = {row.get("版本", "") for row in group}
    structures = {row.get("结构", "") for row in group}
    has_trim = len(versions) > 1
    has_body = len(structures) > 1
    if has_trim and has_body:
        return "BOTH"
    if has_trim:
        return "TRIM"
    if has_body:
        return "BODY"
    return "OTHER"


def priority_tier(diff: str, total_sales: str) -> str:
    try:
        sales = int(total_sales) if total_sales else 0
    except ValueError:
        sales = 0
    if diff in ("TRIM", "BOTH"):
        return "TIER1" if sales >= HIGH_VOLUME_THRESHOLD else "TIER2"
    return "TIER3"


def build_groups(atomic_rows: list[dict[str, str]]) -> dict[tuple[str, str, str], list[dict[str, str]]]:
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in atomic_rows:
        groups[(row["MAKE"], row["MODEL"], row["YEAR"])].append(row)
    return groups


def sync_queue(config_path: str = "config.json") -> tuple[int, dict[str, int]]:
    config = load_config(config_path)
    _, atomic_rows = read_csv(config["atomic_output_csv"])
    reviewed = {
        (row["MAKE"], row["MODEL"], row["YEAR"])
        for row in load_rows(REVIEWS)
    }
    old = {row["queue_key"]: row for row in load_rows(QUEUE)}

    groups = build_groups(atomic_rows)
    fresh = []
    for key, group in groups.items():
        if key in reviewed:
            continue
        if len({row["SALES_ATOM_KEY"] for row in group}) <= 1:
            continue
        if not all(row.get("ITERATION_STATUS") == "REVIEW" and row.get("ALLOCATION_METHOD") == "EQUAL_SPLIT" for row in group):
            continue
        make, model, year = key
        total = group[0].get("MODEL_YEAR_US_SALES", "")
        atom_keys = sorted({row["SALES_ATOM_KEY"] for row in group})
        diff = diff_type(group)
        qkey = queue_key(make, model, year)
        prior = old.get(qkey, {})
        status = prior.get("status", "pending")
        worker = prior.get("worker", "")
        if status == "in_progress" and not worker:
            status = "pending"
        fresh.append({
            "queue_key": qkey,
            "MAKE": make,
            "MODEL": model,
            "YEAR": year,
            "DIFF_TYPE": diff,
            "ATOM_COUNT": str(len(atom_keys)),
            "ATOM_KEYS": ";".join(atom_keys),
            "MODEL_YEAR_US_SALES": total,
            "PRIORITY_TIER": priority_tier(diff, total),
            "status": status,
            "worker": worker,
            "updated_at": prior.get("updated_at", now()),
        })

    def sort_key(row: dict[str, str]) -> tuple:
        try:
            sales = int(row["MODEL_YEAR_US_SALES"]) if row["MODEL_YEAR_US_SALES"] else -1
        except ValueError:
            sales = -1
        return (row["PRIORITY_TIER"], -sales, norm(row["MAKE"]), norm(row["MODEL"]), row["YEAR"])

    fresh.sort(key=sort_key)
    write_csv(QUEUE, QUEUE_FIELDS, fresh)
    tiers = Counter(row["PRIORITY_TIER"] for row in fresh)
    return len(fresh), dict(tiers)


def init(config_path: str = "config.json") -> None:
    with project_lock():
        if not REVIEWS.exists():
            write_csv(REVIEWS, REVIEW_FIELDS, [])
        total, tiers = sync_queue(config_path)
    print(f"allocation-weight queue: {total} MAKE+MODEL+YEAR groups needing trim/结构 级研究; tiers={tiers}")


def claim(limit: int, worker: str) -> None:
    with project_lock():
        rows = load_rows(QUEUE)
        claimed = []
        for row in rows:
            if len(claimed) >= limit:
                break
            if row["status"] != "pending":
                continue
            row.update(status="in_progress", worker=worker, updated_at=now())
            claimed.append(row)
        write_csv(QUEUE, QUEUE_FIELDS, rows)
    writer = csv.DictWriter(
        __import__("sys").stdout,
        fieldnames=["queue_key", "MAKE", "MODEL", "YEAR", "DIFF_TYPE", "MODEL_YEAR_US_SALES", "PRIORITY_TIER", "ATOM_KEYS"],
        delimiter="\t", extrasaction="ignore", lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(claimed)


def compact_records(worker: str, config_path: str = "config.json") -> None:
    config = load_config(config_path)
    _, atomic_rows = read_csv(config["atomic_output_csv"])
    groups = build_groups(atomic_rows)
    for claim_row in load_rows(QUEUE):
        if claim_row["status"] != "in_progress" or claim_row.get("worker") != worker:
            continue
        key = (claim_row["MAKE"], claim_row["MODEL"], claim_row["YEAR"])
        group = groups.get(key, [])
        atoms = ";".join(
            f"{row['SALES_ATOM_KEY']}|版本={row.get('版本','')}|结构={row.get('结构','')}"
            for row in sorted(group, key=lambda r: r["SALES_ATOM_KEY"])
        )
        print(
            f"KEY={claim_row['queue_key']}|MAKE={claim_row['MAKE']}|MODEL={claim_row['MODEL']}|YEAR={claim_row['YEAR']}"
            f"|TOTAL_SALES={claim_row['MODEL_YEAR_US_SALES']}|DIFF_TYPE={claim_row['DIFF_TYPE']}|ATOMS={atoms}"
        )


def release(worker: str) -> None:
    with project_lock():
        rows = load_rows(QUEUE)
        released = 0
        for row in rows:
            if row["status"] == "in_progress" and row.get("worker") == worker:
                row.update(status="pending", worker="", updated_at=now())
                released += 1
        write_csv(QUEUE, QUEUE_FIELDS, rows)
    print(f"released {released} unfinished allocation-weight groups for {worker}")


def _validate_allocations(atom_keys: list[str], allocations: list[dict[str, object]]) -> dict[str, Decimal]:
    submitted = {str(item["SALES_ATOM_KEY"]): item for item in allocations}
    if set(submitted) != set(atom_keys):
        missing = sorted(set(atom_keys) - set(submitted))
        extra = sorted(set(submitted) - set(atom_keys))
        raise SystemExit(f"allocation atom mismatch; missing={missing} extra={extra}")
    weights: dict[str, Decimal] = {}
    for key, item in submitted.items():
        try:
            weight = Decimal(str(item["ALLOCATION_WEIGHT"]))
        except (InvalidOperation, KeyError) as exc:
            raise SystemExit(f"invalid ALLOCATION_WEIGHT for {key}") from exc
        if weight < 0:
            raise SystemExit(f"negative ALLOCATION_WEIGHT for {key}")
        weights[key] = weight
    if abs(sum(weights.values()) - Decimal(1)) > Decimal("0.000001"):
        raise SystemExit(f"allocation weights do not sum to 1: {sum(weights.values())}")
    return weights


def batch_update(path: Path, worker: str) -> None:
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit("batch JSON must be a list")

    with project_lock():
        queue = load_rows(QUEUE)
        claimed = {row["queue_key"]: row for row in queue if row["status"] == "in_progress" and row.get("worker") == worker}
        expected = set(claimed)
        submitted_keys = {str(item.get("queue_key", "")) for item in items}
        if submitted_keys != expected:
            raise SystemExit(
                f"batch coverage mismatch; missing={sorted(expected - submitted_keys)} "
                f"extra={sorted(submitted_keys - expected)}"
            )

        overrides = load_rows(ROOT / "cache" / "allocation_weights.csv") if (ROOT / "cache" / "allocation_weights.csv").exists() else []
        overrides_by_key = {row["SALES_ATOM_KEY"]: row for row in overrides}
        reviews = load_rows(REVIEWS)
        reviewed_at = now()
        allocated = retained = 0

        for item in items:
            claim_row = claimed[str(item["queue_key"])]
            atom_keys = claim_row["ATOM_KEYS"].split(";")
            outcome = str(item.get("outcome", "")).lower()
            note = str(item.get("review_note", "")).strip()
            if not note:
                raise SystemExit(f"review_note is required for {claim_row['queue_key']}")

            if outcome == "allocated":
                source_url = str(item.get("SOURCE_URL", "")).strip()
                method = str(item.get("ALLOCATION_METHOD", "")).strip() or "ESTIMATED_SHARE"
                confidence = str(item.get("SALES_CONFIDENCE", "")).strip().upper() or "MEDIUM"
                if not source_url:
                    raise SystemExit(f"SOURCE_URL is required for allocated outcome: {claim_row['queue_key']}")
                allocations = item.get("allocations")
                if not isinstance(allocations, list) or not allocations:
                    raise SystemExit(f"allocated outcome requires non-empty allocations: {claim_row['queue_key']}")
                weights = _validate_allocations(atom_keys, allocations)
                for atom_key, weight in weights.items():
                    overrides_by_key[atom_key] = {
                        "SALES_ATOM_KEY": atom_key,
                        "ALLOCATION_WEIGHT": str(weight),
                        "ALLOCATION_METHOD": method,
                        "SALES_CONFIDENCE": confidence,
                        "NOTES": f"{note} | {source_url}",
                    }
                    reviews.append({
                        "queue_key": claim_row["queue_key"], "MAKE": claim_row["MAKE"], "MODEL": claim_row["MODEL"],
                        "YEAR": claim_row["YEAR"], "outcome": outcome, "SALES_ATOM_KEY": atom_key,
                        "ALLOCATION_WEIGHT": str(weight), "ALLOCATION_METHOD": method, "SALES_CONFIDENCE": confidence,
                        "SOURCE_URL": source_url, "review_note": note, "reviewed_at": reviewed_at,
                    })
                allocated += 1
            elif outcome == "retained_equal":
                reviews.append({
                    "queue_key": claim_row["queue_key"], "MAKE": claim_row["MAKE"], "MODEL": claim_row["MODEL"],
                    "YEAR": claim_row["YEAR"], "outcome": outcome, "SALES_ATOM_KEY": "",
                    "ALLOCATION_WEIGHT": "", "ALLOCATION_METHOD": "", "SALES_CONFIDENCE": "",
                    "SOURCE_URL": str(item.get("SOURCE_URL", "")).strip(), "review_note": note, "reviewed_at": reviewed_at,
                })
                retained += 1
            else:
                raise SystemExit(f"invalid outcome for {claim_row['queue_key']}: {outcome}")

        write_csv(ROOT / "cache" / "allocation_weights.csv", OVERRIDE_FIELDS, list(overrides_by_key.values()))
        reviews.sort(key=lambda row: (norm(row["MAKE"]), norm(row["MODEL"]), row["YEAR"]))
        write_csv(REVIEWS, REVIEW_FIELDS, reviews)
        total, tiers = sync_queue()
    print(f"allocation-weight batch applied: {allocated} allocated, {retained} retained equal; remaining {total} groups; tiers={tiers}")


def status() -> None:
    rows = load_rows(QUEUE)
    reviews = load_rows(REVIEWS)
    counts: dict[str, int] = {}
    tiers: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
        tiers[row["PRIORITY_TIER"]] = tiers.get(row["PRIORITY_TIER"], 0) + 1
    outcomes = Counter(row.get("outcome", "") for row in reviews)
    print(json.dumps({
        "groups": len(rows),
        "status": counts,
        "tiers": tiers,
        "reviewed": len(reviews),
        "outcomes": outcomes,
    }, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Trim/结构 allocation-weight research queue for multi-atom MAKE+MODEL+YEAR sales groups")
    parser.add_argument("--config", default="config.json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    p = sub.add_parser("claim"); p.add_argument("--limit", type=int, default=8); p.add_argument("--worker", required=True)
    p = sub.add_parser("compact-records"); p.add_argument("--worker", required=True)
    p = sub.add_parser("release"); p.add_argument("--worker", required=True)
    p = sub.add_parser("batch-update"); p.add_argument("--file", type=Path, required=True); p.add_argument("--worker", required=True)
    args = parser.parse_args()
    if args.command == "init": init(args.config)
    elif args.command == "status": status()
    elif args.command == "claim": claim(args.limit, args.worker)
    elif args.command == "compact-records": compact_records(args.worker, args.config)
    elif args.command == "release": release(args.worker)
    else: batch_update(args.file, args.worker)


if __name__ == "__main__":
    main()
