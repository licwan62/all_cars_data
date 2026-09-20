import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from run import dimension_concentration


def rows(dimensions):
    return [
        {"L-MM": str(length), "W-MM": str(width), "H-MM": str(height)}
        for length, width, height in dimensions
    ]


def test_identical_dimensions_have_full_concentration():
    assert dimension_concentration(rows([(4800, 1800, 1400), (4800, 1800, 1400)])) == 100.0


def test_length_variation_has_more_weight_than_equal_relative_width_variation():
    length_score = dimension_concentration(rows([(4500, 1800, 1400), (5100, 1800, 1400)]))
    width_score = dimension_concentration(rows([(4800, 1680, 1400), (4800, 1920, 1400)]))
    assert length_score < width_score
