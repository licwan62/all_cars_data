from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import time
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from common import CACHE_FIELDS, load_config, model_year_key, parse_nonnegative_integer, read_csv, write_csv


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research_queue" / "sales_low_confidence_queue.csv"
REVIEWS = ROOT / "cache" / "research" / "sales_low_second_pass_reviews.csv"
LOCK_FILE = ROOT / "research_queue" / ".sales_low_review.lock"
QUEUE_FIELDS = [
    "queue_key", "MAKE", "MODEL", "YEARS", "record_count", "SOURCE_GROUP",
    "status", "worker", "updated_at",
]
REVIEW_FIELDS = [
    "MAKE", "MODEL", "YEAR", "outcome", "previous_confidence", "new_confidence",
    "source_url", "reviewed_at", "note",
]
ALLOWED_PERIOD = {"FULL_YEAR", "YTD"}
UPGRADED_CONFIDENCE = {"HIGH", "MEDIUM"}


@contextmanager
def project_lock():
    """Serialize dedicated second-pass queue, review log, and cache writes."""
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


def queue_key(make: str, model: str) -> str:
    return hashlib.sha256(f"low-v2\x1f{norm(make)}\x1f{norm(model)}".encode()).hexdigest()[:20]


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def common_source(rows: list[dict[str, str]]) -> str:
    urls = [row.get("SOURCE_URL", "").strip() for row in rows if row.get("SOURCE_URL", "").strip()]
    return Counter(urls).most_common(1)[0][0] if urls else ""


def sync_queue() -> tuple[int, int]:
    config = load_config()
    _, cache = read_csv(config["model_year_cache_csv"])
    reviewed = {model_year_key(row) for row in load_rows(REVIEWS)}
    old = {row["queue_key"]: row for row in load_rows(QUEUE)}
    families: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in cache:
        if row.get("SOURCE_CONFIDENCE", "").upper() != "LOW" or model_year_key(row) in reviewed:
            continue
        families.setdefault((row["MAKE"], row["MODEL"]), []).append(row)

    fresh = []
    for (make, model), rows in families.items():
        key = queue_key(make, model)
        prior = old.get(key, {})
        years = sorted({int(row["YEAR"]) for row in rows})
        source = common_source(rows)
        status = prior.get("status", "pending")
        worker = prior.get("worker", "")
        if status == "in_progress" and not worker:
            status = "pending"
        fresh.append({
            "queue_key": key,
            "MAKE": make,
            "MODEL": model,
            "YEARS": ";".join(map(str, years)),
            "record_count": str(len(years)),
            "SOURCE_GROUP": source,
            "status": status,
            "worker": worker,
            "updated_at": prior.get("updated_at", now()),
        })
    fresh.sort(key=lambda row: (not bool(row["SOURCE_GROUP"]), row["SOURCE_GROUP"], norm(row["MAKE"]), norm(row["MODEL"])))
    write_csv(QUEUE, QUEUE_FIELDS, fresh)
    return len(fresh), sum(int(row["record_count"]) for row in fresh)


def init() -> None:
    with project_lock():
        if not REVIEWS.exists():
            write_csv(REVIEWS, REVIEW_FIELDS, [])
        groups, years = sync_queue()
    print(f"LOW second-pass queue: {groups} model families, {years} model-years")


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
        fieldnames=["queue_key", "MAKE", "MODEL", "record_count", "SOURCE_GROUP"],
        delimiter="\t", extrasaction="ignore", lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(claimed)


def compact_records(worker: str) -> None:
    config = load_config()
    _, cache = read_csv(config["model_year_cache_csv"])
    by_family: dict[tuple[str, str], dict[str, dict[str, str]]] = {}
    for row in cache:
        by_family.setdefault((row["MAKE"], row["MODEL"]), {})[row["YEAR"]] = row
    for claim_row in load_rows(QUEUE):
        if claim_row["status"] != "in_progress" or claim_row.get("worker") != worker:
            continue
        years = claim_row["YEARS"].split(";")
        family = by_family[(claim_row["MAKE"], claim_row["MODEL"])]
        values = ",".join(f"{year}:{family[year]['MODEL_YEAR_US_SALES']}" for year in years)
        source = claim_row.get("SOURCE_GROUP", "")
        print(f"KEY={claim_row['queue_key']}|MAKE={claim_row['MAKE']}|MODEL={claim_row['MODEL']}|YEAR_SALES={values}|SOURCE={source}")


def release(worker: str) -> None:
    with project_lock():
        rows = load_rows(QUEUE)
        released = 0
        for row in rows:
            if row["status"] == "in_progress" and row.get("worker") == worker:
                row.update(status="pending", worker="", updated_at=now())
                released += 1
        write_csv(QUEUE, QUEUE_FIELDS, rows)
    print(f"released {released} unfinished LOW-review families for {worker}")


def expand_items(raw_items: object) -> list[dict[str, object]]:
    if not isinstance(raw_items, list):
        raise SystemExit("batch JSON must be a list")
    expanded: list[dict[str, object]] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise SystemExit("each batch item must be an object")
        outcome = str(raw.get("outcome", "")).lower()
        if outcome == "updated":
            year_sales = raw.get("year_sales")
            if not isinstance(year_sales, dict) or not year_sales:
                raise SystemExit("updated family item requires non-empty year_sales")
            for year, sales in year_sales.items():
                item = {key: value for key, value in raw.items() if key not in {"year_sales", "YEARS"}}
                item["YEAR"] = str(year)
                item["MODEL_YEAR_US_SALES"] = str(sales)
                expanded.append(item)
        elif outcome == "retained_low":
            years = raw.get("YEARS")
            if not isinstance(years, list) or not years:
                raise SystemExit("retained_low family item requires non-empty YEARS")
            for year in years:
                item = {key: value for key, value in raw.items() if key != "YEARS"}
                item["YEAR"] = str(year)
                expanded.append(item)
        else:
            raise SystemExit(f"invalid second-pass outcome: {outcome}")
    return expanded


def batch_update(path: Path, worker: str) -> None:
    items = expand_items(json.loads(path.read_text(encoding="utf-8")))
    with project_lock():
        queue = load_rows(QUEUE)
        claimed = {row["queue_key"]: row for row in queue if row["status"] == "in_progress" and row.get("worker") == worker}
        expected = {(key, year) for key, row in claimed.items() for year in row["YEARS"].split(";")}
        submitted = {(str(item.get("queue_key", "")), str(item.get("YEAR", ""))) for item in items}
        if submitted != expected:
            raise SystemExit(
                f"batch coverage mismatch; missing={sorted(expected - submitted)[:10]} "
                f"extra={sorted(submitted - expected)[:10]}"
            )

        config = load_config()
        _, cache = read_csv(config["model_year_cache_csv"])
        index = {model_year_key(row): i for i, row in enumerate(cache)}
        reviews = load_rows(REVIEWS)
        reviewed_at = now()
        upgraded = retained = 0
        for item in items:
            claim_row = claimed[str(item["queue_key"])]
            key = (claim_row["MAKE"], claim_row["MODEL"], str(item["YEAR"]))
            if key not in index:
                raise SystemExit(f"cache key not found: {key}")
            current = cache[index[key]]
            if current.get("SOURCE_CONFIDENCE", "").upper() != "LOW":
                raise SystemExit(f"second-pass target is no longer LOW: {key}")
            outcome = str(item.get("outcome", "")).lower()
            note = str(item.get("review_note", "")).strip()
            source_url = str(item.get("SOURCE_URL", "")).strip()
            if not note or not source_url:
                raise SystemExit(f"second-pass item requires SOURCE_URL and review_note: {key}")
            if outcome == "updated":
                confidence = str(item.get("SOURCE_CONFIDENCE", "")).strip().upper()
                period = str(item.get("SALES_PERIOD", "")).strip().upper()
                sales = str(item.get("MODEL_YEAR_US_SALES", "")).strip()
                if confidence not in UPGRADED_CONFIDENCE:
                    raise SystemExit(f"updated LOW item must upgrade to MEDIUM/HIGH: {key}")
                if period not in ALLOWED_PERIOD:
                    raise SystemExit(f"invalid SALES_PERIOD for {key}: {period}")
                parse_nonnegative_integer(sales, "MODEL_YEAR_US_SALES")
                replacement = {field: str(item.get(field, current.get(field, ""))).strip() for field in CACHE_FIELDS}
                replacement.update(
                    MAKE=key[0], MODEL=key[1], YEAR=key[2], MODEL_YEAR_US_SALES=sales,
                    SALES_SCOPE="US", SALES_PERIOD=period, SOURCE_URL=source_url,
                    SOURCE_CONFIDENCE=confidence,
                )
                cache[index[key]] = replacement
                new_confidence = confidence
                upgraded += 1
            elif outcome == "retained_low":
                new_confidence = "LOW"
                retained += 1
            else:
                raise SystemExit(f"invalid outcome for {key}: {outcome}")
            reviews = [row for row in reviews if model_year_key(row) != key]
            reviews.append({
                "MAKE": key[0], "MODEL": key[1], "YEAR": key[2], "outcome": outcome,
                "previous_confidence": "LOW", "new_confidence": new_confidence,
                "source_url": source_url, "reviewed_at": reviewed_at, "note": note,
            })

        write_csv(config["model_year_cache_csv"], CACHE_FIELDS, cache)
        reviews.sort(key=lambda row: (norm(row["MAKE"]), norm(row["MODEL"]), int(row["YEAR"])))
        write_csv(REVIEWS, REVIEW_FIELDS, reviews)
        groups, years = sync_queue()
    print(f"LOW second-pass applied: {upgraded} upgraded, {retained} retained LOW; remaining {groups} families / {years} model-years")


def status() -> None:
    rows = load_rows(QUEUE)
    reviews = load_rows(REVIEWS)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    outcomes = Counter(row.get("outcome", "") for row in reviews)
    print(json.dumps({
        "families": len(rows),
        "model_years": sum(int(row["record_count"]) for row in rows),
        "status": counts,
        "reviewed": len(reviews),
        "outcomes": outcomes,
    }, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Second-pass review queue for LOW-confidence US sales cache rows")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    p = sub.add_parser("claim"); p.add_argument("--limit", type=int, default=8); p.add_argument("--max-years", type=int, default=60); p.add_argument("--worker", required=True)
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
