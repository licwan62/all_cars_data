from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "X1.尺寸迭代"
BATCH = PROJECT / "artifacts" / "2026-09-16_02_jeep-wrangler-final-review-release"
SOURCE = ROOT / "data" / "us" / "source" / "US尺寸库.csv"


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class JeepWranglerPublishedReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = read_csv(SOURCE)
        cls.correct = read_csv(BATCH / "correct.csv")
        cls.coverage = read_csv(BATCH / "完整性验证.csv")
        cls.validation = json.loads((BATCH / "验证.json").read_text(encoding="utf-8"))

    def test_published_source_matches_reviewed_candidate(self) -> None:
        self.assertEqual(sha256(SOURCE), sha256(BATCH / "correct.csv"))
        self.assertTrue(self.source.equals(self.correct))
        self.assertEqual(len(self.source), 4346)
        self.assertTrue(self.source["DIMENSION-ID"].is_unique)
        self.assertEqual(
            int(self.source[["L-IN", "W-IN", "H-IN"]].eq("").any(axis=1).sum()),
            4,
        )

    def test_final_review_dimensions(self) -> None:
        keyed = self.source.set_index("DIMENSION-ID")
        expected = {
            "Jeep Wrangler 2dr JL Xtreme SUV 2026": ["170.9", "73.9", "75.5"],
            "Jeep Wrangler 2dr JL SUV 2025-2026": ["166.8", "73.9", "73.6"],
            "Jeep Wrangler 4dr JLU SUV 2025-2026": ["188.4", "73.9", "73.6"],
            "Jeep Gladiator 4dr JT Rubicon Pickup 2025-2026 Crew 5": ["218", "73.8", "76.1"],
            "Jeep Gladiator 4dr JT Mojave Pickup 2025-2026 Crew 5": ["218", "73.8", "76.3"],
        }
        for dimension_id, dimensions in expected.items():
            with self.subTest(dimension_id=dimension_id):
                self.assertEqual(
                    keyed.loc[dimension_id, ["L-IN", "W-IN", "H-IN"]].tolist(),
                    dimensions,
                )

    def test_renegade_is_deferred_not_published(self) -> None:
        renegade_id = "Jeep Wrangler 2dr YJ Renegade SUV 1990-1994"
        self.assertNotIn(renegade_id, set(self.source["DIMENSION-ID"]))
        row = self.coverage.loc[self.coverage["页面车型"].eq("YJ Renegade")].iloc[0]
        self.assertEqual(row["处理结论"], "暂缓-外廓来源冲突")
        self.assertEqual(row["对应DIMENSION-ID"], "")

    def test_release_validation_contract(self) -> None:
        self.assertTrue(self.validation["release_ready"])
        self.assertTrue(self.validation["correct_matches_candidate"])
        self.assertTrue(self.validation["untouched_rows_equal"])
        self.assertTrue(self.validation["dimension_id_unique"])
        self.assertTrue(self.validation["dimension_id_format_valid"])
        self.assertTrue(self.validation["coverage_resolved"])
        self.assertEqual(self.validation["candidate_sha256"], sha256(BATCH / "correct.csv"))
        self.assertEqual(self.validation["coverage_missing_ids"], [])


if __name__ == "__main__":
    unittest.main()
