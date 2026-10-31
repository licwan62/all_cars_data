#!/usr/bin/env python3
"""Build EU/RU coverage-first full tables from explicitly labelled regional candidates."""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "nodes" / "A0.尺码计算"
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch
import data_layout
import output_layout as layout
import pandas_analysis as analysis

SHAPES = ROOT / "nodes" / "03.车形分类核定" / "output" / "车形分类.csv"
DIMENSIONS = ROOT / "nodes" / "02.分类结构审核" / "output"
OUTPUT = PROJECT / "output"
# 各区域从自己的 data/<区域>/ 读取规则和参数；EU 不使用 US 规则。
EU_CONFIG = data_layout.current("EU")
ARTIFACTS = PROJECT / "artifacts"


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def base_id(value: str, region: str) -> str:
    suffix = f" {region}"
    return value[:-len(suffix)] if value.endswith(suffix) else value


def batch_dir() -> Path:
    prefix = date.today().isoformat()
    nums = []
    for path in ARTIFACTS.glob(f"{prefix}_*"):
        match = re.match(rf"{re.escape(prefix)}_(\d{{2}})_", path.name)
        if match:
            nums.append(int(match.group(1)))
    return ARTIFACTS / f"{prefix}_{max(nums, default=0)+1:02d}_regional-coverage-full"


def candidate_shapes(region: str) -> pd.DataFrame:
    shapes = read(SHAPES)
    result = shapes.loc[shapes["COUNTRY"].eq(region), ["DIMENSION-ID", "车形", "处理状态"]].copy()
    result["DIMENSION-ID"] = result["DIMENSION-ID"].map(lambda value: base_id(value, region))
    result["方法"] = result["处理状态"]
    result["置信度"] = result["处理状态"].map(lambda value: "low" if "代理" in value else "medium")
    result["需质量复核"] = result["置信度"].map(lambda value: "yes" if value == "low" else "no")
    if result["DIMENSION-ID"].duplicated().any():
        raise ValueError(f"{region} 车形候选 ID 不唯一")
    return result


def build_eu(artifact: Path, shapes: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    dims = read(DIMENSIONS / "车型结构_EU.csv")
    dims["DIMENSION-ID"] = dims["DIMENSION-ID"].map(lambda value: base_id(value, "EU"))
    if set(dims["DIMENSION-ID"]) != set(shapes["DIMENSION-ID"]):
        raise ValueError("EU 尺寸库与车形候选 ID 集合不一致")
    work = artifact / "input" / "eu-compat"
    work.mkdir(parents=True)
    dims.to_csv(work / "尺寸库.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    shapes[["DIMENSION-ID", "车形"]].to_csv(work / "车形分类.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    pd.DataFrame({"atom_record_id": [f"{item}|ATOM_YEAR=0" for item in dims["DIMENSION-ID"]], "预估销量": [0] * len(dims)}).to_csv(work / "原子销量.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    result, _ = analysis.calculate(work, config_dir=EU_CONFIG.parameters.parent, rules_path=EU_CONFIG.rules, parameters_path=EU_CONFIG.parameters, body_path=work / "车形分类.csv", sales_path=work / "原子销量.csv", include_analysis=True, trim_source=None)
    result["DIMENSION-ID"] = result["DIMENSION-ID"].map(lambda value: f"{value} EU")
    result = result.drop(columns=["TRIM"])  # 只有 US 有 TRIM 匹配环节
    report = {"rows": len(result), "sales_total": 0, "sales_policy": "zero placeholder; no EU sales fact", "shape_policy": "coverage candidate", "low_confidence_shapes": int(shapes["置信度"].eq("low").sum())}
    return result, report


def build_ru(shapes: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    result = read(OUTPUT / layout.full_table("RU"))
    result["_base"] = result["DIMENSION-ID"].map(lambda value: base_id(value, "RU"))
    joined = result.merge(shapes[["DIMENSION-ID", "车形", "置信度", "方法"]], left_on="_base", right_on="DIMENSION-ID", how="left", validate="one_to_one", suffixes=("", "_candidate"))
    if joined["车形_candidate"].eq("").any() or joined["车形_candidate"].isna().any():
        raise ValueError("RU 全量表存在缺失车形候选")
    joined["车形"] = joined["车形_candidate"]
    joined = joined.drop(columns=["_base", "DIMENSION-ID_candidate", "车形_candidate", "置信度", "方法"])
    report = {"rows": len(joined), "sales_total": int(pd.to_numeric(joined[analysis.SIZE_GROUP_SALES], errors="coerce").fillna(0).sum()), "sales_policy": "existing RU proxy sales retained", "shape_policy": "coverage candidate", "low_confidence_shapes": int(shapes["置信度"].eq("low").sum())}
    return joined, report


def main() -> int:
    with RunBatch.create(ARTIFACTS, "regional-coverage-full", PROJECT / "data") as batch:
        batch.input(SHAPES)
        batch.input(DIMENSIONS / "车型结构_EU.csv")
        batch.input(OUTPUT / layout.full_table("RU"))
        shapes_eu, shapes_ru = candidate_shapes("EU"), candidate_shapes("RU")
        with tempfile.TemporaryDirectory(prefix="eu-coverage-") as temp:
            eu, eu_report = build_eu(Path(temp), shapes_eu)
        ru, ru_report = build_ru(shapes_ru)
        for region, frame, report in [("EU", eu, eu_report), ("RU", ru, ru_report)]:
            frame.to_csv(batch.output(layout.full_table(region)), index=False, encoding="utf-8-sig", lineterminator="\n")
            batch.extra(f"尺码匹配报告_{region}.json", compress=False).write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        batch.finish({"EU": eu_report, "RU": ru_report}, publish_to=OUTPUT)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
