from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_regional_shape_output", PROJECT / "code" / "build_regional_shape_output.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
RULES = json.loads((PROJECT / "data" / "区域车形代理规则.json").read_text(encoding="utf-8"))


def lib_row(record_id, structure, category, make="A", model="B", year="2010-2012", dims=("1", "2", "3"), generation=""):
    return {"DIMENSION-ID": record_id, "MAKE": make, "MODEL": model, "版本": "", "结构": structure, "代际": generation,
            "YEAR": year, "分类": category, "L-IN": dims[0], "W-IN": dims[1], "H-IN": dims[2]}


def shape_row(record_id, shape, status):
    return {"DIMENSION-ID": record_id, "COUNTRY": record_id.rsplit(" ", 1)[-1], "车形": shape, "处理状态": status}


def test_incompatible_inherited_shape_falls_back_to_proxy():
    source = [lib_row("A B Wagon 2010-2012 EU", "Wagon", "两厢车")]
    prior = [shape_row("A B Wagon 2010-2012 EU", "SD1", "区域缓存-同车型单一车形")]
    out = module.build(source, prior, [], RULES)["output"][0]
    assert (out["车形"], out["处理状态"]) == ("H0", module.PROXY_STATUS)


def test_van_only_keeps_van_shapes():
    source = [lib_row("A B Van 2010-2012 EU", "Van", "两厢车")]
    prior = [shape_row("A B Van 2010-2012 EU", "SU1", "区域缓存-同车型单一车形")]
    assert module.build(source, prior, [], RULES)["output"][0]["车形"] == "V0"


def test_compatible_shape_is_migrated_across_id_rename():
    old = lib_row("A B Eagle I 1980 SUV 2010-2012 EU", "SUV", "越野车", generation="I")
    new = lib_row("A B 1980 SUV 2010-2012 EU", "SUV", "越野车", generation="I")
    prior = [shape_row(old["DIMENSION-ID"], "SU2", "区域缓存-同车型单一车形")]
    out = module.build([new], prior, [old], RULES)["output"][0]
    assert (out["车形"], out["处理状态"]) == ("SU2", "区域缓存-同车型单一车形")


def test_us_rename_uses_explicit_migration_and_missing_us_fails():
    source = [lib_row("A B Wagon 2001 US", "Wagon", "两厢车")]
    prior = [shape_row("A B B Wagon 2001 US", "H2", "US核定")]
    out = module.build(source, prior, [], RULES, {"A B B Wagon 2001 US": "A B Wagon 2001 US"})["output"][0]
    assert out["车形"] == "H2"
    with pytest.raises(ValueError):
        module.build(source, prior, [], RULES)


@pytest.mark.parametrize("structure,category,expected", [
    ("Liftback", "三厢车", "SD1"), ("Liftback", "两厢车", "H0"), ("Fastback", "跑车", "SD0"),
    ("Sattelschlepper", "", "V0"), ("SUV 5dr", "越野车", "SU1"),
])
def test_proxy_shapes(structure, category, expected):
    assert module.proxy_shape(lib_row("x", structure, category), RULES) == expected
