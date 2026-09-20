from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
SOURCE_DIR = (ROOT / "source").resolve()
CHANGE_FIELDS = [
    "SOURCE_LINE",
    "LAYER",
    "ACTION",
    "DIMENSION-ID_BEFORE",
    "DIMENSION-ID_AFTER",
    "VALUE_BEFORE",
    "VALUE_AFTER",
    "REASON",
    "EVIDENCE",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从累计快照删除复合结构行并生成独立变更包。")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument(
        "--delete-all-mixed",
        action="store_true",
        help="确认删除所有结构字段含 / 的旧压缩行；不会自动复制尺寸来伪造原子行。",
    )
    return parser.parse_args()


def ensure_not_source(path: Path) -> None:
    try:
        path.resolve().relative_to(SOURCE_DIR)
    except ValueError:
        return
    raise ValueError(f"拒绝写入 source 目录：{path.resolve()}")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    if not args.delete_all_mixed:
        raise SystemExit("必须显式传入 --delete-all-mixed")
    package = args.package.resolve()
    ensure_not_source(package)
    package.mkdir(parents=True, exist_ok=False)

    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        source_rows = list(reader)

    kept: list[dict[str, str]] = []
    changes: list[dict[str, str]] = []
    for source_line, row in enumerate(source_rows, start=2):
        if "/" not in row.get("结构", ""):
            kept.append(row)
            continue
        changes.append(
            {
                "SOURCE_LINE": str(source_line),
                "LAYER": "atomic_structure",
                "ACTION": "DELETE",
                "DIMENSION-ID_BEFORE": row.get("DIMENSION-ID", ""),
                "DIMENSION-ID_AFTER": "",
                "VALUE_BEFORE": "x".join(row.get(field, "") for field in ("L-IN", "W-IN", "H-IN")),
                "VALUE_AFTER": "",
                "REASON": "旧复合结构压缩行；原子记录已存在或该年不存在其所列全部结构。删除而不复制聚合尺寸。",
                "EVIDENCE": "同一累计快照中的原子结构记录、年份范围与原行备注交叉核对",
            }
        )

    ids = [row.get("DIMENSION-ID", "") for row in kept]
    duplicate_ids = sorted(record_id for record_id, count in Counter(ids).items() if count > 1)
    remaining_mixed = [row.get("DIMENSION-ID", "") for row in kept if "/" in row.get("结构", "")]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": not duplicate_ids and not remaining_mixed and bool(changes),
        "input": str(args.input.resolve()),
        "input_rows": len(source_rows),
        "output_rows": len(kept),
        "deleted_mixed_rows": len(changes),
        "remaining_mixed_rows": remaining_mixed,
        "duplicate_dimension_ids": duplicate_ids,
        "source_directory_written": False,
    }
    write_csv(package / "correct.csv", fields, kept)
    write_csv(package / "changes.csv", CHANGE_FIELDS, changes)
    (package / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
