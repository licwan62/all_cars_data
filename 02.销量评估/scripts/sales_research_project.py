from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from common import CACHE_FIELDS, load_config, model_year_key, parse_nonnegative_integer, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research_queue" / "sales_quality_queue.csv"
REVIEWS = ROOT / "cache" / "research" / "sales_quality_reviews.csv"
LOCK_FILE = ROOT / "research_queue" / ".sales_quality.lock"
QUEUE_FIELDS = ["queue_key", "MAKE", "MODEL", "YEARS", "record_count", "status", "worker", "updated_at"]
REVIEW_FIELDS = ["MAKE", "MODEL", "YEAR", "outcome", "reviewed_at", "note"]
ALLOWED_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
ALLOWED_PERIOD = {"FULL_YEAR", "YTD"}


@contextmanager
def project_lock():
    """Serialize queue/cache mutations across parallel Windows workers."""
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


def group_key(make: str, model: str) -> str:
    return hashlib.sha256(f"{norm(make)}\x1f{norm(model)}".encode()).hexdigest()[:20]


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def is_candidate(row: dict[str, str]) -> bool:
    return (
        row.get("SOURCE_CONFIDENCE", "").upper() == "LOW"
        or row.get("SALES_SOURCE", "").upper() == "ESTIMATE"
        or not row.get("SOURCE_URL", "").strip()
    )


def sync_queue() -> tuple[int, int]:
    config = load_config()
    _, project_queue = read_csv(config["research_queue_csv"])
    _, cache = read_csv(config["model_year_cache_csv"])
    relevant = {model_year_key(row) for row in project_queue}
    reviewed = {model_year_key(row) for row in load_rows(REVIEWS)}
    old = {row["queue_key"]: row for row in load_rows(QUEUE)}
    groups: dict[tuple[str, str], list[int]] = {}
    for row in cache:
        key = model_year_key(row)
        if key in relevant and key not in reviewed and is_candidate(row):
            groups.setdefault((row["MAKE"], row["MODEL"]), []).append(int(row["YEAR"]))

    fresh = []
    for (make, model), years in groups.items():
        key = group_key(make, model)
        prior = old.get(key, {})
        fresh.append({
            "queue_key": key,
            "MAKE": make,
            "MODEL": model,
            "YEARS": ";".join(str(year) for year in sorted(set(years))),
            "record_count": str(len(set(years))),
            "status": prior.get("status", "pending"),
            "worker": prior.get("worker", ""),
            "updated_at": prior.get("updated_at", now()),
        })
    fresh.sort(key=lambda row: (norm(row["MAKE"]), norm(row["MODEL"])))
    write_csv(QUEUE, QUEUE_FIELDS, fresh)
    return len(fresh), sum(int(row["record_count"]) for row in fresh)


def init() -> None:
    with project_lock():
        if not REVIEWS.exists():
            write_csv(REVIEWS, REVIEW_FIELDS, [])
        groups, rows = sync_queue()
    print(f"quality queue: {groups} model families, {rows} model-years")


def claim(limit: int, max_years: int, worker: str) -> None:
    with project_lock():
        rows = load_rows(QUEUE)
        claimed = []
        claimed_years = 0
        for row in rows:
            if row["status"] != "pending" or len(claimed) >= limit:
                continue
            count = int(row["record_count"])
            if claimed and claimed_years + count > max_years:
                continue
            row.update(status="in_progress", worker=worker, updated_at=now())
            claimed.append(row)
            claimed_years += count
        write_csv(QUEUE, QUEUE_FIELDS, rows)
    writer = csv.DictWriter(
        __import__("sys").stdout,
        fieldnames=["queue_key", "MAKE", "MODEL", "record_count"],
        delimiter="\t",
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(claimed)


def compact_records(worker: str) -> None:
    for row in load_rows(QUEUE):
        if row["status"] == "in_progress" and row.get("worker") == worker:
            years = ",".join(row["YEARS"].split(";"))
            print(f"MAKE={row['MAKE']}|MODEL={row['MODEL']}|YEARS={years}")


def release(worker: str) -> None:
    with project_lock():
        rows = load_rows(QUEUE)
        released = 0
        for row in rows:
            if row["status"] == "in_progress" and row.get("worker") == worker:
                row.update(status="pending", worker="", updated_at=now())
                released += 1
        write_csv(QUEUE, QUEUE_FIELDS, rows)
    print(f"released {released} unfinished model families for {worker}")


def expand_batch_items(raw_items: object) -> list[dict[str, object]]:
    """Expand compact family-level results into one validated item per model-year."""
    if not isinstance(raw_items, list):
        raise SystemExit("batch JSON must be a list")
    expanded: list[dict[str, object]] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise SystemExit("each batch item must be an object")
        if "YEAR" in raw:
            expanded.append(dict(raw))
            continue
        outcome = str(raw.get("outcome", "")).lower()
        if outcome == "updated":
            year_sales = raw.get("year_sales")
            if not isinstance(year_sales, dict) or not year_sales:
                raise SystemExit("family-level updated item requires non-empty year_sales")
            estimated_years = {str(year) for year in raw.get("estimated_years", [])}
            for year, sales in year_sales.items():
                item = {key: value for key, value in raw.items() if key not in {"year_sales", "estimated_years", "YEARS"}}
                item["YEAR"] = str(year)
                item["MODEL_YEAR_US_SALES"] = str(sales)
                if str(year) in estimated_years:
                    item["SALES_SOURCE_TYPE"] = "ESTIMATED"
                    item["SOURCE_CONFIDENCE"] = "LOW"
                    note = str(item.get("NOTES", "")).strip()
                    item["NOTES"] = f"{note}; estimated for weighting from family sales trend".strip("; ")
                expanded.append(item)
        elif outcome == "accepted":
            years = raw.get("YEARS")
            if not isinstance(years, list) or not years:
                raise SystemExit("family-level accepted item requires non-empty YEARS")
            for year in years:
                item = {key: value for key, value in raw.items() if key != "YEARS"}
                item["YEAR"] = str(year)
                expanded.append(item)
        else:
            raise SystemExit(f"invalid family-level outcome: {outcome}")
    return expanded


def batch_update(path: Path, worker: str) -> None:
    items = expand_batch_items(json.loads(path.read_text(encoding="utf-8")))
    with project_lock():
        queue = load_rows(QUEUE)
        claimed = {row["queue_key"]: row for row in queue if row["status"] == "in_progress" and row.get("worker") == worker}
        expected = {
            (key, year)
            for key, row in claimed.items()
            for year in row["YEARS"].split(";")
        }
        submitted = {(str(item.get("queue_key", "")), str(item.get("YEAR", ""))) for item in items}
        if submitted != expected:
            missing = sorted(expected - submitted)
            extra = sorted(submitted - expected)
            raise SystemExit(f"batch coverage mismatch; missing={missing[:10]} extra={extra[:10]}")

        config = load_config()
        _, cache = read_csv(config["model_year_cache_csv"])
        index = {model_year_key(row): i for i, row in enumerate(cache)}
        reviews = load_rows(REVIEWS)
        reviewed_at = now()
        updated = accepted = 0
        for item in items:
            queue_row = claimed[item["queue_key"]]
            key = (queue_row["MAKE"], queue_row["MODEL"], str(item["YEAR"]))
            if key not in index:
                raise SystemExit(f"cache key not found: {key}")
            outcome = str(item.get("outcome", "")).lower()
            note = str(item.get("review_note", "")).strip()
            if outcome == "updated":
                source_url = str(item.get("SOURCE_URL", "")).strip()
                sales = str(item.get("MODEL_YEAR_US_SALES", "")).strip()
                scope = str(item.get("SALES_SCOPE", "")).strip().upper()
                period = str(item.get("SALES_PERIOD", "")).strip().upper()
                confidence = str(item.get("SOURCE_CONFIDENCE", "")).strip().upper()
                if not source_url or not note:
                    raise SystemExit(f"updated item requires SOURCE_URL and review_note: {key}")
                parse_nonnegative_integer(sales, "MODEL_YEAR_US_SALES")
                if scope not in {"US", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"}:
                    raise SystemExit(f"invalid SALES_SCOPE for {key}: {scope}")
                if period not in ALLOWED_PERIOD:
                    raise SystemExit(f"invalid SALES_PERIOD for {key}: {period}")
                if confidence not in ALLOWED_CONFIDENCE:
                    raise SystemExit(f"invalid SOURCE_CONFIDENCE for {key}: {confidence}")
                current = cache[index[key]]
                replacement = {field: str(item.get(field, current.get(field, ""))).strip() for field in CACHE_FIELDS}
                replacement.update(MAKE=key[0], MODEL=key[1], YEAR=key[2], SALES_SCOPE="US", SALES_PERIOD=period, SOURCE_CONFIDENCE=confidence)
                cache[index[key]] = replacement
                updated += 1
            elif outcome == "accepted":
                if not note:
                    raise SystemExit(f"accepted item requires review_note: {key}")
                accepted += 1
            else:
                raise SystemExit(f"invalid outcome for {key}: {outcome}")
            reviews = [row for row in reviews if model_year_key(row) != key]
            reviews.append({"MAKE": key[0], "MODEL": key[1], "YEAR": key[2], "outcome": outcome, "reviewed_at": reviewed_at, "note": note})

        write_csv(config["model_year_cache_csv"], CACHE_FIELDS, cache)
        reviews.sort(key=lambda row: (norm(row["MAKE"]), norm(row["MODEL"]), int(row["YEAR"])))
        write_csv(REVIEWS, REVIEW_FIELDS, reviews)
        groups, rows = sync_queue()
    print(f"quality batch applied: {updated} updated, {accepted} accepted; remaining {groups} families / {rows} model-years")


def status() -> None:
    rows = load_rows(QUEUE)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(json.dumps({"families": len(rows), "model_years": sum(int(row["record_count"]) for row in rows), "status": counts}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales evidence quality research queue")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    p = sub.add_parser("claim"); p.add_argument("--limit", type=int, default=5); p.add_argument("--max-years", type=int, default=30); p.add_argument("--worker", required=True)
    p = sub.add_parser("compact-records"); p.add_argument("--worker", required=True)
    p = sub.add_parser("release"); p.add_argument("--worker", required=True)
    p = sub.add_parser("batch-update"); p.add_argument("--file", type=Path, required=True); p.add_argument("--worker", required=True)
    args = parser.parse_args()
    if args.command == "init": init()
    elif args.command == "status": status()
    elif args.command == "claim": claim(args.limit, args.max_years, args.worker)
    elif args.command == "compact-records": compact_records(args.worker)
    elif args.command == "release": release(args.worker)
    else: batch_update(args.file, args.worker)


if __name__ == "__main__":
    main()
