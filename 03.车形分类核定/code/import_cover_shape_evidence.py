"""显式导入一次已冻结的自动文档证据到 data/ 必要参考资料；不默认读取日期 artifact。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from cover_shape.cli import PROJECT, RunBatch, frozen_input
from cover_shape.evidence import load_evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    facts = [e for e in load_evidence(args.evidence.resolve()) if e["evidence_type"] == "automatic_description"]
    if not facts:
        raise ValueError("未找到自动文档几何证据")
    with RunBatch.create(PROJECT / "artifacts", "cover-shape-reference-import", data_dir=PROJECT / "data") as batch:
        frozen_input(batch, args.evidence.resolve())
        target = PROJECT / "data/cover_shape/evidence.jsonl"
        target.write_text("".join(json.dumps(e, ensure_ascii=False, sort_keys=True)+"\n" for e in facts), encoding="utf-8")
        batch.extra("REPORT.md", compress=False).write_text(
            f"# 几何证据参考导入\n\n从显式冻结输入选取 {len(facts)} 条自动文档几何证据。"
            "保持源 URL、哈希、源年款、身份和推断链，作为本节点 data/ 必要参考，不导入搜索失败/不合格图片。\n", encoding="utf-8")
        batch.finish({"facts": len(facts), "purpose": "representative full-table SHAPE"})
        print(json.dumps({"batch": str(batch.directory), "facts": len(facts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
