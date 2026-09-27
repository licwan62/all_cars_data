#!/usr/bin/env python3
"""把 A0.尺码计算/output 的产线全量表（国别线 <国别>/全量/全量表.csv，店铺线 US/店铺/店铺全量_<店铺>.csv）按产线（data/产线.yaml：US、HNT、TM、TM_拆分、EU、RU）分别压缩为尺码表。

压缩引擎为内置的 src/sizechart（与网站流水线原压缩步骤同一算法，见 src/sizechart/VENDORED.md）：
按原子事实（品牌、车型、结构/CAB/BED、版本、年份）校验，非皮卡与皮卡分表输出。
默认交付仅保留 US、EU、RU 三个国别的高度压缩（有损）结果：
  <国别>/压缩尺码表.csv       非皮卡高度压缩（车型组合/版本/结构两两合并，逐次原子校验）
  <国别>/压缩尺码表_皮卡.csv  皮卡高度压缩
无损表和店铺产线仍可由压缩引擎在内存中生成、供校验和按需扩展，但不是 output 流水线接口。
运行先创建不可覆盖的 artifacts/<批次>/（输入与规则快照、压缩 log、原子事实表、原子检查问题），
全部产线成功后才原子更新 output/。
"""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
import re
import shutil
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "src" / "sizechart"))

import process_tsv as engine  # noqa: E402
from check_atom import build_atom_check  # noqa: E402
from field_profile import load_field_profile  # noqa: E402

UPSTREAM_OUTPUT = PROJECT_DIR.parent / "A0.尺码计算" / "output"
REGIONS = ("US", "EU", "RU")
DATA_DIR = PROJECT_DIR / "data"
FIELD_PROFILE = "字段映射.yaml"
MODEL_COMBO = "车型组合.tsv"
LINES_CONFIG = "产线.yaml"


class CompressionError(ValueError):
    pass


def upstream_file(line: str, region: str | None = None) -> str:
    """A0 output 中产线全量表的相对路径：国别线读区域全量表，店铺线读该区域的店铺全量表。"""
    region = region or line
    if line == region:
        return f"{region}/全量/全量表.csv"
    return f"{region}/店铺/店铺全量_{line}.csv"


def output_names(region: str) -> dict[str, str]:
    """默认交付物：按国别目录存放，文件名不再标注“有损”。"""
    return {
        "non_pickup_high": f"{region}/压缩尺码表.csv",
        "pickup_high": f"{region}/压缩尺码表_皮卡.csv",
    }


def load_lines(data_dir: Path = DATA_DIR) -> dict[str, str]:
    """产线 -> 区域（保持配置顺序）。"""
    config = yaml.safe_load((data_dir / LINES_CONFIG).read_text(encoding="utf-8")) or {}
    lines = {str(name): str((body or {}).get("区域", "")) for name, body in (config.get("产线") or {}).items()}
    bad = {name: region for name, region in lines.items() if region not in REGIONS}
    if not lines or bad:
        raise CompressionError(f"{LINES_CONFIG} 产线为空或区域无效：{bad}")
    return lines


def default_lines(lines: dict[str, str]) -> dict[str, str]:
    """默认仅交付国别产线；HNT/TM 等店铺产线不占用国别输出目录。"""
    return {line: region for line, region in lines.items() if line == region}


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


def compress_line(line: str, frame: pd.DataFrame, field_profile: dict, region: str | None = None, progress: bool = False) -> dict:
    """返回 {"tables": {键: DataFrame}, "log": DataFrame, "atoms": DataFrame, "checks": {类型: DataFrame}}。"""
    region = region or line
    if "DIMENSION-ID" in frame.columns:
        wrong_region = set(frame["DIMENSION-ID"].map(region_of)) - {region}
        if wrong_region:
            raise CompressionError(f"{upstream_file(line, region)} 含非 {region} 的 DIMENSION-ID：{sorted(wrong_region)}")
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
        raise CompressionError(f"{line} 没有可压缩的行（检查 最终尺码/年份区间 等字段映射）")

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
        "行数": {name: int(len(result["tables"][key])) for key, name in result["names"].items()},
        "原子事实数": int(len(result["atoms"])),
        "两两合并": dict(Counter(log["结果"])) if "结果" in log.columns else {},
        "fallback原因": dict(Counter(fallback["原因"].map(fallback_category))) if "原因" in fallback.columns else {},
        "原子检查": {kind: dict(Counter(check["检查结果"])) for kind, check in result["checks"].items()},
    }


def compress_file(line: str, path: Path, region: str, data_dir: Path, progress: bool = False) -> dict:
    """子进程入口：读取一条产线的全量表并压缩。"""
    field_profile = load_field_profile((data_dir / FIELD_PROFILE).resolve())
    return compress_line(line, read_frame(path), field_profile, region, progress)


def run(
    source_dir: Path = UPSTREAM_OUTPUT,
    data_dir: Path = DATA_DIR,
    output_dir: Path = PROJECT_DIR / "output",
    artifacts_dir: Path = PROJECT_DIR / "artifacts",
    progress: bool = False,
    workers: int = 0,
) -> dict:
    """workers：并行进程数，0 = 每条产线一个进程（上限 CPU 数），1 = 当前进程串行。"""
    lines = default_lines(load_lines(data_dir))
    inputs = {line: source_dir / upstream_file(line, lines[line]) for line in lines}
    for path in inputs.values():
        if not path.is_file():
            raise CompressionError(f"找不到输入文件：{path}")
    jobs = [(line, path, lines[line], data_dir, progress) for line, path in inputs.items()]
    workers = workers or min(len(jobs), os.cpu_count() or 1)
    if workers == 1:
        results = {job[0]: compress_file(*job) for job in jobs}
    else:
        # 每条产线独立进程：互不累积缓存状态，总耗时取决于最慢的产线
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {job[0]: executor.submit(compress_file, *job) for job in jobs}
            results = {line: future.result() for line, future in futures.items()}

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifact = next_artifact_dir(artifacts_dir, "compress-by-line")
    (artifact / "input").mkdir(parents=True)
    for path in inputs.values():
        snapshot = artifact / "input" / path.relative_to(source_dir)
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, snapshot)
    shutil.copy2(data_dir / FIELD_PROFILE, artifact / "input")
    shutil.copy2(data_dir / LINES_CONFIG, artifact / "input")
    shutil.copy2(engine.DEFAULT_MODEL_COMBO_PATH, artifact / "input" / MODEL_COMBO)  # 车型组合固定取自本节点 data/

    outputs: list[str] = []
    status_lines = {}
    for line, result in results.items():
        for key, name in result["names"].items():
            write_csv_atomic(artifact / "output" / name, result["tables"][key])
            outputs.append(name)
        log = result["log"]
        # 只留成功合并记录；fallback（数量大）按原因计数写入 status.json，完整 log 可重跑得到
        write_csv_atomic(artifact / f"压缩log_{line}.csv", log[log["结果"] == "success"] if "结果" in log.columns else log)
        write_csv_atomic(artifact / f"原子事实表_{line}.csv", result["atoms"])
        for kind, check in result["checks"].items():
            issues = check[check["检查结果"] != "OK"]
            if not issues.empty:
                write_csv_atomic(artifact / f"原子检查问题_{line}_{kind}.csv", issues)
        status_lines[line] = {"区域": lines[line], "上游输入": upstream_file(line, lines[line]), **summarize(result)}

    status = {"status": "passed", "lines": status_lines, "outputs": outputs}
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    for name in outputs:
        published = output_dir / name
        published.parent.mkdir(parents=True, exist_ok=True)
        staged = published.with_name(f".{published.name}.tmp")
        shutil.copy2(artifact / "output" / name, staged)
        os.replace(staged, published)

    return {**status, "artifact": str(artifact)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按产线把 A0 全量表压缩为尺码表（非皮卡/皮卡 × 无损/有损）")
    parser.add_argument("--source-dir", type=Path, default=UPSTREAM_OUTPUT)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--artifacts-dir", type=Path, default=PROJECT_DIR / "artifacts")
    parser.add_argument("--no-progress", action="store_true", help="不输出周期进度")
    parser.add_argument("--workers", type=int, default=0, help="并行进程数；0 = 每条产线一个（上限 CPU 数），1 = 串行")
    args = parser.parse_args(argv)
    try:
        result = run(
            args.source_dir.resolve(), args.data_dir.resolve(),
            args.output_dir.resolve(), args.artifacts_dir.resolve(),
            progress=not args.no_progress,
            workers=args.workers,
        )
    except CompressionError as error:
        print(f"运行失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
