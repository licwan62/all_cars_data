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
