from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


TEST_PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(TEST_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PROJECT_DIR))

import half_perimeter_analysis as analysis  # noqa: E402


class HalfPerimeterFormulaTests(unittest.TestCase):
    def test_formula_uses_length_height_coefficient_and_offset(self) -> None:
        vehicles = pd.DataFrame(
            [{"车形": "SD1", "L-MM": 4549, "H-MM": 1412}]
        )
        references = pd.DataFrame(
            [{"车身号": "SD1", "周长系数": "0.93"}]
        )

        row = analysis.add_reference_half_perimeter(vehicles, references).iloc[0]

        self.assertEqual(row["参考半周长"], 4794)

    def test_priority_is_preserved_when_more_than_one_size_fits(self) -> None:
        parameters = pd.DataFrame([{"参数": "余量长容差", "值": "500"}])
        rules = pd.DataFrame(
            [
                {
                    "内部尺码": "LATE",
                    "档位序号": 20,
                    "分类": "三厢车",
                    "CAB": "",
                    "版本": "",
                    "半周长上限": 5000,
                    "参考插片上限": 120,
                    "使用": "y",
                },
                {
                    "内部尺码": "FIRST",
                    "档位序号": 10,
                    "分类": "三厢车",
                    "CAB": "",
                    "版本": "",
                    "半周长上限": 5000,
                    "参考插片上限": 120,
                    "使用": "y",
                },
            ]
        )
        matcher = analysis.base.SizeMatcher(parameters, rules, limits=analysis.TEST_LIMITS)

        result = matcher.match("三厢车", "", "", [4800, 100])

        self.assertEqual(result.auto_size, "FIRST")


if __name__ == "__main__":
    unittest.main()
