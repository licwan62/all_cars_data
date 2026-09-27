#!/usr/bin/env python3
"""差评分析节点的编排入口。

正式输入只有 data/ 下人工维护的文件：
  - `差评分析汇总.csv`：逐条差评原始台账（唯一的原始数据）；
  - `差评分析表.csv`：人工按 品牌+车型+结构 汇总、评级的差评分析表；
  - `尺寸分析筛选规则.json`、`耳位筛选规则.json`：关键词信号规则。
运行不回写 data/：
1. 从原始台账筛出"车辆主体尺寸不合适"的差评（01 精选、02 待复核）和耳位相关差评（03 清单），
   这些核对清单只写进 artifacts/<批次>/，供人工据此维护 差评分析表.csv；
2. 按原始台账聚合 耳位分析表、皮卡驾驶室货斗分析表，并给差评分析表补上"尺码"（原始台账 实际尺寸）；
3. 校验差评分析表（键唯一、差评占比 0~1），通过后原子发布三张表到 output/。

本节点没有上游流水线节点。运行先创建不可覆盖的 artifacts/<批次>/，全部成功后才原子更新 output/。
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
RAW_REVIEW_NAME = "差评分析汇总.csv"
NEGATIVE_REVIEW_NAME = "差评分析表.csv"
FILTER_RULES_NAME = "尺寸分析筛选规则.json"
EAR_RULES_NAME = "耳位筛选规则.json"
REQUIRED_INPUTS = (RAW_REVIEW_NAME, NEGATIVE_REVIEW_NAME, FILTER_RULES_NAME, EAR_RULES_NAME)
SIZE_SUMMARY_NAME = "01.差评分析精选.csv"
SIZE_REVIEW_NAME = "02.尺寸问题复核表.csv"
EAR_DETAIL_NAME = "03.耳位问题清单.csv"
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
    missing = [name for name in REQUIRED_INPUTS if not (data_dir / name).is_file()]
    if missing:
        raise NegativeReviewError(f"data/ 缺少输入：{missing}")
    raw_table = data_dir / RAW_REVIEW_NAME
    negative_review_path = data_dir / NEGATIVE_REVIEW_NAME
    rules_path = data_dir / FILTER_RULES_NAME
    ear_rules_path = data_dir / EAR_RULES_NAME

    # 先快照本次运行读取的 data/，再计算；核对清单只写进本批次，不回写 data/。
    artifact = next_artifact_dir(artifacts_dir, "negative-review-analysis")
    (artifact / "input").mkdir(parents=True)
    for name in REQUIRED_INPUTS:
        shutil.copy2(data_dir / name, artifact / "input")

    filtered_count, review_count = summary_mod.build(
        raw_table, rules_path, artifact / SIZE_SUMMARY_NAME, negative_review_path, artifact / SIZE_REVIEW_NAME,
    )
    ear_summary_rows, ear_report = ear_mod.build(
        raw_table, ear_rules_path, negative_review_path, artifact / EAR_DETAIL_NAME,
    )
    cab_bed_rows, cab_bed_report = cab_bed_mod.build(raw_table, negative_review_path)

    rows = read_csv_rows(negative_review_path)
    fieldnames = list(rows[0].keys()) if rows else []
    size_report = add_sizes_from_raw_reviews(rows, read_csv_rows(raw_table))
    if SIZE_COLUMN not in fieldnames:
        insert_at = fieldnames.index("结构") + 1 if "结构" in fieldnames else len(fieldnames)
        fieldnames.insert(insert_at, SIZE_COLUMN)
    validation = validate_negative_review_table(rows)

    write_csv_atomic(artifact / "output" / OUTPUT_NAME, fieldnames, rows)
    write_csv_atomic(artifact / "output" / EAR_OUTPUT_NAME, list(ear_mod.SUMMARY_FIELDS), ear_summary_rows)
    write_csv_atomic(artifact / "output" / CAB_BED_OUTPUT_NAME, list(cab_bed_mod.SUMMARY_FIELDS), cab_bed_rows)

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
