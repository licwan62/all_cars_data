import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import trace_pipeline as trace  # noqa: E402


def test_current_repo_traces_clean():
    payload = json.loads((trace.ROOT / "pipeline.json").read_text(encoding="utf-8"))
    by_id = {node["id"]: node for node in payload["nodes"]}
    for node in payload["nodes"]:
        errors, _stale = trace.trace_node(node, by_id)  # 过期只提示，不让测试失败
        assert not errors, errors
