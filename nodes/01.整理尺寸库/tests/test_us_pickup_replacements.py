import copy
import json
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT / "code"), str(PROJECT.parents[1] / "lib")]

from us_pickup_replacements import apply_pickup_replacements, years


def ranger_fixture():
    plan = json.loads((PROJECT / "data/us/pickup_replacements.json").read_text(encoding="utf-8"))
    rule = plan["replacements"][0]
    old = [{"DIMENSION-ID": key, **rule["scope"], **fields, "分类": "皮卡", "版本": ""}
           for key, fields in rule["expected"].items()]
    return plan, old


def test_ranger_replacement_preserves_coverage_and_retires_invalid_identity():
    plan, old = ranger_fixture()
    untouched = {"DIMENSION-ID": "unrelated"}
    original = copy.deepcopy(old)
    rows, migrations = apply_pickup_replacements([*old, untouched], plan)
    atoms = {(r["CAB"], r["BED"], year): r["L-IN"]
             for r in rows if r is not untouched for year in years(r["YEAR"])}

    assert old == original
    assert untouched in rows
    assert len(atoms) == 42
    assert ("SuperCab", "7", 2008) not in atoms
    assert atoms["SuperCab", "6", 1998] == "202.9"
    assert atoms["SuperCab", "6", 2008] == "203.6"
    assert atoms["Regular", "7", 2004] == "200.6"
    assert atoms["Regular", "7", 2007] == "198.4"
    assert atoms["Regular", "7", 2008] == "201.4"
    assert [m["新DIMENSION-ID"] for m in migrations if m["旧DIMENSION-ID"].endswith("SuperCab 7 US")] == [""]


def test_ranger_replacement_rejects_gaps_and_upstream_drift():
    plan, old = ranger_fixture()
    plan["replacements"][0]["segments"].pop()
    with pytest.raises(ValueError, match="缺少车型年份"):
        apply_pickup_replacements(old, plan)
    old[0]["L-IN"] = "200.0"
    with pytest.raises(ValueError, match="前置条件"):
        apply_pickup_replacements(old, plan)
