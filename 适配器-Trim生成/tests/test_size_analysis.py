from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.size_analysis import (
    build_size_analysis,
    build_size_analysis_files,
    load_size_source,
)


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
        "TRIM": model,
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
                        "TRIM",
                        "版本",
                        "结构",
                        "CAB",
                        "BED",
                        "YEAR",
                        "分类",
                    ]
                )
                + "\nD1,YL,Acura,ADX,ADX,,SUV,,,2025-2026,越野车\n",
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
        self.assertEqual(len(result.final_adapter_rows), 1)
        self.assertEqual(result.final_adapter_rows[0]["Size"], "无可用尺码")

    def test_final_adapter_backfills_every_trim_row(self) -> None:
        result = build_size_analysis(
            [trim("D1"), trim("D2")],
            [audit("D1"), audit("D2")],
            [size("D1", "YL"), size("D2", "无可用尺码")],
        )
        self.assertEqual(len(result.final_adapter_rows), 2)
        self.assertEqual(
            list(result.final_adapter_rows[0]),
            ["DIMENSION-ID", "Size", "Year", "Make", "Model"],
        )
        self.assertEqual(
            [row["Size"] for row in result.final_adapter_rows],
            ["YL", "无可用尺码"],
        )
        self.assertTrue(
            result.report["checks"]["final_adapter_matches_trim_rows"]
        )

    def test_dimension_trim_map_uses_trim_column_and_pipe_separator(self) -> None:
        size_row = size("D1", "YL")
        size_row["TRIM"] = "Santa Fe,Santa Fe Sport,Santa Fe XL"
        result = build_size_analysis(
            [trim("D1")],
            [audit("D1")],
            [size_row],
        )
        self.assertEqual(
            result.dimension_trim_rows,
            [
                {
                    "DIMENSION-ID": "D1",
                    "Trims": "Santa Fe | Santa Fe Sport | Santa Fe XL",
                }
            ],
        )

    def test_final_and_intermediate_outputs_use_separate_directories(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            trim_path = root / "TrimList.csv"
            audit_path = root / "TrimList_audit.csv"
            size_path = root / "尺码分析.csv"
            data_dir = root / "data"
            output_dir = root / "output"
            trim_path.write_text(
                "DIMENSION-ID,Year,Make,Model\nD1,2020,Acura,ADX\n",
                encoding="utf-8-sig",
            )
            audit_path.write_text(
                "DIMENSION-ID,Year,Make,Model,匹配方式,审核状态,证据URL\n"
                "D1,2020,Acura,ADX,继承现有精确键,现有精确键,\n",
                encoding="utf-8-sig",
            )
            size_path.write_text(
                "DIMENSION-ID,自动尺码,MAKE,MODEL,TRIM,版本,结构,CAB,BED,YEAR,分类\n"
                "D1,YL,Acura,ADX,ADX,,SUV,,,2020,越野车\n",
                encoding="utf-8-sig",
            )
            build_size_analysis_files(
                trim_path,
                audit_path,
                size_path,
                "尺码匹配",
                output_dir,
                data_dir,
            )
            self.assertEqual(
                {path.name for path in output_dir.iterdir()},
                {"适配器.csv", "DimensionTrimMap.csv"},
            )
            self.assertTrue((data_dir / "DimensionSizeMap.csv").exists())
            self.assertTrue((data_dir / "SizeAnalysisSummary.json").exists())

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
