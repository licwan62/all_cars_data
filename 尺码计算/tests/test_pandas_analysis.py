from __future__ import annotations

import csv
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


class FullPipelineRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.input_dir = PROJECT_DIR / "input"
        cls.submodel_path = analysis.resolve_submodel_path(cls.input_dir, None, False)
        cls.result = analysis.calculate(cls.input_dir, cls.submodel_path)

    @staticmethod
    def _read_legacy_example(path: Path) -> pd.DataFrame:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        header = [column.strip() for column in rows[0]]
        repaired: list[list[str]] = []
        for row in rows[1:]:
            # 旧文件的销量千分位逗号没有加引号：14 个前置列 + 销量 + 10 个后置列。
            sales = "".join(row[14:-10]).strip().replace(",", "")
            repaired.append(row[:14] + [sales] + row[-10:])
        return pd.DataFrame(repaired, columns=header)

    def test_full_result_contract(self) -> None:
        summary = analysis.validate_result(self.result, 4354)
        self.assertEqual(summary["unique_dimension_ids"], 4354)
        self.assertEqual(summary["matched_sizes"], 4099)
        self.assertEqual(summary["unavailable_sizes"], 251)
        self.assertEqual(summary["incomplete_rows"], 4)
        self.assertEqual(summary["sales_total"], 671987183)

        dimension_id = "MAKE=Chevrolet|MODEL=Bel Air|VERSION=|STRUCTURE=Coupe|YEAR=1960"
        row = self.result.set_index("DIMENSION-ID").loc[dimension_id]
        self.assertEqual(row["TRIM"], "Bel Air")
        self.assertEqual(row["销量合计"], 74286)
        self.assertEqual(row["前宽-MM"], 2031)
        self.assertEqual(row["参考插片"], 266)
        self.assertEqual(row["自动尺码"], "3WXXL-0")
        self.assertEqual(row["自动长度余量"], 146)
        self.assertEqual(self.result.columns[-1], "DIMENSION-ID")
        self.assertTrue(self.result["DIMENSION-ID"].is_monotonic_increasing)
        self.assertFalse(self.result["TRIM"].str.contains("|", regex=False).any())
        self.assertFalse(self.result["TRIM"].str.contains("-", regex=False).any())

    def test_business_results_match_legacy_example(self) -> None:
        legacy = self._read_legacy_example(PROJECT_DIR / "example_output.csv")
        current = self.result.copy()
        joined = current.merge(
            legacy,
            on="DIMENSION-ID",
            suffixes=("_current", "_legacy"),
            validate="one_to_one",
        )
        self.assertEqual(len(joined), 4354)

        for column in ["自动尺码", "自动长度余量", "候选", "原因"]:
            current_values = joined[f"{column}_current"].fillna("").astype(str).str.strip()
            legacy_values = joined[f"{column}_legacy"].fillna("").astype(str).str.strip()
            self.assertTrue(current_values.equals(legacy_values), column)

        for column in ["前宽-MM", "后宽-MM", "参考侧高", "参考插片"]:
            current_values = pd.to_numeric(joined[f"{column}_current"], errors="coerce")
            legacy_values = pd.to_numeric(joined[f"{column}_legacy"], errors="coerce")
            difference = (current_values - legacy_values).abs().dropna()
            self.assertLessEqual(float(difference.max()), 1.0, column)

        current_sales = pd.to_numeric(joined["销量合计_current"], errors="coerce").fillna(0)
        legacy_sales = pd.to_numeric(
            joined["销量合计_legacy"].replace({"-": "0", "": "0"}), errors="coerce"
        ).fillna(0)
        self.assertTrue((current_sales.to_numpy() == legacy_sales.to_numpy()).all())


if __name__ == "__main__":
    unittest.main()
