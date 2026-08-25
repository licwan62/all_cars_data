from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from review_year_generation import (
    IDENTITY,
    audit_gaps,
    audit_generations,
    audit_interval_conflicts,
    dimension_id,
    ensure_not_source,
    merged_row,
    within_envelope,
    write_csv,
    years,
)


DIMENSIONS = ("L-IN", "W-IN", "H-IN")
RESEARCH_DECISIONS = {"RESEARCH_BRANCH_GAP", "RESEARCH_MODEL_YEAR_GAP"}

# 已知并非漏数的年款空档。即使采用宽松终核，也不得自动补齐。
KNOWN_HIATUS = {
    ("Dodge", "Viper", "", "Coupe", "2007"): "2006 与 2008 年款之间为产品空档，不按尺寸相同补年。",
    ("Porsche", "911", "GT3 RS", "Coupe", "2017-2018"): "高性能衍生版本并非逐年连续销售，保留年款空档。",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="以宽松但可追溯的规则推进待终核年份缺口。")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--gap-report", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--single-year-tolerance", type=Decimal, default=Decimal("1.0"))
    parser.add_argument("--two-year-tolerance", type=Decimal, default=Decimal("0.3"))
    return parser.parse_args()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def missing_count(value: str) -> int:
    start, end = years(value)
    return end - start + 1


def identity_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in IDENTITY)


def gap_key(row: dict[str, str]) -> tuple[str, ...]:
    return (*identity_key(row), row["LEFT_YEAR"], row["RIGHT_YEAR"], row["MISSING_YEAR"])


def main() -> None:
    args = parse_args()
    ensure_not_source(args.package)
    args.package.mkdir(parents=True, exist_ok=True)

    fields, rows = read_csv(args.input)
    _, gap_rows = read_csv(args.gap_report)
    input_count = len(rows)

    index: dict[tuple[tuple[str, ...], str, str], int] = {}
    for position, row in enumerate(rows):
        key = (identity_key(row), row.get("代际", ""), row["YEAR"])
        if key in index:
            raise SystemExit(f"相同身份/代际/YEAR 出现多条记录，无法确定缺口两侧：{key}")
        index[key] = position

    parent = list(range(len(rows)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    applied_candidates: list[dict[str, str]] = []
    retained_candidates: list[dict[str, str]] = []
    for gap in gap_rows:
        if gap.get("DECISION") not in RESEARCH_DECISIONS:
            retained_candidates.append({**gap, "FINAL_REVIEW_DECISION": "RETAIN_PRIOR_DECISION"})
            continue

        hiatus_reason = KNOWN_HIATUS.get(
            (gap["MAKE"], gap["MODEL"], gap.get("版本", ""), gap.get("结构", ""), gap["MISSING_YEAR"])
        )
        if hiatus_reason:
            retained_candidates.append({**gap, "FINAL_REVIEW_DECISION": "RETAIN_KNOWN_HIATUS", "FINAL_REVIEW_REASON": hiatus_reason})
            continue

        count = missing_count(gap["MISSING_YEAR"])
        tolerance = args.single_year_tolerance if count == 1 else args.two_year_tolerance if count == 2 else None
        if tolerance is None:
            retained_candidates.append({**gap, "FINAL_REVIEW_DECISION": "RETAIN_LONG_GAP"})
            continue

        generation = gap.get("LEFT_GENERATION", "")
        if not generation or generation != gap.get("RIGHT_GENERATION", ""):
            retained_candidates.append({**gap, "FINAL_REVIEW_DECISION": "RETAIN_GENERATION_BOUNDARY"})
            continue

        left_index = index.get((identity_key(gap), generation, gap["LEFT_YEAR"]))
        right_index = index.get((identity_key(gap), generation, gap["RIGHT_YEAR"]))
        if left_index is None or right_index is None:
            retained_candidates.append({**gap, "FINAL_REVIEW_DECISION": "RETAIN_UNMATCHED_SIDE"})
            continue

        left, right = rows[left_index], rows[right_index]
        if left.get("分类", "") != right.get("分类", ""):
            retained_candidates.append({**gap, "FINAL_REVIEW_DECISION": "RETAIN_CLASSIFICATION_CHANGE"})
            continue
        try:
            stable = within_envelope([left, right], tolerance)
        except (InvalidOperation, KeyError):
            stable = False
        if not stable:
            retained_candidates.append(
                {
                    **gap,
                    "FINAL_REVIEW_DECISION": "RETAIN_DIMENSION_CHANGE",
                    "FINAL_REVIEW_REASON": f"缺口两侧三维包络超过 {tolerance} in。",
                }
            )
            continue

        union(left_index, right_index)
        applied_candidates.append(
            {
                **gap,
                "FINAL_REVIEW_DECISION": "BRIDGE_AND_MERGE",
                "FINAL_REVIEW_REASON": f"同代同分支，缺口 {count} 年，左右三维包络均不超过 {tolerance} in。",
            }
        )

    components: dict[int, list[int]] = {}
    for position in range(len(rows)):
        components.setdefault(find(position), []).append(position)

    output_rows: list[dict[str, str]] = []
    changes: list[dict[str, str]] = []
    for positions in components.values():
        members = [rows[position] for position in positions]
        if len(members) == 1:
            output_rows.append(members[0])
            continue
        merged = merged_row(members)
        output_rows.append(merged)
        changes.append(
            {
                "ACTION": "BRIDGE_GAP_AND_MERGE",
                "DIMENSION_IDS_BEFORE": " | ".join(row["DIMENSION-ID"] for row in members),
                "DIMENSION_ID_AFTER": merged["DIMENSION-ID"],
                "FIELD": "YEAR,L-IN,W-IN,H-IN",
                "YEARS_BEFORE": " | ".join(row["YEAR"] for row in members),
                "YEAR_AFTER": merged["YEAR"],
                "DIMENSIONS_BEFORE": " | ".join("x".join(row[field] for field in DIMENSIONS) for row in members),
                "DIMENSIONS_AFTER": "x".join(merged[field] for field in DIMENSIONS),
                "REASON": "宽松终核：同代同分支的短年份缺口，两侧外廓稳定，按连续年款并段。",
                "EVIDENCE": "上一轮 gap_candidates 与缺口两侧三维记录。",
            }
        )

    output_rows.sort(key=lambda row: (row["MAKE"], row["MODEL"], row.get("版本", ""), years(row["YEAR"]), row.get("结构", "")))
    gaps_after = audit_gaps(output_rows)
    generation_findings = audit_generations(output_rows)
    interval_conflicts = audit_interval_conflicts(output_rows, Decimal("0.1"))
    output_ids = [row["DIMENSION-ID"] for row in output_rows]
    duplicate_ids = sorted(item for item, count in Counter(output_ids).items() if count > 1)
    id_mismatches = [row["DIMENSION-ID"] for row in output_rows if row["DIMENSION-ID"] != dimension_id(row)]
    unresolved_generation = [item for item in generation_findings if item.get("DECISION") == "REVIEW_ONLY"]
    unresolved_conflicts = [item for item in interval_conflicts if item.get("DECISION") == "REVIEW_ONLY"]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": not duplicate_ids and not id_mismatches and not unresolved_generation and not unresolved_conflicts,
        "input": str(args.input.resolve()),
        "gap_report": str(args.gap_report.resolve()),
        "input_rows": input_count,
        "output_rows": len(output_rows),
        "rows_reduced": input_count - len(output_rows),
        "gap_repairs_applied": len(applied_candidates),
        "merge_groups": len(changes),
        "single_year_tolerance_in": str(args.single_year_tolerance),
        "two_year_tolerance_in": str(args.two_year_tolerance),
        "remaining_gap_candidates": len(gaps_after),
        "remaining_research_branch_gaps": sum(item.get("DECISION") == "RESEARCH_BRANCH_GAP" for item in gaps_after),
        "remaining_research_model_year_gaps": sum(item.get("DECISION") == "RESEARCH_MODEL_YEAR_GAP" for item in gaps_after),
        "unresolved_generation_findings": len(unresolved_generation),
        "unresolved_interval_conflicts": len(unresolved_conflicts),
        "duplicate_dimension_ids": duplicate_ids,
        "dimension_id_mismatches": id_mismatches,
        "source_directory_written": False,
    }

    change_fields = [
        "ACTION", "DIMENSION_IDS_BEFORE", "DIMENSION_ID_AFTER", "FIELD", "YEARS_BEFORE", "YEAR_AFTER",
        "DIMENSIONS_BEFORE", "DIMENSIONS_AFTER", "REASON", "EVIDENCE",
    ]
    review_fields = [*gap_rows[0].keys(), "FINAL_REVIEW_DECISION", "FINAL_REVIEW_REASON"] if gap_rows else []
    write_csv(args.package / "correct.csv", fields, output_rows)
    write_csv(args.package / "changes.csv", change_fields, changes)
    write_csv(args.package / "applied_gap_repairs.csv", review_fields, applied_candidates)
    write_csv(args.package / "retained_gap_reviews.csv", review_fields, retained_candidates)
    write_csv(args.package / "gap_candidates.csv", list(gaps_after[0].keys()) if gaps_after else [], gaps_after)
    write_csv(args.package / "generation_findings.csv", list(generation_findings[0].keys()) if generation_findings else [], generation_findings)
    write_csv(args.package / "interval_conflicts.csv", list(interval_conflicts[0].keys()) if interval_conflicts else [], interval_conflicts)
    (args.package / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
