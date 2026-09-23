from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "code" / "build_structure_review.py"
SPEC = importlib.util.spec_from_file_location("build_structure_review", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

STANDARD = module.load_standard()


def row(structure: str, category: str, make="X", model="Y", year="2010-2012", rid=None) -> dict[str, str]:
    base = {field: "" for field in module.FIELDS}
    base.update({"DIMENSION-ID": rid or f"{make} {model} {structure} {year}", "MAKE": make, "MODEL": model,
                 "结构": structure, "YEAR": year, "分类": category})
    return base


@pytest.mark.parametrize("structure,expected", [
    ("Wagon", "两厢车"), ("Wagon 5dr", "两厢车"), ("Van", "两厢车"), ("MPV", "两厢车"), ("Bus", "两厢车"),
    ("Sedan 2dr", "三厢车"), ("Hatchback 4dr", "两厢车"), ("Chassis Cab", "皮卡"), ("SUV", "越野车"),
])
def test_fixed_standard_is_region_independent(structure, expected):
    for region in module.REGIONS:
        category, rule, _ = module.classify(region, row(structure, "三厢车"), STANDARD, [])
        assert category == expected
        assert rule.startswith("通用标准")


def test_excluded_structures_get_blank_category():
    category, rule, _ = module.classify("EU", row("Sattelschlepper", ""), STANDARD, [])
    assert category == "" and rule.startswith("排除")


def test_unresearched_liftback_keeps_upstream_and_is_queued():
    rows = {"US": [], "EU": [row("Liftback", "两厢车")], "RU": []}
    result = module.review(rows, STANDARD, [])
    assert result["outputs"]["EU"][0]["分类"] == "两厢车"
    assert len(result["queue"]) == 1 and result["queue"][0]["结构"] == "Liftback"


def test_research_decision_applies_with_year_limit():
    decisions = [
        {"区域": "EU", "MAKE": "Toyota", "MODEL": "Corolla", "结构": "Liftback", "YEAR": "1976-1980", "分类": "跑车",
         "依据": "三门", "来源URL": "https://example.com/a", "核实日期": "2026-09-23"},
        {"区域": "EU", "MAKE": "Toyota", "MODEL": "Corolla", "结构": "Liftback", "YEAR": "1987-2002", "分类": "三厢车",
         "依据": "五门", "来源URL": "https://example.com/b", "核实日期": "2026-09-23"},
    ]
    old = row("Liftback", "跑车", "Toyota", "Corolla", "1976-1980")
    new = row("Liftback", "跑车", "Toyota", "Corolla", "1992-1997")
    assert module.classify("EU", old, STANDARD, decisions)[0] == "跑车"
    assert module.classify("EU", new, STANDARD, decisions)[0] == "三厢车"
    assert module.classify("US", new, STANDARD, decisions)[0] == "跑车"


def test_unknown_structure_fails():
    with pytest.raises(module.ReviewError):
        module.classify("EU", row("Spaceship", "两厢车"), STANDARD, [])


def test_validate_only_changes_category():
    source = {"US": [row("Wagon", "三厢车")], "EU": [], "RU": []}
    result = module.review(source, STANDARD, [])
    assert module.validate(result, source, STANDARD)["passed"]
    result["outputs"]["US"][0]["YEAR"] = "1999"
    assert not module.validate(result, source, STANDARD)["passed"]


def test_decision_file_is_valid():
    decisions = module.load_decisions()
    for decision in decisions:
        family = decision["结构"]
        assert decision["分类"] in STANDARD["research_required"][family]
