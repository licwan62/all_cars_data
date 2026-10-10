#!/usr/bin/env python3
"""生成根目录 ``流水线状态.md``：反映当前已发布的流水线状态。

内容完全由 ``pipeline.json``、各节点 ``output/manifest.json`` 与 ``release.json`` 推导，
不含运行时刻等易变信息，因此同一发布状态总是渲染出相同的文本。

- 写入：只由 ``scripts/publish_release.py`` 在每次正式发布后调用 ``write_status``。
- 校验：``scripts/validate_pipeline_structure.py`` 调用 ``check_status``，文件被临时工作
  改动或未随发布更新都会校验失败。

    python scripts/pipeline_status.py --check   # 只校验，不写入
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_NAME = "流水线状态.md"
LINE_NAMES = {"U": "上游", "A": "A 全量表", "B": "B 定制评分", "C": "C 代表车型", "D": "D 发货单", "E": "E 尺寸分析", "F": "F 定制分析", "X": "X 旁路"}
TRIGGERS = {"auto": "自动", "on_demand": "按需"}
ON_DEMAND_STATE = "按需待刷新"


def node_trigger(payload: dict, node: dict) -> str:
    """节点触发方式：节点 trigger 字段优先，否则取 pipeline.json line_triggers 中所在线的设置，缺省 auto。"""
    return node.get("trigger") or payload.get("line_triggers", {}).get(node.get("line", "U"), "auto")


def is_on_demand(payload: dict, node: dict) -> bool:
    """按需节点不随默认发布刷新；上游更新只标为“按需待刷新”，不算过期。"""
    return node_trigger(payload, node) == "on_demand"


def _load_json(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else None


def _manifest(root: Path, node: dict) -> dict | None:
    return _load_json(root / node["path"] / "output" / "manifest.json")


def node_state(root: Path, node: dict, by_id: dict[str, dict], on_demand: bool = False) -> tuple[str, list[str]]:
    """返回 (状态, 说明)。状态：最新 / 过期 / 按需待刷新 / 待产出 / 未发布。

    ``on_demand`` 节点的上游更新只说明“需要时可刷新”，状态为 按需待刷新 而不是 过期。
    """
    manifest = _manifest(root, node)
    if manifest is None:
        return "未发布", ["缺少 output/manifest.json"]
    notes: list[str] = []
    recorded = {item["node"]: item for item in manifest.get("upstream", [])}
    for upstream_id in node.get("upstream", []):
        upstream = by_id[upstream_id]
        current = _manifest(root, upstream) or {}
        current_sha = {item["file"]: item["sha256"] for item in current.get("deliverables", [])}
        used = recorded.get(upstream_id)
        if used is None:
            notes.append(f"未记录上游 {upstream['path']} 的输入版本")
            continue
        changed = [item["file"] for item in used.get("files", []) if current_sha.get(item["file"]) != item["sha256"]]
        if changed:
            notes.append(
                f"上游 {upstream['path']} 已更新（使用 {used.get('version')}，当前 {current.get('version')}）：{'、'.join(changed)}"
            )
    if notes:
        return (ON_DEMAND_STATE if on_demand else "过期"), notes
    if not manifest.get("deliverables") and node.get("pending"):
        return "待产出", []
    return "最新", []


def render_status(root: Path = ROOT) -> str:
    payload = json.loads((root / "pipeline.json").read_text(encoding="utf-8"))
    nodes = payload["nodes"]
    by_id = {node["id"]: node for node in nodes}
    release = _load_json(root / "release.json") or {}
    states = {node["id"]: node_state(root, node, by_id, is_on_demand(payload, node)) for node in nodes}

    counts: dict[str, int] = {}
    for state, _ in states.values():
        counts[state] = counts.get(state, 0) + 1
    lines = [
        "# 流水线状态",
        "",
        "> 本文件由 `python scripts/publish_release.py` 在每次发布后自动生成，请勿手工或在临时工作中修改；",
        "> `python scripts/validate_pipeline_structure.py` 会校验它与各节点 `output/manifest.json` 一致。",
        "",
        f"- 最近发布：`{release.get('released_at', '-')}`",
        f"- 节点：{len(nodes)} 个；" + "，".join(f"{state} {counts[state]}" for state in ("最新", "过期", ON_DEMAND_STATE, "待产出", "未发布") if counts.get(state)),
        "",
        "## 节点",
        "",
        "| 节点 | 产线 | 触发 | 版本 | 交付物 | 上游 | 待产出 | 状态 |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for node in nodes:
        manifest = _manifest(root, node) or {}
        upstream = "、".join(by_id[up]["path"] for up in node.get("upstream", [])) or "—"
        pending = "、".join(node.get("pending", [])) or "—"
        state, _ = states[node["id"]]
        lines.append(
            f"| {node['path']} | {LINE_NAMES.get(node.get('line', 'U'), node.get('line', ''))} | "
            f"{TRIGGERS.get(node_trigger(payload, node), node_trigger(payload, node))} | `{manifest.get('version', '-')}` | {len(manifest.get('deliverables', []))} | {upstream} | {pending} | {state} |"
        )

    problems = [(node, notes) for node in nodes for state, notes in [states[node["id"]]] if notes and state != ON_DEMAND_STATE]
    lines += ["", "## 需要处理", ""]
    if problems:
        for node, notes in problems:
            lines.extend(f"- {node['path']}：{note}" for note in notes)
    else:
        lines.append("- 无：所有自动发布节点使用的都是上游当前版本。")

    deferred = [(node, notes) for node in nodes for state, notes in [states[node["id"]]] if state == ON_DEMAND_STATE]
    if deferred:
        lines += [
            "",
            f"## {ON_DEMAND_STATE}",
            "",
            "> 按需节点不随上游发布自动刷新；需要时在节点目录运行 `run`，再 `python scripts/publish_release.py --nodes <id>`。",
            "",
        ]
        for node, notes in deferred:
            lines.extend(f"- {node['path']}（`{node['id']}`）：{note}" for note in notes)

    lines += ["", "## 最终产物", "", "| 产物 | 节点 | 文件 | 待产出 |", "| --- | --- | --- | --- |"]
    for product in payload.get("final_products", []):
        node = by_id.get(product.get("node"), {})
        files = "、".join(f"`{name}`" for name in product.get("files", [])) or "—"
        pending = "、".join(product.get("pending", [])) or "—"
        lines.append(f"| {product['name']} | {node.get('path', product.get('node'))} | {files} | {pending} |")

    lines += ["", "## 交付物来源", ""]
    for node in nodes:
        manifest = _manifest(root, node)
        if not manifest or not manifest.get("deliverables"):
            continue
        lines += [f"### {node['path']} `{manifest['version']}`", "", f"来源批次：`{manifest['artifact']}`", ""]
        lines += ["| 文件 | 行数 | sha256 |", "| --- | ---: | --- |"]
        for item in manifest["deliverables"]:
            rows = item.get("rows")
            lines.append(f"| `{item['file']}` | {'—' if rows is None else rows} | `{item['sha256'][:12]}` |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_status(root: Path = ROOT) -> Path:
    path = root / STATUS_NAME
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(render_status(root), encoding="utf-8", newline="\n")
    temporary.replace(path)
    return path


def check_status(root: Path = ROOT) -> list[str]:
    path = root / STATUS_NAME
    if not path.is_file():
        return [f"缺少 {STATUS_NAME}；请运行 python scripts/publish_release.py 生成"]
    if path.read_text(encoding="utf-8").replace("\r\n", "\n") != render_status(root):
        return [f"{STATUS_NAME} 与当前发布状态不一致（被手工/临时修改，或发布后未更新）；只能通过 python scripts/publish_release.py 更新"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="只校验，不写入")
    args = parser.parse_args(argv)
    if args.check:
        errors = check_status()
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0
    parser.error("状态文件只由 scripts/publish_release.py 写入；此处仅支持 --check")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
