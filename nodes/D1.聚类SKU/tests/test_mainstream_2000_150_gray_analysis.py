from pathlib import Path
import importlib.util

import pandas as pd


SPEC = importlib.util.spec_from_file_location("mainstream2000", Path(__file__).resolve().parents[1] / "src" / "mainstream_2000_150_gray_analysis.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_sku_grain_is_model_year_interval_and_supply_size():
    frame = pd.DataFrame([
        {"MAKE": "A", "MODEL": "B", "YEAR": "2020-2022", "供货尺码": "M", "范围判定": "范围内", "尺码销量总和": 30,
         "源行ID": "1", "CODE": 1, "VERSION": "Base", "CONST": "Sedan", "BACKSIZE": "S", "灰度调整": True},
        {"MAKE": "A", "MODEL": "B", "YEAR": "2020-2022", "供货尺码": "M", "范围判定": "范围内", "尺码销量总和": 70,
         "源行ID": "2", "CODE": 2, "VERSION": "Sport", "CONST": "Sedan", "BACKSIZE": "M", "灰度调整": False},
    ])
    config = {"sku_keys": ["MAKE", "MODEL", "YEAR", "供货尺码"], "portfolio_sku_count": 1, "shipment_budget": 20,
              "max_units_per_sku": 25}
    candidates, selected = MODULE.build_skus(frame, config)
    assert len(candidates) == 1
    assert candidates["销量权重"].item() == 100
    assert selected["建议发货件数"].item() == 20


def test_year_interval_is_not_merged():
    rows = []
    for number, year in enumerate(["2020-2021", "2022-2023"], 1):
        rows.append({"MAKE": "A", "MODEL": "B", "YEAR": year, "供货尺码": "M", "范围判定": "范围内",
                     "尺码销量总和": 10, "源行ID": str(number), "CODE": number, "VERSION": "", "CONST": "Sedan",
                     "BACKSIZE": "M", "灰度调整": False})
    config = {"sku_keys": ["MAKE", "MODEL", "YEAR", "供货尺码"], "portfolio_sku_count": 2, "shipment_budget": 20,
              "max_units_per_sku": 25}
    candidates, _ = MODULE.build_skus(pd.DataFrame(rows), config)
    assert candidates["YEAR"].tolist() == ["2020-2021", "2022-2023"]


def test_capped_allocation_conserves_budget_and_limit():
    result = MODULE.capped_largest_remainder([100, 50, 25, 10], 70, 25)
    assert result.sum() == 70
    assert result.max() <= 25
    assert result.tolist() == [25, 25, 16, 4]


def test_capped_allocation_rejects_impossible_budget():
    import pytest
    with pytest.raises(ValueError, match="超过"):
        MODULE.capped_largest_remainder([1, 1], 51, 25)
