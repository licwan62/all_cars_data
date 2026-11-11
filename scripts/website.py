"""Final website entry point. Build locally by default; deployment is explicit."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=["build", "publish", "release", "ecs-only"], default="build",
                        help="build=local; publish=validated candidate; release=build+NAS+ECS; ecs-only=retry NAS mirror")
    args = parser.parse_args()
    nodes = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))["nodes"]
    node = next(n for n in nodes if n["id"] == "website-publish")
    project = ROOT / node["path"]
    if args.action in {"build", "release"}:
        subprocess.run([sys.executable, str(ROOT / "scripts/run_nodes.py"), "--nodes", node["id"]], cwd=ROOT, check=True)
    if args.action != "build":
        subprocess.run([sys.executable, str(project / "src/run.py"), "ecs-only" if args.action == "ecs-only" else "publish"],
                       cwd=project, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
