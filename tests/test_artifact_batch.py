from __future__ import annotations

import gzip
import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

import artifact_batch as ab


def published_upstream(tmp_path: Path, content: str = "ID,X\n1,2\n") -> Path:
    """模拟一个已发布节点：output/表.csv + manifest.json（sha 一致）。"""
    output = tmp_path / "A0.up" / "output"
    (output / "US").mkdir(parents=True)
    table = output / "US" / "表.csv"
    table.write_text(content, encoding="utf-8")
    manifest = {
        "node": "up", "path": "A0.up", "version": "20260101_01",
        "deliverables": [{
            "file": "US/表.csv", "versioned_file": "US/表-20260101_01.csv",
            "artifact_file": "A0.up/artifacts/2026-01-01_01_up-release/output/US/表-20260101_01.csv",
            "sha256": ab.sha256(table),
        }],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return table


def test_published_input_is_referenced_not_copied(tmp_path):
    table = published_upstream(tmp_path)
    batch = ab.RunBatch.create(tmp_path / "node" / "artifacts", "demo")
    batch.input(table)
    batch.output("结果.csv").write_text("ID\n1\n", encoding="utf-8")
    record = batch.finish({"rows": 1}, publish_to=tmp_path / "node" / "output")

    assert record["inputs"] == [{
        "node": "up", "path": "A0.up", "version": "20260101_01", "file": "US/表.csv",
        "versioned_file": "US/表-20260101_01.csv",
        "artifact_file": "A0.up/artifacts/2026-01-01_01_up-release/output/US/表-20260101_01.csv",
        "sha256": ab.sha256(table),
    }]
    assert not (batch.directory / "input").exists()
    version = f"{date.today():%Y%m%d}_01"
    assert record["outputs"][0]["versioned_file"] == f"结果-{version}.csv"
    assert record["outputs"][0]["rows"] == 1
    assert record["status"] == {"status": "passed", "rows": 1}
    assert (tmp_path / "node" / "output" / "结果.csv").read_text(encoding="utf-8") == "ID\n1\n"
    assert json.loads((batch.directory / "run.json").read_text(encoding="utf-8")) == record


def test_unpublished_or_modified_input_is_copied_with_reason(tmp_path):
    table = published_upstream(tmp_path)
    table.write_text("ID,X\n1,3\n", encoding="utf-8")  # 上游改动后未发布
    loose = tmp_path / "loose.csv"
    loose.write_text("a\n", encoding="utf-8")

    batch = ab.RunBatch.create(tmp_path / "artifacts", "demo")
    batch.input(table)
    batch.input(loose, name="参考/loose.csv")
    batch.finish()
    first, second = batch.inputs
    assert "不一致" in first["copied_because"]
    assert (batch.directory / "input" / "US" / "表.csv").read_text(encoding="utf-8") == "ID,X\n1,3\n"
    assert "不在任何已发布节点" in second["copied_because"]
    assert (batch.directory / "input" / "参考" / "loose.csv").is_file()


def test_extra_is_gzipped_and_numbering_skips_existing_batches(tmp_path):
    artifacts = tmp_path / "artifacts"
    today = date.today().isoformat()
    (artifacts / f"{today}_01_node-release").mkdir(parents=True)
    (artifacts / f".{today}_02_node-release.tmp").mkdir()  # 发布脚本的暂存目录也占号

    batch = ab.RunBatch.create(artifacts, "demo")
    assert batch.directory.name == f"{today}_03_demo"
    path = batch.extra("原子事实表_US.csv")
    assert path.name == "原子事实表_US.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("a\n")
    record = batch.finish()
    assert record["extras"][0].endswith("extra/原子事实表_US.csv.gz")
    assert ab.RunBatch.create(artifacts, "demo").directory.name == f"{today}_04_demo"


def test_failure_is_recorded_and_output_untouched(tmp_path):
    output = tmp_path / "output"
    with pytest.raises(ValueError):
        with ab.RunBatch.create(tmp_path / "artifacts", "demo") as batch:
            batch.output("结果.csv").write_text("x\n", encoding="utf-8")
            raise ValueError("校验失败")
    record = json.loads((batch.directory / "run.json").read_text(encoding="utf-8"))
    assert record["status"]["status"] == "failed" and "校验失败" in record["status"]["error"]
    assert not output.exists()


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True, capture_output=True)


def test_rules_reference_git_commit_and_copy_only_uncommitted_files(tmp_path):
    project = tmp_path / "repo" / "E0.node"
    data = project / "data"
    data.mkdir(parents=True)
    (data / "已提交.json").write_text("{}", encoding="utf-8")
    (data / "将修改.json").write_text("{}", encoding="utf-8")
    git(tmp_path / "repo", "init", "-q")
    git(tmp_path / "repo", "add", ".")
    git(tmp_path / "repo", "commit", "-q", "-m", "init")
    (data / "将修改.json").write_text('{"a": 1}', encoding="utf-8")
    (data / "未跟踪.json").write_text("[]", encoding="utf-8")

    batch = ab.RunBatch.create(project / "artifacts", "demo", data_dir=data)
    rules = batch.finish()["rules"]
    assert rules["git_commit"] and len(rules["git_commit"]) == 40
    assert rules["copied"] == ["data/将修改.json", "data/未跟踪.json"]
    assert {item["file"] for item in rules["files"]} == {"data/已提交.json", "data/将修改.json", "data/未跟踪.json"}
    assert not (batch.directory / "rules" / "data" / "已提交.json").exists()
    assert (batch.directory / "rules" / "data" / "将修改.json").read_text(encoding="utf-8") == '{"a": 1}'


def test_rules_outside_git_are_all_copied(tmp_path):
    data = tmp_path / "node" / "data"
    data.mkdir(parents=True)
    (data / "规则.json").write_text("{}", encoding="utf-8")
    batch = ab.RunBatch.create(tmp_path / "node" / "artifacts", "demo", data_dir=data)
    rules = batch.finish()["rules"]
    assert rules["git_commit"] is None and rules["copied"] == ["data/规则.json"]
