"""Standalone, versioned HTML presentation of a node's current output.

Presentation is separate from production publication: rendering never certifies or
refreshes the source data. The embedded datasets make historical pages independent
of later changes to output/.
"""
from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path

from artifact_batch import RunBatch, sha256, versioned_name
from node_paths import load_record, node_output, node_page
from rules_snapshot import rules_snapshot
from json_interface import SCHEMA, TEXT_SCHEMA, WORKBOOK_SCHEMA, legacy_name

HTML_FILE = "结果.html"
HTML_MANIFEST = "html_manifest.json"
TEMPLATE = Path(__file__).with_name("node_html_template.html")


def packed(value):
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")


def inspect_sources(root, node):
    output = node_output(root, node)
    manifest_path = output / "manifest.json"
    manifest = load_record(manifest_path, root) if manifest_path.is_file() else {}
    published = {i["file"]: i for i in manifest.get("deliverables", [])}
    sources = []
    for name in node.get("outputs", []):
        path = output / name
        item = {"file": name, "exists": path.is_file()}
        if path.is_file():
            item.update(sha256=sha256(path), bytes=path.stat().st_size)
            previous = published.get(name, {})
            item["matches_manifest"] = item["sha256"] == previous.get("sha256")
            if item["matches_manifest"]:
                item["artifact_file"] = previous.get("artifact_file")
        sources.append(item)
    return manifest, sources


def context(root, node, nodes):
    # Import here to avoid coupling RunBatch and the publisher to the status UI.
    from pipeline_status import node_state, is_on_demand

    payload = json.loads((root / "pipeline.json").read_text(encoding="utf-8"))
    manifests = {}
    for entry in nodes:
        path = node_output(root, entry) / "manifest.json"
        manifests[entry["id"]] = load_record(path, root) if path.is_file() else None
    state, warnings = node_state(node, {n["id"]: n for n in nodes}, manifests, is_on_demand(payload, node))
    manifest, sources = inspect_sources(root, node)
    warnings = list(warnings)
    for item in sources:
        if not item["exists"]:
            warnings.append(f"缺少交付物：{item['file']}")
        elif not item["matches_manifest"]:
            warnings.append(f"当前文件未获 manifest 核实：{item['file']}")
    rules = rules_snapshot(root / node["path"])
    if manifest and manifest.get("rules") != rules:
        warnings.append("本节点 data 规则与数据发布版本不一致，数据尚未刷新。")
    return {
        "node": node, "state": state, "warnings": warnings,
        "manifest": manifest, "sources": sources, "rules": rules,
        "children": [{"id": n["id"], "path": n["path"], "lifecycle": n.get("lifecycle", "active")}
                     for n in nodes if n.get("parent") == node["id"]],
    }


def fingerprint(info):
    digest = hashlib.sha256(json.dumps(info, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    digest.update(TEMPLATE.read_bytes())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()


def datasets(root, node, sources):
    result = []
    for item in sources:
        entry = dict(item)
        if not item["exists"]:
            result.append(entry)
            continue
        path = node_output(root, node) / item["file"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise RuntimeError(f"生成 HTML 时源文件变化：{path}")
        text = raw.decode("utf-8-sig")
        payload = json.loads(text) if path.suffix.lower() == ".json" else None
        if isinstance(payload, dict) and payload.get("schema") == SCHEMA:
            entry.update(kind="table", columns=payload["columns"], rows=len(payload["rows"]),
                         packed=packed(payload["rows"]), export_name=Path(legacy_name(node, item["file"])).with_suffix(".csv").as_posix())
        elif isinstance(payload, dict) and payload.get("schema") == WORKBOOK_SCHEMA:
            for sheet in payload["sheets"]:
                result.append({**entry, "file": item["file"] + " / " + sheet["name"], "kind": "table",
                               "columns": sheet["columns"], "rows": len(sheet["rows"]), "packed": packed(sheet["rows"]),
                               "export_name": sheet["name"] + ".csv"})
            continue
        elif isinstance(payload, dict) and payload.get("schema") == TEXT_SCHEMA:
            entry.update(kind="text", packed=packed(payload["text"]), export_name=legacy_name(node, item["file"]))
        elif path.suffix.lower() in {".csv", ".tsv"}:
            reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
            entry["columns"] = next(reader, [])
            rows = list(reader)
            entry.update(kind="table", rows=len(rows), packed=packed(rows))
        else:
            entry.update(kind="text", packed=packed(text))
        result.append(entry)
    return result


def build_node(root, node, nodes):
    """Return metadata for a new HTML batch, or None when already current."""
    root = Path(root).resolve()
    info = context(root, node, nodes)
    signature = fingerprint(info)
    output = node_output(root, node)
    metadata_path = output / HTML_MANIFEST
    old = load_record(metadata_path, root) if metadata_path.is_file() else {}
    page = node_page(root, node)
    html_name = page.name
    if old.get("fingerprint") == signature and page.is_file():
        expected = old.get("deliverables", [{}])[0]
        if sha256(page) == expected.get("sha256"):
            from content_store import resolve_source
            source = resolve_source(root, expected["artifact_file"])
            if source.is_file() and sha256(source) == expected["sha256"]:
                return None
    data = datasets(root, node, info["sources"])
    with RunBatch.create(root / node["path"] / "artifacts", "html-result") as batch:
        for item in info["sources"]:
            if item["exists"]:
                path = output / item["file"]
                batch.input(path)
                if batch.inputs[-1]["sha256"] != item["sha256"]:
                    raise RuntimeError(f"源文件在 HTML 归档时变化：{item['file']}")
        manifest_path = output / "manifest.json"
        if manifest_path.is_file():
            batch.input(manifest_path, "data-manifest.json")
        html_path = batch.output(html_name)
        display = {**info, "datasets": data, "html_version": batch.version,
                   "navigation": {"current": Path(os.path.relpath(root / "流水线状态.html", page.parent)).as_posix(),
                                  "archive": Path(os.path.relpath(root / "流水线状态.html", html_path.parent)).as_posix()}}
        serialized = json.dumps(display, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("&", "\\u0026")
        html = TEMPLATE.read_text(encoding="utf-8").replace("__REPORT_DATA__", serialized)
        html_path.write_text(html, encoding="utf-8", newline="\n")
        artifact = batch.directory.relative_to(root).as_posix()
        metadata = {
            "schema_version": 2, "purpose": "html-presentation", "node": node["id"],
            "path": node["path"], "version": batch.version, "artifact": artifact,
            "fingerprint": signature, "data_version": info["manifest"].get("version"),
            "sources": info["sources"],
            "deliverables": [{"file": html_name, "sha256": sha256(html_path),
                              "current_file": page.relative_to(root).as_posix(),
                              "versioned_file": versioned_name(html_name, batch.version),
                              "artifact_file": html_path.relative_to(root).as_posix()}],
        }
        batch.output(HTML_MANIFEST).write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # A concurrent change must not install a page bearing an obsolete fingerprint.
        if fingerprint(context(root, node, nodes)) != signature:
            raise RuntimeError("生成 HTML 期间节点来源或配置发生变化，拒绝更新展示页")
        batch.finish({"status": "passed", "purpose": "html-presentation", "data_verified": False},
                     publish_paths={html_name: page, HTML_MANIFEST: metadata_path})
        return metadata


def build_reports(root, only=None):
    root = Path(root).resolve()
    nodes = json.loads((root / "pipeline.json").read_text(encoding="utf-8"))["nodes"]
    if only and set(only) - {n["id"] for n in nodes}:
        raise ValueError("未知 HTML 节点：" + ",".join(sorted(set(only) - {n["id"] for n in nodes})))
    results = {}
    for node in nodes:
        if node.get("html_output") and (only is None or node["id"] in only):
            result = build_node(root, node, nodes)
            results[node["id"]] = result
            print(f"HTML {node['id']}: {result['version'] if result else '未变化'}", flush=True)
    return results


def check_reports(root, nodes):
    errors = []
    from content_store import resolve_source
    for node in nodes:
        if not node.get("html_output"):
            continue
        output = node_output(root, node)
        try:
            metadata = load_record(output / HTML_MANIFEST, root)
            entry = metadata["deliverables"][0]
            if entry["file"] != node["html_output"] or sha256(node_page(root, node)) != entry["sha256"]:
                errors.append(f"{node['id']}: HTML 当前页哈希不一致")
            if sha256(resolve_source(root, entry["artifact_file"])) != entry["sha256"]:
                errors.append(f"{node['id']}: HTML 版本存档哈希不一致")
            if metadata.get("fingerprint") != fingerprint(context(root, node, nodes)):
                errors.append(f"{node['id']}: HTML 展示待刷新（运行 build_node_html.py）")
        except (OSError, ValueError, KeyError, IndexError) as error:
            errors.append(f"{node['id']}: HTML 交付缺失或损坏：{error}")
    return errors
