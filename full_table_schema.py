from __future__ import annotations

import pandas as pd


SIZE_MATCH_COLUMNS = ["自动尺码", "自动长度余量", "候选", "原因", "相差数值"]


def build_dimension_analysis(full_table: pd.DataFrame) -> pd.DataFrame:
    """Return the pre-size-matching view of a regional full table."""
    present = [column for column in SIZE_MATCH_COLUMNS if column in full_table.columns]
    if present and len(present) != len(SIZE_MATCH_COLUMNS):
        missing = [column for column in SIZE_MATCH_COLUMNS if column not in full_table.columns]
        raise ValueError(f"尺码结果字段不完整：{', '.join(missing)}")
    analysis = full_table.drop(columns=present).copy()
    if "DIMENSION-ID" not in analysis.columns:
        raise ValueError("尺寸分析表缺少 DIMENSION-ID")
    columns = [column for column in analysis.columns if column != "DIMENSION-ID"] + ["DIMENSION-ID"]
    return analysis[columns]
