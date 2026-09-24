from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import scoring as scoring_mod  # noqa: E402


def key(brand="Ford", model="Focus"):
    return scoring_mod.ModelKey(brand, model)


def test_scores_from_single_structure_row_without_structure_prefix():
    keys = [key()]
    negative = [{"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "差评占比": "0.8",
                 "差评数量": "5", "主要差评原因": "尺寸不合适(3)；质量差(2)"}]
    scored, report = scoring_mod.score_keys(keys, negative, [])
    row = scored[0]
    assert row["差评评分"] == 0.8
    assert row["定制需求等级"] == "高"
    # 只有一个结构：不加结构前缀；质量差不是尺寸/耳位问题，被过滤掉。
    assert row["差评备注"] == "尺寸不合适(3)"
    assert report["数据不足车型数"] == 0


def test_negative_review_falls_back_to_severity_bucket():
    keys = [key()]
    negative = [{"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "差评占比": "", "严重度评级": "高"}]
    scored, _ = scoring_mod.score_keys(keys, negative, [])
    assert scored[0]["差评评分"] == 0.8


def test_no_data_leaves_level_and_note_blank_not_insufficient_string():
    scored, report = scoring_mod.score_keys([key()], [], [])
    row = scored[0]
    assert row["差评评分"] is None
    assert row["定制需求等级"] == ""
    assert row["差评备注"] == ""
    assert row["年份"] == ""
    assert row["尺码"] == ""
    assert report["数据不足车型数"] == 1


def test_sizes_pass_through_merged_across_structures():
    negative = [
        {"品牌": "Acura", "车型": "TLX", "结构": "Sedan", "尺码": "3XL+；3XL"},
        {"品牌": "Acura", "车型": "TLX", "结构": "Coupe", "尺码": "3XL；2XL"},
        {"品牌": "Acura", "车型": "TLX", "结构": "Wagon", "尺码": ""},
    ]
    scored, _ = scoring_mod.score_keys([key("Acura", "TLX")], negative, [])
    assert scored[0]["尺码"] == "3XL+；3XL；2XL"


def test_multiple_structures_merge_into_one_row_with_structure_prefix():
    keys = [key("Chevrolet", "Bel Air")]
    negative = [
        {"品牌": "Chevrolet", "车型": "Bel Air", "结构": "Convertible", "差评占比": "0.2",
         "差评数量": "1", "主要差评原因": "尺寸小 不合适(1)"},
        {"品牌": "Chevrolet", "车型": "Bel Air", "结构": "Sedan", "差评占比": "0.8",
         "差评数量": "3", "主要差评原因": "尺寸不合适(2)；偏小(1)；拉链问题(1)"},
    ]
    scored, report = scoring_mod.score_keys(keys, negative, [])
    row = scored[0]
    # 加权平均：(0.2*1 + 0.8*3) / 4 = 0.65
    assert abs(row["差评评分"] - 0.65) < 1e-9
    # 拉链问题被过滤；多结构时逐条打结构前缀。
    assert row["差评备注"] == "convertible 尺寸小 不合适(1)；sedan 尺寸不合适(2)；sedan 偏小(1)"
    assert report["车型数"] == 1


def test_duplicate_brand_model_structure_is_reported():
    keys = [key()]
    negative = [
        {"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "差评占比": "0.2"},
        {"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "差评占比": "0.9"},
    ]
    _, report = scoring_mod.score_keys(keys, negative, [])
    assert report["差评表结构重复数"] == 1


def test_ear_position_passes_through_without_scoring():
    keys = [key()]
    ear = [{"品牌": "Ford", "车型": "Focus", "耳位(普通/靠前/靠后)": "靠前"}]
    scored, _ = scoring_mod.score_keys(keys, [], ear)
    row = scored[0]
    assert row["耳位(普通/靠前/靠后)"] == "靠前"
    # 耳位不参与评分：没有差评数据时仍然是空（"数据不足"），不会因为有耳位信号就有分数。
    assert row["差评评分"] is None
    assert row["定制需求等级"] == ""


def test_pickup_cab_bed_note_appended():
    keys = [key("Toyota", "Tacoma")]
    negative = [{"品牌": "Toyota", "车型": "Tacoma", "结构": "Pickup", "差评占比": "0.3",
                 "差评数量": "2", "主要差评原因": "尺寸不合适(1)"}]
    cab_bed = [{"品牌": "Toyota", "车型": "Tacoma", "驾驶室货斗备注": "Crew Cab/Short Bed(14)"}]
    scored, _ = scoring_mod.score_keys(keys, negative, [], cab_bed)
    assert scored[0]["差评备注"] == "尺寸不合适(1)；Crew Cab/Short Bed(14)"


def test_years_are_merged_and_compressed_across_structures():
    keys = [key()]
    negative = [
        {"品牌": "Ford", "车型": "Focus", "结构": "Sedan", "年份": "1995,1996"},
        {"品牌": "Ford", "车型": "Focus", "结构": "Coupe", "年份": "1997,2026"},
    ]
    scored, _ = scoring_mod.score_keys(keys, negative, [])
    assert scored[0]["年份"] == "95-97/26"


def test_format_years_groups_consecutive_runs():
    assert scoring_mod.format_years({1995, 1996, 1997, 2026}) == "95-97/26"
    assert scoring_mod.format_years(set()) == ""
    assert scoring_mod.format_years({2004}) == "04"


def test_bucket_level_thresholds():
    rules = scoring_mod.DEFAULT_RULES
    assert scoring_mod.bucket_level(0.1, rules["thresholds"]) == "低"
    assert scoring_mod.bucket_level(0.5, rules["thresholds"]) == "中"
    assert scoring_mod.bucket_level(0.9, rules["thresholds"]) == "高"
    assert scoring_mod.bucket_level(None, rules["thresholds"]) == "数据不足"
