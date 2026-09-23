#!/usr/bin/env python3
"""按新尺码规则和店铺货架配置生成全尺码及各店铺全量表。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from full_table_schema import attach_dimension_code  # noqa: E402
from id_scheme import append_country_code  # noqa: E402
import pandas_analysis as analysis  # noqa: E402


def _required_mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise analysis.DataContractError(f"{name} 必须是 YAML 映射")
    return value


def load_shelf_config(
    config_path: Path,
) -> tuple[Path, str, dict[str, list[tuple[str, str]]]]:
    """读取并校验货架配置，返回规则路径、规则尺码字段和店铺映射。"""
    if not config_path.is_file():
        raise FileNotFoundError(f"店铺货架配置不存在：{config_path}")
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    root = _required_mapping(config, "店铺货架配置")
    rule_config = _required_mapping(root.get("规则"), "规则")
    rule_file = str(rule_config.get("文件", "")).strip()
    size_column = str(rule_config.get("尺码字段", "")).strip()
    if not rule_file or not size_column:
        raise analysis.DataContractError("规则必须包含“文件”和“尺码字段”")
    rule_path = (config_path.parent / rule_file).resolve()
    rules = analysis._read_csv(rule_path)
    analysis._require_columns(rules, [size_column], "店铺配置引用的尺码规则")
    valid_sizes = {
        text
        for value in rules[size_column]
        if (text := analysis._clean_text(value)) is not None
    }

    shops_config = _required_mapping(root.get("店铺"), "店铺")
    if not shops_config:
        raise analysis.DataContractError("店铺配置不能为空")
    shops: dict[str, list[tuple[str, str]]] = {}
    for raw_shop_name, raw_shop in shops_config.items():
        shop_name = str(raw_shop_name).strip()
        if not shop_name or re.search(r"[\\/:*?\"<>|]", shop_name):
            raise analysis.DataContractError(f"店铺名不能用于输出文件名：{raw_shop_name}")
        shop = _required_mapping(raw_shop, f"店铺 {shop_name}")
        raw_mappings = shop.get("尺码映射")
        if not isinstance(raw_mappings, list) or not raw_mappings:
            raise analysis.DataContractError(f"店铺 {shop_name} 的尺码映射不能为空")
        mappings: list[tuple[str, str]] = []
        for index, raw_mapping in enumerate(raw_mappings, start=1):
            mapping = _required_mapping(raw_mapping, f"店铺 {shop_name} 第 {index} 条尺码映射")
            match_size = analysis._clean_text(mapping.get("匹配尺码"))
            shipping_size = analysis._clean_text(mapping.get("发货尺码"))
            if match_size is None or shipping_size is None:
                raise analysis.DataContractError(
                    f"店铺 {shop_name} 第 {index} 条必须包含匹配尺码和发货尺码"
                )
            mappings.append((match_size, shipping_size))
        match_sizes = [item[0] for item in mappings]
        duplicates = sorted({size for size in match_sizes if match_sizes.count(size) > 1})
        if duplicates:
            raise analysis.DataContractError(
                f"店铺 {shop_name} 的匹配尺码重复：{', '.join(duplicates)}"
            )
        unknown_match = sorted(set(match_sizes) - valid_sizes)
        unknown_shipping = sorted({item[1] for item in mappings} - valid_sizes)
        if unknown_match:
            raise analysis.DataContractError(
                f"店铺 {shop_name} 的匹配尺码不在规则中：{', '.join(unknown_match)}"
            )
        if unknown_shipping:
            raise analysis.DataContractError(
                f"店铺 {shop_name} 的发货尺码不在规则中：{', '.join(unknown_shipping)}"
            )
        shops[shop_name] = mappings
    return rule_path, size_column, shops


def apply_shipping_sizes(
    result: pd.DataFrame, mappings: Iterable[tuple[str, str]]
) -> pd.DataFrame:
    """将规则匹配结果和诊断候选转换为店铺发货尺码。"""
    size_map = dict(mappings)
    mapped = result.copy()
    for column in ["自动尺码", "候选"]:
        mapped[column] = mapped[column].map(
            lambda value: size_map.get(value, value)
        )
    return mapped


def _calculate(
    source_dir: Path,
    config_dir: Path,
    rule_path: Path,
    submodel_path: Path | None,
    trim_source: Path | None,
    allowed_sizes: Iterable[str] | None = None,
    include_analysis: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
    return analysis.calculate(
        source_dir,
        submodel_path=submodel_path,
        config_dir=config_dir,
        rules_path=rule_path,
        trim_source=trim_source,
        include_analysis=include_analysis,
        allowed_sizes=allowed_sizes,
    )


def us_rows(result: pd.DataFrame) -> pd.DataFrame:
    """The consolidated source may already contain regional DIMENSION-ID suffixes."""
    ids = result["DIMENSION-ID"].fillna("").astype(str)
    return result.loc[~ids.str.endswith((" EU", " RU"))].copy()


def us_dimension_id(value: object) -> str:
    text = str(value)
    return text if text.endswith(" US") else append_country_code(text, "US")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=WORKSPACE_ROOT / "02.分类结构审核" / "output",
        help="分类结构审核节点输出目录（车型结构.csv）",
    )
    parser.add_argument(
        "--shelf-config",
        type=Path,
        default=SCRIPT_DIR / "data" / "店铺分组" / "货架.yaml",
        help="店铺货架 YAML",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="输出目录；默认在尺码计算/artifacts 下创建新批次",
    )
    parser.add_argument(
        "--no-submodel",
        action="store_true",
        help="不读取子车系维护表，TRIM 留空",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    shelf_config = args.shelf_config.resolve()
    try:
        rule_path, size_column, shops = load_shelf_config(shelf_config)
        config_dir = rule_path.parent
        submodel_path = analysis.resolve_submodel_path(
            source_dir, None, args.no_submodel
        )
        trim_source = analysis.CURRENT_OUTPUT
        if args.no_submodel or submodel_path is not None or not trim_source.is_file():
            trim_source = None
        output_dir = (
            args.output_dir.resolve()
            if args.output_dir
            else analysis.next_artifact_output_dir(
                SCRIPT_DIR / "artifacts", "0917-1-new-naming-store-groups"
            )
        )

        full_result, dimension_analysis = _calculate(
            source_dir,
            config_dir,
            rule_path,
            submodel_path,
            trim_source,
            include_analysis=True,
        )
        expected_rows = len(us_rows(analysis._read_csv(analysis.resolve_data_file(source_dir, "dimensions"))))
        outputs: dict[str, dict[str, object]] = {}
        full_result = us_rows(full_result)
        dimension_analysis = us_rows(dimension_analysis)
        full_result["DIMENSION-ID"] = full_result["DIMENSION-ID"].map(us_dimension_id)
        dimension_analysis["DIMENSION-ID"] = dimension_analysis["DIMENSION-ID"].map(us_dimension_id)
        full_result = attach_dimension_code(full_result)
        dimension_analysis = attach_dimension_code(dimension_analysis)
        full_path = output_dir / "全量表_US.csv"
        analysis_path = output_dir / "尺寸分析表_US.csv"
        analysis.write_result(full_result, full_path)
        analysis.write_result(dimension_analysis, analysis_path)
        outputs["全尺码"] = {
            **analysis.validate_result(full_result, expected_rows),
            "output": str(full_path),
        }

        for shop_name, mappings in shops.items():
            store_result = _calculate(
                source_dir,
                config_dir,
                rule_path,
                submodel_path,
                trim_source,
                allowed_sizes=[item[0] for item in mappings],
            )
            store_result = apply_shipping_sizes(store_result, mappings)
            store_result = us_rows(store_result)
            store_result["DIMENSION-ID"] = store_result["DIMENSION-ID"].map(us_dimension_id)
            store_result = attach_dimension_code(store_result)
            store_path = output_dir / f"店铺全量_{shop_name}.csv"
            analysis.write_result(store_result, store_path)
            outputs[shop_name] = {
                **analysis.validate_result(store_result, expected_rows),
                "matching_sizes": len(mappings),
                "shipping_sizes": len({item[1] for item in mappings}),
                "output": str(store_path),
            }

        summary = {
            "rules_file": str(rule_path),
            "rules_size_column": size_column,
            "shelf_config": str(shelf_config),
            "source_dir": str(source_dir),
            "dimension_analysis": str(analysis_path),
            "outputs": outputs,
        }
        status_path = output_dir / "status.json"
        status_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "尺码匹配报告_US.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        summary["status"] = str(status_path)
        if args.output_dir is None:
            current_output = SCRIPT_DIR / "output"
            for generated in output_dir.iterdir():
                if generated.is_file():
                    analysis.promote_file(generated, current_output / generated.name)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except (analysis.DataContractError, FileNotFoundError, pd.errors.ParserError, yaml.YAMLError) as error:
        print(f"生成失败：{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
