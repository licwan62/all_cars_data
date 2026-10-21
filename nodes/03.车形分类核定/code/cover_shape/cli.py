"""独立研究入口；所有试运行仅留 artifact，不发布旧车形/正式 output。"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import importlib.metadata
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import __version__
from .classifier import classify, validate_taxonomy
from .evidence import load_evidence
from .fetchers import HttpClient, cvs_evidence, official_evidence, search_plan
from .geometry import annotation_svg, profile_features
from .ingest import digest, discover, inspect_table, normalize, read_table

PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch
from node_paths import load_record

DEFAULT_CONFIG = PROJECT / "data" / "cover_shape" / "pipeline.yaml"
RESULT_FIELDS = ["source_record_id", "source_record_ids", "variant_key", "make", "model", "model_year", "generation",
                 "body_type", "trim", "market", "length_mm", "width_mm", "height_mm", "cover_shape", "primary_shape",
                 "alternate_shapes", "taxonomy_version", "status", "review_required", "fit_tested", "fit_status",
                 "reason_codes", "evidence_ids", "classification_rationale", "raw_fields", "pipeline_version", "processed_at_utc"]


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def json_write(path: Path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def jsonl_write(path: Path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n" for r in rows), encoding="utf-8")


def csv_write(path: Path, fields: list[str], rows: list[dict]):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False, sort_keys=True, allow_nan=False) if isinstance(v, (list, dict))
                         else str(v).lower() if isinstance(v, bool) else v for k, v in r.items()} for r in rows)


def read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8-sig"))


def resolve_config(config_path: Path, key: str, config: dict) -> Path:
    path = Path(config[key])
    return path if path.is_absolute() else config_path.parent / path


def record_rule(batch: RunBatch, path: Path):
    # 本节点 data 由 RunBatch 全量规则快照负责，避免再复制一遍。
    if not path.resolve().is_relative_to((PROJECT / "data").resolve()):
        batch.input(path, "external_rules/" + path.name)


def frozen_input(batch: RunBatch, path: Path):
    """显式重分类引用本节点既有运行输出，不复制同一份历史字节。"""
    if path.resolve().is_relative_to((PROJECT / "artifacts").resolve()):
        for parent in path.parents:
            prior_run = parent / "run.json"
            if prior_run.is_file():
                record = load_record(prior_run, ROOT)
                for item in record.get("outputs", []):
                    source = ROOT / item["artifact_file"]
                    if source.resolve() == path.resolve() and digest(path) == item["sha256"]:
                        batch.inputs.append({"node": "shape-classification", "path": PROJECT.name,
                                             "version": record["version"], "file": item["file"],
                                             "artifact_file": item["artifact_file"], "sha256": item["sha256"],
                                             "source": "explicit frozen research run"})
                        return
                raise ValueError("冻结输入不匹配历史 run.json 登记的输出")
        raise ValueError("冻结输入没有可核查的 run.json")
    batch.input(path)


def register_cached_resource(batch: RunBatch, path: Path):
    """重用已有研究批次中的相同响应/照片/模型；缓存可重建，不重复归档字节。"""
    content_hash = digest(path)
    if not hasattr(batch, "_cached_resource_references"):
        index = {}
        for run_path in sorted((PROJECT / "artifacts").glob("*/run.json")):
            previous = load_record(run_path, ROOT)
            for item in previous.get("inputs", []):
                if item.get("artifact_file") and item.get("sha256"):
                    source = ROOT / item["artifact_file"]
                    if source.is_file() and source.resolve().is_relative_to((PROJECT / "artifacts").resolve()):
                        index.setdefault(item["sha256"], item)
        batch._cached_resource_references = index
    reference = batch._cached_resource_references.get(content_hash)
    if reference and digest(ROOT / reference["artifact_file"]) == content_hash:
        batch.inputs.append({"file": str(path.resolve()), "artifact_file": reference["artifact_file"],
                             "sha256": content_hash, "source": "identical previously archived research resource"})
    else:
        batch.input(path, "network/" + path.name)


def group_records(records: list[dict]) -> list[dict]:
    groups = {}
    for record in records:
        key = record["variant_key"]
        if key not in groups:
            groups[key] = {**record, "source_record_ids": [record["source_record_id"]], "raw_records": [record["raw_fields"]]}
        else:
            group = groups[key]
            if any(group.get(k) != record.get(k) for k in ("length_mm", "width_mm", "height_mm", "wheelbase_mm")):
                group["identity_flags"] = sorted(set(group["identity_flags"] + ["SOURCE_DIMENSION_CONFLICT"]))
            group["source_record_ids"].append(record["source_record_id"])
            group["raw_records"].append(record["raw_fields"])
    return sorted(groups.values(), key=lambda r: r["variant_key"])


def select_sample(records: list[dict], sample_path: Path) -> list[dict]:
    _, sample = read_table(sample_path)
    by_key = {(r["source_record_id"], str(r["model_year"])): r for r in records}
    result = []
    for row in sample:
        key = (row["source_record_id"], str(row["model_year"]))
        if key not in by_key:
            raise ValueError(f"样例未在输入中精确命中: {key}")
        result.append(by_key[key])
    return result


def validate_outputs(records, results, evidence):
    if len(results) != len(records) or len({r["variant_key"] for r in results}) != len(results):
        raise ValueError("结果不是每个 variant_key 一行")
    evidence_ids = {e["evidence_id"] for e in evidence}
    for r in results:
        if set(r["evidence_ids"]) - evidence_ids:
            raise ValueError("结果引用不存在证据")
        if r["cover_shape"] != "UNKNOWN" and not r["evidence_ids"]:
            raise ValueError("非 UNKNOWN 分类缺少证据")
        if r["status"] != "VERIFIED" and not r["review_required"]:
            raise ValueError("低证据状态必须复核")
        if r["fit_status"] != "NOT_TESTED" or r["fit_tested"]:
            raise ValueError("不得宣称已打样")


def export_run(batch, records, evidence, taxonomy, timestamp, mode, started, client=None, automatic_policy=None):
    by_variant = defaultdict(list)
    for item in evidence:
        by_variant[item["variant_key"]].append(item)
    results, features = [], []
    for record in records:
        result, feature = classify(record, by_variant[record["variant_key"]], taxonomy, automatic_policy)
        result.update({"pipeline_version": __version__, "processed_at_utc": timestamp})
        results.append(result)
        features.append(feature)
    validate_outputs(records, results, evidence)
    queue = [{"variant_key": r["variant_key"], "priority": 0 if r["status"] == "CONFLICT" else 1 if r["alternate_shapes"] else 2,
              "why_review": r["reason_codes"], "evidence_ids": r["evidence_ids"],
              "suggested_action": "自动继续检索原厂资料/独立来源以核验候选；复核可选，无需提供侧视图" if automatic_policy else
                                  "核实年份/代际/车身版本/市场；导入原厂尺寸、合格侧面标注及人工标定原型"}
             for r in results if r["review_required"]]
    queue.sort(key=lambda r: (r["priority"], r["variant_key"]))
    csv_write(batch.output("cover_shape_results.csv"), RESULT_FIELDS, results)
    csv_write(batch.output("review_queue.csv"), ["variant_key", "priority", "why_review", "evidence_ids", "suggested_action"], queue)
    jsonl_write(batch.output("cover_shape_features.jsonl"), features)
    jsonl_write(batch.output("cover_shape_records.jsonl"), records)
    jsonl_write(batch.output("evidence.jsonl"), evidence)
    counters = Counter(r["status"] for r in results)
    outcomes = Counter(e["data_payload"].get("outcome", "IMPORTED") for e in evidence)
    if client:
        jsonl_write(batch.extra("network_requests.jsonl", compress=False), client.logs)
        for file in sorted(client.used_files):
            register_cached_resource(batch, file)
    # 只绘制合格标注，无版权照片；每张来源单独保留，不抹掉冲突。
    for item in evidence:
        if item["evidence_type"] == "side_profile":
            feature = profile_features(item["data_payload"], taxonomy["image_gate"])
            if feature.get("usable"):
                try:
                    batch.extra("annotations/" + item["evidence_id"].replace(":", "_") + ".svg", compress=False).write_text(
                        annotation_svg(item["data_payload"]), encoding="utf-8")
                except (ValueError, KeyError, TypeError):
                    pass
    manifest = {"pipeline_version": __version__, "taxonomy_version": taxonomy["taxonomy_version"],
                "started_at_utc": timestamp, "elapsed_seconds": round(time.monotonic() - started, 3), "mode": mode,
                "input_references": batch.inputs, "dependency_versions": {"python": platform.python_version(), "PyYAML": yaml.__version__},
                "network_adapters": (["NHTSA_CVS", "explicit_official_url"] + (["source_geometry_descriptions", "Commons_API", "local_U2netp_OpenCV"] if automatic_policy else ["manual_image_search"])) if mode == "online" else [],
                "network_requests": client.count if client else 0, "cache_hits": client.cache_hits if client else 0,
                "variant_count": len(records), "status_counts": dict(counters), "evidence_outcomes": dict(outcomes),
                "fit_status": "NOT_TESTED", "published": False,
                "rules_provenance": "run.json rules (sha256 + git commit + dirty snapshots)",
                "implementation_sha256": {p.name: digest(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
                "reclassify_records": "cover_shape_records.jsonl"}
    manifest["automatic_rule_version"] = automatic_policy["rule_version"] if automatic_policy else None
    if automatic_policy:
        for package in ("numpy", "Pillow", "opencv-python", "opencv-python-headless", "onnxruntime"):
            try: manifest["dependency_versions"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError: pass
    json_write(batch.output("run_manifest.json"), manifest)
    batch.extra("REPORT.md", compress=False).write_text(
        f"# COVER_SHAPE 研究运行\n\n模式：{mode}；车型分支：{len(records)}；状态：{dict(counters)}。\n\n"
        f"证据处理：{dict(outcomes)}；HTTP 请求 {manifest['network_requests']}，缓存命中 {manifest['cache_hits']}。\n\n"
        "本批次不发布正式 output，不改变旧车形号，不用于 COVER_FIT/SKU。\n\n"
        + ("自动检索有许可照片、本地分割/轮心检测/几何试验规则已启用；自动候选最高 INFERRED，"
         "不要求用户提供图片或关键点；不能宣称 VERIFIED 精确率或通用阈值已经标定。\n" if automatic_policy else
         "已审原型为空时 UNKNOWN；准确率与 VERIFIED 精确率尚无人工测试集可评估。\n"),
        encoding="utf-8")
    batch.finish({"mode": mode, "variants": len(records), "status_counts": dict(counters), "published": False})
    return manifest


def run(args):
    started, timestamp = time.monotonic(), utc_now()
    implementation_before = {p: digest(p) for p in Path(__file__).parent.glob("*.py")}
    rules_before = {p: digest(p) for p in (PROJECT / "data").rglob("*") if p.is_file()}
    config_path = Path(args.config).resolve()
    config = read_yaml(config_path)
    taxonomy_path = resolve_config(config_path, "taxonomy", config)
    mapping_path = resolve_config(config_path, "column_map", config)
    sources_path = resolve_config(config_path, "sources", config)
    taxonomy, mapping, sources = read_yaml(taxonomy_path), read_yaml(mapping_path), read_yaml(sources_path)
    automatic_path = resolve_config(config_path, "automatic", config) if config.get("automatic") else None
    automatic_policy = read_yaml(automatic_path) if automatic_path else None
    if automatic_policy and not automatic_policy.get("enabled"):
        automatic_policy = None
    validate_taxonomy(taxonomy)
    if args.mode == "online" and (args.limit is None or args.limit <= 0 or args.max_requests <= 0):
        raise ValueError("联网必须指定正数 --limit 和 --max-requests")
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit 必须为正数")
    input_path = Path(args.input).resolve()
    before = digest(input_path)
    with RunBatch.create(PROJECT / "artifacts", "cover-shape-" + args.mode, data_dir=PROJECT / "data") as batch:
        batch.input(input_path)
        for p in (config_path, taxonomy_path, mapping_path, sources_path):
            record_rule(batch, p)
        if automatic_path:
            record_rule(batch, automatic_path)
        columns, rows = read_table(input_path)
        missing_columns = set(mapping["columns"].values()) - set(columns)
        if missing_columns:
            raise ValueError(f"显式映射列不存在: {sorted(missing_columns)}")
        records = normalize(rows, mapping, before)
        if args.sample:
            sample_path = Path(args.sample).resolve()
            record_rule(batch, sample_path)
            records = select_sample(records, sample_path)
        records = group_records(records)
        if args.limit:
            records = records[:args.limit]
        evidence = []
        evidence_path = Path(args.evidence).resolve() if args.evidence else resolve_config(config_path, "evidence", config)
        if evidence_path.exists():
            record_rule(batch, evidence_path)
            evidence = load_evidence(evidence_path)
        elif args.evidence:
            raise ValueError(f"证据文件不存在: {evidence_path}")
        keys = {r["variant_key"] for r in records}
        unused = [e["evidence_id"] for e in evidence if e["variant_key"] not in keys]
        if unused:
            json_write(batch.extra("unused_evidence.json", compress=False), {"evidence_ids": unused})
        evidence = [e for e in evidence if e["variant_key"] in keys]
        client = None
        if args.mode == "online":
            print(json.dumps({"estimate": {"vehicles": len(records), "max_http_requests_including_robots_retries": args.max_requests,
                                         "paid_api_cost": 0, "seconds_per_request": sources["seconds_per_request"]}}, ensure_ascii=False), flush=True)
            client = HttpClient(sources, PROJECT / "cache" / "cover_shape", args.max_requests)
        collector = None
        if client and automatic_policy:
            from .automatic import AutomaticCollector
            collector = AutomaticCollector(client, automatic_policy, records)
        for record in records:
            if not automatic_policy:
                evidence.append(search_plan(record, timestamp, args.mode))
            if client:
                evidence.append(cvs_evidence(record, client, timestamp))
                for source in sources.get("official_sources", []):
                    if source["variant_key"] == record["variant_key"]:
                        evidence.append(official_evidence(record, client, timestamp, source))
                if collector:
                    print(json.dumps({"automatic_research": record["source_record_id"], "year": record["model_year"]}, ensure_ascii=False), flush=True)
                    evidence.extend(collector.collect(record, timestamp))
        # 导入 evidence 可能包含上一次的搜索计划，按 ID 去重但禁止不同内容覆盖。
        by_id = {}
        for e in evidence:
            existing = by_id.get(e["evidence_id"])
            if existing and {k: v for k, v in existing.items() if k != "retrieved_at_utc"} != {k: v for k, v in e.items() if k != "retrieved_at_utc"}:
                raise ValueError("同 evidence_id 内容不一致")
            by_id.setdefault(e["evidence_id"], e)
        if digest(input_path) != before:
            raise ValueError("运行期间源数据变化")
        implementation_after = {p: digest(p) for p in Path(__file__).parent.glob("*.py")}
        rules_after = {p: digest(p) for p in (PROJECT / "data").rglob("*") if p.is_file()}
        if implementation_before != implementation_after or rules_before != rules_after:
            raise ValueError("运行期间实现或规则发生变化；拒绝把结果登记为可复现成功批次，请重新运行")
        manifest = export_run(batch, records, list(by_id.values()), taxonomy, timestamp, args.mode, started, client, automatic_policy)
        print(json.dumps({"batch": str(batch.directory), "status_counts": manifest["status_counts"]}, ensure_ascii=False))


def inspect(args):
    path = Path(args.input).resolve()
    if args.out and Path(args.out).resolve() == path:
        raise ValueError("--out 不得覆盖输入")
    if args.out:
        destination = Path(args.out).resolve()
        if destination.is_relative_to((PROJECT / "data").resolve()) or "output" in destination.parts or "artifacts" in destination.parts:
            raise ValueError("--out 仅允许工作目录；规则/output/artifacts 由流水线维护")
    report = inspect_table(path)
    with RunBatch.create(PROJECT / "artifacts", "cover-shape-inspection", data_dir=PROJECT / "data") as batch:
        batch.input(path)
        target = batch.output("inspection.json")
        json_write(target, report)
        batch.output("column_map_draft.yaml").write_text(yaml.safe_dump(report["column_map_draft"], allow_unicode=True, sort_keys=False), encoding="utf-8")
        batch.extra("REPORT.md", compress=False).write_text(
            f"# 只读盘点\n\n行数 {report['rows']}；原文件 sha256 未变化。\n\n"
            f"缺失代际 {report['missing_generation']}；重复主键 {len(report['duplicate_source_ids'])}；"
            f"重复整行 {report['exact_duplicate_rows']}。\n\n" + "\n".join(f"- {r}" for r in report["risks"]) + "\n", encoding="utf-8")
        batch.finish({"source_unchanged": True, "rows": report["rows"]})
        if args.out:
            destination = Path(args.out).resolve()
            # 非正式可重建的工作副本；正式交付仅在 artifact 中。
            destination.parent.mkdir(parents=True, exist_ok=True)
            tmp = destination.with_suffix(destination.suffix + ".tmp")
            tmp.write_bytes(target.read_bytes())
            os.replace(tmp, destination)
        print(json.dumps({"batch": str(batch.directory), "rows": report["rows"], "source_unchanged": True}, ensure_ascii=False))


def reclassify(args):
    evidence_path, taxonomy_path = Path(args.evidence).resolve(), Path(args.taxonomy).resolve()
    if args.records:
        records_path = Path(args.records).resolve()
    else:
        # 附加输入文件保留身份原值，不能仅由证据重建没有证据的 UNKNOWN 分支。
        suffix = evidence_path.name.removeprefix("evidence")
        records_path = evidence_path.with_name("cover_shape_records" + suffix)
    taxonomy = read_yaml(taxonomy_path)
    automatic_path = Path(args.automatic).resolve() if args.automatic else PROJECT / "data/cover_shape/automatic.yaml"
    automatic_policy = read_yaml(automatic_path) if automatic_path.is_file() else None
    validate_taxonomy(taxonomy)
    with RunBatch.create(PROJECT / "artifacts", "cover-shape-reclassify", data_dir=PROJECT / "data") as batch:
        frozen_input(batch, evidence_path)
        frozen_input(batch, records_path)
        record_rule(batch, taxonomy_path)
        if automatic_policy:
            record_rule(batch, automatic_path)
        evidence = load_evidence(evidence_path)
        records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        manifest = export_run(batch, records, evidence, taxonomy, utc_now(), "reclassify", time.monotonic(), automatic_policy=automatic_policy)
        print(json.dumps({"batch": str(batch.directory), "status_counts": manifest["status_counts"]}, ensure_ascii=False))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="cover-shape", description="只读 COVER_SHAPE 研究；不发布 fitment")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("inspect")
    p.add_argument("--input", required=True)
    p.add_argument("--out")
    p.set_defaults(func=inspect)
    p = sub.add_parser("run")
    p.add_argument("--input", required=True)
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--mode", choices=("offline", "online"), default="offline")
    p.add_argument("--sample")
    p.add_argument("--evidence")
    p.add_argument("--limit", type=int)
    p.add_argument("--max-requests", type=int, default=120)
    p.set_defaults(func=run)
    p = sub.add_parser("reclassify")
    p.add_argument("--evidence", required=True)
    p.add_argument("--taxonomy", required=True)
    p.add_argument("--records")
    p.add_argument("--automatic", help="重分类的自动几何规则；默认读取本节点 data/cover_shape/automatic.yaml")
    p.set_defaults(func=reclassify)
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (ValueError, OSError, KeyError, TypeError, ImportError) as e:
        parser.exit(2, f"cover-shape: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    main()
