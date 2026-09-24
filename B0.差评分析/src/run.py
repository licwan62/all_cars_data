#!/usr/bin/env python3
"""差评分析节点的编排入口。

两步：
1. 用筛选规则从原始差评汇总（`data/00.差评分析汇总.csv`）里挑出"车辆主体尺寸不合适"的
   差评，写到 `data/01.差评分析精选.csv`（供人工核对）和 `data/02.尺寸问题复核表.csv`
   （疑似但无法自动判定的待人工复核记录）；同时给 `data/00.差评分析汇总.csv` 补上/刷新
   用于互相关联的主键列（差评汇总主键）。`data/差评分析表.csv` 是人工维护的文件，只读，
   本节点不写回；01 表用 品牌/车型/结构 三列直接记录匹配到的 差评分析表.csv 行，而不是另造
   一个哈希外键。
2. 校验人工维护的 `data/差评分析表.csv`（品牌+车型+结构 粒度的差评占比/严重度评级汇总），
   通过后原子发布为 `output/差评分析表.csv`，供下游节点（如 B1.压缩定制评分）读取。

本节点没有上游流水线节点：原始差评数据是人工导出维护的台账，不是别的节点产物。
车型语义修复（`data/车型语义修复映射.json`）是一次性的人工数据修正，用
`src/apply_model_semantic_repairs.py` 单独运行、直接改写 `data/00.差评分析汇总.csv`，
不属于本节点常规 run 流程。
运行先创建不可覆盖的 artifacts/<批次>/，校验通过后才原子更新 output/。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import build_size_analysis_summary as summary_mod
from src import build_ear_position_summary as ear_mod
from src import build_pickup_cab_bed_summary as cab_bed_mod

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
RAW_REVIEW_TABLE = DATA_DIR / "00.差评分析汇总.csv"
FILTER_RULES = DATA_DIR / "尺寸分析筛选规则.json"
SIZE_ANALYSIS_SUMMARY = DATA_DIR / "01.差评分析精选.csv"
SIZE_ANALYSIS_REVIEW = DATA_DIR / "02.尺寸问题复核表.csv"
EAR_POSITION_DETAIL = DATA_DIR / "03.耳位问题清单.csv"
EAR_POSITION_RULES = DATA_DIR / "耳位筛选规则.json"
NEGATIVE_REVIEW_TABLE = DATA_DIR / "差评分析表.csv"
OUTPUT_NAME = "差评分析表.csv"
EAR_OUTPUT_NAME = "耳位分析表.csv"
CAB_BED_OUTPUT_NAME = "皮卡驾驶室货斗分析表.csv"

KEY_COLUMNS = ("品牌", "车型", "结构")
SIZE_COLUMN = "尺码"


class NegativeReviewError(ValueError):
    pass


def read_csv_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise NegativeReviewError(f"找不到输入文件：{path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_atomic(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def validate_negative_review_table(rows: list[dict]) -> dict:
    """检查 品牌+车型+结构 键唯一，差评占比（如有）落在 0~1。"""
    seen: dict[tuple, int] = {}
    duplicates: list[dict] = []
    bad_ratios: list[dict] = []
    for row in rows:
        key = tuple((row.get(column) or "").strip() for column in KEY_COLUMNS)
        if not key[0] or not key[1]:
            continue
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            duplicates.append(dict(zip(KEY_COLUMNS, key)))
        ratio = (row.get("差评占比") or "").strip()
        if ratio:
            try:
                value = float(ratio)
            except ValueError:
                bad_ratios.append({"key": dict(zip(KEY_COLUMNS, key)), "差评占比": ratio})
            else:
                if not (0.0 <= value <= 1.0):
                    bad_ratios.append({"key": dict(zip(KEY_COLUMNS, key)), "差评占比": ratio})
    if duplicates:
        raise NegativeReviewError(f"差评分析表.csv 存在重复键（品牌+车型+结构）：{duplicates}")
    if bad_ratios:
        raise NegativeReviewError(f"差评分析表.csv 差评占比不是 0~1 的数值：{bad_ratios}")
    return {"行数": len(rows), "重复键数": len(duplicates), "差评占比异常数": len(bad_ratios)}


def add_sizes_from_raw_reviews(rows: list[dict], raw_rows: list[dict]) -> dict:
    """Fill 尺码 from the raw review table's 实际尺寸 field.

    Raw reviews are linked with the same conservative model matcher used by the
    size-review detail table.  Multiple observed sizes are retained in source
    order and de-duplicated instead of choosing one silently.
    """
    sizes_by_key: dict[tuple[str, str, str], list[str]] = {}
    for raw_row in raw_rows:
        size = (raw_row.get("实际尺寸") or "").strip()
        if not size:
            continue
        matched = summary_mod.match_analysis_row(raw_row, rows)
        if not matched:
            continue
        key = tuple((matched.get(column) or "").strip() for column in KEY_COLUMNS)
        values = sizes_by_key.setdefault(key, [])
        if size not in values:
            values.append(size)

    populated = 0
    for row in rows:
        key = tuple((row.get(column) or "").strip() for column in KEY_COLUMNS)
        row[SIZE_COLUMN] = "；".join(sizes_by_key.get(key, []))
        populated += bool(row[SIZE_COLUMN])
    return {"有尺码行数": populated, "无尺码行数": len(rows) - populated}


def next_artifact_dir(artifacts_dir: Path, description: str) -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = [
        int(match.group(1))
        for path in artifacts_dir.glob(f"{prefix}*")
        if (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))
    ]
    return artifacts_dir / f"{prefix}{max(used, default=0) + 1:02d}_{description}"


def run(
    data_dir: Path = DATA_DIR,
    output_dir: Path = PROJECT_DIR / "output",
    artifacts_dir: Path = PROJECT_DIR / "artifacts",
) -> dict:
    raw_table = data_dir / "00.差评分析汇总.csv"
    rules_path = data_dir / "尺寸分析筛选规则.json"
    size_summary_path = data_dir / "01.差评分析精选.csv"
    size_review_path = data_dir / "02.尺寸问题复核表.csv"
    ear_rules_path = data_dir / "耳位筛选规则.json"
    ear_detail_path = data_dir / "03.耳位问题清单.csv"
    negative_review_path = data_dir / "差评分析表.csv"

    # 先备份本次运行实际读取的人工维护输入（data/ 是唯一正式输入），再让 build() 就地刷新
    # data/00.差评分析汇总.csv 的主键列；这样 artifacts/<批次>/input 里留的是这次运行开始时
    # data/ 的真实状态，不是被本次运行自己改过之后的状态。
    artifact = next_artifact_dir(artifacts_dir, "negative-review-analysis")
    (artifact / "input").mkdir(parents=True)
    for source in (raw_table, rules_path, ear_rules_path, negative_review_path):
        if source.is_file():
            shutil.copy2(source, artifact / "input")

    filtered_count = review_count = None
    if raw_table.is_file() and rules_path.is_file() and negative_review_path.is_file():
        filtered_count, review_count = summary_mod.build(
            raw_table, rules_path, size_summary_path, negative_review_path, size_review_path,
        )

    ear_summary_rows: list[dict] = []
    ear_report: dict = {}
    if raw_table.is_file() and ear_rules_path.is_file() and negative_review_path.is_file():
        ear_summary_rows, ear_report = ear_mod.build(
            raw_table, ear_rules_path, negative_review_path, ear_detail_path,
        )

    cab_bed_rows: list[dict] = []
    cab_bed_report: dict = {}
    if raw_table.is_file() and negative_review_path.is_file():
        cab_bed_rows, cab_bed_report = cab_bed_mod.build(raw_table, negative_review_path)

    rows = read_csv_rows(negative_review_path)
    fieldnames = list(rows[0].keys()) if rows else []
    size_report = {"有尺码行数": 0, "无尺码行数": len(rows)}
    if raw_table.is_file():
        size_report = add_sizes_from_raw_reviews(rows, read_csv_rows(raw_table))
    if SIZE_COLUMN not in fieldnames:
        insert_at = fieldnames.index("结构") + 1 if "结构" in fieldnames else len(fieldnames)
        fieldnames.insert(insert_at, SIZE_COLUMN)
    validation = validate_negative_review_table(rows)

    write_csv_atomic(artifact / "output" / OUTPUT_NAME, fieldnames, rows)
    write_csv_atomic(artifact / "output" / EAR_OUTPUT_NAME, list(ear_mod.SUMMARY_FIELDS), ear_summary_rows)
    write_csv_atomic(artifact / "output" / CAB_BED_OUTPUT_NAME, list(cab_bed_mod.SUMMARY_FIELDS), cab_bed_rows)
    for extra_output in (size_summary_path, size_review_path, ear_detail_path):
        if extra_output.is_file():
            shutil.copy2(extra_output, artifact / extra_output.name)

    status = {
        "status": "passed",
        "尺寸问题差评筛选": filtered_count,
        "尺寸问题待复核": review_count,
        "耳位分析": ear_report,
        "驾驶室货斗分析": cab_bed_report,
        "差评分析表校验": validation,
        "尺码提取": size_report,
        "outputs": [OUTPUT_NAME, EAR_OUTPUT_NAME, CAB_BED_OUTPUT_NAME],
    }
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    for name in (OUTPUT_NAME, EAR_OUTPUT_NAME, CAB_BED_OUTPUT_NAME):
        staged = (output_dir / name).with_suffix(".tmp")
        shutil.copy2(artifact / "output" / name, staged)
        os.replace(staged, output_dir / name)

    return {**status, "artifact": str(artifact)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="筛选尺寸相关差评、校验并发布差评分析表")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--artifacts-dir", type=Path, default=PROJECT_DIR / "artifacts")
    args = parser.parse_args(argv)
    try:
        result = run(args.data_dir.resolve(), args.output_dir.resolve(), args.artifacts_dir.resolve())
    except NegativeReviewError as error:
        print(f"运行失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
