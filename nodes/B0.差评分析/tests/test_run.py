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


def test_run_reads_single_raw_ledger_and_never_writes_data(tmp_path: Path):
    import hashlib
    import shutil

    data = tmp_path / "data"
    shutil.copytree(PROJECT / "data", data)
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in data.iterdir()}
    result = run_mod.run(data, tmp_path / "output", tmp_path / "artifacts")
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in data.iterdir()}
    assert after == before
    assert sorted(path.name for path in (tmp_path / "output").iterdir()) == sorted(result["outputs"])
    artifact = Path(result["artifact"])
    for name in (run_mod.SIZE_SUMMARY_NAME, run_mod.SIZE_REVIEW_NAME, run_mod.EAR_DETAIL_NAME):
        assert (artifact / name).is_file()
    assert sorted(path.name for path in (artifact / "input").iterdir()) == sorted(run_mod.REQUIRED_INPUTS)
