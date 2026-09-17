#!/usr/bin/env python3
"""Validate, merge and audit isolated multi-device fitment outputs."""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


MAPPING_NAME = "ktype_mapping_final.tsv"
DIMENSION_NAME = "dimension_groups_final.tsv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def portable_text_sha256(path: Path) -> str:
    """Hash logical UTF-8 text independent of BOM and checkout line endings."""
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def read_json(path: Path):
    candidates = (path, Path(f"{path}.bak"))
    errors = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            return json.loads(candidate.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # preserve the primary error for diagnostics
            errors.append(f"{candidate}: {exc}")
    if errors:
        raise ValueError("JSON 损坏且无法从备份恢复: " + "; ".join(errors))
    raise FileNotFoundError(f"文件不存在: {path}")


def write_text_atomic(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_table(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream, delimiter="\t"))
    if not rows or not rows[0] or not rows[0][0].strip():
        raise ValueError(f"空表或缺少表头: {path}")
    width = len(rows[0])
    for number, row in enumerate(rows[1:], 2):
        if len(row) != width:
            raise ValueError(f"列数不一致: {path}:{number}，期望 {width}，实际 {len(row)}")
    return rows[0], rows[1:]


def column_index(header, name, path):
    try:
        return header.index(name)
    except ValueError as exc:
        raise ValueError(f"缺少列 {name}: {path}") from exc


def sequence(group_id):
    match = re.match(r"^(.*-)(\d+)$", group_id)
    if match:
        return match.group(1), int(match.group(2)), max(2, len(match.group(2)))
    return f"{group_id}-", 1, 2


def validate_manifest(project_root: Path, manifest_path: Path, partition_count: int):
    manifest = read_json(manifest_path)
    version = manifest.get("version")
    if version not in (1, 2):
        raise ValueError(f"不支持的 manifest 版本: {manifest.get('version')}")
    if version == 2 and manifest.get("hash_mode") != "portable_utf8_lf_v1":
        raise ValueError(f"不支持的 manifest 哈希格式: {manifest.get('hash_mode')}")
    if manifest.get("partition_count") != partition_count:
        raise ValueError("manifest 分片数与命令行不一致")
    tasks = manifest.get("tasks") or []
    if len(tasks) != manifest.get("task_count"):
        raise ValueError("manifest.task_count 与 tasks 数量不一致")
    task_ids = [str(item.get("task_id", "")) for item in tasks]
    if not all(task_ids) or len(task_ids) != len(set(task_ids)):
        raise ValueError("manifest 含空或重复 task_id")
    for item in manifest.get("input_files") or []:
        path = project_root / Path(item["path"])
        if not path.is_file():
            raise FileNotFoundError(f"manifest 输入文件不存在: {path}")
        actual_hash = portable_text_sha256(path) if version == 2 else sha256(path)
        if actual_hash != item["sha256"]:
            raise ValueError(f"manifest 输入文件哈希不匹配: {path}")
    return manifest


def validate_completion(project_root: Path, manifest, allow_incomplete: bool):
    failures = []
    counts = {}
    for item in manifest["tasks"]:
        part = int(item["partition"])
        counts[part] = counts.get(part, 0) + 1
        checkpoint_value = item.get("checkpoint_path")
        checkpoint = (
            project_root / Path(checkpoint_value)
            if checkpoint_value
            else project_root / "checkpoints" / f"part-{part:02d}" / f"{item['task_id']}.json"
        )
        try:
            state = read_json(checkpoint)
        except Exception as exc:
            failures.append(f"{item['task_id']}: {exc}")
            continue
        if state.get("task_id") != item["task_id"] or state.get("status") != "成功":
            failures.append(
                f"{item['task_id']}: status={state.get('status')!r}, "
                f"checkpoint_task_id={state.get('task_id')!r}"
            )
    missing_parts = [part for part in range(1, manifest["partition_count"] + 1) if not counts.get(part)]
    if missing_parts:
        failures.append(f"manifest 中存在空分片: {missing_parts}")
    if failures and not allow_incomplete:
        preview = "\n  ".join(failures[:20])
        suffix = "" if len(failures) <= 20 else f"\n  ...另有 {len(failures) - 20} 项"
        raise ValueError(f"仍有 {len(failures)} 个任务未成功，拒绝生成最终表:\n  {preview}{suffix}")
    return failures


def merge_tables(table_root: Path, partition_count: int):
    mapping_header = dimension_header = None
    mappings = {}
    dimensions = {}
    mapping_sources = {}
    remaps = []

    for part in range(1, partition_count + 1):
        part_dir = table_root / f"part-{part:02d}"
        mapping_path = part_dir / MAPPING_NAME
        dimension_path = part_dir / DIMENSION_NAME
        for path in (mapping_path, dimension_path):
            if not path.is_file():
                raise FileNotFoundError(f"缺少分片 {part}/{partition_count} 的输出表: {path}")

        current_mapping_header, mapping_rows = read_table(mapping_path)
        current_dimension_header, dimension_rows = read_table(dimension_path)
        if mapping_header is None:
            mapping_header = current_mapping_header
            dimension_header = current_dimension_header
        elif current_mapping_header != mapping_header or current_dimension_header != dimension_header:
            raise ValueError(f"分片表头不一致: {part_dir}")

        mapping_id_index = column_index(mapping_header, "id", mapping_path)
        mapping_group_index = column_index(mapping_header, "DIMENSION_GROUP_ID", mapping_path)
        dimension_id_index = column_index(dimension_header, "DIMENSION_GROUP_ID", dimension_path)
        signature_indexes = [column_index(dimension_header, name, dimension_path) for name in ("LengthMM", "WidthMM", "HeightMM")]

        remap = {}
        seen_part_dimension_ids = set()
        for source_row in dimension_rows:
            row = list(source_row)
            original_id = row[dimension_id_index].strip()
            if not original_id or original_id in seen_part_dimension_ids:
                raise ValueError(f"分片内尺寸组主键为空或重复: {original_id!r} ({dimension_path})")
            seen_part_dimension_ids.add(original_id)
            signature = tuple(row[index].strip() for index in signature_indexes)
            target_id = original_id
            if original_id in dimensions:
                existing_signature = tuple(dimensions[original_id][index].strip() for index in signature_indexes)
                if signature != existing_signature:
                    prefix, number, width = sequence(original_id)
                    family = re.compile(rf"^{re.escape(prefix)}(\d+)$")
                    matching_id = None
                    maximum = number
                    for known_id, known_row in dimensions.items():
                        match = family.match(known_id)
                        if not match:
                            continue
                        maximum = max(maximum, int(match.group(1)))
                        known_signature = tuple(known_row[index].strip() for index in signature_indexes)
                        if matching_id is None and known_signature == signature:
                            matching_id = known_id
                    if matching_id:
                        target_id = matching_id
                    else:
                        while True:
                            maximum += 1
                            candidate = f"{prefix}{maximum:0{width}d}"
                            if candidate not in dimensions:
                                target_id = candidate
                                break
                    remap[original_id] = target_id
                    remaps.append({"partition": part, "original_id": original_id, "target_id": target_id, "dimensions": signature})
            row[dimension_id_index] = target_id
            if target_id not in dimensions:
                dimensions[target_id] = row

        for source_row in mapping_rows:
            row = list(source_row)
            mapping_id = row[mapping_id_index].strip()
            if not mapping_id:
                raise ValueError(f"映射主键为空: {mapping_path}")
            group_id = row[mapping_group_index].strip()
            if group_id in remap:
                row[mapping_group_index] = remap[group_id]
                group_id = remap[group_id]
            if group_id not in dimensions:
                raise ValueError(f"映射 {mapping_id!r} 引用了不存在的尺寸组 {group_id!r}: {mapping_path}")
            if mapping_id in mappings and mappings[mapping_id] != row:
                raise ValueError(f"跨分片映射主键冲突: {mapping_id!r}\n  {mapping_sources[mapping_id]}\n  {mapping_path}")
            mappings[mapping_id] = row
            mapping_sources[mapping_id] = mapping_path

    return mapping_header, list(mappings.values()), dimension_header, list(dimensions.values()), remaps


def audit(project_root: Path, manifest, mapping_header, mappings, dimension_header, dimensions, incomplete, remaps):
    mapping_ktype_index = column_index(mapping_header, "Ktype", MAPPING_NAME)
    mapping_group_index = column_index(mapping_header, "DIMENSION_GROUP_ID", MAPPING_NAME)
    dimension_id_index = column_index(dimension_header, "DIMENSION_GROUP_ID", DIMENSION_NAME)
    dimension_indexes = {name: column_index(dimension_header, name, DIMENSION_NAME) for name in ("LengthMM", "WidthMM", "HeightMM", "DimensionSource", "SourceURL")}

    input_ktypes = set()
    for item in manifest["input_files"]:
        input_path = project_root / Path(item["path"])
        header, rows = read_table(input_path)
        candidates = [index for index, value in enumerate(header) if value.casefold() == "ktype"]
        if len(candidates) != 1:
            raise ValueError(f"输入表必须恰好包含一个 Ktype 列: {input_path}")
        input_ktypes.update(row[candidates[0]].strip() for row in rows if row[candidates[0]].strip())

    output_ktypes = {row[mapping_ktype_index].strip() for row in mappings if row[mapping_ktype_index].strip()}
    dimension_ids = {row[dimension_id_index].strip() for row in dimensions}
    referenced_ids = {row[mapping_group_index].strip() for row in mappings}
    invalid_dimensions = []
    for row in dimensions:
        group_id = row[dimension_id_index].strip()
        for name in ("LengthMM", "WidthMM", "HeightMM"):
            value = row[dimension_indexes[name]].strip()
            try:
                if float(value) <= 0:
                    raise ValueError
            except ValueError:
                invalid_dimensions.append(f"{group_id}.{name}={value!r}")
        for name in ("DimensionSource", "SourceURL"):
            if not row[dimension_indexes[name]].strip():
                invalid_dimensions.append(f"{group_id}.{name}=空")

    missing_ktypes = sorted(input_ktypes - output_ktypes)
    unknown_ktypes = sorted(output_ktypes - input_ktypes)
    missing_groups = sorted(referenced_ids - dimension_ids)
    orphan_groups = sorted(dimension_ids - referenced_ids)
    passed = not any((incomplete, missing_ktypes, unknown_ktypes, missing_groups, orphan_groups, invalid_dimensions))
    return {
        "version": 1,
        "run_id": manifest["run_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "counts": {
            "manifest_tasks": manifest["task_count"],
            "incomplete_tasks": len(incomplete),
            "input_ktypes": len(input_ktypes),
            "output_ktypes": len(output_ktypes),
            "mapping_rows": len(mappings),
            "dimension_rows": len(dimensions),
            "dimension_id_remaps": len(remaps),
        },
        "issues": {
            "incomplete_tasks": incomplete,
            "missing_ktypes": missing_ktypes,
            "unknown_ktypes": unknown_ktypes,
            "missing_dimension_groups": missing_groups,
            "orphan_dimension_groups": orphan_groups,
            "invalid_dimensions": invalid_dimensions,
        },
        "dimension_id_remaps": remaps,
    }


def write_table_atomic(path: Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--table-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--partition-count", type=int, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    if args.partition_count < 2:
        raise ValueError("partition-count 必须大于等于 2")

    project_root = args.project_root.resolve()
    table_root = args.table_root.resolve()
    manifest = validate_manifest(project_root, args.manifest.resolve(), args.partition_count)
    incomplete = validate_completion(project_root, manifest, args.allow_incomplete)
    mapping_header, mappings, dimension_header, dimensions, remaps = merge_tables(table_root, args.partition_count)
    report = audit(project_root, manifest, mapping_header, mappings, dimension_header, dimensions, incomplete, remaps)
    report_json = json.dumps(report, ensure_ascii=False, indent=2)
    report_text = "\n".join([
        f"run_id: {report['run_id']}",
        f"审计结果: {'通过' if report['passed'] else '失败'}",
        *(f"{key}: {value}" for key, value in report["counts"].items()),
        *(f"{key}: {len(value)}" for key, value in report["issues"].items()),
        "",
    ])
    write_text_atomic(table_root / "audit_report.json", report_json + "\n")
    write_text_atomic(table_root / "audit_report.txt", report_text)
    if not report["passed"] and not args.allow_incomplete:
        raise ValueError(f"最终审计未通过，详见 {table_root / 'audit_report.json'}")

    write_table_atomic(table_root / DIMENSION_NAME, dimension_header, dimensions)
    write_table_atomic(table_root / MAPPING_NAME, mapping_header, mappings)
    merge_manifest = {
        "version": 1,
        "run_id": manifest["run_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "partial": not report["passed"],
        "files": {
            MAPPING_NAME: {"rows": len(mappings), "sha256": sha256(table_root / MAPPING_NAME)},
            DIMENSION_NAME: {"rows": len(dimensions), "sha256": sha256(table_root / DIMENSION_NAME)},
            "audit_report.json": {"sha256": sha256(table_root / "audit_report.json")},
        },
    }
    write_text_atomic(table_root / "merge_manifest.json", json.dumps(merge_manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"最终审计: {'通过' if report['passed'] else '部分汇总'}")
    print(f"已汇总 Ktype 映射 {len(mappings)} 行: {table_root / MAPPING_NAME}")
    print(f"已汇总尺寸组 {len(dimensions)} 行: {table_root / DIMENSION_NAME}")
    print(f"已协调跨设备尺寸组 ID 冲突 {len(remaps)} 个")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"分片汇总失败: {exc}", file=sys.stderr)
        raise SystemExit(2)
