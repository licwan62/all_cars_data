import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from atom_verifier import (build_atom_map, build_verified_candidates,
                           expand_original_atoms, verify_candidate,
                           verify_unique_real_atom_ownership,
                           verify_unique_real_atom_title_coverage)
from export import export_fallback_conflicts


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


def test_fallback_conflict_export_traces_every_real_owner_record(tmp_path):
    target = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Crew", "BED": "5.5"},
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Crew", "BED": "6.5"},
    ])
    owner = rows("B", "B1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Crew", "BED": "6.5"},
    ])
    owner["rows"]["DIMENSION-ID"] = "B-DIMENSION"
    diag = verify_candidate(
        target["rows"], "A", build_atom_map([target, owner]), "A1"
    )
    assert diag["CONFLICT_ATOMS"] == "Ford|F-150||2020|Crew|6.5"
    target["_optimization_attempt"] = {
        "name": "attempted", "year_ranges": "2020-2021", "gap_years": "",
        "diagnostics": diag,
    }
    target["_fallback"] = {
        "name": "fallback", "year_ranges": "2020/2021",
        "diagnostics": {"MERGE_STATUS": "ACCEPT"},
    }

    path = export_fallback_conflicts([target, owner], str(tmp_path))
    exported = pd.read_csv(path)
    assert len(exported) == 1
    assert exported.loc[0, "EXISTING_PHYSICAL_SKU"] == "B"
    assert exported.loc[0, "EXISTING_CLUSTER_ID"] == "B1"
    assert exported.loc[0, "SOURCE_DIMENSION_ID"] == "B-DIMENSION"


def test_nonexistent_cab_bed_cartesian_combinations_are_allowed():
    cluster = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Regular", "BED": "8.0"},
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Crew", "BED": "5.5"},
    ])
    diag = verify_candidate(cluster["rows"], "A", build_atom_map([cluster]), "A1")
    assert diag["MERGE_STATUS"] == "ACCEPT"
    assert diag["UNRESOLVED_NEW_ATOM_COUNT"] == 0
    assert diag["INFERRED_NEW_ATOM_COUNT"] == 6
    final, _ = build_verified_candidates([cluster])
    assert len(final) == 1
    assert all(c["MERGE_STATUS"] == "ACCEPT" for c in final)


def test_ram_style_variants_merge_when_only_generated_bed_combinations_are_missing():
    cluster = rows("PK-XL", "RAM", [
        {"YEAR_START": 2019, "YEAR_END": 2026, "CAB": "Crew", "BED": "5.6", "版本": ""},
        {"YEAR_START": 2019, "YEAR_END": 2026, "CAB": "Crew", "BED": "6.4", "版本": ""},
        {"YEAR_START": 2021, "YEAR_END": 2024, "CAB": "Crew", "BED": "5.6", "版本": "TRX"},
        {"YEAR_START": 2025, "YEAR_END": 2026, "CAB": "Crew", "BED": "5.6", "版本": "RHO"},
    ])
    final, _ = build_verified_candidates([cluster])
    assert len(final) == 1
    assert final[0]["MERGE_STATUS"] == "ACCEPT"
    assert final[0]["_diagnostics"]["INFERRED_NEW_ATOM_COUNT"] == 26


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


def test_final_real_atom_coverage_requires_one_cluster_id():
    left = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2022, "CAB": "Crew", "BED": "5.5"},
    ])
    right = rows("A", "A2", [
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Crew", "BED": "5.5"},
    ])
    diag = verify_unique_real_atom_ownership([left, right])
    assert diag["MERGE_STATUS"] == "REJECT"
    assert diag["MULTI_CLUSTER_ATOM_COUNT"] == 1


def test_final_real_atom_coverage_ignores_nonexistent_combinations():
    cluster = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Regular", "BED": "8.0"},
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Crew", "BED": "5.5"},
    ])
    diag = verify_unique_real_atom_ownership([cluster])
    assert diag["MERGE_STATUS"] == "ACCEPT"
    assert diag["ORIGINAL_ATOM_COUNT"] == 2


def test_final_title_coverage_detects_same_sku_overlap():
    broad = rows("A", "A1", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Crew", "BED": "5.5"},
        {"YEAR_START": 2021, "YEAR_END": 2021, "CAB": "Crew", "BED": "6.5"},
    ])
    exact = rows("A", "A2", [
        {"YEAR_START": 2020, "YEAR_END": 2020, "CAB": "Crew", "BED": "6.5"},
    ])
    assert verify_unique_real_atom_ownership([broad, exact])["MERGE_STATUS"] == "ACCEPT"
    diag = verify_unique_real_atom_title_coverage([broad, exact])
    assert diag["MERGE_STATUS"] == "REJECT"
    assert diag["MULTI_CLUSTER_ATOM_COUNT"] == 1
