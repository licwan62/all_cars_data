#!/usr/bin/env python3
"""Build EU/RU coverage-first full tables from explicitly labelled regional candidates."""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "A0.尺码计算"
sys.path.insert(0, str(ROOT))
from full_table_schema import attach_dimension_code
import pandas_analysis as analysis

SHAPES = ROOT / "03.车形分类核定" / "output" / "车形分类.csv"
DIMENSIONS = ROOT / "01.整理尺寸库" / "output"
OUTPUT = PROJECT / "output"
ARTIFACTS = PROJECT / "artifacts"


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def base_id(value: str, region: str) -> str:
    suffix = f" {region}"
    return value[:-len(suffix)] if value.endswith(suffix) else value


def batch_dir() -> Path:
    prefix = date.today().isoformat()
    nums = []
    for path in ARTIFACTS.glob(f"{prefix}_*_*regional-coverage-full"):
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
    dims = read(DIMENSIONS / "尺寸库_EU.csv")
    dims["DIMENSION-ID"] = dims["DIMENSION-ID"].map(lambda value: base_id(value, "EU"))
    if set(dims["DIMENSION-ID"]) != set(shapes["DIMENSION-ID"]):
        raise ValueError("EU 尺寸库与车形候选 ID 集合不一致")
    work = artifact / "input" / "eu-compat"
    work.mkdir(parents=True)
    dims.to_csv(work / "尺寸库.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    shapes[["DIMENSION-ID", "车形"]].to_csv(work / "车形分类.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    pd.DataFrame({"atom_record_id": [f"{item}|ATOM_YEAR=0" for item in dims["DIMENSION-ID"]], "预估销量": [0] * len(dims)}).to_csv(work / "原子销量.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    result, _ = analysis.calculate(work, config_dir=PROJECT / "data", body_path=work / "车形分类.csv", sales_path=work / "原子销量.csv", include_analysis=True, trim_source=None)
    result["DIMENSION-ID"] = result["DIMENSION-ID"].map(lambda value: f"{value} EU")
    result = attach_dimension_code(result)
    report = {"rows": len(result), "sales_total": 0, "sales_policy": "zero placeholder; no EU sales fact", "shape_policy": "coverage candidate", "low_confidence_shapes": int(shapes["置信度"].eq("low").sum())}
    return result, report


def build_ru(shapes: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    result = read(OUTPUT / "全量表_RU.csv")
    result["_base"] = result["DIMENSION-ID"].map(lambda value: base_id(value, "RU"))
    joined = result.merge(shapes[["DIMENSION-ID", "车形", "置信度", "方法"]], left_on="_base", right_on="DIMENSION-ID", how="left", validate="one_to_one", suffixes=("", "_candidate"))
    if joined["车形_candidate"].eq("").any() or joined["车形_candidate"].isna().any():
        raise ValueError("RU 全量表存在缺失车形候选")
    joined["车形"] = joined["车形_candidate"]
    joined = joined.drop(columns=["_base", "DIMENSION-ID_candidate", "车形_candidate", "置信度", "方法"])
    report = {"rows": len(joined), "sales_total": int(pd.to_numeric(joined["销量合计"], errors="coerce").fillna(0).sum()), "sales_policy": "existing RU proxy sales retained", "shape_policy": "coverage candidate", "low_confidence_shapes": int(shapes["置信度"].eq("low").sum())}
    return joined, report


def main() -> int:
    artifact = batch_dir()
    staging = artifact.with_name(f".{artifact.name}.tmp")
    try:
        shapes_eu, shapes_ru = candidate_shapes("EU"), candidate_shapes("RU")
        eu, eu_report = build_eu(staging, shapes_eu)
        ru, ru_report = build_ru(shapes_ru)
        (staging / "output").mkdir(parents=True, exist_ok=True)
        for region, frame, report in [("EU", eu, eu_report), ("RU", ru, ru_report)]:
            frame.to_csv(staging / "output" / f"全量表_{region}.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
            (staging / "output" / f"尺码匹配报告_{region}.json").write_text(json.dumps({"status": "passed", "coverage_first": True, **report}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        os.replace(staging, artifact)
        for region in ("EU", "RU"):
            for name in (f"全量表_{region}.csv", f"尺码匹配报告_{region}.json"):
                temporary = OUTPUT / f".{name}.tmp"
                shutil.copy2(artifact / "output" / name, temporary)
                os.replace(temporary, OUTPUT / name)
        print(json.dumps({"artifact": str(artifact), "EU": eu_report, "RU": ru_report}, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        if staging.exists(): shutil.rmtree(staging)
        print(f"区域覆盖全量生成失败：{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
