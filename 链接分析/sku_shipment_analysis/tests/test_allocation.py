import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import allocate, fixed_consumer_name, merge_test_year, proportional_integer_allocation, sku_name, year_code
from build_merged_clusters import sibling_size_merge_targets


def test_proportional_integer_allocation_reconciles():
    result = proportional_integer_allocation(pd.Series([1, 2, 3], index=["A", "B", "C"]), 11)
    assert result.sum() == 11
    assert result.to_dict() == {"A": 2, "B": 4, "C": 5}


def test_cluster_allocation_uses_pack_multiple():
    summary = pd.DataFrame(
        {
            "PHYSICAL_SIZE": ["S", "S"],
            "CLUSTER_ID": ["A", "B"],
            "CONSUMER_NAME": ["A", "B"],
            "CLUSTER_SALES": [70, 30],
        }
    )
    shipment = pd.DataFrame({"PHYSICAL_SIZE": ["S"], "发货量": [10]})
    result = allocate(summary, shipment, 3)
    assert result["行发货量"].sum() == 9
    assert set(result["行发货量"]) == {3, 6}


def test_year_code_uses_two_digit_ranges():
    assert year_code("1973-1998") == "Y73-98"
    assert year_code("1964-1966/1970-1973") == "Y64-66+70-73"


def test_non_pickup_sku_omits_cab_bed_and_cluster_id():
    config = {
        "make_abbreviations": {"Chevrolet": "CHEV"},
        "model_abbreviations": {"Nova": "NOVA"},
        "cab_abbreviations": {"REGULAR": "REG"},
        "year_prefix": "Y", "bed_prefix": "B", "bed_decimal_multiplier": 10,
        "non_pickup_include_cab": False, "non_pickup_include_bed": False,
    }
    row = pd.Series({
        "MAKE": "Chevrolet", "MODEL": "Nova", "分类": "跑车", "CAB_GROUP": "REGULAR",
        "CONSUMER_NAME": "Chevrolet Nova 1962-1972 6.5'", "FITMENT_YEAR": "1962-1972",
        "PHYSICAL_SIZE": "3L-W", "CLUSTER_ID": "CAR-123",
    })
    assert sku_name(row, config) == "CHEV_NOVA_Y62-72_3L-W"


def test_pickup_sku_includes_cab_and_bed():
    config = {
        "make_abbreviations": {"Chevrolet": "CHEV"},
        "model_abbreviations": {"C/K": "CK"},
        "cab_abbreviations": {"REGULAR": "REG"}, "axle_abbreviations": {"DRW": "DRW"},
        "year_prefix": "Y", "bed_prefix": "B", "bed_decimal_multiplier": 10,
    }
    row = pd.Series({
        "MAKE": "Chevrolet", "MODEL": "C/K", "分类": "皮卡", "CAB_GROUP": "REGULAR",
        "AXLE_TYPE": "SRW", "CONSUMER_NAME": "Chevrolet C/K Regular 6.5' Standard Bed",
        "FITMENT_YEAR": "1973-1998", "PHYSICAL_SIZE": "PK-M",
    })
    assert sku_name(row, config) == "CHEV_CK_REG_B65_Y73-98_PK-M"


def test_pickup_consumer_name_preserves_source_cab_and_bed_labels():
    config = {"consumer_name_separator": " | ", "cab_display": {"EXTENDED": "Extended"}}
    row = pd.Series({
        "MAKE_MODEL": "Ford F-150", "CONSUMER_YEAR": "1994-1995", "分类": "皮卡",
        "CAB_GROUP": "EXTENDED",
        "CONSUMER_NAME": "Ford F-150 1994-1995 | SuperCab | 6.5' Standard Bed",
    })
    assert fixed_consumer_name(row, config) == "Ford F-150 1994-1995 | SuperCab | 6.5' Standard Bed"


def test_sedan_coupe_consumer_name_omits_structure():
    config = {
        "consumer_name_separator": " | ",
        "structure_order": ["Convertible", "Coupe", "Fastback", "Hardtop", "Sedan"],
        "structure_display": {},
    }
    row = pd.Series({
        "MAKE_MODEL": "Chevrolet Nova", "FITMENT_YEAR": "1962-1972",
        "分类": "三厢车 / 跑车", "结构": "Sedan / Coupe",
    })
    assert fixed_consumer_name(row, config) == "Chevrolet Nova 1962-1972"


def test_non_pickup_structure_whitelist_controls_consumer_name():
    config = {
        "consumer_name_separator": " | ",
        "structure_order": ["Coupe", "Sedan"],
        "structure_display": {},
        "non_pickup_structure_whitelist": [
            {"make": "Example", "model": "Model", "structures": ["Coupe"]}
        ],
    }
    row = pd.Series({
        "MAKE": "Example", "MODEL": "Model", "MAKE_MODEL": "Example Model", "FITMENT_YEAR": "2000-2001",
        "分类": "SUV", "结构": "Sedan / Coupe",
    })
    assert fixed_consumer_name(row, config) == "Example Model 2000-2001 | Coupe"


def test_year_merge_accepts_safe_expansion():
    row = pd.Series({
        "MAKE": "Chevrolet", "MODEL": "Malibu", "FITMENT_YEAR": "1964-1974/1978-1983",
        "PHYSICAL_SIZE": "3XL-W",
    })
    result = merge_test_year(row, {})
    assert result["CONSUMER_YEAR"] == "1964-1983"
    assert result["YEAR_MERGE_STATUS"] == "MERGED_SAFE"
    assert result["NEW_YEAR_COUNT"] == 3


def test_year_merge_rejects_other_physical_size():
    row = pd.Series({
        "MAKE": "Chevrolet", "MODEL": "Malibu", "FITMENT_YEAR": "1964-1974/1978-1983",
        "PHYSICAL_SIZE": "3XL-W",
    })
    ownership = {("Chevrolet", "Malibu", 1976): {("3XXL-W", "CAR-OTHER"): 5300.0}}
    result = merge_test_year(row, ownership, {"3XL-W": 5050.0}, 50)
    assert result["CONSUMER_YEAR"] == "1964-1975/1977-1983"
    assert result["YEAR_MERGE_STATUS"] == "MERGED_SAFE_PARTIAL"
    assert "1976=3XXL-W:CAR-OTHER" in result["YEAR_CONFLICT_DETAIL"]


def test_year_conflict_detail_compacts_consecutive_years():
    row = pd.Series({
        "MAKE": "Example", "MODEL": "Model", "FITMENT_YEAR": "1964/1967",
        "PHYSICAL_SIZE": "3XL-W",
    })
    ownership = {
        ("Example", "Model", 1965): {("3XXL-W", "CAR-OTHER"): 5200.0},
        ("Example", "Model", 1966): {("3XXL-W", "CAR-OTHER"): 5220.0},
    }
    result = merge_test_year(row, ownership, {"3XL-W": 5050.0}, 50)
    assert result["YEAR_CONFLICT_DETAIL"] == "1965-1966=3XXL-W:CAR-OTHER,车长=5200-5220mm,最大超出=170mm"


def test_year_merge_does_not_overlap_an_existing_sibling_source():
    row = pd.Series({
        "MAKE": "Pontiac", "MODEL": "Bonneville", "FITMENT_YEAR": "1959-1969/1971-1976",
        "PHYSICAL_SIZE": "3XXXL",
    })
    ownership = {("Pontiac", "Bonneville", 1970): {("3XXXXL", "CAR-LARGE"): 5705.0}}
    result = merge_test_year(row, ownership, {"3XXXL": 5700.0}, 50)
    assert result["CONSUMER_YEAR"] == "1959-1969/1971-1976"
    assert result["YEAR_MERGE_STATUS"] == "REJECTED_SOURCE_OCCUPIED"
    assert result["FINAL_SIZE"] == "3XXXL"
    assert result["MAX_LENGTH_OVERFLOW"] == 5.0


def test_overlapping_sibling_clusters_merge_into_smallest_compatible_size():
    summary = pd.DataFrame({
        "CLUSTER_ID": ["CAR-SMALL", "CAR-LARGE", "CAR-OTHER"],
        "逻辑尺码": ["3L-W", "3XL-W", "3XXL-W"],
        "MAKE": ["Oldsmobile"] * 3,
        "MODEL": ["Cutlass"] * 3,
        "YEAR_COMPACT": ["1961-1963", "1962-1963/1978", "1964-1977/1979"],
    })
    detail = pd.DataFrame({
        "CLUSTER_ID": ["CAR-SMALL", "CAR-LARGE", "CAR-OTHER"],
        "L-MM": [4780, 5022, 5479],
    })

    targets = sibling_size_merge_targets(
        summary, detail, {"3L-W": 4850, "3XL-W": 5050, "3XXL-W": 5500}, 50
    )

    assert targets == {"CAR-SMALL": "3XL-W", "CAR-LARGE": "3XL-W"}
