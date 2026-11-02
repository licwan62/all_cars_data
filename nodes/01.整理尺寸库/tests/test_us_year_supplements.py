import hashlib
import copy
import json
import sys
from pathlib import Path

import pytest

NODE = Path(__file__).resolve().parents[1]
ROOT = NODE.parents[1]
sys.path[:0] = [str(ROOT / "lib"), str(NODE / "code")]
from us_year_supplements import apply_supplements


def test_mirage_1991_height_is_resolved_by_same_year_gs_brochure():
    rules = json.loads((NODE / "data/us/year_gap_resolutions.json").read_text(encoding="utf-8-sig"))
    item = next(r for r in rules["resolutions"]
                if (r["make"], r["model"], r["year"]) == ("Mitsubishi", "Mirage", 1991))
    assert item["status"] == "verified_add"
    assert item["record"]["结构"] == "Sedan"
    assert item["record"]["H-IN"] == "52.8"
    assert any(s.get("dimensions", {}).get("H-IN") == "55.3" for s in item["sources"])
    brochure = next(s for s in item["sources"]
                    if s.get("evidence_type") == "original_us_brochure_dimension_crosscheck")
    assert brochure["year"] == 1991 and brochure["selected_trim"].startswith("Mirage GS")
    assert brochure["dimensions"]["H-IN"] == "52.8"
    rows = [{"DIMENSION-ID": "baseline", "MAKE": "Other", "MODEL": "Car", "YEAR": "2000"}]
    result, review = apply_supplements(rows, {"resolutions": [item]}, NODE)
    assert result[-1]["DIMENSION-ID"] == "Mitsubishi Mirage Sedan 1991 US"
    assert review[0]["处理结果"] == "verified_add"


@pytest.mark.parametrize("make,model,year", [
    ("Volkswagen", "Golf", 1986),
    ("Volkswagen", "Golf", 1988),
    ("Plymouth", "Sundance", 1987),
])
def test_original_us_brochure_does_not_resolve_unspecified_mirror_width(make, model, year):
    rules = json.loads((NODE / "data/us/year_gap_resolutions.json").read_text(encoding="utf-8-sig"))
    item = next(r for r in rules["resolutions"]
                if (r["make"], r["model"], r["year"]) == (make, model, year))
    assert item["status"] == "pending"
    assert any(s.get("file", "").endswith(".jpg") and s.get("market") == "US"
               for s in item["sources"])
    rows = [{"DIMENSION-ID": "baseline", "MAKE": "Other", "MODEL": "Car", "YEAR": "2000"}]
    result, review = apply_supplements(rows, {"resolutions": [item]}, NODE)
    assert result == rows
    assert review[0]["DIMENSION-ID"] == ""
    proposed = copy.deepcopy(item)
    proposed["status"] = "verified_add"
    with pytest.raises(ValueError, match="同年美国同车身证据"):
        apply_supplements(rows, {"resolutions": [proposed]}, NODE)


def test_local_evidence_is_checked_and_cannot_escape_data(tmp_path):
    evidence = tmp_path / "data/us/evidence/document.pdf"
    evidence.parent.mkdir(parents=True)
    evidence.write_bytes(b"original")
    rules = {"resolutions": [{"make": "A", "model": "M", "year": 2020,
        "status": "pending", "reason": "awaiting review", "sources": [{
            "url": "https://example.com/document.pdf", "file": "data/us/evidence/document.pdf",
            "sha256": hashlib.sha256(b"original").hexdigest()}]}]}
    rows = [{"DIMENSION-ID": "existing", "MAKE": "A", "MODEL": "M", "YEAR": "2019"}]
    result, review = apply_supplements(rows, rules, tmp_path)
    assert result == rows and review[0]["处理结果"] == "pending"
    evidence.write_bytes(b"changed")
    with pytest.raises(ValueError, match="SHA"):
        apply_supplements(rows, rules, tmp_path)
    rules["resolutions"][0]["sources"][0]["file"] = "../outside.pdf"
    with pytest.raises(ValueError, match="节点data目录"):
        apply_supplements(rows, rules, tmp_path)


def test_generation_requires_evidence_for_the_same_market_and_year():
    rows = [{"DIMENSION-ID": "A M Sedan 2019 US", "MAKE": "A", "MODEL": "M", "YEAR": "2019"}]
    dimensions = {"L-IN": "180", "W-IN": "70", "H-IN": "55"}
    rules = {"resolutions": [{"make": "A", "model": "M", "year": 2020,
        "status": "verified_add", "reason": "reviewed", "record": {
            "结构": "Sedan", "代际": "gen2", "参考车型": "2020 A M Sedan", **dimensions},
        "sources": [{"url": "https://example.com/specs", "market": "US", "year": 2020,
            "body": "Sedan", "width_basis": "without_mirrors", "dimensions": dimensions}]}]}
    with pytest.raises(ValueError, match="代际"):
        apply_supplements(rows, rules)
    source = {"url": "https://example.com/history", "evidence_type": "generation_continuity",
              "market": "US", "year": 2019, "generation": "gen2"}
    rules["resolutions"][0]["sources"].append(source)
    with pytest.raises(ValueError, match="代际"):
        apply_supplements(rows, rules)
    source["year"] = 2020
    result, _ = apply_supplements(rows, rules)
    assert result[-1]["代际"] == "gen2"


def test_approximate_add_is_added_with_pending_final_review_status():
    rules = json.loads((NODE / "data/us/year_gap_resolutions.json").read_text(encoding="utf-8-sig"))
    approx = [r for r in rules["resolutions"] if r["status"] == "approximate_add"]
    assert approx and all(r["record"]["迭代状态"].startswith("待终核") and r["record"]["备注"] for r in approx)
    item = copy.deepcopy(approx[0])
    rows = [{"DIMENSION-ID": "baseline", "MAKE": "Other", "MODEL": "Car", "YEAR": "2000", "迭代状态": ""}]
    result, review = apply_supplements(rows, {"resolutions": [item]}, NODE)
    assert result[-1]["迭代状态"].startswith("待终核")
    assert review[0]["处理结果"] == "approximate_add"
    item["record"]["迭代状态"] = "可入库"
    with pytest.raises(ValueError):
        apply_supplements(rows, {"resolutions": [item]}, NODE)
