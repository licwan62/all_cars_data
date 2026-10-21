from __future__ import annotations

import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "data" / "us" / "0916" / "00_US尺寸库.csv"


def test_first_generation_rav4_keeps_distinct_us_body_styles():
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    rows = [
        row for row in rows
        if row["MAKE"] == "Toyota"
        and row["MODEL"] == "RAV4"
        and row["代际"] == "gen1"
    ]

    assert len(rows) == 7
    assert {row["版本"] for row in rows if row["结构"] == "SUV"} == {"2dr", "4dr"}
    assert {row["YEAR"] for row in rows if row["版本"] == "2dr"} == {"1996", "1997", "1998"}
    assert {row["YEAR"] for row in rows if row["版本"] == "4dr"} == {"1996", "1997", "1998-2000"}
    assert [(row["结构"], row["YEAR"]) for row in rows if row["结构"] == "Convertible"] == [
        ("Convertible", "1998-1999")
    ]
    assert all(row["版本"] in row["DIMENSION-ID"] for row in rows if row["结构"] == "SUV")
    assert not any(row["版本"] == "2dr" and "2000" in row["YEAR"] for row in rows)
