from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
SOURCE_DIR = (ROOT / "source").resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from id_scheme import dimension_id


DIMENSIONS = ("L-IN", "W-IN", "H-IN")
IDENTITY = ("MAKE", "MODEL", "版本", "CAB", "BED", "结构")
MERGE_CONTEXT = ("代际", "分类")
KNOWN_PARALLEL_BOUNDARIES = {
    ("Jaguar", "XJ", "gen1", "gen2", "1988-1992"): (
        "Series III 与 XJ40 在该区间并行，保留两代重叠。",
        "Jaguar Heritage 车型时间线",
    ),
    ("Jeep", "Wrangler", "gen3", "gen4", "2018"): (
        "2018 model year 同时存在 JK 与 JL，属于正常换代并售。",
        "Jeep/Stellantis 2018 Wrangler 产品资料",
    ),
    ("Mercedes-Benz", "SL-Class", "gen1", "gen2", "1963"): (
        "300 SL 末期与 W113 首年同为 1963，属于正常交接。",
        "Mercedes-Benz Public Archive 车型时间线",
    ),
}
KNOWN_GAPS = {
    ("Hyundai", "Tiburon", "", "Coupe", "2002"): ("北美年款换代空档。", "Hyundai 车型年款时间线"),
    ("Jeep", "Wrangler", "2dr", "SUV", "1996"): ("Wrangler 没有 1996 model year，YJ 与 TJ 在此交接。", "Jeep/Stellantis Wrangler 历史资料"),
    ("Kia", "Carnival", "Sedona LWB", "MPV", "2013"): ("美国 Sedona 跳过 2013 model year。", "Kia 美国年款资料"),
    ("Land Rover", "Defender", "90 NAS", "SUV", "1996"): ("NAS Defender 90 的 1995 与 1997 之间没有 1996 model year。", "Land Rover NAS Defender 年款资料"),
    ("Mitsubishi", "Eclipse Cross", "", "Crossover", "2021"): ("美国市场跳过 2021 model year 后以改款车型恢复。", "Mitsubishi Motors North America 年款资料"),
    ("Mitsubishi", "i-MiEV", "", "Hatchback", "2013"): ("美国市场 i-MiEV 年款销售空档。", "Mitsubishi Motors North America 年款资料"),
    ("Mitsubishi", "i-MiEV", "", "Hatchback", "2015"): ("美国市场 i-MiEV 年款销售空档。", "Mitsubishi Motors North America 年款资料"),
    ("Mitsubishi", "Mirage", "", "Hatchback", "2016"): ("美国市场在改款前跳过 2016 model year。", "Mitsubishi Motors North America 年款资料"),
    ("Nissan", "GT-R", "NISMO", "Coupe", "2022"): ("NISMO 分支并非每个 GT-R 年款都在美国连续销售。", "Nissan USA GT-R NISMO 年款资料"),
    ("Porsche", "911", "GT3", "Coupe", "2009"): ("GT3 分支的美国年款空档。", "Porsche Newsroom 911 GT3 车型时间线"),
    ("Porsche", "911", "GT3 RS", "Coupe", "2009"): ("GT3 RS 分支的美国年款空档。", "Porsche Newsroom 911 GT3 RS 车型时间线"),
    ("Porsche", "911", "GT3", "Coupe", "2017"): ("991.1 与 991.2 GT3 的美国年款交接空档。", "Porsche Newsroom 911 GT3 车型时间线"),
    ("Porsche", "Cayenne", "", "SUV", "2007"): ("第一代与改款 Cayenne 的美国年款空档。", "Porsche Newsroom Cayenne 车型时间线"),
}
KNOWN_MODEL_GENERATION_OVERLAPS = {
    ("BMW", "2 Series", 1, 2): "Coupe/Convertible/Gran Coupe 分支换代不同步。",
    ("BMW", "3 Series", 5, 6): "新一代 Sedan 上市时上一代 Coupe/Convertible 继续销售。",
    ("BMW", "6 Series", 3, 4): "Gran Turismo 与 Coupe/Convertible 分支代际口径并行。",
    ("Cadillac", "CTS", 2, 3): "第二代 Coupe 延续到第三代 Sedan 上市之后。",
    ("Chevrolet", "Blazer", 1, 2): "K5/full-size、S-10 compact 与现代 crossover 为名称复用的不同产品线。",
    ("Chevrolet", "Blazer", 2, 3): "K5/full-size、S-10 compact 与现代 crossover 为名称复用的不同产品线。",
    ("Chevrolet", "C/K", 3, 4): "旧 R/V 系列与 GMT400 新 C/K 在过渡期并行。",
    ("Ford", "Explorer", 2, 3): "Explorer Sport Trac pickup 与 SUV 主线使用不同换代边界。",
    ("Hyundai", "Elantra", 4, 5): "Elantra Touring/Hatchback 与 Sedan 换代不同步。",
    ("Jaguar", "XJ", 1, 2): "Series III 与 XJ40 并行生产。",
    ("Lexus", "IS", 2, 3): "第二代 Convertible 延续到第三代 Sedan 上市之后。",
    ("Mercedes-Benz", "C-Class", 4, 5): "上一代 Coupe 分支延续到新一代 Sedan 上市之后。",
    ("Saturn", "S-Series", 2, 3): "Sedan/Wagon 与 Coupe 的换代年口径不同。",
    ("Toyota", "Land Cruiser", 1, 2): "40 Series 与 60 Series 在产品线中并行。",
    ("Toyota", "RAV4", 3, 4): "第三代衍生分支与第四代主线年款并行。",
    ("Toyota", "Yaris", 2, 3): "Hatchback 与 iA/Sedan 产品线换代口径不同。",
    ("Volkswagen", "Jetta", 5, 6): "Jetta SportWagen 与 Sedan 换代不同步。",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="审计年份/代际并安全合并连续同外廓记录。")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--tolerance", type=Decimal, default=Decimal("0.1"))
    parser.add_argument("--apply-safe-merges", action="store_true")
    parser.add_argument("--generation-decisions", type=Path, help="已确认的代际年份规则 JSON")
    parser.add_argument("--identity-decisions", type=Path, help="已确认的 VERSION 等身份区分规则 JSON")
    return parser.parse_args()


def ensure_not_source(path: Path) -> None:
    try:
        path.resolve().relative_to(SOURCE_DIR)
    except ValueError:
        return
    raise ValueError(f"拒绝写入 source 目录：{path.resolve()}")


def years(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", value.strip())
    if not match:
        raise ValueError(value)
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if start > end:
        raise ValueError(value)
    return start, end


def generation_number(value: str) -> int | None:
    match = re.fullmatch(r"gen(\d+)", value.strip(), re.IGNORECASE)
    return int(match.group(1)) if match else None


def decimals(row: dict[str, str]) -> tuple[Decimal, Decimal, Decimal] | None:
    try:
        return tuple(Decimal(row[field]) for field in DIMENSIONS)  # type: ignore[return-value]
    except (InvalidOperation, KeyError):
        return None


def within_envelope(rows: list[dict[str, str]], tolerance: Decimal) -> bool:
    values = [decimals(row) for row in rows]
    if any(value is None for value in values):
        return False
    return all(max(value[index] for value in values if value) - min(value[index] for value in values if value) <= tolerance for index in range(3))


def unique_join(rows: list[dict[str, str]], field: str) -> str:
    values: list[str] = []
    for row in rows:
        value = row.get(field, "").strip()
        if value and value not in values:
            values.append(value)
    return " | ".join(values)


def merged_row(rows: list[dict[str, str]]) -> dict[str, str]:
    result = dict(rows[0])
    starts_ends = [years(row["YEAR"]) for row in rows]
    start = min(item[0] for item in starts_ends)
    end = max(item[1] for item in starts_ends)
    result["YEAR"] = str(start) if start == end else f"{start}-{end}"
    for field in DIMENSIONS:
        result[field] = max(rows, key=lambda row: Decimal(row[field]))[field]
    for field in ("参考车型", "备注", "迭代状态"):
        result[field] = unique_join(rows, field)
    result["DIMENSION-ID"] = dimension_id(result)
    return result


def find_merge_groups(rows: list[dict[str, str]], tolerance: Decimal) -> list[list[int]]:
    grouped: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[tuple(row.get(field, "") for field in IDENTITY + MERGE_CONTEXT)].append(index)

    result: list[list[int]] = []
    for indices in grouped.values():
        ordered = sorted(indices, key=lambda index: years(rows[index]["YEAR"]))
        cluster: list[int] = []
        cluster_end = -1
        for index in ordered:
            start, end = years(rows[index]["YEAR"])
            proposed = cluster + [index]
            if cluster and start <= cluster_end + 1 and within_envelope([rows[item] for item in proposed], tolerance):
                cluster = proposed
                cluster_end = max(cluster_end, end)
            else:
                if len(cluster) > 1:
                    result.append(cluster)
                cluster = [index]
                cluster_end = end
        if len(cluster) > 1:
            result.append(cluster)
    return result


def audit_gaps(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    model_coverage: dict[tuple[str, str], set[int]] = defaultdict(set)
    for row in rows:
        grouped[tuple(row.get(field, "") for field in IDENTITY)].append(row)
        start, end = years(row["YEAR"])
        model_coverage[(row["MAKE"], row["MODEL"])].update(range(start, end + 1))
    findings: list[dict[str, str]] = []
    for key, group in grouped.items():
        ordered = sorted(group, key=lambda row: years(row["YEAR"]))
        covered_end = years(ordered[0]["YEAR"])[1]
        left = ordered[0]
        for right in ordered[1:]:
            right_start, right_end = years(right["YEAR"])
            if right_start > covered_end + 1:
                missing_year = str(covered_end + 1) if right_start == covered_end + 2 else f"{covered_end + 1}-{right_start - 1}"
                missing_years = set(range(covered_end + 1, right_start))
                covered_by_other_branch = missing_years.issubset(model_coverage[(left["MAKE"], left["MODEL"])])
                known_gap = KNOWN_GAPS.get((left["MAKE"], left["MODEL"], left.get("版本", ""), left.get("结构", ""), missing_year))
                same_generation = left.get("代际", "") == right.get("代际", "")
                if known_gap:
                    decision = "VALID_HIATUS"
                    reason = known_gap[0]
                elif same_generation and covered_by_other_branch:
                    decision = "RESEARCH_BRANCH_GAP"
                    reason = "同车型其他结构/版本覆盖该年份；当前缺口属于分支范围，不等于整车型漏年"
                elif same_generation:
                    decision = "RESEARCH_MODEL_YEAR_GAP"
                    reason = "同代际且整车型在该年份没有其他记录，优先核查是否漏年"
                elif covered_by_other_branch:
                    decision = "REVIEW_BRANCH_OR_GENERATION_BOUNDARY"
                    reason = "同车型其他结构/版本覆盖该年份；需核查当前分支的销售边界"
                elif len(missing_years) >= 5:
                    decision = "REVIEW_NAMEPLATE_HIATUS"
                    reason = "跨代长时间空档，可能是停产或名称复用，不能自动补齐"
                else:
                    decision = "REVIEW_GENERATION_BOUNDARY"
                    reason = "跨代短空档，需核查换代首末年"
                findings.append(
                    {
                        **dict(zip(IDENTITY, key)),
                        "LEFT_YEAR": left["YEAR"],
                        "LEFT_GENERATION": left.get("代际", ""),
                        "RIGHT_YEAR": right["YEAR"],
                        "RIGHT_GENERATION": right.get("代际", ""),
                        "MISSING_YEAR": missing_year,
                        "PRIORITY": "RESOLVED" if known_gap else ("HIGH" if same_generation and right_start == covered_end + 2 else ("MEDIUM" if same_generation else "REVIEW")),
                        "MODEL_YEAR_COVERED_BY_OTHER_BRANCH": "YES" if covered_by_other_branch else "NO",
                        "REASON": reason,
                        "EVIDENCE": known_gap[1] if known_gap else "累计快照年份连续性审计",
                        "DECISION": decision,
                    }
                )
            if right_end > covered_end:
                covered_end = right_end
                left = right
    return findings


def audit_generations(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], dict[int, list[tuple[int, int]]]] = defaultdict(lambda: defaultdict(list))
    invalid: list[dict[str, str]] = []
    for row in rows:
        number = generation_number(row.get("代际", ""))
        if number is None:
            invalid.append({"MAKE": row["MAKE"], "MODEL": row["MODEL"], "ISSUE": "COMPOSITE_GENERATION_LABEL_REVIEW", "DETAIL": row.get("代际", ""), "DECISION": "REVIEW_ONLY", "REASON": "代际字段不是单一 genN"})
            continue
        grouped[(row["MAKE"], row["MODEL"])][number].append(years(row["YEAR"]))

    findings = invalid
    for (make, model), generations in grouped.items():
        spans = {number: (min(item[0] for item in values), max(item[1] for item in values)) for number, values in generations.items()}
        ordered = sorted(spans.items())
        for (left_number, left_span), (right_number, right_span) in zip(ordered, ordered[1:]):
            if right_span[0] < left_span[0]:
                findings.append(
                    {
                        "MAKE": make,
                        "MODEL": model,
                        "ISSUE": "GENERATION_ORDER_INVERSION",
                        "DETAIL": f"gen{left_number}={left_span[0]}-{left_span[1]}; gen{right_number}={right_span[0]}-{right_span[1]}",
                    }
                )
            elif right_span[0] <= left_span[1] - 1:
                known_reason = KNOWN_MODEL_GENERATION_OVERLAPS.get((make, model, left_number, right_number))
                findings.append(
                    {
                        "MAKE": make,
                        "MODEL": model,
                        "ISSUE": "GENERATION_OVERLAP_GT_1_YEAR",
                        "DETAIL": f"gen{left_number}={left_span[0]}-{left_span[1]}; gen{right_number}={right_span[0]}-{right_span[1]}",
                        "DECISION": "VALID_PARALLEL_OR_LINEAGE" if known_reason else "REVIEW_ONLY",
                        "REASON": known_reason or "模型级代际跨度重叠，尚未确认是否为不同结构/版本并行",
                    }
                )
    return findings


def audit_interval_conflicts(rows: list[dict[str, str]], tolerance: Decimal) -> list[dict[str, str]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(field, "") for field in IDENTITY)].append(row)
    findings: list[dict[str, str]] = []
    for key, group in grouped.items():
        ordered = sorted(group, key=lambda row: years(row["YEAR"]))
        for index, left in enumerate(ordered):
            left_start, left_end = years(left["YEAR"])
            for right in ordered[index + 1 :]:
                right_start, right_end = years(right["YEAR"])
                if right_start > left_end:
                    break
                if left.get("代际") == right.get("代际") and left.get("分类") == right.get("分类") and within_envelope([left, right], tolerance):
                    continue
                overlap = str(max(left_start, right_start)) if min(left_end, right_end) == max(left_start, right_start) else f"{max(left_start, right_start)}-{min(left_end, right_end)}"
                if left.get("代际") == right.get("代际"):
                    left_dimensions = decimals(left)
                    right_dimensions = decimals(right)
                    major_geometry_delta = bool(left_dimensions and right_dimensions and (abs(left_dimensions[0] - right_dimensions[0]) >= Decimal("2.5") or abs(left_dimensions[1] - right_dimensions[1]) >= Decimal("1.0")))
                    issue = "LIKELY_UNKEYED_BODY_OR_WHEELBASE_VARIANT" if major_geometry_delta else "OVERLAPPING_SPEC_OR_TRIM_CONFLICT"
                else:
                    issue = "GENERATION_BOUNDARY_OVERLAP"
                known = KNOWN_PARALLEL_BOUNDARIES.get((left["MAKE"], left["MODEL"], left.get("代际", ""), right.get("代际", ""), overlap))
                findings.append(
                    {
                        **dict(zip(IDENTITY, key)),
                        "LEFT_YEAR": left["YEAR"],
                        "LEFT_GENERATION": left.get("代际", ""),
                        "LEFT_DIMENSIONS": "x".join(left.get(field, "") for field in DIMENSIONS),
                        "RIGHT_YEAR": right["YEAR"],
                        "RIGHT_GENERATION": right.get("代际", ""),
                        "RIGHT_DIMENSIONS": "x".join(right.get(field, "") for field in DIMENSIONS),
                        "OVERLAP_YEAR": overlap,
                        "ISSUE": issue,
                        "DECISION": "VALID_PARALLEL" if known else "REVIEW_ONLY",
                        "REASON": known[0] if known else "同一无年份 key 的区间重叠但尺寸、分类或代际不满足安全合并条件",
                        "EVIDENCE": known[1] if known else "累计快照内部冲突审计",
                    }
                )
    return findings


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def apply_generation_decisions(
    rows: list[dict[str, str]], decision_path: Path | None
) -> list[dict[str, str]]:
    if decision_path is None:
        return []
    rules = json.loads(decision_path.read_text(encoding="utf-8"))
    changes: list[dict[str, str]] = []
    matched = [0] * len(rules)
    for row in rows:
        start, end = years(row["YEAR"])
        for index, rule in enumerate(rules):
            if row["MAKE"] != rule["make"] or row["MODEL"] != rule["model"]:
                continue
            if start < int(rule["year_start"]) or end > int(rule["year_end"]):
                continue
            matched[index] += 1
            before = row.get("代际", "")
            after = rule["generation"]
            if before == after:
                continue
            row["代际"] = after
            changes.append(
                {
                    "ACTION": "UPDATE_GENERATION",
                    "DIMENSION_IDS_BEFORE": row["DIMENSION-ID"],
                    "DIMENSION_ID_AFTER": row["DIMENSION-ID"],
                    "FIELD": "代际",
                    "VALUE_BEFORE": before,
                    "VALUE_AFTER": after,
                    "YEARS_BEFORE": row["YEAR"],
                    "YEAR_AFTER": row["YEAR"],
                    "DIMENSIONS_BEFORE": "x".join(row[field] for field in DIMENSIONS),
                    "DIMENSIONS_AFTER": "x".join(row[field] for field in DIMENSIONS),
                    "REASON": rule["reason"],
                    "EVIDENCE": rule["evidence"],
                }
            )
    unmatched = [rules[index] for index, count in enumerate(matched) if count == 0]
    if unmatched:
        raise SystemExit(f"代际规则未命中任何记录：{unmatched}")
    return changes


def apply_identity_decisions(
    rows: list[dict[str, str]], decision_path: Path | None
) -> list[dict[str, str]]:
    if decision_path is None:
        return []
    rules = json.loads(decision_path.read_text(encoding="utf-8"))
    changes: list[dict[str, str]] = []
    matched = [0] * len(rules)
    extra_rows: list[dict[str, str]] = []
    selectable = ("MAKE", "MODEL", "YEAR", "版本", "结构", "代际", "L-IN", "W-IN", "H-IN")
    for row in rows:
        for index, rule in enumerate(rules):
            selector = rule["match"]
            if any(row.get(field, "") != str(selector[field]) for field in selectable if field in selector):
                continue
            matched[index] += 1
            action = rule.get("action", "UPDATE")
            if action == "DELETE":
                if row.get("__delete") == "1":
                    continue
                row["__delete"] = "1"
                changes.append(
                    {
                        "ACTION": "DELETE_AGGREGATE",
                        "DIMENSION_IDS_BEFORE": row["DIMENSION-ID"],
                        "DIMENSION_ID_AFTER": "",
                        "FIELD": "",
                        "VALUE_BEFORE": "",
                        "VALUE_AFTER": "",
                        "YEARS_BEFORE": row["YEAR"],
                        "YEAR_AFTER": "",
                        "DIMENSIONS_BEFORE": "x".join(row[item] for item in DIMENSIONS),
                        "DIMENSIONS_AFTER": "",
                        "REASON": rule["reason"],
                        "EVIDENCE": rule["evidence"],
                    }
                )
                continue
            if action == "SPLIT":
                if row.get("__delete") == "1":
                    continue
                before_id = row["DIMENSION-ID"]
                row["__delete"] = "1"
                created: list[dict[str, str]] = []
                for overrides in rule["records"]:
                    clone = {key: value for key, value in row.items() if not key.startswith("__")}
                    clone.update({key: str(value) for key, value in overrides.items()})
                    clone["DIMENSION-ID"] = dimension_id(clone)
                    created.append(clone)
                extra_rows.extend(created)
                changes.append(
                    {
                        "ACTION": "SPLIT_IDENTITY_OR_YEAR",
                        "DIMENSION_IDS_BEFORE": before_id,
                        "DIMENSION_ID_AFTER": " | ".join(item["DIMENSION-ID"] for item in created),
                        "FIELD": "YEAR,版本",
                        "VALUE_BEFORE": f"{row['YEAR']}|{row.get('版本', '')}",
                        "VALUE_AFTER": " | ".join(f"{item['YEAR']}|{item.get('版本', '')}" for item in created),
                        "YEARS_BEFORE": row["YEAR"],
                        "YEAR_AFTER": " | ".join(item["YEAR"] for item in created),
                        "DIMENSIONS_BEFORE": "x".join(row[item] for item in DIMENSIONS),
                        "DIMENSIONS_AFTER": " | ".join("x".join(item[field] for field in DIMENSIONS) for item in created),
                        "REASON": rule["reason"],
                        "EVIDENCE": rule["evidence"],
                    }
                )
                continue
            field = rule["field"]
            before = row.get(field, "")
            after = str(rule["value"])
            if before == after:
                continue
            before_id = row["DIMENSION-ID"]
            row[field] = after
            row["DIMENSION-ID"] = dimension_id(row)
            changes.append(
                {
                    "ACTION": f"UPDATE_{field.upper()}",
                    "DIMENSION_IDS_BEFORE": before_id,
                    "DIMENSION_ID_AFTER": row["DIMENSION-ID"],
                    "FIELD": field,
                    "VALUE_BEFORE": before,
                    "VALUE_AFTER": after,
                    "YEARS_BEFORE": row["YEAR"],
                    "YEAR_AFTER": row["YEAR"],
                    "DIMENSIONS_BEFORE": "x".join(row[item] for item in DIMENSIONS),
                    "DIMENSIONS_AFTER": "x".join(row[item] for item in DIMENSIONS),
                    "REASON": rule["reason"],
                    "EVIDENCE": rule["evidence"],
                }
            )
    unmatched = [rules[index] for index, count in enumerate(matched) if count != 1]
    if unmatched:
        raise SystemExit(f"身份区分规则必须各命中且只命中一条记录：{unmatched}")
    rows.extend(extra_rows)
    return changes


def main() -> None:
    args = parse_args()
    ensure_not_source(args.package)
    args.package.mkdir(parents=True, exist_ok=True)
    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    input_row_count = len(rows)

    invalid_year_ids = []
    for row in rows:
        try:
            years(row["YEAR"])
        except ValueError:
            invalid_year_ids.append(row["DIMENSION-ID"])
    if invalid_year_ids:
        raise SystemExit(f"YEAR 格式错误，无法继续：{invalid_year_ids[:10]}")

    generation_changes = apply_generation_decisions(rows, args.generation_decisions)
    identity_changes = apply_identity_decisions(rows, args.identity_decisions)
    rows = [row for row in rows if row.get("__delete") != "1"]
    groups = find_merge_groups(rows, args.tolerance)
    merge_candidates = []
    for group in groups:
        members = [rows[index] for index in group]
        merged = merged_row(members)
        merge_candidates.append(
            {
                "DIMENSION_IDS": " | ".join(row["DIMENSION-ID"] for row in members),
                "MAKE": merged["MAKE"],
                "MODEL": merged["MODEL"],
                "版本": merged["版本"],
                "结构": merged["结构"],
                "代际": merged["代际"],
                "YEARS_BEFORE": " | ".join(row["YEAR"] for row in members),
                "YEAR_AFTER": merged["YEAR"],
                "DIMENSIONS_BEFORE": " | ".join("x".join(row[field] for field in DIMENSIONS) for row in members),
                "DIMENSIONS_AFTER": "x".join(merged[field] for field in DIMENSIONS),
                "DECISION": "APPLY_SAFE_MERGE" if args.apply_safe_merges else "CANDIDATE",
            }
        )

    output_rows = rows
    changes: list[dict[str, str]] = [*generation_changes, *identity_changes]
    if args.apply_safe_merges:
        first_to_merged: dict[int, dict[str, str]] = {}
        removed: set[int] = set()
        for group in groups:
            members = [rows[index] for index in group]
            first_to_merged[min(group)] = merged_row(members)
            removed.update(group)
            changes.append(
                {
                    "ACTION": "MERGE_CONTIGUOUS",
                    "DIMENSION_IDS_BEFORE": " | ".join(row["DIMENSION-ID"] for row in members),
                    "DIMENSION_ID_AFTER": first_to_merged[min(group)]["DIMENSION-ID"],
                    "FIELD": "YEAR,L-IN,W-IN,H-IN",
                    "VALUE_BEFORE": "",
                    "VALUE_AFTER": "",
                    "YEARS_BEFORE": " | ".join(row["YEAR"] for row in members),
                    "YEAR_AFTER": first_to_merged[min(group)]["YEAR"],
                    "DIMENSIONS_BEFORE": " | ".join("x".join(row[field] for field in DIMENSIONS) for row in members),
                    "DIMENSIONS_AFTER": "x".join(first_to_merged[min(group)][field] for field in DIMENSIONS),
                    "REASON": f"同一无年份 key、同代际同分类、年份连续或重叠，三维包络差均不超过 {args.tolerance} in",
                    "EVIDENCE": "累计快照内相邻记录的身份字段、代际、分类、年份和三维数值",
                }
            )
        output_rows = []
        for index, row in enumerate(rows):
            if index in first_to_merged:
                output_rows.append(first_to_merged[index])
            elif index not in removed:
                output_rows.append(row)

    gaps = audit_gaps(output_rows)
    generation_findings = audit_generations(output_rows)
    unresolved_generation_findings = [item for item in generation_findings if item.get("DECISION") == "REVIEW_ONLY"]
    confirmed_generation_parallel = [item for item in generation_findings if item.get("DECISION") == "VALID_PARALLEL_OR_LINEAGE"]
    interval_conflicts = audit_interval_conflicts(output_rows, args.tolerance)
    confirmed_parallel = [item for item in interval_conflicts if item["DECISION"] == "VALID_PARALLEL"]
    unresolved_conflicts = [item for item in interval_conflicts if item["DECISION"] == "REVIEW_ONLY"]
    output_ids = [row["DIMENSION-ID"] for row in output_rows]
    duplicate_ids = sorted(record_id for record_id, count in Counter(output_ids).items() if count > 1)
    id_mismatches = [row["DIMENSION-ID"] for row in output_rows if row["DIMENSION-ID"] != dimension_id(row)]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": not duplicate_ids and not id_mismatches,
        "input": str(args.input.resolve()),
        "input_rows": input_row_count,
        "output_rows": len(output_rows),
        "tolerance_in": str(args.tolerance),
        "merge_groups": len(groups),
        "generation_rows_corrected": len(generation_changes),
        "identity_rows_distinguished": len(identity_changes),
        "rows_reduced": len(rows) - len(output_rows),
        "gap_candidates": len(gaps),
        "generation_findings": len(generation_findings),
        "unresolved_generation_findings": len(unresolved_generation_findings),
        "confirmed_generation_parallel": len(confirmed_generation_parallel),
        "interval_conflicts": len(interval_conflicts),
        "confirmed_parallel_boundaries": len(confirmed_parallel),
        "unresolved_interval_conflicts": len(unresolved_conflicts),
        "duplicate_dimension_ids": duplicate_ids,
        "dimension_id_mismatches": id_mismatches,
        "source_directory_written": False,
    }
    write_csv(args.package / "correct.csv", fields, output_rows)
    write_csv(
        args.package / "changes.csv",
        ["ACTION", "DIMENSION_IDS_BEFORE", "DIMENSION_ID_AFTER", "FIELD", "VALUE_BEFORE", "VALUE_AFTER", "YEARS_BEFORE", "YEAR_AFTER", "DIMENSIONS_BEFORE", "DIMENSIONS_AFTER", "REASON", "EVIDENCE"],
        changes,
    )
    write_csv(
        args.package / "merge_candidates.csv",
        ["DIMENSION_IDS", "MAKE", "MODEL", "版本", "结构", "代际", "YEARS_BEFORE", "YEAR_AFTER", "DIMENSIONS_BEFORE", "DIMENSIONS_AFTER", "DECISION"],
        merge_candidates,
    )
    write_csv(
        args.package / "gap_candidates.csv",
        [*IDENTITY, "LEFT_YEAR", "LEFT_GENERATION", "RIGHT_YEAR", "RIGHT_GENERATION", "MISSING_YEAR", "MODEL_YEAR_COVERED_BY_OTHER_BRANCH", "PRIORITY", "REASON", "EVIDENCE", "DECISION"],
        gaps,
    )
    write_csv(args.package / "generation_findings.csv", ["MAKE", "MODEL", "ISSUE", "DETAIL", "DECISION", "REASON"], generation_findings)
    write_csv(
        args.package / "interval_conflicts.csv",
        [*IDENTITY, "LEFT_YEAR", "LEFT_GENERATION", "LEFT_DIMENSIONS", "RIGHT_YEAR", "RIGHT_GENERATION", "RIGHT_DIMENSIONS", "OVERLAP_YEAR", "ISSUE", "DECISION", "REASON", "EVIDENCE"],
        interval_conflicts,
    )
    (args.package / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
