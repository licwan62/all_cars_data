from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pipeline_portal
from pipeline_portal import Portal, handler_for


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def fixture_portal(tmp_path: Path) -> tuple[Portal, Path, Path]:
    data = tmp_path / "all_cars_data"
    web = tmp_path / "pipeline_carstable_to_webapp"
    data.mkdir()
    web.mkdir()
    nodes = [
        {"id": "size-calculation", "path": "nodes/A0.尺码计算", "line": "A", "layer": 4, "upstream": [], "pending": []},
        {"id": "size-compression", "path": "nodes/A1.压缩尺寸信息", "line": "A", "layer": 5, "upstream": ["size-calculation"], "pending": ["压缩表"]},
        {"id": "sales-estimation", "path": "nodes/02.销量评估", "line": "U", "layer": 2, "upstream": [], "pending": []},
        {"id": "review", "path": "nodes/B0.审查", "line": "B", "layer": 5, "upstream": ["size-calculation"], "pending": []},
    ]
    write_json(data / "pipeline.json", {"nodes": nodes, "line_triggers": {"A": "auto", "U": "auto", "B": "on_demand"}})
    for node in nodes:
        (data / node["path"] / "data").mkdir(parents=True)
    current = data / "nodes/A0.尺码计算/output/全量表.csv"
    current.parent.mkdir(parents=True)
    current.write_text("new", encoding="utf-8")
    origin = data / "nodes/A0.尺码计算/artifacts/2026-10-29_01_run/output/全量表.csv"
    origin.parent.mkdir(parents=True)
    origin.write_text("new", encoding="utf-8")
    digest = hashlib.sha256(b"new").hexdigest()
    write_json(current.parent / "manifest.json", {
        "node": "size-calculation", "version": "20261029_01", "published_at": "2026-10-29T10:00:00+08:00",
        "deliverables": [{"file": "全量表.csv", "sha256": digest, "artifact_file": origin.relative_to(data).as_posix()}],
        "upstream": [], "pending": [],
    })
    for node in nodes[1:]:
        write_json(data / node["path"] / "output/manifest.json", {
            "node": node["id"], "version": "20261028_01", "published_at": "2026-10-28T10:00:00+08:00",
            "deliverables": [], "pending": node["pending"],
            "upstream": [{"node": "size-calculation", "version": "20261028_01", "basis": "run",
                          "files": [{"file": "全量表.csv", "sha256": hashlib.sha256(b"old").hexdigest()}]}]
            if node["upstream"] else [],
        })
    write_json(origin.parent.parent / "run.json", {
        "batch": "2026-10-29_01_run", "created_at": "2026-10-29T09:00:00+08:00",
        "finished_at": "2026-10-29T09:02:00+08:00", "status": {"status": "failed"}, "command": ["python run.py"],
    })
    write_json(origin.parent.parent / "manifest.json", {
        "node": "size-calculation", "version": "20261029_01", "published_at": "2026-10-29T10:00:00+08:00",
    })
    site = web / "artifact/2026-10-29_01_pipeline/artifact.json"
    write_json(site, {
        "batch": "2026-10-29_01_pipeline", "status": "partial", "created_at": "2026-10-29T11:00:00+08:00",
        "steps": {"build_public_site": {"status": "succeeded"}},
        "publish": {"public": {"status": "promoted"}, "nas": {"status": "failed", "error": "冲突"}},
        "upstream": {"sources": {key: {"node": node, "version": "20261029_01"} for key, node in
                                  (("a0_output_dir", "size-calculation"), ("compressed_output_dir", "size-compression"),
                                   ("sales_output_dir", "sales-estimation"))}},
    })
    document = data / "nodes/A0.尺码计算/data/规则.md"
    document.write_text("规则说明", encoding="utf-8")
    return Portal(data, web, data / "portal/data/journal.sqlite3"), data, web


def test_overview_traces_real_pins_and_separate_site_states(tmp_path):
    portal, _, _ = fixture_portal(tmp_path)
    overview = portal.overview()
    states = {node["id"]: node["state"] for node in overview["nodes"]}
    assert states["size-compression"] == "过期"
    assert states["review"] == "按需待刷新"
    assert overview["site"]["build"] == "succeeded"
    assert overview["site"]["public"] == "promoted"
    assert overview["site"]["nas"] == "failed"
    assert {edge["from"] for edge in overview["edges"] if edge["to"] == "website"} == {
        "size-calculation", "size-compression", "sales-estimation"}
    assert {source["node"]: source["version"] for source in portal.node("website")["upstream"]} == {
        "size-calculation": "20261029_01", "size-compression": "20261029_01", "sales-estimation": "20261029_01"}


def test_events_retry_deduplicate_and_notes_survive_restart(tmp_path):
    portal, data, web = fixture_portal(tmp_path)
    first = portal.events()
    assert any(event["kind"] == "运行" and event["status"] == "failed" for event in first)
    assert any(event["kind"] == "发布" for event in first)
    assert any(event["kind"] == "网站批次" for event in first)
    site_path = web / "artifact/2026-10-29_01_pipeline/artifact.json"
    site = json.loads(site_path.read_text(encoding="utf-8"))
    site["status"] = "complete"
    site["publish"]["nas"]["status"] = "published"
    write_json(site_path, site)
    second = portal.events()
    site_events = [event for event in second if event["kind"] == "网站批次"]
    assert len(site_events) == 1 and "NAS published" in site_events[0]["detail"]
    run2 = data / "nodes/A0.尺码计算/artifacts/2026-10-30_01_retry/run.json"
    write_json(run2, {"created_at": "2026-10-30T09:00:00+08:00", "status": {"status": "passed"}})
    assert len([event for event in portal.events() if event["kind"] == "运行"]) == 2
    record = portal.add_note({"node_id": "size-calculation", "summary": "已核对", "detail": "修正来源",
                              "event_key": site_events[0]["event_key"], "file_ref": "data:nodes/A0.尺码计算/data/规则.md"})
    assert record["id"] > 0
    reopened = Portal(data, web, portal.db_path)
    notes = [event for event in reopened.events("size-calculation") if event["type"] == "note"]
    assert len(notes) == 1 and notes[0]["summary"] == "已核对"
    assert list((portal.db_path.parent / "backups").glob("journal-*.sqlite3"))


def test_files_preview_and_archived_provenance(tmp_path):
    portal, data, _ = fixture_portal(tmp_path)
    details = portal.node("size-calculation")
    assert any(item["path"].endswith("规则.md") for item in details["docs"])
    ref = "data:nodes/A0.尺码计算/data/规则.md"
    assert portal.preview(ref)["content"] == "规则说明"
    source = details["outputs"][0]["source"]
    assert source["location"] == "本地" and source["exists"]
    archived_batch = data / "nodes/A0.尺码计算/artifacts/2026-10-01_01_old"
    archived_target = tmp_path / "archive" / "2026-10-01_01_old"
    archived_target.mkdir(parents=True)
    (archived_target / "REPORT.md").write_text("历史记录", encoding="utf-8")
    write_json(data / "artifacts_archive.json", {"archives": [{"batches": [{
        "batch": archived_batch.relative_to(data).as_posix(), "archive_path": str(archived_target)}]}]})
    item = portal.file_entry("data", archived_batch.relative_to(data).as_posix() + "/REPORT.md")
    assert item["location"] == "归档" and item["exists"]
    assert portal.preview(item["ref"])["content"] == "历史记录"
    try:
        portal.resolve_ref("data:../secret.txt")
    except ValueError:
        pass
    else:
        raise AssertionError("must reject paths outside the repository")


def test_local_http_preview_note_and_open(tmp_path, monkeypatch):
    portal, _, _ = fixture_portal(tmp_path)
    opened = []
    monkeypatch.setattr(pipeline_portal.os, "startfile", lambda path: opened.append(path), raising=False)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(portal))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    ref = "data:nodes/A0.尺码计算/data/规则.md"

    def send(path, payload, origin=base):
        raw = json.dumps(payload).encode("utf-8")
        request = Request(base + path, data=raw, headers={
            "Origin": origin, "Content-Type": "application/json", "X-Portal-Request": "1", "X-Portal-Token": portal.token}, method="POST")
        with urlopen(request) as response:
            return json.load(response)

    try:
        with urlopen(base + "/api/overview") as response:
            assert len(json.load(response)["nodes"]) == 4
        with urlopen(base + "/api/preview?ref=" + quote(ref, safe="")) as response:
            assert json.load(response)["content"] == "规则说明"
        assert send("/api/notes", {"node_id": "size-calculation", "summary": "页面记录"})["id"] > 0
        assert send("/api/open", {"ref": ref})["location"] == "本地"
        assert opened and opened[0].name == "规则.md"
        try:
            send("/api/open", {"ref": ref}, origin="http://evil.example")
        except HTTPError as error:
            assert error.code == 403
        else:
            raise AssertionError("cross-origin write must be rejected")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_sha_search_covers_all_materials_and_uses_raw_input_digest(tmp_path):
    portal, data, _ = fixture_portal(tmp_path)
    folder = data / "nodes/A0.尺码计算/data"
    for i in range(501):
        (folder / f"{i:04d}.txt").write_bytes(b"filler")
    raw = b"target\r\n"
    (folder / "zz-target.txt").write_bytes(raw)
    sha = hashlib.sha256(raw).hexdigest()
    write_json(data / "nodes/A1.压缩尺寸信息/artifacts/2026-11-01_01_run/run.json", {
        "status": {"status": "passed"}, "inputs": [{"file": "zz-target.txt",
        "sha256": hashlib.sha256(b"target\n").hexdigest(), "raw_sha256": sha}]})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(portal))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.server_port}/api/content?sha={sha}") as response:
            result = json.load(response)
        assert any(item["artifact_file"].endswith("/zz-target.txt") for item in result["locations"])
        assert any(item["node"] == "size-compression" for item in result["consumers"])
        with portal.materials.connect() as db:
            assert db.execute("SELECT COUNT(*) FROM materials").fetchone()[0] == 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
