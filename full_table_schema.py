from __future__ import annotations

from pathlib import Path

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


ROOT = Path(__file__).resolve().parent
DIMENSION_CODE_MAP = ROOT / "02.代码映射" / "output" / "尺寸编码映射.csv"


def attach_dimension_code(frame: pd.DataFrame, code_map_path: Path | None = None) -> pd.DataFrame:
    """按 DIMENSION-ID 关联上游代码映射的 DIMENSION-CODE，并放在 DIMENSION-ID 之前。

    frame 的 DIMENSION-ID 必须已带区域后缀（" US"/" EU"/" RU"），与代码映射一致；
    任何 ID 在映射中缺失都视为上游未跟上，直接报错而不是写空值。
    """
    path = code_map_path or DIMENSION_CODE_MAP
    mapping = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    if mapping["DIMENSION-ID"].duplicated().any():
        raise ValueError(f"{path} 的 DIMENSION-ID 不唯一")
    codes = frame["DIMENSION-ID"].map(mapping.set_index("DIMENSION-ID")["DIMENSION-CODE"])
    missing = frame.loc[codes.isna(), "DIMENSION-ID"]
    if len(missing):
        raise ValueError(f"{len(missing)} 个 DIMENSION-ID 缺少 DIMENSION-CODE，例如：{missing.head(3).tolist()}")
    result = frame.drop(columns=["DIMENSION-CODE"], errors="ignore").copy()
    result.insert(result.columns.get_loc("DIMENSION-ID"), "DIMENSION-CODE", codes.to_numpy())
    return result
