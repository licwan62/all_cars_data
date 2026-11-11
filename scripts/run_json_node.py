"""Execute one node using JSON-only inter-node transport.

Existing computation engines run in an isolated, disposable repository view. Only
declared upstream JSON handoffs are materialized there as legacy engine inputs.
Their output is converted and installed through RunBatch; CSV never crosses nodes.
"""
from __future__ import annotations
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch, sha256
from json_interface import convert, materialize, legacy_name
from node_paths import node_output, node_page
from pipeline_contract import publishable
from rules_snapshot import rules_snapshot


def run_node(root, node_id):
    root = Path(root).resolve()
    payload = json.loads((root / "pipeline.json").read_text(encoding="utf-8"))
    by_id = {n["id"]: n for n in payload["nodes"]}
    node = by_id[node_id]
    if not publishable(node) or not node.get("engine_run"):
        raise ValueError(f"{node_id} 没有可运行的 JSON 节点入口")
    project = root / node["path"]
    with tempfile.TemporaryDirectory(prefix="json-node-") as temporary:
        sandbox = Path(temporary)
        for folder in ("lib", "scripts"):
            shutil.copytree(root / folder, sandbox / folder, ignore=shutil.ignore_patterns("__pycache__"))
        # Legacy engines may inspect the contract. Their private view uses their
        # native filenames; the authoritative repository contract is JSON-only.
        native_payload = json.loads(json.dumps(payload))
        for item in native_payload["nodes"]:
            original = by_id[item["id"]]
            item["outputs"] = [legacy_name(original, name) for name in item.get("outputs", [])]
            item["run"] = item.get("engine_run", [])
            item.pop("output_dir", None)
            item.pop("html_at_root", None)
            for inp in item.get("inputs", []):
                inp["file"] = legacy_name(by_id[inp["node"]], inp["file"])
        (sandbox / "pipeline.json").write_text(json.dumps(native_payload, ensure_ascii=False), encoding="utf-8")
        target = sandbox / node["path"]
        target.mkdir(parents=True)
        # Copy only owned implementation/configuration, never historic artifacts,
        # stale own outputs, caches, or another node's data.
        folders = node.get("code_dir") or []
        if isinstance(folders, str):
            folders = [folders]
        for folder in dict.fromkeys(["data", *folders]):
            if (project / folder).is_dir():
                shutil.copytree(project / folder, target / folder, ignore=shutil.ignore_patterns("__pycache__"))
        for path in project.iterdir():
            if path.is_file():
                shutil.copy2(path, target / path.name)
        with RunBatch.create(project / "artifacts", "json-node", data_dir=project / "data") as batch:
            for upstream_id in node.get("upstream", []):
                upstream = by_id[upstream_id]
                out = sandbox / upstream["path"] / "output"
                out.mkdir(parents=True, exist_ok=True)
                entries = []
                inputs = [i for i in node.get("inputs", []) if i["node"] == upstream_id]
                for inp in inputs:
                    source = node_output(root, upstream) / inp["file"]
                    if not source.is_file() and not inp.get("required", True):
                        continue
                    batch.input(source, f"{upstream_id}/{inp['file']}")
                    dest = out / legacy_name(upstream, inp["file"])
                    materialize(source, dest)
                    entries.append({"file": dest.relative_to(out).as_posix(), "sha256": sha256(dest)})
                # The private compatibility manifest makes engines that enumerate
                # published inputs see only the files this node is allowed to use.
                (out / "manifest.json").write_text(json.dumps({"node": upstream_id, "version": "scratch-json-input", "deliverables": entries}), encoding="utf-8")
            for command in node["engine_run"]:
                parts = shlex.split(command)
                if parts[0] == "python":
                    parts[0] = sys.executable
                subprocess.run(parts, cwd=target, check=True, env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"})
            if rules_snapshot(target) != rules_snapshot(project):
                raise RuntimeError("计算引擎改写了规则；拒绝安装 JSON 接口")
            for name in node["outputs"]:
                source = target / "output" / legacy_name(node, name)
                batch.output(name).write_bytes(convert(source))
            return batch.finish({"status": "passed", "transport": "json", "engine": "isolated-native-adapter"}, publish_to=node_output(root, node))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", required=True)
    args = parser.parse_args()
    run_node(ROOT, args.node)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
