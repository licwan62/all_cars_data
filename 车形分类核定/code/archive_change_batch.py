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
    parser.add_argument("--title", default="全量 DIMENSION-ID 代际轮廓复核")
    args = parser.parse_args()

    project = Path(__file__).resolve().parents[1]
    repo = project.parent
    current_path = project / "artifacts" / "record_shape.csv"
    audit_path = project / "artifacts" / "all_dimension_shape_audit_2026-08-25.csv"
    audit_summary_path = project / "artifacts" / "all_dimension_shape_audit_2026-08-25.json"
    validation_path = project / "artifacts" / "validation_report.json"
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
            reason = "按实际轮廓和代际重核；结构名不作为 30/31/32 直接映射。"
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
    for source_name, target_name in (
        ("hatch_wagon_front_review_2026-08-25.json", "hatch_wagon_front_review.json"),
        ("classic_shape_review_2026-08-25.json", "classic_shape_review.json"),
        ("generation_shape_cache_review_2026-08-25.json", "generation_shape_review.json"),
    ):
        shutil.copy2(project / "artifacts" / source_name, args.batch / target_name)

    audit_summary = json.loads(audit_summary_path.read_text(encoding="utf-8-sig"))
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    action_counts = Counter(row["ACTION"] for row in changes)
    shape_counts = Counter(current.values())
    report = f"""# {args.title}

本批次以 `{baseline}` 为变更对比基线，以分类结构审核最新规范快照为输入，将车形规则落实到全部 `{len(current_rows):,}` 个 `DIMENSION-ID`。本轮未写入 `source` 目录。

## 核定规则

- `STRUCTURE` 只用于定位分支，不直接映射 `30/31/32`。
- 方形宽车头是 `32` 最高优先级特征；确认后不再与 `31` 比较。
- `31` 仅在排除方形宽车头后，按低矮、下宽上窄的实际比例核定。
- `20/21` 按车头收窄和前角轮廓逐代复核。
- 2000 年以前历史车型逐条审计，仅复用已独立核定的同代轮廓结论。

## 结果统计

- 全量结果：{len(current_rows):,} 条，唯一 ID {len(current):,} 个。
- 2000 年以前重点审计：{audit_summary['pre_2000_records_audited']:,} 条。
- 对比基线的增量记录：{len(changes):,} 条；`RECLASSIFY` {action_counts['RECLASSIFY']:,}，`ADD` {action_counts['ADD']:,}，`REMOVE` {action_counts['REMOVE']:,}。
- 车形分布：{', '.join(f'{key}={shape_counts[key]}' for key in sorted(shape_counts, key=lambda value: int(value)))}。
- 非独立代际的 3x 失败：{audit_summary['independent_generation_3x_failures']}。
- 机器验收：{'PASS' if validation['passed'] else 'FAIL'}。

## 文件说明

- `correct.csv`：本批次完成时的全量 `DIMENSION-ID,车形` 快照。
- `changes.csv`：相对基线的实际新增、删除和改类。
- `all_dimension_audit.csv/json`：全 ID 逐条判定与摘要。
- `hatch_wagon_front_review.json`：`20/21` 前脸边界复核。
- `classic_shape_review.json`：历史车型轮廓复核。
- `generation_shape_review.json`：`30/31/32` 代际缓存和结构直映射清理审计。
- `validation.json`：本批次机器验收结果。

## 保留风险

- `ADD/REMOVE` 中包含上游年份合并、结构原子化和 `DIMENSION-ID` 重组，不应解读为单纯车形改类。
- 新证据如推翻已核代际，应追加新批次，不覆盖本快照。
"""
    (args.batch / "report.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
