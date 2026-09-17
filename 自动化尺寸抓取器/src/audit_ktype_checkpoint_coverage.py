#!/usr/bin/env python3
"""Audit Ktype coverage of batch checkpoints and optionally reopen bad successes."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any


TERMINAL_SUCCESS = "成功"
REOPENED_STATUS = "进行中"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    backup = path.with_suffix(path.suffix + ".coverage-audit.bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def expected_ktypes(checkpoint: dict[str, Any]) -> set[str]:
    state = checkpoint.get("ktype_state") or {}
    progress = state.get("ktype_progress") or {}
    return {str(value).strip() for value in progress if str(value).strip()}


def covered_ktypes(mapping_path: Path) -> set[str]:
    if not mapping_path.is_file():
        return set()
    with mapping_path.open(encoding="utf-8-sig", newline="") as handle:
        return {
            (row.get("Ktype") or "").strip()
            for row in csv.DictReader(handle, delimiter="\t")
            if (row.get("Ktype") or "").strip()
        }


def mapping_path_for(checkpoint_path: Path, checkpoint: dict[str, Any]) -> Path:
    state = checkpoint.get("ktype_state") or {}
    artifacts = state.get("artifacts") or {}
    configured = artifacts.get("current_mapping")
    if configured:
        configured_path = Path(str(configured))
        if configured_path.is_file():
            return configured_path
    return (
        checkpoint_path.parent
        / "task-state"
        / str(checkpoint.get("task_id", checkpoint_path.stem))
        / "current_mapping.tsv"
    )


def update_batch_progress(checkpoint_path: Path, task_id: str, missing: list[str]) -> bool:
    path = checkpoint_path.parent / "batch_progress.json"
    if not path.is_file():
        return False
    document = read_json(path)
    changed = False
    for task in document.get("batches", document.get("tasks", [])):
        if str(task.get("task_id")) != task_id:
            continue
        task["status"] = "pending"
        task["remarks"] = (
            f"Ktype 覆盖率审计重开：缺少 {len(missing)} 个 Ktype；"
            f"{','.join(missing)}"
        )
        changed = True
    if changed:
        batches = document.get("batches", [])
        pending_indexes = [
            int(item["index"])
            for item in batches
            if item.get("status") != "success" and "index" in item
        ]
        if pending_indexes:
            document["next_pending_index"] = min(pending_indexes)
        write_json(path, document)
    return changed


def audit(checkpoint_path: Path, apply: bool) -> dict[str, Any] | None:
    checkpoint = read_json(checkpoint_path)
    expected = expected_ktypes(checkpoint)
    if not expected:
        return None
    mapping_path = mapping_path_for(checkpoint_path, checkpoint)
    covered = covered_ktypes(mapping_path)
    missing = sorted(expected - covered, key=lambda item: (not item.isdigit(), int(item) if item.isdigit() else item))
    result = {
        "checkpoint": str(checkpoint_path),
        "task_id": str(checkpoint.get("task_id", checkpoint_path.stem)),
        "task_name": str(checkpoint.get("task_name", "")),
        "status": str(checkpoint.get("status", "")),
        "expected": len(expected),
        "covered": len(expected & covered),
        "coverage": len(expected & covered) / len(expected),
        "missing": missing,
        "mapping": str(mapping_path),
        "modified": False,
    }
    if apply and missing and checkpoint.get("status") == TERMINAL_SUCCESS:
        checkpoint["status"] = REOPENED_STATUS
        checkpoint["phase"] = "processing"
        checkpoint["remarks"] = (
            f"Ktype 覆盖率审计重开：缺少 {len(missing)} 个 Ktype；"
            f"{','.join(missing)}"
        )
        write_json(checkpoint_path, checkpoint)
        update_batch_progress(checkpoint_path, result["task_id"], missing)
        result["modified"] = True
    elif apply and missing and checkpoint.get("status") == REOPENED_STATUS:
        update_batch_progress(checkpoint_path, result["task_id"], missing)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, help="工作区目录，例如 workspaces/0802-eu")
    parser.add_argument("--apply", action="store_true", help="重开覆盖不全但状态为成功的 checkpoint")
    parser.add_argument("--all-statuses", action="store_true", help="报告所有状态；默认只报告成功 checkpoint")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出报告")
    args = parser.parse_args()

    checkpoint_paths = sorted((args.workspace / "checkpoints").glob("part-*/*.json"))
    results = []
    for path in checkpoint_paths:
        if path.name in {"batch_progress.json", "progress.json"} or path.name.endswith(".bak"):
            continue
        result = audit(path, args.apply)
        if result and (args.all_statuses or result["status"] == TERMINAL_SUCCESS):
            results.append(result)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            marker = "已重开" if result["modified"] else ("异常" if result["missing"] else "正常")
            print(
                f"[{marker}] {result['task_name']} status={result['status']} "
                f"coverage={result['covered']}/{result['expected']} "
                f"missing={','.join(result['missing']) or '-'}"
            )
        bad = sum(bool(item["missing"]) for item in results)
        changed = sum(bool(item["modified"]) for item in results)
        print(f"检查 {len(results)} 个 checkpoint；覆盖不全 {bad} 个；修改 {changed} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
