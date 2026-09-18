from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "export_eu_pipeline.py"
spec = importlib.util.spec_from_file_location("export_eu_pipeline", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source = pd.DataFrame(
        [
            ["Demo", "One", "Base", "Van", "FWD", "Gas", "80", "109", "Jan 2020", "-", "1"],
            ["Demo", "Two", "Base", "MPV", "FWD", "Gas", "90", "122", "Jan 2021", "-", "2"],
            ["Demo", "Three", "Base", "Sedan", "RWD", "Gas", "100", "136", "Jan 2022", "-", "3"],
        ],
        columns=module.SOURCE_COLUMNS,
    )
    mapping = pd.DataFrame(
        [
            ["1", "1", "Van", "G1", "", "4", "EU-DEMO-SHARED-01", "HIGH", "cargo, quoted", "READY"],
            ["2", "2", "MPV", "G1", "", "5", "EU-DEMO-SHARED-01", "HIGH", "passenger", "READY"],
            ["3", "3", "Sedan", "G1", "", "4", "", "LOW", "no evidence", "PENDING: source"],
        ],
        columns=module.MAPPING_COLUMNS,
    )
    dimensions = pd.DataFrame(
        [
            ["EU-DEMO-SHARED-01", "4500", "1800", "1900", "Official, brochure", "https://example.com/demo"],
            ["EU-DEMO-ORPHAN-01", "4300", "1750", "1450", "Official", "https://example.com/orphan"],
        ],
        columns=module.DIMENSION_COLUMNS,
    )
    return source, mapping, dimensions


def test_build_pipeline_inputs_filters_pending_and_orphans() -> None:
    source, mapping, dimensions = frames()
    source_out, mapping_out, dimensions_out, summary = module.build_pipeline_inputs(
        source, mapping, dimensions
    )
    assert source_out["Ktype"].tolist() == ["1", "2"]
    assert mapping_out["IterationStatus"].tolist() == ["READY", "READY"]
    assert dimensions_out["DIMENSION_GROUP_ID"].tolist() == [
        "EU-DEMO-SHARED-01-PIPE-MPV",
        "EU-DEMO-SHARED-01-PIPE-VAN",
    ]
    assert list(dimensions_out.columns) == module.PIPELINE_DIMENSION_COLUMNS
    assert summary["pending_mapping_rows_skipped"] == 1
    assert summary["ready_ktypes"] == 2
    assert summary["shared_dimension_groups_split_for_pipeline"] == 1


def test_exported_csv_is_quoted_and_build_base_keeps_mapping_body_style(tmp_path: Path) -> None:
    source, mapping, dimensions = frames()
    source, mapping, dimensions, summary = module.build_pipeline_inputs(
        source, mapping, dimensions
    )
    module.export_source_candidate(source, mapping, dimensions, tmp_path, summary)

    matched_text = (tmp_path / "source" / "KtypeMatched.csv").read_text(encoding="utf-8-sig")
    dimension_text = (tmp_path / "source" / "DimensionGroup尺寸.csv").read_text(encoding="utf-8-sig")
    assert '"cargo, quoted"' in matched_text
    assert '"Official, brochure"' in dimension_text

    eu = module._load_eu_module()
    base, extra = eu.build_base(tmp_path / "source", 2026)
    assert extra["repaired_csv_rows"] == {"Ktype": 0, "KtypeMatched": 0, "DimensionGroup": 0}
    assert set(base["结构"]) == {"Van", "MPV"}
    assert set(base["分类"]) == {"两厢车"}


def test_conflicting_mapping_id_is_rejected() -> None:
    source, mapping, dimensions = frames()
    conflict = mapping.iloc[[0]].copy()
    conflict.loc[:, "DIMENSION_GROUP_ID"] = "EU-DEMO-OTHER-01"
    mapping = pd.concat([mapping, conflict], ignore_index=True)
    with pytest.raises(module.ExportError, match="id 存在冲突"):
        module.build_pipeline_inputs(source, mapping, dimensions)
