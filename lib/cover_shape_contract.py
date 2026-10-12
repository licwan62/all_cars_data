"""新 SHAPE 与旧车形系数独立；全量表只按精确地区 DIMENSION-ID 关联。"""
from __future__ import annotations

import pandas as pd

from id_scheme import append_country_code

SHAPE_FIELDS = ["SHAPE", "SHAPE_STATUS", "SHAPE_YEAR", "SHAPE_METHOD", "SHAPE_ALTERNATES", "SHAPE_SOURCE"]
FULL_TABLE_SHAPE_FIELDS = ["SHAPE"]
SHAPE_LABELS = {"LOW_FASTBACK", "LOW_NOTCHBACK", "SPORT_LIFTBACK", "STANDARD_SEDAN", "COMPACT_HATCH", "TALL_BOX",
                "WAGON", "SLOPED_CROSSOVER", "BOXY_SUV", "PICKUP", "OTHER", "UNKNOWN"}
SHAPE_STATUSES = {"VERIFIED", "PROBABLE", "INFERRED", "CONFLICT", "UNKNOWN"}


def attach_cover_shape(frame: pd.DataFrame, shapes: pd.DataFrame, country: str) -> pd.DataFrame:
    required = ["DIMENSION-ID", "COUNTRY", *SHAPE_FIELDS]
    missing = set(required) - set(shapes.columns)
    if missing:
        raise ValueError(f"COVER_SHAPE 缺少字段：{sorted(missing)}")
    if shapes["DIMENSION-ID"].duplicated().any():
        raise ValueError("COVER_SHAPE 的 DIMENSION-ID 不唯一")
    if frame["DIMENSION-ID"].duplicated().any():
        raise ValueError("全量表的 DIMENSION-ID 不唯一")
    if not shapes["SHAPE"].isin(SHAPE_LABELS).all() or not shapes["SHAPE_STATUS"].isin(SHAPE_STATUSES).all():
        raise ValueError("SHAPE 标签或状态非法")
    regional = shapes.loc[shapes["COUNTRY"].eq(country), required].copy()
    for value in regional["DIMENSION-ID"]:
        if not str(value).endswith(" " + country):
            raise ValueError("COVER_SHAPE 地区与 ID 后缀不一致")
    original = frame.drop(columns=[k for k in SHAPE_FIELDS if k in frame.columns]).copy()
    keys = original["DIMENSION-ID"].map(lambda value: append_country_code(str(value), country))
    lookup = regional.set_index("DIMENSION-ID")
    absent = sorted(set(keys) - set(lookup.index))
    if absent:
        raise ValueError(f"{country} 全量记录缺少 SHAPE：{len(absent)} 条，例如 {absent[:3]}")
    for field in FULL_TABLE_SHAPE_FIELDS:
        original[field] = keys.map(lookup[field])
        if original[field].isna().any() or original[field].astype(str).eq("").any():
            raise ValueError(f"{country} 全量表 {field} 存在空值")
    year = pd.to_numeric(keys.map(lookup["SHAPE_YEAR"]), errors="coerce")
    if year.isna().any() or not year.between(1886, 2100).all() or not year.eq(year.round()).all():
        raise ValueError("SHAPE_YEAR 无效")
    # DIMENSION-ID 首列、TRIM/相差数值末列保持原契约；新字段紧跟旧车形。
    columns = [c for c in original.columns if c not in SHAPE_FIELDS]
    position = columns.index("车形") + 1 if "车形" in columns else len(columns)
    ordered = columns[:position] + FULL_TABLE_SHAPE_FIELDS + columns[position:]
    return original[ordered]
