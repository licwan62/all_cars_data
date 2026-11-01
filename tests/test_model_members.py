import json
from pathlib import Path

import pytest
from model_members import ModelCoverage, load_members, year_set

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "nodes/01.整理尺寸库/data/us/model_members.json"


def row(model, year):
    return {"MAKE": "Audi", "MODEL": model, "YEAR": year, "DIMENSION-ID": f"Audi {model} {year} US"}


def test_rs7_alias_group_boundaries_and_independent_2026():
    matcher = ModelCoverage([row("A7/S7/RS7", "2012-2018"), row("A7/S7/RS7", "2019-2025"), row("RS7", "2026")], load_members(RULES))
    assert matcher.classify("Audi", "RS 7", 2021)["state"] == "组合记录覆盖、成员年份待核"
    assert matcher.classify("Audi", "RS 7", 2026)["state"] == "独立记录覆盖"
    assert matcher.classify("Audi", "RS7", 2011)["state"] == "确认年份缺口（本地参考差集）"
    assert matcher.classify("Audi", "S7", 2012)["state"] == "组合记录覆盖、成员年份待核"
    assert matcher.classify("Audi", "RS7 Performance", 2021)["state"] == "名称待核"
    assert matcher.classify("Other", "RS7", 2026)["state"] == "名称待核"


def test_year_gap_not_filled_between_combined_records():
    matcher = ModelCoverage([row("A7/S7/RS7", "2012-2018"), row("A7/S7/RS7", "2021-2025")], load_members(RULES))
    assert matcher.classify("Audi", "RS7", 2020)["state"] == "确认年份缺口（本地参考差集）"


def test_unknown_slash_is_not_split_or_declared_independent():
    matcher = ModelCoverage([row("Foo/Bar", "2020")], load_members(RULES))
    assert matcher.classify("Audi", "Foo", 2020)["state"] == "名称待核"
    assert matcher.classify("Audi", "Foo/Bar", 2020)["state"] == "名称待核"
    assert year_set("2020-2022") == {2020, 2021, 2022}
    with pytest.raises(ValueError):
        year_set("2022-2020")


def test_alias_ambiguity_rejected(tmp_path):
    data = json.loads(RULES.read_text(encoding="utf-8"))
    data["groups"][0]["members"][0]["aliases"] = ["RS 7"]
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Ambiguous"):
        load_members(path)
