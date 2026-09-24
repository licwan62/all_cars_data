from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import compress as compress_mod  # noqa: E402


def row(make="Ford", model="Focus", structure="Sedan", cab="", bed="", year="2018-2019", size="M", region="US"):
    return {
        "MAKE": make, "MODEL": model, "结构": structure, "CAB": cab, "BED": bed,
        "YEAR": year, "自动尺码": size, "DIMENSION-ID": f"{make} {model} {structure} {year} {region}",
    }


def test_merges_adjacent_years_with_same_size():
    rows = [row(year="2018-2019", size="M"), row(year="2020-2021", size="M")]
    compressed, meta = compress_mod.compress(rows)
    assert len(compressed) == 1
    assert compressed[0]["年份区间"] == "2018-2021"
    assert compressed[0]["自动尺码"] == "M"
    assert meta["report"]["冲突数"] == 0


def test_does_not_bridge_gap_years():
    rows = [row(year="2018-2019", size="M"), row(year="2021-2022", size="M")]
    compressed, _ = compress_mod.compress(rows)
    ranges = sorted(item["年份区间"] for item in compressed)
    assert ranges == ["2018-2019", "2021-2022"]


def test_pools_structures_sharing_same_size_same_year():
    rows = [row(structure="Sedan", year="2020-2020", size="M"), row(structure="Coupe", year="2020-2020", size="M")]
    compressed, _ = compress_mod.compress(rows)
    assert len(compressed) == 1
    assert compressed[0]["变体数"] == 2
    assert "Sedan" in compressed[0]["结构池"] and "Coupe" in compressed[0]["结构池"]


def test_splits_structures_with_different_sizes():
    rows = [row(structure="Sedan", year="2020-2020", size="M"), row(structure="Coupe", year="2020-2020", size="L")]
    compressed, _ = compress_mod.compress(rows)
    assert len(compressed) == 2
    assert {item["自动尺码"] for item in compressed} == {"M", "L"}


def test_conflicting_size_for_same_variant_year_is_majority_voted_and_reported():
    conflicting_rows = [row(year="2020-2020", size="M")] * 2 + [row(year="2020-2020", size="L")]
    compressed, meta = compress_mod.compress(conflicting_rows)
    assert len(compressed) == 1
    assert compressed[0]["自动尺码"] == "M"
    assert meta["report"]["冲突数"] == 1


def test_skips_rows_with_missing_size_or_bad_year():
    rows = [row(size=""), row(year="not-a-range")]
    compressed, meta = compress_mod.compress(rows)
    assert compressed == []
    assert meta["report"]["跳过行数"] == 2


def test_lossless_merges_variant_years_independently_of_sibling_structures():
    rows = [
        row(structure="Sedan", year="2017-2020", size="3L"),
        row(structure="Sedan", year="2021-2026", size="3L"),
        row(structure="Hatchback", year="2017-2020", size="2L"),
    ]
    compressed, _ = compress_mod.compress(rows)
    sedan = [item for item in compressed if item["结构池"] == "Sedan"]
    assert [item["年份区间"] for item in sedan] == ["2017-2026"]


def test_lossy_bridges_short_gap_and_pools_structures_with_unique_sizes():
    rows = [
        row(structure="Sedan", year="2010-2012", size="M"),
        row(structure="Sedan", year="2014-2016", size="M"),
        row(structure="Coupe", year="2013-2016", size="M"),
        row(structure="Wagon", year="2010-2016", size="L"),
    ]
    result = compress_mod.compress_all(rows, max_gap_years=3)
    assert result["check"]["无损"]["通过"] and result["check"]["有损"]["通过"]
    m_rows = [item for item in result["lossy"] if item["自动尺码"] == "M"]
    assert len(m_rows) == 1
    assert m_rows[0]["年份区间"] == "2010-2016"
    assert m_rows[0]["结构池"] == "Coupe; Sedan"
    assert m_rows[0]["扩张原子数"] == 4
    assert m_rows[0]["扩张原子"] == "coupe_10-12; sedan_13"


def test_lossy_lists_only_years_for_single_variant_expansion():
    rows = [
        row(structure="Sedan", year="2022-2023", size="M"),
        row(structure="Sedan", year="2026-2027", size="M"),
    ]
    result = compress_mod.compress_all(rows, max_gap_years=3)
    assert len(result["lossy"]) == 1
    assert result["lossy"][0]["扩张原子数"] == 2
    assert result["lossy"][0]["扩张原子"] == "24-25"


def test_lossy_never_covers_real_atom_with_other_size():
    rows = [
        row(structure="Sedan", year="2010-2011", size="M"),
        row(structure="Sedan", year="2012-2012", size="L"),
        row(structure="Sedan", year="2013-2014", size="M"),
    ]
    result = compress_mod.compress_all(rows, max_gap_years=3)
    assert result["check"]["有损"]["通过"]
    assert len(result["lossy"]) == 3


def test_lossy_respects_max_gap():
    rows = [row(year="2000-2001", size="M"), row(year="2010-2011", size="M")]
    result = compress_mod.compress_all(rows, max_gap_years=3)
    assert len(result["lossy"]) == 2


def test_region_of_extracts_known_suffix():
    assert compress_mod.region_of("Ford Focus Sedan 2018-2019 US") == "US"
    assert compress_mod.region_of("Ford Focus Sedan 2018-2019") == ""
