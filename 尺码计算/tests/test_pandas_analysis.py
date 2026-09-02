from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import pandas_analysis as analysis  # noqa: E402


class SizeMatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = pd.DataFrame([{"参数": "余量长容差", "值": "500"}])

    def test_drw_pool_and_sedan_length_fallback(self) -> None:
        rules = pd.DataFrame(
            [
                {
                    "内部尺码": "SEDAN",
                    "档位序号": "1",
                    "分类": "三厢车",
                    "CAB": "",
                    "版本": "",
                    "长上限": "5000",
                    "参考插片上限": "120",
                    "使用": "y",
                },
                {
                    "内部尺码": "SPORT",
                    "档位序号": "2",
                    "分类": "跑车",
                    "CAB": "",
                    "版本": "",
                    "长上限": "6000",
                    "参考插片上限": "120",
                    "使用": "y",
                },
                {
                    "内部尺码": "PK-W",
                    "档位序号": "3",
                    "分类": "皮卡",
                    "CAB": "",
                    "版本": "DRW",
                    "长上限": "6000",
                    "参考插片上限": "999",
                    "使用": "y",
                },
            ]
        )
        matcher = analysis.SizeMatcher(self.parameters, rules)

        sedan = matcher.match("三厢车", "", "", [5500, 100])
        self.assertEqual(sedan.auto_size, "SPORT")
        self.assertEqual(sedan.length_margin, 500)

        drw = matcher.match("皮卡", "Crew", "Classic DRW", [5700, 200])
        self.assertEqual(drw.auto_size, "PK-W")
        self.assertEqual(drw.length_margin, 300)

    def test_incomplete_and_nearest_reasons(self) -> None:
        rules = pd.DataFrame(
            [
                {
                    "内部尺码": "ONLY",
                    "档位序号": "1",
                    "分类": "两厢车",
                    "CAB": "",
                    "版本": "",
                    "长上限": "4000",
                    "参考插片上限": "120",
                    "使用": "y",
                }
            ]
        )
        matcher = analysis.SizeMatcher(self.parameters, rules)

        incomplete = matcher.match("两厢车", "", "", [None, 100])
        self.assertEqual(incomplete.auto_size, "数据不全")

        too_long = matcher.match("两厢车", "", "", [4100, 150])
        self.assertEqual(too_long.auto_size, "无可用尺码")
        self.assertEqual(too_long.candidate, "ONLY")
        self.assertEqual(too_long.reason, "超长")
        self.assertEqual(too_long.difference, 100)

        too_loose = matcher.match("两厢车", "", "", [3000, 100])
        self.assertEqual(too_loose.reason, "超余量")
        self.assertEqual(too_loose.difference, 1000)

    def test_trim_format_removes_brand_hyphen_and_spaces(self) -> None:
        value = analysis._format_trim_candidates(
            ["Jaguar|XF", "Jaguar|XFR", "Jaguar|XFR-S"]
        )
        self.assertEqual(value, "XF,XFR,XFRS")


class BodyDimensionFormulaTests(unittest.TestCase):
    def test_new_arc_formula_and_insert_ignore_neck_width(self) -> None:
        vehicles = pd.DataFrame(
            [{"DIMENSION-ID": "Acura ADX SUV 2025-2026", "W-MM": 1842, "H-MM": 1621}]
        )
        bodies = pd.DataFrame(
            [{"DIMENSION-ID": "Acura ADX SUV 2025-2026", "车形": "SU1"}]
        )
        references = pd.DataFrame(
            [
                {
                    "车身号": "SU1",
                    "前宽系数": "0.7318",
                    "后宽系数": "0.7457",
                    # 特意设得很大：新规则不得把车颈等效宽并入参考插片。
                    "颈宽系数": "0.99",
                    "弧长系数": "0.81",
                }
            ]
        )

        row = analysis.add_body_dimensions(vehicles, bodies, references).iloc[0]

        self.assertEqual(row["前宽-MM"], 1348)
        self.assertEqual(row["后宽-MM"], 1374)
        self.assertEqual(row["参考侧高"], 1309)
        self.assertEqual(row["参考插片"], -70)


class FullPipelineRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_dir = PROJECT_DIR.parent / "source"
        cls.config_dir = PROJECT_DIR / "rules"
        cls.submodel_path = analysis.resolve_submodel_path(cls.source_dir, None, False)
        cls.result = analysis.calculate(
            cls.source_dir,
            cls.submodel_path,
            config_dir=cls.config_dir,
        )

    def test_full_result_contract(self) -> None:
        summary = analysis.validate_result(self.result, 4354)
        self.assertEqual(summary["unique_dimension_ids"], 4354)
        self.assertEqual(summary["matched_sizes"], 4119)
        self.assertEqual(summary["unavailable_sizes"], 162)
        self.assertEqual(summary["incomplete_rows"], 73)
        self.assertEqual(summary["sales_total"], 671987183)

        dimension_id = "Chevrolet Bel Air Coupe 1960"
        row = self.result.set_index("DIMENSION-ID").loc[dimension_id]
        self.assertEqual(row["TRIM"], "Bel Air")
        self.assertEqual(row["销量合计"], 74286)
        self.assertEqual(row["前宽-MM"], 2052)
        self.assertEqual(row["参考插片"], 276)
        self.assertEqual(row["自动尺码"], "3WXXL-0")
        self.assertEqual(row["自动长度余量"], 146)
        self.assertEqual(self.result.columns[-1], "DIMENSION-ID")
        self.assertTrue(self.result["DIMENSION-ID"].is_monotonic_increasing)
        self.assertFalse(self.result["TRIM"].str.contains("|", regex=False).any())
        self.assertFalse(self.result["TRIM"].str.contains("-", regex=False).any())
        self.assertTrue(
            self.result.loc[self.result["车形"].eq("V1"), "自动尺码"].eq("数据不全").all()
        )

    def test_acura_adx_uses_su1_formula(self) -> None:
        row = self.result.set_index("DIMENSION-ID").loc["Acura ADX SUV 2025-2026"]
        self.assertEqual(row["车形"], "SU1")
        self.assertEqual(row["W-MM"], 1842)
        self.assertEqual(row["H-MM"], 1621)
        self.assertEqual(row["参考侧高"], 1309)


if __name__ == "__main__":
    unittest.main()
