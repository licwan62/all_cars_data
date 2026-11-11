import json
from pathlib import Path

import pytest
import artifact_batch as ab
import organize_project_layout as layout
from node_paths import node_output, node_page
from node_html import check_reports
from organize_project_layout import organize
from migrate_json_interfaces import migrate
from test_json_html_interfaces import fixture


def test_layout_moves_json_and_names_node_pages_without_changing_data(tmp_path, monkeypatch):
    nodes = fixture(tmp_path, monkeypatch)
    rule = tmp_path / nodes[0]["path"] / "data/manual.csv"
    rule.write_bytes(b"key,value\n001,1.00\n")
    migrate(tmp_path)
    before = rule.read_bytes()
    original = tmp_path / nodes[0]["path"] / "output/表.json"
    data_bytes = original.read_bytes()
    organize(tmp_path, apply=True)
    payload = json.loads((tmp_path / "pipeline.json").read_text())
    node = payload["nodes"][0]
    assert node_output(tmp_path, node) == tmp_path / "json/up"
    assert (node_output(tmp_path, node) / "表.json").read_bytes() == data_bytes
    assert node_page(tmp_path, node).parent == tmp_path / node["path"]
    assert node_page(tmp_path, node).name == "00.up.html"
    assert not (tmp_path / node["path"] / "output").exists()
    assert rule.read_bytes() == before
    assert check_reports(tmp_path, payload["nodes"]) == []
    assert organize(tmp_path, apply=True) == []
    reference, reason = ab.published_reference(node_output(tmp_path, node) / "表.json", ab.sha256(node_output(tmp_path, node) / "表.json"))
    assert reference["node"] == "up" and not reason


def test_layout_rejects_destination_collision_before_mutation(tmp_path, monkeypatch):
    nodes = fixture(tmp_path, monkeypatch)
    migrate(tmp_path)
    target = tmp_path / "json/up/表.json"
    target.parent.mkdir(parents=True)
    target.write_text("conflict")
    config = (tmp_path / "pipeline.json").read_bytes()
    with pytest.raises(ValueError, match="不同内容"):
        organize(tmp_path, apply=True)
    assert (tmp_path / "pipeline.json").read_bytes() == config
    assert (tmp_path / nodes[0]["path"] / "output/表.json").is_file()


def test_split_page_and_metadata_publication_rolls_back_on_error(tmp_path, monkeypatch):
    monkeypatch.setattr(ab, "REPO_ROOT", tmp_path)
    page = tmp_path / "nodes/sample/业务报告.html"
    meta = tmp_path / "json/sample/html_manifest.json"
    for path in (page, meta):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("old")
    batch = ab.RunBatch.create(tmp_path / "nodes/sample/artifacts", "split-test")
    batch.output("业务报告.html").write_text("new page")
    batch.output("html_manifest.json").write_text('{"new":true}')
    original = ab.os.replace
    def fail(source, destination):
        if Path(destination) == meta:
            raise OSError("test installation failure")
        return original(source, destination)
    monkeypatch.setattr(ab.os, "replace", fail)
    with pytest.raises(OSError):
        batch.finish(publish_paths={"业务报告.html": page, "html_manifest.json": meta})
    assert page.read_text() == meta.read_text() == "old"


def test_layout_restores_config_and_working_pages_when_render_fails(tmp_path, monkeypatch):
    nodes = fixture(tmp_path, monkeypatch)
    migrate(tmp_path)
    config = (tmp_path / "pipeline.json").read_bytes()
    old = json.loads(config)
    changed = layout.contract(old)
    target = node_page(tmp_path, changed["nodes"][0])
    def fail(root):
        target.write_text("partial rendering")
        raise RuntimeError("render failed")
    monkeypatch.setattr(layout, "build_reports", fail)
    with pytest.raises(RuntimeError, match="render failed"):
        organize(tmp_path, apply=True)
    assert (tmp_path / "pipeline.json").read_bytes() == config
    assert not target.exists()
    assert (tmp_path / nodes[0]["path"] / "output/表.json").is_file()
    assert layout.plan(tmp_path, old, changed)  # No collision prevents a retry.
