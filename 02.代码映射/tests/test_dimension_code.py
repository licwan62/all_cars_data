from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.config import load_settings, region_names
from src.dimension_code import dimension_code, duplicate_code_count, year_code
from src.main import run_all


def test_year_code_uses_last_two_digits_of_both_ends():
    assert year_code("1956-2012") == "5612"
    assert year_code("2013-2015") == "1315"
    assert year_code("1994") == "9494"
    with pytest.raises(ValueError):
        year_code("1994-")


def test_dimension_code_concatenates_prefix_make_model_year():
    assert dimension_code("", "25", "02", "1995-2001") == "25029501"
    assert dimension_code("E", "016", "013", "2009-2012") == "E0160130912"


def test_duplicate_code_count_counts_rows_sharing_a_code():
    rows = [{"DIMENSION-CODE": "a"}, {"DIMENSION-CODE": "a"}, {"DIMENSION-CODE": "b"}]
    assert duplicate_code_count(rows) == 2


def _config(tmp_path: Path) -> Path:
    config = tmp_path / "config.yaml"
    config.write_text(
        "\n".join(
            [
                f"input: {{path: {tmp_path / 'lib.csv'}, encoding: utf-8-sig}}",
                "columns: {make: MAKE, model: MODEL, sales: '', dimension_id: DIMENSION-ID, year: YEAR}",
                "code: {width: 2, max_value: 99}",
                "regions:",
                "  - {name: US, prefix: '', width: 2, mapping_dir: data/mapping/us}",
                "  - {name: EU, prefix: E, width: 3, mapping_dir: data/mapping/eu}",
                "mapping: {make_path: data/mapping/us/make_mapping.csv, model_path: data/mapping/us/model_mapping.csv}",
                "artifacts: {path: artifacts, slug: code-mapping-publish}",
                "publish: {path: output/车型编码映射.csv, dimension_code_path: output/尺寸编码映射.csv}",
                "public_publish: {path: public/车型编码映射.csv}",
            ]
        ),
        encoding="utf-8",
    )
    return config


def test_run_all_encodes_each_region_independently(tmp_path):
    with (tmp_path / "lib.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["DIMENSION-ID", "MAKE", "MODEL", "YEAR"])
        writer.writerows(
            [
                ["Ford Focus Sedan 2010-2014 US", "Ford", "Focus", "2010-2014"],
                ["Ford Focus Sedan 2010-2014 EU", "Ford", "Focus", "2010-2014"],
                ["Audi A4 Sedan 1994 EU", "Audi", "A4", "1994"],
            ]
        )
    config = _config(tmp_path)
    assert region_names(config) == ["US", "EU"]
    assert load_settings(config, "EU").code_width == 3

    run_all(config)

    with (tmp_path / "output" / "尺寸编码映射.csv").open(encoding="utf-8-sig", newline="") as handle:
        codes = {row["DIMENSION-ID"]: row["DIMENSION-CODE"] for row in csv.DictReader(handle)}
    assert codes == {
        "Ford Focus Sedan 2010-2014 US": "00001014",
        "Ford Focus Sedan 2010-2014 EU": "E0010001014",
        "Audi A4 Sedan 1994 EU": "E0000009494",
    }
