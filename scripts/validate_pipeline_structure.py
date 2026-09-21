from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "pipeline.json"
REQUIRED_DIRECTORIES = ("data", "output", "artifacts")


def check_layers(nodes: list[dict]) -> list[str]:
    """layer = 最长上游链长度；目录前缀 NN. 必须等于 layer；上游必须在更低层。"""
    errors: list[str] = []
    by_id = {node["id"]: node for node in nodes}
    depth: dict[str, int] = {}

    def resolve(node_id: str, trail: tuple[str, ...]) -> int:
        if node_id in trail:
            raise ValueError(" -> ".join((*trail, node_id)))
        if node_id not in depth:
            ups = [resolve(up, (*trail, node_id)) for up in by_id[node_id].get("upstream", []) if up in by_id]
            depth[node_id] = max(ups, default=-1) + 1
        return depth[node_id]

    try:
        for node_id in by_id:
            resolve(node_id, ())
    except ValueError as cycle:
        return [f"依赖存在环: {cycle}"]

    for node in nodes:
        node_id, layer = node["id"], node.get("layer")
        if layer != depth[node_id]:
            errors.append(f"{node_id}: layer={layer}，按上游计算应为 {depth[node_id]}")
        prefix = node["path"].split(".", 1)[0]
        line = node.get("line", "U")
        if line == "U":
            if not (prefix.isdigit() and len(prefix) == 2 and int(prefix) == depth[node_id]):
                errors.append(f"{node_id}: 目录 {node['path']} 的序号前缀应为 {depth[node_id]:02d}.")
            continue
        index = node.get("index")
        if prefix != f"{line}{index}":
            errors.append(f"{node_id}: 目录 {node['path']} 的前缀应为 {line}{index}.")
        for up in node.get("upstream", []):
            up_node = by_id.get(up)
            if up_node and up_node.get("line") == line and not up_node.get("index", 0) < index:
                errors.append(f"{node_id}: 线内序号 {index} 必须大于上游 {up} 的序号")
        if index == 0 and any(by_id[u].get("line") == line for u in node.get("upstream", []) if u in by_id):
            errors.append(f"{node_id}: 枢纽节点 {line}0 不应依赖同线节点")
    hubs = [node for node in nodes if node.get("line", "U") != "U" and node.get("index") == 0]
    numeric_depth = max((depth[n["id"]] for n in nodes if n.get("line", "U") == "U"), default=-1)
    for hub in hubs:
        if depth[hub["id"]] <= numeric_depth:
            errors.append(f"{hub['id']}: 枢纽必须位于所有数字层节点之后")
    return errors


def check_outputs(nodes: list[dict]) -> list[str]:
    """outputs 只列已存在的稳定交付物；未产出的必须写入 pending。"""
    return [
        f"{node['id']}: {node['path']}/output/{name} 不存在（未产出的请移到 pending）"
        for node in nodes
        for name in node.get("outputs", [])
        if not (ROOT / node["path"] / "output" / name).is_file()
    ]


VERSION_SUFFIX = re.compile(r"-\d{8}_\d{2}(?=\.[^.]+$)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_release_naming(nodes: list[dict]) -> list[str]:
    """artifact 内文件带 -YYYYMMDD_NN 后缀；output/ 使用去后缀的稳定文件名，内容与 artifact 一致。"""
    errors: list[str] = []
    for node in nodes:
        base = ROOT / node["path"]
        manifest_path = base / "output" / "manifest.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        version = manifest.get("version", "")
        artifact_dir = ROOT / manifest.get("artifact", "")
        for item in manifest.get("deliverables", []):
            name, versioned = item["file"], item.get("versioned_file", "")
            stem, dot, ext = name.rpartition(".")
            if versioned != f"{stem}-{version}{dot}{ext}":
                errors.append(f"{node['id']}: {name} 的 versioned_file 应为 {stem}-{version}{dot}{ext}，实际 {versioned}")
                continue
            out_file = base / "output" / name
            art_file = artifact_dir / "output" / versioned
            if not art_file.is_file():
                errors.append(f"{node['id']}: 来源 artifact 缺少 {art_file.relative_to(ROOT)}")
            elif out_file.is_file() and sha256(out_file) != sha256(art_file):
                errors.append(f"{node['id']}: output/{name} 与 {versioned} 内容不一致")
        for path in (base / "output").glob("*"):
            if VERSION_SUFFIX.search(path.name):
                errors.append(f"{node['id']}: output/ 不得带 artifact 后缀: {path.name}")
    return errors


def check_final_products(products: list[dict], nodes: list[dict]) -> list[str]:
    errors: list[str] = []
    paths = {node["id"]: node["path"] for node in nodes}
    for product in products:
        node_id = product.get("node")
        if node_id not in paths:
            errors.append(f"最终产物 {product.get('name')}: 未知节点 {node_id}")
            continue
        for name in product.get("files", []):
            if not (ROOT / paths[node_id] / "output" / name).is_file():
                errors.append(f"最终产物 {product['name']}: {paths[node_id]}/output/{name} 不存在")
    return errors


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    nodes = payload.get("nodes", [])
    errors: list[str] = []
    node_ids = {node.get("id") for node in nodes}

    if not nodes or None in node_ids or len(node_ids) != len(nodes):
        errors.append("pipeline.json 的节点 id 为空或重复")

    governance = payload.get("governance", {})
    owner_id = governance.get("manifest_owner")
    owner_path = governance.get("manifest_owner_path")
    if owner_id != "link-analysis" or owner_path != "D2.链接分析":
        errors.append("pipeline.json 必须登记由最后节点 D2.链接分析（link-analysis）维护")

    for node in nodes:
        node_id = node["id"]
        project = (ROOT / node["path"]).resolve()
        try:
            project.relative_to(ROOT)
        except ValueError:
            errors.append(f"{node_id}: path 越出仓库")
            continue
        if not project.is_dir():
            errors.append(f"{node_id}: 项目目录不存在: {node['path']}")
            continue
        if not (project / "AGENTS.md").is_file():
            errors.append(f"{node_id}: 缺少 AGENTS.md")
        for directory in REQUIRED_DIRECTORIES:
            if not (project / directory).is_dir():
                errors.append(f"{node_id}: 缺少 {directory}/")
        for upstream in node.get("upstream", []):
            if upstream not in node_ids:
                errors.append(f"{node_id}: 未知上游 {upstream}")
            if upstream == node_id:
                errors.append(f"{node_id}: 不得依赖自身")

    errors.extend(check_layers(nodes))
    errors.extend(check_outputs(nodes))
    errors.extend(check_release_naming(nodes))
    errors.extend(check_final_products(payload.get("final_products", []), nodes))

    if errors:
        print("流水线结构校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"流水线结构校验通过：{len(nodes)} 个 agent，均具备 data/output/artifacts。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
