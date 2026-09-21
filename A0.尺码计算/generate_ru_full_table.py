#!/usr/bin/env python3
"""Generate the RU full-size table from the maintained RU dimensional rules."""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from full_table_schema import attach_dimension_code  # noqa: E402
import pandas_analysis as analysis


SOURCE_DIR = WORKSPACE_ROOT / "01.整理尺寸库" / "output"
RU_DIMENSIONS_PATH = SOURCE_DIR / "尺寸库_RU.csv"
RU_RAW_SOURCE_DIR = WORKSPACE_ROOT / "01.整理尺寸库" / "data" / "ru" / "0916"
RU_SALES_PATH = WORKSPACE_ROOT / "02.销量评估" / "data" / "ru" / "auto_ru_model_sales_with_match_key.csv"
DIMENSION_PROJECT = WORKSPACE_ROOT / "01.整理尺寸库"
RULES_PATH = SCRIPT_DIR / "data" / "ru" / "尺寸" / "0921.2-真实上限.csv"
PARAMETERS_PATH = SCRIPT_DIR / "data" / "ru" / "参数" / "0921.1-仅余量.csv"
OUTPUT_DIR = SCRIPT_DIR / "output"
ARTIFACTS_DIR = SCRIPT_DIR / "artifacts"

RULE_COLUMNS = ["亚马逊尺码", "OZON尺码", "发货尺码", "分类", "长_mm", "宽_mm", "高_mm"]
PARAMETER_NAMES = {"余量长容差"}


def _numeric(value: object) -> float:
    parsed = pd.to_numeric(str(value).strip(), errors="coerce")
    if pd.isna(parsed):
        raise analysis.DataContractError(f"规则数值无效：{value!r}")
    return float(parsed)


def read_parameters(path: Path) -> dict[str, float]:
    parameters = analysis._read_csv(path)
    analysis._require_columns(parameters, ["参数", "值"], "RU 尺码参数")
    values = {
        str(row["参数"]).strip(): _numeric(row["值"])
        for _, row in parameters.iterrows()
        if str(row["参数"]).strip()
    }
    missing = sorted(PARAMETER_NAMES - set(values))
    if missing:
        raise analysis.DataContractError(f"RU 尺码参数缺少：{', '.join(missing)}")
    return values


def read_rules(path: Path) -> pd.DataFrame:
    rules = analysis._read_csv(path)
    analysis._require_columns(rules, RULE_COLUMNS, "RU 尺码规则")
    result = rules[RULE_COLUMNS].copy()
    for column in ["亚马逊尺码", "分类"]:
        result[column] = result[column].astype("string").str.strip()
    if result["亚马逊尺码"].eq("").any() or result["分类"].eq("").any():
        raise analysis.DataContractError("RU 尺码规则的亚马逊尺码和分类不能为空")
    for column in ["长_mm", "宽_mm", "高_mm"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    if result[["长_mm", "宽_mm", "高_mm"]].isna().any().any():
        raise analysis.DataContractError("RU 尺码规则存在非数值的长、宽或高")
    if result.duplicated(["分类", "亚马逊尺码"]).any():
        raise analysis.DataContractError("RU 尺码规则中同分类的亚马逊尺码必须唯一")
    return result.sort_values(["分类", "长_mm", "宽_mm", "高_mm", "亚马逊尺码"], kind="stable")


def match_ru_sizes(
    vehicles: pd.DataFrame, rules: pd.DataFrame, parameters: dict[str, float]
) -> pd.DataFrame:
    """Match each vehicle to the smallest same-category rule that covers all dimensions.

    Rule 长/宽/高 are real fit upper limits; only 余量长容差 (rule length minus vehicle length) is a parameter.
    """
    required = ["分类", "L-MM", "W-MM", "H-MM"]
    analysis._require_columns(vehicles, required, "RU 全量基础表")
    by_category = {category: group for category, group in rules.groupby("分类", sort=False)}
    matched: list[dict[str, object]] = []
    for _, vehicle in vehicles.iterrows():
        category = str(vehicle["分类"]).strip()
        length, width, height = (pd.to_numeric(vehicle[column], errors="coerce") for column in ["L-MM", "W-MM", "H-MM"])
        if pd.isna(length) or pd.isna(width) or pd.isna(height):
            matched.append({"自动尺码": "数据不全", "OZON尺码": "", "发货尺码": "", "自动长度余量": "", "候选": "", "原因": "数据不全", "相差数值": ""})
            continue
        pool = by_category.get(category)
        if pool is None:
            matched.append({"自动尺码": "无可用尺码", "OZON尺码": "", "发货尺码": "", "自动长度余量": "", "候选": "", "原因": "无同分类规则", "相差数值": ""})
            continue
        fits = pool.loc[
            (pool["长_mm"] >= length)
            & (pool["宽_mm"] >= width)
            & (pool["高_mm"] >= height)
            & (pool["长_mm"] - length <= parameters["余量长容差"])
        ]
        if not fits.empty:
            rule = fits.iloc[0]
            matched.append({"自动尺码": rule["亚马逊尺码"], "OZON尺码": rule["OZON尺码"], "发货尺码": rule["发货尺码"], "自动长度余量": round(float(rule["长_mm"] - length), 1), "候选": "", "原因": "", "相差数值": ""})
            continue
        # Diagnostics select the closest dimensional upper-limit violation.
        differences = pd.concat([
            length - pool["长_mm"],
            width - pool["宽_mm"],
            height - pool["高_mm"],
            pool["长_mm"] - length - parameters["余量长容差"],
        ], axis=1)
        differences.columns = ["超长", "超宽", "超高", "超余量"]
        max_difference = differences.clip(lower=0).max(axis=1)
        nearest = max_difference.sort_values(kind="stable").index[0]
        rule = pool.loc[nearest]
        reason = differences.loc[nearest].idxmax()
        matched.append({"自动尺码": "无可用尺码", "OZON尺码": "", "发货尺码": "", "自动长度余量": "", "候选": rule["亚马逊尺码"], "原因": reason, "相差数值": round(float(max_difference.loc[nearest]), 1)})
    return pd.DataFrame(matched, index=vehicles.index)


def _load_file_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise analysis.DataContractError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_ru_sales_by_dimension() -> tuple[pd.DataFrame, dict[str, object]]:
    """Rebuild the source match_key groups and map their aggregated proxy sales to published RU IDs."""
    code_dir = DIMENSION_PROJECT / "code"
    if str(code_dir) not in sys.path:
        sys.path.insert(0, str(code_dir))
    from regional_size_common import build_dimension_library
    from regional_sources import build_ru_base as build_ru_source_base

    merge_module = _load_file_module(code_dir / "merge_dimension_library.py", "ru_dimension_merge")
    source_base, source_summary = build_ru_source_base(RU_RAW_SOURCE_DIR, sales_path=RU_SALES_PATH)
    library, metadata = build_dimension_library(source_base)
    sales_by_old_id = dict(
        zip(metadata["DIMENSION-ID"], pd.to_numeric(metadata["销量合计"], errors="coerce").fillna(0), strict=True)
    )
    rows = library.to_dict("records")
    for row in rows:
        row["_sales_total"] = float(sales_by_old_id.get(row["DIMENSION-ID"], 0))
    rows = merge_module.transform_region_rows(rows, "ru", aggregate_fields=("_sales_total",))
    sales = pd.DataFrame(
        {
            "DIMENSION-ID": [row["DIMENSION-ID"] for row in rows],
            "销量合计": [row["_sales_total"] for row in rows],
        }
    )
    if sales["DIMENSION-ID"].duplicated().any():
        raise analysis.DataContractError("RU 销量映射后的 DIMENSION-ID 不唯一")
    sales_source = analysis._read_csv(RU_SALES_PATH)
    sales_source["sale_detail"] = pd.to_numeric(sales_source["sale_detail"], errors="coerce").fillna(0)
    source_total = int(sales_source["sale_detail"].sum())
    matched_total = int(sales["销量合计"].sum())
    audit = {
        "sales_source_rows": int(len(sales_source)),
        "sales_source_positive_rows": int(sales_source["sale_detail"].gt(0).sum()),
        "sales_source_zero_rows": int(sales_source["sale_detail"].eq(0).sum()),
        "sales_source_total": source_total,
        "matched_sales_total": matched_total,
        "unmatched_sales_total": source_total - matched_total,
        "sales_rows_without_match_key": int(sales_source["match_key"].astype("string").fillna("").str.strip().eq("").sum()),
        "dimension_rows_with_positive_proxy_sales": int(sales["销量合计"].gt(0).sum()),
        "dimension_rows_with_zero_proxy_sales": int(sales["销量合计"].eq(0).sum()),
        "source_join_summary": source_summary,
    }
    return sales, audit


def build_ru_full_base(dimensions: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    """Build the full-table-compatible columns available from the dimension library."""
    required = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类", "L-IN", "W-IN", "H-IN"]
    analysis._require_columns(dimensions, required, "尺寸库")
    result = pd.DataFrame(index=dimensions.index)
    for column in ["MAKE", "MODEL", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类", "DIMENSION-ID"]:
        result[column] = dimensions[column]
    result["TRIM"] = ""
    for source, destination in [("L-IN", "L-MM"), ("W-IN", "W-MM"), ("H-IN", "H-MM")]:
        result[destination] = analysis._round_nullable(analysis._numeric(dimensions[source]) * analysis.MM_PER_INCH)
    result = result.merge(sales, on="DIMENSION-ID", how="left", validate="one_to_one")
    result["销量合计"] = pd.to_numeric(result["销量合计"], errors="coerce").fillna(0)
    if result["销量合计"].mod(1).ne(0).any():
        raise analysis.DataContractError("RU sale_detail 汇总结果不是整数")
    result["销量合计"] = result["销量合计"].round().astype("Int64")
    # Shape-derived fields are not available in the RU regional pipeline yet.
    for column in ["车形", "前宽-MM", "后宽-MM", "参考侧高", "插片指数", "等效长"]:
        result[column] = ""
    return result[[column for column in analysis.DEFAULT_OUTPUT_COLUMNS if column not in {"自动尺码", "自动长度余量", "候选", "原因", "相差数值"}]]


def next_artifact_dir() -> Path:
    prefix = f"{date.today().isoformat()}_"
    numbers = [int(match.group(1)) for path in ARTIFACTS_DIR.glob(f"{prefix}[0-9][0-9]_*") if (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))]
    return ARTIFACTS_DIR / f"{prefix}{max(numbers, default=0) + 1:02d}_ru-full-size-matching"


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, destination)


def main() -> int:
    artifact_dir = next_artifact_dir()
    artifact_output = artifact_dir / "output"
    artifact_inputs = artifact_dir / "input"
    try:
        rules = read_rules(RULES_PATH)
        parameters = read_parameters(PARAMETERS_PATH)
        dimensions = analysis._read_csv(RU_DIMENSIONS_PATH)
        sales, sales_audit = build_ru_sales_by_dimension()
        dimension_ids = set(dimensions["DIMENSION-ID"])
        sales_ids = set(sales["DIMENSION-ID"])
        if dimension_ids != sales_ids:
            raise analysis.DataContractError(
                f"RU 尺寸库与销量映射 ID 集合不一致：尺寸独有 {len(dimension_ids - sales_ids)}，销量独有 {len(sales_ids - dimension_ids)}"
            )
        base = build_ru_full_base(dimensions, sales)
        matched = match_ru_sizes(base, rules, parameters)
        result = base.copy()
        result = pd.concat([result, matched], axis=1)
        ordered = [*analysis.DEFAULT_OUTPUT_COLUMNS[:21], "OZON尺码", "发货尺码", *analysis.DEFAULT_OUTPUT_COLUMNS[21:]]
        result = attach_dimension_code(result[ordered])
        expected_rows = len(dimensions)
        summary = analysis.validate_result(result, expected_rows)
        if result["DIMENSION-ID"].duplicated().any():
            raise analysis.DataContractError("RU 全量表 DIMENSION-ID 不唯一")

        artifact_inputs.mkdir(parents=True)
        shutil.copy2(RULES_PATH, artifact_inputs / RULES_PATH.name)
        shutil.copy2(PARAMETERS_PATH, artifact_inputs / PARAMETERS_PATH.name)
        shutil.copy2(RU_DIMENSIONS_PATH, artifact_inputs / "尺寸库_RU.csv")
        shutil.copy2(RU_SALES_PATH, artifact_inputs / RU_SALES_PATH.name)
        shutil.copy2(RU_RAW_SOURCE_DIR / "auto_ru_dimensions_with_match_key.csv", artifact_inputs / "auto_ru_dimensions_with_match_key.csv")
        shutil.copy2(RU_RAW_SOURCE_DIR / "auto_ru_catalog_rank.csv", artifact_inputs / "auto_ru_catalog_rank.csv")
        full_path = artifact_output / "全量表_RU.csv"
        analysis.write_result(result, full_path)
        report = {
            **summary,
            "source": str(SOURCE_DIR),
            "dimensions": str(RU_DIMENSIONS_PATH),
            "sales_source": str(RU_SALES_PATH),
            "rules": str(RULES_PATH),
            "parameters": str(PARAMETERS_PATH),
            "size_distribution": result["自动尺码"].value_counts().to_dict(),
            "sales_audit": sales_audit,
        }
        report_path = artifact_output / "尺码匹配报告_RU.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (artifact_dir / "status.json").write_text(json.dumps({"status": "passed", "output": str(full_path), "report": str(report_path)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        atomic_copy(full_path, OUTPUT_DIR / full_path.name)
        atomic_copy(report_path, OUTPUT_DIR / report_path.name)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "status.json").write_text(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"生成失败：{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
