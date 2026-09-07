from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "analyze_legacy_sizes.py"
SPEC = importlib.util.spec_from_file_location("analyze_legacy_sizes", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
legacy = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = legacy
SPEC.loader.exec_module(legacy)


def rule(line: int, size: str, seq: int, category: str, cover_hp: float):
    return legacy.Rule(line, size, "", seq, category, "", "", size, 400, cover_hp)


class LegacyHalfPerimeterTests(unittest.TestCase):
    def setUp(self):
        self.parameters = legacy.Parameters(100, 635)

    def test_cover_half_perimeter_converts_cm_and_adds_allowance(self):
        model, side_length, half_perimeter = legacy.resolve_cover_size("3S-0", {"3S-0": 428})
        self.assertEqual("3S-0", model)
        self.assertEqual(428, side_length)
        self.assertEqual(5780, half_perimeter)

    def test_explicit_and_suffix_aliases_are_supported(self):
        cover = {"3XL+-0": 520, "3XXL": 540}
        self.assertEqual("3XL+-0", legacy.resolve_cover_size("3XL+0", cover)[0])
        self.assertEqual("3XXL", legacy.resolve_cover_size("3XXL-0", cover)[0])

    def test_record_half_perimeter_uses_length_plus_height_in_inches(self):
        value = legacy.record_half_perimeter_mm({"L-IN": "190", "H-IN": "55"})
        self.assertEqual(6223, value)

    def test_strict_boundaries_do_not_enter_pool(self):
        pools = legacy.build_pools(
            [
                rule(2, "AT_LOWER", 1, "跑车", 6323),
                rule(3, "AT_UPPER", 2, "跑车", 6858),
            ]
        )
        result = legacy.match_vehicle(
            {"分类": "跑车", "L-IN": "190", "H-IN": "55"}, pools, self.parameters
        )
        self.assertEqual("无可用尺码", result["匹配状态"])

    def test_smallest_sequence_in_same_category_wins(self):
        pools = legacy.build_pools(
            [
                rule(2, "LATE", 20, "三厢车", 6600),
                rule(3, "FIRST", 10, "三厢车", 6500),
                rule(4, "OTHER_CATEGORY", 1, "跑车", 6500),
            ]
        )
        result = legacy.match_vehicle(
            {"分类": "三厢车", "L-IN": "190", "H-IN": "55"}, pools, self.parameters
        )
        self.assertEqual("已匹配", result["匹配状态"])
        self.assertEqual("FIRST", result["内部尺码"])
        self.assertIn("LATE", result["入池候选"])

    def test_incomplete_dimensions_are_not_forced(self):
        result = legacy.match_vehicle(
            {"分类": "三厢车", "L-IN": "", "H-IN": "55"},
            legacy.build_pools([rule(2, "SIZE", 1, "三厢车", 6500)]),
            self.parameters,
        )
        self.assertEqual("数据不全", result["匹配状态"])


if __name__ == "__main__":
    unittest.main()
