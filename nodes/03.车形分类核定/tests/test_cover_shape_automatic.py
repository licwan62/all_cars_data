"""自动检索/几何/分类门禁回归；合成图片只作为算法测试，非车型金标准。"""
from __future__ import annotations

import copy
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
import yaml
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "code"))
from cover_shape.automatic import AutomaticCollector, licence, metadata_match
from cover_shape.automatic_geometry import GeometryError, analyze_mask, candidate_from_features, load_image
from cover_shape.classifier import classify
from cover_shape.evidence import make_evidence, validate
from cover_shape.fetchers import FetchError, HttpClient
from cover_shape.ingest import discover, normalize

STAMP = "2026-10-12T12:00:00Z"


@pytest.fixture
def policy():
    return yaml.safe_load((PROJECT / "data/cover_shape/automatic.yaml").read_text(encoding="utf-8"))


def record(body="Hatchback", year=2025, height=1300):
    raw = {"make": "Synthetic", "model": "TestCar", "model_year": str(year), "generation": "TEST",
           "body_type": body, "market": "TEST", "length_mm": "4400", "height_mm": str(height)}
    return normalize([raw], discover(list(raw)), "synthetic-only")[0]


def page(title="File:2025 Synthetic TestCar Hatchback.jpg", description="Synthetic TestCar", license_name="CC BY-SA 4.0"):
    return {"pageid": 1, "title": title, "categories": [], "imageinfo": [{"mime": "image/jpeg",
            "descriptionurl": "https://commons.wikimedia.org/wiki/File:Synthetic.jpg", "url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Synthetic.jpg",
            "extmetadata": {"LicenseShortName": {"value": license_name}, "ImageDescription": {"value": description},
                            "Artist": {"value": "SYNTHETIC TEST"}, "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0/"}}}]}


def synthetic_geometry(kind="slope"):
    rgb = np.full((650, 1400, 3), 255, np.uint8)
    mask = np.zeros(rgb.shape[:2], np.float32)
    rear = [(865, 100), (1210, 320), (1250, 360)] if kind == "slope" else (
           [(865, 100), (980, 250), (1250, 250)] if kind == "notch" else [(1160, 100), (1250, 320)])
    points = np.array([(150, 350), (370, 310), (560, 100), *rear, (1250, 450), (150, 450)], np.int32)
    cv2.fillPoly(mask, [points], 1)
    rgb[mask > .5] = (90, 160, 210)
    for x in [420, 1020]:
        cv2.circle(mask, (x, 430), 75, 1, -1)
        cv2.circle(rgb, (x, 430), 75, (30, 30, 30), -1)
        cv2.circle(rgb, (x, 430), 48, (180, 180, 180), 4)
    return rgb, mask, ([[420, 430], [1020, 430]], [75, 75])


def test_exact_model_year_and_variant_not_capture_date(policy):
    r = record()
    assert metadata_match(page(), r, policy, True)["acceptable_for_inference"]
    for title in ["File:2024 Synthetic TestCar Hatchback.jpg", "File:Synthetic TestCar at car show 2025-05-21.jpg",
                  "File:2025 Synthetic DifferentCar Hatchback.jpg", "File:2025 Synthetic TestCar Coupe.jpg"]:
        assert not metadata_match(page(title), r, policy, True)["acceptable_for_inference"]


def test_same_year_coupe_hatch_cannot_share_metadata(policy):
    picture = page()
    assert metadata_match(picture, record("Hatchback"), policy, True)["acceptable_for_inference"]
    assert not metadata_match(picture, record("Coupe"), policy, True)["acceptable_for_inference"]


@pytest.mark.parametrize("keyword", ["rendering", "ai-generated", "lowered", "modified", "miniature", "interior"])
def test_generated_modified_or_non_vehicle_sources_rejected(policy, keyword):
    assert not metadata_match(page(description="Synthetic TestCar " + keyword), record(), policy, False)["acceptable_for_inference"]


def test_license_missing_rejected_and_attribution_preserved(policy):
    assert licence(page(license_name="All rights reserved")["imageinfo"][0], policy["allowed_licenses"]) is None
    result = licence(page()["imageinfo"][0], policy["allowed_licenses"])
    assert result["author"] == "SYNTHETIC TEST" and result["source_page"].startswith("https://commons.wikimedia.org/")


def test_mask_and_shape_reproducible_without_manual_annotations(policy):
    rgb, mask, wheels = synthetic_geometry()
    a, overlay = analyze_mask(rgb, mask, policy["geometry"], wheels)
    b, _ = analyze_mask(rgb, mask, policy["geometry"], wheels)
    assert a == b and len(a["top_profile_64"]) == 64
    assert a["measurement_units"] == "relative_shape" and overlay.startswith(b"\x89PNG")
    label = candidate_from_features(a, {"length_mm": 4400, "height_mm": 1300}, policy["classification"])
    assert label["label"] == "LOW_FASTBACK"


def test_geometry_discriminates_notch_and_box_without_bodytype(policy):
    rgb, mask, wheels = synthetic_geometry("notch")
    feature, _ = analyze_mask(rgb, mask, policy["geometry"], wheels)
    assert candidate_from_features(feature, {"length_mm": 4400, "height_mm": 1300}, policy["classification"])["label"] == "LOW_NOTCHBACK"
    rgb, mask, wheels = synthetic_geometry("box")
    feature, _ = analyze_mask(rgb, mask, policy["geometry"], wheels)
    assert candidate_from_features(feature, {"length_mm": 4200, "height_mm": 1650}, policy["classification"])["label"] == "TALL_BOX"


def test_bad_masks_missing_dimensions_not_forced(policy):
    rgb, mask, wheels = synthetic_geometry()
    with pytest.raises(GeometryError): analyze_mask(rgb, np.zeros_like(mask), policy["geometry"], wheels)
    mask[:, :160] = 1
    with pytest.raises(GeometryError): analyze_mask(rgb, mask, policy["geometry"], wheels)
    assert candidate_from_features({"usable": True}, {"length_mm": None, "height_mm": None}, policy["classification"])["label"] == "UNKNOWN"


def test_automatic_candidate_is_inferred_and_never_fit_tested(policy):
    r = record()
    rgb, mask, wheels = synthetic_geometry()
    feature, _ = analyze_mask(rgb, mask, policy["geometry"], wheels)
    item = make_evidence(r, "automatic_profile", "https://commons.wikimedia.org/wiki/File:Synthetic.jpg", "SYNTHETIC TEST",
                         STAMP, {"automatic": True, "features": feature, "identity_match": {"acceptable_for_inference": True}}, [], "B", "a" * 64)
    tax = yaml.safe_load((PROJECT / "data/cover_shape/taxonomy_v1.yaml").read_text(encoding="utf-8"))
    result, _ = classify(r, [item], tax, policy)
    assert result["status"] == "INFERRED" and result["cover_shape"] == "LOW_FASTBACK"
    assert result["review_required"] and result["fit_status"] == "NOT_TESTED"
    assert "EXPERIMENTAL_RULES_NOT_CALIBRATED" in result["reason_codes"]
    wrong = copy.deepcopy(item)
    wrong["variant_key"] = "different-generation"
    assert classify(r, [wrong], tax, policy)[0]["cover_shape"] == "UNKNOWN"
    wrong = copy.deepcopy(item)
    wrong["data_payload"]["features"]["top_profile_64"] = []
    with pytest.raises(ValueError): validate(wrong)


def test_api_and_media_access_requires_explicit_registration(tmp_path, monkeypatch):
    sources = {"allowed_domains": ["commons.wikimedia.org", "upload.wikimedia.org"],
               "documented_api_endpoints": ["https://commons.wikimedia.org/w/api.php"],
               "licensed_media_domains": ["upload.wikimedia.org"]}
    client = HttpClient(sources, tmp_path, 4)
    called = []
    monkeypatch.setattr(client, "_request", lambda url: called.append(url) or b"registered")
    assert client.documented_api("https://commons.wikimedia.org/w/api.php?action=query") == b"registered"
    with pytest.raises(FetchError): client.documented_api("https://commons.wikimedia.org/wiki/Page")
    with pytest.raises(FetchError): client.licensed_media("https://upload.wikimedia.org/car.jpg", {})
    assert client.licensed_media("https://upload.wikimedia.org/car.jpg", {"name": "CC0", "source_page": "https://commons.wikimedia.org/wiki/File:Car.jpg"}) == b"registered"


def test_collection_failures_are_evidence_no_user_images_required(policy):
    class FakeClient:
        def documented_api(self, url): return json.dumps({"error": {"code": "maxlag"}}).encode()
    r = record()
    evidence = AutomaticCollector(FakeClient(), policy, [r]).collect(r, STAMP)
    assert len(evidence) == 4 and evidence[-1]["data_payload"]["outcome"] == "NO_ACCEPTED_IMAGE"
    assert evidence[0]["data_payload"]["error_code"].startswith("COMMONS_API_ERROR:")


@pytest.mark.parametrize("title", ["File:Moscow, Kia Soul, Aug 2025 01.jpg", "File:Kia Soul at car show 2025-05-21.jpg"])
def test_capture_year_never_promoted_to_model_year(policy, title):
    r = {**record(), "make": "Kia", "model": "Soul"}
    assert not metadata_match(page(title, description="Kia Soul"), r, policy, False)["model_year_confirmed"]


def test_model_comparison_in_description_not_the_photographed_vehicle(policy):
    r = {**record(year=1974), "make": "Ford", "model": "Mustang"}
    p = page("File:1974 Ford XB Fairmont GS Hardtop.jpg", description="Compared to the Ford Mustang")
    assert not metadata_match(p, r, policy, False)["acceptable_for_inference"]


def test_performance_trim_not_used_for_base_variant(policy):
    r = {**record(), "make": "Honda", "model": "Civic"}
    assert not metadata_match(page("File:2025 Honda Civic Type R.jpg", "Honda Civic"), r, policy, False)["acceptable_for_inference"]


def test_hough_pair_requires_real_dark_tires_not_body_circles(policy):
    rgb, mask, _ = synthetic_geometry()
    feature, _ = analyze_mask(rgb, mask, policy["geometry"])
    assert feature["image_quality"]["geometry_gate_passed"]
    rgb[:] = 230
    with pytest.raises(GeometryError): analyze_mask(rgb, mask, policy["geometry"])


def test_explicit_model_year_contradiction_cannot_be_overridden_by_categories(policy):
    r = {**record(year=2020), "make": "Toyota", "model": "Yaris"}
    p = page("File:2023 Toyota Yaris Cross.jpg", "2020 Toyota Yaris")
    p["categories"] = [{"title": "Category:2020 Toyota Yaris"}]
    assert not metadata_match(p, r, policy, False)["acceptable_for_inference"]
