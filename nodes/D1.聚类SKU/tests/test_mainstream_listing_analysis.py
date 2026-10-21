from pathlib import Path
import importlib.util

import pandas as pd
import pytest


SPEC = importlib.util.spec_from_file_location("mainstream_listing_analysis", Path(__file__).resolve().parents[1] / "src" / "mainstream_listing_analysis.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_integer_allocation_conserves_budget_and_ties():
    assert MODULE.largest_remainder([1, 1, 1], 800).tolist() == [267, 267, 266]
    assert MODULE.largest_remainder([0, 1, 3], 800).tolist() == [0, 200, 600]
    with pytest.raises(ValueError):
        MODULE.largest_remainder([0, 0], 800)
    with pytest.raises(ValueError):
        MODULE.largest_remainder([1, -1], 800)


def test_year_compaction_preserves_gaps():
    assert MODULE.compact_years([2020, 2017, 2018, 2022, 2022]) == "2017-2018/2020/2022"
    with pytest.raises(ValueError):
        MODULE.parse_years("2025-2020")


def test_holds_do_not_absorb_shipment_budget():
    candidates = pd.DataFrame({"候选状态": ["暂缓", "可参与试算", "可参与试算"],
                               "近期销量估值": [10000, 300, 100]})
    selected = MODULE.select_portfolio(candidates, 2, 800)
    assert selected["800件试算分配"].tolist() == [600, 200]
    assert not selected["候选状态"].eq("暂缓").any()


def test_source_mismatch_is_not_silently_zero_filled():
    full = pd.DataFrame({"DIMENSION-ID": ["dimension-one"]})
    sales = pd.DataFrame({"atom_record_id": ["other|ATOM_YEAR=2020"], "预估销量": [10]})
    with pytest.raises(ValueError, match="未完全对齐"):
        MODULE.prepare(full, sales, {}, {"ranking_years": [2020, 2025], "reference_years": [2010, 2025]}, {})


def test_scope_excludes_current_w_and_legacy_dedicated_but_not_wagon():
    import json
    config = json.loads(MODULE.CONFIG_PATH.read_text(encoding="utf-8"))
    w_config = json.loads((MODULE.PROJECT / "data" / "W型车目标尺码.json").read_text(encoding="utf-8"))
    rows = []
    for i, (make, model, structure, size, year) in enumerate([
        ("Ford", "Truck", "Pickup", "PK-S", "2020"),
        ("Buick", "Classic", "Sedan", "4M-0", "2020"),
        ("Tesla", "Model X", "SUV", "YL", "2020"),
        ("Dodge", "Challenger", "Coupe", "3XL-0", "2020"),
        ("Chevrolet", "Bel Air", "Sedan", "3XL", "1957"),
        ("Chevrolet", "Bel Air", "Wagon", "5L", "1957"),
        ("Toyota", "Camry", "Sedan", "3XL", "2020"),
    ]):
        rows.append({"DIMENSION-ID": str(i), "MAKE": make, "MODEL": model, "版本": "", "结构": structure,
                     "分类": "皮卡" if structure == "Pickup" else "三厢车", "YEAR": year, "SHAPE": "TEST",
                     "自动尺码": size, "L-MM": 4000, "W-MM": 1800, "H-MM": 1500,
                     "自动长度余量": 100, "尺寸组销量": 10})
    sales = pd.DataFrame({"atom_record_id": [f"{i}|ATOM_YEAR={row['YEAR']}" for i, row in enumerate(rows)], "预估销量": [10] * len(rows)})
    rules = {"rules": [{"尺码": row["自动尺码"]} for row in rows]}
    full, _ = MODULE.prepare(pd.DataFrame(rows), sales, rules, config, w_config)
    assert full["范围判定"].tolist() == ["排除皮卡", "排除W范围", "排除W范围", "排除W范围", "排除W范围", "范围内", "范围内"]


def test_missing_sales_outside_period_are_preserved_but_inside_period_stop():
    import json
    config = json.loads(MODULE.CONFIG_PATH.read_text(encoding="utf-8"))
    w_config = json.loads((MODULE.PROJECT / "data" / "W型车目标尺码.json").read_text(encoding="utf-8"))
    full = pd.DataFrame([{"DIMENSION-ID": "one", "MAKE": "Test", "MODEL": "Car", "版本": "",
                          "结构": "Sedan", "分类": "三厢车", "YEAR": "2020-2027", "SHAPE": "STANDARD_SEDAN",
                          "自动尺码": "3XL", "L-MM": 4900, "W-MM": 1800, "H-MM": 1500,
                          "自动长度余量": 150, "尺寸组销量": 10}])
    sales = pd.DataFrame({"atom_record_id": ["one|ATOM_YEAR=2020", "one|ATOM_YEAR=2027"],
                          "预估销量": [10, float("nan")]})
    prepared, atoms = MODULE.prepare(full, sales, {"rules": [{"尺码": "3XL"}]}, config, w_config)
    assert prepared["近期销量估值"].item() == 10
    assert prepared["期外缺失年度数"].item() == 1
    assert atoms.loc[atoms["ATOM_YEAR"].eq(2027), "预估销量"].isna().all()
    sales.loc[1, "atom_record_id"] = "one|ATOM_YEAR=2021"
    with pytest.raises(ValueError, match="分析期销量存在缺失"):
        MODULE.prepare(full, sales, {"rules": [{"尺码": "3XL"}]}, config, w_config)
