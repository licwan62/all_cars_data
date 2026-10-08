from __future__ import annotations

import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "data" / "us" / "0916" / "00_US尺寸库.csv"


def test_2027_gle_uses_official_maximum_exterior_dimensions():
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["MAKE"] == "Mercedes-Benz" and row["MODEL"] == "GLE-Class"
        ]

    coupe = next(row for row in rows if row["结构"] == "Coupe" and row["代际"] == "gen2")
    assert coupe["YEAR"] == "2021-2027"
    assert (coupe["L-IN"], coupe["W-IN"], coupe["H-IN"]) == ("195.3", "79.4", "67.7")

    suv_2027 = next(row for row in rows if row["结构"] == "SUV" and row["YEAR"] == "2027")
    assert suv_2027["代际"] == "gen2"
    assert (suv_2027["L-IN"], suv_2027["W-IN"], suv_2027["H-IN"]) == (
        "194.6",
        "79.7",
        "70.7",
    )
