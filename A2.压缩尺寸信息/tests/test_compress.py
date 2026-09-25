from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from src import run as run_mod  # noqa: E402

FIELDS = ["MAKE", "MODEL", "版本", "结构", "CAB", "BED", "YEAR", "分类", "自动尺码", "DIMENSION-ID"]


def row(make="Ford", model="Focus", version="", structure="Sedan", cab="", bed="", year="2018-2019", category="三厢车", size="M", region="US"):
    return {
        "MAKE": make, "MODEL": model, "版本": version, "结构": structure, "CAB": cab, "BED": bed,
        "YEAR": year, "分类": category, "自动尺码": size,
        "DIMENSION-ID": " ".join(part for part in [make, model, version, structure, year, region] if part),
    }


def profile() -> dict:
    return run_mod.load_field_profile((PROJECT_DIR / "data" / run_mod.FIELD_PROFILE).resolve())


def compress(rows: list[dict], region: str = "US") -> dict[str, pd.DataFrame]:
    frame = pd.DataFrame(rows, columns=FIELDS).astype(str)
    return run_mod.compress_region(region, frame, profile())["tables"]


def years_of(table: pd.DataFrame) -> list[str]:
    return sorted(table["YEAR"].tolist())


def test_single_year_rows_are_kept():
    # 旧算法只认 YYYY-YYYY，单年份行被整行跳过（US 约 30%）
    tables = compress([row(year="1987"), row(year="1988"), row(year="1989-1990")])
    assert years_of(tables["non_pickup_lossless"]) == ["1987-1990"]


def test_versions_with_different_sizes_are_not_majority_voted():
    tables = compress([
        row(model="Blazer", version="2dr", structure="SUV", year="1995-1997", size="YM"),
        row(model="Blazer", version="4dr", structure="SUV", year="1995-1997", size="YL"),
    ])
    high = tables["non_pickup_high"]
    assert set(zip(high["VERSION"], high["BACKSIZE"])) == {("2dr", "YM"), ("4dr", "YL")}


def test_same_size_rows_merge_in_high_table():
    tables = compress([row(year="2018-2019", size="M"), row(year="2020-2021", size="M")])
    assert years_of(tables["non_pickup_high"]) == ["2018-2021"]


def test_pickups_are_split_into_pickup_tables():
    tables = compress([
        row(),
        row(make="Ford", model="F-150", structure="", cab="Crew", bed="5.5", category="皮卡", year="2019-2020", size="PK-M"),
    ])
    assert len(tables["pickup_lossless"]) == 1
    assert tables["pickup_lossless"].iloc[0]["CAB"] == "Crew"
    assert "F-150" not in set(tables["non_pickup_lossless"]["MODEL"])


def test_wrong_region_rows_fail():
    with pytest.raises(run_mod.CompressionError):
        compress([row(region="EU")], region="US")


def test_model_combo_comes_from_node_data():
    assert run_mod.engine.DEFAULT_MODEL_COMBO_PATH == PROJECT_DIR / "data" / run_mod.MODEL_COMBO


def write_sources(source_dir: Path, rows_by_region: dict[str, list[dict]]) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    for region, rows in rows_by_region.items():
        with (source_dir / run_mod.upstream_file(region)).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)


def test_run_writes_artifact_and_outputs(tmp_path: Path):
    write_sources(tmp_path / "src", {region: [row(region=region)] for region in run_mod.REGIONS})
    result = run_mod.run(tmp_path / "src", PROJECT_DIR / "data", tmp_path / "output", tmp_path / "artifacts")
    expected = sorted(name for region in run_mod.REGIONS for name in run_mod.output_names(region).values())
    assert sorted(path.name for path in (tmp_path / "output").iterdir()) == expected
    artifact = Path(result["artifact"])
    status = json.loads((artifact / "status.json").read_text(encoding="utf-8"))
    assert status["status"] == "passed"
    assert (artifact / "input" / run_mod.FIELD_PROFILE).is_file()
    assert (artifact / "input" / run_mod.MODEL_COMBO).is_file()


def test_failed_run_leaves_output_untouched(tmp_path: Path):
    output = tmp_path / "output"
    output.mkdir()
    (output / "keep.csv").write_text("x", encoding="utf-8")
    write_sources(tmp_path / "src", {"US": [row()], "EU": [row(region="US")], "RU": [row(region="RU")]})
    with pytest.raises(run_mod.CompressionError):
        run_mod.run(tmp_path / "src", PROJECT_DIR / "data", output, tmp_path / "artifacts")
    assert [path.name for path in output.iterdir()] == ["keep.csv"]
