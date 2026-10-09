#!/usr/bin/env python3
"""按 pipeline.json 对各节点做一次标准发布（自上游到下游）。

每个节点：
1. 交付物、上游输入（sha256）、本节点 data/ 规则快照、pending 与发布说明都与当前 manifest 相同时**不发布**，
   沿用原版本（``--force`` 除外）；
2. 否则新建不可覆盖的 ``artifacts/YYYY-MM-DD_NN_<node>-release/``，写 ``manifest.json`` 与 ``REPORT.md``；
3. 每个交付物的字节只存一次（见 ``artifact_refs``）：内容与上一版相同则引用上一版的 ``artifact_file``；
   与节点运行批次 ``run.json`` 登记的输出相同则引用运行批次文件；都没有才按 ``名称-YYYYMMDD_NN.扩展名``
   复制进本批次 ``output/``。只改了规则或上游的发布批次因此只有几 KB；
4. 全部校验通过后，原子写入节点 ``output/manifest.json``（``output/`` 的交付物本身就是发布内容）；
5. ``REPORT.md`` 说明发布原因，并将交付物与上一版本比较，记录 CSV 的新增、删除、字段修改及示例。

最后在仓库根目录写 ``release.json`` 汇总各节点当前版本与 artifact 来源，并重新生成 ``流水线状态.md``
（该状态文件只由本脚本写入）。

触发方式（``pipeline.json`` 的 ``line_triggers``）：默认只发布 auto 节点（上游与 A 线）；B/C/D/E/X 等按需节点
不随上游刷新，只在 ``--nodes``、``--lines`` 显式点名或 ``--all`` 时发布。

    python scripts/publish_release.py                       # 只发布 auto 节点
    python scripts/publish_release.py --nodes representative-model
    python scripts/publish_release.py --lines B,C           # 按线发布按需节点
    python scripts/publish_release.py --all                 # 包括全部按需节点
    python scripts/publish_release.py --nodes <id> --force  # 内容未变也新建发布批次
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
import time
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))  # 共享模块 rules_snapshot 在 lib/

from artifact_refs import RUN_RECORD, sha256, versioned_name
from pipeline_status import is_on_demand, write_status
from rules_snapshot import describe_changes, rules_changes, rules_snapshot  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "manifest.json"
REPORT_NAME = "REPORT.md"


class ReleaseError(ValueError):
    pass


def row_count(path: Path) -> int | None:
    if path.suffix.lower() not in {".csv", ".tsv"}:
        return None
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle, delimiter=delimiter)) - 1, 0)


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


def write_report(path: Path, node: dict, version: str, released_at: str, previous_manifest: dict | None, deliverables: list[dict], output_dir: Path, root: Path, rules: list[dict] | None = None, reasons: list[str] | None = None) -> None:
    """Write an auditable, compact Markdown description of this artifact's changes."""
    lines = [
        "# 发布报告", "",
        f"- 节点：`{node['id']}`（`{node['path']}`）",
        f"- 版本：`{version}`",
        f"- 发布时间：`{released_at}`",
        f"- 发布原因：{'；'.join(reasons or ['输出刷新'])}。", "",
    ]
    if rules is not None:
        lines.extend(["## 规则（data/）", ""])
        if previous_manifest is None or "rules" not in previous_manifest:
            lines.append(f"- 本版本首次记录规则快照，共 {len(rules)} 个文件。")
        else:
            changed = describe_changes(rules_changes(previous_manifest["rules"], rules))
            lines.append(f"- 相对上一版本：{changed}。" if changed else "- 与上一版本相同。")
        lines.append("")
    lines.extend(["## 交付物与变更", ""])
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
            lines.extend(["", f"- 内容未变化；引用 `{item['artifact_file']}`，未复制。", ""])
            continue
        lines.append("")
        lines.append(f"- 内容已变化：{old.get('rows', 'N/A')} 行 → {item.get('rows', 'N/A')} 行；存于 `{item['artifact_file']}`。")
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
                        "artifact_file": item.get("artifact_file") or f"{manifest['artifact']}/output/{item.get('versioned_file')}",
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


def replace_with_retry(source: Path, target: Path, attempts: int = 5, delay: float = 1.0) -> None:
    """Windows 上新写入的目录可能被杀毒/索引短暂占用，重命名失败时有限次重试。"""
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)


def _upstream_signature(records: list[dict]) -> list[tuple]:
    return sorted((record["node"], item["file"], item["sha256"]) for record in records for item in record.get("files", []))


def _reusable(root: Path, item: dict | None, digest: str) -> bool:
    """旧记录指向的 artifact 文件存在且内容就是 digest。"""
    if not item or item.get("sha256") != digest or not item.get("artifact_file") or not item.get("versioned_file"):
        return False
    source = root / item["artifact_file"]
    return source.is_file() and sha256(source) == digest


def run_batch_outputs(project: Path) -> dict[tuple[str, str], dict]:
    """节点运行批次 run.json 登记的成功输出：(文件, sha256) → 记录；同内容取最早批次（字节最先存在那里）。"""
    found: dict[tuple[str, str], dict] = {}
    for record_path in sorted((project / "artifacts").glob(f"*/{RUN_RECORD}")):
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if record.get("status", {}).get("status") != "passed":
            continue
        for item in record.get("outputs", []):
            found.setdefault((item["file"], item["sha256"]), item)
    return found


def release_reasons(previous: dict | None, deliverables: list[dict], upstream: list[dict], rules: list[dict], node: dict) -> list[str]:
    """与当前 manifest 比较，返回需要新建发布批次的原因；空表示无变化。"""
    if previous is None:
        return ["首次发布"]
    reasons = []
    old = {item["file"]: item["sha256"] for item in previous.get("deliverables", [])}
    new = {item["file"]: item["sha256"] for item in deliverables}
    if old != new:
        reasons.append("交付物变化：" + "、".join(sorted(name for name in old.keys() | new.keys() if old.get(name) != new.get(name))))
    if _upstream_signature(previous.get("upstream", [])) != _upstream_signature(upstream):
        reasons.append("上游输入变化")
    if "rules" not in previous:
        reasons.append("首次记录规则快照")
    elif previous["rules"] != rules:
        reasons.append(f"规则变化（{describe_changes(rules_changes(previous['rules'], rules))}）")
    if previous.get("pending", []) != node.get("pending", []) or previous.get("notes", []) != node.get("release_notes", []):
        reasons.append("pending/发布说明变化")
    return reasons


def release_node(root: Path, node: dict, by_id: dict[str, dict], today: str, released_at: str, force: bool = False) -> dict | None:
    """发布一个节点；交付物、上游、规则与说明均未变化且未 force 时返回 None，沿用当前版本。"""
    project = root / node["path"]
    output_dir = project / "output"
    artifacts_dir = project / "artifacts"
    previous_manifest_path = output_dir / MANIFEST_NAME
    previous_manifest = json.loads(previous_manifest_path.read_text(encoding="utf-8")) if previous_manifest_path.is_file() else None
    previous = {item["file"]: item for item in (previous_manifest or {}).get("deliverables", [])}

    current = []
    for name in node.get("outputs", []):
        published = output_dir / name
        current.append({"file": name, "sha256": sha256(published), "bytes": published.stat().st_size, "rows": row_count(published)})
    upstream = upstream_records(root, node, by_id)
    rules = rules_snapshot(project)
    reasons = release_reasons(previous_manifest, current, upstream, rules, node)
    if not reasons:
        if not force:
            return None
        reasons = ["--force 强制发布（内容未变化）"]

    artifacts_dir.mkdir(exist_ok=True)
    batch_name, version = next_batch(artifacts_dir, today, artifact_slug(node))
    batch_dir = artifacts_dir / batch_name
    staging = artifacts_dir / f".{batch_name}.tmp"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    run_outputs = run_batch_outputs(project)
    deliverables = []
    copied = []
    for item in current:
        name = item["file"]
        run_item = run_outputs.get((name, item["sha256"]))
        if _reusable(root, previous.get(name), item["sha256"]):
            source = previous[name]
        elif _reusable(root, run_item, item["sha256"]):
            source = run_item
        else:
            versioned = versioned_name(name, version)
            target = staging / "output" / versioned
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(output_dir / name, target)
            if sha256(target) != item["sha256"]:
                raise ReleaseError(f"{node['path']}: output/{name} 在发布过程中被改动")
            source = {"versioned_file": versioned, "artifact_file": f"{node['path']}/artifacts/{batch_name}/output/{versioned}"}
            copied.append(name)
        deliverables.append(
            {"file": name, "versioned_file": source["versioned_file"], "artifact_file": source["artifact_file"],
             "sha256": item["sha256"], "bytes": item["bytes"], "rows": item["rows"]}
        )
    manifest = {
        "schema_version": 1,
        "node": node["id"],
        "path": node["path"],
        "version": version,
        "artifact": f"{node['path']}/artifacts/{batch_name}",
        "published_at": released_at,
        "deliverables": deliverables,
        "upstream": upstream,
        "rules": rules,
        "pending": node.get("pending", []),
        "notes": node.get("release_notes", []),
    }
    write_report(staging / REPORT_NAME, node, version, released_at, previous_manifest, deliverables, output_dir, root, rules, reasons)
    write_json_atomic(staging / MANIFEST_NAME, manifest)
    replace_with_retry(staging, batch_dir)

    # output/ 的交付物本身就是发布内容（上面已按 sha256 与来源校验），无需回写。
    # 输出合同变化时只退役上一版 manifest 拥有、本版不再声明的稳定文件。
    current_files = {item["file"] for item in deliverables}
    for item in (previous_manifest or {}).get("deliverables", []):
        name = item.get("file")
        retired = output_dir / name if name else None
        if name and name not in current_files and retired and retired.is_file():
            retired.unlink()
    write_json_atomic(output_dir / MANIFEST_NAME, manifest)
    return {**manifest, "_copied": copied, "_reasons": reasons}


def select_nodes(payload: dict, nodes: list[dict], only: set[str] | None, lines: set[str] | None, include_on_demand: bool) -> list[dict]:
    """显式点名（only/lines）的节点不论触发方式都发布；否则只发布 auto 节点，include_on_demand 时全部发布。"""
    known_ids = {node["id"] for node in nodes}
    known_lines = {node.get("line", "U") for node in nodes}
    unknown = sorted((only or set()) - known_ids) + sorted((lines or set()) - known_lines)
    if unknown:
        raise ReleaseError(f"未知节点或产线：{', '.join(unknown)}")
    if only or lines:
        return [node for node in nodes if node["id"] in (only or set()) or node.get("line", "U") in (lines or set())]
    return [node for node in nodes if include_on_demand or not is_on_demand(payload, node)]


def release_all(root: Path, only: set[str] | None = None, dry_run: bool = False, lines: set[str] | None = None, include_on_demand: bool = False, force: bool = False) -> dict:
    payload = json.loads((root / "pipeline.json").read_text(encoding="utf-8"))
    nodes = topological_order(payload["nodes"])
    by_id = {node["id"]: node for node in payload["nodes"]}
    selected = select_nodes(payload, nodes, only, lines, include_on_demand)
    skipped = [node for node in nodes if node not in selected and is_on_demand(payload, node)]
    errors = check_outputs(root, selected)
    if errors:
        raise ReleaseError("\n".join(errors))
    now = datetime.now().astimezone()
    released: dict[str, dict] = {}
    for node in selected:
        if dry_run:
            print(f"[dry-run] {node['id']}: {len(node.get('outputs', []))} 个交付物")
            continue
        result = release_node(root, node, by_id, date.today().isoformat(), now.isoformat(timespec="seconds"), force)
        if result is None:
            print(f"{node['path']}: 未变化，沿用当前版本")
            continue
        copied, reasons = result.pop("_copied"), result.pop("_reasons")
        released[node["id"]] = result
        print(
            f"{node['path']}: {result['version']}  {len(result['deliverables'])} 个交付物（新存 {len(copied)}，其余引用），"
            f"pending {len(result['pending'])}；{'；'.join(reasons)}"
        )
    if skipped and not (only or lines):
        print("按需节点未发布（需要时用 --nodes/--lines/--all）：" + "、".join(node["path"] for node in skipped))
    if not dry_run and released:
        summary_path = root / "release.json"
        previous = json.loads(summary_path.read_text(encoding="utf-8-sig"))["nodes"] if summary_path.is_file() else {}
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
        write_status(root)
    return released


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", help="只发布这些节点 id（逗号分隔，可点名按需节点），默认发布全部 auto 节点")
    parser.add_argument("--lines", help="发布这些产线的全部节点（逗号分隔，如 B,C），可与 --nodes 合用")
    parser.add_argument("--all", action="store_true", help="默认发布时同时包括按需节点")
    parser.add_argument("--force", action="store_true", help="交付物、上游、规则均未变化也新建发布批次（交付物仍只引用不复制）")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status-only", action="store_true", help="不发布，只按当前各节点 manifest 重建 流水线状态.md")
    args = parser.parse_args(argv)
    if args.status_only:
        print(f"已更新 {write_status(ROOT).name}")
        return 0
    try:
        release_all(
            ROOT,
            set(args.nodes.split(",")) if args.nodes else None,
            args.dry_run,
            set(args.lines.split(",")) if args.lines else None,
            args.all,
            args.force,
        )
    except ReleaseError as error:
        print(f"发布失败：{error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
