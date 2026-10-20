import importlib.util
import json
from pathlib import Path
import sys

import pandas as pd
import pytest


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
SPEC = importlib.util.spec_from_file_location("expanded_listing_analysis", SRC / "expanded_listing_analysis.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_request_config_covers_21_items_and_six_corvette_generations():
    config = json.loads(MODULE.CONFIG_PATH.read_text(encoding="utf-8"))
    assert len(config["segments"]) == 25
    assert len({s["parent"] for s in config["segments"]}) == 21
    assert {s["generation"] for s in config["segments"] if s["MODEL"] == "Corvette"} == {"gen3", "gen4", "gen5", "gen6", "gen7", "gen8"}


def test_doors_and_generations_do_not_cross_match():
    config = json.loads(MODULE.CONFIG_PATH.read_text(encoding="utf-8"))
    rows = pd.DataFrame({"MAKE": ["Ford", "Ford", "Ford", "Chevrolet", "Chevrolet"],
                         "MODEL": ["Bronco", "Bronco", "Bronco Sport", "Corvette", "Corvette"],
                         "版本": ["2dr", "4dr Raptor", "", "", ""],
                         "代际": ["gen6", "gen6", "gen1", "gen3", "gen8"],
                         "YEAR": ["2022-2026", "2022-2026", "2021-2026", "1968-1982", "2020-2026"]})
    for segment_id, expected in [("BRONCO_2DR", [0]), ("BRONCO_4DR", [1]), ("CORVETTE_C3", [3]), ("CORVETTE_C8", [4])]:
        segment = next(s for s in config["segments"] if s["id"] == segment_id)
        assert rows.index[MODULE.request_mask(rows, segment, config, 2026)].tolist() == expected


def test_reserve_counts_overlap_once_and_zero_recent_classic_gets_only_floor():
    selected = pd.DataFrame({"CLUSTER_ID": ["old", "overlap", "classic"], "近期销量估值": [300, 100, 0]})
    result = MODULE.allocate(selected, {"overlap", "classic"}, 900, 6).set_index("CLUSTER_ID")
    assert result["综合试算件数"].sum() == 900
    assert result["指定试销保底件数"].sum() == 12
    assert result.loc["classic", "综合试算件数"] == 6
    assert result.loc["overlap", "指定试销保底件数"] == 6
    assert set(result.index) == {"old", "overlap", "classic"}
    with pytest.raises(ValueError, match="超过预算"):
        MODULE.allocate(selected, {"overlap", "classic"}, 5, 6)


def test_request_choice_skips_held_newer_variant_and_uses_reference_period():
    candidates = pd.DataFrame({"请求细分ID": ["OUTBACK", "OUTBACK"], "候选状态": ["暂缓", "可参与试算"],
                               "近期销量估值": [900000, 0], "参考期销量估值": [900000, 500000],
                               "生命周期已知销量估值": [900000, 500000], "CLUSTER_ID": ["held", "old"],
                               "PHYSICAL_SKU": ["5L", "2XXL"], "适配年份": ["2020-2025", "2010-2019"],
                               "版本": ["Wilderness", ""], "结构": ["Wagon", "Hatchback"]})
    config = {"segments": [{"id": "OUTBACK", "label": "Subaru Outback", "parent": "Subaru Outback"}]}
    selected, coverage = MODULE.pick_requested(candidates, config)
    assert selected == {"OUTBACK": "old"}
    assert coverage.loc[0, "代表选择依据"] == "2010-2025参考期销量"


def test_explicit_scope_exception_is_narrow_and_does_not_clear_quality_holds():
    config = json.loads(MODULE.CONFIG_PATH.read_text(encoding="utf-8"))
    rows = pd.DataFrame([
        {"DIMENSION-ID": "x", "MAKE": "Tesla", "MODEL": "Model X", "版本": "", "代际": "gen1", "YEAR": "2016-2026", "自动尺码": "YXXL-525", "范围判定": "排除W范围", "暂缓原因": "hold"},
        {"DIMENSION-ID": "classic", "MAKE": "Buick", "MODEL": "Classic", "版本": "", "代际": "gen1", "YEAR": "1970", "自动尺码": "4M-0", "范围判定": "排除W范围", "暂缓原因": ""},
        {"DIMENSION-ID": "bad", "MAKE": "Dodge", "MODEL": "Challenger", "版本": "", "代际": "gen3", "YEAR": "2015-2023", "自动尺码": "无可用尺码", "范围判定": "排除W范围", "暂缓原因": ""},
    ])
    for column, value in [("L-MM", 5000), ("W-MM", 1900), ("H-MM", 1500), ("自动长度余量", 100), ("质量提醒", ""), ("CLUSTER_ID", "original")]:
        rows[column] = value
    atoms = pd.DataFrame({"atom_record_id": ["x|ATOM_YEAR=2020"], "预估销量": [10], "DIMENSION-ID": ["x"], "ATOM_YEAR": [2020], "期外销量缺失": [False]})
    full, _ = MODULE.extend_scope(rows, atoms, {"rules": [{"尺码": "YXXL-525"}, {"尺码": "4M-0"}]}, config, {"fitment_max_year": 2026})
    full = full.set_index("DIMENSION-ID")
    assert full.loc["x", "范围判定"] == "范围内"
    assert full.loc["x", "暂缓原因"] == "hold"
    assert full.loc["classic", "范围判定"] == "排除W范围"
    assert full.loc["bad", "范围判定"] == "排除W范围"
