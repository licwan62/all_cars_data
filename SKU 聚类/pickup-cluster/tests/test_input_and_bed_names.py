import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from consumer_name import (assign_required_exclusions, format_bed_segment,
                           format_cab_segment, _get_variant_labels)
from load_data import load_fitment_with_atom_sales
from year_gap_filler import optimize_consumer_name


def test_bed_group_only_when_entire_range_fits_one_group():
    mixed = pd.DataFrame({"BED_LENGTH": [5.5, 8.0]})
    assert format_bed_segment(mixed, include_group=False) == "5.5'-8.0' Bed"
    assert format_bed_segment(mixed, include_group=True) == "5.5'-8.0' Bed"
    assert format_bed_segment(pd.DataFrame({"BED_LENGTH": [5.0, 5.8]}), True) == "5.0'-5.8' Short Bed"
    assert format_bed_segment(pd.DataFrame({"BED_LENGTH": [6.0, 6.8]}), True) == "6.0'-6.8' Standard Bed"
    assert format_bed_segment(pd.DataFrame({"BED_LENGTH": [7.0, 8.0]}), True) == "7.0'-8.0' Long Bed"


def test_atom_sales_are_aggregated_to_dimension_id(tmp_path, monkeypatch):
    fitment = pd.DataFrame({"DIMENSION-ID": ["D1", "D2"], "分类": ["皮卡", "皮卡"]})
    monkeypatch.setattr(pd, "read_excel", lambda *args, **kwargs: fitment.copy())
    sales_path = tmp_path / "atom_sales.csv"
    pd.DataFrame({
        "atom_record_id": ["D1|ATOM_YEAR=2020", "D1|ATOM_YEAR=2021", "D2|ATOM_YEAR=2020"],
        "预估销量": [10, 20, 5],
    }).to_csv(sales_path, index=False, encoding="gb18030")
    result = load_fitment_with_atom_sales("unused.xlsx", str(sales_path))
    assert result["预估销量 的总和"].tolist() == [30, 5]


def test_optimized_name_is_always_generated_for_mixed_bed_range():
    frame = pd.DataFrame({
        "MAKE_NORMALIZED": ["Ford", "Ford"], "MODEL_FAMILY": ["F-150", "F-150"],
        "版本": ["", ""], "CAB": ["Regular", "Regular"],
        "BED_LENGTH": [5.5, 8.0], "YEAR_START": [2020, 2020], "YEAR_END": [2020, 2020],
    })
    cluster = {"rows": frame, "BED_GROUP": "MIXED"}
    name = optimize_consumer_name(cluster, frame, try_gap_fill=False)
    assert name == "Ford F-150 2020 | Regular | 5.5'-8.0' Bed"


def test_optimized_cab_collapses_approved_club_quad_synonyms():
    frame = pd.DataFrame({"CAB": ["Club/Quad", "Quad"]})
    assert format_cab_segment(frame, optimize=True) == "Club/Quad"


def _semantic_cluster(make, model, version, sku, cab, bed, start, end):
    return {"自动尺码": sku, "rows": pd.DataFrame({
        "MAKE_NORMALIZED": [make], "MODEL_FAMILY": [model], "版本": [version],
        "CAB": [cab], "BED": [bed], "YEAR_START": [start], "YEAR_END": [end],
    })}


def test_cross_sku_special_versions_and_classic_require_excludes():
    f150 = _semantic_cluster("Ford", "F-150", "", "PK-L", "SuperCrew", 5.5, 2001, 2026)
    raptor = _semantic_cluster("Ford", "F-150", "Raptor", "PK-XL", "SuperCrew", 5.5, 2021, 2026)
    silverado = _semantic_cluster("Chevrolet", "Silverado 1500", "", "PK-L", "Crew", 5.8, 2004, 2026)
    trail_boss = _semantic_cluster("Chevrolet", "Silverado 1500", "Trail Boss", "PK-XL", "Crew", 5.8, 2021, 2026)
    ram = _semantic_cluster("Ram", "1500", "", "PK-XL", "Crew", 5.6, 2019, 2026)
    classic = _semantic_cluster("Ram", "1500 Classic", "", "PK-L", "Crew", 5.6, 2019, 2023)
    clusters = [f150, raptor, silverado, trail_boss, ram, classic]
    assign_required_exclusions(clusters)
    assert f150["_required_exclusions"] == ["2021-2026 Raptor"]
    assert silverado["_required_exclusions"] == ["2021-2026 Trail Boss"]
    assert ram["_required_exclusions"] == ["2019-2023 Classic"]


def test_tremor_is_treated_as_regular_version_for_display():
    assert _get_variant_labels(pd.Series({"版本": "Tremor"})) == set()
