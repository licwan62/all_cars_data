from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MODULE = PROJECT / "src" / "build_size_analysis_summary.py"
SPEC = importlib.util.spec_from_file_location("size_summary", MODULE)
assert SPEC and SPEC.loader
size_summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(size_summary)


RULES = {
    "main_size_signals": ["尺寸不合适", "太小", "does not fit", "too small"],
    "main_cover_signals": ["车罩", "cover", "保险杠"],
    "accessory_only_signals": ["收纳袋", "遮阳挡", "拉链"],
    "size_direction": {
        "偏小": ["太小", "too small"],
        "偏大": ["太大"],
        "尺寸或版型不符": ["尺寸不合适", "does not fit"],
    },
}


def test_selects_main_cover_size_complaint_and_direction():
    row = {"英文": "Cover does not fit. Too small for my car.", "翻译": "", "差评点": "尺寸不合适，偏小"}
    result = size_summary.select_row(row, RULES)
    assert result and result[0] == "车辆主体尺寸不合适"
    assert result[1] == "偏小"
    assert "英文" in result[2] and "差评点" in result[2]


def test_excludes_accessory_only_size_complaint():
    row = {"英文": "", "翻译": "遮阳挡太小", "差评点": "遮阳挡尺寸不合适"}
    assert size_summary.select_row(row, RULES) is None


def test_excludes_accessory_size_when_cover_is_only_mentioned_elsewhere():
    row = {"英文": "The cover looks fine.", "翻译": "", "差评点": "保护泡沫板太小"}
    assert size_summary.select_row(row, RULES) is None


def test_description_is_concise_and_keeps_the_main_fit_problem():
    row = {"英文": "Cover does not fit; mirrors do not align and it is too short.", "翻译": ""}
    description = size_summary.describe_size_issue(row, "偏小")
    assert description == "车罩偏短，无法完整覆盖，后视镜位不对"
    assert len(description) <= 50


def test_semantic_classification_recovers_vehicle_fit_without_cover_keyword():
    row = {"英文": "Does NOT fit a 2024 MB GLC SUV. Way too small", "车型": "Mercedes GLC"}
    assert size_summary.semantic_classification(row, RULES) == ("车辆主体车罩", "英文明确描述车辆适配或尺寸问题")


def test_semantic_classification_routes_sunshade_to_review():
    row = {"英文": "This sun shade did not fit my vehicle.", "车型": "Toyota 4Runner"}
    assert size_summary.semantic_classification(row, RULES)[0] == "配件尺寸问题"
