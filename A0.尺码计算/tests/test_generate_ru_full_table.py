from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
SPEC = importlib.util.spec_from_file_location("generate_ru_full_table", PROJECT / "src" / "generate_ru_full_table.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_ru_sales_are_aggregated_by_match_key_and_cover_published_dimensions():
    sales, audit = module.build_ru_sales_by_dimension()

    assert len(sales) == 13617
    assert sales["DIMENSION-ID"].is_unique
    assert sales["销量合计"].sum() == 297009
    assert audit["sales_source_total"] == 301065
    assert audit["unmatched_sales_total"] == 4056
    assert audit["sales_rows_without_match_key"] == 304
    assert audit["sales_source_positive_rows"] == 4272
    assert audit["dimension_rows_with_positive_proxy_sales"] == 4050


def test_ru_full_base_uses_only_ru_dimensions_and_sales():
    dimensions = module.analysis._read_csv(module.RU_DIMENSIONS_PATH)
    sales, _ = module.build_ru_sales_by_dimension()

    result = module.build_ru_full_base(dimensions, sales)

    assert len(result) == 13617
    assert result["DIMENSION-ID"].str.endswith(" RU").all()
    assert result["销量合计"].sum() == 297009


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


def test_ru_rule_ozon_mapping_matches_the_approved_size_labels():
    rules = module.read_rules(module.RULES_PATH)
    expected = {
        "2M": ("2L+", "L"), "2XL": ("2XL+", "XL"),
        "6L": ("3XL+0", "XL"), "A": ("PK-M", ""),
        "3XXL": ("3XXL", "XLL"), "S": ("YM+", "YM"),
        "XL": ("YXXL", "YXL"),
    }
    for ozon, (amazon, ship) in expected.items():
        row = rules.loc[rules["OZON尺码"].eq(ozon)].iloc[0]
        assert (row["亚马逊尺码"], row["发货尺码"]) == (amazon, ship)

    for ozon, amazon in {"5S": "2L-200", "5M": "2XL-200"}.items():
        row = rules.loc[rules["OZON尺码"].eq(ozon)].iloc[0]
        assert (row["亚马逊尺码"], row["发货尺码"]) == (amazon, "")

    blank_ozon = rules.loc[rules["OZON尺码"].eq("")]
    assert set(blank_ozon["亚马逊尺码"]) == {"2S-280", "2XXL-545", "YS-380", "YS-410"}
    assert blank_ozon["发货尺码"].eq("").all()
