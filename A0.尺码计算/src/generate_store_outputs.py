#!/usr/bin/env python3
"""生成 US 全量表、各店铺全量表与 TRIM适配器（US 的尺码匹配与 TRIM 匹配在同一次运行内完成）。

1. 按 data/US/店铺/货架.yaml 指定的当前 US 规则计算全尺码结果；各店铺先按货架限定候选池再换成发货尺码。
2. 用 data/US/TRIM 的已审核 TrimList/TRIM 值做 TRIM 匹配：回填 US 全量表与店铺全量表的 TRIM 列，并生成 TRIM适配器。
3. 全部写入新的 artifacts/<批次>/output/（按 output_layout 的 <国别>/<类别>/ 布局），校验通过后原子更新 output/。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
WORKSPACE_ROOT = PROJECT_DIR.parent
if str(WORKSPACE_ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT / "lib"))

from id_scheme import append_country_code  # noqa: E402
import data_layout  # noqa: E402
import output_layout as layout  # noqa: E402
import pandas_analysis as analysis  # noqa: E402
from trim.matching import match_trims  # noqa: E402


def _required_mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise analysis.DataContractError(f"{name} 必须是 YAML 映射")
    return value


def load_shelf_config(
    config_path: Path,
    region_config: data_layout.RegionConfig | None = None,
) -> tuple[Path, str, dict[str, list[tuple[str, str]]]]:
    """读取并校验货架配置，返回当前 US 规则路径、规则尺码字段和店铺映射。

    规则与尺码字段取自 data/当前规则.yaml（US）；货架只维护店铺的匹配尺码与发货尺码。
    """
    if not config_path.is_file():
        raise FileNotFoundError(f"店铺货架配置不存在：{config_path}")
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    root = _required_mapping(config, "店铺货架配置")
    region_config = region_config or data_layout.current("US")
    rule_path, size_column = region_config.rules, region_config.size_column
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
    parameters_path: Path,
    rule_path: Path,
    allowed_sizes: Iterable[str] | None = None,
) -> pd.DataFrame:
    result = analysis.calculate(
        source_dir,
        config_dir=parameters_path.parent,
        rules_path=rule_path,
        parameters_path=parameters_path,
        allowed_sizes=allowed_sizes,
    )
    result = us_rows(result)
    result["DIMENSION-ID"] = result["DIMENSION-ID"].map(us_dimension_id)
    return result


def us_rows(result: pd.DataFrame) -> pd.DataFrame:
    """The consolidated source may already contain regional DIMENSION-ID suffixes."""
    ids = result["DIMENSION-ID"].fillna("").astype(str)
    return result.loc[~ids.str.endswith((" EU", " RU"))].copy()


def us_dimension_id(value: object) -> str:
    text = str(value)
    return text if text.endswith(" US") else append_country_code(text, "US")


def fill_trims(result: pd.DataFrame, trims: Mapping[str, str]) -> pd.DataFrame:
    """TRIM 列取 TRIM 匹配结果；未匹配的 DIMENSION-ID 留空。"""
    filled = result.copy()
    filled["TRIM"] = filled["DIMENSION-ID"].map(trims).fillna("")
    return filled


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
        default=data_layout.SHELF_CONFIG,
        help="店铺货架 YAML",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="输出目录；默认在尺码计算/artifacts 下创建新批次",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    shelf_config = args.shelf_config.resolve()
    try:
        rule_path, size_column, shops = load_shelf_config(shelf_config)
        config_dir = data_layout.current("US").parameters
        output_dir = (
            args.output_dir.resolve()
            if args.output_dir
            else analysis.next_artifact_output_dir(PROJECT_DIR / "artifacts", "us-size-trim")
        )
        expected_rows = len(us_rows(analysis._read_csv(analysis.resolve_data_file(source_dir, "dimensions"))))

        full_result = _calculate(source_dir, config_dir, rule_path)
        trim = match_trims(full_result, output_dir.parent / "trim")
        full_result = fill_trims(full_result, trim.trims)
        full_path = output_dir / layout.full_table("US")
        analysis.write_result(full_result, full_path)
        outputs: dict[str, dict[str, object]] = {
            "全尺码": {**analysis.validate_result(full_result, expected_rows), "output": str(full_path)}
        }

        for shop_name, mappings in shops.items():
            store_result = _calculate(
                source_dir, config_dir, rule_path, allowed_sizes=[item[0] for item in mappings]
            )
            store_result = fill_trims(apply_shipping_sizes(store_result, mappings), trim.trims)
            if store_result["DIMENSION-ID"].tolist() != full_result["DIMENSION-ID"].tolist():
                raise analysis.DataContractError(f"店铺 {shop_name} 全量表与 US 全量表行不一致")
            store_path = output_dir / layout.store_table(shop_name)
            analysis.write_result(store_result, store_path)
            outputs[shop_name] = {
                **analysis.validate_result(store_result, expected_rows),
                "matching_sizes": len(mappings),
                "shipping_sizes": len({item[1] for item in mappings}),
                "output": str(store_path),
            }

        adapter_path = output_dir / layout.TRIM_ADAPTER
        adapter_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(trim.adapter, adapter_path)

        summary = {
            "rules_file": str(rule_path),
            "rules_size_column": size_column,
            "parameters_file": str(config_dir),
            "shelf_config": str(shelf_config),
            "source_dir": str(source_dir),
            "trim": {**trim.status, "data_dir": str(data_layout.TRIM_DIR), "adapter": str(adapter_path)},
            "outputs": outputs,
        }
        (output_dir.parent / "status.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if args.output_dir is None:
            current_output = PROJECT_DIR / "output"
            for generated in output_dir.rglob("*"):
                if generated.is_file():
                    analysis.promote_file(generated, current_output / generated.relative_to(output_dir))
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except (analysis.DataContractError, FileNotFoundError, ValueError, pd.errors.ParserError, yaml.YAMLError) as error:
        print(f"生成失败：{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
