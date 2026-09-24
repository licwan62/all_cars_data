from __future__ import annotations

import json
from datetime import date

import publish_release as release
import rules_snapshot as rules
import trace_pipeline as trace
from test_publish_release import make_repo


def write_rule(repo, relative: str, text: str) -> None:
    path = repo / "01.b" / "data" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def trace_b(repo, monkeypatch) -> list[str]:
    monkeypatch.setattr(trace, "ROOT", repo)
    payload = json.loads((repo / "pipeline.json").read_text(encoding="utf-8"))
    by_id = {node["id"]: node for node in payload["nodes"]}
    errors, stale = trace.trace_node(by_id["b"], by_id)
    assert not errors, errors
    return stale


def test_snapshot_ignores_line_endings_and_scratch_files(tmp_path):
    (tmp_path / "data" / "us").mkdir(parents=True)
    (tmp_path / "data" / "us" / "规则.csv").write_bytes(b"a,b\n1,2\n")
    (tmp_path / "data" / "~$规则.xlsx").write_bytes(b"lock")
    (tmp_path / "data" / "__pycache__").mkdir()
    (tmp_path / "data" / "__pycache__" / "x.pyc").write_bytes(b"x")
    before = rules.rules_snapshot(tmp_path)
    assert [item["file"] for item in before] == ["data/us/规则.csv"]

    (tmp_path / "data" / "us" / "规则.csv").write_bytes(b"a,b\r\n1,2\r\n")
    assert rules.rules_snapshot(tmp_path) == before


def test_release_records_rules_and_trace_flags_rule_edits(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    write_rule(repo, "us/0924.1.csv", "尺码,长上限\n4S-0,4850\n")
    release.release_all(repo)

    manifest = json.loads((repo / "01.b" / "output" / "manifest.json").read_text(encoding="utf-8"))
    assert [item["file"] for item in manifest["rules"]] == ["data/us/0924.1.csv"]
    assert trace_b(repo, monkeypatch) == []

    # 新建一版规则、修改旧规则：输出未重新发布，节点应判为过期并列出文件。
    write_rule(repo, "us/0924.2.csv", "尺码,长上限,插片指数下限\n4S-0,4850,120\n")
    write_rule(repo, "us/0924.1.csv", "尺码,长上限\n4S-0,4900\n")
    stale = trace_b(repo, monkeypatch)
    assert len(stale) == 1
    assert "修改 data/us/0924.1.csv" in stale[0] and "新增 data/us/0924.2.csv" in stale[0]

    release.release_all(repo, only={"b"})
    assert trace_b(repo, monkeypatch) == []
    report = (
        repo / "01.b" / "artifacts" / f"{date.today().isoformat()}_02_b-release" / "REPORT.md"
    ).read_text(encoding="utf-8")
    assert "新增 data/us/0924.2.csv" in report


def test_manifest_without_rules_is_not_stale(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    release.release_all(repo)
    path = repo / "01.b" / "output" / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    del manifest["rules"]
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    write_rule(repo, "us/new.csv", "x\n")

    assert trace_b(repo, monkeypatch) == []
    assert trace.rules_state(manifest) == "未记录"
