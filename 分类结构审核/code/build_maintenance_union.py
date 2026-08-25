from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
SOURCE_DIR = (ROOT / "source").resolve()
DEFAULT_OUTPUT = PROJECT / "artifacts" / "maintenance_union" / "车型尺寸库_规范合并.csv"

FIELDS = [
    "DIMENSION-ID",
    "MAKE",
    "MODEL",
    "版本",
    "CAB",
    "BED",
    "结构",
    "代际",
    "YEAR",
    "分类",
    "L-IN",
    "W-IN",
    "H-IN",
    "参考车型",
    "备注",
    "迭代状态",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="合并人工维护的普通车与老爷车数据；不会写入 source 目录。"
    )
    parser.add_argument("--normal", required=True, type=Path, help="普通车 CSV")
    parser.add_argument("--classic", required=True, type=Path, help="老爷车 CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="规范合并 CSV")
    parser.add_argument("--provenance-output", type=Path, help="来源旁表 CSV")
    parser.add_argument("--validation-output", type=Path, help="校验报告 JSON")
    return parser.parse_args()


def is_within(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory)
        return True
    except ValueError:
        return False


def assert_safe_output(path: Path) -> None:
    if is_within(path, SOURCE_DIR):
        raise ValueError(f"拒绝写入 source 目录：{path.resolve()}")


def read_rows(path: Path, segment: str) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        rows = []
        for source_row, row in enumerate(reader, start=2):
            clean = {field: (row.get(field) or "").strip() for field in FIELDS}
            clean["__segment"] = segment
            clean["__source_file"] = str(path.resolve())
            clean["__source_row"] = str(source_row)
            rows.append(clean)
    return header, rows


def year_interval(value: str) -> tuple[int, int]:
    parts = value.split("-", 1)
    if len(parts) == 1:
        year = int(parts[0])
        return year, year
    return int(parts[0]), int(parts[1])


def identity_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[field] for field in ("MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际"))


def escape_id_value(value: str) -> str:
    return (value or "").strip().replace("%", "%25").replace("|", "%7C")


def expected_dimension_id(row: dict[str, str]) -> str:
    parts = [
        ("MAKE", "MAKE"),
        ("MODEL", "MODEL"),
        ("VERSION", "版本"),
        ("STRUCTURE", "结构"),
        ("YEAR", "YEAR"),
    ]
    if row.get("分类") == "皮卡":
        parts.extend((("CAB", "CAB"), ("BED", "BED")))
    return "|".join(f"{label}={escape_id_value(row.get(field, ''))}" for label, field in parts)


def validate(
    normal_header: list[str],
    classic_header: list[str],
    rows: list[dict[str, str]],
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    checks: list[dict[str, object]] = []

    for segment, header in (("normal", normal_header), ("classic", classic_header)):
        passed = header == FIELDS
        checks.append({"check": f"{segment}_schema", "passed": passed, "actual": header})
        if not passed:
            errors.append(f"{segment} 表头必须与规范 16 字段完全一致")

    mixed = [row["DIMENSION-ID"] for row in rows if "/" in row["结构"]]
    checks.append({"check": "atomic_structure", "passed": not mixed, "examples": mixed[:20]})
    if mixed:
        errors.append(f"发现 {len(mixed)} 条复合结构；维护输入必须一行一种结构")

    mismatched_ids = [
        {"actual": row["DIMENSION-ID"], "expected": expected_dimension_id(row)}
        for row in rows
        if row["DIMENSION-ID"] != expected_dimension_id(row)
    ]
    checks.append(
        {
            "check": "dimension_id_matches_fields",
            "passed": not mismatched_ids,
            "examples": mismatched_ids[:20],
        }
    )
    if mismatched_ids:
        errors.append(f"发现 {len(mismatched_ids)} 条 DIMENSION-ID 与身份字段不一致")

    blank_ids = [row["__source_row"] for row in rows if not row["DIMENSION-ID"]]
    id_counts = Counter(row["DIMENSION-ID"] for row in rows if row["DIMENSION-ID"])
    duplicate_ids = sorted(key for key, count in id_counts.items() if count > 1)
    checks.append(
        {
            "check": "dimension_id_unique",
            "passed": not blank_ids and not duplicate_ids,
            "blank_rows": blank_ids[:20],
            "duplicate_examples": duplicate_ids[:20],
        }
    )
    if blank_ids or duplicate_ids:
        errors.append(f"DIMENSION-ID 空值 {len(blank_ids)} 条、重复 {len(duplicate_ids)} 组")

    invalid_years: list[str] = []
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        try:
            start, end = year_interval(row["YEAR"])
            if start > end:
                raise ValueError
            row["__year_start"], row["__year_end"] = str(start), str(end)
        except (TypeError, ValueError):
            invalid_years.append(row["DIMENSION-ID"])
            continue
        grouped[identity_key(row)].append(row)

    overlaps: list[dict[str, str]] = []
    for group in grouped.values():
        ordered = sorted(group, key=lambda row: (int(row["__year_start"]), int(row["__year_end"])))
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                if int(right["__year_start"]) > int(left["__year_end"]):
                    break
                if left["__segment"] != right["__segment"]:
                    overlaps.append(
                        {
                            "normal_or_classic_a": left["__segment"],
                            "id_a": left["DIMENSION-ID"],
                            "normal_or_classic_b": right["__segment"],
                            "id_b": right["DIMENSION-ID"],
                        }
                    )
    checks.append(
        {
            "check": "year_format_and_cross_segment_non_overlap",
            "passed": not invalid_years and not overlaps,
            "invalid_year_examples": invalid_years[:20],
            "overlap_examples": overlaps[:20],
        }
    )
    if invalid_years:
        errors.append(f"YEAR 格式错误 {len(invalid_years)} 条；仅接受 YYYY 或 YYYY-YYYY")
    if overlaps:
        errors.append(f"普通车与老爷车存在 {len(overlaps)} 组同身份年份重叠")

    report: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": not errors,
        "row_count": len(rows),
        "segment_counts": dict(Counter(row["__segment"] for row in rows)),
        "checks": checks,
        "errors": errors,
    }
    return report, errors


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    provenance = (args.provenance_output or output.with_suffix(".provenance.csv")).resolve()
    validation = (args.validation_output or output.with_suffix(".validation.json")).resolve()
    for path in (output, provenance, validation):
        assert_safe_output(path)
    output_paths = {output, provenance, validation}
    if len(output_paths) != 3:
        raise ValueError("合并表、来源旁表和校验报告必须使用三个不同路径")
    input_paths = {args.normal.resolve(), args.classic.resolve()}
    if output_paths & input_paths:
        raise ValueError("输出路径不得覆盖任一人工维护输入")

    normal_header, normal_rows = read_rows(args.normal, "normal")
    classic_header, classic_rows = read_rows(args.classic, "classic")
    rows = normal_rows + classic_rows
    report, errors = validate(normal_header, classic_header, rows)

    validation.parent.mkdir(parents=True, exist_ok=True)
    validation.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if errors:
        raise SystemExit("合并已中止：" + "；".join(errors) + f"。详见 {validation}")

    write_csv(output, FIELDS, rows)
    provenance_rows = [
        {
            "DIMENSION-ID": row["DIMENSION-ID"],
            "SOURCE_SEGMENT": row["__segment"],
            "SOURCE_FILE": row["__source_file"],
            "SOURCE_ROW": row["__source_row"],
        }
        for row in rows
    ]
    write_csv(
        provenance,
        ["DIMENSION-ID", "SOURCE_SEGMENT", "SOURCE_FILE", "SOURCE_ROW"],
        provenance_rows,
    )
    print(json.dumps({"output": str(output), "provenance": str(provenance), **report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
