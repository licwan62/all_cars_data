"""向已生成的国别与店铺全量表追加 SHAPE，不更改已有列、顺序、尺码或 TRIM。"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import yaml

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch, published_reference, sha256
from cover_shape_contract import SHAPE_FIELDS, FULL_TABLE_SHAPE_FIELDS, attach_cover_shape


def read(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def register_base(batch, path):
    """已发布原全量表只记引用；刚生成的内部中间表只记哈希，不重复保存。"""
    reference, _ = published_reference(path, sha256(path))
    if reference:
        batch.inputs.append(reference)
    # 正式输入及其引用仍是当前上游 output；内部生成表由节点 run 在沙箱可复现。


def main():
    config = yaml.safe_load((PROJECT / "data/全量SHAPE.yaml").read_text(encoding="utf-8"))
    from shape_adjustment import load_config
    adjustment_enabled = load_config()["enabled"]
    if config["fields"] != FULL_TABLE_SHAPE_FIELDS or config["use_for_size_matching"] != adjustment_enabled:
        raise ValueError("全量 SHAPE 合同不一致")
    source_path = ROOT / "03.车形分类核定" / "output" / config["source_file"]
    with RunBatch.create(PROJECT / "artifacts", "full-table-cover-shape", data_dir=PROJECT / "data") as batch:
        batch.input(source_path)
        shapes = read(source_path)
        # 所有基表都来自本节点正式生成流程；上游真实输入只记 output 版本引用。
        upstream_nodes = ["01.整理尺寸库", "02.分类结构审核", "02.销量评估", "03.车形分类核定"]
        for node in upstream_nodes:
            batch.input_published(ROOT / node / "output", exclude=(source_path,), name_prefix=node, missing_ok=True)
        summaries, base_hashes = {}, {}
        for name in config["full_tables"]:
            country = name.split("/")[0]
            path = PROJECT / "output" / name
            frame = read(path)
            register_base(batch, path)
            base_hashes[name] = sha256(path)
            enriched = attach_cover_shape(frame, shapes, country)
            old = frame.drop(columns=[f for f in SHAPE_FIELDS if f in frame])
            if not enriched[old.columns].equals(old):
                raise ValueError(f"{name} 原有数据发生变化")
            enriched.to_csv(batch.output(name), index=False, encoding="utf-8-sig", lineterminator="\n")
            summaries[name] = {"rows": len(enriched), "shape_counts": dict(Counter(enriched["SHAPE"])),
                               "all_shape_nonblank": bool(enriched["SHAPE"].ne("").all()), "existing_fields_unchanged": True}
        status = {"tables": summaries, "base_table_sha256": base_hashes, "new_fields": FULL_TABLE_SHAPE_FIELDS,
                  "shape_size_adjustment_rule": config["size_adjustment_rule"],
                  "shape_size_adjustment_enabled": adjustment_enabled}
        batch.extra("REPORT.md", compress=False).write_text("# 全量表 SHAPE 回填\n\n" + json.dumps(status, ensure_ascii=False, indent=2) +
            "\n\n规则差异：全量SHAPE.yaml 仅插入 SHAPE；状态/代表年/方法/备选/来源由 03 节点维护。"
            f"本回填步骤保持全表行序、原列值和TRIM不变；US独立SHAPE调整规则启用状态：{adjustment_enabled}，EU/RU未启用。\n", encoding="utf-8")
        batch.finish(status, publish_to=PROJECT / "output")
        print(json.dumps({"batch": str(batch.directory), **status}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
