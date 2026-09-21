from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("publish_ru_data", PROJECT / "publish_ru_data.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_ru_release_inputs_are_consistent():
    summary = module.validate_release()

    assert summary["dimension_rows"] == 13848
    assert summary["full_rows"] == 13848
    assert summary["unique_dimension_ids"] == 13848
    assert summary["sales_total"] == 296972
    assert summary["matched_sizes"] == 13314
    assert summary["unavailable_sizes"] == 534
