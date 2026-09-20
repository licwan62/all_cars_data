from __future__ import annotations

import importlib.util
import unittest
from decimal import Decimal
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "code" / "review_year_generation.py"
SPEC = importlib.util.spec_from_file_location("review_year_generation", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def row(year: str, length: str, generation: str = "gen1") -> dict[str, str]:
    return {
        "DIMENSION-ID": year,
        "MAKE": "Example",
        "MODEL": "Model",
        "版本": "",
        "CAB": "",
        "BED": "",
        "结构": "Sedan",
        "代际": generation,
        "YEAR": year,
        "分类": "三厢车",
        "L-IN": length,
        "W-IN": "70.0",
        "H-IN": "55.0",
        "参考车型": "",
        "备注": "",
        "迭代状态": "",
    }


class YearGenerationTests(unittest.TestCase):
    def test_contiguous_within_tolerance_merges(self) -> None:
        rows = [row("2000", "180.0"), row("2001-2002", "180.1")]
        self.assertEqual([[0, 1]], MODULE.find_merge_groups(rows, Decimal("0.1")))

    def test_tolerance_does_not_drift_across_chain(self) -> None:
        rows = [row("2000", "180.0"), row("2001", "180.1"), row("2002", "180.2")]
        self.assertEqual([[0, 1]], MODULE.find_merge_groups(rows, Decimal("0.1")))

    def test_generation_boundary_is_not_merged(self) -> None:
        rows = [row("2000", "180.0", "gen1"), row("2001", "180.0", "gen2")]
        self.assertEqual([], MODULE.find_merge_groups(rows, Decimal("0.1")))

    def test_one_year_same_generation_gap_is_high_priority(self) -> None:
        findings = MODULE.audit_gaps([row("2000", "180.0"), row("2002", "181.0")])
        self.assertEqual("2001", findings[0]["MISSING_YEAR"])
        self.assertEqual("HIGH", findings[0]["PRIORITY"])


if __name__ == "__main__":
    unittest.main()
