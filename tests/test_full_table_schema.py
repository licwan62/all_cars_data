from __future__ import annotations

import unittest

import pandas as pd

from full_table_schema import SIZE_MATCH_COLUMNS, build_dimension_analysis


class FullTableSchemaTests(unittest.TestCase):
    def test_analysis_removes_only_size_match_columns(self) -> None:
        row = {
            "MAKE": "Acura",
            "等效长": 4569,
            "自动尺码": "YL",
            "自动长度余量": 131,
            "候选": "",
            "原因": "",
            "相差数值": "",
            "DIMENSION-ID": "Acura ADX SUV 2025-2026 US",
        }
        analysis = build_dimension_analysis(pd.DataFrame([row]))
        self.assertEqual(list(analysis.columns), ["MAKE", "等效长", "DIMENSION-ID"])
        self.assertTrue(all(column not in analysis.columns for column in SIZE_MATCH_COLUMNS))
        self.assertEqual(analysis.iloc[0]["DIMENSION-ID"], row["DIMENSION-ID"])


if __name__ == "__main__":
    unittest.main()
