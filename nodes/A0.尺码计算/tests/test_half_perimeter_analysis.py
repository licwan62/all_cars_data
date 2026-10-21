from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


TEST_PROJECT_DIR = Path(__file__).resolve().parents[1] / "src"
if str(TEST_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PROJECT_DIR))

import half_perimeter_analysis as analysis  # noqa: E402


class EquivalentLengthFormulaTests(unittest.TestCase):
    def test_formula_uses_length_width_coefficient_and_offset(self) -> None:
        vehicles = pd.DataFrame(
            [{"车形": "SD1", "L-MM": 4549, "W-MM": 1412}]
        )
        references = pd.DataFrame(
            [{"车身号": "SD1", "周长系数": "0.93"}]
        )

        row = analysis.add_equivalent_length(vehicles, references).iloc[0]

        self.assertEqual(row["等效长"], 4794)

    def test_rule_file_order_breaks_ties_and_ignores_legacy_order_number(self) -> None:
        # README：长上限与插片指数上限都相同时按规则文件顺序取第一个，历史 档位序号 不参与排序。
        parameters = pd.DataFrame([{"参数": "余量长容差", "值": "500"}])
        rules = pd.DataFrame(
            [
                {
                    "内部尺码": "LATE",
                    "档位序号": 20,
                    "分类": "三厢车",
                    "CAB": "",
                    "版本": "",
                    "等效长上限": 5000,
                    "插片指数上限": 120,
                    "使用": "y",
                },
                {
                    "内部尺码": "FIRST",
                    "档位序号": 10,
                    "分类": "三厢车",
                    "CAB": "",
                    "版本": "",
                    "等效长上限": 5000,
                    "插片指数上限": 120,
                    "使用": "y",
                },
            ]
        )
        matcher = analysis.base.SizeMatcher(parameters, rules, limits=analysis.TEST_LIMITS)

        result = matcher.match("三厢车", "", "", [4800, 100])

        self.assertEqual(result.auto_size, "LATE")


if __name__ == "__main__":
    unittest.main()
