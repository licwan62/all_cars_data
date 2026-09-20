from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE_DIR_NAMES = {".bak", "node_modules", "__pycache__", ".git"}


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


def plan_moves(root: Path, keep: int) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    for artifacts_dir in find_artifacts_dirs(root):
        batches = batch_dirs(artifacts_dir)
        if len(batches) <= keep:
            continue
        project_rel = artifacts_dir.parent.relative_to(root)
        for batch in batches[: len(batches) - keep]:
            dest = root / ".bak" / "artifacts" / project_rel / batch.name
            moves.append((batch, dest))
    return moves


def main() -> int:
    parser = argparse.ArgumentParser(
        description="把各项目 artifacts 目录下较旧的批次移入 .bak/artifacts/<项目>/<批次>，只保留最近 N 个。"
    )
    parser.add_argument("--keep", type=int, default=5, help="每个 artifacts 目录保留的最近批次数（默认 5）")
    parser.add_argument("--root", type=Path, default=ROOT, help="仓库根目录（默认脚本所在目录）")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不实际移动")
    args = parser.parse_args()

    root = args.root.resolve()
    moves = plan_moves(root, args.keep)

    if not moves:
        print("没有需要归档的批次。")
        return 0

    for src, dest in moves:
        print(f"{'[dry-run] ' if args.dry_run else ''}{src.relative_to(root)} -> {dest.relative_to(root)}")
        if args.dry_run:
            continue
        if dest.exists():
            raise SystemExit(f"目标已存在，拒绝覆盖：{dest}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))

    print(f"{'将移动' if args.dry_run else '已移动'} {len(moves)} 个批次。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
