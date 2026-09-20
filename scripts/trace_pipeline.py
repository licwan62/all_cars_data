#!/usr/bin/env python3
"""追踪各节点当前 output/ 的来源和输入是否一致、是否过期。

对每个节点读取 output/manifest.json（当前输出的输入输出点信息）并检查：
1. 每个交付物：output/<名称> 的 sha256 == 来源 artifact 里 <名称>-<版本> 文件的 sha256，
   且文件名主干一致（只差版本后缀）。
2. 每个上游输入：manifest 记录的 sha256 == 上游当前 output/ 文件的 sha256；不一致即本节点已过期，需要重跑。
3. 上游节点当前版本与 manifest 记录的输入版本对比（仅提示）。

打印追踪表；存在不一致或过期节点时返回 1。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest(node: dict) -> dict | None:
    path = ROOT / node["path"] / "output" / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def trace_node(node: dict, by_id: dict[str, dict]) -> tuple[list[str], list[str]]:
    """返回 (错误, 过期提示)。"""
    errors: list[str] = []
    stale: list[str] = []
    manifest = load_manifest(node)
    if manifest is None:
        return [f"{node['path']}: 缺少 output/manifest.json"], stale
    for item in manifest.get("deliverables", []):
        name = item["file"]
        artifact_file = ROOT / item.get("artifact_file", "")
        if not item.get("artifact_file"):
            errors.append(f"{node['path']}: {name} 缺少 artifact_file 来源")
            continue
        stem, _, ext = name.rpartition(".")
        if artifact_file.name != f"{stem}-{manifest['version']}.{ext}":
            errors.append(f"{node['path']}: {name} 的来源文件名 {artifact_file.name} 与版本 {manifest['version']} 不一致")
        elif not artifact_file.is_file():
            errors.append(f"{node['path']}: 来源 {item['artifact_file']} 不存在")
        elif not (ROOT / node["path"] / "output" / name).is_file():
            errors.append(f"{node['path']}: output/{name} 不存在")
        elif sha256(artifact_file) != sha256(ROOT / node["path"] / "output" / name):
            errors.append(f"{node['path']}: output/{name} 与来源 artifact 内容不一致")
    for upstream in manifest.get("upstream", []):
        up_node = by_id[upstream["node"]]
        up_manifest = load_manifest(up_node)
        current = {item["file"]: item["sha256"] for item in (up_manifest or {}).get("deliverables", [])}
        changed = [f["file"] for f in upstream.get("files", []) if current.get(f["file"]) != f["sha256"]]
        if changed:
            stale.append(
                f"{node['path']}: 上游 {up_node['path']} 已变化（记录 {upstream.get('version')}，"
                f"当前 {(up_manifest or {}).get('version')}）：{', '.join(changed)}"
            )
    return errors, stale


def main() -> int:
    payload = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))
    by_id = {node["id"]: node for node in payload["nodes"]}
    failed = False
    print(f"{'节点':<22}{'版本':<14}{'交付物':>4}  {'上游输入':>6}  状态")
    for node in payload["nodes"]:
        errors, stale = trace_node(node, by_id)
        manifest = load_manifest(node) or {}
        state = "OK" if not (errors or stale) else ("ERROR" if errors else "STALE")
        print(f"{node['path']:<22}{manifest.get('version', '-'):<14}{len(manifest.get('deliverables', [])):>4}  {len(manifest.get('upstream', [])):>6}  {state}")
        for line in [*errors, *stale]:
            print(f"    - {line}")
        failed = failed or bool(errors or stale)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
