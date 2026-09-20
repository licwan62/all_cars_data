from __future__ import annotations

import unittest

from src.fitment_coverage import build_fitment_coverage


def dimension(
    dimension_id: str,
    model: str,
    year: str,
    version: str = "",
    structure: str = "SUV",
) -> dict[str, str]:
    return {
        "DIMENSION-ID": dimension_id,
        "MAKE": "Acura",
        "MODEL": model,
        "版本": version,
        "结构": structure,
        "YEAR": year,
        "CAB": "",
        "BED": "",
    }


class FitmentCoverageTests(unittest.TestCase):
    def test_every_4a_atom_receives_attempt_status(self) -> None:
        fitment_rows = [
            {"year": "2020", "make": "Acura", "model": "ADX"},
            {"year": "2020", "make": "Acura", "model": "ZDX"},
            {"year": "2020", "make": "Acura", "model": "ADX Type S"},
            {"year": "2020", "make": "Other", "model": "Unknown"},
        ]
        dimensions = [
            dimension("D1", "ADX", "2020"),
            dimension("D2", "ZDX", "2020"),
            dimension("D3", "ADX Type", "2020", version="S"),
        ]
        trim_rows = [
            {"DIMENSION-ID": "D1", "Year": "2020", "Make": "Acura", "Model": "ADX"}
        ]
        review_rows = [
            {
                "DIMENSION-ID": "D2",
                "Year": "2020",
                "候选Make": "Acura",
                "候选Model": "ZDX",
            }
        ]
        result = build_fitment_coverage(
            fitment_rows, dimensions, trim_rows, review_rows
        )
        statuses = {row["Model"]: row["尝试状态"] for row in result.coverage_rows}
        self.assertEqual(statuses["ADX"], "MATCHED")
        self.assertEqual(statuses["ZDX"], "ONLINE_REVIEW_ATTEMPTED")
        self.assertEqual(statuses["ADX Type S"], "SEMANTIC_CANDIDATE_ATTEMPTED")
        self.assertEqual(statuses["Unknown"], "ATTEMPTED_NO_DIMENSION_CANDIDATE")
        self.assertEqual(result.report["counts"]["unattempted_4a_atoms"], 0)


if __name__ == "__main__":
    unittest.main()
