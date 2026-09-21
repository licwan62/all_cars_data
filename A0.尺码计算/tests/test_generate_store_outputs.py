from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import generate_store_outputs as store_outputs  # noqa: E402


class StoreOutputTests(unittest.TestCase):
    def test_project_shelf_config_matches_new_rule(self) -> None:
        rule_path, size_column, shops = store_outputs.load_shelf_config(
            PROJECT_DIR / "data" / "店铺分组" / "货架.yaml"
        )

        self.assertEqual(rule_path.name, "0917.1-新命名.csv")
        self.assertEqual(size_column, "尺码")
        self.assertEqual(set(shops), {"HNT", "TM", "TM_拆分"})
        self.assertEqual(dict(shops["TM_拆分"])["3XXL-550"], "4XL")

    def test_shipping_size_mapping_updates_result_and_candidate(self) -> None:
        source = pd.DataFrame(
            [
                {"自动尺码": "3XXL-550", "候选": "3XXL-550"},
                {"自动尺码": "无可用尺码", "候选": "4XL"},
                {"自动尺码": "数据不全", "候选": None},
            ]
        )

        result = store_outputs.apply_shipping_sizes(
            source,
            [("3XXL-550", "4XL"), ("4XL", "4XL")],
        )

        self.assertEqual(result["自动尺码"].tolist(), ["4XL", "无可用尺码", "数据不全"])
        self.assertEqual(result["候选"].tolist()[:2], ["4XL", "4XL"])


if __name__ == "__main__":
    unittest.main()
