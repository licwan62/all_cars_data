from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from src import ambiguity  # noqa: E402
from tests.test_compress import FIELDS, profile, row  # noqa: E402


def frame(rows: list[dict]) -> pd.DataFrame:
    table = pd.DataFrame(rows, columns=[*FIELDS, "代际"]).fillna("").astype(str)
    return table


def jaguar_rows() -> list[dict]:
    """同车型、同结构、无版本：两代年份重叠且尺码不同（Jaguar XJ Sedan 1979-1992 / 1988-1994 的形态）。"""
    return [
        {**row(make="Jaguar", model="XJ", year="1979-1992", size="3XXL-520", sales=140, length=5067), "代际": "gen1"},
        {**row(make="Jaguar", model="XJ", year="1988-1994", size="4M-0", sales=70, length=4989), "代际": "gen2"},
    ]


def test_year_ranges_collapse_consecutive_years():
    assert ambiguity.year_ranges([1990, 1988, 1989, 1995]) == "1988-1990/1995"


def test_overlapping_identities_with_different_sizes_are_source_ambiguity():
    table = frame(jaguar_rows())
    detail = ambiguity.ambiguous_keys(ambiguity.source_atom_rows(table, profile()))
    assert sorted(set(detail["YEAR"].astype(int))) == list(range(1988, 1993))
    summary = ambiguity.summarize_source_ambiguity(table, detail)
    assert len(summary) == 1
    group = summary.iloc[0]
    assert group["重叠年份"] == "1988-1992"
    assert group["原子数"] == 5
    assert group["尺码"] == "3XXL-520 | 4M-0"
    assert "代际" in group["区分字段"] and "L-MM" in group["区分字段"]
    # 重叠 5 年：gen1 每年 140/14=10，gen2 每年 70/7=10，不重复计
    assert group["涉及销量"] == 100.0


def test_same_size_overlap_is_not_ambiguous():
    rows = jaguar_rows()
    rows[1]["自动尺码"] = "3XXL-520"
    detail = ambiguity.ambiguous_keys(ambiguity.source_atom_rows(frame(rows), profile()))
    assert detail.empty
    assert ambiguity.summarize_source_ambiguity(frame(rows), detail).empty


def test_multi_is_classified_by_source_or_compression():
    table = frame(jaguar_rows())
    detail = ambiguity.ambiguous_keys(ambiguity.source_atom_rows(table, profile()))
    issues = pd.DataFrame([
        {"压缩类型": "非皮卡", "MAKE": "Jaguar", "MODEL": "XJ", "YEAR": "1990", "VERSION": "", "CONST": "Sedan",
         "CAB": "", "BED_FT": "", "BACKSIZE": "4M-0", "检查结果": "MULTI"},
        {"压缩类型": "非皮卡", "MAKE": "Jaguar", "MODEL": "XJ", "YEAR": "1993", "VERSION": "", "CONST": "Sedan",
         "CAB": "", "BED_FT": "", "BACKSIZE": "4M-0", "检查结果": "MULTI"},
    ])
    classified = ambiguity.classify_multi(issues, detail)
    assert classified["歧义来源"].tolist() == [ambiguity.SOURCE, ambiguity.INTRODUCED]
