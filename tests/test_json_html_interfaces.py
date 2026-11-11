import base64
import gzip
import json
from pathlib import Path
import shutil

import pytest
import artifact_batch as ab
from artifact_refs import referenced_batches
from json_interface import SCHEMA, convert, materialize, manifest_hashes, load_table
from migrate_json_interfaces import migrate, migrated_contract
from node_html import build_reports, check_reports
from run_json_node import run_node

REPO = Path(__file__).resolve().parents[1]


def test_rule_metadata_order_alone_does_not_create_a_release():
    from publish_release import release_reasons
    previous = {"deliverables": [], "upstream": [], "rules": [
        {"file": "data/b.json", "sha256": "b", "bytes": 7},
        {"file": "data/a.json", "sha256": "a", "bytes": 9},
    ]}
    current = [{"file": "data/a.json", "sha256": "a"}, {"file": "data/b.json", "sha256": "b"}]
    assert release_reasons(previous, [], [], current, {}) == []


def test_csv_and_tsv_with_same_stem_get_distinct_json_interfaces():
    result = migrated_contract({"directory_contract": {"artifacts": "immutable"}, "nodes": [
        {"id": "sample", "path": "nodes/00.sample", "outputs": ["table.csv", "table.tsv"], "run": [], "public_outputs": []}
    ]})
    assert result["nodes"][0]["outputs"] == ["table.json", "table.tsv.json"]


def fixture(root, monkeypatch):
    monkeypatch.setattr(ab, "REPO_ROOT", root)
    for folder in ("lib", "scripts"):
        shutil.copytree(REPO / folder, root / folder, ignore=shutil.ignore_patterns("__pycache__"))
    nodes = [
        {"id": "up", "path": "nodes/00.up", "outputs": ["表.csv"], "upstream": [], "inputs": [],
         "run": [], "public_outputs": ["表.csv"], "kind": "node", "lifecycle": "active", "line": "U", "code_dir": "src"},
        {"id": "down", "path": "nodes/01.down", "outputs": ["结果.csv"], "upstream": ["up"],
         "inputs": [{"node": "up", "file": "表.csv", "required": True}],
         "run": ["python src/run.py"], "public_outputs": [], "kind": "node", "lifecycle": "active", "line": "U", "code_dir": "src"},
        {"id": "planned", "path": "nodes/02.plan", "outputs": [], "upstream": [], "inputs": [],
         "run": [], "public_outputs": [], "kind": "node", "lifecycle": "planned", "line": "U", "code_dir": "src"},
    ]
    for node in nodes:
        project = root / node["path"]
        for folder in ("output", "data", "src"):
            (project / folder).mkdir(parents=True)
        if node["outputs"]:
            with ab.RunBatch.create(project / "artifacts", "original") as batch:
                batch.output(node["outputs"][0]).write_text('ID,名字\n001,"</script><img src=x onerror=alert(1)>"\n002,"a,b"\n', encoding="utf-8")
                record = batch.finish(publish_to=project / "output")
            manifest = {"node": node["id"], "path": node["path"], "version": record["version"],
                        "artifact": record["batch"], "deliverables": record["outputs"], "rules": [], "upstream": []}
            (project / "output" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    config = {"nodes": nodes, "line_triggers": {"U": "auto"}, "directory_contract": {"artifacts": "immutable"}}
    (root / "pipeline.json").write_text(json.dumps(config), encoding="utf-8")
    return nodes


def test_json_roundtrip_preserves_lexical_values(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text('ID,value,note\n001,1.00,"a,b"\n002,,"line1\nline2"\n', encoding="utf-8-sig", newline="\n")
    target = tmp_path / "input.json"
    target.write_bytes(convert(source))
    table = load_table(target)
    assert table["rows"] == [["001", "1.00", "a,b"], ["002", "", "line1\nline2"]]
    restored = tmp_path / "restored.csv"
    materialize(target, restored)
    again = json.loads(convert(restored))
    assert again["rows"] == table["rows"]
    assert again["columns"] == table["columns"]


def test_migration_preserves_evidence_and_html_is_self_contained(tmp_path, monkeypatch):
    nodes = fixture(tmp_path, monkeypatch)
    old_manifest = json.loads((tmp_path / nodes[0]["path"] / "output/manifest.json").read_text())
    original = tmp_path / old_manifest["deliverables"][0]["artifact_file"]
    original_bytes = original.read_bytes()
    migrate(tmp_path)
    payload = json.loads((tmp_path / "pipeline.json").read_text())
    assert payload["nodes"][1]["inputs"][0]["file"] == "表.json"
    assert all(name.endswith('.json') for n in payload["nodes"] for name in n["outputs"])
    output = tmp_path / nodes[0]["path"] / "output"
    assert not (output / "表.csv").exists()
    assert original.read_bytes() == original_bytes
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["upstream"] == old_manifest["upstream"]
    assert manifest_hashes(manifest)["表.csv"] == old_manifest["deliverables"][0]["sha256"]
    results = build_reports(tmp_path)
    assert len(results) == 3
    assert check_reports(tmp_path, payload["nodes"]) == []
    html = (output / "结果.html").read_text(encoding="utf-8")
    raw = html.split('<script id="report-data" type="application/json">')[1].split('</script>')[0]
    data = json.loads(raw)
    rows = json.loads(gzip.decompress(base64.b64decode(data["datasets"][0]["packed"])))
    assert rows[0][0] == '001'
    assert rows[0][1].startswith('</script>')
    assert '<img src=x' not in html
    protected = referenced_batches(tmp_path, payload["nodes"])
    assert results["up"]["artifact"] in protected
    assert all(value is None for value in build_reports(tmp_path).values())
    (output / "结果.html").write_text("broken", encoding="utf-8")
    assert check_reports(tmp_path, payload["nodes"])


def test_runner_uses_json_input_and_only_installs_json(tmp_path, monkeypatch):
    nodes = fixture(tmp_path, monkeypatch)
    script = tmp_path / nodes[1]["path"] / "src/run.py"
    script.write_text('''from pathlib import Path
import csv
p=Path(__file__).resolve().parents[1]
rows=list(csv.reader((p.parent/"00.up/output/表.csv").open(encoding="utf-8-sig")))
assert not (p.parent/"00.up/data").exists()
(p/"output").mkdir(exist_ok=True)
with (p/"output/结果.csv").open("w",encoding="utf-8",newline="") as f:
    csv.writer(f).writerows(rows)
''', encoding="utf-8")
    migrate(tmp_path)
    record = run_node(tmp_path, "down")
    output = tmp_path / nodes[1]["path"] / "output"
    assert (output / "结果.json").is_file() and not (output / "结果.csv").exists()
    assert record["inputs"][0]["file"] == "表.json"
    assert load_table(output / "结果.json")["rows"][0][0] == '001'
    before = (output / "结果.json").read_bytes()
    script.write_text("raise RuntimeError('engine failed')", encoding="utf-8")
    with pytest.raises(Exception):
        run_node(tmp_path, "down")
    assert (output / "结果.json").read_bytes() == before
