from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "code"))
from cover_shape.automatic_documents import DocumentText, collect_documents, describe_candidate, geometric_descriptions
from cover_shape.classifier import classify
from cover_shape.ingest import discover, normalize


@pytest.fixture
def policy():
    return yaml.safe_load((PROJECT / "data/cover_shape/automatic.yaml").read_text(encoding="utf-8"))


def test_body_type_alone_and_marketing_text_do_not_classify(policy):
    assert geometric_descriptions(["This is a hatchback. Stylish and sporty coupe. Great cargo space."], policy["description_lexicon"])["observations"] == {}
    assert describe_candidate({}, {"length_mm": 4200, "height_mm": 1600}, policy["classification"])["label"] == "UNKNOWN"


def test_shared_page_separates_coupe_and_hatchback_description(policy):
    # 合成分句；几何词和数值验证，不是生产车型证据。
    sentence = 'A two-door notchback has a separate trunk, and a three-door hatchback has a sloping roofline.'
    coupe = geometric_descriptions([sentence], policy["description_lexicon"], policy["body_identity_aliases"]["coupe"])
    hatch = geometric_descriptions([sentence], policy["description_lexicon"], policy["body_identity_aliases"]["hatchback"])
    assert coupe["observations"] == {"rear_step": True}
    assert hatch["observations"] == {"roof_slope": True}
    assert describe_candidate(coupe["observations"], {"length_mm": 4400, "height_mm": 1300}, policy["classification"])["label"] == "LOW_NOTCHBACK"
    assert describe_candidate(hatch["observations"], {"length_mm": 4400, "height_mm": 1300}, policy["classification"])["label"] == "LOW_FASTBACK"


@pytest.mark.parametrize("sentence", ["It has no longer a fastback roofline.", "A concept has a boxy silhouette.", "The interior has a compact footprint."])
def test_negative_concept_and_interior_geometry_not_used(policy, sentence):
    assert not geometric_descriptions([sentence], policy["description_lexicon"])["observations"]


def test_extraction_does_not_make_64_point_measurement(policy):
    parser = DocumentText()
    parser.feed('<html><title>2025 Synthetic car</title><script>boxy silhouette</script><p>The car has a fastback roofline.</p></html>')
    parser.flush()
    features = geometric_descriptions(parser.chunks, policy["description_lexicon"])
    assert features["observations"] == {"roof_slope": True}
    assert len(features["source_snippets"]["roof_slope"].split()) <= 10


def test_navigation_footer_geometry_is_not_current_vehicle_evidence(policy):
    parser = DocumentText()
    parser.feed('<title>2025 car</title><p>Basic hatchback.</p><footer><p>Other car: boxy silhouette.</p></footer>')
    parser.flush()
    assert not geometric_descriptions(parser.chunks, policy["description_lexicon"])["observations"]


def test_original_body_type_has_no_effect_on_document_classifier(policy):
    observations = {"box_outline": True, "upright_rear": True}
    for body in ["Hatchback", "Wagon", "Sedan"]:
        dimensions = {"body_type": body, "length_mm": 4200, "height_mm": 1650}
        assert describe_candidate(observations, dimensions, policy["classification"])["label"] == "TALL_BOX"


def test_cabin_description_requires_measured_compact_high_proportions(policy):
    obs = geometric_descriptions(["A cab-rearward design positions the cabin."], policy["description_lexicon"])["observations"]
    assert describe_candidate(obs, {"length_mm": 4100, "height_mm": 1500}, policy["classification"])["label"] == "COMPACT_HATCH"
    assert describe_candidate(obs, {"length_mm": 4700, "height_mm": 1500}, policy["classification"])["label"] == "UNKNOWN"


def test_document_e2e_exact_scope_inferred_and_preserves_year_chain(policy):
    raw = {"make": "Synthetic", "model": "TestCar", "model_year": "2025", "body_type": "Hatchback", "generation": "TEST",
           "market": "TEST", "length_mm": "4400", "height_mm": "1400", "YEAR": "2024-2025"}
    mapping = discover(list(raw))
    record = normalize([raw], mapping, "test-only")[0]
    auto = copy.deepcopy(policy)
    auto["document_sources"] = [{"selector": {"make": "Synthetic", "model": "TestCar", "generation": "TEST", "market": "TEST", "body_types": ["Hatchback"]},
                                 "url": "https://factory.example.org/test", "publisher": "SYNTHETIC TEST",
                                 "source_rank": "A", "source_model_year": 2024, "source_market": "TEST", "title_pattern": "2024 Synthetic TestCar"}]
    class Client:
        def get(self, url): return b'<title>2024 Synthetic TestCar</title><p>The car has a fastback roofline.</p>'
    evidence = collect_documents(record, Client(), auto, "2026-10-12T00:00:00Z")
    assert evidence[0]["evidence_type"] == "automatic_description"
    assert evidence[0]["data_payload"]["inference_chain"]["source_year"] == 2024
    assert evidence[0]["model_year_claim"] == 2024
    assert evidence[0]["variant_claim"]["generation"] == ""
    tax = yaml.safe_load((PROJECT / "data/cover_shape/taxonomy_v1.yaml").read_text(encoding="utf-8"))
    result, feature = classify(record, evidence, tax, auto)
    assert result["cover_shape"] == "SPORT_LIFTBACK" and result["status"] == "INFERRED"
    assert feature["top_profile_64"] == [] and feature["measurement_units"] == "qualitative"
    other = {**record, "generation": "OTHER"}
    assert collect_documents(other, Client(), auto, "2026-10-12T00:00:00Z") == []
    record["raw_fields"]["YEAR"] = "2025"
    assert collect_documents(record, Client(), auto, "2026-10-12T00:00:00Z")[0]["data_payload"]["error_code"] == "DOCUMENT_YEAR_OUTSIDE_SOURCE_BRANCH"


@pytest.mark.parametrize("sentence,observation", [
    ("A fastback-style roof describes the external body.", "roof_slope"),
    ("A tapered roofline describes the external body.", "roof_slope"),
    ("A squared body profile describes the external body.", "box_outline"),
    ("The transition from rear quarter glass to the low-slung position of the rear tail is continuous.", "roof_slope"),
])
def test_additional_geometric_phrases_require_actual_shape_description(policy, sentence, observation):
    assert geometric_descriptions([sentence], policy["description_lexicon"])["observations"] == {observation: True}


def test_new_document_sources_exclude_wrong_market_and_special_body_versions(policy):
    raw = {"make": "Acura", "model": "Integra", "model_year": "2024", "body_type": "Hatchback", "generation": "gen5",
           "trim": "Type S", "market": "US", "length_mm": "4700", "height_mm": "1400", "YEAR": "2024-2026"}
    record = normalize([raw], discover(list(raw)), "test-only")[0]
    class Client:
        def get(self, url): raise AssertionError("wrong branch must not request ordinary Integra page")
    assert not collect_documents(record, Client(), policy, "2026-10-12T00:00:00Z")
    record.update(trim="", market="EU")
    assert not collect_documents(record, Client(), policy, "2026-10-12T00:00:00Z")
