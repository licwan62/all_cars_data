#!/usr/bin/env python3
"""按 pipeline.json 对各节点做一次标准发布（自上游到下游）。

每个节点：
1. 新建不可覆盖的 ``artifacts/YYYY-MM-DD_NN_<node>-release/``，并写入 ``REPORT.md``；
2. 把 ``outputs`` 声明的稳定交付物按 ``名称-YYYYMMDD_NN.扩展名`` 保存进该批次的 ``output/``，
   并写 ``manifest.json``（交付物、sha256、上游节点及其版本、待落地项）；
3. 全部校验通过后，去掉版本后缀，原子发布到节点 ``output/``，同时写入同样的 ``output/manifest.json``；
4. ``REPORT.md`` 将当前交付物与上一版本 artifact 比较，记录 CSV 的新增、删除、字段修改及示例。

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
MANIFEST_NAME = "manifest.json"
REPORT_NAME = "REPORT.md"


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


def artifact_slug(node: dict) -> str:
    """Return a stable, human-readable description for an automated release batch."""
    value = re.sub(r"[^a-z0-9]+", "-", str(node["id"]).lower()).strip("-")
    return f"{value or 'pipeline'}-release"


def next_batch(artifacts_dir: Path, day: str, slug: str) -> tuple[str, str]:
    """返回 (批次目录名, 版本后缀)，如 ('2026-09-21_01_dimension-library-release', '20260921_01')。"""
    used = [
        int(match.group(1))
        for path in artifacts_dir.glob(f"{day}_*")
        if path.is_dir() and (match := re.match(rf"^{re.escape(day)}_(\d{{2}})_", path.name))
    ]
    number = max(used, default=0) + 1
    if number > 99:
        raise ReleaseError(f"{artifacts_dir} 当天批次已用尽")
    return f"{day}_{number:02d}_{slug}", f"{day.replace('-', '')}_{number:02d}"


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _csv_change_summary(previous: Path, current: Path) -> list[str]:
    """Summarize logical CSV changes without putting a huge row diff in the report."""
    with previous.open("r", encoding="utf-8-sig", newline="") as handle:
        old_rows = list(csv.DictReader(handle))
    with current.open("r", encoding="utf-8-sig", newline="") as handle:
        new_rows = list(csv.DictReader(handle))
    key = "DIMENSION-ID" if all(row.get("DIMENSION-ID", "").strip() for row in old_rows + new_rows) else None
    if not key or len({row[key] for row in old_rows}) != len(old_rows) or len({row[key] for row in new_rows}) != len(new_rows):
        return ["- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。"]
    old_by_key = {row[key]: row for row in old_rows}
    new_by_key = {row[key]: row for row in new_rows}
    added = sorted(new_by_key.keys() - old_by_key.keys())
    removed = sorted(old_by_key.keys() - new_by_key.keys())
    changed: list[tuple[str, list[str]]] = []
    columns: dict[str, int] = {}
    for record_id in sorted(old_by_key.keys() & new_by_key.keys()):
        fields = sorted(
            field for field in set(old_by_key[record_id]) | set(new_by_key[record_id])
            if old_by_key[record_id].get(field, "") != new_by_key[record_id].get(field, "")
        )
        if fields:
            changed.append((record_id, fields))
            for field in fields:
                columns[field] = columns.get(field, 0) + 1
    summary = [f"- 行级差异：新增 {len(added)}，删除 {len(removed)}，修改 {len(changed)}。"]
    if columns:
        summary.append("- 变更字段计数：" + "，".join(f"`{field}` {count}" for field, count in sorted(columns.items())) + "。")
    for label, values in (("新增", added), ("删除", removed)):
        if values:
            summary.append(f"- {label}示例（最多 10 条）：" + "；".join(f"`{value}`" for value in values[:10]) + "。")
    if changed:
        summary.append("- 修改示例（最多 20 条）：")
        summary.extend(f"  - `{record_id}`：" + "、".join(f"`{field}`" for field in fields) for record_id, fields in changed[:20])
    return summary


def write_report(path: Path, node: dict, version: str, released_at: str, previous_manifest: dict | None, deliverables: list[dict], output_dir: Path, root: Path) -> None:
    """Write an auditable, compact Markdown description of this artifact's changes."""
    lines = [
        "# 发布报告", "",
        f"- 节点：`{node['id']}`（`{node['path']}`）",
        f"- 版本：`{version}`",
        f"- 发布时间：`{released_at}`",
        f"- 工作描述：{artifact_slug(node).removesuffix('-release')} 输出刷新。", "",
        "## 交付物与变更", "",
    ]
    previous = {item["file"]: item for item in (previous_manifest or {}).get("deliverables", [])}
    for item in deliverables:
        name = item["file"]
        current = output_dir / name
        old = previous.get(name)
        lines.append(f"### `{name}`")
        if not old:
            lines.extend(["", f"- 本版本新增交付物，共 {item.get('rows', 'N/A')} 行。", ""])
            continue
        old_path = root / old.get("artifact_file", "")
        if not old_path.is_file():
            lines.extend(["", "- 未找到上一版本 artifact，无法生成内容差异。", ""])
            continue
        if old.get("sha256") == item["sha256"]:
            lines.extend(["", "- 内容未变化；仅产生新的发布版本。", ""])
            continue
        lines.append("")
        lines.append(f"- 内容已变化：{old.get('rows', 'N/A')} 行 → {item.get('rows', 'N/A')} 行。")
        if current.suffix.lower() == ".csv" and old_path.suffix.lower() == ".csv":
            lines.extend(_csv_change_summary(old_path, current))
        else:
            lines.append("- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


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
    previous_manifest_path = output_dir / MANIFEST_NAME
    previous_manifest = json.loads(previous_manifest_path.read_text(encoding="utf-8")) if previous_manifest_path.is_file() else None
    batch_name, version = next_batch(artifacts_dir, today, artifact_slug(node))
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
    write_report(staging / REPORT_NAME, node, version, released_at, previous_manifest, deliverables, output_dir, root)
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
