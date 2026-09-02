from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_git_csv(repo: Path, revision: str, relative_path: str) -> list[dict[str, str]]:
    content = subprocess.check_output(
        ["git", "show", f"{revision}:{relative_path}"], cwd=repo
    ).decode("utf-8-sig")
    return list(csv.DictReader(content.splitlines()))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive one immutable shape-review batch.")
    parser.add_argument("--batch", required=True, type=Path)
    before = parser.add_mutually_exclusive_group(required=True)
    before.add_argument("--before-revision")
    before.add_argument("--before-file", type=Path)
    parser.add_argument("--title", default="依据 reference.csv 的全量车形重核")
    args = parser.parse_args()

    project = Path(__file__).resolve().parents[1]
    repo = project.parent
    current_path = project / "artifacts" / "record_shape.csv"
    audit_path = project / "artifacts" / "all_dimension_shape_audit_2026-09-02.csv"
    audit_summary_path = project / "artifacts" / "all_dimension_shape_audit_2026-09-02.json"
    validation_path = project / "artifacts" / "validation_report.json"
    reference_path = project / "doc" / "reference.csv"
    relative_current = current_path.relative_to(repo).as_posix()

    current_rows = read_rows(current_path)
    if args.before_file:
        before_path = args.before_file.resolve()
        before_rows = read_rows(before_path)
        baseline = str(before_path)
    else:
        before_rows = read_git_csv(repo, args.before_revision, relative_current)
        baseline = f"{args.before_revision} 中的 `record_shape.csv`"
    current = {row["DIMENSION-ID"]: row["车形"] for row in current_rows}
    before = {row["DIMENSION-ID"]: row["车形"] for row in before_rows}

    changes: list[dict[str, str]] = []
    for dimension_id in sorted(before.keys() | current.keys()):
        old = before.get(dimension_id, "")
        new = current.get(dimension_id, "")
        if old == new:
            continue
        if not old:
            action = "ADD"
            reason = "上游规范快照新增或 DIMENSION-ID 重组，按新规则核定车形。"
        elif not new:
            action = "REMOVE"
            reason = "上游规范快照删除、合并或重组该 DIMENSION-ID。"
        else:
            action = "RECLASSIFY"
            reason = "依据新版 reference.csv 的车身号、真实轮廓及代际重新核定。"
        changes.append(
            {
                "ACTION": action,
                "DIMENSION-ID": dimension_id,
                "SHAPE_BEFORE": old,
                "SHAPE_AFTER": new,
                "REASON": reason,
            }
        )

    args.batch.mkdir(parents=True, exist_ok=False)
    shutil.copy2(current_path, args.batch / "correct.csv")
    write_csv(
        args.batch / "changes.csv",
        ["ACTION", "DIMENSION-ID", "SHAPE_BEFORE", "SHAPE_AFTER", "REASON"],
        changes,
    )
    shutil.copy2(audit_path, args.batch / "all_dimension_audit.csv")
    shutil.copy2(audit_summary_path, args.batch / "all_dimension_audit.json")
    shutil.copy2(validation_path, args.batch / "validation.json")
    shutil.copy2(reference_path, args.batch / "reference.csv")

    audit_summary = json.loads(audit_summary_path.read_text(encoding="utf-8-sig"))
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    action_counts = Counter(row["ACTION"] for row in changes)
    shape_counts = Counter(current.values())
    reference_rows = read_rows(reference_path)
    shape_order = [row["车身号"] for row in reference_rows]
    report = f"""# {args.title}

本批次以 `{baseline}` 为变更对比基线，以 `doc/reference.csv` 为车形定义唯一真源，将新版车身号落实到全部 `{len(current_rows):,}` 个 `DIMENSION-ID`。本轮未写入 `source` 目录。

## 核定规则

- 只允许输出 `reference.csv` 的 18 个车身号，旧数字编号全部废止。
- `H0/H1/H2/H3` 按低斜两厢、高方两厢、现代流线 Wagon、经典方正 Estate 重新拆分，不沿用旧 `20/21` 边界。
- Dodge Challenger 全系使用专用 `dodge-challenger`。
- Pickup 按 `DUAL > P2 > P1 > P0` 的例外优先级；SUV 按 `JP/SU2/SU0/SU1` 的真实轮廓核定。
- `STRUCTURE` 只用于定位真实分支，不能代替轮廓证据。
- 同车型同代际同外壳复用结论；源数据代际粒度不足且轮廓确有变化时细化到年份分支。

## 结果统计

- 全量结果：{len(current_rows):,} 条，唯一 ID {len(current):,} 个。
- 2000 年以前重点审计：{audit_summary['pre_2000_records_audited']:,} 条。
- 对比基线的增量记录：{len(changes):,} 条；`RECLASSIFY` {action_counts['RECLASSIFY']:,}，`ADD` {action_counts['ADD']:,}，`REMOVE` {action_counts['REMOVE']:,}。
- 车形分布：{', '.join(f'{key}={shape_counts[key]}' for key in shape_order)}。
- 历史编号残留：{len(audit_summary['legacy_shape_values_remaining'])}。
- 机器验收：{'PASS' if validation['passed'] else 'FAIL'}。

## 文件说明

- `correct.csv`：本批次完成时的全量 `DIMENSION-ID,车形` 快照。
- `changes.csv`：相对基线的实际新增、删除和改类。
- `all_dimension_audit.csv/json`：全 ID 逐条判定与摘要。
- `reference.csv`：本批次实际使用的规则源快照。
- `validation.json`：本批次机器验收结果。

## 保留风险

- 本轮 `RECLASSIFY` 同时包含定义等价的编号迁移和 `H*` 等边界重判；逐条原因以 `all_dimension_audit.csv` 为准。
- 新证据如推翻已核代际，应追加新批次，不覆盖本快照。
"""
    (args.batch / "report.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
