from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


MODULE_PATH = Path(__file__).resolve().parents[1] / "research" / "gray_zone_research.py"
SPEC = importlib.util.spec_from_file_location("pickup_gray_zone", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_50mm_gray_zone_promotes_three_boundary_atoms() -> None:
    source = pd.read_csv(MODULE.SOURCE_DETAIL, encoding="utf-8-sig")
    gray, decisions = MODULE.apply_gray_zone(source, 50.0)
    assert len(decisions) == 3
    assert set(decisions["MODEL"]) == {
        "Escalade EXT",
        "F-150",
        "F-250/F-350 Super Duty",
    }
    changed = gray[gray["自动尺码"] != source["PHYSICAL_SKU"]]
    assert len(changed) == 3
    assert (changed["自动长度余量"] >= 0).all()
