from __future__ import annotations

import json
from pathlib import Path

import archive_old_artifacts as archive
import publish_release as release
from test_publish_release import make_repo


def test_archive_keeps_batches_still_referenced_by_current_manifests(tmp_path):
    repo = make_repo(tmp_path)
    release.release_all(repo)  # a、b 的 _01 批次保存字节
    for number in range(2, 5):  # 之后 a 多次强制发布：新批次只引用 _01
        release.release_all(repo, only={"a"}, force=True)
    batches = sorted(path.name for path in (repo / "00.a" / "artifacts").iterdir())
    assert len(batches) == 4

    moves = {src.name for src, _ in archive.plan_moves(repo, keep=1)}
    assert batches[0] not in moves  # 当前 manifest 的交付物仍引用 _01
    assert batches[-1] not in moves  # 最近一个保留
    assert moves == set(batches[1:-1])


def test_referenced_batches_follow_retained_manifests(tmp_path):
    import artifact_refs

    repo = make_repo(tmp_path)
    release.release_all(repo)
    payload = json.loads((repo / "pipeline.json").read_text(encoding="utf-8"))
    refs = artifact_refs.referenced_batches(repo, payload["nodes"])
    day = next((repo / "00.a" / "artifacts").iterdir()).name
    assert f"00.a/artifacts/{day}" in refs  # b 的上游记录与 a 的交付物都指向它


def test_archive_to_dest_verifies_copy_deletes_local_and_writes_index(tmp_path):
    (tmp_path / "repo").mkdir()
    repo = make_repo(tmp_path / "repo")
    release.release_all(repo)
    for _ in range(3):
        release.release_all(repo, only={"a"}, force=True)
    old = sorted((repo / "00.a" / "artifacts").iterdir())[1]
    files = {path.relative_to(old).as_posix(): path.read_bytes() for path in old.rglob("*") if path.is_file()}

    dest = tmp_path / "nas"
    assert archive.main(["--root", str(repo), "--keep", "1", "--dest", str(dest)]) == 0
    assert not old.exists()
    archived = dest / "00.a" / old.name
    assert {path.relative_to(archived).as_posix(): path.read_bytes() for path in archived.rglob("*") if path.is_file()} == files
    index = json.loads((repo / archive.INDEX_NAME).read_text(encoding="utf-8"))
    batch = next(item for item in index["archives"][0]["batches"] if item["batch"] == f"00.a/artifacts/{old.name}")
    assert batch["files"] == len(files) and set(batch["sha256"]) == set(files)
    assert json.loads((dest / archive.DEST_INDEX_NAME).read_text(encoding="utf-8")) == index


def test_batches_with_uncommitted_files_are_not_archived(tmp_path):
    import subprocess

    repo = make_repo(tmp_path)
    release.release_all(repo)
    for _ in range(3):
        release.release_all(repo, only={"a"}, force=True)
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "init"], check=True)
    batches = sorted((repo / "00.a" / "artifacts").iterdir())
    (batches[1] / "进行中.txt").write_text("wip", encoding="utf-8")  # 未跟踪文件

    moves = {src.name for src, _ in archive.plan_moves(repo, keep=1)}
    assert batches[1].name not in moves and batches[2].name in moves
