import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location("website_node_run", Path(__file__).parents[1] / "src/run.py")
website = importlib.util.module_from_spec(spec)
spec.loader.exec_module(website)


def fixture(tmp_path, monkeypatch, legacy):
    monkeypatch.setattr(website, "ROOT", tmp_path)
    by_id = {}
    node = {"inputs": []}
    for owner, name, old in [("size-calculation", "US/全量/全量表.json", "US/全量/全量表.csv"),
                             ("size-compression", "US/压缩尺码表.json", "US/压缩尺码表.csv")]:
        by_id[owner] = {"id": owner, "path": "nodes/" + owner, "output_dir": "json/" + owner,
                        "interface_files": {old: name}}
        node["inputs"].append({"node": owner, "file": name})
        output = tmp_path / "json" / owner
        path = output / name
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"schema": "vehicle-pipeline/table-v1", "columns": ["DIMENSION-ID", "YEAR"],
                                    "rows": [["0001", "2020"]]}), encoding="utf-8")
        digest = website.sha256(path)
        item = {"file": name, "sha256": digest, "legacy_file": old, "legacy_sha256": "old-csv-digest"}
        manifest = {"node": owner, "version": "v1", "deliverables": [item]}
        if owner == "size-calculation":
            basis = {"file": old if legacy else name, "sha256": "old-csv-digest" if legacy else digest}
        else:
            manifest["upstream"] = [{"node": "size-calculation", "files": [basis]}]
        (output / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    batch = SimpleNamespace(inputs=[])
    batch.input = lambda p: batch.inputs.append({"sha256": website.sha256(p)})
    return batch, node, by_id


@pytest.mark.parametrize("legacy", [True, False])
def test_pin_current_and_migrated_provenance_without_rewriting_official_inputs(tmp_path, monkeypatch, legacy):
    batch, node, by_id = fixture(tmp_path, monkeypatch, legacy)
    before = {p: p.read_bytes() for p in (tmp_path / "json").rglob("*.json")}
    view = tmp_path / "private"
    digests = website.pin_inputs(batch, node, by_id, view)
    csv = view / "size-calculation/US/全量/全量表.csv"
    assert "0001,2020" in csv.read_text(encoding="utf-8-sig")
    a1 = json.loads((view / "size-compression/manifest.json").read_text(encoding="utf-8"))
    assert a1["upstream"][0]["files"][0]["sha256"] == website.sha256(csv)
    assert len(batch.inputs) == 2 and len(digests) == 4
    assert all(p.read_bytes() == content for p, content in before.items())


def test_stale_a1_is_rejected_before_translating_hashes(tmp_path, monkeypatch):
    batch, node, by_id = fixture(tmp_path, monkeypatch, True)
    manifest = tmp_path / "json/size-compression/manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["upstream"][0]["files"][0]["sha256"] = "different-a0"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="does not reference current A0"):
        website.pin_inputs(batch, node, by_id, tmp_path / "private")


def test_unpublished_json_is_rejected(tmp_path, monkeypatch):
    batch, node, by_id = fixture(tmp_path, monkeypatch, False)
    path = tmp_path / "json/size-calculation/US/全量/全量表.json"
    path.write_text('{}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unpublished or changed"):
        website.pin_inputs(batch, node, by_id, tmp_path / "private")


def test_changes_after_pinning_are_rejected(tmp_path, monkeypatch):
    batch, node, by_id = fixture(tmp_path, monkeypatch, False)
    digests = website.pin_inputs(batch, node, by_id, tmp_path / "private")
    path = tmp_path / "json/size-compression/manifest.json"
    path.write_text('{}', encoding="utf-8")
    with pytest.raises(ValueError, match="Input changed during build"):
        website.verify_inputs(digests)
