from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.size_analysis import build_size_analysis, load_size_source


def trim(dimension_id: str, year: int = 2020) -> dict[str, str]:
    return {
        "DIMENSION-ID": dimension_id,
        "Year": str(year),
        "Make": "Acura",
        "Model": "ADX",
    }


def audit(dimension_id: str, year: int = 2020) -> dict[str, str]:
    return {
        **trim(dimension_id, year),
        "匹配方式": "继承现有精确键",
        "审核状态": "现有精确键",
        "证据URL": "",
    }


def size(
    dimension_id: str,
    value: str,
    structure: str = "SUV",
    model: str = "ADX",
) -> dict[str, str]:
    return {
        "DIMENSION-ID": dimension_id,
        "自动尺码": value,
        "MAKE": "Acura",
        "MODEL": model,
        "版本": "",
        "结构": structure,
        "CAB": "",
        "BED": "",
        "YEAR": "2020",
        "分类": "越野车",
    }


class SizeAnalysisTests(unittest.TestCase):
    def test_load_size_source_from_canonical_csv(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "尺码分析.csv"
            path.write_text(
                ",".join(
                    [
                        "DIMENSION-ID",
                        "自动尺码",
                        "MAKE",
                        "MODEL",
                        "版本",
                        "结构",
                        "CAB",
                        "BED",
                        "YEAR",
                        "分类",
                    ]
                )
                + "\nD1,YL,Acura,ADX,,SUV,,,2025-2026,越野车\n",
                encoding="utf-8-sig",
            )
            self.assertEqual(load_size_source(path)[0]["自动尺码"], "YL")

    def test_same_size_multiple_dimensions_is_safe(self) -> None:
        result = build_size_analysis(
            [trim("D1"), trim("D2")],
            [audit("D1"), audit("D2")],
            [size("D1", "YL"), size("D2", "YL")],
        )
        self.assertEqual(result.report["counts"]["single_size_keys"], 1)
        self.assertEqual(result.report["counts"]["multi_size_expansion_keys"], 0)

    def test_multiple_sizes_creates_summary_and_detail(self) -> None:
        result = build_size_analysis(
            [trim("D1"), trim("D2")],
            [audit("D1"), audit("D2")],
            [size("D1", "YL"), size("D2", "YXL")],
        )
        self.assertEqual(len(result.multi_size_rows), 1)
        self.assertEqual(len(result.multi_size_detail_rows), 2)
        self.assertEqual(result.multi_size_rows[0]["Size数量"], 2)
        self.assertEqual(result.multi_size_rows[0]["发布判定"], "保留全部分支")

    def test_status_value_is_not_publishable_size(self) -> None:
        result = build_size_analysis(
            [trim("D1")],
            [audit("D1")],
            [size("D1", "无可用尺码")],
        )
        self.assertEqual(len(result.no_size_rows), 1)
        self.assertEqual(result.report["counts"]["single_size_keys"], 0)

    def test_multiple_structures_are_retained_as_expansion(self) -> None:
        result = build_size_analysis(
            [trim("D1"), trim("D2")],
            [audit("D1"), audit("D2")],
            [
                size("D1", "PK-L", structure="Pickup", model="C/K"),
                size("D2", "YXXL", structure="SUV", model="Suburban"),
            ],
        )
        expansion = result.multi_size_rows[0]
        self.assertIn("MULTI_STRUCTURE", expansion["展开类型"])
        self.assertIn("MULTI_SOURCE_MODEL", expansion["展开类型"])
        self.assertEqual(len(result.adapter_size_rows), 2)
        self.assertEqual(len(result.dimension_size_rows), 2)


if __name__ == "__main__":
    unittest.main()
