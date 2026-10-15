#!/usr/bin/env python3
"""只读存储审计：统计目录字节数/文件数、Git 跟踪情况、Git 历史占用与历史批次重复字节。

    python scripts/storage_audit.py                                   # 审计本仓库
    python scripts/storage_audit.py --root ../pipeline_carstable_to_webapp --json-out audit.json --md-out audit.md
    python scripts/storage_audit.py --no-hash --no-git-history        # 快速模式

口径：
- 字节数为文件逻辑大小（``st_size``，不是磁盘占用），GB/MB 为十进制（1 GB = 10^9 B），MiB 为 2^20 B。
- 每个文件按路径归入唯一类别（优先级从高到低）：``.git``、``node_modules``（任意层）、``backup``（顶层 ``.bak``/``bak``）、
  ``artifacts``（任意层 ``artifacts``/``artifact`` 目录）、``work``、``cache``（``cache``/``__pycache__``/``.pytest_cache``）、
  ``logs``、``output``、``public``、``data``、``other``。
- Git 跟踪：``git ls-files`` 当前索引，大小取工作区文件。Git 历史：``git rev-list --objects --all`` 中每个 blob 的
  打包后磁盘大小（``objectsize:disk``）按其首次出现的路径归类，反映“缩减 Git 历史”可能的收益上限。
- 重复字节：只在 ``--dup-category`` 指定类别（默认 artifacts）内统计；先按大小分组，只对同大小且 ≥ ``--min-dup-size``
  的文件计算 SHA-256；重复字节 = 总字节 − 去重后字节。重复字节不等于可删除字节（历史批次不可变）。
- 排除：符号链接与无法读取的文件（计入 ``errors``）；``.git`` 只统计大小，不参与哈希。

本工具只读，不修改任何文件。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

CATEGORIES = ["git", "node_modules", "backup", "artifacts", "work", "cache", "logs", "output", "public", "data", "other"]
CACHE_NAMES = {"cache", "__pycache__", ".pytest_cache"}


def classify(parts: tuple[str, ...]) -> str:
    """按路径各级目录名（相对根，不含文件名）归类。"""

    dirs = parts[:-1]
    if parts and parts[0] == ".git":
        return "git"
    if "node_modules" in dirs:
        return "node_modules"
    if dirs and dirs[0] in {".bak", "bak"}:
        return "backup"
    if any(d in {"artifacts", "artifact"} for d in dirs):
        return "artifacts"
    if "work" in dirs:
        return "work"
    if any(d in CACHE_NAMES for d in dirs):
        return "cache"
    if "logs" in dirs:
        return "logs"
    if "output" in dirs:
        return "output"
    if "public" in dirs:
        return "public"
    if "data" in dirs:
        return "data"
    return "other"


def walk(root: Path):
    """产出 (相对路径 parts, 大小)；不跟随符号链接。"""

    stack = [root]
    errors: list[str] = []
    while stack:
        current = stack.pop()
        try:
            entries = list(os.scandir(current))
        except OSError as exc:
            errors.append(f"{current}: {exc}")
            continue
        for entry in entries:
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    stack.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    rel = Path(entry.path).relative_to(root)
                    yield rel.parts, entry.stat(follow_symlinks=False).st_size
            except OSError as exc:
                errors.append(f"{entry.path}: {exc}")
    walk.errors = errors  # type: ignore[attr-defined]


def git_lines(root: Path, *args: str, stdin: bytes | None = None) -> list[str]:
    result = subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=root, input=stdin, capture_output=True, check=True)
    return result.stdout.decode("utf-8", errors="replace").split("\0" if "-z" in args else "\n")


def git_tracked(root: Path) -> set[str]:
    try:
        return {line for line in git_lines(root, "ls-files", "-z") if line}
    except (OSError, subprocess.CalledProcessError):
        return set()


def git_history(root: Path) -> dict:
    """Git 历史中各类别 blob 的打包后大小（按首次出现路径归类）。"""

    try:
        objects = subprocess.run(["git", "-c", "core.quotepath=off", "rev-list", "--objects", "--all"], cwd=root, capture_output=True, check=True).stdout
        batch = subprocess.run(
            ["git", "cat-file", "--batch-check=%(objecttype) %(objectsize) %(objectsize:disk) %(rest)"],
            cwd=root, input=objects, capture_output=True, check=True,
        ).stdout.decode("utf-8", errors="replace")
    except (OSError, subprocess.CalledProcessError) as exc:
        return {"error": str(exc)}
    by_cat: dict[str, dict[str, int]] = defaultdict(lambda: {"blobs": 0, "bytes": 0, "disk_bytes": 0})
    top_paths: dict[str, int] = defaultdict(int)
    for line in batch.splitlines():
        kind, size, disk, *rest = line.split(" ", 3)
        if kind != "blob":
            continue
        path = rest[0] if rest else ""
        parts = tuple(path.split("/")) if path else ("?",)
        cat = classify(parts) if path else "other"
        stats = by_cat[cat]
        stats["blobs"] += 1
        stats["bytes"] += int(size)
        stats["disk_bytes"] += int(disk)
        prefix = "/".join(parts[:3]) if len(parts) > 3 else "/".join(parts[:-1]) or path
        top_paths[prefix] += int(disk)
    largest = sorted(top_paths.items(), key=lambda kv: kv[1], reverse=True)[:20]
    return {"by_category": dict(by_cat), "largest_path_prefixes_disk": [{"prefix": p, "disk_bytes": b} for p, b in largest]}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duplicate_stats(root: Path, files: list[tuple[str, int]], min_size: int) -> dict:
    by_size: dict[int, list[str]] = defaultdict(list)
    for rel, size in files:
        by_size[size].append(rel)
    total = sum(size for _, size in files)
    hashed = 0
    by_hash: dict[str, list[str]] = {}
    unique_bytes = 0
    errors: list[str] = []
    for size, paths in by_size.items():
        if len(paths) == 1 or size < min_size:
            # 大小唯一必然不重复；小文件不哈希，按唯一计（保守低估重复量）
            unique_bytes += size * len(paths)
            continue
        groups: dict[str, list[str]] = defaultdict(list)
        for rel in paths:
            try:
                groups[sha256(root / rel)].append(rel)
                hashed += 1
            except OSError as exc:
                errors.append(f"{rel}: {exc}")
        for digest, members in groups.items():
            unique_bytes += size
            if len(members) > 1:
                by_hash[digest] = members
    dup_bytes = total - unique_bytes
    top = sorted(by_hash.items(), key=lambda kv: (len(kv[1]) - 1) * (root / kv[1][0]).stat().st_size, reverse=True)[:15]
    return {
        "files": len(files),
        "bytes": total,
        "hashed_files": hashed,
        "unique_bytes": unique_bytes,
        "duplicate_bytes": dup_bytes,
        "duplicate_groups": len(by_hash),
        "min_hashed_size": min_size,
        "top_groups": [
            {"copies": len(m), "size": (root / m[0]).stat().st_size, "sha256": d, "examples": m[:3]} for d, m in top
        ],
        "errors": errors,
    }


def fmt(num: int) -> str:
    for unit, factor in (("GB", 10**9), ("MB", 10**6), ("KB", 10**3)):
        if num >= factor:
            return f"{num / factor:.2f} {unit}"
    return f"{num} B"


def audit(root: Path, do_hash: bool, do_history: bool, dup_categories: set[str], min_dup: int, depth: int) -> dict:
    tracked = git_tracked(root)
    cats: dict[str, dict[str, int]] = {c: {"files": 0, "bytes": 0, "tracked_files": 0, "tracked_bytes": 0} for c in CATEGORIES}
    tops: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0, "tracked_files": 0})
    dup_pool: list[tuple[str, int]] = []
    for parts, size in walk(root):
        rel = "/".join(parts)
        cat = classify(parts)
        is_tracked = rel in tracked
        bucket = cats[cat]
        bucket["files"] += 1
        bucket["bytes"] += size
        if is_tracked:
            bucket["tracked_files"] += 1
            bucket["tracked_bytes"] += size
        key = "/".join(parts[: min(depth, len(parts) - 1)]) or "<root files>"
        tops[key]["files"] += 1
        tops[key]["bytes"] += size
        tops[key]["tracked_files"] += int(is_tracked)
        if do_hash and cat in dup_categories:
            dup_pool.append((rel, size))
    head = ""
    try:
        head = git_lines(root, "rev-parse", "HEAD")[0].strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    report = {
        "root": str(root),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "git_head": head,
        "units": "bytes (logical st_size); GB/MB decimal",
        "totals": {"files": sum(c["files"] for c in cats.values()), "bytes": sum(c["bytes"] for c in cats.values()),
                   "tracked_files": len(tracked), "tracked_bytes": sum(c["tracked_bytes"] for c in cats.values())},
        "categories": cats,
        "top_dirs": dict(sorted(tops.items(), key=lambda kv: kv[1]["bytes"], reverse=True)),
        "walk_errors": getattr(walk, "errors", []),
    }
    if do_hash:
        report["duplicates"] = {"categories": sorted(dup_categories), **duplicate_stats(root, dup_pool, min_dup)}
    if do_history:
        report["git_history"] = git_history(root)
    return report


def to_markdown(report: dict, top_n: int) -> str:
    lines = [
        f"# 存储审计：{report['root']}",
        "",
        f"- 时间：{report['generated_at']}；Git HEAD：`{report['git_head'] or '-'}`",
        f"- 单位：{report['units']}；口径与排除项见 `scripts/storage_audit.py` 文档字符串。",
        f"- 合计：{report['totals']['files']:,} 个文件，{fmt(report['totals']['bytes'])}；"
        f"Git 跟踪 {report['totals']['tracked_files']:,} 个（工作区大小 {fmt(report['totals']['tracked_bytes'])}）",
        "",
        "## 按类别",
        "",
        "| 类别 | 文件数 | 字节 | Git 跟踪文件 | 跟踪字节 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, c in sorted(report["categories"].items(), key=lambda kv: kv[1]["bytes"], reverse=True):
        if c["files"]:
            lines.append(f"| {name} | {c['files']:,} | {fmt(c['bytes'])} | {c['tracked_files']:,} | {fmt(c['tracked_bytes'])} |")
    lines += ["", f"## 最大目录（前 {top_n}）", "", "| 目录 | 文件数 | 字节 | Git 跟踪文件 |", "| --- | ---: | ---: | ---: |"]
    for name, c in list(report["top_dirs"].items())[:top_n]:
        lines.append(f"| `{name}` | {c['files']:,} | {fmt(c['bytes'])} | {c['tracked_files']:,} |")
    dup = report.get("duplicates")
    if dup:
        lines += [
            "",
            f"## 重复字节（类别：{', '.join(dup['categories'])}）",
            "",
            f"- 文件 {dup['files']:,} 个，{fmt(dup['bytes'])}；哈希 {dup['hashed_files']:,} 个（≥ {dup['min_hashed_size']} B 且同大小）",
            f"- 去重后 {fmt(dup['unique_bytes'])}；重复 {fmt(dup['duplicate_bytes'])}（{dup['duplicate_groups']:,} 组）。重复量不是可删除量。",
        ]
        for g in dup["top_groups"][:8]:
            lines.append(f"  - {g['copies']} 份 × {fmt(g['size'])}：`{g['examples'][0]}`")
    hist = report.get("git_history")
    if hist and "by_category" in hist:
        lines += ["", "## Git 历史（全部引用可达 blob，按首次路径归类）", "", "| 类别 | blob 数 | 原始字节 | 打包后字节 |", "| --- | ---: | ---: | ---: |"]
        for name, c in sorted(hist["by_category"].items(), key=lambda kv: kv[1]["disk_bytes"], reverse=True):
            lines.append(f"| {name} | {c['blobs']:,} | {fmt(c['bytes'])} | {fmt(c['disk_bytes'])} |")
        lines += ["", "打包后占用最大的路径前缀：", ""]
        for item in hist["largest_path_prefixes_disk"][:10]:
            lines.append(f"- `{item['prefix']}`：{fmt(item['disk_bytes'])}")
    if report["walk_errors"]:
        lines += ["", f"读取错误 {len(report['walk_errors'])} 项（见 JSON）。"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--no-hash", action="store_true", help="不统计重复字节")
    parser.add_argument("--no-git-history", action="store_true", help="不统计 Git 历史")
    parser.add_argument("--dup-category", action="append", choices=CATEGORIES, help="统计重复的类别（可多次，默认 artifacts）")
    parser.add_argument("--min-dup-size", type=int, default=1024)
    parser.add_argument("--depth", type=int, default=2, help="按目录汇总的层数")
    parser.add_argument("--top", type=int, default=25)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    report = audit(root, not args.no_hash, not args.no_git_history, set(args.dup_category or ["artifacts"]), args.min_dup_size, args.depth)
    text = to_markdown(report, args.top)
    if args.json_out:
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(text, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
