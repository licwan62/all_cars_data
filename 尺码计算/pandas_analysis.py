#!/usr/bin/env python3
"""用 pandas 复现车型车罩尺码的 Power Query 计算链。"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from datetime import date
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


MM_PER_INCH = 25.4
PANEL_OFFSET_MM = 750.0
EQUIVALENT_LENGTH_OFFSET_MM = 1500.0
DEFAULT_OUTPUT_COLUMNS = [
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
    "前宽-MM",
    "后宽-MM",
    "参考侧高",
    "插片指数",
    "等效长",
    "自动尺码",
    "自动长度余量",
    "候选",
    "原因",
    "相差数值",
    "DIMENSION-ID",
]


class DataContractError(ValueError):
    """输入表结构或关键数据不符合计算契约。"""


@dataclass(frozen=True)
class LimitSpec:
    """一个“车型值 <= 尺码上限”的动态匹配维度。"""

    rule_column: str
    source_column: str
    reason: str
    is_length: bool = False


DEFAULT_LIMITS = (
    LimitSpec("长上限", "L-MM", "超长", is_length=True),
    LimitSpec("插片指数上限", "插片指数", "插片指数超上限"),
)

SOURCE_FILE_ALIASES = {
    "dimensions": ("尺寸库.csv", "车型尺寸库.csv", "车型尺寸.csv"),
    "bodies": ("车身分类.csv", "车型形状分类.csv", "车型车身.csv"),
    "sales": ("销量明细.csv", "atom_sales.csv"),
}

CONFIG_FILES = {
    "parameters": "尺码匹配参数.csv",
    "rules": "尺码匹配规则.csv",
}


@dataclass(frozen=True)
class MatchResult:
    auto_size: str
    length_margin: float | None = None
    candidate: str | None = None
    reason: str | None = None
    difference: float | None = None
    has_final_candidate: bool = False


@dataclass
class SizePool:
    candidates: list[dict[str, object]]
    max_length: float | None


def _require_columns(frame: pd.DataFrame, columns: Iterable[str], table_name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise DataContractError(f"{table_name} 缺少字段：{', '.join(missing)}")


def resolve_data_file(directory: Path, logical_name: str) -> Path:
    """Resolve a canonical source filename, with legacy project-input fallback."""
    aliases = SOURCE_FILE_ALIASES[logical_name]
    for filename in aliases:
        candidate = directory / filename
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"数据源目录 {directory} 缺少 {logical_name}：应存在 {' 或 '.join(aliases)}"
    )


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"输入文件不存在：{path}")
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )


def _clean_text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _numeric(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip().str.replace(",", "", regex=False)
    return pd.to_numeric(normalized, errors="coerce")


def _coefficient(series: pd.Series) -> pd.Series:
    """Read decimal coefficients while retaining legacy ``81%`` support."""

    normalized = series.astype("string").str.strip()
    has_percent_sign = normalized.str.endswith("%", na=False)
    numeric = pd.to_numeric(normalized.str.rstrip("%"), errors="coerce")
    return numeric.where(~has_percent_sign, numeric / 100.0)


def _round_nullable(series: pd.Series, digits: int = 0) -> pd.Series:
    """按 Power Query Number.Round 的默认舍入方式（四舍六入五成双）舍入。"""

    result = series.round(digits)
    if digits == 0:
        return result.astype("Int64")
    return result.astype("Float64")


def _compact_number_column(series: pd.Series) -> pd.Series:
    """写 CSV 时将 146.0 写作 146，同时保留真正的一位小数。"""

    values: list[object] = []
    for value in series:
        if value is None or pd.isna(value):
            values.append(None)
        else:
            number = float(value)
            values.append(int(number) if number.is_integer() else number)
    return pd.Series(values, index=series.index, dtype=object)


def _parse_year_range(value: object) -> tuple[int | None, int | None]:
    text = _clean_text(value)
    if text is None:
        return None, None
    normalized = re.sub(r"[/–—－]", "-", text)
    parts = [part.strip() for part in normalized.split("-") if part.strip()]
    if not parts:
        return None, None
    try:
        start = int(float(parts[0]))
        end = int(float(parts[-1])) if len(parts) > 1 else start
    except ValueError:
        return None, None
    return start, end


def _prepare_submodel_index(submodels: pd.DataFrame) -> dict[tuple[str, str, str], list[tuple[int, str]]]:
    required = ["Year", "主车型", "结构", "版本", "候选车型"]
    _require_columns(submodels, required, "子车系维护表")
    selected = submodels[required].copy()
    selected["Year"] = pd.to_numeric(selected["Year"], errors="coerce").astype("Int64")
    for column in ["主车型", "结构", "版本", "候选车型"]:
        selected[column] = selected[column].map(lambda value: _clean_text(value) or "")
    selected = selected.loc[
        selected["Year"].notna()
        & selected["主车型"].ne("")
        & selected["候选车型"].ne("")
    ].copy()
    selected["候选车型"] = selected["候选车型"].str.split(";")
    selected = selected.explode("候选车型", ignore_index=True)
    selected["候选车型"] = selected["候选车型"].str.strip()
    selected = selected.loc[selected["候选车型"].ne("")].drop_duplicates(required)

    grouped = (
        selected.groupby(["Year", "主车型", "结构", "版本"], sort=False, dropna=False)[
            "候选车型"
        ]
        .agg(lambda values: "; ".join(sorted(set(values))))
        .reset_index()
    )
    index: dict[tuple[str, str, str], list[tuple[int, str]]] = {}
    for row in grouped.itertuples(index=False, name=None):
        year, main_model, structure, version, candidates = row
        index.setdefault((main_model, structure, version), []).append((int(year), candidates))
    return index


def _format_trim_candidates(candidates: Iterable[str]) -> str:
    """去掉“品牌|”前缀和连字符，以紧凑逗号连接去重后的 TRIM。"""

    normalized: list[str] = []
    seen: set[str] = set()
    for candidate in sorted(candidates):
        trim = candidate.split("|", 1)[1] if "|" in candidate else candidate
        trim = re.sub(r"[-‐‑‒–—－]", "", trim).strip()
        if trim and trim not in seen:
            seen.add(trim)
            normalized.append(trim)
    return ",".join(normalized)


def add_trims(dimensions: pd.DataFrame, submodels: pd.DataFrame | None) -> pd.Series:
    """按 q_全量 的关联规则生成去品牌、去连字符的 TRIM。"""

    if submodels is None:
        return pd.Series("", index=dimensions.index, dtype="string")

    index = _prepare_submodel_index(submodels)
    values: list[str] = []
    for row in dimensions[["MAKE", "MODEL", "结构", "版本", "YEAR"]].itertuples(
        index=False, name=None
    ):
        make, model, structure, version, year_value = row
        main_model = " ".join(
            part for part in (_clean_text(make), _clean_text(model)) if part is not None
        )
        key = (main_model, _clean_text(structure) or "", _clean_text(version) or "")
        start, end = _parse_year_range(year_value)
        candidates: set[str] = set()
        if start is not None and end is not None:
            for year, joined_candidates in index.get(key, []):
                if start <= year <= end:
                    candidates.update(
                        item.strip() for item in joined_candidates.split(";") if item.strip()
                    )
        values.append(_format_trim_candidates(candidates))
    return pd.Series(values, index=dimensions.index, dtype="string")


def build_vehicle_base(dimensions: pd.DataFrame, submodels: pd.DataFrame | None = None) -> pd.DataFrame:
    required = [
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
    ]
    _require_columns(dimensions, required, "车型尺寸")
    base = dimensions[required].copy()
    if base["DIMENSION-ID"].duplicated().any():
        examples = base.loc[base["DIMENSION-ID"].duplicated(), "DIMENSION-ID"].head(3).tolist()
        raise DataContractError(f"车型尺寸的 DIMENSION-ID 不唯一，例如：{examples}")

    base["TRIM"] = add_trims(base, submodels)
    for inch_column, mm_column in [("L-IN", "L-MM"), ("W-IN", "W-MM"), ("H-IN", "H-MM")]:
        base[mm_column] = _round_nullable(_numeric(base[inch_column]) * MM_PER_INCH)
    return base.drop(columns=["L-IN", "W-IN", "H-IN"])


def aggregate_sales(sales: pd.DataFrame) -> pd.DataFrame:
    _require_columns(sales, ["atom_record_id", "预估销量"], "销量明细")
    normalized = sales[["atom_record_id", "预估销量"]].copy()
    normalized["DIMENSION-ID"] = (
        normalized["atom_record_id"]
        .astype("string")
        .str.split("|ATOM_YEAR=", n=1, regex=False)
        .str[0]
    )
    normalized["预估销量"] = _numeric(normalized["预估销量"])
    grouped = (
        normalized.groupby("DIMENSION-ID", as_index=False, sort=False, dropna=False)["预估销量"]
        .sum(min_count=1)
        .rename(columns={"预估销量": "销量合计"})
    )
    return grouped


def add_body_dimensions(
    vehicles: pd.DataFrame,
    bodies: pd.DataFrame,
    references: pd.DataFrame,
) -> pd.DataFrame:
    _require_columns(bodies, ["DIMENSION-ID", "车形"], "车身分类")
    reference_columns = [
        "车身号",
        "前宽系数",
        "后宽系数",
        "弧长系数",
    ]
    _require_columns(references, reference_columns, "参考尺寸计算")
    if bodies["DIMENSION-ID"].duplicated().any():
        raise DataContractError("车身分类的 DIMENSION-ID 必须唯一")
    if references["车身号"].duplicated().any():
        raise DataContractError("参考尺寸计算的车身号必须唯一")

    body_map = bodies[["DIMENSION-ID", "车形"]].copy()
    body_map["车形"] = body_map["车形"].astype("string").str.strip()
    body_map["车形"] = body_map["车形"].mask(body_map["车形"].eq(""))
    factors = references[reference_columns].copy()
    factors = factors.rename(columns={"车身号": "车形"})
    factors["车形"] = factors["车形"].astype("string").str.strip()
    for column in reference_columns[1:]:
        factors[column] = _coefficient(factors[column])

    result = vehicles.merge(body_map, on="DIMENSION-ID", how="left", validate="one_to_one")
    result = result.merge(factors, on="车形", how="left", validate="many_to_one")

    width = result["W-MM"].astype("Float64")
    height = result["H-MM"].astype("Float64")
    result["前宽-MM"] = _round_nullable(width * result["前宽系数"])
    result["后宽-MM"] = _round_nullable(width * result["后宽系数"])
    result["参考侧高"] = _round_nullable(
        (height + width / 2) * result["弧长系数"] - PANEL_OFFSET_MM
    )
    legacy_insert_index = (
        (result["前宽-MM"].astype("Float64") + result["后宽-MM"].astype("Float64"))
        / 4
        - PANEL_OFFSET_MM
    )
    pickup_insert_index = (
        result["前宽-MM"].astype("Float64") / 2 - PANEL_OFFSET_MM
    )
    result["插片指数"] = _round_nullable(
        legacy_insert_index.where(result["分类"].ne("皮卡"), pickup_insert_index)
    )
    return result.drop(columns=reference_columns[1:])


def add_equivalent_length(vehicles: pd.DataFrame, references: pd.DataFrame) -> pd.DataFrame:
    """按车形周长系数计算仅供参考留痕的等效长，单位为毫米。"""
    _require_columns(vehicles, ["车形", "L-MM", "W-MM"], "车型计算结果")
    _require_columns(references, ["车身号", "周长系数"], "参考尺寸计算")
    if references["车身号"].duplicated().any():
        raise DataContractError("参考尺寸计算的车身号必须唯一")
    factors = references.set_index("车身号")["周长系数"]
    factors.index = factors.index.str.strip()
    if factors.index.duplicated().any():
        raise DataContractError("参考尺寸计算的车身号去空格后必须唯一")
    factor = vehicles["车形"].map(_coefficient(factors))
    result = vehicles.copy()
    result["等效长"] = _round_nullable(
        (result["L-MM"].astype("Float64") + result["W-MM"].astype("Float64"))
        * factor - EQUIVALENT_LENGTH_OFFSET_MM
    )
    return result


def add_reference_half_perimeter(vehicles: pd.DataFrame, references: pd.DataFrame) -> pd.DataFrame:
    """兼容旧调用名；返回采用新公式计算的“等效长”。"""
    return add_equivalent_length(vehicles, references)


class SizeMatcher:
    """Power Query 尺码函数的索引化 pandas 实现。"""

    def __init__(
        self,
        parameters: pd.DataFrame,
        rules: pd.DataFrame,
        limits: Sequence[LimitSpec] = DEFAULT_LIMITS,
        include_disabled_rules: bool = False,
    ) -> None:
        self.limits = tuple(limits)
        if not self.limits:
            raise DataContractError("上限字段配置不能为空")
        length_positions = [index for index, spec in enumerate(self.limits) if spec.is_length]
        if len(length_positions) > 1:
            raise DataContractError("用于长度的上限字段最多只能有一个")
        if len({spec.rule_column for spec in self.limits}) != len(self.limits):
            raise DataContractError("尺码上限字段不能重复")
        self.length_position = length_positions[0] if length_positions else None
        self.length_rule_column = (
            self.limits[self.length_position].rule_column
            if self.length_position is not None
            else None
        )
        self.length_tolerance = self._read_tolerance(parameters)
        self.pools = self._build_pools(rules, include_disabled_rules)
        self.cache: dict[tuple[object, ...], MatchResult] = {}

    @staticmethod
    def _read_tolerance(parameters: pd.DataFrame) -> float:
        _require_columns(parameters, ["参数", "值"], "尺码匹配参数")
        normalized = parameters[["参数", "值"]].copy()
        normalized["参数"] = normalized["参数"].map(_clean_text)
        normalized["值"] = _numeric(normalized["值"])
        found = normalized.loc[normalized["参数"].eq("余量长容差"), "值"]
        if found.empty or pd.isna(found.iloc[0]):
            raise DataContractError("参数“余量长容差”不存在或不是数字")
        return float(found.iloc[0])

    def _build_pools(
        self, rules: pd.DataFrame, include_disabled_rules: bool
    ) -> dict[tuple[str, str | None, str | None], SizePool]:
        required = [
            "内部尺码",
            "档位序号",
            "分类",
            "CAB",
            "版本",
            *[spec.rule_column for spec in self.limits],
        ]
        _require_columns(rules, required, "尺码匹配规则")
        normalized = rules.copy()
        if not include_disabled_rules and "使用" in normalized.columns:
            normalized = normalized.loc[
                normalized["使用"].astype("string").str.strip().str.casefold().eq("y")
            ].copy()
        for column in ["内部尺码", "分类", "CAB", "版本"]:
            normalized[column] = normalized[column].map(_clean_text)
        for column in ["档位序号", *[spec.rule_column for spec in self.limits]]:
            normalized[column] = _numeric(normalized[column])
        normalized = normalized.loc[normalized["分类"].notna()].copy()

        pools: dict[tuple[str, str | None, str | None], SizePool] = {}
        for key, group in normalized.groupby(["分类", "CAB", "版本"], dropna=False, sort=True):
            category, cab, version = key
            pool_key = (
                str(category),
                None if pd.isna(cab) else str(cab),
                None if pd.isna(version) else str(version),
            )
            max_length: float | None = None
            if self.length_rule_column is not None:
                lengths = group[self.length_rule_column].dropna()
                if not lengths.empty:
                    max_length = float(lengths.max())
            complete = group["档位序号"].notna()
            for spec in self.limits:
                complete &= group[spec.rule_column].notna()
            candidates = (
                group.loc[complete]
                .sort_values("档位序号", kind="stable")
                .to_dict(orient="records")
            )
            pools[pool_key] = SizePool(candidates=candidates, max_length=max_length)
        return pools

    def _pool(self, category: str | None, cab: str | None, version: str | None) -> SizePool:
        if category is None:
            return SizePool([], None)
        return self.pools.get((category, cab, version), SizePool([], None))

    @staticmethod
    def _round_one(value: float) -> float:
        return float(np.round(value, 1))

    def _row_difference(
        self, rule: Mapping[str, object], values: Sequence[float]
    ) -> tuple[float, str | None]:
        exceeded: list[tuple[float, str]] = []
        for value, spec in zip(values, self.limits, strict=True):
            difference = float(value) - float(rule[spec.rule_column])
            if difference > 0:
                exceeded.append((difference, spec.reason))
        if exceeded:
            max_difference = max(item[0] for item in exceeded)
            reason = next(item[1] for item in exceeded if item[0] == max_difference)
            return self._round_one(max_difference), reason

        if self.length_position is not None and self.length_rule_column is not None:
            margin = float(rule[self.length_rule_column]) - float(values[self.length_position])
            if margin > self.length_tolerance:
                return self._round_one(margin), "超余量"
        return 0.0, None

    def _calculate_pool(self, pool: SizePool, values: Sequence[float | None]) -> MatchResult:
        if len(values) != len(self.limits) or any(value is None or pd.isna(value) for value in values):
            return MatchResult("数据不全")
        numeric_values = tuple(float(value) for value in values)
        base_candidate: dict[str, object] | None = None
        for rule in pool.candidates:
            if all(
                float(rule[spec.rule_column]) >= numeric_values[index]
                for index, spec in enumerate(self.limits)
            ):
                base_candidate = rule
                break

        nearest: tuple[dict[str, object], float, str | None] | None = None
        for rule in pool.candidates:
            difference, reason = self._row_difference(rule, numeric_values)
            if nearest is None or difference < nearest[1]:
                nearest = (rule, difference, reason)

        if base_candidate is not None:
            margin: float | None = None
            if self.length_position is not None and self.length_rule_column is not None:
                margin = float(base_candidate[self.length_rule_column]) - numeric_values[
                    self.length_position
                ]
            if margin is None or margin <= self.length_tolerance:
                return MatchResult(
                    auto_size=_clean_text(base_candidate.get("内部尺码")) or "",
                    length_margin=None if margin is None else self._round_one(margin),
                    has_final_candidate=True,
                )

        if nearest is not None:
            rule, difference, reason = nearest
            return MatchResult(
                auto_size="无可用尺码",
                candidate=_clean_text(rule.get("内部尺码")),
                reason=reason,
                difference=difference,
            )
        return MatchResult("无可用尺码")

    def _calculate_category(
        self,
        category: str | None,
        cab: str | None,
        version: str | None,
        values: Sequence[float | None],
    ) -> MatchResult:
        exact_result: MatchResult | None = None
        if category is not None and cab is not None and version is not None:
            exact_result = self._calculate_pool(self._pool(category, cab, version), values)
        if exact_result is not None and exact_result.has_final_candidate:
            return exact_result

        version_result: MatchResult | None = None
        if category is not None and version is not None:
            version_result = self._calculate_pool(self._pool(category, None, version), values)
        if version_result is not None and version_result.has_final_candidate:
            return version_result
        return self._calculate_pool(self._pool(category, None, None), values)

    def _max_category_length(
        self, category: str, cab: str | None, version: str | None
    ) -> float | None:
        candidates: list[float] = []
        if cab is not None and version is not None:
            value = self._pool(category, cab, version).max_length
            if value is not None:
                candidates.append(value)
        if version is not None:
            value = self._pool(category, None, version).max_length
            if value is not None:
                candidates.append(value)
        value = self._pool(category, None, None).max_length
        if value is not None:
            candidates.append(value)
        return max(candidates) if candidates else None

    def match(
        self,
        category: object,
        cab: object,
        version: object,
        values: Sequence[object],
    ) -> MatchResult:
        category_text = _clean_text(category)
        cab_text = _clean_text(cab)
        version_text = _clean_text(version)
        if version_text is not None and "DRW" in version_text.upper():
            version_text = "DRW"
        numeric_values = tuple(
            None if value is None or pd.isna(value) else float(value) for value in values
        )
        cache_key = (category_text, cab_text, version_text, *numeric_values)
        if cache_key in self.cache:
            return self.cache[cache_key]

        result = self._calculate_category(
            category_text, cab_text, version_text, numeric_values
        )
        length_value = (
            numeric_values[self.length_position] if self.length_position is not None else None
        )
        if category_text == "三厢车" and length_value is not None:
            max_length = self._max_category_length("三厢车", cab_text, version_text)
            if max_length is not None and max_length < length_value:
                result = self._calculate_category("跑车", cab_text, version_text, numeric_values)
        self.cache[cache_key] = result
        return result

    def apply(self, vehicles: pd.DataFrame) -> pd.DataFrame:
        source_columns = ["分类", "CAB", "版本", *[spec.source_column for spec in self.limits]]
        _require_columns(vehicles, source_columns, "车型计算结果")
        results: list[MatchResult] = []
        for row in vehicles[source_columns].itertuples(index=False, name=None):
            category, cab, version, *values = row
            results.append(self.match(category, cab, version, values))
        result_frame = pd.DataFrame(
            {
                "自动尺码": [result.auto_size for result in results],
                "自动长度余量": [result.length_margin for result in results],
                "候选": [result.candidate for result in results],
                "原因": [result.reason for result in results],
                "相差数值": [result.difference for result in results],
            },
            index=vehicles.index,
        )
        return pd.concat([vehicles, result_frame], axis=1)


def resolve_submodel_path(
    input_dir: Path, explicit_path: Path | None, no_submodel: bool
) -> Path | None:
    if no_submodel:
        return None
    if explicit_path is not None:
        if not explicit_path.is_file():
            raise FileNotFoundError(f"子车系维护表不存在：{explicit_path}")
        return explicit_path
    local_path = input_dir / "子车系维护表.csv"
    if local_path.is_file():
        return local_path
    repository_path = Path(__file__).resolve().parent.parent / "public" / "子车系维护表.csv"
    return repository_path if repository_path.is_file() else None


def calculate(
    input_dir: Path,
    submodel_path: Path | None = None,
    include_disabled_rules: bool = False,
    sort_output: bool = True,
    config_dir: Path | None = None,
    rules_path: Path | None = None,
    body_path: Path | None = None,
    trim_source: Path | None = None,
) -> pd.DataFrame:
    config_dir = config_dir or Path(__file__).resolve().parent / "rules"
    dimensions = _read_csv(resolve_data_file(input_dir, "dimensions"))
    bodies = _read_csv(body_path or resolve_data_file(input_dir, "bodies"))
    sales = _read_csv(resolve_data_file(input_dir, "sales"))
    references = _read_csv(input_dir / "参考尺寸计算.csv")
    parameters = _read_csv(config_dir / CONFIG_FILES["parameters"])
    rules = _read_csv(rules_path or config_dir / CONFIG_FILES["rules"])
    submodels = _read_csv(submodel_path) if submodel_path is not None else None

    result = build_vehicle_base(dimensions, submodels)
    if submodels is None and trim_source is not None:
        prior = _read_csv(trim_source)
        _require_columns(prior, ["DIMENSION-ID", "TRIM"], "TRIM 保留来源")
        if prior["DIMENSION-ID"].duplicated().any():
            raise DataContractError("TRIM 保留来源的 DIMENSION-ID 必须唯一")
        trims = prior.set_index("DIMENSION-ID")["TRIM"]
        missing = ~result["DIMENSION-ID"].isin(trims.index)
        if missing.any():
            raise DataContractError(f"TRIM 保留来源缺少 {int(missing.sum())} 个 DIMENSION-ID")
        result["TRIM"] = result["DIMENSION-ID"].map(trims)
    sales_total = aggregate_sales(sales)
    result = result.merge(sales_total, on="DIMENSION-ID", how="left", validate="one_to_one")
    result["销量合计"] = result["销量合计"].fillna(0)
    if np.allclose(result["销量合计"].dropna() % 1, 0):
        result["销量合计"] = result["销量合计"].round().astype("Int64")
    result = add_body_dimensions(result, bodies, references)
    result = add_equivalent_length(result, references)
    matcher = SizeMatcher(
        parameters,
        rules,
        include_disabled_rules=include_disabled_rules,
    )
    result = matcher.apply(result)

    if sort_output:
        result = result.sort_values(
            "DIMENSION-ID", ascending=True, na_position="last", kind="stable"
        ).reset_index(drop=True)
    result = result[DEFAULT_OUTPUT_COLUMNS].copy()
    result["自动长度余量"] = _compact_number_column(result["自动长度余量"])
    result["相差数值"] = _compact_number_column(result["相差数值"])
    return result


def validate_result(result: pd.DataFrame, expected_rows: int) -> dict[str, object]:
    if len(result) != expected_rows:
        raise DataContractError(f"输出行数 {len(result)} 与车型尺寸行数 {expected_rows} 不一致")
    if result["DIMENSION-ID"].duplicated().any():
        raise DataContractError("输出 DIMENSION-ID 不唯一")
    missing_sales = int(result["销量合计"].isna().sum())
    if missing_sales:
        raise DataContractError(f"输出仍有 {missing_sales} 行空销量")
    invalid_status = result["自动尺码"].isna() | result["自动尺码"].astype("string").str.strip().eq("")
    if invalid_status.any():
        raise DataContractError(f"输出仍有 {int(invalid_status.sum())} 行没有尺码状态")
    return {
        "rows": len(result),
        "unique_dimension_ids": int(result["DIMENSION-ID"].nunique()),
        "matched_sizes": int((~result["自动尺码"].isin(["数据不全", "无可用尺码"])).sum()),
        "unavailable_sizes": int(result["自动尺码"].eq("无可用尺码").sum()),
        "incomplete_rows": int(result["自动尺码"].eq("数据不全").sum()),
        "sales_total": int(pd.to_numeric(result["销量合计"], errors="coerce").sum()),
    }


def write_result(result: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
        na_rep="",
    )


def write_workbook_candidate(
    result: pd.DataFrame,
    template_path: Path,
    output_path: Path,
    sheet_name: str = "尺码匹配",
) -> None:
    """Build a publishable workbook candidate without modifying the source template."""
    try:
        from openpyxl import load_workbook
    except ImportError as error:  # pragma: no cover - dependency error is environment-specific
        raise DataContractError("生成 Excel 候选需要安装 openpyxl") from error
    if not template_path.is_file():
        raise FileNotFoundError(f"Excel 模板不存在：{template_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template_path, output_path)
    workbook = load_workbook(output_path)
    if sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        sheet.delete_rows(1, sheet.max_row)
    else:
        sheet = workbook.create_sheet(sheet_name)
    sheet.append(list(result.columns))
    for values in result.itertuples(index=False, name=None):
        sheet.append(
            [
                None
                if pd.isna(value)
                else value.item()
                if isinstance(value, np.generic)
                else value
                for value in values
            ]
        )
    sheet.freeze_panes = "A2"
    workbook.save(output_path)
    workbook.close()


def next_change_output_dir(changes_dir: Path, description: str = "size-calculation") -> Path:
    """Return a new, non-overwriting batch output directory."""
    batch_date = date.today().isoformat()
    safe_description = re.sub(r"[^A-Za-z0-9_-]+", "-", description).strip("-")
    safe_description = safe_description or "size-calculation"
    existing_numbers = []
    if changes_dir.is_dir():
        pattern = re.compile(rf"^{re.escape(batch_date)}_(\d{{2}})_")
        for candidate in changes_dir.iterdir():
            match = pattern.match(candidate.name)
            if candidate.is_dir() and match:
                existing_numbers.append(int(match.group(1)))
    next_number = max(existing_numbers, default=0) + 1
    return changes_dir / f"{batch_date}_{next_number:02d}_{safe_description}" / "output"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    workspace_dir = script_dir.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="兼容旧用法：数据源与规则均从同一目录读取；设置后覆盖 --source-dir/--config-dir",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=workspace_dir / "public",
        help="共享数据源目录（默认：仓库 public）",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=script_dir / "rules",
        help="尺码匹配规则目录（默认：脚本同级 rules）",
    )
    parser.add_argument(
        "--rules-file",
        type=Path,
        help="尺码匹配规则 CSV；默认使用 config-dir/尺码匹配规则.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="输出 CSV 路径；指定后不自动创建 changes 批次",
    )
    parser.add_argument(
        "--changes-dir",
        type=Path,
        default=script_dir / "changes",
        help="迭代批次根目录（默认：脚本同级 changes）",
    )
    parser.add_argument(
        "--change-description",
        default="size-calculation",
        help="自动创建的批次目录说明（默认：size-calculation）",
    )
    parser.add_argument(
        "--workbook-template",
        type=Path,
        default=workspace_dir / "source" / "车型数据尺码.xlsx",
        help="保留其他工作表的 Excel 模板（默认：source/车型数据尺码.xlsx）",
    )
    parser.add_argument(
        "--workbook-output",
        type=Path,
        help="可选的历史 Excel 候选路径；默认只生成 CSV 真源候选",
    )
    parser.add_argument(
        "--no-workbook-output",
        action="store_true",
        help="只生成 CSV，不生成 Excel 候选",
    )
    parser.add_argument(
        "--body-source", type=Path,
        help="可选车形核定候选，覆盖数据源目录中的车身分类表",
    )
    parser.add_argument(
        "--trim-source", type=Path,
        help="缺少子车系维护表时，按 DIMENSION-ID 保留该表的 TRIM；默认使用数据源目录的全量数据.csv",
    )
    parser.add_argument(
        "--submodel-source",
        type=Path,
        help="可选的子车系维护表；默认从数据源目录或仓库 source 读取",
    )
    parser.add_argument(
        "--no-submodel",
        action="store_true",
        help="不读取子车系维护表，TRIM 留空",
    )
    parser.add_argument(
        "--include-disabled-rules",
        action="store_true",
        help="也使用“使用”列不是 y 的规则",
    )
    parser.add_argument(
        "--keep-source-order",
        action="store_true",
        help="保留车型尺寸源顺序；默认按 DIMENSION-ID 升序",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    input_dir = (args.input_dir or args.source_dir).resolve()
    config_dir = (args.input_dir or args.config_dir).resolve()
    batch_output_dir = None
    if args.output:
        output_path = args.output.resolve()
    else:
        batch_output_dir = next_change_output_dir(
            args.changes_dir.resolve(), args.change_description
        )
        output_path = batch_output_dir / "pandas_output.csv"
    try:
        submodel_path = resolve_submodel_path(
            input_dir,
            args.submodel_source.resolve() if args.submodel_source else None,
            args.no_submodel,
        )
        trim_source = args.trim_source or (input_dir / "全量数据.csv")
        if args.no_submodel or submodel_path is not None:
            trim_source = None
        elif args.trim_source is None and not trim_source.is_file():
            trim_source = None
        result = calculate(
            input_dir,
            submodel_path=submodel_path,
            include_disabled_rules=args.include_disabled_rules,
            sort_output=not args.keep_source_order,
            config_dir=config_dir,
            rules_path=args.rules_file.resolve() if args.rules_file else None,
            body_path=args.body_source.resolve() if args.body_source else None,
            trim_source=trim_source,
        )
        expected_rows = len(_read_csv(resolve_data_file(input_dir, "dimensions")))
        summary = validate_result(result, expected_rows)
        write_result(result, output_path)
        if args.workbook_output and not args.no_workbook_output:
            write_workbook_candidate(
                result,
                args.workbook_template.resolve(),
                args.workbook_output.resolve(),
            )
    except (DataContractError, FileNotFoundError, pd.errors.ParserError) as error:
        print(f"计算失败：{error}", file=sys.stderr)
        return 2

    summary["output"] = str(output_path)
    summary["workbook_output"] = (
        str(args.workbook_output.resolve())
        if args.workbook_output and not args.no_workbook_output
        else None
    )
    summary["source_dir"] = str(input_dir)
    summary["config_dir"] = str(config_dir)
    summary["rules_file"] = str(args.rules_file.resolve()) if args.rules_file else str(config_dir / CONFIG_FILES["rules"])
    summary["submodel_source"] = str(submodel_path) if submodel_path else None
    summary["trim_source"] = str(trim_source) if trim_source else None
    summary["body_source"] = str(args.body_source.resolve()) if args.body_source else str(resolve_data_file(input_dir, "bodies"))
    if batch_output_dir is not None:
        status_path = batch_output_dir / "status.json"
        status_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        summary["status"] = str(status_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
