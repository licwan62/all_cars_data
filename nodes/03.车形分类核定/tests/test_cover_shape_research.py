"""合成几何仅测试算法/门禁，不是对真实车型的证据或人工金标准。"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import urllib.error
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "code"))
from cover_shape import cli
from cover_shape.classifier import classify, validate_taxonomy
from cover_shape.evidence import exact_match, make_evidence, validate
from cover_shape.fetchers import FetchError, HttpClient, cvs_evidence, parse_cvs
from cover_shape.geometry import profile_features
from cover_shape.ingest import digest, discover, identity, inspect_table, normalize, read_table

STAMP = "2026-10-12T00:00:00Z"


@pytest.fixture
def taxonomy():
    return yaml.safe_load((PROJECT / "data/cover_shape/taxonomy_v1.yaml").read_text(encoding="utf-8"))


@pytest.fixture
def record():
    row = {"id": "sample-1", "make": "SYNTHETIC", "model": "TestCar", "model_year": "2025", "body_type": "Hatchback",
           "generation": "TEST", "market": "TEST", "length_mm": "4000", "width_mm": "1800", "height_mm": "1500"}
    mapping = discover(list(row))
    mapping["width_definition"] = "excluding_mirrors"
    return normalize([row], mapping, "test-file")[0]


@pytest.fixture
def profile(record):
    payload = {"quality": {k: True for k in ("identity_confirmed", "full_vehicle", "unoccluded", "low_perspective", "stock_vehicle", "real_image")},
               "annotation": {"front_x": 0, "rear_x": 1000, "ground_y": 500,
                              "wheel_centers": [[200, 400], [800, 400]], "wheel_radii": [90, 90],
                              "top_points": [[0, 350], [200, 300], [400, 100], [650, 100], [900, 300], [1000, 350]],
                              "hood_end_x": 200, "roof_start_x": 400, "roof_end_x": 650, "rear_deck_start_x": 900},
               "independent_source_id": "synthetic-a"}
    return make_evidence(record, "side_profile", "https://fixtures.example.org/a", "SYNTHETIC TEST ONLY", STAMP,
                         payload, [], "B", "a" * 64, license_note="Synthetic test data; not real vehicle evidence")


def calibrated(taxonomy, feature, label="LOW_FASTBACK"):
    result = copy.deepcopy(taxonomy)
    keys = ("hood_ratio", "roof_start_x", "roof_end_x", "rear_deck_ratio")
    result["prototypes"] = [{"id": "synthetic-only", "label": label, "features": {k: feature[k] for k in keys},
                             "scales": {k: 0.1 for k in keys}, "max_distance": 0.5, "reviewed": True,
                             "reviewer": "SYNTHETIC_TEST", "reviewed_at_utc": STAMP,
                             "calibration_evidence_ids": ["synthetic-only-not-factual"]}]
    return result


def test_real_pilot_is_pending_and_all_hatchbacks_not_mapped(taxonomy):
    _, rows = read_table(PROJECT / "data/cover_shape/pilot_cases.csv")
    assert len(rows) == 8 and all(r["review_status"] == "PENDING" for r in rows)
    assert taxonomy["prototypes"] == []


def test_exact_identity_splits_generation_body_year_trim_and_market(record, profile):
    assert exact_match(profile, record)
    for key, value in [("model_year", 2024), ("body_type", "Coupe"), ("generation", "OLD"), ("trim", "GT"), ("market", "CA")]:
        altered = {**record, key: value}
        altered["variant_key"] = identity(altered)
        assert altered["variant_key"] != record["variant_key"]
        assert not exact_match(profile, altered)


def test_inches_original_values_and_stable_id():
    row = {"MAKE": " Ford ", "MODEL": "Mustang", "YEAR": "1973-1974", "L-IN": "175", "结构": "Coupe"}
    mapping = discover(list(row))
    records = normalize([row], mapping, "frozen-hash")
    assert [r["model_year"] for r in records] == [1973, 1974]
    assert records[0]["length_mm"] == 4445
    assert records[0]["raw_fields"]["MAKE"] == " Ford "
    assert records[0]["source_record_id"] == "frozen-hash:row:2"
    assert records[0].get("market", "") == ""
    assert records[0]["variant_key"] != records[1]["variant_key"]
    assert records == normalize([row], mapping, "frozen-hash")


@pytest.mark.parametrize("value", ["NaN", "inf", "-1", "0", "unknown"])
def test_invalid_dimensions_remain_missing(value):
    row = {"make": "A", "model": "B", "model_year": "2025", "length_mm": value}
    out = normalize([row], discover(list(row)), "id")[0]
    assert out["length_mm"] is None and "INVALID_LENGTH_MM" in out["identity_flags"]


def test_ambiguous_columns_are_not_silently_selected():
    mapping = discover(["MAKE", "make", "MODEL"])
    assert mapping["ambiguities"]["make"] == ["MAKE", "make"]
    assert "make" not in mapping["columns"]


def test_inspection_reports_duplicates_and_preserves_hash(tmp_path):
    path = tmp_path / "cars.csv"
    path.write_text("id,make,model,model_year\n1,A,B,2025\n1,A,B,2025\n", encoding="utf-8")
    before = digest(path)
    report = inspect_table(path)
    assert report["duplicate_source_ids"] == {"1": 2}
    assert report["exact_duplicate_rows"] == 1
    assert report["sha256_before"] == report["sha256_after"] == before == digest(path)


def test_xlsx_read_only(tmp_path):
    from openpyxl import Workbook
    path = tmp_path / "cars.xlsx"
    book = Workbook()
    book.active.append(["make", "model", "model_year"])
    book.active.append(["A", "B", 2025])
    book.save(path)
    before = digest(path)
    columns, rows = read_table(path)
    assert normalize(rows, discover(columns), before)[0]["model_year"] == 2025
    assert digest(path) == before


def test_profile_has_deterministic_64_points_and_relative_units(profile, taxonomy):
    first = profile_features(profile["data_payload"], taxonomy["image_gate"])
    assert first == profile_features(profile["data_payload"], taxonomy["image_gate"])
    assert first["usable"] and len(first["top_profile_64"]) == 64
    assert first["measurement_units"] == "relative_shape"
    assert first["hood_ratio"] == 0.2 and first["roof_plateau_ratio"] == 0.25
    assert first["rear_slope_index"] == 2


@pytest.mark.parametrize("problem", ["low_perspective", "real_image", "stock_vehicle", "full_vehicle", "unoccluded", "identity_confirmed"])
def test_bad_or_generated_images_rejected(profile, taxonomy, problem):
    profile["data_payload"]["quality"][problem] = False
    feature = profile_features(profile["data_payload"], taxonomy["image_gate"])
    assert not feature["usable"] and feature["top_profile_64"] == []


def test_wheel_gate_and_missing_interval(profile, taxonomy):
    profile["data_payload"]["annotation"]["wheel_radii"][1] = 130
    assert not profile_features(profile["data_payload"], taxonomy["image_gate"])["usable"]
    profile["data_payload"]["annotation"]["wheel_radii"][1] = 90
    profile["data_payload"]["missing_intervals"] = [[0.4, 0.5]]
    feature = profile_features(profile["data_payload"], taxonomy["image_gate"])
    assert not feature["usable"] and any(v is None for v in feature["top_profile_64"])


def test_unreviewed_prototype_rejected(record, profile, taxonomy):
    feature = profile_features(profile["data_payload"], taxonomy["image_gate"])
    calibrated_tax = calibrated(taxonomy, feature)
    calibrated_tax["prototypes"][0]["reviewed"] = False
    with pytest.raises(ValueError):
        validate_taxonomy(calibrated_tax)


def test_no_evidence_and_uncalibrated_data_stay_unknown(record, profile, taxonomy):
    for evidence in ([], [profile]):
        result, _ = classify(record, evidence, taxonomy)
        assert result["cover_shape"] == "UNKNOWN" and result["status"] == "UNKNOWN"
        assert result["review_required"] and result["fit_status"] == "NOT_TESTED"


def test_hatchback_not_a_classification_feature(record, profile, taxonomy):
    feature = profile_features(profile["data_payload"], taxonomy["image_gate"])
    tax = calibrated(taxonomy, feature)
    result, _ = classify(record, [profile], tax)
    assert result["cover_shape"] == "LOW_FASTBACK" and result["status"] == "PROBABLE"
    assert record["body_type"] == "Hatchback"
    changed = copy.deepcopy(profile)
    changed["data_payload"]["annotation"]["roof_start_x"] = 300
    changed["data_payload"]["annotation"]["roof_end_x"] = 800
    assert classify(record, [changed], tax)[0]["cover_shape"] == "UNKNOWN"


def test_verified_requires_independent_geometry_and_authority(record, profile, taxonomy):
    feature = profile_features(profile["data_payload"], taxonomy["image_gate"])
    tax = calibrated(taxonomy, feature)
    dim = make_evidence(record, "dimensions", "https://factory.example.net/spec", "SYNTHETIC FACTORY", STAMP,
                        {"length_mm": 4000, "height_mm": 1500, "identity_confirmed": True}, [], "A")
    second = copy.deepcopy(profile)
    second.update(evidence_id="second", source_url="https://independent.example.net/profile", sha256="b" * 64)
    second["data_payload"]["independent_source_id"] = "synthetic-b"
    assert classify(record, [profile, dim], tax)[0]["status"] == "PROBABLE"
    assert classify(record, [profile, second, dim], tax)[0]["status"] == "VERIFIED"
    second["sha256"] = profile["sha256"]
    assert classify(record, [profile, second, dim], tax)[0]["status"] == "PROBABLE"


def test_profile_conflict_kept_not_averaged(record, profile, taxonomy):
    feature = profile_features(profile["data_payload"], taxonomy["image_gate"])
    second = copy.deepcopy(profile)
    second["evidence_id"] = "other"
    second["data_payload"]["annotation"]["top_points"][3][1] = 250
    result, features = classify(record, [profile, second], calibrated(taxonomy, feature))
    assert result["status"] == "CONFLICT" and result["review_required"]
    assert "PROFILE_CONFLICT" in result["reason_codes"]
    assert features["top_profile_64"] == feature["top_profile_64"]


def test_dimensions_and_wrong_identity_conflicts(record, profile, taxonomy):
    feature = profile_features(profile["data_payload"], taxonomy["image_gate"])
    dims = make_evidence(record, "dimensions", "https://fixtures.example.org/d", "SYNTHETIC", STAMP,
                         {"length_mm": 5000}, [], "A")
    assert classify(record, [profile, dims], calibrated(taxonomy, feature))[0]["status"] == "CONFLICT"
    wrong = copy.deepcopy(profile)
    wrong["variant_claim"]["body_type"] = "Coupe"
    assert classify(record, [wrong], taxonomy)[0]["status"] == "CONFLICT"


def test_multiple_candidates_require_review(record, profile, taxonomy):
    feature = profile_features(profile["data_payload"], taxonomy["image_gate"])
    tax = calibrated(taxonomy, feature)
    tax["prototypes"].append({**tax["prototypes"][0], "id": "other", "label": "SPORT_LIFTBACK"})
    result, _ = classify(record, [profile], tax)
    assert result["alternate_shapes"] == ["SPORT_LIFTBACK"] and result["review_required"]


def test_schema_and_local_hash_required(profile):
    validate(profile)
    profile["data_payload"]["local_content"] = True
    profile["sha256"] = ""
    with pytest.raises(ValueError):
        validate(profile)


def cvs_fixture():
    # 合成响应形状；字段/单位来自官方定义，非车型事实。
    return {"Count": 1, "Message": "synthetic", "Results": [{"Specs": [{"Name": k, "Value": v} for k, v in
            {"Make": "SYNTHETIC", "Model": "TestCar", "MYR": "11", "OL": "400", "OW": "180", "OH": "150", "WB": "260", "B": "80"}.items()]}]}


def test_actual_cvs_schema_and_cm_conversion(record):
    payload = cvs_fixture()
    assert parse_cvs(payload)[0]["OL"] == "400"
    class FakeClient:
        def get(self, url):
            return json.dumps(payload).encode()
    evidence = cvs_evidence(record, FakeClient(), STAMP)
    assert evidence["data_payload"]["length_mm"] == 4000
    assert evidence["data_payload"]["outcome"] == "UNCONFIRMED_MATCH"
    assert evidence["market_claim"] == "CA" and not exact_match(evidence, record)
    assert evidence["data_payload"]["MYR_definition"].startswith("last two")
    assert "rear_deck_ratio" not in evidence["data_payload"]
    payload["Results"][0] = {"OL": "400"}
    with pytest.raises(FetchError):
        parse_cvs(payload)


def test_cvs_partial_model_missing_data_and_failure(record):
    class FakeClient:
        def get(self, url):
            payload = cvs_fixture()
            payload["Results"][0]["Specs"][1]["Value"] = "TestCar 4DR"
            return json.dumps(payload).encode()
    e = cvs_evidence(record, FakeClient(), STAMP)
    assert "CVS_VARIANT_AMBIGUOUS" in e["validation_flags"]
    assert "length_mm" not in e["data_payload"]
    assert e["data_payload"]["outcome"] == "VARIANT_AMBIGUOUS"
    class FailedClient:
        def get(self, url):
            raise FetchError("HTTP_403")
    e = cvs_evidence(record, FailedClient(), STAMP)
    assert e["data_payload"]["error_code"] == "HTTP_403"


def test_network_whitelist_robots_cache_and_budget(tmp_path, monkeypatch):
    sources = {"allowed_domains": ["fixtures.example.org"], "seconds_per_request": 1, "timeout_seconds": 1, "retries": 0}
    client = HttpClient(sources, tmp_path, 2)
    monkeypatch.setattr("cover_shape.fetchers.time.sleep", lambda seconds: None)
    class Response:
        def __init__(self, body): self.body = body
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, limit): return self.body
    class Opener:
        def open(self, request, timeout):
            return Response(b"User-agent: *\nDisallow: /blocked\n" if request.full_url.endswith("robots.txt") else b"fixture")
    client.opener = Opener()
    assert client.get("https://fixtures.example.org/allowed") == b"fixture"
    assert client.get("https://fixtures.example.org/allowed") == b"fixture"
    assert client.count == 2 and client.cache_hits == 1
    for url in ("https://unlisted.example.org/", "https://fixtures.example.org/blocked", "https://fixtures.example.org/new",
                "https://fixtures.example.org/?api_key=secret", "https://user:pass@fixtures.example.org/"):
        with pytest.raises(FetchError): client.get(url)
    (next(tmp_path.glob("*.body"))).write_bytes(b"tampered")
    fresh = HttpClient(sources, tmp_path, 2)
    with pytest.raises(FetchError, match="CACHE_HASH_MISMATCH"):
        fresh.get("https://fixtures.example.org/allowed")


def test_offline_e2e_and_reclassify_preserve_unknown_without_network(tmp_path, monkeypatch, capsys):
    # 八个明确身份的合成输入，不伪造真实来源；没有证据必须八个 UNKNOWN。
    project = tmp_path / "node"
    (project / "data").mkdir(parents=True)
    rules = project / "data"
    mapping = discover(["id", "make", "model", "model_year", "generation", "body_type", "market"])
    for name, value in [("column_map.yaml", mapping), ("taxonomy.yaml", yaml.safe_load((PROJECT / "data/cover_shape/taxonomy_v1.yaml").read_text(encoding="utf-8"))),
                        ("sources.yaml", {"allowed_domains": [], "seconds_per_request": 1}),
                        ("pipeline.yaml", {"column_map": "column_map.yaml", "taxonomy": "taxonomy.yaml", "sources": "sources.yaml", "evidence": "evidence.jsonl"})]:
        (rules / name).write_text(yaml.safe_dump(value), encoding="utf-8")
    input_path = rules / "input.csv"
    input_path.write_text("id,make,model,model_year,generation,body_type,market\n" +
                          "".join(f"{i},SYNTHETIC,Case{i},2025,TEST,Hatchback,TEST\n" for i in range(8)), encoding="utf-8")
    before = digest(input_path)
    monkeypatch.setattr(cli, "PROJECT", project)
    def forbidden(*args, **kwargs): raise AssertionError("offline network")
    monkeypatch.setattr(HttpClient, "get", forbidden)
    cli.main(["run", "--input", str(input_path), "--config", str(rules / "pipeline.yaml")])
    batch = next((project / "artifacts").iterdir())
    results = list(__import__("csv").DictReader(next((batch / "output").glob("cover_shape_results-*.csv")).open(encoding="utf-8-sig")))
    assert len(results) == 8 and {r["status"] for r in results} == {"UNKNOWN"}
    assert digest(input_path) == before and not (project / "output").exists()
    assert json.loads((batch / "run.json").read_text(encoding="utf-8"))["status"]["status"] == "passed"
    evidence_path = next((batch / "output").glob("evidence-*.jsonl"))
    cli.main(["reclassify", "--evidence", str(evidence_path), "--taxonomy", str(rules / "taxonomy.yaml")])
    rerun = sorted((project / "artifacts").iterdir())[-1]
    actual = list(__import__("csv").DictReader(next((rerun / "output").glob("cover_shape_results-*.csv")).open(encoding="utf-8-sig")))
    for a, b in zip(results, actual):
        assert {k: v for k, v in a.items() if k != "processed_at_utc"} == {k: v for k, v in b.items() if k != "processed_at_utc"}
    cli.main(["run", "--input", str(input_path), "--config", str(rules / "pipeline.yaml")])
    assert len(list((project / "artifacts").iterdir())) == 3


def test_online_requires_explicit_limit(tmp_path):
    with pytest.raises(SystemExit) as e:
        cli.main(["run", "--input", str(tmp_path / "not_read.csv"), "--mode", "online"])
    assert e.value.code == 2


def test_failed_run_does_not_change_output(tmp_path, monkeypatch):
    project = tmp_path / "node"
    (project / "data").mkdir(parents=True)
    (project / "output").mkdir()
    existing = project / "output" / "stable.csv"
    existing.write_bytes(b"unchanged")
    path = project / "data" / "bad.csv"
    path.write_text("MAKE,MODEL\nA,B\n", encoding="utf-8")
    monkeypatch.setattr(cli, "PROJECT", project)
    with pytest.raises(SystemExit): cli.main(["run", "--input", str(path)])
    batch = next((project / "artifacts").iterdir())
    assert json.loads((batch / "run.json").read_text(encoding="utf-8"))["status"]["status"] == "failed"
    assert existing.read_bytes() == b"unchanged"
