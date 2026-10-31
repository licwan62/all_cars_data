import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from business_release import match_sku_renames


LISTING = [
    {"CLUSTER_ID": "C1", "SKU_NAME": "OLDS_88_Y49-99_4L", "链接名称": "Oldsmobile 88 1949-1999",
     "适配车型": "Oldsmobile 88", "适配年份": "1949-1958/1961-1964/1992-1999", "尺码": "4L"},
    {"CLUSTER_ID": "C2", "SKU_NAME": "OLDS_88_Y86-91_4M", "链接名称": "Oldsmobile 88 1986-1991",
     "适配车型": "Oldsmobile 88", "适配年份": "1986-1991", "尺码": "4M"},
]


def rename(years, size, sku):
    return {"车型": "Oldsmobile 88", "年份": years, "尺寸": size, "SKU输出": sku}


def test_business_sku_matches_fitment_years_or_link_span():
    matched = match_sku_renames(LISTING, [
        rename("1949-1958/1961-1964/1992-1999", "4L-0", "SKU-A"),
        rename("1986-1991", "4M-0", "SKU-B"),
    ])
    assert {cluster: row["SKU输出"] for cluster, row in matched.items()} == {"C1": "SKU-A", "C2": "SKU-B"}

    by_span = match_sku_renames(LISTING, [rename("1949-1999", "4L-0", "SKU-A"), rename("1986-1991", "4M-0", "SKU-B")])
    assert by_span["C1"]["SKU输出"] == "SKU-A"


def test_business_sku_must_cover_every_listing_with_matching_size():
    with pytest.raises(ValueError, match="缺少链接"):
        match_sku_renames(LISTING, [rename("1986-1991", "4M-0", "SKU-B")])
    with pytest.raises(ValueError, match="尺寸"):
        match_sku_renames(LISTING, [rename("1949-1999", "4XL-0", "SKU-A"), rename("1986-1991", "4M-0", "SKU-B")])
    with pytest.raises(ValueError, match="匹配到 0 条"):
        match_sku_renames(LISTING, [rename("1950-1999", "4L-0", "SKU-A")])
