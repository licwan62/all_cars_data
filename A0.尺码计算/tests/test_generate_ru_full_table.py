from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
SPEC = importlib.util.spec_from_file_location("generate_ru_full_table", PROJECT / "generate_ru_full_table.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_ru_sales_are_aggregated_by_match_key_and_cover_published_dimensions():
    sales, audit = module.build_ru_sales_by_dimension()

    assert len(sales) == 13848
    assert sales["DIMENSION-ID"].is_unique
    assert sales["销量合计"].sum() == 296972
    assert audit["sales_source_total"] == 301065
    assert audit["unmatched_sales_total"] == 4093
    assert audit["sales_rows_without_match_key"] == 304
    assert audit["sales_source_positive_rows"] == 4272
    assert audit["dimension_rows_with_positive_proxy_sales"] == 4175


def test_ru_full_base_uses_only_ru_dimensions_and_sales():
    dimensions = module.analysis._read_csv(module.RU_DIMENSIONS_PATH)
    sales, _ = module.build_ru_sales_by_dimension()

    result = module.build_ru_full_base(dimensions, sales)

    assert len(result) == 13848
    assert result["DIMENSION-ID"].str.endswith(" RU").all()
    assert result["销量合计"].sum() == 296972


def test_ru_matching_uses_per_size_length_margin():
    rules = pd.DataFrame(
        [
            {"亚马逊尺码": "紧身", "OZON尺码": "", "发货尺码": "", "分类": "两厢车", "长_mm": 3000, "宽_mm": 1800, "高_mm": 1800, "余量长上限_mm": 100},
            {"亚马逊尺码": "宽松", "OZON尺码": "", "发货尺码": "", "分类": "两厢车", "长_mm": 3300, "宽_mm": 1800, "高_mm": 1800, "余量长上限_mm": 635},
        ]
    )
    vehicles = pd.DataFrame([{"分类": "两厢车", "L-MM": 2800, "W-MM": 1600, "H-MM": 1600}])

    matched = module.match_ru_sizes(vehicles, rules, {"余量长容差": 635})

    assert matched.loc[0, "自动尺码"] == "宽松"


def test_ru_matching_prefers_smaller_cover_volume_over_shorter_length():
    rules = pd.DataFrame(
        [
            {"亚马逊尺码": "2L-200", "OZON尺码": "", "发货尺码": "", "分类": "两厢车", "长_mm": 4250, "宽_mm": 2100, "高_mm": 2000, "余量长上限_mm": 635},
            {"亚马逊尺码": "2L", "OZON尺码": "", "发货尺码": "", "分类": "两厢车", "长_mm": 4520, "宽_mm": 2100, "高_mm": 1780, "余量长上限_mm": 635},
        ]
    )
    vehicles = pd.DataFrame([{"分类": "两厢车", "L-MM": 4249, "W-MM": 1699, "H-MM": 1501}])

    matched = module.match_ru_sizes(vehicles, rules, {"余量长容差": 635})

    assert matched.loc[0, "自动尺码"] == "2L"
