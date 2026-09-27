from __future__ import annotations

import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "data" / "us" / "0916" / "00_US尺寸库.csv"


def load_rows(make: str, model: str) -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        return [
            row for row in csv.DictReader(handle)
            if row["MAKE"] == make and row["MODEL"] == model
        ]


def test_2001_jimmy_keeps_short_and_long_wheelbase_bodies_separate():
    rows = [row for row in load_rows("GMC", "Jimmy") if row["YEAR"] == "2001"]

    assert {row["版本"] for row in rows} == {"2dr", "4dr"}
    assert {row["DIMENSION-ID"] for row in rows} == {
        "GMC Jimmy 2dr SUV 2001",
        "GMC Jimmy 4dr SUV 2001",
    }
    assert {row["版本"]: row["L-IN"] for row in rows} == {"2dr": "177.3", "4dr": "183.8"}


def test_first_generation_sidekick_keeps_door_counts_separate():
    rows = [row for row in load_rows("Suzuki", "Sidekick") if row["版本"] != "Sport"]

    assert {row["版本"] for row in rows} == {"2dr", "4dr"}
    assert {row["YEAR"] for row in rows if row["版本"] == "2dr"} == {"1989-1994", "1995"}
    assert {row["YEAR"] for row in rows if row["版本"] == "4dr"} == {"1991", "1992-1994", "1995"}
    assert all(row["版本"] in row["DIMENSION-ID"] for row in rows)
    assert {row["L-IN"] for row in rows if row["版本"] == "2dr"} == {"142.5"}
    assert {row["L-IN"] for row in rows if row["版本"] == "4dr"} == {"158.7"}
