from pathlib import Path
import importlib.util

import pandas as pd


SPEC = importlib.util.spec_from_file_location("modern801", Path(__file__).resolve().parents[1] / "src" / "nonpickup_modern_801_analysis.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_largest_remainder_conserves_801():
    result = MODULE.largest_remainder([1, 1, 1], 801)
    assert result.tolist() == [267, 267, 267]
    assert result.sum() == 801


def test_exclusions_are_case_insensitive_and_version_specific():
    frame = pd.DataFrame({"MAKE": ["Ford", "Ford"], "MODEL": ["Bronco", "Bronco"], "VERSION": ["4dr", "Sport"]})
    rule = {"MAKE": "ford", "MODEL": "BRONCO", "VERSION_CONTAINS": "4DR"}
    assert MODULE.exclusion_mask(frame, rule).tolist() == [True, False]


def test_prepare_excludes_old_size_series_even_if_year_is_recent():
    config = {"min_fitment_year": 2010, "max_fitment_year": 2026, "exclude_size_prefixes": ["4"], "excluded_models": []}
    source = pd.DataFrame([{"CODE": 1, "MAKE": "Mercury", "MODEL": "Grand Marquis", "YEAR": "2010-2011", "VERSION": "",
                            "CONST": "Sedan", "BACKSIZE": "4L-0", "尺码销量总和": 1, "最大长-MM": 5000, "最小长-MM": 5000,
                            "最大宽-MM": 1800, "最小宽-MM": 1800, "最大高-MM": 1400, "最小高-MM": 1400}])
    rules = {"rules": [{"尺码": "4L-0", "尺码池": "S", "长上限": "5100"}]}
    result, _ = MODULE.prepare(source, config, rules)
    assert result["范围判定"].item() == "排除老车尺码系列"


def test_gray_matching_promotes_only_safe_adjacent_group():
    config = {"gray_match": {"identity_keys": ["MAKE", "MODEL", "VERSION", "CONST"], "max_year_gap": 1,
              "max_group_spread_mm": {"length": 50, "width": 50, "height": 50}, "adjacent_sizes_only": True,
              "target_length_margin_mm": {"min": 50, "max_exclusive": 500}}}
    rows = []
    for code, year, size, order, upper, length in [(1, 2020, "S", 0, 4500, 4490), (2, 2021, "M", 1, 4700, 4520)]:
        rows.append({"CODE": code, "MAKE": "A", "MODEL": "B", "VERSION": "", "CONST": "Sedan", "BACKSIZE": size,
                     "范围判定": "范围内", "尺码池": "P", "尺码序": order, "长上限": upper, "建议起始年": year, "建议结束年": year,
                     "最大长-MM": length, "最小长-MM": length, "最大宽-MM": 1800, "最小宽-MM": 1800,
                     "最大高-MM": 1450, "最小高-MM": 1450})
    result, audit = MODULE.apply_gray_matching(pd.DataFrame(rows), config)
    assert result["供货尺码"].tolist() == ["M", "M"]
    assert result["灰度调整"].tolist() == [True, False]
    assert audit["判定"].tolist() == ["通过"]

    rows[1]["最大高-MM"] = rows[1]["最小高-MM"] = 1510
    result, audit = MODULE.apply_gray_matching(pd.DataFrame(rows), config)
    assert result["供货尺码"].tolist() == ["S", "M"]
    assert audit["判定"].tolist() == ["拒绝"]
