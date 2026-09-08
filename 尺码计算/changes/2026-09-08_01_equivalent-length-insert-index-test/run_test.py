#!/usr/bin/env python3
"""基于现有全量结果，使用 0908 规则重算等效长、插片指数和自动尺码。"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import pandas_analysis as analysis


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input_全量数据.csv"
REFERENCES = ROOT / "input_参考尺寸计算.csv"
RULES = ROOT / "rules_尺码匹配规则-0908.csv"
PARAMETERS = ROOT / "rules_尺码匹配参数.csv"
OUTPUT = ROOT / "result_尺码计算测试-0908.csv"
REPORT = ROOT / "summary_尺码计算测试-0908.json"


def main() -> None:
    source = analysis._read_csv(INPUT)
    references = analysis._read_csv(REFERENCES)
    rules = analysis._read_csv(RULES)
    parameters = analysis._read_csv(PARAMETERS)

    required = [
        "分类", "车形", "L-MM", "W-MM", "前宽-MM", "后宽-MM", "自动尺码",
        "DIMENSION-ID",
    ]
    analysis._require_columns(source, required, "现有全量结果")

    result = source.rename(columns={"自动尺码": "原自动尺码"}).copy()
    result = result.drop(
        columns=["参考插片", "参考半周长", "自动长度余量", "候选", "原因", "相差数值"],
        errors="ignore",
    )
    result["L-MM"] = analysis._numeric(result["L-MM"]).astype("Int64")

    front = analysis._numeric(result["前宽-MM"])
    rear = analysis._numeric(result["后宽-MM"])
    legacy_index = (front + rear) / 4 - analysis.PANEL_OFFSET_MM
    pickup_index = front / 2 - analysis.PANEL_OFFSET_MM
    result["插片指数"] = analysis._round_nullable(
        legacy_index.where(result["分类"].ne("皮卡"), pickup_index)
    )

    factors = references[["车身号", "周长系数"]].copy()
    factors["车身号"] = factors["车身号"].astype("string").str.strip()
    if factors["车身号"].duplicated().any():
        raise analysis.DataContractError("参考尺寸计算的车身号去空格后必须唯一")
    coefficient = result["车形"].map(
        analysis._coefficient(factors.set_index("车身号")["周长系数"])
    )
    result["等效长"] = analysis._round_nullable(
        (result["L-MM"].astype("Float64") + analysis._numeric(result["W-MM"]))
        * coefficient
        - analysis.EQUIVALENT_LENGTH_OFFSET_MM
    )

    old_result_columns = ["自动尺码", "自动长度余量", "候选", "原因", "相差数值"]
    result = result.drop(columns=old_result_columns, errors="ignore")
    result = analysis.SizeMatcher(parameters, rules).apply(result)
    result["尺码变化"] = result["原自动尺码"].ne(result["自动尺码"])

    ordered = [
        *[column for column in analysis.DEFAULT_OUTPUT_COLUMNS if column in result.columns],
        "原自动尺码",
        "尺码变化",
    ]
    result = result[ordered]
    analysis.write_result(result, OUTPUT)

    pickup = result.loc[result["分类"].eq("皮卡")]
    report = {
        "input": str(INPUT.relative_to(ROOT)),
        "rules": str(RULES.relative_to(ROOT)),
        "rows": int(len(result)),
        "changed_rows": int(result["尺码变化"].sum()),
        "matched_rows": int((~result["自动尺码"].isin(["数据不全", "无可用尺码"])).sum()),
        "unavailable_rows": int(result["自动尺码"].eq("无可用尺码").sum()),
        "incomplete_rows": int(result["自动尺码"].eq("数据不全").sum()),
        "pickup": {
            "rows": int(len(pickup)),
            "changed_rows": int(pickup["尺码变化"].sum()),
            "unavailable_rows": int(pickup["自动尺码"].eq("无可用尺码").sum()),
            "incomplete_rows": int(pickup["自动尺码"].eq("数据不全").sum()),
            "pk_wx_or_wxxl_rows": int(pickup["自动尺码"].isin(["PK-WX", "PK-WXXL"]).sum()),
            "insert_index_min": int(pickup["插片指数"].min()),
            "insert_index_max": int(pickup["插片指数"].max()),
            "equivalent_length_min": int(pickup["等效长"].min()),
            "equivalent_length_max": int(pickup["等效长"].max()),
            "size_counts": {
                str(key): int(value)
                for key, value in pickup["自动尺码"].value_counts(dropna=False).items()
            },
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
