#!/usr/bin/env python3
"""把 A1.全量生成/output/全量生成_{US,EU,RU}.csv 按区域分别压缩为尺码表。

压缩引擎为内置的 src/sizechart（与网站流水线原压缩步骤同一算法，见 src/sizechart/VENDORED.md）：
按原子事实（品牌、车型、结构/CAB/BED、版本、年份）校验，非皮卡与皮卡分表输出。
每个区域输出 4 张表：
  压缩尺码表_<区域>.csv            非皮卡无损（同事实连续年份合并）
  压缩尺码表_<区域>_有损.csv       非皮卡高度压缩（车型组合/版本/结构两两合并，逐次原子校验）
  压缩尺码表_<区域>_皮卡.csv       皮卡无损
  压缩尺码表_<区域>_皮卡_有损.csv  皮卡高度压缩
运行先创建不可覆盖的 artifacts/<批次>/（输入与规则快照、压缩 log、原子事实表、原子检查问题），
全部区域成功后才原子更新 output/。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "src" / "sizechart"))

import process_tsv as engine  # noqa: E402
from check_atom import build_atom_check  # noqa: E402
from field_profile import load_field_profile  # noqa: E402

UPSTREAM_OUTPUT = PROJECT_DIR.parent / "A1.全量生成" / "output"
REGIONS = ("US", "EU", "RU")
DATA_DIR = PROJECT_DIR / "data"
FIELD_PROFILE = "字段映射.yaml"
MODEL_COMBO = "车型组合.tsv"


class CompressionError(ValueError):
    pass


def upstream_file(region: str) -> str:
    return f"全量生成_{region}.csv"


def output_names(region: str) -> dict[str, str]:
    return {
        "non_pickup_lossless": f"压缩尺码表_{region}.csv",
        "non_pickup_high": f"压缩尺码表_{region}_有损.csv",
        "pickup_lossless": f"压缩尺码表_{region}_皮卡.csv",
        "pickup_high": f"压缩尺码表_{region}_皮卡_有损.csv",
    }


def region_of(dimension_id: str) -> str:
    token = dimension_id.rsplit(" ", 1)[-1] if dimension_id else ""
    return token if token in REGIONS else ""


def read_frame(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise CompressionError(f"找不到输入文件：{path}")
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig", keep_default_na=False)


def write_csv_atomic(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8-sig", lineterminator="\n")
    os.replace(temporary, path)


def next_artifact_dir(artifacts_dir: Path, description: str) -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = [
        int(match.group(1))
        for path in artifacts_dir.glob(f"{prefix}*")
        if (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))
    ]
    return artifacts_dir / f"{prefix}{max(used, default=0) + 1:02d}_{description}"


def export_or_empty(frame: pd.DataFrame, exporter, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns) if frame.empty else exporter(frame)


def compress_region(region: str, frame: pd.DataFrame, field_profile: dict, progress: bool = False) -> dict:
    """返回 {"tables": {键: DataFrame}, "log": DataFrame, "atoms": DataFrame, "checks": {类型: DataFrame}}。"""
    if "DIMENSION-ID" in frame.columns:
        wrong_region = set(frame["DIMENSION-ID"].map(region_of)) - {region}
        if wrong_region:
            raise CompressionError(f"{upstream_file(region)} 含其他区域的 DIMENSION-ID：{sorted(wrong_region)}")
    reporter = engine.ProgressReporter(interval_seconds=10.0, enabled=progress)
    non_lossless, _, non_high, pick_lossless, pick_high, log_df, atom_df = engine.transform_all_outputs(
        frame, progress=reporter, field_profile=field_profile
    )
    names = output_names(region)
    tables = {
        "non_pickup_lossless": export_or_empty(non_lossless, engine.export_non_pickup_table, engine.NON_PICKUP_EXPORT_COLUMNS),
        "non_pickup_high": export_or_empty(non_high, engine.export_non_pickup_table, engine.NON_PICKUP_EXPORT_COLUMNS),
        "pickup_lossless": export_or_empty(pick_lossless, engine.export_pickup_table, engine.PICKUP_EXPORT_COLUMNS),
        "pickup_high": export_or_empty(pick_high, engine.export_pickup_table, engine.PICKUP_EXPORT_COLUMNS),
    }
    if all(table.empty for table in tables.values()):
        raise CompressionError(f"{region} 没有可压缩的行（检查 最终尺码/年份区间 等字段映射）")

    atom_export = engine.export_table(atom_df)
    checks: dict[str, pd.DataFrame] = {}
    kinds = atom_export["压缩类型"].map(engine.normalize_text) if not atom_export.empty else pd.Series(dtype=str)
    if not tables["non_pickup_high"].empty:
        checks["非皮卡"] = build_atom_check(atom_export[kinds == "非皮卡"].copy(), tables["non_pickup_high"], progress=reporter, progress_phase="非皮卡原子检查")
    if not tables["pickup_high"].empty:
        checks["皮卡"] = build_atom_check(atom_export[kinds == "皮卡"].copy(), tables["pickup_high"], progress=reporter, progress_phase="皮卡原子检查")
    return {"names": names, "tables": tables, "log": engine.export_table(log_df), "atoms": atom_export, "checks": checks}


FALLBACK_REASONS = ("原子事实对应多条候选记录", "原子事实未被候选记录覆盖", "命中尺码", "原子事实命中不同尺码候选记录", "候选合并范围内没有可验证原子事实", "候选年份区间内存在同BED不同尺码事实")


def fallback_category(reason: str) -> str:
    return next((name for name in FALLBACK_REASONS if name in reason), reason)


def summarize(result: dict) -> dict:
    log = result["log"]
    fallback = log[log["结果"] == "fallback"] if "结果" in log.columns else log.iloc[0:0]
    return {
        "行数": {result["names"][key]: int(len(table)) for key, table in result["tables"].items()},
        "原子事实数": int(len(result["atoms"])),
        "两两合并": dict(Counter(log["结果"])) if "结果" in log.columns else {},
        "fallback原因": dict(Counter(fallback["原因"].map(fallback_category))) if "原因" in fallback.columns else {},
        "原子检查": {kind: dict(Counter(check["检查结果"])) for kind, check in result["checks"].items()},
    }


def run(
    source_dir: Path = UPSTREAM_OUTPUT,
    data_dir: Path = DATA_DIR,
    output_dir: Path = PROJECT_DIR / "output",
    artifacts_dir: Path = PROJECT_DIR / "artifacts",
    progress: bool = False,
) -> dict:
    field_profile = load_field_profile((data_dir / FIELD_PROFILE).resolve())
    inputs = {region: source_dir / upstream_file(region) for region in REGIONS}
    results = {region: compress_region(region, read_frame(path), field_profile, progress) for region, path in inputs.items()}

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifact = next_artifact_dir(artifacts_dir, "compress-by-region")
    (artifact / "input").mkdir(parents=True)
    for path in inputs.values():
        shutil.copy2(path, artifact / "input")
    shutil.copy2(data_dir / FIELD_PROFILE, artifact / "input")
    shutil.copy2(engine.DEFAULT_MODEL_COMBO_PATH, artifact / "input" / MODEL_COMBO)  # 车型组合固定取自本节点 data/

    outputs: list[str] = []
    status_regions = {}
    for region, result in results.items():
        for key, table in result["tables"].items():
            name = result["names"][key]
            write_csv_atomic(artifact / "output" / name, table)
            outputs.append(name)
        log = result["log"]
        # 只留成功合并记录；fallback（数量大）按原因计数写入 status.json，完整 log 可重跑得到
        write_csv_atomic(artifact / f"压缩log_{region}.csv", log[log["结果"] == "success"] if "结果" in log.columns else log)
        write_csv_atomic(artifact / f"原子事实表_{region}.csv", result["atoms"])
        for kind, check in result["checks"].items():
            issues = check[check["检查结果"] != "OK"]
            if not issues.empty:
                write_csv_atomic(artifact / f"原子检查问题_{region}_{kind}.csv", issues)
        status_regions[region] = {"上游输入": upstream_file(region), **summarize(result)}

    status = {"status": "passed", "regions": status_regions, "outputs": outputs}
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    for name in outputs:
        staged = output_dir / f".{name}.tmp"
        shutil.copy2(artifact / "output" / name, staged)
        os.replace(staged, output_dir / name)

    return {**status, "artifact": str(artifact)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按区域把 A1 全量表压缩为尺码表（非皮卡/皮卡 × 无损/有损）")
    parser.add_argument("--source-dir", type=Path, default=UPSTREAM_OUTPUT)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--artifacts-dir", type=Path, default=PROJECT_DIR / "artifacts")
    parser.add_argument("--no-progress", action="store_true", help="不输出周期进度")
    args = parser.parse_args(argv)
    try:
        result = run(
            args.source_dir.resolve(), args.data_dir.resolve(),
            args.output_dir.resolve(), args.artifacts_dir.resolve(),
            progress=not args.no_progress,
        )
    except CompressionError as error:
        print(f"运行失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
