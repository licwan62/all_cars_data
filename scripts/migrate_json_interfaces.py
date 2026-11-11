"""Lossless format migration of current handoffs; never rerun or re-certify data.

Preserves the original upstream evidence and rules in each manifest. Historical
artifact files are read for reference only and are never rewritten.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch, sha256, versioned_name
from json_interface import convert, json_name, legacy_metadata, table_row_count
from node_paths import repository_metadata, load_record, node_output


def refresh_release_index(root, payload):
    path = repository_metadata(root, "release.json")
    summary = load_record(path, root) if path.is_file() else {"schema_version": 1, "nodes": {}}
    before = copy.deepcopy(summary)
    for node in payload["nodes"]:
        source = node_output(root, node) / "manifest.json"
        if not source.is_file() or not node.get("outputs"):
            continue
        manifest = load_record(source, root)
        summary.setdefault("nodes", {})[node["id"]] = {
            "path": node["path"], "version": manifest["version"], "artifact": manifest["artifact"],
            "deliverables": [i["file"] for i in manifest["deliverables"]], "pending": manifest.get("pending", []),
        }
    if summary == before and summary.get("format_migrated_at"):
        return
    summary["format_migrated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def migrated_contract(payload):
    result = copy.deepcopy(payload)
    mappings = {}
    for node in result["nodes"]:
        mapping = {}
        occupied = {name for name in node.get("outputs", []) if name.endswith(".json")}
        for name in node.get("outputs", []):
            candidate = name if name.endswith(".json") else json_name(name)
            if not name.endswith(".json") and candidate in occupied:
                candidate = name + ".json"
            mapping[name] = candidate
            occupied.add(candidate)
        if len(set(mapping.values())) != len(mapping):
            raise ValueError(f"{node['id']}: JSON 文件名冲突")
        mappings[node["id"]] = mapping
        node["interface_files"] = mapping
        node["outputs"] = list(mapping.values())
        node["public_outputs"] = [mapping[name] for name in node.get("public_outputs", [])]
        node["html_output"] = "结果.html"
        node["engine_run"] = node.get("run", [])
        if node["engine_run"]:
            prefix = "../" * len(Path(node["path"]).parts)
            node["run"] = [f"python {prefix}scripts/run_json_node.py --node {node['id']}"]
    for node in result["nodes"]:
        for inp in node.get("inputs", []):
            inp["file"] = mappings[inp["node"]].get(inp["file"], json_name(inp["file"]))
        for rule in node.get("identity_coverage", []):
            rule["output"] = mappings[node["id"]][rule["output"]]
            rule["file"] = mappings[rule["upstream"]][rule["file"]]
    for product in result.get("final_products", []):
        product["files"] = [mappings[product["node"]].get(name, name) for name in product.get("files", [])]
    result["interface_contract"] = {
        "format": "json", "table_schema": "vehicle-pipeline/table-v1",
        "policy": "节点间正式接口只读写JSON。表格采用columns+rows字符串矩阵；保留空值、顺序、前导零。人工data和外部源文件不迁移。旧计算引擎仅在隔离临时工作区物化CSV，不跨节点读取CSV。",
        "run": "python scripts/run_nodes.py --nodes <id>",
    }
    result["html_contract"] = {
        "output": "结果.html", "manifest": "html_manifest.json",
        "build": "python scripts/build_node_html.py",
        "policy": "所有登记项目交付HTML最终展示，完整内嵌JSON结果并提供CSV导出。artifacts按版本保存HTML快照及必要数据依据；历史批次不改写。容器/待接入/历史页不表示生产已验证。",
    }
    result["directory_contract"]["output"] = "JSON data handoffs plus 结果.html final presentation; data manifest.json and presentation html_manifest.json keep distinct provenance"
    result["directory_contract"]["artifacts"] += "; HTML result versions are immutable self-contained snapshots, with JSON provenance and original data artifacts retained"
    result["publication_contract"] = "public_outputs显式登记可导出的JSON表格；NAS发布时转换为CSV，其他JSON及HTML保持内部；本次迁移不发布NAS。"
    return result


def migrate(root):
    root = Path(root).resolve()
    config_path = root / "pipeline.json"
    original = config_path.read_bytes()
    payload = json.loads(original)
    if payload.get("interface_contract", {}).get("format") == "json":
        refresh_release_index(root, payload)
        print("JSON 接口已迁移；没有修改")
        return
    updated = migrated_contract(payload)
    by_id = {n["id"]: n for n in updated["nodes"]}
    # Preflight every file before changing any stable publication record.
    for node in payload["nodes"]:
        for name in node.get("outputs", []):
            convert(root / node["path"] / "output" / name)
    restore = {}
    retired = []
    try:
        for old_node in payload["nodes"]:
            if not old_node.get("outputs"):
                continue
            node = by_id[old_node["id"]]
            project = root / node["path"]
            output = project / "output"
            manifest_path = output / "manifest.json"
            previous = load_record(manifest_path, root) if manifest_path.is_file() else {}
            restore[manifest_path] = manifest_path.read_bytes() if manifest_path.is_file() else None
            with RunBatch.create(project / "artifacts", "json-interface-migration") as batch:
                if manifest_path.is_file():
                    batch.input(manifest_path, "previous-manifest.json")
                deliverables = []
                for old_name, name in node["interface_files"].items():
                    source = output / old_name
                    batch.input(source)
                    target = batch.output(name)
                    target.write_bytes(convert(source))
                    deliverables.append({
                        "file": name, "versioned_file": versioned_name(name, batch.version),
                        "artifact_file": target.relative_to(root).as_posix(), "sha256": sha256(target),
                        "bytes": target.stat().st_size, "rows": table_row_count(target),
                        **legacy_metadata(target, node, name),
                    })
                    if old_name != name:
                        retired.append((source, sha256(source)))
                manifest = {**previous, "schema_version": 2, "node": node["id"], "path": node["path"],
                            "version": batch.version, "artifact": batch.directory.relative_to(root).as_posix(),
                            "deliverables": deliverables,
                            "format_migration": {"previous_version": previous.get("version"),
                                                 "policy": "仅格式转换；数据未重算、未新核实，保留原upstream/rules依据。"}}
                # Native JSON may be content-reused by RunBatch. Its manifest must
                # point to durable bytes, not a filename the content store removes.
                from content_store import ContentIndex
                index = ContentIndex(root)
                index.rebuild()
                stored = {}
                for item in deliverables:
                    key = (item["sha256"], item["bytes"])
                    existing = stored.get(key) or index.find(*key)
                    if existing:
                        item["artifact_file"] = existing
                        item["content_reference"] = True
                    stored[key] = item["artifact_file"]
                index.close()
                batch.output("manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                batch.finish({"status": "passed", "purpose": "json-format-migration", "data_recomputed": False}, publish_to=output)
                # Standard publisher expects the immutable batch manifest here.
                (batch.directory / "manifest.json").write_bytes(manifest_path.read_bytes())
            print(f"JSON {node['id']}: {len(deliverables)} 个接口，数据未重算", flush=True)
        temporary = config_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, config_path)
    except BaseException:
        config_path.write_bytes(original)
        for path, value in restore.items():
            if value is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(value)
        raise
    # Retire only explicitly replaced, unchanged handoffs. Their original bytes
    # are protected by the migration run inputs and the original manifests.
    for path, expected in retired:
        if path.is_file() and sha256(path) == expected:
            path.unlink()
    refresh_release_index(root, updated)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    migrate(ROOT)
