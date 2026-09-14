"""Tests for year_parser module."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from year_parser import parse_year, merge_year_ranges, format_year_ranges


def test_parse_single_year():
    assert parse_year("2025") == (2025, 2025)
    assert parse_year("1994") == (1994, 1994)


def test_parse_year_range():
    assert parse_year("2015-2018") == (2015, 2018)
    assert parse_year("2004-2012") == (2004, 2012)


def test_parse_invalid():
    assert parse_year("") == (None, None)
    assert parse_year("abc") == (None, None)


def test_merge_adjacent():
    ranges = [(1983, 1988), (1989, 1990), (1991, 1991)]
    result = merge_year_ranges(ranges)
    assert result == [(1983, 1991)]


def test_merge_overlapping():
    ranges = [(2000, 2005), (2004, 2010)]
    result = merge_year_ranges(ranges)
    assert result == [(2000, 2010)]


def test_merge_separate():
    ranges = [(1983, 1992), (1996, 2000), (2004, 2012)]
    result = merge_year_ranges(ranges)
    assert result == [(1983, 1992), (1996, 2000), (2004, 2012)]


def test_merge_with_gap():
    ranges = [(2000, 2005), (2010, 2015)]
    result = merge_year_ranges(ranges)
    assert result == [(2000, 2005), (2010, 2015)]


def test_format_year_ranges():
    ranges = [(1983, 1992), (1996, 2000), (2004, 2012)]
    result = format_year_ranges(ranges)
    assert result == "1983-1992/1996-2000/2004-2012"


def test_format_single_year():
    ranges = [(2025, 2025)]
    result = format_year_ranges(ranges)
    assert result == "2025"


def test_format_empty():
    assert format_year_ranges([]) == ""