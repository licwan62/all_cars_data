import sys
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT.parents[1] / "lib"))
sys.path.insert(0, str(PROJECT / "code"))
from cover_shape.family_cache import CACHE_FIELDS, FamilyCache, outcome, read_cache, validate_rules, write_cache
from cover_shape.ingest import discover
from cover_shape.representatives import build


def rule(**kwargs):
    base = {k: "" for k in CACHE_FIELDS}
    base.update(market="US", make="Synthetic", model="Test", body_type="Hatchback", shape="COMPACT_HATCH",
                sample_years="2021", source_url="https://example.org/spec", note="fixture")
    base.update(kwargs)
    return base


def record(rid="r US", generation="ONE", years=(2020, 2021, 2022), market="US", body="Hatchback", trim=""):
    return {"source_record_id": rid, "make": "Synthetic", "model": "Test", "generation": generation, "body_type": body,
            "trim": trim, "market": market, "covered_years": list(years), "CAB": "", "BED": "", "raw_fields": {}}


def test_family_rule_covers_other_years_and_branches_but_not_other_structures():
    cache = FamilyCache([rule()])
    sampled, scope = cache.select(record())
    assert scope == "same_market" and outcome(sampled, scope, record())["SHAPE_STATUS"] == "PROBABLE"
    later = record(years=(2024, 2025), trim="Sport")
    result = outcome(*cache.select(later), later)
    assert result["SHAPE_METHOD"] == "family_cache_inherited" and result["SHAPE_STATUS"] == "INFERRED"
    assert result["SHAPE_YEAR"] == "2021"
    assert cache.select(record(body="Sedan")) == (None, "")


def test_more_specific_generation_year_and_pattern_rules_win():
    rules = [rule(), rule(generation="TWO", shape="SPORT_LIFTBACK", sample_years="2024"),
             rule(match_pattern=r"VERSION=Type R", shape="LOW_FASTBACK", sample_years="2023")]
    cache = FamilyCache(rules)
    assert cache.select(record())[0]["shape"] == "COMPACT_HATCH"
    assert cache.select(record(generation="TWO"))[0]["shape"] == "SPORT_LIFTBACK"
    assert cache.select(record(trim="Type R"))[0]["shape"] == "LOW_FASTBACK"
    split = FamilyCache([rule(year_end="2019", shape="WAGON", sample_years="2018"), rule(year_start="2020", sample_years="2021")])
    assert split.select(record(years=(2018, 2019)))[0]["shape"] == "WAGON"
    with pytest.raises(ValueError, match="冲突"):
        split.select(record(years=(2019, 2020)))


def test_cross_market_reuse_requires_year_overlap_and_is_inferred():
    cache = FamilyCache([rule(generation="ONE")], {"cross_market_sources": ["US"]})
    cache.learn_spans([record()])
    eu = record("r EU", generation="G7", market="EU", years=(2021, 2022, 2023))
    found, scope = cache.select(eu)
    assert scope == "cross_market"
    result = outcome(found, scope, eu)
    assert result["SHAPE_METHOD"] == "family_cache_cross_market" and result["SHAPE_STATUS"] == "INFERRED"
    assert cache.select(record("old EU", market="EU", years=(2001, 2002))) == (None, "")
    assert FamilyCache([rule()]).select(eu) == (None, "")


def test_rules_require_source_note_sample_years_and_valid_shape(tmp_path):
    with pytest.raises(ValueError, match="sample_years"):
        validate_rules([rule(sample_years="")])
    with pytest.raises(ValueError, match="source_url"):
        validate_rules([rule(source_url="")])
    with pytest.raises(ValueError, match="SHAPE"):
        validate_rules([rule(shape="Hatchback")])
    with pytest.raises(ValueError, match="重复"):
        validate_rules([rule(), rule(note="again")])
    path = tmp_path / "family_cache.csv"
    write_cache(path, [rule(), rule(generation="TWO", sample_years="2024;2025")])
    assert len(read_cache(path)) == 2


def test_build_applies_cache_per_record_after_exact_evidence():
    full = yaml.safe_load((PROJECT / "data/cover_shape/full_table.yaml").read_text(encoding="utf-8"))
    taxonomy = yaml.safe_load((PROJECT / "data/cover_shape/taxonomy_v1.yaml").read_text(encoding="utf-8"))
    auto = yaml.safe_load((PROJECT / "data/cover_shape/automatic.yaml").read_text(encoding="utf-8"))

    def row(rid, year, body="Hatchback"):
        return {"DIMENSION-ID": rid, "MAKE": "Synthetic", "MODEL": "Test", "代际": "ONE", "版本": "", "结构": body,
                "YEAR": year, "L-IN": "170", "W-IN": "70", "H-IN": "58", "CAB": "", "BED": ""}

    rows = [row("a US", "2020-2021"), row("b US", "2022-2024"), row("c US", "2020-2024", body="Sedan")]
    legacy = [{"DIMENSION-ID": r["DIMENSION-ID"], "COUNTRY": "US", "车形": "SD1", "处理状态": "T"} for r in rows]
    cache = FamilyCache([rule(sample_years="2021", shape="SPORT_LIFTBACK")])
    out, audit = build(rows, legacy, [{"车身号": "SD1", "描述": "fixture"}], [], discover(list(rows[0])), full,
                       taxonomy, auto, "fixture", cache=cache)
    by_id = {r["DIMENSION-ID"]: r for r in out}
    assert by_id["a US"]["SHAPE_METHOD"] == "family_cache_sampled" and by_id["a US"]["SHAPE_STATUS"] == "PROBABLE"
    assert by_id["b US"]["SHAPE_METHOD"] == "family_cache_inherited" and by_id["b US"]["SHAPE"] == "SPORT_LIFTBACK"
    assert by_id["c US"]["SHAPE_METHOD"] == "prototype_geometry_dimensions"
