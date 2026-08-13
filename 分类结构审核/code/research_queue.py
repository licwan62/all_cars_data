from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
SOURCE_DIR = ROOT / "source"
ARTIFACTS = PROJECT / "artifacts"
QUEUE_DIR = PROJECT / "research_queue"
QUEUE_FILE = QUEUE_DIR / "queue.csv"
CHECKPOINT_FILE = QUEUE_DIR / "checkpoint.json"
PROGRESS_FILE = QUEUE_DIR / "progress_report.json"
FIELDS = ["queue_key", "DIMENSION-ID", "MAKE", "MODEL", "版本", "YEAR", "issue_type", "current_structure", "suspected_structure", "status", "worker", "suggested_structure", "suggested_category", "confidence", "source_url", "note", "updated_at"]
STATUSES = {"pending", "in_progress", "done", "blocked"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def key(record_id: str, issue_type: str, detail: str) -> str:
    raw = f"{record_id}\x1f{issue_type}\x1f{detail}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def atomic_write(rows: list[dict[str, str]]) -> None:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    temp = QUEUE_FILE.with_suffix(".csv.tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    replace_with_retry(temp, QUEUE_FILE)
    counts = {status: sum(r.get("status") == status for r in rows) for status in sorted(STATUSES)}
    checkpoint = {"updated_at": now(), "total": len(rows), "counts": counts}
    temp_json = CHECKPOINT_FILE.with_suffix(".json.tmp")
    temp_json.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        replace_with_retry(temp_json, CHECKPOINT_FILE)
    except PermissionError:
        # queue.csv is the source of truth. Some editors briefly lock the
        # checkpoint on Windows; leaving the fresh .tmp snapshot is recoverable.
        print(f"警告：checkpoint 被占用，最新快照保留在 {temp_json}")
    issue_types = {}
    done_categories = {}
    blocked_models = {}
    for row in rows:
        issue = row.get("issue_type", "")
        issue_types[issue] = issue_types.get(issue, 0) + 1
        if row.get("status") == "done":
            category = row.get("suggested_category", "")
            if category:
                done_categories[category] = done_categories.get(category, 0) + 1
        elif row.get("status") == "blocked":
            model = " ".join(part for part in (row.get("MAKE", ""), row.get("MODEL", "")) if part)
            blocked_models[model] = blocked_models.get(model, 0) + 1
    progress = {
        "total": len(rows),
        "status": {status: counts[status] for status in ("done", "blocked", "pending", "in_progress")},
        "issue_type": issue_types,
        "done_categories": done_categories,
        "blocked_manual_review": blocked_models,
        "note": "queue.csv 是状态源；artifacts 需通过 regenerate_artifacts.py 重建同步。",
    }
    temp_progress = PROGRESS_FILE.with_suffix(".json.tmp")
    temp_progress.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        replace_with_retry(temp_progress, PROGRESS_FILE)
    except PermissionError:
        print(f"警告：progress_report 被占用，最新快照保留在 {temp_progress}")


def replace_with_retry(source: Path, target: Path, attempts: int = 8) -> None:
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.15 * (attempt + 1))


def candidate_rows() -> list[dict[str, str]]:
    result = []
    source_by_id = {row.get("DIMENSION-ID", ""): row for row in read_rows(SOURCE_DIR / "车型尺寸库.csv")}
    sources = [
        (ARTIFACTS / "audit_table1_corrections.csv", "correction", "原结构", "建议结构", "修改原因"),
        (ARTIFACTS / "audit_table3_uncertain.csv", "uncertain", "当前结构", "疑似结构", "问题"),
        (ARTIFACTS / "audit_table4_split.csv", "split", "当前结构", "建议结构", "拆分原因"),
        (ARTIFACTS / "audit_table5_other.csv", "other", "当前值", "", "疑似问题"),
    ]
    for path, issue_type, current_col, suspected_col, detail_col in sources:
        for row in read_rows(path):
            source = source_by_id.get(row.get("DIMENSION-ID", ""), {})
            if issue_type == "uncertain" and source.get("MAKE") == "Chevrolet" and source.get("MODEL") == "Suburban":
                # Existing correction queue rows are retained as blocked/manual
                # review items; do not duplicate the same record from table 3.
                continue
            detail = row.get(detail_col, "")
            result.append({
                "queue_key": key(row.get("DIMENSION-ID", ""), issue_type, detail),
                "DIMENSION-ID": row.get("DIMENSION-ID", ""), "MAKE": source.get("MAKE", ""),
                "MODEL": source.get("MODEL", ""), "版本": source.get("版本", ""), "YEAR": source.get("YEAR", ""),
                "issue_type": issue_type, "current_structure": row.get(current_col, "") or source.get("结构", ""),
                "suspected_structure": row.get(suspected_col, ""), "status": "pending", "worker": "",
                "suggested_structure": "", "confidence": "", "source_url": "", "note": detail, "updated_at": now(),
            })
    return result


def init_queue() -> None:
    existing = {row["queue_key"]: row for row in read_rows(QUEUE_FILE)}
    for row in candidate_rows():
        existing.setdefault(row["queue_key"], row)
    source_rows = {row.get("DIMENSION-ID", ""): row for row in read_rows(SOURCE_DIR / "车型尺寸库.csv")}
    for row in existing.values():
        source = source_rows.get(row.get("DIMENSION-ID", ""), {})
        for field in ("MAKE", "MODEL", "版本", "YEAR"):
            if not row.get(field):
                row[field] = source.get(field, "")
    rows = sorted(existing.values(), key=lambda r: (r.get("status", ""), r.get("issue_type", ""), r.get("DIMENSION-ID", "")))
    atomic_write(rows)
    print(f"队列已就绪：{len(rows)} 条，文件 {QUEUE_FILE}")


def claim(limit: int, worker: str) -> None:
    rows = read_rows(QUEUE_FILE)
    claimed = []
    for row in rows:
        if row.get("status") == "pending" and len(claimed) < limit:
            row.update(status="in_progress", worker=worker, updated_at=now())
            claimed.append(row)
    atomic_write(rows)
    print(json.dumps(claimed, ensure_ascii=False, indent=2))


def update(queue_key: str, **changes: str) -> None:
    rows = read_rows(QUEUE_FILE)
    target = next((row for row in rows if row.get("queue_key") == queue_key), None)
    if target is None:
        raise SystemExit(f"找不到 queue_key: {queue_key}")
    if changes.get("status") not in STATUSES:
        raise SystemExit(f"非法状态: {changes.get('status')}")
    target.update({k: v for k, v in changes.items() if v is not None})
    target["updated_at"] = now()
    atomic_write(rows)


def batch_update(path: Path) -> None:
    rows = read_rows(QUEUE_FILE)
    by_key = {row.get("queue_key", ""): row for row in rows}
    updates = json.loads(path.read_text(encoding="utf-8"))
    missing = []
    for item in updates:
        target = by_key.get(item.get("queue_key", ""))
        if target is None:
            missing.append(item.get("queue_key", ""))
            continue
        status = item.get("status", "done")
        if status not in STATUSES:
            raise SystemExit(f"非法状态: {status}")
        target.update({k: str(v) for k, v in item.items() if k in FIELDS and k != "queue_key" and v is not None})
        target["status"] = status
        target["updated_at"] = now()
    if missing:
        raise SystemExit(f"找不到 queue_key: {missing}")
    atomic_write(rows)
    print(f"批量更新完成：{len(updates)} 条")


def main() -> None:
    parser = argparse.ArgumentParser(description="可断点维护的车型结构研究队列")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    claim_parser = sub.add_parser("claim")
    claim_parser.add_argument("--limit", type=int, default=10)
    claim_parser.add_argument("--worker", required=True)
    update_parser = sub.add_parser("update")
    update_parser.add_argument("--key", required=True)
    update_parser.add_argument("--status", required=True, choices=sorted(STATUSES))
    update_parser.add_argument("--worker")
    update_parser.add_argument("--suggested-structure")
    update_parser.add_argument("--suggested-category")
    update_parser.add_argument("--confidence")
    update_parser.add_argument("--source-url")
    update_parser.add_argument("--note")
    batch_parser = sub.add_parser("batch-update")
    batch_parser.add_argument("--file", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "init":
        init_queue()
    elif args.command == "claim":
        claim(args.limit, args.worker)
    elif args.command == "update":
        update(args.key, status=args.status, worker=args.worker, suggested_structure=args.suggested_structure,
               suggested_category=args.suggested_category, confidence=args.confidence,
               source_url=args.source_url, note=args.note)
    else:
        batch_update(args.file)


if __name__ == "__main__":
    main()
