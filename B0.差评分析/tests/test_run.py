from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MODULE = PROJECT / "src" / "run.py"
SPEC = importlib.util.spec_from_file_location("negative_review_run", MODULE)
assert SPEC and SPEC.loader
run_mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_mod)


def test_add_sizes_uses_actual_size_and_deduplicates_in_source_order():
    analysis_rows = [
        {"品牌": "Ford", "车型": "F-150", "结构": "Pickup"},
        {"品牌": "Honda", "车型": "Accord", "结构": "Sedan"},
    ]
    raw_rows = [
        {"车型": "2020 Ford F-150", "实际尺寸": "PK-XL"},
        {"车型": "Ford F-150 Crew Cab", "实际尺寸": "PK-XL"},
        {"车型": "Ford F-150", "实际尺寸": "PK-XXL"},
        {"车型": "Honda Accord", "实际尺寸": ""},
    ]

    report = run_mod.add_sizes_from_raw_reviews(analysis_rows, raw_rows)

    assert analysis_rows[0]["尺码"] == "PK-XL；PK-XXL"
    assert analysis_rows[1]["尺码"] == ""
    assert report == {"有尺码行数": 1, "无尺码行数": 1}
