import csv
from pathlib import Path

import output_layout as layout
from build_match_report import shelf_rows
from trim.matching import load_id_migration, maintained_trims, migrated_ids
from trim.size_analysis import normalized_trims


PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT / "output"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def test_us_full_table_trim_comes_from_maintained_trim_values():
    _, rows = read_rows(OUTPUT / layout.full_table("US"))
    current_ids = {row["DIMENSION-ID"].removesuffix(" US") for row in rows}
    maintained = maintained_trims(current_ids)
    assert any(row["TRIM"] for row in rows)
    for row in rows:
        base_id = row["DIMENSION-ID"].removesuffix(" US")
        assert row["TRIM"] == normalized_trims(maintained.get(base_id, "")), row["DIMENSION-ID"]


def test_store_tables_share_us_rows_and_trim():
    _, us_rows = read_rows(OUTPUT / layout.full_table("US"))
    for store in dict.fromkeys(row[0] for row in shelf_rows()):
        _, store_rows = read_rows(OUTPUT / layout.store_table(store))
        assert [row["DIMENSION-ID"] for row in store_rows] == [row["DIMENSION-ID"] for row in us_rows]
        assert [row["TRIM"] for row in store_rows] == [row["TRIM"] for row in us_rows]


def test_only_us_tables_have_trim_and_none_have_dimension_code():
    for region in layout.REGIONS:
        columns, _ = read_rows(OUTPUT / layout.full_table(region))
        assert ("TRIM" in columns) == (region == "US"), region
        assert "DIMENSION-CODE" not in columns
        assert columns[0] == "DIMENSION-ID"
        assert (columns[-1] == "TRIM") == (region == "US"), region


def test_trim_adapter_points_to_current_us_ids():
    _, us_rows = read_rows(OUTPUT / layout.full_table("US"))
    current_ids = {row["DIMENSION-ID"].removesuffix(" US") for row in us_rows}
    columns, adapter = read_rows(OUTPUT / layout.TRIM_ADAPTER)
    assert columns == ["DIMENSION-ID", "Size", "Year", "Make", "Model"]
    assert adapter and {row["DIMENSION-ID"] for row in adapter if row["DIMENSION-ID"]} <= current_ids


def test_id_migration_maps_by_year_then_default(tmp_path):
    path = tmp_path / "migration.csv"
    path.write_text(
        "旧DIMENSION-ID,Year,新DIMENSION-ID,依据\nOld,2020,New A,拆分\nOld,,New B,默认\nGone,,,不映射\n",
        encoding="utf-8-sig",
    )
    migration = load_id_migration({"New A", "New B"}, path)
    assert migrated_ids(migration, "Old", "2020") == ["New A"]
    assert migrated_ids(migration, "Old", "2021") == ["New B"]
    assert migrated_ids(migration, "Old", None) == ["New A", "New B"]
    assert migrated_ids(migration, "Gone", "2020") == []
    assert migrated_ids(migration, "Other", "2020") is None


def test_each_region_has_markdown_match_report():
    for region in layout.REGIONS:
        text = (OUTPUT / layout.match_report(region)).read_text(encoding="utf-8")
        assert text.startswith(f"# {region} 尺码匹配报告")
        assert "## 匹配概况" in text and "## 尺码规则" in text
    assert "## TRIM 匹配" in (OUTPUT / layout.match_report("US")).read_text(encoding="utf-8")
