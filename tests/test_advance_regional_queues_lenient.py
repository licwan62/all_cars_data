import importlib.util
from pathlib import Path
import unittest


PATH = Path(__file__).resolve().parents[1] / "scripts" / "advance_regional_queues_lenient.py"
SPEC = importlib.util.spec_from_file_location("advance_regional_queues_lenient", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class LenientRegionalQueueTests(unittest.TestCase):
    def test_one_shape_accepts_only_unambiguous_value(self):
        self.assertEqual(MODULE.one_shape("SU1"), "SU1")
        self.assertEqual(MODULE.one_shape("SU1; SU1"), "SU1")
        self.assertEqual(MODULE.one_shape("SU1; SD1"), "")
        self.assertEqual(MODULE.one_shape(""), "")

    def test_loose_shape_keeps_existing_before_using_proxy(self):
        self.assertEqual(MODULE.loose_shape({"当前车形": "SU1", "结构": "Coupe", "分类": "跑车"})[:2], ("SU1", "medium"))
        self.assertEqual(MODULE.loose_shape({"当前车形": "", "结构": "Pickup", "分类": "皮卡"})[0], "P0")


if __name__ == "__main__":
    unittest.main()
