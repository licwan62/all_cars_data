import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from atom_verifier import (build_atom_map, build_verified_candidates,
                           expand_original_atoms, verify_candidate)


def rows(sku, cid, facts):
    frame = pd.DataFrame([{**{
        "MAKE_NORMALIZED": "Ford", "MODEL_FAMILY": "F-150", "版本": "",
        "L-MM": 5500, "W-MM": 2000, "H-MM": 1900, "自动长度余量": 100,
        "预估销量 的总和": 1, "自动尺码": sku,
    }, **fact} for fact in facts])
    frame["CAB_GROUP"] = frame["CAB"].map({"Crew": "CREW", "Regular": "REGULAR"}).fillna("OTHER")
    frame["BED_GROUP"] = pd.to_numeric(frame["BED"]).map(lambda x: "SHORT" if x < 6 else "STANDARD" if x < 7 else "LONG")
    return {"CLUSTER_ID": cid, "自动尺码": sku, "rows": frame,
            "TRUCK_TYPE": "FULLSIZE", "CAB_GROUP": "CREW", "BED_GROUP": "SHORT",
            "AXLE_TYPE": "SRW", "safety_pass": True}


def test_original_atom_map_expands_entire_year_range():
    cluster = rows("A", "A1", [{"YEAR_START": 2020, "YEAR_END": 2022, "CAB": "Crew", "BED": "5.5"}])
    assert len(expand_original_atoms(cluster["rows"])) == 3
    assert len(build_atom_map([cluster])) == 3


def test_safe_cartesian_expansion_is_explicitly_inferred_and_accepted():
    cluster = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Crew", "BED": "5.5"},
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Crew", "BED": "6.5"},
    ])
    diag = verify_candidate(cluster["rows"], "A", build_atom_map([cluster]), "A1")
    assert diag["MERGE_STATUS"] == "ACCEPT"
    assert diag["NEW_ATOM_COUNT"] == 2
    assert diag["INFERRED_NEW_ATOM_COUNT"] == 2
    assert diag["INFERRED_CLUSTER_ID"] == "A1"


def test_cross_sku_candidate_is_rejected_and_split_before_output():
    a = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Crew", "BED": "5.5"},
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Crew", "BED": "6.5"},
    ])
    b = rows("B", "B1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Crew", "BED": "6.5"},
    ])
    final, audit = build_verified_candidates([a, b])
    final_a = [c for c in final if c["自动尺码"] == "A"]
    assert len(final_a) == 2
    assert all(c["MERGE_STATUS"] != "REJECT" for c in final)
    assert any(x["MERGE_STATUS"] == "REJECT" for x in audit)
    assert all(c["_diagnostics"]["PHYSICAL_SKU_CONFLICT_ATOM_COUNT"] == 0 for c in final)


def test_unsupported_cab_bed_cartesian_combinations_are_rejected():
    cluster = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Regular", "BED": "8.0"},
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Crew", "BED": "5.5"},
    ])
    diag = verify_candidate(cluster["rows"], "A", build_atom_map([cluster]), "A1")
    assert diag["MERGE_STATUS"] == "REJECT"
    assert diag["UNRESOLVED_NEW_ATOM_COUNT"] == 4
    final, _ = build_verified_candidates([cluster])
    assert len(final) == 2
    assert all(c["MERGE_STATUS"] == "ACCEPT" for c in final)


def test_mixed_cab_and_bed_metadata_is_not_copied_from_first_row():
    cluster = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Regular", "BED": "8.0"},
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Regular", "BED": "6.5"},
    ])
    final, _ = build_verified_candidates([cluster])
    # Same CAB can merge because both structural combinations exist; BED group is mixed.
    assert len(final) == 1
    assert final[0]["CAB_GROUP"] == "REGULAR"
    assert final[0]["BED_GROUP"] == "MIXED"


def test_missing_year_is_safe_when_structure_has_historical_other_sku():
    target = rows("A", "A1", [
        {"YEAR_START": 2012, "YEAR_END": 2012, "CAB": "Regular", "BED": "6.5"},
        {"YEAR_START": 2014, "YEAR_END": 2014, "CAB": "Regular", "BED": "6.5"},
    ])
    historical = rows("B", "B1", [
        {"YEAR_START": 1994, "YEAR_END": 1995, "CAB": "Regular", "BED": "6.5"},
    ])
    atom_map = build_atom_map([target, historical])
    diag = verify_candidate(target["rows"], "A", atom_map, "A1", year_ranges=[(2012, 2014)])
    assert diag["MERGE_STATUS"] == "ACCEPT"
    assert diag["INFERRED_NEW_ATOM_COUNT"] == 1
    assert diag["PHYSICAL_SKU_CONFLICT_ATOM_COUNT"] == 0
