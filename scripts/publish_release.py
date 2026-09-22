#!/usr/bin/env python3
"""按 pipeline.json 对各节点做一次标准发布（自上游到下游）。

每个节点：
1. 新建不可覆盖的 ``artifacts/YYYY-MM-DD_NN_release/``；
2. 把 ``outputs`` 声明的稳定交付物按 ``名称-YYYYMMDD_NN.扩展名`` 保存进该批次的 ``output/``，
   并写 ``manifest.json``（交付物、sha256、上游节点及其版本、待落地项）；
3. 全部校验通过后，去掉版本后缀，原子发布到节点 ``output/``，同时写入同样的 ``output/manifest.json``。

最后在仓库根目录写 ``release.json`` 汇总各节点当前版本与 artifact 来源。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "release"
MANIFEST_NAME = "manifest.json"


class ReleaseError(ValueError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def row_count(path: Path) -> int | None:
    if path.suffix.lower() not in {".csv", ".tsv"}:
        return None
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle, delimiter=delimiter)) - 1, 0)


def versioned_name(file_name: str, version: str) -> str:
    path = Path(file_name)
    return f"{path.stem}-{version}{path.suffix}"


def topological_order(nodes: list[dict]) -> list[dict]:
    by_id = {node["id"]: node for node in nodes}
    ordered: list[dict] = []
    seen: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in seen:
            return
        seen.add(node_id)
        for upstream in by_id[node_id].get("upstream", []):
            visit(upstream)
        ordered.append(by_id[node_id])

    for node in nodes:
        visit(node["id"])
    return ordered


def next_batch(artifacts_dir: Path, day: str) -> tuple[str, str]:
    """返回 (批次目录名, 版本后缀)，如 ('2026-09-21_01_release', '20260921_01')。"""
    used = [
        int(match.group(1))
        for path in artifacts_dir.glob(f"{day}_*")
        if path.is_dir() and (match := re.match(rf"^{re.escape(day)}_(\d{{2}})_", path.name))
    ]
    number = max(used, default=0) + 1
    if number > 99:
        raise ReleaseError(f"{artifacts_dir} 当天批次已用尽")
    return f"{day}_{number:02d}_{SLUG}", f"{day.replace('-', '')}_{number:02d}"


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def upstream_records(root: Path, node: dict, by_id: dict[str, dict]) -> list[dict]:
    records = []
    for upstream_id in node.get("upstream", []):
        upstream = by_id[upstream_id]
        manifest_path = root / upstream["path"] / "output" / MANIFEST_NAME
        if not manifest_path.is_file():
            records.append({"node": upstream_id, "version": None, "files": []})
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records.append(
            {
                "node": upstream_id,
                "version": manifest["version"],
                "artifact": manifest["artifact"],
                "files": [
                    {
                        "file": item["file"],
                        "versioned_file": item.get("versioned_file"),
                        "artifact_file": f"{manifest['artifact']}/output/{item.get('versioned_file')}",
                        "sha256": item["sha256"],
                    }
                    for item in manifest["deliverables"]
                ],
            }
        )
    return records


def check_outputs(root: Path, nodes: list[dict]) -> list[str]:
    errors = []
    for node in nodes:
        for name in node.get("outputs", []):
            if not (root / node["path"] / "output" / name).is_file():
                errors.append(f"{node['id']}: output/{name} 不存在；未产出的交付物请移到 pending")
    return errors


def release_node(root: Path, node: dict, by_id: dict[str, dict], today: str, released_at: str) -> dict:
    project = root / node["path"]
    output_dir = project / "output"
    artifacts_dir = project / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    batch_name, version = next_batch(artifacts_dir, today)
    batch_dir = artifacts_dir / batch_name
    staging = artifacts_dir / f".{batch_name}.tmp"
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "output").mkdir(parents=True)

    deliverables = []
    for name in node.get("outputs", []):
        source = output_dir / name
        target = staging / "output" / versioned_name(name, version)
        shutil.copy2(source, target)
        deliverables.append(
            {
                "file": name,
                "versioned_file": target.name,
                "artifact_file": f"{node['path']}/artifacts/{batch_name}/output/{target.name}",
                "sha256": sha256(target),
                "bytes": target.stat().st_size,
                "rows": row_count(target),
            }
        )
    manifest = {
        "schema_version": 1,
        "node": node["id"],
        "path": node["path"],
        "version": version,
        "artifact": f"{node['path']}/artifacts/{batch_name}",
        "published_at": released_at,
        "deliverables": deliverables,
        "upstream": upstream_records(root, node, by_id),
        "pending": node.get("pending", []),
        "notes": node.get("release_notes", []),
    }
    write_json_atomic(staging / MANIFEST_NAME, manifest)
    os.replace(staging, batch_dir)

    # 校验通过后才发布：去掉版本后缀，逐文件原子替换
    for item in deliverables:
        published = output_dir / item["file"]
        temporary = published.with_name(f".{published.name}.tmp")
        shutil.copy2(batch_dir / "output" / item["versioned_file"], temporary)
        os.replace(temporary, published)
    write_json_atomic(output_dir / MANIFEST_NAME, manifest)
    return manifest


def release_all(root: Path, only: set[str] | None = None, dry_run: bool = False) -> dict:
    payload = json.loads((root / "pipeline.json").read_text(encoding="utf-8"))
    nodes = topological_order(payload["nodes"])
    by_id = {node["id"]: node for node in payload["nodes"]}
    selected = [node for node in nodes if not only or node["id"] in only]
    errors = check_outputs(root, selected)
    if errors:
        raise ReleaseError("\n".join(errors))
    now = datetime.now().astimezone()
    released: dict[str, dict] = {}
    for node in selected:
        if dry_run:
            print(f"[dry-run] {node['id']}: {len(node.get('outputs', []))} 个交付物")
            continue
        manifest = release_node(root, node, by_id, date.today().isoformat(), now.isoformat(timespec="seconds"))
        released[node["id"]] = manifest
        print(f"{node['path']}: {manifest['version']}  {len(manifest['deliverables'])} 个交付物，pending {len(manifest['pending'])}")
    if not dry_run and released:
        summary_path = root / "release.json"
        previous = json.loads(summary_path.read_text(encoding="utf-8"))["nodes"] if summary_path.is_file() else {}
        previous = {node_id: entry for node_id, entry in previous.items() if node_id in by_id}
        previous.update(
            {
                node_id: {
                    "path": manifest["path"],
                    "version": manifest["version"],
                    "artifact": manifest["artifact"],
                    "deliverables": [item["file"] for item in manifest["deliverables"]],
                    "pending": manifest["pending"],
                }
                for node_id, manifest in released.items()
            }
        )
        write_json_atomic(
            summary_path,
            {"schema_version": 1, "released_at": now.isoformat(timespec="seconds"), "nodes": previous},
        )
    return released


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", help="只发布这些节点 id（逗号分隔），默认全量")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        release_all(ROOT, set(args.nodes.split(",")) if args.nodes else None, args.dry_run)
    except ReleaseError as error:
        print(f"发布失败：{error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
