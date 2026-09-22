#!/usr/bin/env python3
"""把 A1.全量生成/output/全量表_汇总.csv 按匹配尺码压缩年份/结构池，
并结合 data/ 里的三张人工维护表打出"定制需求度（通用版型偏离度）"评分。

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

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src import compress as compress_mod
from src import scoring as scoring_mod

PROJECT_DIR = Path(__file__).resolve().parent
UPSTREAM_OUTPUT = PROJECT_DIR.parent / "A1.全量生成" / "output"
UPSTREAM_FILE = "全量表_汇总.csv"
DATA_DIR = PROJECT_DIR / "data"
COMPRESS_CONFIG = DATA_DIR / "压缩配置.json"
SCORING_RULES = DATA_DIR / "定制评分规则.json"
STRUCTURE_MERGE_MAP = DATA_DIR / "结构归并映射.json"
NEGATIVE_REVIEW_TABLE = DATA_DIR / "差评分析表.csv"
MANUAL_PROGRESS_TABLE = DATA_DIR / "人工维护进度.csv"
EAR_STATUS_TABLE = DATA_DIR / "车耳状态登记.csv"
COMPRESSED_OUTPUT_NAME = "压缩尺码表.csv"
SCORE_OUTPUT_NAME = "定制需求度评分.csv"

COMPRESSED_FIELDS = ["区域", "MAKE", "MODEL", "结构池", "年份区间", "自动尺码", "变体数", "覆盖原子数"]
SCORE_FIELDS = [
    "品牌", "车型", "结构", "差评评分", "人工维护进度评分", "车耳状态评分",
    "综合定制需求度", "定制需求等级", "参与评分维度数",
]


class CompressionScoringError(ValueError):
    pass


def read_csv_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise CompressionScoringError(f"找不到输入文件：{path}")
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
    source_dir: Path = UPSTREAM_OUTPUT,
    data_dir: Path = DATA_DIR,
    output_dir: Path = PROJECT_DIR / "output",
    artifacts_dir: Path = PROJECT_DIR / "artifacts",
) -> dict:
    upstream_path = source_dir / UPSTREAM_FILE
    rows = read_csv_rows(upstream_path)

    compress_config = load_json(data_dir / "压缩配置.json", {"尺码字段": compress_mod.DEFAULT_SIZE_FIELD})
    compressed_rows, compress_meta = compress_mod.compress(rows, compress_config["尺码字段"])

    structure_merge_map = load_json(STRUCTURE_MERGE_MAP, {"映射": {}})["映射"]
    keys = sorted({
        scoring_mod.ModelKey(
            row.get("MAKE", "").strip(), row.get("MODEL", "").strip(),
            scoring_mod.canonicalize_structure(row.get("结构", "").strip(), structure_merge_map),
        )
        for row in rows if row.get("MAKE", "").strip() and row.get("MODEL", "").strip()
    })
    scoring_rules = load_json(data_dir / "定制评分规则.json", scoring_mod.DEFAULT_RULES)
    scored_rows, scoring_meta = scoring_mod.score_keys(
        keys,
        scoring_mod.read_csv_rows(data_dir / "差评分析表.csv"),
        scoring_mod.read_csv_rows(data_dir / "人工维护进度.csv"),
        scoring_mod.read_csv_rows(data_dir / "车耳状态登记.csv"),
        scoring_rules,
    )

    artifact = next_artifact_dir(artifacts_dir, "compress-and-score")
    (artifact / "input").mkdir(parents=True)
    shutil.copy2(upstream_path, artifact / "input")
    for table_path in (NEGATIVE_REVIEW_TABLE, MANUAL_PROGRESS_TABLE, EAR_STATUS_TABLE):
        if table_path.is_file():
            shutil.copy2(table_path, artifact / "input")
    for config_path in (COMPRESS_CONFIG, SCORING_RULES, STRUCTURE_MERGE_MAP):
        if config_path.is_file():
            shutil.copy2(config_path, artifact / "input")

    write_csv_atomic(artifact / "output" / COMPRESSED_OUTPUT_NAME, COMPRESSED_FIELDS, compressed_rows)
    write_csv_atomic(artifact / "output" / SCORE_OUTPUT_NAME, SCORE_FIELDS, scored_rows)

    status = {
        "status": "passed",
        "上游输入行数": len(rows),
        "压缩": compress_meta["report"],
        "评分": scoring_meta,
        "outputs": [COMPRESSED_OUTPUT_NAME, SCORE_OUTPUT_NAME],
    }
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if compress_meta["conflicts"]:
        (artifact / "冲突报告.json").write_text(
            json.dumps(compress_meta["conflicts"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    if compress_meta["skipped"]:
        (artifact / "跳过行报告.json").write_text(
            json.dumps(compress_meta["skipped"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    for name in (COMPRESSED_OUTPUT_NAME, SCORE_OUTPUT_NAME):
        staged = (output_dir / name).with_suffix(".tmp")
        shutil.copy2(artifact / "output" / name, staged)
        os.replace(staged, output_dir / name)

    return {**status, "artifact": str(artifact)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="压缩年份/结构池并打定制需求度评分")
    parser.add_argument("--source-dir", type=Path, default=UPSTREAM_OUTPUT)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--artifacts-dir", type=Path, default=PROJECT_DIR / "artifacts")
    args = parser.parse_args(argv)
    try:
        result = run(
            args.source_dir.resolve(), args.data_dir.resolve(),
            args.output_dir.resolve(), args.artifacts_dir.resolve(),
        )
    except CompressionScoringError as error:
        print(f"运行失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
