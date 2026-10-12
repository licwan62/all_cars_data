from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "code"))
from cover_shape.ingest import discover
from cover_shape.representatives import build, prototype_candidate, representative_groups


@pytest.fixture
def policy():
    return yaml.safe_load((PROJECT / "data/cover_shape/full_table.yaml").read_text(encoding="utf-8"))


def row(rid="A Sedan 2020-2024 US", generation="ONE", body="Sedan", year="2020-2024", length="180"):
    return {"DIMENSION-ID": rid, "MAKE": "Synthetic", "MODEL": "Test", "代际": generation, "版本": "", "结构": body,
            "YEAR": year, "L-IN": length, "W-IN": "70", "H-IN": "55", "CAB": "", "BED": ""}


def prior(rows, code="SD1"):
    return [{"DIMENSION-ID": r["DIMENSION-ID"], "COUNTRY": r["DIMENSION-ID"].rsplit(" ", 1)[-1], "车形": code, "处理状态": "TEST"} for r in rows]


def test_representative_median_selects_present_year_not_gap(policy):
    rows = [row(year="2000-2001"), row(rid="second US", year="2010-2011")]
    groups = representative_groups(rows, prior(rows), discover(list(rows[0])), policy, "fixture", [])
    assert len(groups) == 1 and groups[0][1]["model_year"] == 2001
    assert len(groups[0][2]) == 2


@pytest.mark.parametrize("changed", [{"代际": "TWO"}, {"结构": "Hatchback"}, {"版本": "GT"}, {"CAB": "Crew"},
                                      {"BED": "Long"}, {"L-IN": "181"}, {"DIMENSION-ID": "second EU"}])
def test_generations_variants_dimensions_and_markets_never_share_groups(policy, changed):
    first = row()
    second = {**row(rid="second US"), **changed}
    groups = representative_groups([first, second], prior([first, second]), discover(list(first)), policy, "fixture", [])
    assert len(groups) == 2


def test_missing_generation_isolates_rows(policy):
    rows = [row(generation=""), row(rid="second US", generation="")]
    assert len(representative_groups(rows, prior(rows), discover(list(rows[0])), policy, "fixture", [])) == 2


def test_fallback_uses_geometry_and_dimensions_not_body_type(policy):
    dimensions = {"length_mm": 4200, "width_mm": 1800, "height_mm": 1650}
    geometry = {"high_cabin": True, "short_hood": True, "box_body": True}
    for body in ("Hatchback", "Sedan", "Wagon", "SUV"):
        assert prototype_candidate(geometry, {**dimensions, "body_type": body}, policy)[0] == "TALL_BOX"
    assert prototype_candidate({"sloped_rear": True}, {"length_mm": 4400, "width_mm": 1800, "height_mm": 1300}, policy)[0] == "LOW_FASTBACK"
    assert prototype_candidate({"low_cabin": True}, {"length_mm": 4400, "width_mm": 1800, "height_mm": 1300}, policy)[0] == "LOW_NOTCHBACK"


def test_missing_dimensions_other_without_inventing_measurements(policy):
    values = {"length_mm": None, "width_mm": 1800, "height_mm": 1800}
    label, _, reasons = prototype_candidate({"box_body": True}, values, policy)
    assert label == "OTHER" and "MISSING_OR_INVALID_DIMENSIONS" in reasons
    assert values["length_mm"] is None


def test_every_source_row_gets_one_shape_and_source_is_immutable(policy):
    rows = [row(), row(rid="second US", year="2025-2026")]
    original = copy.deepcopy(rows)
    taxonomy = yaml.safe_load((PROJECT / "data/cover_shape/taxonomy_v1.yaml").read_text(encoding="utf-8"))
    auto = yaml.safe_load((PROJECT / "data/cover_shape/automatic.yaml").read_text(encoding="utf-8"))
    out, audit = build(rows, prior(rows), [{"车身号": "SD1", "描述": "Synthetic geometry prototype"}], [],
                       discover(list(rows[0])), policy, taxonomy, auto, "fixture")
    assert [r["DIMENSION-ID"] for r in out] == [r["DIMENSION-ID"] for r in rows]
    assert {r["SHAPE"] for r in out} == {"STANDARD_SEDAN"}
    assert all(r["SHAPE_STATUS"] == "INFERRED" for r in out)
    assert len(audit) == 1 and rows == original


def test_research_target_scope_can_project_unknown_source_market_without_crossing_branch(policy):
    rows = [row()]
    mapping = discover(list(rows[0]))
    initial = representative_groups(rows, prior(rows), mapping, policy, "fixture", [])
    gid, representative, _, _ = initial[0]
    scope = {k: representative.get(k, "") for k in ("make", "model", "generation", "body_type", "trim", "market", "group_id")}
    fact = {"evidence_id": "SYNTHETIC_TEST_ONLY", "variant_key": representative["variant_key"],
            "evidence_type": "automatic_description", "source_url": "https://fixtures.example.org/document",
            "source_rank": "B", "validation_flags": [], "model_year_claim": 2022, "market_claim": "",
            "variant_claim": {}, "data_payload": {"automatic": True, "target_scope": scope,
            "inference_chain": {"upstream_branch": rows[0]["DIMENSION-ID"]},
            "identity_match": {"acceptable_for_inference": True},
            "features": {"usable": True, "geometric_observations": {"roof_slope": True}, "top_profile_64": []}}}
    taxonomy = yaml.safe_load((PROJECT / "data/cover_shape/taxonomy_v1.yaml").read_text(encoding="utf-8"))
    auto = yaml.safe_load((PROJECT / "data/cover_shape/automatic.yaml").read_text(encoding="utf-8"))
    output, _ = build(rows, prior(rows), [{"车身号": "SD1", "描述": "Synthetic prototype"}], [fact], mapping, policy, taxonomy, auto, "fixture")
    assert output[0]["SHAPE_METHOD"] == "representative_evidence" and output[0]["SHAPE_STATUS"] == "INFERRED"
    wrong = copy.deepcopy(fact)
    wrong["data_payload"]["target_scope"]["generation"] = "OTHER"
    assert not representative_groups(rows, prior(rows), mapping, policy, "fixture", [wrong])[0][3]
