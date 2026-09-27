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


if __name__ == "__main__":
    unittest.main()
