from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MODULE = PROJECT / "src" / "build_ear_position_summary.py"
SPEC = importlib.util.spec_from_file_location("ear_summary", MODULE)
assert SPEC and SPEC.loader
ear_summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ear_summary)


RULES = {
    "车耳信号": ["mirror", "后视镜"],
    "靠前信号": ["靠前", "too far forward"],
    "靠后信号": ["靠后", "too far back"],
}


def test_ignores_complaints_without_mirror_mention():
    assert ear_summary.classify_ear_position("cover is too small overall", RULES) is None


def test_mirror_mention_without_direction_is_normal():
    assert ear_summary.classify_ear_position("后视镜袋位置不对", RULES) == "普通"


def test_forward_direction_detected():
    assert ear_summary.classify_ear_position("mirror pocket placed too far forward", RULES) == "靠前"
    assert ear_summary.classify_ear_position("后视镜位置太靠前了", RULES) == "靠前"


def test_backward_direction_detected():
    assert ear_summary.classify_ear_position("后视镜位置太靠后了", RULES) == "靠后"


def test_conflicting_directions_fall_back_to_normal():
    assert ear_summary.classify_ear_position("后视镜靠前也靠后，完全对不上", RULES) == "普通"
