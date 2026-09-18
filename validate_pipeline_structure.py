from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "pipeline.json"
REQUIRED_DIRECTORIES = ("data", "output", "artifacts")


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    nodes = payload.get("nodes", [])
    errors: list[str] = []
    node_ids = {node.get("id") for node in nodes}

    if not nodes or None in node_ids or len(node_ids) != len(nodes):
        errors.append("pipeline.json 的节点 id 为空或重复")

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

    if errors:
        print("流水线结构校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"流水线结构校验通过：{len(nodes)} 个 agent，均具备 data/output/artifacts。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
