# -*- coding: utf-8 -*-
"""按自动尺码选取代表车型，并生成可直接交付的 CSV。"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "全量数据.csv"
RULES = ROOT / "public" / "尺码匹配规则.csv"
OUTPUT = ROOT / "车型代表分析" / "output" / "代表车型.csv"
OUTPUT_TSV = ROOT / "车型代表分析" / "output" / "代表车型.tsv"
TARGET_SIZES = ["3XL", "3XXL", "3L-W", "3XL-W", "3XXL-W", "3XXXL", "3XXXXL"]
OUTPUT_FIELDS = ["车型", "dimension-id", "型号", "车长", "车宽", "车高", "车形", "销量", "参考半周长", "in_eagle"]
TSV_FIELDS = ["车型", "型号", "车长", "车宽", "车高", "车形"]


def number(row: dict[str, str], field: str) -> float:
    try:
        return float(row[field])
    except (KeyError, TypeError, ValueError):
        return 0.0


def end_year(value: str) -> int:
    try:
        return int(value[-4:])
    except (TypeError, ValueError):
        return 0


def normalize(value: float, low: float, high: float) -> float:
    return (value - low) / (high - low) if high > low else 1.0


def display_name(row: dict[str, str]) -> str:
    # 结构已由车形列体现；Cab/Bed 必须保留，才能唯一对应皮卡 DIMENSION-ID。
    fields = ["YEAR", "MAKE", "MODEL", "版本", "CAB", "BED"]
    return " ".join(row.get(field, "").strip() for field in fields if row.get(field, "").strip())


def logical_size(row: dict[str, str], rules: list[dict[str, str]]) -> str:
    """Re-evaluate the logical size; 自动尺码 stores the internal size."""
    category = row.get("分类", "").strip()
    length = number(row, "L-MM")
    insert = number(row, "插片指数")
    for rule in rules:
        if rule.get("分类", "").strip() != category:
            continue
        if number(rule, "长上限") >= length and number(rule, "插片指数上限") >= insert:
            return rule.get("逻辑尺码", "").strip() if number(rule, "长上限") - length <= 500 else ""
    return ""


def rank_group(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    positive_sales = [row for row in rows if number(row, "销量合计") > 0]
    pool = positive_sales if len(positive_sales) >= 4 else rows

    lengths = [number(row, "L-MM") for row in pool]
    girths = [number(row, "等效长") for row in pool]
    years = [end_year(row.get("YEAR", "")) for row in pool]
    sales_logs = [math.log10(1 + number(row, "销量合计")) for row in pool]
    bounds = (
        min(lengths), max(lengths), min(girths), max(girths),
        min(years), max(years), max(sales_logs),
    )

    for row in pool:
        length_score = normalize(number(row, "L-MM"), bounds[0], bounds[1])
        girth_score = normalize(number(row, "等效长"), bounds[2], bounds[3])
        year_score = normalize(end_year(row.get("YEAR", "")), bounds[4], bounds[5])
        sales_score = math.log10(1 + number(row, "销量合计")) / bounds[6] if bounds[6] else 0
        row["_score"] = 0.30 * length_score + 0.30 * girth_score + 0.20 * sales_score + 0.20 * year_score

    ranked = sorted(
        pool,
        key=lambda row: (
            row["_score"],
            end_year(row.get("YEAR", "")),
            number(row, "销量合计"),
            row.get("DIMENSION-ID", ""),
        ),
        reverse=True,
    )

    # 先覆盖不同车型/版本/Cab/Bed，再在候选不足时用其他年代补足。
    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()
    signatures: set[tuple[str, ...]] = set()
    for row in ranked:
        signature = tuple(row.get(field, "") for field in ("MAKE", "MODEL", "版本", "CAB", "BED"))
        if signature not in signatures:
            selected.append(row)
            selected_ids.add(row["DIMENSION-ID"])
            signatures.add(signature)
        if len(selected) == 4:
            return selected
    for row in ranked:
        if row["DIMENSION-ID"] not in selected_ids:
            selected.append(row)
        if len(selected) == 4:
            break
    return selected


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    with RULES.open("r", encoding="utf-8-sig", newline="") as handle:
        rules = [row for row in csv.DictReader(handle) if row.get("使用", "").strip().casefold() == "y"]
    rules.sort(key=lambda row: number(row, "档位序号"))

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_rows:
        size = logical_size(row, rules)
        if size in TARGET_SIZES and number(row, "L-MM") and number(row, "等效长"):
            groups[size].append(row)

    output_rows = []
    for size in TARGET_SIZES:
        for row in rank_group(groups[size]):
            output_rows.append(
                {
                    "车型": display_name(row),
                    "dimension-id": row.get("DIMENSION-ID", ""),
                    "型号": size,
                    "车长": int(number(row, "L-MM")),
                    "车宽": int(number(row, "W-MM")),
                    "车高": int(number(row, "H-MM")),
                    "车形": row.get("车形", ""),
                    "销量": int(number(row, "销量合计")),
                    # Keep the established output column name for consumers;
                    # the current calculation field is 等效长.
                    "参考半周长": int(number(row, "等效长")),
                    "in_eagle": 0,
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    with OUTPUT_TSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row[field] for field in TSV_FIELDS} for row in output_rows)

    print(f"sizes={len(groups)} rows={len(output_rows)} output={OUTPUT} tsv={OUTPUT_TSV}")


if __name__ == "__main__":
    main()
