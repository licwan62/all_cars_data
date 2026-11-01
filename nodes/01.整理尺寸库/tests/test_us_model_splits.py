import copy
import csv
import json
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path[:0] = [str(ROOT / "lib"), str(PROJECT / "code")]
from us_model_splits import apply_splits, fingerprint
from model_members import load_members, model_key


def fixture():
    rows = [{"DIMENSION-ID": f"Audi A7/S7/RS7 Liftback {year} US", "MAKE": "Audi", "MODEL": "A7/S7/RS7",
        "YEAR": str(year), "代际": "gen2", "结构": "Liftback", "分类": "三厢车", "版本": "",
        "L-IN": "199", "W-IN": "79", "H-IN": "59", "参考车型": "old group", "备注": ""} for year in (2024, 2025)]
    plan = {"pilots": [{"id": "test", "status": "approved", "members": ["A7", "S7", "RS7"],
        "old_records": {r["DIMENSION-ID"]: fingerprint(r) for r in rows},
        "reference_names": {m: [m] for m in ["A7", "S7", "RS7"]}, "evidence_ids": ["e"],
        "year_decisions": [{"member": m, "year": y, "presence": "present", "evidence_ids": ["e"]} for m in ["A7", "S7", "RS7"] for y in (2024, 2025)],
        "downstream_reviews": {n: {"reviewed": True, "basis": "fixture evidence", "allocation": "unallocated", "old_codes": "preserve"}
            for n in ["structure-review", "shape-classification", "code-mapping", "sales-estimation", "size-calculation"]},
        "segments": [{"old_id": r["DIMENSION-ID"], "member": m, "YEAR": r["YEAR"], "L-IN": "190" if r["YEAR"] == "2024" else "191", "W-IN": "75", "H-IN": "55", "evidence_ids": ["e"], "reference": "independent evidence"}
            for r in rows for m in ["A7", "S7", "RS7"]]}]}
    evidence = {"sources": [{"id": "e", "status": "verified", "market": "US", "members": ["A7", "S7", "RS7"], "years": [2024, 2025],
        "presence_records": [{"member": m, "year": y, "presence": "present"} for m in ["A7", "S7", "RS7"] for y in (2024, 2025)],
        "facts": ["us_presence", "dimensions"], "dimension_records": [{"member": m, "year": y, "unit": "in", "width_basis": "without_mirrors",
            "generation": "gen2",
            "L-IN": "190" if y == 2024 else "191", "W-IN": "75", "H-IN": "55"} for m in ["A7", "S7", "RS7"] for y in (2024, 2025)]}]}
    return rows, plan, evidence


def test_approved_split_uses_independent_dimensions_and_complete_migration():
    rows, plan, evidence = fixture()
    untouched = {**rows[-1], "DIMENSION-ID": "Audi RS7 Liftback 2026 US", "MODEL": "RS7", "YEAR": "2026"}
    output, migration, _, pending = apply_splits(rows + [untouched], plan, evidence, [])
    assert len(output) == 7 and len(migration) == 6 and not pending
    assert untouched in output
    assert {r["L-IN"] for r in output if r != untouched} == {"190", "191"}
    assert {r["新DIMENSION-ID"] for r in migration} <= {r["DIMENSION-ID"] for r in output}
    assert {r["旧DIMENSION-ID"] for r in migration} == set(plan["pilots"][0]["old_records"])


@pytest.mark.parametrize("failure", ["years", "dimensions", "numbers", "duplicate", "sales", "codes", "downstream", "drift"])
def test_incomplete_or_unsafe_split_rejected_without_mutation(failure):
    rows, plan, evidence = fixture()
    pilot = plan["pilots"][0]
    if failure == "years": pilot["year_decisions"].pop()
    elif failure == "dimensions": pilot["segments"].pop()
    elif failure == "numbers": pilot["segments"][0]["L-IN"] = "199"
    elif failure == "duplicate": pilot["segments"].append(pilot["segments"][0])
    elif failure == "sales": pilot["downstream_reviews"]["sales-estimation"]["allocation"] = "copy_to_all"
    elif failure == "codes": pilot["downstream_reviews"]["code-mapping"]["old_codes"] = "delete"
    elif failure == "downstream": pilot["downstream_reviews"].pop("shape-classification")
    elif failure == "drift": rows[0]["L-IN"] = "200"
    original = copy.deepcopy(rows)
    with pytest.raises(ValueError): apply_splits(rows, plan, evidence, [])
    assert rows == original


def test_real_pending_plan_keeps_all_records_and_2026_rs7():
    with (PROJECT / "output/尺寸库_US.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    plan = json.loads((PROJECT / "data/us/audi_a7_split.json").read_text(encoding="utf-8"))
    evidence = json.loads((PROJECT / "data/us/audi_a7_evidence.json").read_text(encoding="utf-8"))
    output, migration, candidates, pending = apply_splits(rows, plan, evidence, [])
    assert output == rows and migration == []
    assert len(candidates) == 42 and len(pending) == 6
    assert all(not r["L-IN"] and not r["W-IN"] and not r["H-IN"] for r in candidates)
    rules = load_members(PROJECT / "data/us/model_members.json")
    labels = {(model_key(r["MAKE"]), model_key(r["MODEL"])) for r in rows if "/" in r["MODEL"]}
    assert labels == {(model_key(r["make"]), model_key(r["model"])) for r in rules["groups"]}


def test_absent_year_must_be_explicit_and_cannot_have_a_dimension_segment():
    rows, plan, evidence = fixture()
    pilot = plan["pilots"][0]
    pilot["year_decisions"][0]["presence"] = "absent"
    evidence["sources"][0]["presence_records"][0]["presence"] = "absent"
    with pytest.raises(ValueError, match="未供售"):
        apply_splits(rows, plan, evidence, [])
    pilot["segments"] = [r for r in pilot["segments"] if not (r["member"] == "A7" and r["YEAR"] == "2024")]
    output, migration, _, _ = apply_splits(rows, plan, evidence, [])
    assert len(output) == len(migration) == 5


@pytest.mark.parametrize("change", ["partial", "wrong_market", "mirrors", "missing_year", "nonpositive"])
def test_evidence_limits_prevent_activation(change):
    rows, plan, evidence = fixture()
    source = evidence["sources"][0]
    if change == "partial": source["status"] = "partial"
    elif change == "wrong_market": source["market"] = "EU"
    elif change == "mirrors": source["dimension_records"][0]["width_basis"] = "with_mirrors"
    elif change == "missing_year": source["years"] = [2025]
    elif change == "nonpositive": plan["pilots"][0]["segments"][0]["L-IN"] = "0"
    with pytest.raises(ValueError):
        apply_splits(rows, plan, evidence, [])
