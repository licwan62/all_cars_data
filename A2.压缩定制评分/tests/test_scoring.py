from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import scoring as scoring_mod  # noqa: E402


def key(brand="Ford", model="Focus", structure="Sedan"):
    return scoring_mod.ModelKey(brand, model, structure)


def test_scores_from_all_three_tables():
    keys = [key()]
    negative = [{"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "差评占比": "0.8"}]
    manual = [{"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "当前状态": "未开始"}]
    ear = [{"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "车耳状态": "正常"}]
    scored, report = scoring_mod.score_keys(keys, negative, manual, ear)
    row = scored[0]
    assert row["差评评分"] == 0.8
    assert row["人工维护进度评分"] == 1.0
    assert row["车耳状态评分"] == 0.0
    assert abs(row["综合定制需求度"] - 0.6) < 1e-9
    assert row["参与评分维度数"] == 3
    assert report["数据不足车型数"] == 0


def test_missing_data_reweights_instead_of_zero():
    keys = [key()]
    manual = [{"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "当前状态": "进行中"}]
    scored, _ = scoring_mod.score_keys(keys, [], manual, [])
    row = scored[0]
    assert row["差评评分"] is None
    assert row["车耳状态评分"] is None
    assert row["综合定制需求度"] == 0.5
    assert row["参与评分维度数"] == 1


def test_no_data_at_all_is_insufficient_not_zero():
    scored, report = scoring_mod.score_keys([key()], [], [], [])
    row = scored[0]
    assert row["综合定制需求度"] is None
    assert row["定制需求等级"] == "数据不足"
    assert report["数据不足车型数"] == 1


def test_negative_review_falls_back_to_severity_bucket():
    keys = [key()]
    negative = [{"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "差评占比": "", "严重度评级": "高"}]
    scored, _ = scoring_mod.score_keys(keys, negative, [], [])
    assert scored[0]["差评评分"] == 0.8


def test_bucket_level_thresholds():
    rules = scoring_mod.DEFAULT_RULES
    assert scoring_mod.bucket_level(0.1, rules["thresholds"]) == "低"
    assert scoring_mod.bucket_level(0.5, rules["thresholds"]) == "中"
    assert scoring_mod.bucket_level(0.9, rules["thresholds"]) == "高"
    assert scoring_mod.bucket_level(None, rules["thresholds"]) == "数据不足"


def test_canonicalize_structure_folds_regional_five_door_suv_into_bare_suv():
    mapping = {"SUV 5dr": "SUV"}
    assert scoring_mod.canonicalize_structure("SUV 5dr", mapping) == "SUV"
    assert scoring_mod.canonicalize_structure("SUV", mapping) == "SUV"
    assert scoring_mod.canonicalize_structure("SUV 3dr", mapping) == "SUV 3dr"
    assert scoring_mod.canonicalize_structure("Sedan", mapping) == "Sedan"


def test_canonicalize_structure_without_mapping_is_identity():
    assert scoring_mod.canonicalize_structure("SUV 5dr") == "SUV 5dr"


def test_duplicate_keys_in_manual_table_are_reported():
    keys = [key()]
    manual = [
        {"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "当前状态": "未开始"},
        {"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "当前状态": "已完成"},
    ]
    _, report = scoring_mod.score_keys(keys, [], manual, [])
    assert report["人工维护进度表重复键数"] == 1
