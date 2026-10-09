"""把各节点 artifacts 下较旧的批次归档到仓库外（默认 .bak/artifacts，可用 --dest 指向 NAS），只保留最近 N 个。

    python scripts/archive_old_artifacts.py --keep 3 --dry-run
    python scripts/archive_old_artifacts.py --keep 3 --dest "\\\\NAS8824B4\\Public\\PQData\\bak\\all_cars_data\\artifacts"

安全规则：
- 按引用计数保护：当前各节点 output/manifest.json 引用的批次（交付物来源、上游输入），以及被保留批次的
  manifest.json / run.json 间接引用的批次一律不移动，保证 trace_pipeline 仍能追到每份字节；
- 含未提交（git 未跟踪或已修改）文件的批次不移动，避免带走进行中的工作；
- ``legacy-*`` 目录视为最旧的历史，不占保留名额；
- 先复制到目标并逐文件校验 sha256，全部一致后才删除本地；目标已存在则拒绝覆盖；
- 每次归档追加记录到仓库根目录 ``artifacts_archive.json``（批次 → 归档位置、文件数、字节数、各文件 sha256），
  目标根目录同步写一份 ``ARCHIVE_INDEX.json``。归档后在仓库提交本地删除与索引。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from artifact_refs import referenced_batches, sha256

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIR_NAMES = {".bak", "node_modules", "__pycache__", ".git"}
INDEX_NAME = "artifacts_archive.json"
DEST_INDEX_NAME = "ARCHIVE_INDEX.json"


def find_artifacts_dirs(root: Path) -> list[Path]:
    """Find every project-level ``artifacts`` directory under root."""

    found = []
    for path in root.rglob("artifacts"):
        if not path.is_dir():
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in path.relative_to(root).parts):
            continue
        found.append(path)
    return sorted(found)


def batch_dirs(artifacts_dir: Path) -> list[Path]:
    """Candidate archive batches: immediate subdirectories with a digit-led
    name (``2026-09-07_01_...``, ``0914.2-...``). Non-digit-led subdirectories
    (e.g. category folders holding live project code) are left untouched, as
    are loose files such as README.md.
    """

    candidates = [
        child
        for child in artifacts_dir.iterdir()
        if child.is_dir() and child.name[:1].isdigit()
    ]
    return sorted(candidates, key=lambda p: p.name)


def legacy_dirs(artifacts_dir: Path) -> list[Path]:
    """``legacy-*``：节点合并前的历史批次集合，视为最旧，不占保留名额。"""
    return sorted(child for child in artifacts_dir.iterdir() if child.is_dir() and child.name.startswith("legacy-"))


def dirty_paths(root: Path, artifacts_dir: Path) -> set[str] | None:
    """artifacts_dir 下 git 未跟踪/已修改的文件（相对仓库的 posix 路径）；不在 git 仓库时返回 None。"""
    try:
        status = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=false", "status", "--porcelain", "-z", "--untracked-files=all", "--",
             artifacts_dir.relative_to(root).as_posix()],
            capture_output=True, text=True, encoding="utf-8", check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {entry[3:] for entry in status.split("\0") if len(entry) > 3}


def plan_moves(root: Path, keep: int, dest_root: Path | None = None, tracked_only: bool = True) -> list[tuple[Path, Path]]:
    dest_root = dest_root or root / ".bak" / "artifacts"
    pipeline = root / "pipeline.json"
    nodes = json.loads(pipeline.read_text(encoding="utf-8"))["nodes"] if pipeline.is_file() else []
    artifact_dirs = find_artifacts_dirs(root)
    recent = {
        batch.relative_to(root).as_posix()
        for artifacts_dir in artifact_dirs
        for batch in batch_dirs(artifacts_dir)[-keep:] if keep > 0
    }
    protected = referenced_batches(root, nodes, recent)
    moves: list[tuple[Path, Path]] = []
    for artifacts_dir in artifact_dirs:
        project_rel = artifacts_dir.parent.relative_to(root)
        dirty = dirty_paths(root, artifacts_dir) if tracked_only else set()
        for batch in legacy_dirs(artifacts_dir) + batch_dirs(artifacts_dir):
            relative = batch.relative_to(root).as_posix()
            if relative in protected:
                continue
            if dirty and any(path == relative or path.startswith(relative + "/") for path in dirty):
                continue  # 有未提交内容：留给作者处理（不在 git 仓库时 dirty 为 None，不过滤）
            moves.append((batch, dest_root / project_rel / batch.name))
    return moves


def file_hashes(directory: Path) -> dict[str, str]:
    return {path.relative_to(directory).as_posix(): sha256(path) for path in sorted(directory.rglob("*")) if path.is_file()}


def archive_batch(source: Path, target: Path) -> dict:
    """复制到 target 并逐文件校验后删除 source；返回索引记录（不含批次路径）。"""
    if target.exists():
        raise SystemExit(f"目标已存在，拒绝覆盖：{target}")
    hashes = file_hashes(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(f".{target.name}.tmp")
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(source, staging)
    copied = file_hashes(staging)
    if copied != hashes:
        shutil.rmtree(staging)
        raise SystemExit(f"复制校验失败，未删除本地：{source}")
    os.replace(staging, target)
    size = sum(path.stat().st_size for path in source.rglob("*") if path.is_file())
    shutil.rmtree(source)
    return {"files": len(hashes), "bytes": size, "sha256": hashes}


def append_index(path: Path, entry: dict) -> None:
    payload = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"schema_version": 1, "archives": []}
    payload["archives"].append(entry)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keep", type=int, default=5, help="每个 artifacts 目录保留的最近批次数（默认 5）")
    parser.add_argument("--root", type=Path, default=ROOT, help="仓库根目录（默认脚本所在目录）")
    parser.add_argument("--dest", type=Path, help="归档根目录（默认 <仓库>/.bak/artifacts），如 NAS 的 PQData/bak/all_cars_data/artifacts")
    parser.add_argument("--include-dirty", action="store_true", help="也归档含未提交文件的批次（默认跳过）")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不实际移动")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    dest_root = args.dest or root / ".bak" / "artifacts"
    moves = plan_moves(root, args.keep, dest_root, tracked_only=not args.include_dirty)
    if not moves:
        print("没有需要归档的批次。")
        return 0

    entry = {"archived_at": datetime.now().astimezone().isoformat(timespec="seconds"), "dest": str(dest_root), "keep": args.keep, "batches": []}
    total = 0
    for src, dest in moves:
        print(f"{'[dry-run] ' if args.dry_run else ''}{src.relative_to(root).as_posix()} -> {dest}", flush=True)
        if args.dry_run:
            total += sum(path.stat().st_size for path in src.rglob("*") if path.is_file())
            continue
        record = archive_batch(src, dest)
        total += record["bytes"]
        entry["batches"].append({"batch": src.relative_to(root).as_posix(), "archive_path": str(dest), **record})

    if not args.dry_run:
        append_index(root / INDEX_NAME, entry)
        append_index(dest_root / DEST_INDEX_NAME, entry)
    print(f"{'将归档' if args.dry_run else '已归档'} {len(moves)} 个批次，{total / 2**20:.0f} MB → {dest_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
