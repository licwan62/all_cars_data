from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CATALOG = ROOT / "source" / "catalog.json"


@dataclass
class Inspection:
    path: Path
    exists: bool
    rows: int | None = None
    columns: list[str] | None = None
    sha256: str | None = None
    errors: list[str] | None = None

    @property
    def ok(self) -> bool:
        return self.exists and not self.errors


def repository_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as error:
        raise ValueError(f"目录清单路径越出仓库：{value}") from error
    return path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def key_examples(fields: list[str], keys: list[tuple[str, ...]]) -> str:
    examples = []
    for key in keys[:3]:
        text = ", ".join(f"{field}={value}" for field, value in zip(fields, key))
        examples.append(text[:180] + ("…" if len(text) > 180 else ""))
    return "; ".join(examples)


def inspect_csv(path: Path, dataset: dict[str, Any]) -> Inspection:
    errors: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        if not columns:
            errors.append("没有表头")
        if len(columns) != len(set(columns)):
            errors.append("存在重复表头")
        missing = [item for item in dataset.get("required_columns", []) if item not in columns]
        if missing:
            errors.append(f"缺少字段：{', '.join(missing)}")
        key_fields = dataset.get("primary_key", [])
        keys: set[tuple[str, ...]] = set()
        duplicate_count = 0
        duplicate_keys: list[tuple[str, ...]] = []
        blank_count = 0
        blank_rows: list[int] = []
        row_count = 0
        for row_count, row in enumerate(reader, start=1):
            if key_fields:
                key = tuple((row.get(field) or "").strip() for field in key_fields)
                if all(not value for value in key):
                    blank_count += 1
                    if len(blank_rows) < 3:
                        blank_rows.append(row_count + 1)
                elif key in keys:
                    duplicate_count += 1
                    if key not in duplicate_keys and len(duplicate_keys) < 3:
                        duplicate_keys.append(key)
                else:
                    keys.add(key)
        if blank_count:
            errors.append(
                f"主键空值 {blank_count} 行（CSV 行号示例: "
                f"{', '.join(map(str, blank_rows))}）"
            )
        if duplicate_count:
            errors.append(
                f"主键重复 {duplicate_count} 行（示例: "
                f"{key_examples(key_fields, duplicate_keys)}）"
            )
    return Inspection(path, True, row_count, columns, file_sha256(path), errors)


def inspect_file(path: Path, dataset: dict[str, Any]) -> Inspection:
    if not path.is_file():
        return Inspection(path, False, errors=["文件不存在"])
    if dataset.get("format") == "csv":
        return inspect_csv(path, dataset)
    if dataset.get("format") == "xlsx" and not zipfile.is_zipfile(path):
        return Inspection(path, True, sha256=file_sha256(path), errors=["不是有效的 xlsx 文件"])
    return Inspection(path, True, sha256=file_sha256(path), errors=[])


def csv_keys(path: Path, fields: list[str]) -> set[tuple[str, ...]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [field for field in fields if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path} 缺少关联字段：{', '.join(missing)}")
        keys = {
            tuple((row.get(field) or "").strip() for field in fields)
            for row in reader
        }
        return {key for key in keys if any(key)}


def apply_key_reference(inspection: Inspection, dataset: dict[str, Any]) -> None:
    reference = dataset.get("key_reference")
    if not reference or not inspection.exists or inspection.path.suffix.lower() != ".csv":
        return
    own_keys = csv_keys(inspection.path, reference["fields"])
    reference_keys = csv_keys(
        repository_path(reference["path"]), reference["reference_fields"]
    )
    missing = reference_keys - own_keys
    extra = own_keys - reference_keys
    errors = inspection.errors if inspection.errors is not None else []
    if reference.get("relationship") == "exact" and missing:
        errors.append(
            f"关联主键缺失 {len(missing)} 个（示例: "
            f"{key_examples(reference['fields'], sorted(missing)[:3])}）"
        )
    if extra:
        errors.append(
            f"关联主键越界 {len(extra)} 个（示例: "
            f"{key_examples(reference['fields'], sorted(extra)[:3])}）"
        )
    inspection.errors = errors


def load_catalog(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    datasets = payload.get("datasets")
    if not isinstance(datasets, list):
        raise ValueError("source/catalog.json 缺少 datasets 数组")
    names = [item.get("name") for item in datasets]
    if len(names) != len(set(names)):
        raise ValueError("source/catalog.json 存在重复数据集名称")
    return datasets


def inspect_dataset(dataset: dict[str, Any]) -> tuple[Inspection, Inspection | None, str]:
    source = inspect_file(repository_path(dataset["path"]), dataset)
    apply_key_reference(source, dataset)
    candidate = None
    state = "无候选"
    if dataset.get("candidate"):
        candidate = inspect_file(repository_path(dataset["candidate"]), dataset)
        apply_key_reference(candidate, dataset)
        if not candidate.exists:
            state = "候选未生成"
        elif not candidate.ok:
            state = "候选不合格"
        elif source.sha256 == candidate.sha256:
            state = "已同步"
        else:
            source_columns = source.columns or []
            candidate_columns = candidate.columns or []
            if source_columns and source_columns != candidate_columns:
                state = "待发布（字段变化）"
            else:
                state = "待发布"
    return source, candidate, state


def print_status(datasets: list[dict[str, Any]], *, fail_on_error: bool) -> int:
    failed = False
    print(f"{'数据集':<18} {'源状态':<8} {'源行数':>8}  候选状态")
    print("-" * 72)
    for dataset in datasets:
        source, candidate, state = inspect_dataset(dataset)
        source_state = "正常" if source.ok else "异常"
        rows = "-" if source.rows is None else str(source.rows)
        print(f"{dataset['name']:<18} {source_state:<8} {rows:>8}  {state}")
        for error in source.errors or []:
            print(f"  source: {error}")
        for error in (candidate.errors if candidate else []) or []:
            print(f"  candidate: {error}")
        failed = failed or not source.ok or bool(candidate and candidate.exists and not candidate.ok)
    return 1 if fail_on_error and failed else 0


def publish_plan(datasets: list[dict[str, Any]], name: str) -> int:
    matches = [item for item in datasets if item["name"] == name]
    if not matches:
        print(f"未知数据集：{name}", file=sys.stderr)
        return 2
    dataset = matches[0]
    if not dataset.get("candidate"):
        print(f"{name} 没有可直接发布的项目候选，只能人工维护。", file=sys.stderr)
        return 2
    source, candidate, state = inspect_dataset(dataset)
    assert candidate is not None
    if not candidate.ok:
        print(f"候选未通过校验：{candidate.path}", file=sys.stderr)
        for error in candidate.errors or []:
            print(f"- {error}", file=sys.stderr)
        return 1
    schema_changed = bool(source.columns and source.columns != candidate.columns)
    if schema_changed and not dataset.get("allow_schema_change"):
        print("候选与 source 表头不一致，已阻止发布计划。", file=sys.stderr)
        return 1
    print(f"数据集：{name}")
    print(f"当前状态：{state}")
    print(f"候选：{candidate.path.relative_to(ROOT)}")
    print(f"目标：{source.path.relative_to(ROOT)}")
    if schema_changed:
        print("警告：本次会改变字段结构，请先确认所有下游项目已经兼容。")
    print("\n本工具不会覆盖 source。确认并备份后，由人工执行：")
    print(
        "Copy-Item -LiteralPath "
        f"'{candidate.path}' -Destination '{source.path}' -Force"
    )
    print("python data_workflow.py check")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查 source 真源及项目候选；永不自动覆盖 source")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="显示 source 与项目候选的同步状态")
    subparsers.add_parser("check", help="严格校验 source 和已生成候选")
    publish = subparsers.add_parser("publish-plan", help="校验候选并打印人工覆盖命令")
    publish.add_argument("dataset", help="catalog.json 中的数据集名称")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    try:
        datasets = load_catalog(args.catalog.resolve())
        if args.command == "publish-plan":
            return publish_plan(datasets, args.dataset)
        return print_status(datasets, fail_on_error=args.command == "check")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"数据工作流失败：{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
