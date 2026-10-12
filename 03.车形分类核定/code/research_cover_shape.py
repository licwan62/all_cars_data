"""消费车型族研究队列，显式限量联网；每族只研究未覆盖代际的抽样年份，合格结论写入车型族缓存。"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter

import yaml

from build_cover_shape_output import PROJECT, RunBatch, load_inputs, produce
from cover_shape.automatic import AutomaticCollector
from cover_shape.classifier import classify
from cover_shape.cli import jsonl_write, register_cached_resource, utc_now
from cover_shape.family_cache import CACHE_FIELDS, RULE_IDENTITY, family_id, write_cache
from cover_shape.fetchers import HttpClient, cvs_evidence
from cover_shape.ingest import digest, identity
from cover_shape.representatives import representative_groups
from cover_shape.research_queue import open_tasks, read_queue, record_attempt, select_tasks


def sample_targets(task, groups, policy):
    """每个未覆盖代际取一个抽样年份，选覆盖该年份且成员最多的尺寸分支作为研究对象。"""
    targets = []
    pending = {g["generation"]: g for g in task["generations"] if g["covered"] < g["records"]}
    for generation in task["research_generations"][: policy.get("max_generations_per_auto_task", 2)]:
        samples = pending[generation]["sample_years"]
        year = samples[(len(samples) - 1) // 2]
        candidates = [(len(members), gid, record) for gid, record, members, _ in groups
                      if family_id(record) == task["family_id"] and record.get("generation", "") == generation
                      and any(year in m["covered_years"] for m in members)]
        if not candidates:
            continue
        _, gid, record = max(candidates, key=lambda c: (c[0], c[1]))
        target = {**record, "model_year": year}
        target["variant_key"] = identity(target)
        targets.append((generation, gid, target))
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["online"], required=True)
    parser.add_argument("--limit", type=int, default=8, help="本批研究的车型族数")
    parser.add_argument("--max-requests", type=int, default=120)
    parser.add_argument("--market", choices=["US", "EU", "RU"], nargs="+", help="默认按研究规则只推进 US")
    parser.add_argument("--plan-only", action="store_true", help="只读查看本批车型族及抽样年份，不联网或新建批次")
    args = parser.parse_args()
    if args.limit <= 0 or args.max_requests <= 0:
        parser.error("--limit 和 --max-requests 必须为正数")
    queue_path = PROJECT / "output/shape_research_queue.jsonl"
    queue = read_queue(queue_path)
    if not queue:
        parser.error("请先运行 build_cover_shape_output.py 建立车型族研究队列")
    policy = yaml.safe_load((PROJECT / "data/cover_shape/research_queue.yaml").read_text(encoding="utf-8"))
    markets = args.market or policy["research_markets"]
    selected = select_tasks(queue, policy, args.limit, markets=markets)
    plan = {"markets": markets, "selection": "model_families", "open_families": len(open_tasks(queue, policy, markets)),
            "selected": len(selected), "max_requests": args.max_requests,
            "tasks": [{k: t[k] for k in ("family_id", "market", "make", "model", "body_type", "state", "pending_records",
                                          "research_generations", "suggested_sample_years")} for t in selected]}
    if args.plan_only:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    with RunBatch.create(PROJECT / "artifacts", "shape-family-research", data_dir=PROJECT / "data") as batch:
        inputs = load_inputs(batch)
        batch.input(queue_path)
        # 取证过程中输入或规则被并行修改时，不发布混合版本，也不覆写他人修改。
        watched = [inputs["source_path"], queue_path, *sorted((PROJECT / "data").rglob("*")),
                   *sorted((PROJECT / "code").rglob("*.py"))]
        watched = {path: digest(path) for path in watched if path.is_file()}
        jsonl_write(batch.extra("research_plan.jsonl", compress=False), plan["tasks"])
        if not selected:
            batch.finish({"selected": 0, "reason": "没有到期且可研究的车型族"})
            print("没有到期且可研究的车型族")
            return
        groups = representative_groups(inputs["source"], inputs["legacy"], inputs["mapping"], inputs["policy"], inputs["source_sha"], inputs["evidence"])
        sources = yaml.safe_load((PROJECT / "data/cover_shape/sources.yaml").read_text(encoding="utf-8"))
        client = HttpClient(sources, PROJECT / "cache/cover_shape", args.max_requests)
        collector = AutomaticCollector(client, inputs["automatic"], [r for _, r, _, _ in groups])
        results, gathered, facts, progress, new_rules, report = [], [], [], {}, [], []
        print(json.dumps({"selected": len(selected), "max_requests": args.max_requests, "paid_api_cost": 0}, ensure_ascii=False), flush=True)
        for task in selected:
            if client.count >= client.max_requests:
                break
            task_evidence, task_results, task_rules = [], [], []
            timestamp = utc_now()
            for generation, gid, record in sample_targets(task, groups, policy):
                if client.count >= client.max_requests:
                    break
                print(json.dumps({"research": record["source_record_id"], "generation": generation, "year": record["model_year"]}, ensure_ascii=False), flush=True)
                evidence = [cvs_evidence(record, client, timestamp), *collector.collect(record, timestamp)]
                eligible = []
                for item in evidence:
                    if item["evidence_type"] not in {"automatic_description", "automatic_profile"} or item["validation_flags"]:
                        continue
                    scoped = copy.deepcopy(item)
                    scoped["data_payload"]["target_scope"] = {k: record.get(k, "") for k in ("make", "model", "generation", "body_type", "trim", "market", "CAB", "BED", "group_id")}
                    scoped["data_payload"]["inference_chain"] = {**scoped["data_payload"].get("inference_chain", {}),
                        "upstream_branch": record["source_record_id"], "generation": generation, "target_year": record["model_year"],
                        "target_scope_not_source_verification": True, "family_id": task["family_id"]}
                    scoped["evidence_id"] = "e:" + hashlib.sha256(json.dumps([scoped["variant_key"], scoped["source_url"], scoped["data_payload"]], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
                    eligible.append(scoped)
                result, _ = classify(record, eligible, inputs["taxonomy"], inputs["automatic"])
                result.update(group_id=gid, family_id=task["family_id"], generation=generation)
                task_results.append(result)
                task_evidence.extend(evidence)
                facts.extend(eligible)
                if eligible and result["cover_shape"] != "UNKNOWN" and result["status"] != "CONFLICT":
                    # 抽样年份结论写成本代际的车型族规则，同代其余年份/尺寸/trim 继承；跨代不继承。
                    task_rules.append({**{k: "" for k in CACHE_FIELDS}, "market": task["market"], "make": task["make"],
                        "model": task["model"], "body_type": task["body_type"], "generation": generation,
                        "shape": result["cover_shape"], "alternates": ";".join(result["alternate_shapes"]),
                        "sample_years": str(record["model_year"]), "source_url": "; ".join(sorted({e["source_url"] for e in eligible})),
                        "note": f"automatic {result['status']}; evidence {','.join(e['evidence_id'] for e in eligible)}",
                        "worker": "automatic", "updated_at": timestamp})
                report.append((task, generation, record, result))
            results.extend(task_results)
            gathered.extend(task_evidence)
            new_rules.extend(task_rules)
            progress[task["family_id"]] = record_attempt(task, task_evidence, task_results, task_rules, policy, batch.directory.name, timestamp)
        # 来源失败/图片拒绝保留在本批次；data 中仅保留真正提取的几何事实和由其得到的族规则，绝不将失败当覆盖。
        previous = {e["evidence_id"]: e for e in inputs["evidence"]}
        previous.update({e["evidence_id"]: e for e in facts})
        inputs["evidence"] = list(previous.values())
        replaced = {tuple(r[k] for k in RULE_IDENTITY) for r in new_rules}
        inputs["family_cache"] = [r for r in inputs["family_cache"] if tuple(r[k] for k in RULE_IDENTITY) not in replaced] + new_rules
        evidence_path = PROJECT / "data/cover_shape/evidence.jsonl"
        cache_path = PROJECT / "data/cover_shape/family_cache.csv"
        if any(digest(path) != expected for path, expected in watched.items()):
            raise RuntimeError("研究期间输入、代码或规则发生变化；本批不发布，请用当前版本重跑")
        prior_evidence, prior_cache = evidence_path.read_bytes(), cache_path.read_bytes()
        try:
            jsonl_write(batch.extra("research_evidence.jsonl", compress=False), gathered)
            jsonl_write(batch.extra("research_results.jsonl", compress=False), results)
            jsonl_write(batch.extra("network_requests.jsonl", compress=False), client.logs)
            for file in sorted(client.used_files):
                register_cached_resource(batch, file)
            if facts:
                jsonl_write(evidence_path, inputs["evidence"])
            if new_rules:
                write_cache(cache_path, inputs["family_cache"])
            summary = produce(batch, inputs=inputs, queue_overrides=progress)
            summary["research_run"] = {"selected": len(selected), "sampled_targets": len(results), "new_geometry_facts": len(facts),
                                       "new_family_rules": len(new_rules), "markets": markets, "selection": "model_families",
                                       "requests": client.count, "cache_hits": client.cache_hits,
                                       "results": dict(Counter(p["state"] for p in progress.values()))}
            batch.extra("RESEARCH_REPORT.md", compress=False).write_text("# 车型族抽样研究\n\n" + json.dumps(summary["research_run"], ensure_ascii=False, indent=2) +
                "\n\n研究单元为 市场/品牌/车型/结构；每个未覆盖代际只研究一个抽样年份（长代际在后续批次补首末年）。"
                "合格结论写入 data/cover_shape/family_cache.csv 的代际规则，同代其余年份/尺寸/trim/CAB/BED 继承（INFERRED，抽样年所在记录 PROBABLE）。"
                "取证失败/无合格侧面仍留队列，48 小时后可重试，最多 3 次；成功只表示得到候选依据，不等于 VERIFIED。\n\n"
                "|车型族|代际|研究年|候选分类|状态|\n|---|---|---|---|---|\n" +
                "".join(f"|{t['make']} {t['model']} {t['body_type']} {t['market']}|{g or '-'}|{r['model_year']}|{res['cover_shape']}|{res['status']}|\n"
                        for t, g, r, res in report), encoding="utf-8")
            batch.finish(summary, publish_to=PROJECT / "output")
        except Exception:
            evidence_path.write_bytes(prior_evidence)
            cache_path.write_bytes(prior_cache)
            raise
        print(json.dumps({"batch": str(batch.directory), **summary["research_run"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
