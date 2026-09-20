from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_consolidated_full_table as consolidated  # noqa: E402


def write_region(output_dir: Path, region: str, extra: dict[str, str] | None = None) -> None:
    row = {"MAKE": "Ford", "自动尺码": "3L", **(extra or {})}
    row.update({"DIMENSION-CODE": f"{region}0001", "DIMENSION-ID": f"Ford Focus {region}"})
    pd.DataFrame([row]).to_csv(output_dir / f"全量表_{region}.csv", index=False, encoding="utf-8-sig")


def test_consolidates_three_regions_with_union_columns(tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    write_region(output, "US")
    write_region(output, "EU")
    write_region(output, "RU", {"OZON尺码": "L"})

    result = consolidated.run(output, tmp_path / "final", tmp_path / "artifacts")

    frame = pd.read_csv(tmp_path / "final" / "全量表_汇总.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    assert result["rows"] == 3
    assert list(frame.columns)[-2:] == ["DIMENSION-CODE", "DIMENSION-ID"]
    assert frame.loc[frame["DIMENSION-ID"].str.endswith("US"), "OZON尺码"].item() == ""
    assert list((tmp_path / "artifacts").glob("*_01_consolidated-full-table/status.json"))


def test_missing_region_or_code_column_fails_without_touching_output(tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    write_region(output, "US")
    with pytest.raises(consolidated.ConsolidationError, match="缺少 EU 全量表"):
        consolidated.run(output, tmp_path / "final", tmp_path / "artifacts")

    pd.DataFrame([{"MAKE": "A", "DIMENSION-ID": "A EU"}]).to_csv(
        output / "全量表_EU.csv", index=False, encoding="utf-8-sig"
    )
    write_region(output, "RU")
    with pytest.raises(consolidated.ConsolidationError, match="DIMENSION-CODE"):
        consolidated.run(output, tmp_path / "final", tmp_path / "artifacts")
    assert not (tmp_path / "final" / "全量表_汇总.csv").exists()
    assert not (tmp_path / "artifacts").exists()
