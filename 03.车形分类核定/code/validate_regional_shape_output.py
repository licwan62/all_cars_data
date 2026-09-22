from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "01.整理尺寸库" / "output" / "尺寸库.csv"
OUTPUT = PROJECT / "output" / "车形分类.csv"
QUEUE = PROJECT / "research_queue" / "regional_queue.csv"
REPORT = PROJECT / "output" / "validation_report.json"
ALLOWED = {"DUAL", "H0", "H1", "H2", "H3", "JP", "P0", "P1", "P2", "SD0", "SD1", "SD2", "SU0", "SU1", "SU2", "V0", "V1", "dodge-challenger"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def region(record_id: str) -> str:
    suffix = record_id.rsplit(" ", 1)[-1].upper()
    return suffix if suffix in {"US", "EU", "RU"} else "US"


def main() -> None:
    source = read(SOURCE)
    output = read(OUTPUT)
    queue = read(QUEUE)
    source_ids = [row["DIMENSION-ID"] for row in source]
    output_ids = [row["DIMENSION-ID"] for row in output]
    checks = {
        "source_ids_unique": len(source_ids) == len(set(source_ids)),
        "output_ids_unique": len(output_ids) == len(set(output_ids)),
        "complete_source_coverage": set(output_ids) == set(source_ids),
        "country_matches_id": all(row["COUNTRY"] == region(row["DIMENSION-ID"]) for row in output),
        "allowed_shapes_only": all(row["车形"] in ALLOWED for row in output),
        "no_blank_shape_or_status": all(row["车形"] and row["处理状态"] for row in output),
        "queue_is_output_subset": {row["DIMENSION-ID"] for row in queue} <= set(output_ids),
        "all_us_rows_nuclear": all(row["处理状态"] == "US核定" for row in output if row["COUNTRY"] == "US"),
    }
    report = {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "source_rows": len(source),
        "output_rows": len(output),
        "review_queue_rows": len(queue),
        "by_country": dict(Counter(row["COUNTRY"] for row in output)),
        "by_status": dict(Counter(row["处理状态"] for row in output)),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
