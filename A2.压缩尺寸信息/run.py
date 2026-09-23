#!/usr/bin/env python3
"""把 A0.尺码计算/output/全量表_{US,EU,RU}.csv 按区域分别压缩为结构池 × 年份区间。

每个区域独立输出无损表与有损表；运行先创建不可覆盖的 artifacts/<批次>/，
全部区域原子检查通过后才原子更新 output/。
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

PROJECT_DIR = Path(__file__).resolve().parent
UPSTREAM_OUTPUT = PROJECT_DIR.parent / "A0.尺码计算" / "output"
REGIONS = ("US", "EU", "RU")
DATA_DIR = PROJECT_DIR / "data"
COMPRESS_CONFIG = DATA_DIR / "压缩配置.json"

COMPRESSED_FIELDS = ["区域", "MAKE", "MODEL", "结构池", "年份区间", "自动尺码", "变体数", "覆盖原子数"]
LOSSY_FIELDS = COMPRESSED_FIELDS + ["扩张原子数"]


class CompressionError(ValueError):
    pass


def upstream_file(region: str) -> str:
    return f"全量表_{region}.csv"


def lossless_name(region: str) -> str:
    return f"压缩尺码表_{region}.csv"


def lossy_name(region: str) -> str:
    return f"压缩尺码表_{region}_有损.csv"


def read_csv_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise CompressionError(f"找不到输入文件：{path}")
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


def compress_region(region: str, rows: list[dict], size_field: str, max_gap_years: int) -> dict:
    wrong_region = {compress_mod.region_of(row.get("DIMENSION-ID", "")) for row in rows} - {region}
    if wrong_region:
        raise CompressionError(f"{upstream_file(region)} 含其他区域的 DIMENSION-ID：{sorted(wrong_region)}")
    result = compress_mod.compress_all(rows, size_field, max_gap_years)
    failed = {name: check for name, check in result["check"].items() if not check["通过"]}
    if failed:
        raise CompressionError(f"{region} 原子事实检查未通过：{json.dumps(failed, ensure_ascii=False)[:2000]}")
    return result


def run(
    source_dir: Path = UPSTREAM_OUTPUT,
    data_dir: Path = DATA_DIR,
    output_dir: Path = PROJECT_DIR / "output",
    artifacts_dir: Path = PROJECT_DIR / "artifacts",
) -> dict:
    config = load_json(data_dir / "压缩配置.json", {"尺码字段": compress_mod.DEFAULT_SIZE_FIELD})
    size_field = config["尺码字段"]
    max_gap = int(config.get("有损最大年份空洞", compress_mod.DEFAULT_MAX_GAP_YEARS))

    inputs = {region: source_dir / upstream_file(region) for region in REGIONS}
    results = {region: compress_region(region, read_csv_rows(path), size_field, max_gap) for region, path in inputs.items()}

    artifact = next_artifact_dir(artifacts_dir, "compress-by-region")
    (artifact / "input").mkdir(parents=True)
    for path in inputs.values():
        shutil.copy2(path, artifact / "input")
    if COMPRESS_CONFIG.is_file():
        shutil.copy2(COMPRESS_CONFIG, artifact / "input")

    outputs: list[str] = []
    status_regions = {}
    for region, result in results.items():
        for name, fields, table in (
            (lossless_name(region), COMPRESSED_FIELDS, result["lossless"]),
            (lossy_name(region), LOSSY_FIELDS, result["lossy"]),
        ):
            write_csv_atomic(artifact / "output" / name, fields, table)
            outputs.append(name)
        if result["conflicts"]:
            (artifact / f"冲突报告_{region}.json").write_text(
                json.dumps(result["conflicts"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        if result["skipped"]:
            (artifact / f"跳过行报告_{region}.json").write_text(
                json.dumps(result["skipped"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        status_regions[region] = {
            "上游输入": upstream_file(region),
            "压缩": result["report"],
            "原子检查": {name: {k: v for k, v in check.items() if k != "示例"} for name, check in result["check"].items()},
        }

    status = {"status": "passed", "regions": status_regions, "outputs": outputs}
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    for name in outputs:
        staged = (output_dir / name).with_suffix(".tmp")
        shutil.copy2(artifact / "output" / name, staged)
        os.replace(staged, output_dir / name)

    return {**status, "artifact": str(artifact)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按区域把 A0 全量表压缩为结构池 x 年份区间")
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
    except CompressionError as error:
        print(f"运行失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
