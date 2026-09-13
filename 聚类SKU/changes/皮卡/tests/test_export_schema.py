import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from export import SUMMARY_COLUMNS, export_cluster_detail, export_cluster_summary


def _cluster(rows):
    diagnostics = {
        "MERGE_STATUS": "ACCEPT",
        "ORIGINAL_ATOM_COUNT": 2,
        "EXPANDED_ATOM_COUNT": 4,
        "INFERRED_NEW_ATOM_COUNT": 2,
        "MULTI_CLUSTER_ATOM_COUNT": 0,
        "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": 0,
    }
    return {
        "CLUSTER_ID": "LINK-000001",
        "LINK_ID": "LINK-000001",
        "CLUSTER_KEY": "internal-key",
        "PROVISIONAL_CLUSTER_ID": "OLD-ID",
        "自动尺码": "PK-L",
        "TRUCK_TYPE": "FULLSIZE",
        "AXLE_TYPE": "SRW",
        "CAB_GROUP": "MIXED",
        "BED_GROUP": "MIXED",
        "CONSUMER_NAME_OPTIMIZED": "2020-2021 Ford F-150",
        "MAIN_PART": "2020-2021 Ford F-150",
        "ADDITION_PART": "Crew Cab Short Bed (5.5')",
        "YEAR_COMPACT": "2020-2021",
        "FITMENT_SUMMARY": "Ford F-150",
        "fitment_count": len(rows),
        "year_min": 2020,
        "year_max": 2021,
        "l_min": 5000.04,
        "l_max": 5100.06,
        "w_min": 1900.04,
        "w_max": 2000.06,
        "h_min": 1800.04,
        "h_max": 1900.06,
        "length_margin_min": 99.94,
        "length_margin_median": 105.06,
        "estimated_sales": 1234.56,
        "CLUSTER_SCORE": 0.36,
        "CONFIDENCE": "HIGH",
        "safety_pass": True,
        "YEAR_GAP_FILLED": 0,
        "_diagnostics": diagnostics,
        "_optimized_diagnostics": diagnostics,
        "rows": rows,
    }


def test_summary_uses_cluster_id_as_the_only_exported_identifier(tmp_path):
    rows = pd.DataFrame({"DIMENSION-ID": ["D1"]})
    path = Path(export_cluster_summary([_cluster(rows)], str(tmp_path)))
    result = pd.read_csv(path, encoding="utf-8-sig")

    assert result.columns.tolist() == SUMMARY_COLUMNS
    assert result["CLUSTER_ID"].is_unique
    assert not {"LINK_ID", "CLUSTER_KEY", "PROVISIONAL_CLUSTER_ID"} & set(result.columns)
    assert "1234.6" in path.read_text(encoding="utf-8-sig")


def test_detail_removes_internal_and_repeated_cluster_columns(tmp_path):
    valid = pd.DataFrame({
        "DIMENSION-ID": ["D1"],
        "自动尺码": ["PK-L"],
        "EXCEPTION_REASON": [""],
        "L-MM": [5000.04],
    })
    cluster = _cluster(valid.copy())
    path = Path(export_cluster_detail([cluster], valid, str(tmp_path)))
    result = pd.read_csv(path, encoding="utf-8-sig")

    assert result.columns[:3].tolist() == ["CLUSTER_ID", "PHYSICAL_SKU", "DIMENSION-ID"]
    assert not {
        "LINK_ID", "CLUSTER_KEY", "PROVISIONAL_CLUSTER_ID", "CLUSTER_SCORE",
        "自动尺码", "EXCEPTION_REASON",
    } & set(result.columns)
    assert "5000.0" in path.read_text(encoding="utf-8-sig")
