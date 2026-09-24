from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "X1.尺寸迭代"
BATCH = PROJECT / "artifacts" / "2026-09-16_02_jeep-wrangler-final-review-release"
# 当前上游尺寸库（01.整理尺寸库 output）；历史批次的发布内容以 correct.csv 为准。
SOURCE = ROOT / "01.整理尺寸库" / "output" / "尺寸库_US.csv"


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def sha256(path: Path) -> str:
    # 仓库 core.autocrlf 会在检出时把 LF 改成 CRLF；按提交时的 LF 字节计算。
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class JeepWranglerPublishedReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = read_csv(SOURCE)
        cls.correct = read_csv(BATCH / "correct.csv")
        cls.coverage = read_csv(BATCH / "完整性验证.csv")
        cls.validation = json.loads((BATCH / "验证.json").read_text(encoding="utf-8"))

    def test_published_source_matches_reviewed_candidate(self) -> None:
        self.assertEqual(len(self.correct), 4346)
        self.assertTrue(self.correct["DIMENSION-ID"].is_unique)
        self.assertEqual(
            int(self.correct[["L-IN", "W-IN", "H-IN"]].eq("").any(axis=1).sum()),
            4,
        )

    def test_final_review_dimensions(self) -> None:
        current = self.source.set_index("DIMENSION-ID")
        released = self.correct.set_index("DIMENSION-ID")
        expected = {
            "Jeep Wrangler 2dr JL Xtreme SUV 2026": ["170.9", "73.9", "75.5"],
            "Jeep Wrangler 2dr JL SUV 2025-2026": ["166.8", "73.9", "73.6"],
            "Jeep Wrangler 4dr JLU SUV 2025-2026": ["188.4", "73.9", "73.6"],
            "Jeep Gladiator 4dr JT Rubicon Pickup 2025-2026 Crew 5": ["218", "73.8", "76.1"],
            "Jeep Gladiator 4dr JT Mojave Pickup 2025-2026 Crew 5": ["218", "73.8", "76.3"],
        }
        for dimension_id, dimensions in expected.items():
            with self.subTest(dimension_id=dimension_id):
                self.assertEqual(released.loc[dimension_id, ["L-IN", "W-IN", "H-IN"]].tolist(), dimensions)
                self.assertEqual(current.loc[f"{dimension_id} US", ["L-IN", "W-IN", "H-IN"]].tolist(), dimensions)

    def test_renegade_is_deferred_not_published(self) -> None:
        renegade_id = "Jeep Wrangler 2dr YJ Renegade SUV 1990-1994"
        self.assertNotIn(renegade_id, set(self.correct["DIMENSION-ID"]))
        self.assertNotIn(f"{renegade_id} US", set(self.source["DIMENSION-ID"]))
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
