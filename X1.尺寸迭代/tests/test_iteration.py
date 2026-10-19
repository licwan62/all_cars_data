from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
# 历史批次 2026-09-16_02 已在 de777c02 清理出本地 artifacts/；审核结论固定为精简 fixture
# （验证.json、完整性验证.csv 原样取自 git 6365cc4e，correct摘要.json 为 correct.csv 的行数、sha256 与终核记录），
# 日常测试不再依赖历史批次的本地位置。
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "2026-09-16_02_jeep-wrangler-final-review-release"
# 当前上游尺寸库（01.整理尺寸库 output）。
SOURCE = ROOT / "01.整理尺寸库" / "output" / "尺寸库_US.csv"
RENEGADE_ID = "Jeep Wrangler 2dr YJ Renegade SUV 1990-1994"


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


class JeepWranglerPublishedReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = read_csv(SOURCE)
        cls.correct = json.loads((FIXTURE / "correct摘要.json").read_text(encoding="utf-8"))
        cls.coverage = read_csv(FIXTURE / "完整性验证.csv")
        cls.validation = json.loads((FIXTURE / "验证.json").read_text(encoding="utf-8"))

    def test_published_source_matches_reviewed_candidate(self) -> None:
        self.assertEqual(self.correct["rows"], 4346)
        self.assertTrue(self.correct["dimension_id_unique"])
        self.assertEqual(self.correct["rows_missing_lwh"], 4)

    def test_final_review_dimensions(self) -> None:
        current = self.source.set_index("DIMENSION-ID")
        expected = {
            "Jeep Wrangler 2dr JL Xtreme SUV 2026": ["170.9", "73.9", "75.5"],
            "Jeep Wrangler 2dr JL SUV 2025-2026": ["166.8", "73.9", "73.6"],
            "Jeep Wrangler 4dr JLU SUV 2025-2026": ["188.4", "73.9", "73.6"],
            "Jeep Gladiator 4dr JT Rubicon Pickup 2025-2026 Crew 5": ["218", "73.8", "76.1"],
            "Jeep Gladiator 4dr JT Mojave Pickup 2025-2026 Crew 5": ["218", "73.8", "76.3"],
        }
        for dimension_id, dimensions in expected.items():
            with self.subTest(dimension_id=dimension_id):
                released = self.correct["records"][dimension_id]
                self.assertEqual([released["L-IN"], released["W-IN"], released["H-IN"]], dimensions)
                self.assertEqual(current.loc[f"{dimension_id} US", ["L-IN", "W-IN", "H-IN"]].tolist(), dimensions)

    def test_renegade_is_deferred_not_published(self) -> None:
        self.assertFalse(self.correct["dimension_ids_contain"][RENEGADE_ID])
        self.assertNotIn(f"{RENEGADE_ID} US", set(self.source["DIMENSION-ID"]))
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
        self.assertEqual(self.validation["candidate_sha256"], self.correct["sha256_lf"])
        self.assertEqual(self.validation["coverage_missing_ids"], [])


if __name__ == "__main__":
    unittest.main()
