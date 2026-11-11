#!/usr/bin/env python3
"""生成根目录的流水线 Markdown 状态与 HTML 快照。

内容完全由 ``pipeline.json``、集中 ``json/<节点ID>/manifest.json`` 与 ``json/_meta/release.json`` 推导，
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
from collections import Counter, defaultdict
from functools import cache
from html import escape
from pathlib import Path
from string import Template
from tempfile import NamedTemporaryFile
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))  # 共享模块在 lib/

from pipeline_contract import lifecycle_state
from json_interface import manifest_hashes
from node_paths import repository_metadata, node_output, node_page, load_record, node_dir_name  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STATUS_NAME = "流水线状态.md"
HTML_NAME = "流水线状态.html"
HTML_TEMPLATE = Path(__file__).with_suffix(".html")
LINE_NAMES = {"U": "上游", "A": "A 全量表", "B": "B 定制评分", "C": "C 代表车型", "D": "D 发货单", "E": "E 尺寸分析", "F": "F 定制分析", "X": "X 旁路", "M": "M 车型年覆盖"}
TRIGGERS = {"auto": "自动", "on_demand": "按需"}
ON_DEMAND_STATE = "按需待刷新"
STATE_ORDER = ("最新", "过期", ON_DEMAND_STATE, "待产出", "未发布", "业务容器", "待接入", "历史保留")


def node_trigger(payload: dict, node: dict) -> str:
    """节点触发方式：节点 trigger 字段优先，否则取 pipeline.json line_triggers 中所在线的设置，缺省 auto。"""
    return node.get("trigger") or payload.get("line_triggers", {}).get(node.get("line", "U"), "auto")


def is_on_demand(payload: dict, node: dict) -> bool:
    """按需节点不随默认发布刷新；上游更新只标为“按需待刷新”，不算过期。"""
    return node_trigger(payload, node) == "on_demand"


def _load_json(path: Path, root: Path = ROOT) -> dict | None:
    return load_record(path, root) if path.is_file() else None


def _manifest(root: Path, node: dict) -> dict | None:
    return _load_json(node_output(root, node) / "manifest.json", root)


def _name(path: str) -> str:
    """展示用节点目录名（不含 nodes/ 前缀）。"""
    return node_dir_name(path)


def node_state(node: dict, by_id: dict[str, dict], manifests: dict, on_demand: bool = False) -> tuple[str, list[str]]:
    """返回 (状态, 说明)。状态：最新 / 过期 / 按需待刷新 / 待产出 / 未发布。

    ``on_demand`` 节点的上游更新只说明“需要时可刷新”，状态为 按需待刷新 而不是 过期。
    """
    if state := lifecycle_state(node):
        return state, node.get("blockers", [])
    manifest = manifests[node["id"]]
    if manifest is None:
        return "未发布", ["缺少数据 manifest.json"]
    notes: list[str] = []
    recorded = {item["node"]: item for item in manifest.get("upstream", [])}
    for upstream_id in node.get("upstream", []):
        upstream = by_id[upstream_id]
        current = manifests[upstream_id] or {}
        current_sha = manifest_hashes(current)
        used = recorded.get(upstream_id)
        if used is None:
            notes.append(f"未记录上游 {_name(upstream['path'])} 的输入版本")
            continue
        changed = [item["file"] for item in used.get("files", []) if current_sha.get(item["file"]) != item["sha256"]]
        if changed:
            notes.append(
                f"上游 {_name(upstream['path'])} 已更新（使用 {used.get('version')}，当前 {current.get('version')}）：{'、'.join(changed)}"
            )
    if notes:
        return (ON_DEMAND_STATE if on_demand else "过期"), notes
    if not manifest.get("deliverables") and node.get("pending"):
        return "待产出", []
    return "最新", []


def _load_snapshot(root: Path) -> tuple[dict, dict, dict, dict]:
    payload = json.loads((root / "pipeline.json").read_text(encoding="utf-8"))
    by_id = {node["id"]: node for node in payload["nodes"]}
    release = _load_json(repository_metadata(root, "release.json"), root) or {}
    manifests = {node_id: _manifest(root, node) for node_id, node in by_id.items()}
    states = {
        node_id: node_state(node, by_id, manifests, is_on_demand(payload, node))
        for node_id, node in by_id.items()
    }
    return payload, release, manifests, states


def render_status(root: Path = ROOT) -> str:
    return _render_markdown(*_load_snapshot(root))


def _render_markdown(payload: dict, release: dict, manifests: dict, states: dict) -> str:
    nodes = payload["nodes"]
    by_id = {node["id"]: node for node in nodes}
    counts = Counter(state for state, _ in states.values())
    lines = [
        "# 流水线状态",
        "",
        "> 本文件由 `python scripts/publish_release.py` 在每次发布后自动生成，请勿手工或在临时工作中修改；",
        "> `python scripts/validate_pipeline_structure.py` 会校验它与集中 `json/<节点ID>/manifest.json` 一致。",
        "",
        "[打开 HTML 快照，查看节点依赖图](流水线状态.html)",
        "",
        f"- 最近发布：`{release.get('released_at', '-')}`",
        f"- 节点：{len(nodes)} 个；" + "，".join(f"{state} {counts[state]}" for state in STATE_ORDER if counts[state]),
        "",
        "## 节点",
        "",
        "| 节点 | 产线 | 触发 | 版本 | 交付物 | 上游 | 待产出 | 状态 |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for node in nodes:
        manifest = manifests[node["id"]] or {}
        upstream = "、".join(_name(by_id[up]["path"]) for up in node.get("upstream", [])) or "—"
        pending = "、".join(node.get("pending", [])) or "—"
        state, _ = states[node["id"]]
        lines.append(
            f"| {_name(node['path'])} | {LINE_NAMES.get(node.get('line', 'U'), node.get('line', ''))} | "
            f"{TRIGGERS.get(node_trigger(payload, node), node_trigger(payload, node))} | `{manifest.get('version', '-')}` | {len(manifest.get('deliverables', []))} | {upstream} | {pending} | {state} |"
        )

    problems = [(node, notes) for node in nodes for state, notes in [states[node["id"]]] if notes and state != ON_DEMAND_STATE]
    lines += ["", "## 需要处理", ""]
    if problems:
        for node, notes in problems:
            lines.extend(f"- {_name(node['path'])}：{note}" for note in notes)
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
            lines.extend(f"- {_name(node['path'])}（`{node['id']}`）：{note}" for note in notes)

    lines += ["", "## 最终产物", "", "| 产物 | 节点 | 文件 | 待产出 |", "| --- | --- | --- | --- |"]
    for product in payload.get("final_products", []):
        node = by_id.get(product.get("node"), {})
        files = "、".join(f"`{name}`" for name in product.get("files", [])) or "—"
        pending = "、".join(product.get("pending", [])) or "—"
        lines.append(f"| {product['name']} | {_name(node.get('path', product.get('node')))} | {files} | {pending} |")

    lines += ["", "## 交付物来源", ""]
    for node in nodes:
        manifest = manifests[node["id"]]
        if not manifest or not manifest.get("deliverables"):
            continue
        lines += [f"### {_name(node['path'])} `{manifest['version']}`", "", f"来源批次：`{_name(manifest['artifact'])}`", ""]
        lines += ["| 文件 | 行数 | sha256 |", "| --- | ---: | --- |"]
        for item in manifest["deliverables"]:
            rows = item.get("rows")
            lines.append(f"| `{item['file']}` | {'—' if rows is None else rows} | `{item['sha256'][:12]}` |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _node_href(node_id: str) -> str:
    return "#node-" + quote(node_id, safe="")


def _render_graph(nodes: dict, states: dict) -> str:
    @cache
    def layer(node_id: str) -> int:
        node = nodes[node_id]
        if "layer" in node:
            return node["layer"]
        return 1 + max((layer(upstream) for upstream in node.get("upstream", [])), default=-1)

    columns = defaultdict(list)
    for node_id, node in nodes.items():
        if node.get("kind") != "container":
            columns[layer(node_id)].append(node_id)
    if not columns:
        return "<p>暂无数据节点。</p>"

    card_width, card_height, column_step, row_step = 176, 48, 213, 64
    row_count = max(map(len, columns.values()))
    width = max(columns) * column_step + card_width + 24
    height = 48 + row_count * row_step
    positions, labels = {}, []
    gaps = {}
    for depth, ids in sorted(columns.items()):
        x = 12 + depth * column_step
        top = 38 + (row_count - len(ids)) * row_step // 2
        labels.append(f'<text class="layer" x="{x}" y="23">第 {depth} 层</text>')
        gaps[depth] = [top - 8 + row * row_step for row in range(len(ids) + 1)]
        for row, node_id in enumerate(ids):
            positions[node_id] = x, top + row * row_step

    def curve(start_x: int, start_y: int, end_x: int, end_y: int) -> str:
        bend = min(54, (end_x - start_x) // 2)
        return f"C {start_x + bend} {start_y}, {end_x - bend} {end_y}, {end_x} {end_y}"

    edges, cards = [], []
    for node_id, (x, y) in positions.items():
        node = nodes[node_id]
        state = states[node_id][0]
        for upstream in node.get("upstream", []):
            if upstream not in positions:
                continue
            left, top = positions[upstream]
            start_x, start_y = left + card_width, top + card_height // 2
            end_y = y + card_height // 2
            path = [f"M {start_x} {start_y}"]
            # Route edges that span layers through gaps between intervening cards.
            for depth in range(layer(upstream) + 1, layer(node_id)):
                if depth not in gaps:
                    continue
                lane_x = 12 + depth * column_step
                target_y = start_y + (end_y - start_y) * (lane_x - start_x) / (x - start_x)
                lane_y = min(gaps[depth], key=lambda gap: abs(gap - target_y))
                path.append(curve(start_x, start_y, lane_x - 4, lane_y))
                start_x, start_y = lane_x + card_width + 4, lane_y
                path.append(f"H {start_x}")
            path.append(curve(start_x, start_y, x - 3, end_y))
            edges.append(
                f'<path class="edge" data-from="{escape(upstream)}" data-to="{escape(node_id)}" '
                f'd="{" ".join(path)}"/>'
            )
        name = _name(node["path"]).replace("/nodes/", " · ")
        cards.append(
            f'<a href="{_node_href(node_id)}" data-node="{escape(node_id)}" data-state="{state}" '
            f'aria-label="{escape(name)}，{state}" transform="translate({x} {y})">'
            f'<rect width="{card_width}" height="{card_height}" rx="8"/>'
            f'<text x="10" y="19">{escape(name)}</text>'
            f'<text class="card-state" x="10" y="36">{state}</text></a>'
        )
    return "\n".join([
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'style="--graph-min-width: {width * 4 // 5}px" aria-label="节点数据依赖图">',
        '<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" '
        'orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="context-stroke"/></marker></defs>',
        *labels, *edges, *cards, "</svg>",
    ])


def _render_html(payload: dict, release: dict, manifests: dict, states: dict) -> str:
    nodes = {node["id"]: node for node in payload["nodes"]}
    downstream = defaultdict(list)
    children = defaultdict(list)
    for node_id, node in nodes.items():
        for upstream in node.get("upstream", []):
            downstream[upstream].append(node_id)
        if parent := node.get("parent"):
            children[parent].append(node_id)

    def links(ids: list[str]) -> str:
        return "、".join(
            f'<a href="{_node_href(node_id)}">{escape(_name(nodes[node_id]["path"]))}</a>'
            for node_id in ids
        ) or "—"

    cards = []
    for node_id, node in nodes.items():
        manifest = manifests[node_id] or {}
        state, notes = states[node_id]
        line = node.get("line", "U")
        trigger = node_trigger(payload, node)
        fields = {
            "产线": escape(LINE_NAMES.get(line, line)),
            "触发": "—" if node.get("kind") == "container" else escape(TRIGGERS.get(trigger, trigger)),
            "版本": escape(manifest.get("version", "—")),
            "交付物": str(len(manifest.get("deliverables", []))),
            "上游": links(node.get("upstream", [])),
            "下游": links(downstream[node_id]),
        }
        if node.get("html_output"):
            href = quote(node_page(Path("."), node).as_posix(), safe="/")
            fields["最终结果"] = f'<a href="{href}">打开 HTML · 支持 CSV 导出</a>'
        if parent := node.get("parent"):
            fields["所属容器"] = links([parent])
        if children[node_id]:
            fields["子节点"] = links(children[node_id])
        if pending := node.get("pending"):
            fields["待产出"] = escape("、".join(pending))

        details = "".join(f"<div><dt>{key}</dt><dd>{value}</dd></div>" for key, value in fields.items())
        note_list = "<ul>" + "".join(f"<li>{escape(note)}</li>" for note in notes) + "</ul>" if notes else ""
        cards.append(
            f'<article id="node-{escape(node_id)}"><div class="node-title">'
            f'<h3>{escape(_name(node["path"]))}</h3><span class="badge" data-state="{state}">{state}</span>'
            f'</div><code>{escape(node_id)}</code><dl>{details}</dl>{note_list}</article>'
        )
    counts = Counter(state for state, _ in states.values())
    return Template(HTML_TEMPLATE.read_text(encoding="utf-8")).substitute(
        released_at=escape(release.get("released_at", "—")),
        node_count=len(nodes),
        summary="\n".join(
            f'<li data-state="{state}">{state} <b>{counts[state]}</b></li>'
            for state in STATE_ORDER if counts[state]
        ),
        graph=_render_graph(nodes, states),
        cards="\n".join(cards),
    )


def _snapshots(root: Path) -> dict[str, str]:
    snapshot = _load_snapshot(root)
    return {STATUS_NAME: _render_markdown(*snapshot), HTML_NAME: _render_html(*snapshot)}


def write_status(root: Path = ROOT) -> None:
    for name, content in _snapshots(root).items():
        path = root / name
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        with NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=root, delete=False) as handle:
            temporary = Path(handle.name)
            try:
                handle.write(content)
                handle.close()
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)


def check_status(root: Path = ROOT) -> list[str]:
    errors = []
    for name, content in _snapshots(root).items():
        path = root / name
        if not path.is_file():
            errors.append(f"缺少 {name}；请运行 python scripts/publish_release.py --status-only 生成")
        elif path.read_text(encoding="utf-8") != content:
            errors.append(f"{name} 与当前发布状态不一致；请运行 python scripts/publish_release.py --status-only 更新")
    return errors


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
