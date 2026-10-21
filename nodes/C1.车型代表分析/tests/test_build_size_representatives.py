import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "src" / "build_size_representatives.py"
SPEC = importlib.util.spec_from_file_location("build_size_representatives", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CompressedCandidateTests(unittest.TestCase):
    def test_year_overlap(self):
        self.assertTrue(MODULE.overlaps("2014-2026", "2025-2026"))
        self.assertFalse(MODULE.overlaps("1965-1973", "2025-2026"))

    def test_combined_structure_matches(self):
        self.assertTrue(MODULE.structure_matches("Convertible/Targa", "Targa"))
        self.assertFalse(MODULE.structure_matches("Convertible/Targa", "Coupe"))

    def test_incl_version_matches(self):
        self.assertTrue(MODULE.version_matches("Incl: Dakar", "Dakar"))
        self.assertTrue(MODULE.version_matches("GT2/GT3", "GT3"))


class RankGroupTests(unittest.TestCase):
    def test_ranking_uses_length_sales_and_year_without_equivalent_length(self):
        rows = [
            {"DIMENSION-ID": "short", "L-MM": "4000", "YEAR": "2020-2024", "尺寸组销量": "100"},
            {"DIMENSION-ID": "long", "L-MM": "4500", "YEAR": "2020-2024", "尺寸组销量": "100"},
        ]
        ranked = MODULE.rank_group(rows)
        self.assertEqual([row["DIMENSION-ID"] for row in ranked], ["long", "short"])
        self.assertNotIn("参考半周长", MODULE.OUTPUT_FIELDS)


if __name__ == "__main__":
    unittest.main()
