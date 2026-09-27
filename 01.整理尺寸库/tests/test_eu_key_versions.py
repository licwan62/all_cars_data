from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[1]
for path in (PROJECT.parent / "lib", PROJECT / "code"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import merge_dimension_library as merge  # noqa: E402
from regional_size_common import BASE_COLUMNS, RegionalDataError, build_dimension_library_rows, read_csv  # noqa: E402
from regional_sources import key_version, load_key_version_pattern, non_key_tokens  # noqa: E402

PATTERN = load_key_version_pattern()


@pytest.mark.parametrize(
    ("sources", "expected"),
    [
        (("906.657", "elwb h2 prefl"), "elwb h2"),
        (("V362", "l1h1 facelift"), "l1h1"),
        (("X62", ""), ""),
        (("", "3dr prefl"), "3dr"),
        (("", "lwb highroof drw"), "lwb highroof drw"),
        (("K0", "xs high"), ""),
        (("", "LWB lwb"), "LWB"),
        (("F5P", "facelift phase2 mk3 2012 rwd 47kwh"), ""),
    ],
)
def test_key_version_keeps_only_key_tokens(sources, expected):
    assert key_version(PATTERN, *sources) == expected


def test_non_key_tokens_drop_key_words():
    assert non_key_tokens(PATTERN, "lwb h2 prefl 906.657") == "prefl 906.657"


def _base(rows):
    frame = pd.DataFrame(rows)
    for column in BASE_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    return frame


def test_collisions_append_variant_then_body_code_then_dimensions():
    common = {"MAKE": "Audi", "MODEL": "A6", "结构": "Wagon", "YEAR": "2006-2011", "分类": "旅行车", "销量合计": 0}
    base = _base([
        {**common, "版本": "", "_source_variant": "prefl", "_body_code": "4F5", "L-MM": 4933, "W-MM": 1864, "H-MM": 1453},
        {**common, "版本": "", "_source_variant": "facelift", "_body_code": "4F5", "L-MM": 4935, "W-MM": 1855, "H-MM": 1463},
        {**common, "版本": "", "_source_variant": "facelift", "_body_code": "4F5", "L-MM": 4935, "W-MM": 1855, "H-MM": 1463},
        {**common, "MODEL": "A4", "版本": "", "_source_variant": "prefl", "_body_code": "8K5", "L-MM": 4700, "W-MM": 1800, "H-MM": 1400},
    ])
    library, _, row_ids = build_dimension_library_rows(base)
    assert sorted(library["版本"]) == ["", "facelift", "prefl"]  # 无冲突的 A4 版本留空
    assert row_ids.tolist()[1] == row_ids.tolist()[2]  # 完全相同的车身合并到同一 ID


def test_merge_stage_traces_every_input_id():
    rows = [
        {"DIMENSION-ID": "a", "MAKE": "A", "MODEL": "B", "版本": "", "CAB": "", "BED": "", "结构": "SUV", "代际": "",
         "YEAR": "2000-2001", "分类": "SUV", "L-IN": "180", "W-IN": "70", "H-IN": "66", "参考车型": "", "备注": "", "迭代状态": "可入库"},
    ]
    rows.append({**rows[0], "DIMENSION-ID": "b"})
    result, mapping = merge.transform_region_rows_traced(rows, "eu")
    assert len(result) == 1 and "_origin" not in result[0]
    assert mapping == {"a": result[0]["DIMENSION-ID"], "b": result[0]["DIMENSION-ID"]}


def test_published_eu_library_and_migration_are_consistent():
    library = read_csv(PROJECT / "output" / "尺寸库_EU.csv")
    merge.validate_eu_migration(library.to_dict("records"))
    migration = read_csv(PROJECT / "output" / "EU_ID迁移.csv")
    assert set(migration["关系"]) <= {"一对一", "合并", "拆分", "合并且拆分"}
    versions = library["版本"]
    assert versions.eq("").mean() > 0.4
    assert not versions.str.split().map(lambda tokens: len(tokens) != len({t.casefold() for t in tokens})).any()


def test_migration_mismatch_fails(tmp_path):
    path = tmp_path / "m.csv"
    path.write_text("旧DIMENSION-ID,新DIMENSION-ID,关系,旧版本,新版本\nold,new,一对一,,\n", encoding="utf-8-sig")
    with pytest.raises(RegionalDataError, match="不一致"):
        merge.validate_eu_migration([{"DIMENSION-ID": "other"}], path)
