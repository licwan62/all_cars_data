from __future__ import annotations

import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "data" / "us" / "0916" / "00_US尺寸库.csv"


def test_outback_sport_is_a_separate_impreza_derived_wagon_family():
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    sport_rows = [
        row for row in rows
        if row["MAKE"] == "Subaru" and row["MODEL"] == "Outback Sport"
    ]
    outback_rows = [
        row for row in rows
        if row["MAKE"] == "Subaru" and row["MODEL"] == "Outback"
    ]

    assert len(sport_rows) == 8
    assert all(not row["版本"] for row in sport_rows)
    assert {row["结构"] for row in sport_rows} == {"Wagon"}
    assert all("Outback Sport" not in row["DIMENSION-ID"].replace("Subaru Outback Sport", "", 1) for row in sport_rows)
    assert max(float(row["L-IN"]) for row in sport_rows) < min(float(row["L-IN"]) for row in outback_rows)
