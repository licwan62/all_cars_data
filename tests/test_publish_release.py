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
    batch = repo / "00.a" / "artifacts" / f"{day.isoformat()}_01_release"
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
    assert summary["nodes"]["b"]["artifact"].endswith("_01_release")

    release.release_all(repo)  # 第二次不覆盖，批次号递增
    assert (repo / "00.a" / "artifacts" / f"{day.isoformat()}_02_release").is_dir()
    assert (batch / "manifest.json").is_file()


def test_missing_declared_output_aborts_before_any_write(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "01.b" / "output" / "全量表_US.csv").unlink()
    with pytest.raises(release.ReleaseError, match="全量表_US.csv"):
        release.release_all(repo)
    assert not (repo / "00.a" / "artifacts").exists()
    assert not (repo / "release.json").exists()
