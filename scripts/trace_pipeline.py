#!/usr/bin/env python3
"""追踪各节点当前 output/ 的来源和输入是否一致、是否过期。

对每个节点读取 output/manifest.json（当前输出的输入输出点信息）并检查：
1. 每个交付物：output/<名称> 的 sha256 == 来源 artifact 文件 <名称>-<存储版本> 的 sha256 == 记录值；
   未变化的交付物引用最早保存这份字节的批次，存储版本可早于 manifest 版本。上游记录引用的 artifact 文件必须存在。
2. 每个上游输入：manifest 记录的 sha256 == 上游当前 output/ 文件的 sha256；不一致即本节点已过期，需要重跑。
3. 上游节点当前版本与 manifest 记录的输入版本对比（仅提示）。
4. 本节点 data/ 规则：与 manifest 的 ``rules`` 快照比对；规则已改而输出未重新发布即过期。
   旧 manifest 没有 ``rules`` 时显示“未记录”，下次发布后生效。

按需节点（``pipeline.json`` 的 ``line_triggers`` 为 on_demand，如 B/C/D/E/X 线）不随上游刷新：上游变化只记为
“按需待刷新”（ON-DEMAND）提示，不算过期；其自身规则变化仍算过期。

打印追踪表；存在不一致或过期节点时返回 1。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))  # 共享模块 rules_snapshot 在 lib/

from artifact_refs import check_deliverable_source, sha256
from pipeline_status import is_on_demand
from rules_snapshot import describe_changes, rules_changes, rules_snapshot  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def load_manifest(node: dict) -> dict | None:
    path = ROOT / node["path"] / "output" / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def trace_node(node: dict, by_id: dict[str, dict], on_demand: bool = False) -> tuple[list[str], list[str], list[str]]:
    """返回 (错误, 过期提示, 按需待刷新提示)。on_demand 节点的上游变化归入第三项。"""
    errors: list[str] = []
    stale: list[str] = []
    deferred: list[str] = []
    manifest = load_manifest(node)
    if manifest is None:
        return [f"{node['path']}: 缺少 output/manifest.json"], stale, deferred
    for item in manifest.get("deliverables", []):
        name = item["file"]
        if not item.get("artifact_file"):
            errors.append(f"{node['path']}: {name} 缺少 artifact_file 来源")
            continue
        problem = check_deliverable_source(ROOT, manifest, item)
        published = ROOT / node["path"] / "output" / name
        if problem:
            errors.append(f"{node['path']}: {problem}")
        elif not published.is_file():
            errors.append(f"{node['path']}: output/{name} 不存在")
        elif not sha256(ROOT / item["artifact_file"]) == sha256(published) == item["sha256"]:
            errors.append(f"{node['path']}: output/{name} 与来源 artifact 或记录的 sha256 不一致")
    for upstream in manifest.get("upstream", []):
        missing = [f["artifact_file"] for f in upstream.get("files", []) if f.get("artifact_file") and not (ROOT / f["artifact_file"]).is_file()]
        if missing:
            errors.append(f"{node['path']}: 引用的上游 artifact 不存在（被移走或改名）：{', '.join(missing)}")
        up_node = by_id[upstream["node"]]
        up_manifest = load_manifest(up_node)
        current = {item["file"]: item["sha256"] for item in (up_manifest or {}).get("deliverables", [])}
        changed = [f["file"] for f in upstream.get("files", []) if current.get(f["file"]) != f["sha256"]]
        if changed:
            (deferred if on_demand else stale).append(
                f"{node['path']}: 上游 {up_node['path']} 已变化（记录 {upstream.get('version')}，"
                f"当前 {(up_manifest or {}).get('version')}）：{', '.join(changed)}"
            )
    if "rules" in manifest:
        changed = describe_changes(rules_changes(manifest["rules"], rules_snapshot(ROOT / node["path"])))
        if changed:
            stale.append(f"{node['path']}: 本节点规则在 {manifest['version']} 发布后已变化：{changed}")
    return errors, stale, deferred


def rules_state(manifest: dict) -> str:
    return "已记录" if "rules" in manifest else "未记录"


def main() -> int:
    payload = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))
    by_id = {node["id"]: node for node in payload["nodes"]}
    failed = False
    print(f"{'节点':<22}{'版本':<14}{'交付物':>4}  {'上游输入':>6}  {'规则快照':<6}状态")
    for node in payload["nodes"]:
        errors, stale, deferred = trace_node(node, by_id, is_on_demand(payload, node))
        manifest = load_manifest(node) or {}
        state = "ERROR" if errors else "STALE" if stale else "ON-DEMAND" if deferred else "OK"
        print(f"{node['path']:<22}{manifest.get('version', '-'):<14}{len(manifest.get('deliverables', [])):>4}  {len(manifest.get('upstream', [])):>6}  {rules_state(manifest):<8}{state}")
        for line in [*errors, *stale]:
            print(f"    - {line}")
        for line in deferred:
            print(f"    · 按需待刷新 {line}")
        failed = failed or bool(errors or stale)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
