from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MODULE = PROJECT / "src" / "build_pickup_cab_bed_summary.py"
SPEC = importlib.util.spec_from_file_location("cab_bed_summary", MODULE)
assert SPEC and SPEC.loader
cab_bed_summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cab_bed_summary)


def test_extracts_cab_and_bed_from_free_text_model():
    row = {"车型": "Chevrolet Silverado 1500(1998-24) Crew Cab SB Bed"}
    assert cab_bed_summary.extract_cab_bed(row) == ("Crew Cab", "Short Bed")


def test_extracts_abbreviated_long_bed_suffix():
    row = {"车型": "C10(60-87)-Regular Cab LB"}
    assert cab_bed_summary.extract_cab_bed(row) == ("Regular Cab", "Long Bed")


def test_super_crew_normalises_to_crew_cab():
    row = {"车型": "F150-SuperCrew SB Bed-0824"}
    assert cab_bed_summary.extract_cab_bed(row) == ("Crew Cab", "Short Bed")


def test_falls_back_to_structured_fields_when_text_has_no_match():
    row = {"车型": "1989 GMC OBS", "提取驾驶室": "Regular Cab", "提取货斗": ""}
    assert cab_bed_summary.extract_cab_bed(row) == ("Regular Cab", "")


def test_no_signal_returns_empty_strings():
    row = {"车型": "BMW X5"}
    assert cab_bed_summary.extract_cab_bed(row) == ("", "")
