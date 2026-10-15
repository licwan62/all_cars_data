#!/usr/bin/env python3
"""为仓库根目录 ``.bak/`` 生成迁移计划，并在获准后按计划复制到 NAS、校验、再删除本地。

``.bak/`` 是 2026-09 前后手工移出的旧批次（``.bak/<节点简称>/<批次>/``），不在 Git 中，节点归档工具
``archive_old_artifacts.py`` 不处理它。本工具按“迁移单元”（``.bak`` 下第二层目录，即一个旧批次）记录：

- 源路径、目标路径（默认 ``\\\\NAS8824B4\\Public\\PQData\\bak\\all_cars_data\\dotbak\\<子目录>\\<批次>``）；
- 每个文件的大小与 SHA-256；
- 潜在引用：在 Git 跟踪的文本文件（json/md/yaml/csv/py 等）中出现该批次名的位置（只按批次名匹配，
  不同节点的同名批次会互相计入，需人工复核）；
- 文件在 Git 历史中是否存在同字节 blob（``git hash-object`` 后查 ``git cat-file -e``）：不在历史中的文件
  只在本地存在，迁移失败即丢失，需优先校验。

    python scripts/plan_bak_migration.py --plan-out plan.json --md-out plan.md          # 只读，生成计划
    python scripts/plan_bak_migration.py --execute plan.json                            # 复制并逐文件校验（不删除）
    python scripts/plan_bak_migration.py --execute plan.json --delete-source            # 校验通过后删除本地（需用户确认）

执行时目标已存在且内容不同则拒绝；源文件与计划记录的 SHA-256 不一致（计划过期）则拒绝；每个单元复制后
逐文件校验，全部一致才删除该单元的本地源。完成后追加 ``<目标根>/DOTBAK_INDEX.json`` 与仓库根目录
``artifacts_archive.json``（``kind: dotbak``），可据此恢复原路径。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
BAK = ROOT / ".bak"
DEFAULT_DEST = r"\\NAS8824B4\Public\PQData\bak\all_cars_data\dotbak"
TEXT_SUFFIXES = {".json", ".md", ".yaml", ".yml", ".csv", ".py", ".txt", ".ps1", ".tsv"}
INDEX_NAME = "artifacts_archive.json"
DEST_INDEX_NAME = "DOTBAK_INDEX.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def units(bak: Path) -> list[Path]:
    found = []
    for first in sorted(p for p in bak.iterdir() if p.is_dir()):
        for second in sorted(first.iterdir()):
            found.append(second)
    return found


def tracked_text_files(root: Path) -> list[Path]:
    out = subprocess.run(["git", "-c", "core.quotepath=off", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout
    return [root / p for p in out.decode("utf-8").split("\0") if p and Path(p).suffix.lower() in TEXT_SUFFIXES and "node_modules" not in p]


def find_references(names: list[str], files: list[Path], root: Path) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {name: [] for name in names}
    for path in files:
        try:
            if path.stat().st_size > 20_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for name in names:
            if name in text:
                refs[name].append(path.relative_to(root).as_posix())
    return refs


def blobs_in_history(paths: list[Path], root: Path) -> set[Path]:
    """返回内容已作为 blob 存在于本仓库对象库中的文件。"""

    if not paths:
        return set()
    present: set[Path] = set()
    chunk = 200
    # 原始字节与经 autocrlf 等过滤后的字节各查一次：提交时 CRLF 可能被归一为 LF
    for extra in (["--no-filters"], []):
        for start in range(0, len(paths), chunk):
            batch = [p for p in paths[start:start + chunk] if p not in present]
            if not batch:
                continue
            hashes = subprocess.run(["git", "hash-object", "--stdin-paths", *extra], cwd=root, input="\n".join(str(p) for p in batch),
                                    capture_output=True, encoding="utf-8", check=True).stdout.split()
            check = subprocess.run(["git", "cat-file", "--batch-check"], cwd=root, input="\n".join(hashes), capture_output=True, encoding="utf-8").stdout.splitlines()
            for path, line in zip(batch, check):
                if not line.endswith("missing"):
                    present.add(path)
    return present


def build_plan(dest_root: str) -> dict:
    tracked = tracked_text_files(ROOT)
    unit_dirs = units(BAK)
    refs = find_references(sorted({u.name for u in unit_dirs}), tracked, ROOT)
    plan_units = []
    for unit in unit_dirs:
        files = sorted(p for p in unit.rglob("*") if p.is_file()) if unit.is_dir() else [unit]
        in_history = blobs_in_history(files, ROOT)
        rel_unit = unit.relative_to(BAK)
        entries = [
            {"path": p.relative_to(unit).as_posix() if unit.is_dir() else p.name, "bytes": p.stat().st_size, "sha256": sha256(p), "in_git_history": p in in_history}
            for p in files
        ]
        plan_units.append({
            "source": (Path(".bak") / rel_unit).as_posix(),
            "dest": str(PureWindowsPath(dest_root, *rel_unit.parts)),
            "is_dir": unit.is_dir(),
            "files": len(entries),
            "bytes": sum(e["bytes"] for e in entries),
            "local_only_files": sum(not e["in_git_history"] for e in entries),
            "references": refs.get(unit.name, []),
            "entries": entries,
        })
    return {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_root": ".bak",
        "dest_root": dest_root,
        "note": ".bak 被 .gitignore 忽略，全部文件都未提交；in_git_history 表示同字节内容可从 Git 对象库恢复。",
        "units": plan_units,
        "totals": {
            "units": len(plan_units),
            "files": sum(u["files"] for u in plan_units),
            "bytes": sum(u["bytes"] for u in plan_units),
            "local_only_bytes": sum(e["bytes"] for u in plan_units for e in u["entries"] if not e["in_git_history"]),
            "referenced_units": sum(bool(u["references"]) for u in plan_units),
        },
    }


def to_markdown(plan: dict) -> str:
    t = plan["totals"]
    lines = [
        "# .bak 迁移计划",
        "",
        f"- 生成时间：{plan['generated_at']}；源：仓库 `.bak/`；目标根：`{plan['dest_root']}`",
        f"- 单元 {t['units']} 个，文件 {t['files']:,} 个，{t['bytes'] / 1e9:.3f} GB（十进制）；其中仅本地存在（不在 Git 对象库）"
        f" {t['local_only_bytes'] / 1e9:.3f} GB；被 Git 跟踪文本引用的单元 {t['referenced_units']} 个。",
        f"- {plan['note']}",
        "- 逐文件 SHA-256 见同名 JSON 计划。执行：`python scripts/plan_bak_migration.py --execute <plan.json> [--delete-source]`。",
        "",
        "| 源 | 文件数 | MB | 仅本地文件 | 引用 |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for u in plan["units"]:
        ref = "<br>".join(f"`{r}`" for r in u["references"][:3]) + (f" 等 {len(u['references'])} 处" if len(u["references"]) > 3 else "")
        lines.append(f"| `{u['source']}` | {u['files']:,} | {u['bytes'] / 1e6:.1f} | {u['local_only_files']:,} | {ref or '—'} |")
    return "\n".join(lines) + "\n"


def execute(plan_path: Path, delete_source: bool) -> int:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    done: list[dict] = []
    try:
        return _execute_units(plan, delete_source, done)
    finally:
        if done:  # 中途失败也要登记已完成（可能已删除本地）的单元
            _append_index(plan, done)


def _execute_units(plan: dict, delete_source: bool, done: list[dict]) -> int:
    for unit in plan["units"]:
        src = (ROOT / unit["source"]).resolve()
        if BAK.resolve() not in src.parents:
            print(f"拒绝：{src} 不在 .bak 内", file=sys.stderr)
            return 2
        dest = Path(unit["dest"])
        if not src.exists():
            print(f"跳过（源已不存在）：{unit['source']}")
            continue
        for entry in unit["entries"]:
            source_file = src / entry["path"] if unit["is_dir"] else src
            if sha256(source_file) != entry["sha256"]:
                print(f"拒绝：计划已过期，{unit['source']}/{entry['path']} 与计划 SHA-256 不一致", file=sys.stderr)
                return 2
            target = dest / entry["path"] if unit["is_dir"] else dest
            if target.exists():
                if sha256(target) != entry["sha256"]:
                    print(f"拒绝：目标已存在且内容不同 {target}", file=sys.stderr)
                    return 2
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target)
        bad = [e["path"] for e in unit["entries"] if sha256(dest / e["path"] if unit["is_dir"] else dest) != e["sha256"]]
        if bad:
            print(f"校验失败，保留本地：{unit['source']}：{bad[:5]}", file=sys.stderr)
            return 1
        print(f"已复制并校验 {unit['files']} 个文件：{unit['source']} -> {dest}")
        if delete_source:
            if unit["is_dir"]:
                shutil.rmtree(src)
            else:
                src.unlink()
            print(f"  已删除本地 {unit['source']}")
        done.append({"source": unit["source"], "archive_path": str(dest), "files": unit["files"], "bytes": unit["bytes"],
                     "sha256": {e["path"]: e["sha256"] for e in unit["entries"]}, "local_deleted": delete_source})
    return 0


def _append_index(plan: dict, done: list[dict]) -> None:
    record = {"archived_at": datetime.now().astimezone().isoformat(timespec="seconds"), "kind": "dotbak", "dest": plan["dest_root"], "units": done}
    index = ROOT / INDEX_NAME
    data = json.loads(index.read_text(encoding="utf-8")) if index.is_file() else {"schema_version": 1, "archives": []}
    data["archives"].append(record)
    index.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    dest_index = Path(plan["dest_root"]) / DEST_INDEX_NAME
    existing = json.loads(dest_index.read_text(encoding="utf-8")) if dest_index.is_file() else {"schema_version": 1, "archives": []}
    existing["archives"].append(record)
    dest_index.write_text(json.dumps(existing, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dest", default=DEFAULT_DEST)
    parser.add_argument("--plan-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--execute", type=Path, metavar="PLAN_JSON")
    parser.add_argument("--delete-source", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    if args.execute:
        return execute(args.execute, args.delete_source)
    if not BAK.is_dir():
        print("没有 .bak/，无需迁移")
        return 0
    plan = build_plan(args.dest)
    if args.plan_out:
        args.plan_out.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    text = to_markdown(plan)
    if args.md_out:
        args.md_out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
