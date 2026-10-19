#!/usr/bin/env python3
"""资料与责任登记草案（只读）：扫描各节点 data/，生成资料目录草案与归属/重复/缺证清单。

改造方案工作包 0 的第一步：先登记现有资料位置与身份，不移动文件、不改变结果。草案写到
``reports/资料登记草案/``，不写入任何节点 data/（写入会改变规则快照、使节点判为过期）；维护人确认后，
再把本节点的资料目录.csv 放进自己的 data/ 并随下一次运行发布。

生成内容：
- ``资料目录.csv``：每份 data/ 文件一行（含已登记子项目如 D2 皮卡/data）。资料ID 由系统首次生成，之后按
  (节点, 文件位置) 或内容 sha256 沿用，文件改名不改变身份。业务用途、适用范围、资料日期、维护人由维护人填写，
  草案只给推断类别与“待填写/待指定”，不虚构负责人或来源。
- ``登记摘要.md``：各节点资料数量；同内容多处保存（重复维护候选）；代码中未发现引用的资料（说明/历史/
  未启用候选）；代码从 data/ 以外读取的正式输入候选（cache/、work/ 等）；大表（确认是人工资料还是生成中间表）；
  不在 pipeline.json 登记的节点目录。

    python scripts/material_catalog.py            # 生成/刷新草案，沿用已有资料ID
    python scripts/material_catalog.py --check    # 只打印摘要，不写文件
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from rules_snapshot import _ignored, content_sha256  # noqa: E402

OUT_DIR = ROOT / "reports" / "资料登记草案"
CATALOG = "资料目录.csv"
SUMMARY = "登记摘要.md"
FIELDS = [
    "资料ID", "节点", "节点路径", "文件位置", "推断类别", "维护状态", "业务用途", "适用范围", "资料日期", "维护人",
    "替代资料ID", "内容sha256", "字节数", "行数", "代码引用", "同内容其他位置", "首次提交", "最近提交",
]
CODE_SUFFIXES = {".py", ".ps1", ".psm1", ".yaml", ".yml", ".json"}
LARGE_BYTES = 5 * 1024 * 1024
LARGE_ROWS = 20000
# 代码里以这些目录开头的相对路径：不属于 data/ 却可能承担正式业务依据
NON_DATA_DIRS = ("cache", "work", "research_queue", "source", "input", "archive")
NON_DATA_PATTERN = re.compile(r"""["'](?:\.\./)?((?:%s)/[^"'\s]+\.(?:csv|json|jsonl|xlsx|yaml|yml|tsv))["']""" % "|".join(NON_DATA_DIRS))
CATEGORY_RULES = [
    ("说明", re.compile(r"(^|/)(README|AGENTS)[^/]*$|\.md$", re.I)),
    ("例外/人工决定", re.compile(r"例外|override|修正|白名单|判定|登记|决定|exception|manual", re.I)),
    ("规则/配置", re.compile(r"规则|标准|政策|policy|rule|config|配置|产线|\.ya?ml$", re.I)),
    ("映射", re.compile(r"映射|对应|mapping|map", re.I)),
]


def as_list(value) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def infer_category(relative: str) -> str:
    for label, pattern in CATEGORY_RULES:
        if pattern.search(relative):
            return label
    return "资料/证据"


def row_count(path: Path) -> str:
    if path.suffix.lower() not in {".csv", ".tsv", ".jsonl"}:
        return ""
    with path.open("rb") as handle:
        lines = sum(1 for _ in handle)
    return str(max(lines - (0 if path.suffix.lower() == ".jsonl" else 1), 0))


def git_dates(path: Path) -> tuple[str, str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--follow", "--format=%ad", "--date=short", "--", str(path.relative_to(ROOT))],
            capture_output=True, text=True, encoding="utf-8", check=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return "", ""
    return (out[-1], out[0]) if out else ("未提交", "未提交")


def code_text(node: dict) -> str:
    base = ROOT / node["path"]
    chunks = []
    for name in as_list(node.get("code_dir")):
        for path in (base / name).rglob("*"):
            if path.suffix in CODE_SUFFIXES and path.is_file() and "__pycache__" not in path.parts and "artifacts" not in path.parts:
                chunks.append(path.read_text(encoding="utf-8-sig", errors="replace"))
    return "\n".join(chunks)


def data_dirs(node: dict) -> list[Path]:
    """节点 data/ 与 code_dir 中各子项目的 data/（如 D2 的 皮卡/data）。"""
    base = ROOT / node["path"]
    found = [base / "data"]
    for name in as_list(node.get("code_dir")):
        candidate = base / name / "data"
        if name not in {"src", "code", "scripts"} and candidate.is_dir():
            found.append(candidate)
    return [path for path in found if path.is_dir()]


def load_existing(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build(existing: list[dict], nodes: list[dict]) -> tuple[list[dict], dict]:
    by_location = {(row["节点"], row["文件位置"]): row for row in existing}
    by_sha = defaultdict(list)
    for row in existing:
        by_sha[(row["节点"], row["内容sha256"])].append(row)
    used_ids = {row["资料ID"] for row in existing}
    counters: dict[str, int] = defaultdict(int)
    for row in existing:
        match = re.match(r"^M-(.+)-(\d{4})$", row["资料ID"])
        if match:
            counters[match.group(1)] = max(counters[match.group(1)], int(match.group(2)))

    rows: list[dict] = []
    findings = {"unreferenced": [], "non_data": [], "large": [], "nodes": {}}
    for node in nodes:
        base = ROOT / node["path"]
        text = code_text(node)
        node_rows = []
        for directory in data_dirs(node):
            for path in sorted(directory.rglob("*")):
                relative_to_dir = path.relative_to(directory)
                if not path.is_file() or _ignored(relative_to_dir):
                    continue
                location = path.relative_to(base).as_posix()
                digest = content_sha256(path)
                previous = by_location.get((node["id"], location))
                if previous is None:
                    candidates = [row for row in by_sha.get((node["id"], digest), []) if (node["id"], row["文件位置"]) not in {(node["id"], r["文件位置"]) for r in rows}]
                    previous = candidates[0] if candidates else None
                if previous:
                    material_id = previous["资料ID"]
                else:
                    counters[node["id"]] += 1
                    material_id = f"M-{node['id']}-{counters[node['id']]:04d}"
                    while material_id in used_ids:
                        counters[node["id"]] += 1
                        material_id = f"M-{node['id']}-{counters[node['id']]:04d}"
                used_ids.add(material_id)
                referenced = path.name in text or path.stem in text and len(path.stem) >= 4
                first, last = git_dates(path)
                keep = previous or {}
                row = {
                    "资料ID": material_id, "节点": node["id"], "节点路径": node["path"], "文件位置": location,
                    "推断类别": infer_category(location),
                    "维护状态": keep.get("维护状态") or "待确认",
                    "业务用途": keep.get("业务用途") or "待填写",
                    "适用范围": keep.get("适用范围") or "待填写",
                    "资料日期": keep.get("资料日期") or "待填写",
                    "维护人": keep.get("维护人") or "待指定",
                    "替代资料ID": keep.get("替代资料ID", ""),
                    "内容sha256": digest, "字节数": str(path.stat().st_size), "行数": row_count(path),
                    "代码引用": "代码中出现文件名" if referenced else "未发现",
                    "同内容其他位置": "", "首次提交": first, "最近提交": last,
                }
                node_rows.append(row)
                if not referenced and row["推断类别"] != "说明":
                    findings["unreferenced"].append(row)
                if path.stat().st_size >= LARGE_BYTES or (row["行数"] and int(row["行数"]) >= LARGE_ROWS):
                    findings["large"].append(row)
        rows.extend(node_rows)
        findings["nodes"][node["id"]] = (node["path"], len(node_rows))
        config_text = "\n".join(
            path.read_text(encoding="utf-8-sig", errors="replace")
            for directory in data_dirs(node) for path in directory.rglob("*.json") if path.is_file()
        )
        hits = sorted({match.group(1) for match in NON_DATA_PATTERN.finditer(text + "\n" + config_text)})
        for hit in hits:
            exists = (base / hit).exists() or any((base / name / hit).exists() for name in as_list(node.get("code_dir")))
            tracked = bool(subprocess.run(
                ["git", "-C", str(ROOT), "ls-files", "--", f"{node['path']}/{hit}"], capture_output=True, text=True, encoding="utf-8",
            ).stdout.strip())
            if exists:
                findings["non_data"].append((node["path"], hit, "已提交到 Git" if tracked else "未跟踪"))
    by_digest = defaultdict(list)
    for row in rows:
        if int(row["字节数"]) > 0 and row["推断类别"] != "说明":
            by_digest[row["内容sha256"]].append(row)
    duplicates = [group for group in by_digest.values() if len(group) > 1]
    for group in duplicates:
        for row in group:
            row["同内容其他位置"] = "；".join(f"{other['节点路径']}/{other['文件位置']}" for other in group if other is not row)
    findings["duplicates"] = duplicates
    registered = {(ROOT / node["path"]).resolve() for node in nodes}
    findings["unregistered_dirs"] = sorted(
        path.name for path in ROOT.iterdir()
        if path.is_dir() and re.match(r"^[0-9A-Z]\d?\.", path.name) and path.resolve() not in registered
    )
    return rows, findings


def render_summary(rows: list[dict], findings: dict) -> str:
    lines = [
        "# 资料与责任登记草案摘要", "",
        "由 `python scripts/material_catalog.py` 生成，只读扫描各节点 data/ 与代码；不移动文件、不改变任何交付。",
        "推断类别、代码引用均为启发式结果，需节点维护人确认；业务用途、适用范围、资料日期、维护人保持“待填写/待指定”，",
        "不虚构来源或负责人。确认后的资料目录放入各节点自己的 data/，随下一次运行发布。", "",
        "## 各节点资料数量", "", "| 节点 | 资料数 |", "| --- | ---: |",
    ]
    lines += [f"| {path} | {count} |" for path, count in findings["nodes"].values()]
    lines += ["", f"合计 {len(rows)} 份。", ""]
    lines += ["## 同内容多处保存（重复维护候选）", ""]
    if findings["duplicates"]:
        lines += ["同一业务事实应只在一个归属节点维护；其他节点改为读取归属节点 output 或登记来源关系。", ""]
        for group in findings["duplicates"]:
            lines.append("- " + "；".join(f"`{row['节点路径']}/{row['文件位置']}`" for row in group))
    else:
        lines.append("- 未发现。")
    lines += ["", "## data/ 以外的正式输入候选", "",
              "代码或 data/ 配置引用、且实际存在的 cache/、work/ 等路径。若承担长期业务依据（如销量证据、分配权重），应迁入 data/；",
              "若可由运行重建，则保持可重建并从正式依据中去掉。", ""]
    lines += [f"- `{path}/{hit}`（{state}）" for path, hit, state in findings["non_data"]] or ["- 未发现。"]
    lines += ["", "## 大表（确认是人工维护资料还是生成中间表）", ""]
    lines += [f"- `{row['节点路径']}/{row['文件位置']}`：{int(row['字节数']) / 1048576:.1f} MB，{row['行数'] or '-'} 行" for row in findings["large"]] or ["- 未发现。"]
    lines += ["", "## 代码中未发现引用的资料（说明/历史/未启用候选）", "",
              "按文件名在 code_dir 中查找，未出现不等于未使用（可能按目录整体读取）；请维护人标注业务用途或历史停用。", ""]
    by_node = defaultdict(list)
    for row in findings["unreferenced"]:
        by_node[row["节点路径"]].append(row["文件位置"])
    lines += [f"- {path}：" + "、".join(f"`{name}`" for name in names) for path, names in by_node.items()] or ["- 未发现。"]
    lines += ["", "## 未在 pipeline.json 登记的节点目录", ""]
    lines += [f"- `{name}`" for name in findings["unregistered_dirs"]] or ["- 未发现。"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="只打印摘要，不写文件")
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)
    nodes = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))["nodes"]
    rows, findings = build(load_existing(args.out / CATALOG), nodes)
    summary = render_summary(rows, findings)
    if args.check:
        print(summary)
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / CATALOG).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    (args.out / SUMMARY).write_text(summary, encoding="utf-8")
    print(f"已写入 {args.out / CATALOG}（{len(rows)} 份资料）与 {args.out / SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
