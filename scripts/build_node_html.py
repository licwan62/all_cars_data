"""Build versioned standalone HTML results without running or publishing data nodes."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from node_html import build_reports, check_reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", help="Comma-separated node IDs; default: all registered pages")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        nodes = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))["nodes"]
        if args.nodes:
            nodes = [n for n in nodes if n["id"] in args.nodes.split(",")]
        errors = check_reports(ROOT, nodes)
        print("\n".join(errors) if errors else f"HTML 校验通过：{len(nodes)} 个项目")
        return bool(errors)
    build_reports(ROOT, set(args.nodes.split(",")) if args.nodes else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
