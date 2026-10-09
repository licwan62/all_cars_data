from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

import publish_release as release


def make_repo(tmp_path: Path) -> Path:
    nodes = [
        {"id": "a", "path": "00.a", "upstream": [], "outputs": ["车型结构.csv"], "pending": []},
        {"id": "b", "path": "01.b", "upstream": ["a"], "outputs": ["全量表_US.csv"], "pending": ["全量表_EU.csv"]},
    ]
    (tmp_path / "pipeline.json").write_text(json.dumps({"nodes": nodes}), encoding="utf-8")
    for node, name in zip(nodes, ["车型结构.csv", "全量表_US.csv"]):
        output = tmp_path / node["path"] / "output"
        output.mkdir(parents=True)
        (output / name).write_text("ID,X\n1,2\n3,4\n", encoding="utf-8-sig")
    return tmp_path


def test_release_versions_artifact_files_and_publishes_stable_names(tmp_path):
    repo = make_repo(tmp_path)
    release.release_all(repo)

    day = date.today()
    version = f"{day:%Y%m%d}_01"
    batch = repo / "00.a" / "artifacts" / f"{day.isoformat()}_01_a-release"
    assert (batch / "output" / f"车型结构-{version}.csv").is_file()
    assert (repo / "00.a" / "output" / "车型结构.csv").is_file()

    manifest = json.loads((repo / "01.b" / "output" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == version
    assert manifest["pending"] == ["全量表_EU.csv"]
    assert manifest["deliverables"][0]["rows"] == 2
    upstream = manifest["upstream"][0]
    assert upstream["node"] == "a" and upstream["version"] == version
    assert upstream["files"][0]["sha256"] == json.loads(
        (repo / "00.a" / "output" / "manifest.json").read_text(encoding="utf-8")
    )["deliverables"][0]["sha256"]

    summary = json.loads((repo / "release.json").read_text(encoding="utf-8"))
    assert summary["nodes"]["b"]["artifact"].endswith("_01_b-release")

    assert release.release_all(repo) == {}  # 交付物、上游、规则均未变化：不新建批次
    assert not (repo / "00.a" / "artifacts" / f"{day.isoformat()}_02_a-release").exists()

    release.release_all(repo, only={"a"}, force=True)  # 强制发布：新批次只引用旧文件
    second = repo / "00.a" / "artifacts" / f"{day.isoformat()}_02_a-release"
    assert (batch / "manifest.json").is_file()
    assert not (second / "output").exists()
    report = (second / "REPORT.md").read_text(encoding="utf-8")
    assert "# 发布报告" in report and "--force" in report
    assert "内容未变化；引用" in report
    item = json.loads((repo / "00.a" / "output" / "manifest.json").read_text(encoding="utf-8"))["deliverables"][0]
    assert item["artifact_file"] == f"00.a/artifacts/{day.isoformat()}_01_a-release/output/车型结构-{version}.csv"


def test_rule_change_releases_lightweight_batch_referencing_previous_bytes(tmp_path):
    repo = make_repo(tmp_path)
    release.release_all(repo)
    (repo / "01.b" / "data").mkdir()
    (repo / "01.b" / "data" / "规则.json").write_text("{}", encoding="utf-8")

    released = release.release_all(repo)
    assert set(released) == {"b"}
    day = date.today()
    second = repo / "01.b" / "artifacts" / f"{day.isoformat()}_02_b-release"
    assert "规则变化" in (second / "REPORT.md").read_text(encoding="utf-8")
    assert not (second / "output").exists()
    assert released["b"]["deliverables"][0]["versioned_file"] == f"全量表_US-{day:%Y%m%d}_01.csv"


def test_release_references_matching_run_batch_output(tmp_path):
    repo = make_repo(tmp_path)
    run_batch = repo / "00.a" / "artifacts" / "2026-01-01_01_run"
    (run_batch / "output").mkdir(parents=True)
    content = (repo / "00.a" / "output" / "车型结构.csv").read_bytes()
    (run_batch / "output" / "车型结构-20260101_01.csv").write_bytes(content)
    record = {
        "status": {"status": "passed"},
        "outputs": [{
            "file": "车型结构.csv", "versioned_file": "车型结构-20260101_01.csv",
            "artifact_file": "00.a/artifacts/2026-01-01_01_run/output/车型结构-20260101_01.csv",
            "sha256": release.sha256(run_batch / "output" / "车型结构-20260101_01.csv"),
        }],
    }
    (run_batch / "run.json").write_text(json.dumps(record), encoding="utf-8")

    released = release.release_all(repo, only={"a"})
    assert released["a"]["deliverables"][0]["artifact_file"] == record["outputs"][0]["artifact_file"]
    assert not (repo / released["a"]["artifact"] / "output").exists()


def test_release_report_explains_csv_row_and_field_changes(tmp_path):
    repo = make_repo(tmp_path)
    release.release_all(repo)
    output = repo / "00.a" / "output" / "车型结构.csv"
    output.write_text("ID,X\n1,9\n4,5\n", encoding="utf-8-sig")

    release.release_all(repo, only={"a"})

    day = date.today()
    report = (repo / "00.a" / "artifacts" / f"{day.isoformat()}_02_a-release" / "REPORT.md").read_text(encoding="utf-8")
    assert "内容已变化" in report
    assert "缺少可唯一定位的 `DIMENSION-ID`" in report


def test_missing_declared_output_aborts_before_any_write(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "01.b" / "output" / "全量表_US.csv").unlink()
    with pytest.raises(release.ReleaseError, match="全量表_US.csv"):
        release.release_all(repo)
    assert not (repo / "00.a" / "artifacts").exists()
    assert not (repo / "release.json").exists()


def test_release_writes_status_file_and_tampering_is_detected(tmp_path):
    import pipeline_status

    repo = make_repo(tmp_path)
    assert pipeline_status.check_status(repo)  # 发布前不存在

    release.release_all(repo)
    status = repo / pipeline_status.STATUS_NAME
    text = status.read_text(encoding="utf-8")
    assert "| 01.b |" in text and "最新" in text
    assert pipeline_status.check_status(repo) == []

    status.write_text(text + "\n临时笔记\n", encoding="utf-8")
    assert pipeline_status.check_status(repo)


def test_status_marks_node_stale_when_upstream_republished(tmp_path):
    import pipeline_status

    repo = make_repo(tmp_path)
    release.release_all(repo)
    (repo / "00.a" / "output" / "车型结构.csv").write_text("ID,X\n1,3\n", encoding="utf-8-sig")
    release.release_all(repo, only={"a"})

    text = (repo / pipeline_status.STATUS_NAME).read_text(encoding="utf-8")
    assert "| 01.b |" in text and "过期" in text
    assert "上游 00.a 已更新" in text
    assert pipeline_status.check_status(repo) == []


def test_dry_run_does_not_touch_status_file(tmp_path):
    import pipeline_status

    repo = make_repo(tmp_path)
    release.release_all(repo, dry_run=True)
    assert not (repo / pipeline_status.STATUS_NAME).exists()


def make_on_demand_repo(tmp_path: Path) -> Path:
    """a（U 线，自动）→ c（C 线，按需）。"""
    nodes = [
        {"id": "a", "path": "00.a", "line": "U", "upstream": [], "outputs": ["车型结构.csv"], "pending": []},
        {"id": "c", "path": "C1.c", "line": "C", "index": 1, "upstream": ["a"], "outputs": ["代表车型.csv"], "pending": []},
    ]
    payload = {"line_triggers": {"U": "auto", "C": "on_demand"}, "nodes": nodes}
    (tmp_path / "pipeline.json").write_text(json.dumps(payload), encoding="utf-8")
    for node in nodes:
        output = tmp_path / node["path"] / "output"
        output.mkdir(parents=True)
        (output / node["outputs"][0]).write_text("ID,X\n1,2\n", encoding="utf-8-sig")
    return tmp_path


def test_default_release_skips_on_demand_nodes(tmp_path):
    repo = make_on_demand_repo(tmp_path)
    released = release.release_all(repo)
    assert set(released) == {"a"}
    assert not (repo / "C1.c" / "artifacts").exists()

    assert set(release.release_all(repo, only={"c"})) == {"c"}  # 显式点名才发布
    assert set(release.release_all(repo, lines={"C"}, force=True)) == {"c"}
    assert set(release.release_all(repo, include_on_demand=True, force=True)) == {"a", "c"}
    with pytest.raises(release.ReleaseError, match="未知节点或产线"):
        release.release_all(repo, only={"nope"})


def test_on_demand_node_is_not_stale_when_upstream_republished(tmp_path, monkeypatch):
    import pipeline_status
    import trace_pipeline

    repo = make_on_demand_repo(tmp_path)
    release.release_all(repo, include_on_demand=True)
    (repo / "00.a" / "output" / "车型结构.csv").write_text("ID,X\n1,3\n", encoding="utf-8-sig")
    release.release_all(repo)

    text = (repo / pipeline_status.STATUS_NAME).read_text(encoding="utf-8")
    assert "| C1.c | C 代表车型 | 按需 |" in text and "按需待刷新" in text
    assert "过期" not in text
    assert pipeline_status.check_status(repo) == []

    payload = json.loads((repo / "pipeline.json").read_text(encoding="utf-8"))
    node = payload["nodes"][1]
    by_id = {item["id"]: item for item in payload["nodes"]}
    monkeypatch.setattr(trace_pipeline, "ROOT", repo)
    errors, stale, deferred = trace_pipeline.trace_node(node, by_id, on_demand=True)
    assert (errors, stale) == ([], []) and deferred
    assert trace_pipeline.trace_node(node, by_id)[1]  # 作为自动节点时则为过期
