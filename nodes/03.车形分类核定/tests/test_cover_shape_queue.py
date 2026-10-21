from datetime import datetime, timezone
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT.parents[1] / "lib"))
sys.path.insert(0, str(PROJECT / "code"))
from cover_shape.family_cache import sample_years
from cover_shape.research_queue import open_tasks, record_attempt, refresh_queue, select_tasks


def policy():
    return yaml.safe_load((PROJECT / "data/cover_shape/research_queue.yaml").read_text(encoding="utf-8"))


def record(rid="fixture US", model="Test", body="Hatchback", generation="ONE", years=None, market="US", length=4200, trim=""):
    return {"source_record_id": rid, "model_year": 2022, "make": "Synthetic", "model": model, "generation": generation,
            "body_type": body, "trim": trim, "market": market, "length_mm": length, "width_mm": 1800, "height_mm": 1500,
            "covered_years": years or [2020, 2021, 2022]}


def group(gid, *records):
    return gid, records[0], list(records), []


def audit(gid, alternates=()):
    return {"group_id": gid, "SHAPE": "COMPACT_HATCH", "SHAPE_STATUS": "INFERRED", "alternate_shapes": list(alternates)}


def outcomes(groups, method="prototype_geometry_dimensions", overrides=None):
    rows = {r["source_record_id"]: {"SHAPE": "COMPACT_HATCH", "SHAPE_METHOD": method} for _, _, members, _ in groups for r in members}
    for rid, value in (overrides or {}).items():
        rows[rid]["SHAPE_METHOD"] = value
    return rows


def queue(groups, previous=(), **kwargs):
    return refresh_queue(groups, [audit(g[0]) for g in groups], outcomes(groups, **kwargs), list(previous), policy())


def test_one_task_per_model_structure_family_with_few_sample_years():
    groups = [group("a", record("a US", years=list(range(2010, 2016)))),
              group("b", record("b US", generation="TWO", years=list(range(2016, 2026)))),
              group("c", record("c US", trim="Sport", length=4300, years=[2010, 2011, 2012])),
              group("d", record("d US", body="Sedan"))]
    rows = queue(groups)
    assert len(rows) == 2  # Hatchback 族（多代际/尺寸/trim 合并）与 Sedan 族分开研究
    hatch = next(r for r in rows if r["body_type"] == "Hatchback")
    assert hatch["affected_records"] == 3 and hatch["research_generations"] == ["ONE", "TWO"]
    assert hatch["suggested_sample_years"] == [2012, 2018, 2023]
    assert sample_years(list(range(2020, 2024)), policy()) == [2021]


def test_cache_coverage_drives_state():
    groups = [group("a", record("a US")), group("b", record("b US", generation="TWO"))]
    assert queue(groups)[0]["state"] == "PENDING"
    partial = queue(groups, overrides={"a US": "family_cache_inherited"})[0]
    assert partial["state"] == "PARTIAL" and partial["research_generations"] == ["TWO"]
    done = queue(groups, method="family_cache_sampled")[0]
    assert done["state"] == "CACHED" and not open_tasks([done], policy())
    cross = queue(groups, method="family_cache_cross_market")[0]
    assert cross["state"] == "PENDING" and cross["cross_market_records"] == 2


def test_failed_attempt_backoff_and_reset_on_changed_membership():
    groups = [group("a", record("a US"))]
    first = queue(groups)[0]
    failed = record_attempt(first, [], [{"status": "UNKNOWN", "cover_shape": "UNKNOWN"}], [], policy(), "fixture", "2026-10-12T00:00:00Z")
    again = queue(groups, [failed])[0]
    assert again["state"] == "NO_EVIDENCE" and again["attempts"] == 1
    assert not select_tasks([again], policy(), 8, datetime(2026, 10, 12, tzinfo=timezone.utc))
    assert select_tasks([again], policy(), 8, datetime(2026, 10, 15, tzinfo=timezone.utc))
    changed = queue([group("a", record("a US", years=[2021, 2022]))], [failed])[0]
    assert changed["state"] == "PENDING" and changed["attempts"] == 0
    rule = {"shape": "COMPACT_HATCH"}
    good = record_attempt(first, [], [{"status": "INFERRED", "cover_shape": "COMPACT_HATCH"}], [rule], policy(), "b", "2026-10-12T00:00:00Z")
    assert good["state"] == "PARTIAL" and not good["next_retry_at_utc"]
    limited = {"evidence_id": "s", "data_payload": {"error_code": "REQUEST_BUDGET_EXHAUSTED"}}
    deferred = record_attempt(first, [limited], [{"status": "UNKNOWN", "cover_shape": "UNKNOWN"}], [], policy(), "b", "2026-10-12T00:00:00Z")
    assert deferred["state"] == "DEFERRED_LIMIT" and deferred["attempts"] == 0


def test_missing_dimensions_blocked_and_attempt_limit():
    blocked = queue([group("a", record("a US", length=None))])[0]
    assert blocked["state"] == "BLOCKED_INPUT" and not select_tasks([blocked], policy(), 8)
    row = queue([group("a", record("a US"))])[0]
    row.update(state="NO_EVIDENCE", attempts=3)
    assert not select_tasks([row], policy(), 8)


def test_default_us_only_explicit_market_and_model_diversity():
    groups = [group("eu", record("eu EU", market="EU")), group("us", record("us US")),
              group("us2", record("us2 US", body="Sedan")), group("o", record("o US", model="Other"))]
    rows = queue(groups)
    picked = select_tasks(rows, policy(), 8)
    assert {r["market"] for r in picked} == {"US"} and {r["model"] for r in picked} == {"Test", "Other"}
    assert [r["market"] for r in select_tasks(rows, policy(), 8, markets=["EU"])] == ["EU"]


def test_kickoff_and_ambiguity_priority():
    groups = [group("a", record("a US")), group("k", {**record("k US"), "make": "Kia", "model": "Soul"})]
    rows = refresh_queue(groups, [audit("a", ["SPORT_LIFTBACK"]), audit("k")], outcomes(groups), [], policy())
    assert [r["priority_reason"] for r in rows] == ["kickoff", "ambiguous"]
