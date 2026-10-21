#!/usr/bin/env python3
"""结合上游差评分析表和耳位分析表，给每个 品牌+车型 打"定制需求度（通用版型偏离度）"评分。

2026-09-23 起评分粒度从 品牌+车型+结构 收窄为 品牌+车型，且只保留"差评"一个评分维度
（人工维护进度、车耳状态两个人工登记维度已删除，详见 src/scoring.py 顶部说明和 AGENTS.md
迁移记录）。耳位(普通/靠前/靠后) 现在完全来自上游 B0.差评分析/output/耳位分析表.csv，
按 品牌+车型 透传展示，不参与评分。

评分键（品牌+车型）直接从 A0.尺码计算/output/<国别>/全量/全量表.csv（US、EU、RU）的 MAKE/MODEL 推导，与
A1.压缩尺寸信息 的"结构池"压缩结果无关。

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

from src import scoring as scoring_mod

PROJECT_DIR = Path(__file__).resolve().parents[1]
UPSTREAM_FULL_TABLE_OUTPUT = PROJECT_DIR.parent / "A0.尺码计算" / "output"
UPSTREAM_FULL_TABLE_FILES = tuple(f"{region}/全量/全量表.csv" for region in ("US", "EU", "RU"))
UPSTREAM_NEGATIVE_REVIEW_OUTPUT = PROJECT_DIR.parent / "B0.差评分析" / "output"
UPSTREAM_NEGATIVE_REVIEW_FILE = "差评分析表.csv"
UPSTREAM_EAR_POSITION_OUTPUT = PROJECT_DIR.parent / "B0.差评分析" / "output"
UPSTREAM_EAR_POSITION_FILE = "耳位分析表.csv"
UPSTREAM_CAB_BED_OUTPUT = PROJECT_DIR.parent / "B0.差评分析" / "output"
UPSTREAM_CAB_BED_FILE = "皮卡驾驶室货斗分析表.csv"
DATA_DIR = PROJECT_DIR / "data"
SCORING_RULES = DATA_DIR / "定制评分规则.json"
EAR_REGISTRY = "车耳状态登记.csv"
SCORE_OUTPUT_NAME = "定制需求度评分.csv"

SCORE_FIELDS = ["品牌", "车型", "尺码", "差评评分", "定制需求等级", "差评备注", "耳位(普通/靠前/靠后)", "年份"]


class ScoringError(ValueError):
    pass


def read_csv_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise ScoringError(f"找不到输入文件：{path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path, default: dict) -> dict:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv_atomic(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def next_artifact_dir(artifacts_dir: Path, description: str) -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = [
        int(match.group(1))
        for path in artifacts_dir.glob(f"{prefix}*")
        if (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))
    ]
    return artifacts_dir / f"{prefix}{max(used, default=0) + 1:02d}_{description}"


def run(
    full_table_dir: Path = UPSTREAM_FULL_TABLE_OUTPUT,
    negative_review_dir: Path = UPSTREAM_NEGATIVE_REVIEW_OUTPUT,
    ear_position_dir: Path = UPSTREAM_EAR_POSITION_OUTPUT,
    cab_bed_dir: Path = UPSTREAM_CAB_BED_OUTPUT,
    data_dir: Path = DATA_DIR,
    output_dir: Path = PROJECT_DIR / "output",
    artifacts_dir: Path = PROJECT_DIR / "artifacts",
) -> dict:
    full_table_paths = [full_table_dir / name for name in UPSTREAM_FULL_TABLE_FILES]
    rows = [row for path in full_table_paths for row in read_csv_rows(path)]
    negative_review_path = negative_review_dir / UPSTREAM_NEGATIVE_REVIEW_FILE
    negative_review_rows = read_csv_rows(negative_review_path)
    ear_position_path = ear_position_dir / UPSTREAM_EAR_POSITION_FILE
    ear_position_rows = read_csv_rows(ear_position_path)
    cab_bed_path = cab_bed_dir / UPSTREAM_CAB_BED_FILE
    cab_bed_rows = read_csv_rows(cab_bed_path)

    keys = sorted({
        scoring_mod.ModelKey(row.get("MAKE", "").strip(), row.get("MODEL", "").strip())
        for row in rows if row.get("MAKE", "").strip() and row.get("MODEL", "").strip()
    })
    scoring_rules = load_json(data_dir / "定制评分规则.json", scoring_mod.DEFAULT_RULES)
    ear_registry_path = data_dir / EAR_REGISTRY
    ear_registry_rows = read_csv_rows(ear_registry_path) if ear_registry_path.is_file() else []
    try:
        scored_rows, scoring_meta = scoring_mod.score_keys(
            keys, negative_review_rows, ear_position_rows, cab_bed_rows, scoring_rules, ear_registry_rows,
        )
    except ValueError as error:
        raise ScoringError(str(error)) from error

    artifact = next_artifact_dir(artifacts_dir, "score")
    (artifact / "input").mkdir(parents=True)
    for path in full_table_paths:
        snapshot = artifact / "input" / path.relative_to(full_table_dir)
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, snapshot)
    shutil.copy2(negative_review_path, artifact / "input")
    shutil.copy2(ear_position_path, artifact / "input")
    shutil.copy2(cab_bed_path, artifact / "input")
    for rule_file in (data_dir / "定制评分规则.json", ear_registry_path):
        if rule_file.is_file():
            shutil.copy2(rule_file, artifact / "input")

    write_csv_atomic(artifact / "output" / SCORE_OUTPUT_NAME, SCORE_FIELDS, scored_rows)

    status = {
        "status": "passed",
        "上游全量表行数": len(rows),
        "上游差评分析表行数": len(negative_review_rows),
        "上游耳位分析表行数": len(ear_position_rows),
        "上游驾驶室货斗分析表行数": len(cab_bed_rows),
        "车耳状态登记行数": len(ear_registry_rows),
        "评分": scoring_meta,
        "outputs": [SCORE_OUTPUT_NAME],
    }
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    staged = (output_dir / SCORE_OUTPUT_NAME).with_suffix(".tmp")
    shutil.copy2(artifact / "output" / SCORE_OUTPUT_NAME, staged)
    os.replace(staged, output_dir / SCORE_OUTPUT_NAME)

    return {**status, "artifact": str(artifact)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="结合差评分析表/耳位分析表打定制需求度评分")
    parser.add_argument("--full-table-dir", type=Path, default=UPSTREAM_FULL_TABLE_OUTPUT)
    parser.add_argument("--negative-review-dir", type=Path, default=UPSTREAM_NEGATIVE_REVIEW_OUTPUT)
    parser.add_argument("--ear-position-dir", type=Path, default=UPSTREAM_EAR_POSITION_OUTPUT)
    parser.add_argument("--cab-bed-dir", type=Path, default=UPSTREAM_CAB_BED_OUTPUT)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--artifacts-dir", type=Path, default=PROJECT_DIR / "artifacts")
    args = parser.parse_args(argv)
    try:
        result = run(
            args.full_table_dir.resolve(), args.negative_review_dir.resolve(), args.ear_position_dir.resolve(),
            args.cab_bed_dir.resolve(), args.data_dir.resolve(), args.output_dir.resolve(),
            args.artifacts_dir.resolve(),
        )
    except ScoringError as error:
        print(f"运行失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
