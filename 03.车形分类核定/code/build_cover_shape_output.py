"""按代表年份构建全记录 SHAPE 稳定交付物；正式生成不默认联网。"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch
from cover_shape_contract import SHAPE_FIELDS, SHAPE_LABELS, SHAPE_STATUSES
from cover_shape.cli import csv_write, jsonl_write
from cover_shape.evidence import load_evidence
from cover_shape.ingest import digest, read_table
from cover_shape.representatives import build, representative_groups
from cover_shape.family_cache import FamilyCache, read_cache
from cover_shape.research_queue import open_tasks, read_queue, refresh_queue


def load_inputs(batch):
    source_path = ROOT / "02.分类结构审核/output/车型结构.csv"
    legacy_path = PROJECT / "output/车形分类.csv"
    data = PROJECT / "data/cover_shape"
    batch.input(source_path)
    batch.input(legacy_path)
    _, source = read_table(source_path)
    _, legacy = read_table(legacy_path)
    _, reference = read_table(PROJECT / "data/参考尺寸计算.csv")
    def rule(name): return yaml.safe_load((data / name).read_text(encoding="utf-8"))
    return {"source": source, "legacy": legacy, "reference": reference, "policy": rule("full_table.yaml"),
            "evidence": load_evidence(data / "evidence.jsonl"), "mapping": rule("column_map.yaml"),
            "taxonomy": rule("taxonomy_v1.yaml"), "automatic": rule("automatic.yaml"),
            "queue_policy": rule("research_queue.yaml"), "family_cache": read_cache(data / "family_cache.csv"),
            "source_sha": digest(source_path), "source_path": source_path}


def produce(batch, inputs=None, queue_overrides=None):
        inputs = inputs or load_inputs(batch)
        source, legacy, reference, evidence = (inputs[k] for k in ("source", "legacy", "reference", "evidence"))
        policy, before, source_path = inputs["policy"], inputs["source_sha"], inputs["source_path"]
        groups = representative_groups(source, legacy, inputs["mapping"], policy, before, evidence)
        rows, audit = build(source, legacy, reference, evidence, inputs["mapping"], policy,
                            inputs["taxonomy"], inputs["automatic"], before, groups=groups,
                            cache=FamilyCache(inputs["family_cache"], inputs["queue_policy"]))
        queue_path = PROJECT / "output/shape_research_queue.jsonl"
        previous = read_queue(queue_path)
        if queue_path.is_file():
            batch.input(queue_path)
        overrides = queue_overrides or {}
        previous = [overrides.get(r["family_id"], r) for r in previous]
        queue = refresh_queue(groups, audit, {r["DIMENSION-ID"]: r for r in rows}, previous, inputs["queue_policy"])
        tasks = open_tasks(queue, inputs["queue_policy"])
        jsonl_write(batch.output("shape_research_queue.jsonl"), queue)
        checks = {"exact_source_order_and_coverage": [r["DIMENSION-ID"] for r in rows] == [r["DIMENSION-ID"] for r in source],
                  "unique_ids": len({r["DIMENSION-ID"] for r in rows}) == len(rows),
                  "all_have_class": all(r["SHAPE"] in SHAPE_LABELS - {"UNKNOWN"} for r in rows),
                  "valid_status": all(r["SHAPE_STATUS"] in SHAPE_STATUSES for r in rows),
                  "complete_metadata": all(all(str(r[k]) for k in SHAPE_FIELDS) for r in rows),
                  "source_unchanged": digest(source_path) == before}
        if not all(checks.values()):
            raise ValueError(f"全记录 SHAPE 校验失败：{checks}")
        csv_write(batch.output("COVER_SHAPE.csv"), ["DIMENSION-ID", "COUNTRY", *SHAPE_FIELDS], rows)
        with gzip.open(batch.extra("representative_audit.json"), "wt", encoding="utf-8") as handle:
            json.dump(audit, handle, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        summary = {"rows": len(rows), "representative_groups": len(audit), "rule_version": policy["version"],
                   "shape_counts": dict(Counter(r["SHAPE"] for r in rows)),
                   "status_counts": dict(Counter(r["SHAPE_STATUS"] for r in rows)),
                   "method_counts": dict(Counter(r["SHAPE_METHOD"] for r in rows)),
                   "by_country": dict(Counter(r["COUNTRY"] for r in rows)), "validation": checks,
                   "fit_status": "NOT_TESTED", "network_requests": 0,
                   "research_queue": {"families": len(queue),
                                      "states_by_market": {m: dict(Counter(r["state"] for r in queue if r["market"] == m))
                                                           for m in inputs["queue_policy"]["market_priority"]},
                                      "research_markets": inputs["queue_policy"].get("research_markets", ["US"]),
                                      "open_tasks": len(tasks), "open_sample_years": sum(len(r["suggested_sample_years"]) for r in tasks),
                                      "family_cache_rules": len(inputs["family_cache"]),
                                      "attempted_families": sum(r["attempts"] > 0 for r in queue)},
                   "limitations": "原型几何先验与尺寸补齐是推断；20 条尺寸缺失/无效记录归 OTHER，未补猜尺寸"}
        batch.output("cover_shape_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        batch.extra("REPORT.md", compress=False).write_text(
            "# 全记录代表年 SHAPE\n\n" + json.dumps(summary, ensure_ascii=False, indent=2) +
            "\n\n规则差异：冻结精确分支几何证据优先；其次 family_cache.csv 车型族研究结论（同市场含抽样年的记录 PROBABLE，"
            "同族其余年份/尺寸 INFERRED，EU/RU 按年份重叠复用 US 结论 INFERRED）；其余依据旧几何原型先验与实际尺寸推断。"
            "研究队列按市场/车型/结构分族，每个代际只抽少数年份。"
            "同市场/代际/版本/CAB/BED/尺寸/旧几何原型分组，缺代际时隔离源行；优先源证据年款，否则中位覆盖年。"
            "新 SHAPE 不改变旧车形及尺码计算；原始 YEAR 和尺寸不回写。\n", encoding="utf-8")
        return summary


def main():
    with RunBatch.create(PROJECT / "artifacts", "representative-cover-shape", data_dir=PROJECT / "data") as batch:
        summary = produce(batch)
        batch.finish(summary, publish_to=PROJECT / "output")
        print(json.dumps({"batch": str(batch.directory), **summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
