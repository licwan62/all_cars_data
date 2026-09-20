from __future__ import annotations

import importlib.util
import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT / "code" / "merge_dimension_library.py"
SPEC = importlib.util.spec_from_file_location("merge_dimension_library", MODULE_PATH)
assert SPEC and SPEC.loader
merge_dimension_library = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(merge_dimension_library)


def test_load_region_appends_the_matching_suffix(monkeypatch, tmp_path):
    source = tmp_path / "00_US尺寸库.csv"
    source.write_text(
        "DIMENSION-ID,MAKE,MODEL,版本,CAB,BED,结构,代际,YEAR,分类,L-IN,W-IN,H-IN,参考车型,备注,迭代状态\n"
        "Acura ADX SUV 2025-2026,Acura,ADX,,,,SUV,,2025-2026,越野车,185.8,72.5,63.8,,,可入库\n",
        encoding="utf-8-sig",
    )
    monkeypatch.setattr(merge_dimension_library, "region_library_path", lambda region: source)

    rows = merge_dimension_library.load_region("us")

    assert rows[0]["DIMENSION-ID"] == "Acura ADX SUV 2025-2026 US"


def test_merge_keeps_each_region_distinct_after_suffix(monkeypatch):
    row = {
        "DIMENSION-ID": "Same ID", "MAKE": "A", "MODEL": "B", "版本": "", "CAB": "", "BED": "",
        "结构": "SUV", "代际": "", "YEAR": "2025", "分类": "越野车", "L-IN": "1", "W-IN": "1",
        "H-IN": "1", "参考车型": "", "备注": "", "迭代状态": "",
    }
    monkeypatch.setattr(merge_dimension_library, "load_region", lambda region: [{**row, "DIMENSION-ID": f"Same ID {region.upper()}"}])

    assert [row["DIMENSION-ID"] for row in merge_dimension_library.merge()] == [
        "Same ID US", "Same ID EU", "Same ID RU"
    ]


def test_load_eu_region_clears_reference_and_dimension_source(monkeypatch, tmp_path):
    source = tmp_path / "00_EU尺寸库.csv"
    source.write_text(
        "DIMENSION-ID,MAKE,MODEL,版本,CAB,BED,结构,代际,YEAR,分类,L-IN,W-IN,H-IN,参考车型,备注,迭代状态\n"
        "AC 428 Convertible 1965-1974,AC,428,,,,Convertible,,1965-1974,跑车,174,67,51,来源车型,尺寸来源：https://example.com,可入库\n",
        encoding="utf-8-sig",
    )
    monkeypatch.setattr(merge_dimension_library, "region_library_path", lambda region: source)

    row = merge_dimension_library.load_region("eu")[0]

    assert row["DIMENSION-ID"] == "AC 428 Convertible 1965-1974 EU"
    assert row["参考车型"] == ""
    assert row["备注"] == ""


def test_structure_door_rules_are_loaded_from_json():
    rules = merge_dimension_library.load_structure_rules()

    assert merge_dimension_library.normalize_structure("Hatchback 3-door", rules) == "Hatchback"
    assert merge_dimension_library.normalize_structure("SUV 5-door", rules) == "SUV 5dr"
    assert merge_dimension_library.normalize_structure("Hatchback 4-door", rules) == "Hatchback 4dr"
    assert merge_dimension_library.normalize_structure("3-door", rules) == ""
    assert merge_dimension_library.normalize_structure("5-door", rules) == "5dr"
    assert merge_dimension_library.normalize_structure("Sedan", rules) == "Sedan"


def test_regenerate_dimension_ids_uses_normalized_fields_and_resolves_collisions():
    rules = merge_dimension_library.load_dimension_id_rules()
    rows = [
        {
            "MAKE": "Example", "MODEL": "Tracker", "版本": "", "结构": "SUV", "YEAR": "2000-2001",
            "分类": "越野车", "CAB": "", "BED": "", "代际": "I", "L-IN": "142.5", "W-IN": "64.2", "H-IN": "65.1",
        },
        {
            "MAKE": "Example", "MODEL": "Tracker", "版本": "", "结构": "SUV", "YEAR": "2000-2001",
            "分类": "越野车", "CAB": "", "BED": "", "代际": "I", "L-IN": "143.0", "W-IN": "64.2", "H-IN": "65.4",
        },
    ]

    merge_dimension_library.regenerate_dimension_ids(rows, "ru", rules)

    assert len({row["DIMENSION-ID"] for row in rows}) == 2
    assert all(row["DIMENSION-ID"].endswith(" RU") for row in rows)
    assert all("door" not in row["DIMENSION-ID"].lower() for row in rows)
    assert all(row["版本"].startswith("I L") for row in rows)


def test_normalized_physical_duplicates_are_collapsed():
    rules = merge_dimension_library.load_dimension_id_rules()
    row = {
        "MAKE": "SsangYong", "MODEL": "Korando", "版本": "", "CAB": "", "BED": "", "结构": "SUV",
        "代际": "II", "YEAR": "1996-2006", "分类": "越野车", "L-IN": "170.5", "W-IN": "72.5",
        "H-IN": "76.4", "迭代状态": "可入库", "DIMENSION-ID": "old",
    }

    unique = merge_dimension_library.deduplicate_normalized_rows([row.copy(), row.copy()], rules)

    assert len(unique) == 1


def test_published_eu_ru_ids_follow_json_rules():
    rules = merge_dimension_library.load_dimension_id_rules()
    for region in ("EU", "RU"):
        path = PROJECT / "output" / f"尺寸库_{region}.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        ids = [row["DIMENSION-ID"] for row in rows]
        assert len(ids) == len(set(ids))
        assert all(
            row["DIMENSION-ID"]
            == merge_dimension_library.append_country_code(
                merge_dimension_library._compose_dimension_id(row, rules), region
            )
            for row in rows
        )
