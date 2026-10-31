"""Run explicitly selected registered nodes in topological order, then publish locally.

No network crawling or public NAS publication. Restore a node's stable output on failure.
"""
import argparse
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from pipeline_contract import publishable
from rules_snapshot import rules_snapshot
from publish_release import topological_order, release_all


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", required=True)
    args = parser.parse_args()
    selected = set(args.nodes.split(","))
    nodes = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))["nodes"]
    if selected - {n["id"] for n in nodes}:
        parser.error("未知节点")
    for node in topological_order(nodes):
        if node["id"] not in selected:
            continue
        if not publishable(node) or not node.get("run"):
            parser.error(f"{node['id']} 不具备生产运行入口")
        project = ROOT / node["path"]
        before = rules_snapshot(project)
        with tempfile.TemporaryDirectory(prefix="node-output-backup-") as temp:
            output = project / "output"
            existed = output.exists()
            if existed:
                shutil.copytree(output, Path(temp) / "output")
            try:
                for command in node["run"]:
                    parts = shlex.split(command)
                    if parts[0] == "python":
                        parts[0] = sys.executable
                    print(f"[{node['id']}] {command}", flush=True)
                    subprocess.run(parts, cwd=project, check=True)
                if rules_snapshot(project) != before:
                    raise RuntimeError(f"{node['id']} 在运行中改写data，拒绝发布")
                release_all(ROOT, only={node["id"]})
            except BaseException:
                # Verified absolute path must remain inside this node.
                output.resolve().relative_to(project.resolve())
                if output.exists():
                    shutil.rmtree(output)
                if existed:
                    shutil.copytree(Path(temp) / "output", output)
                raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
