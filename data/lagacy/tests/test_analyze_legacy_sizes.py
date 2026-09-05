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


def rule(line: int, size: str, seq: int, cab: str, limits: tuple[float, float, float]):
    return legacy.Rule(line, size, "", seq, "皮卡", cab, *limits, "")


class LegacyMatchingTests(unittest.TestCase):
    def setUp(self):
        self.tolerances = legacy.Tolerances(0, 10, 11, 25)

    def test_smallest_sequence_fitting_rule_wins(self):
        rules = [rule(2, "S", 1, "", (200, 75, 70)), rule(3, "L", 2, "", (230, 80, 75))]
        result = legacy.match_vehicle(
            {"分类": "皮卡", "CAB": "Crew", "L-IN": "190", "W-IN": "74", "H-IN": "68"},
            legacy.build_pools(rules),
            self.tolerances,
        )
        self.assertEqual("已匹配", result["匹配状态"])
        self.assertEqual("S", result["内部尺码"])

    def test_exact_cab_pool_precedes_generic_and_can_fallback(self):
        rules = [
            rule(2, "GEN", 1, "", (260, 90, 80)),
            rule(3, "REG", 2, "Regular", (240, 80, 75)),
        ]
        pools = legacy.build_pools(rules)
        exact = legacy.match_vehicle(
            {"分类": "皮卡", "CAB": "Regular", "L-IN": "230", "W-IN": "79", "H-IN": "70"},
            pools,
            self.tolerances,
        )
        fallback = legacy.match_vehicle(
            {"分类": "皮卡", "CAB": "Regular", "L-IN": "250", "W-IN": "79", "H-IN": "70"},
            pools,
            self.tolerances,
        )
        self.assertEqual("REG", exact["内部尺码"])
        self.assertEqual("GEN", fallback["内部尺码"])

    def test_incomplete_dimensions_are_not_forced(self):
        result = legacy.match_vehicle(
            {"分类": "皮卡", "CAB": "", "L-IN": "", "W-IN": "79", "H-IN": "70"},
            legacy.build_pools([rule(2, "GEN", 1, "", (260, 90, 80))]),
            self.tolerances,
        )
        self.assertEqual("数据不全", result["匹配状态"])

    def test_shadowed_rule_is_detected(self):
        early = rule(2, "EARLY", 1, "", (220, 80, 75))
        late = rule(3, "LATE", 2, "", (220, 79, 74))
        shadows = legacy.find_shadowing([early, late], self.tolerances)
        self.assertEqual(early, shadows[late.line_no])

    def test_different_length_bands_are_not_fully_shadowed(self):
        early = rule(2, "EARLY", 1, "", (230, 80, 75))
        late = rule(3, "LATE", 2, "", (220, 79, 74))
        shadows = legacy.find_shadowing([early, late], self.tolerances)
        self.assertNotIn(late.line_no, shadows)

    def test_tolerance_boundaries_and_surplus_lower_bound(self):
        tolerances = legacy.Tolerances(2, 10, 11, 25)
        candidate = rule(2, "SIZE", 1, "", (200, 70, 60))
        pools = legacy.build_pools([candidate])
        upper_boundary = legacy.match_vehicle(
            {"分类": "皮卡", "CAB": "", "L-IN": "202", "W-IN": "80", "H-IN": "71"},
            pools,
            tolerances,
        )
        too_short = legacy.match_vehicle(
            {"分类": "皮卡", "CAB": "", "L-IN": "174.9", "W-IN": "70", "H-IN": "60"},
            pools,
            tolerances,
        )
        self.assertEqual("已匹配", upper_boundary["匹配状态"])
        self.assertEqual("无可用尺码", too_short["匹配状态"])
        self.assertEqual("超余量", too_short["匹配原因"])


if __name__ == "__main__":
    unittest.main()
