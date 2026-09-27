import importlib.util
from pathlib import Path
import unittest


PATH = Path(__file__).resolve().parents[1] / "src" / "publish_eu_current_research.py"
SPEC = importlib.util.spec_from_file_location("publish_eu_current_research", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class PublishEuCurrentResearchTests(unittest.TestCase):
    def test_current_research_is_subset_without_trim_or_code(self):
        result, report = MODULE.build()
        self.assertEqual(len(result), report["published_rows"])
        self.assertLessEqual(len(result), report["eu_dimension_library_rows"])
        self.assertTrue(result["DIMENSION-ID"].is_unique)
        self.assertNotIn("DIMENSION-CODE", result.columns)
        self.assertNotIn("TRIM", result.columns)


if __name__ == "__main__":
    unittest.main()
