from __future__ import annotations

import json
from pathlib import Path

import pytest

import identity_coverage as coverage
import publish_release as release


def write_csv(path: Path, header: str, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8-sig")


def make_repo(tmp_path: Path, downstream_ids: list[str], rule: dict | None = None) -> Path:
    rule = rule or {"output": "车型结构.csv", "upstream": "a", "file": "尺寸库.csv"}
    nodes = [
        {"id": "a", "path": "01.a", "upstream": [], "outputs": ["尺寸库.csv"], "pending": []},
        {"id": "b", "path": "02.b", "upstream": ["a"], "outputs": [rule["output"]], "pending": [], "identity_coverage": [rule]},
        {"id": "c", "path": "02.c", "upstream": ["a"], "outputs": ["其他.csv"], "pending": []},
    ]
    (tmp_path / "pipeline.json").write_text(json.dumps({"nodes": nodes}), encoding="utf-8")
    write_csv(tmp_path / "01.a" / "output" / "尺寸库.csv", "DIMENSION-ID,L", ["X 2020 US,1", "Y 2021 US,2"])
    key = rule.get("key", "DIMENSION-ID")
    write_csv(tmp_path / "02.b" / "output" / rule["output"], f"{key},V", [f"{value},1" for value in downstream_ids])
    write_csv(tmp_path / "02.c" / "output" / "其他.csv", "K", ["1"])
    return tmp_path


def by_id(repo: Path) -> dict[str, dict]:
    return {node["id"]: node for node in json.loads((repo / "pipeline.json").read_text(encoding="utf-8"))["nodes"]}


def test_equal_mode_reports_missing_and_residual(tmp_path):
    repo = make_repo(tmp_path, ["X 2020 US", "Z 1999 US"])
    nodes = by_id(repo)
    [gap] = coverage.check_node(repo, nodes["b"], nodes)
    assert gap.missing == ["Y 2021 US"] and gap.residual == ["Z 1999 US"]
    assert "缺 1 个" in gap.describe() and "保留 1 个" in gap.describe()


def test_key_split_and_subset_mode(tmp_path):
    rule = {"output": "原子销量.csv", "key": "atom_record_id", "key_split": "|", "upstream": "a", "file": "尺寸库.csv", "mode": "subset"}
    repo = make_repo(tmp_path, ["X 2020 US|ATOM_YEAR=2020"], rule)
    nodes = by_id(repo)
    [gap] = coverage.check_node(repo, nodes["b"], nodes)
    assert gap.ok  # subset：只取一部分身份不算缺口


def test_validate_rules_requires_declared_upstream_and_outputs():
    nodes = [
        {"id": "a", "upstream": [], "outputs": ["尺寸库.csv"]},
        {"id": "b", "upstream": [], "outputs": [], "identity_coverage": [{"output": "x.csv", "upstream": "a", "file": "无.csv", "mode": "all"}]},
    ]
    errors = coverage.validate_rules(nodes)
    assert any("不是本节点已声明的上游" in error for error in errors)
    assert any("不在本节点 outputs" in error for error in errors)
    assert any("mode 只能是" in error for error in errors)
    assert any("不在上游 outputs" in error for error in errors)


def test_release_refuses_auto_node_with_identity_gap_but_releases_others(tmp_path):
    repo = make_repo(tmp_path, ["X 2020 US"])
    with pytest.raises(release.IdentityGapError, match="身份未承接"):
        release.release_all(repo)
    assert not (repo / "02.b" / "output" / "manifest.json").exists()
    assert (repo / "02.c" / "output" / "manifest.json").is_file()  # 其他节点照常发布
    assert "02.c" in (repo / "release.json").read_text(encoding="utf-8")

    released = release.release_all(repo, accept_identity_gaps=True)
    [check] = released["b"]["checks"]["identity_coverage"]
    assert check["missing"] == 1 and check["missing_examples"] == ["Y 2021 US"]
    report = (repo / released["b"]["artifact"] / "REPORT.md").read_text(encoding="utf-8")
    assert "## 身份承接" in report and "已显式接受" in report


def test_upstream_record_uses_run_inputs_not_latest_manifest(tmp_path):
    repo = make_repo(tmp_path, ["X 2020 US", "Y 2021 US"])
    release.release_all(repo)
    old = json.loads((repo / "01.a" / "output" / "manifest.json").read_text(encoding="utf-8"))
    output = repo / "02.b" / "output" / "车型结构.csv"
    batch = repo / "02.b" / "artifacts" / "2026-01-01_01_run"
    (batch / "output").mkdir(parents=True)
    (batch / "output" / "车型结构-20260101_01.csv").write_bytes(output.read_bytes())
    old_input = {**old["deliverables"][0], "node": "a", "path": "01.a", "version": old["version"]}
    (batch / "run.json").write_text(json.dumps({
        "batch": "02.b/artifacts/2026-01-01_01_run", "status": {"status": "passed"}, "inputs": [old_input],
        "outputs": [{"file": "车型结构.csv", "versioned_file": "车型结构-20260101_01.csv",
                     "artifact_file": "02.b/artifacts/2026-01-01_01_run/output/车型结构-20260101_01.csv",
                     "sha256": release.sha256(output)}],
    }), encoding="utf-8")
    # 上游新增一个文件列并重新发布；本节点未重跑，manifest 应仍记录运行时读取的旧版本
    write_csv(repo / "01.a" / "output" / "尺寸库.csv", "DIMENSION-ID,L,W", ["X 2020 US,1,1", "Y 2021 US,2,2"])
    release.release_all(repo, only={"a"})
    released = release.release_all(repo, only={"b"}, force=True)
    [record] = released["b"]["upstream"]
    assert record["basis"] == "run" and record["version"] == old["version"]
    assert record["files"][0]["sha256"] == old["deliverables"][0]["sha256"]
    assert "运行批次实际读取" in (repo / released["b"]["artifact"] / "REPORT.md").read_text(encoding="utf-8")


def test_upstream_without_run_record_is_marked_publish_time(tmp_path):
    repo = make_repo(tmp_path, ["X 2020 US", "Y 2021 US"])
    released = release.release_all(repo)
    assert released["b"]["upstream"][0]["basis"] == "publish-time"
    assert released["b"]["checks"]["unverified_deliverables"] == ["车型结构.csv"]


def test_copied_input_is_resolved_to_later_published_upstream_version(tmp_path):
    repo = make_repo(tmp_path, ["X 2020 US", "Y 2021 US"])
    release.release_all(repo)
    nodes = by_id(repo)
    upstream = json.loads((repo / "01.a" / "output" / "manifest.json").read_text(encoding="utf-8"))
    digest = upstream["deliverables"][0]["sha256"]
    copied = {"file": "01.a/output/尺寸库.csv", "artifact_file": "02.b/artifacts/x/input/尺寸库.csv", "sha256": digest,
              "copied_because": "上游改动后未发布"}
    [item] = release.resolve_copied_inputs(repo, nodes["b"], nodes, [copied])
    assert item["node"] == "a" and item["version"] == upstream["version"] and item["artifact_file"] == upstream["deliverables"][0]["artifact_file"]
    [stale] = release.resolve_copied_inputs(repo, nodes["b"], nodes, [{**copied, "sha256": "0" * 64}])
    assert stale["version"] is None and stale["artifact_file"] == copied["artifact_file"]
