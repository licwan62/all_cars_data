#!/usr/bin/env python3
"""隔离运行 07 车衣数据的半周长尺码匹配测试，不发布到 source。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


TEST_DIR = Path(__file__).resolve().parent
SIZE_PROJECT_DIR = TEST_DIR.parent
WORKSPACE_DIR = SIZE_PROJECT_DIR.parent
if str(SIZE_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(SIZE_PROJECT_DIR))

import pandas_analysis as base  # noqa: E402


DEFAULT_COVER_SOURCE = WORKSPACE_DIR / "source" / "车衣数据" / "07-车衣数据.csv"
DEFAULT_SOURCE_DIR = WORKSPACE_DIR / "source"
DEFAULT_BASE_RULES = SIZE_PROJECT_DIR / "rules" / "尺码匹配规则.csv"
DEFAULT_PARAMETERS = SIZE_PROJECT_DIR / "rules" / "尺码匹配参数.csv"
DEFAULT_OUTPUT = TEST_DIR / "output" / "半周长测试结果.csv"
DEFAULT_RULE_OUTPUT = TEST_DIR / "rules" / "半周长匹配规则.csv"

# 07 表中的型号与现行规则名称不完全一致。这里只保留能够从现有命名
# 明确确认的别名；其余缺少侧片长的尺码继续保留规则行，但不参与匹配。
EXPLICIT_COVER_ALIASES = {
    "YM": "YM+",
}

TEST_LIMITS = (
    base.LimitSpec("半周长上限", "参考半周长", "半周长超上限", is_length=True),
    base.LimitSpec("参考插片上限", "参考插片", "参考插片超上限"),
)


def add_reference_half_perimeter(
    vehicles: pd.DataFrame,
    references: pd.DataFrame,
) -> pd.DataFrame:
    """按车形周长系数计算参考半周长，单位为毫米。"""

    base._require_columns(vehicles, ["车形", "L-MM", "H-MM"], "车型计算结果")
    base._require_columns(references, ["车身号", "周长系数"], "参考尺寸计算")
    if references["车身号"].duplicated().any():
        raise base.DataContractError("参考尺寸计算的车身号必须唯一")

    factors = references[["车身号", "周长系数"]].copy()
    factors = factors.rename(columns={"车身号": "车形"})
    factors["车形"] = factors["车形"].astype("string").str.strip()
    factors["周长系数"] = base._coefficient(factors["周长系数"])

    result = vehicles.merge(factors, on="车形", how="left", validate="many_to_one")
    length = result["L-MM"].astype("Float64")
    height = result["H-MM"].astype("Float64")
    result["参考半周长"] = base._round_nullable(
        (length + height) * result["周长系数"] - base.PANEL_OFFSET_MM
    )
    return result


def _cover_alias_candidates(rule: pd.Series) -> list[str]:
    candidates: list[str] = []
    internal_size = base._clean_text(rule.get("内部尺码"))
    logical_size = base._clean_text(rule.get("逻辑尺码"))
    note = base._clean_text(rule.get("备注"))
    note_alias = note[1:].strip() if note and note.startswith("=") else None

    for candidate in (internal_size, note_alias, logical_size):
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    for key in (internal_size, logical_size):
        alias = EXPLICIT_COVER_ALIASES.get(key or "")
        if alias and alias not in candidates:
            candidates.append(alias)
    return candidates


def build_half_perimeter_rules(
    base_rules: pd.DataFrame,
    cover_sizes: pd.DataFrame,
) -> pd.DataFrame:
    """把 07 侧片长作为半周长上限，并完整保留原规则优先级。"""

    base._require_columns(
        base_rules,
        [
            "逻辑尺码",
            "内部尺码",
            "档位序号",
            "分类",
            "CAB",
            "版本",
            "长上限",
            "参考插片上限",
            "使用",
            "备注",
        ],
        "尺码匹配规则",
    )
    base._require_columns(cover_sizes, ["型号", "侧片长"], "07-车衣数据")

    cover = cover_sizes[["型号", "侧片长"]].copy()
    cover["型号"] = cover["型号"].map(base._clean_text)
    cover["侧片长"] = base._numeric(cover["侧片长"])
    cover = cover.loc[cover["型号"].notna() & cover["侧片长"].notna()].copy()
    if cover["型号"].duplicated().any():
        duplicates = sorted(cover.loc[cover["型号"].duplicated(False), "型号"].astype(str).unique())
        raise base.DataContractError(f"07-车衣数据的型号重复：{', '.join(duplicates)}")
    cover_by_model = cover.set_index("型号")["侧片长"].to_dict()

    result = base_rules.copy()
    result.insert(result.columns.get_loc("长上限") + 1, "原长上限", result["长上限"])
    half_perimeter_limits: list[float | None] = []
    cover_models: list[str | None] = []
    for _, rule in result.iterrows():
        selected_model: str | None = None
        selected_value: float | None = None
        for candidate in _cover_alias_candidates(rule):
            if candidate in cover_by_model:
                selected_model = candidate
                selected_value = float(cover_by_model[candidate]) * 10.0
                break
        cover_models.append(selected_model)
        half_perimeter_limits.append(selected_value)

    result["半周长上限"] = pd.array(half_perimeter_limits, dtype="Float64")
    result["车衣数据型号"] = pd.array(cover_models, dtype="string")
    result["半周长上限来源"] = result["车衣数据型号"].map(
        lambda value: "07-车衣数据.csv / 侧片长×10" if pd.notna(value) else "缺少可用侧片长"
    )

    ordered_columns = [
        "逻辑尺码",
        "内部尺码",
        "档位序号",
        "分类",
        "CAB",
        "版本",
        "半周长上限",
        "参考插片上限",
        "使用",
        "备注",
        "车衣数据型号",
        "半周长上限来源",
        "原长上限",
    ]
    return result[ordered_columns]


def calculate_test(
    source_dir: Path = DEFAULT_SOURCE_DIR,
    cover_source: Path = DEFAULT_COVER_SOURCE,
    base_rules_path: Path = DEFAULT_BASE_RULES,
    parameters_path: Path = DEFAULT_PARAMETERS,
    submodel_path: Path | None = None,
    sort_output: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dimensions = base._read_csv(base.resolve_data_file(source_dir, "dimensions"))
    bodies = base._read_csv(base.resolve_data_file(source_dir, "bodies"))
    sales = base._read_csv(base.resolve_data_file(source_dir, "sales"))
    references = base._read_csv(source_dir / "参考尺寸计算.csv")
    parameters = base._read_csv(parameters_path)
    base_rules = base._read_csv(base_rules_path)
    cover_sizes = base._read_csv(cover_source)
    submodels = base._read_csv(submodel_path) if submodel_path is not None else None

    rules = build_half_perimeter_rules(base_rules, cover_sizes)
    result = base.build_vehicle_base(dimensions, submodels)
    sales_total = base.aggregate_sales(sales)
    result = result.merge(sales_total, on="DIMENSION-ID", how="left", validate="one_to_one")
    result["销量合计"] = result["销量合计"].fillna(0)
    if np.allclose(result["销量合计"].dropna() % 1, 0):
        result["销量合计"] = result["销量合计"].round().astype("Int64")
    result = base.add_body_dimensions(result, bodies, references)
    result = add_reference_half_perimeter(result, references)

    matcher = base.SizeMatcher(parameters, rules, limits=TEST_LIMITS)
    result = matcher.apply(result).rename(columns={"自动长度余量": "自动半周长余量"})
    if sort_output:
        result = result.sort_values(
            "DIMENSION-ID", ascending=True, na_position="last", kind="stable"
        ).reset_index(drop=True)

    output_columns = [
        "MAKE",
        "MODEL",
        "TRIM",
        "版本",
        "结构",
        "CAB",
        "BED",
        "代际",
        "YEAR",
        "分类",
        "L-MM",
        "W-MM",
        "H-MM",
        "销量合计",
        "车形",
        "周长系数",
        "参考半周长",
        "前宽-MM",
        "后宽-MM",
        "参考侧高",
        "参考插片",
        "自动尺码",
        "自动半周长余量",
        "候选",
        "原因",
        "相差数值",
        "DIMENSION-ID",
    ]
    result = result[output_columns].copy()
    result["自动半周长余量"] = base._compact_number_column(result["自动半周长余量"])
    result["相差数值"] = base._compact_number_column(result["相差数值"])
    return result, rules


def validate_test_result(result: pd.DataFrame, rules: pd.DataFrame, expected_rows: int) -> dict[str, object]:
    summary = base.validate_result(result.rename(columns={"自动半周长余量": "自动长度余量"}), expected_rows)
    source_priorities = base._read_csv(DEFAULT_BASE_RULES)["档位序号"].reset_index(drop=True)
    test_priorities = rules["档位序号"].reset_index(drop=True)
    if not source_priorities.equals(test_priorities):
        raise base.DataContractError("测试规则的档位序号或行序发生变化")
    summary.update(
        {
            "rules": int(len(rules)),
            "rules_with_half_perimeter_limit": int(rules["半周长上限"].notna().sum()),
            "active_rules_with_half_perimeter_limit": int(
                (
                    rules["使用"].astype("string").str.strip().str.casefold().eq("y")
                    & rules["半周长上限"].notna()
                ).sum()
            ),
            "half_perimeter_formula": "(L-MM + H-MM) * 周长系数 - 750",
            "published": False,
        }
    )
    return summary


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--cover-source", type=Path, default=DEFAULT_COVER_SOURCE)
    parser.add_argument("--base-rules", type=Path, default=DEFAULT_BASE_RULES)
    parser.add_argument("--parameters", type=Path, default=DEFAULT_PARAMETERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--rule-output", type=Path, default=DEFAULT_RULE_OUTPUT)
    parser.add_argument("--submodel-source", type=Path)
    parser.add_argument("--no-submodel", action="store_true")
    parser.add_argument("--keep-source-order", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_dir = args.source_dir.resolve()
    try:
        submodel_path = base.resolve_submodel_path(
            source_dir,
            args.submodel_source.resolve() if args.submodel_source else None,
            args.no_submodel,
        )
        result, rules = calculate_test(
            source_dir=source_dir,
            cover_source=args.cover_source.resolve(),
            base_rules_path=args.base_rules.resolve(),
            parameters_path=args.parameters.resolve(),
            submodel_path=submodel_path,
            sort_output=not args.keep_source_order,
        )
        expected_rows = len(base._read_csv(base.resolve_data_file(source_dir, "dimensions")))
        summary = validate_test_result(result, rules, expected_rows)
        base.write_result(result, args.output.resolve())
        base.write_result(rules, args.rule_output.resolve())
    except (base.DataContractError, FileNotFoundError, pd.errors.ParserError) as error:
        print(f"半周长测试计算失败：{error}", file=sys.stderr)
        return 2

    summary.update(
        {
            "output": str(args.output.resolve()),
            "rule_output": str(args.rule_output.resolve()),
            "source": str(args.cover_source.resolve()),
        }
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
