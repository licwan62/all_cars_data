#!/usr/bin/env python3
"""按自动尺码生成宽高统计、极值车型和尺寸异常清单。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_DIR / "output" / "全量表_汇总.csv"
DEFAULT_CONFIG = PROJECT_DIR / "data" / "dimension_stats_config.json"
DEFAULT_OUTPUT = PROJECT_DIR / "output"
DEFAULT_ARTIFACTS = PROJECT_DIR / "artifacts"

STATS_NAME = "尺码宽高统计.csv"
EXTREMES_NAME = "尺码宽高极值车型.csv"
OUTLIERS_NAME = "尺码尺寸异常.csv"
OUTPUT_NAMES = (STATS_NAME, EXTREMES_NAME, OUTLIERS_NAME)
REQUIRED_COLUMNS = {"自动尺码", "W-MM", "H-MM", "DIMENSION-ID"}
REGIONS = ("US", "EU", "RU")


class DimensionStatisticsError(ValueError):
    pass


def read_config(path: Path) -> dict[str, object]:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {"excluded_sizes", "iqr_multiplier", "zscore_threshold", "variance_ddof"}
    missing = required - set(config)
    if missing:
        raise DimensionStatisticsError(f"配置缺少字段: {sorted(missing)}")
    if config["variance_ddof"] != 0:
        raise DimensionStatisticsError("当前交付口径要求总体方差 variance_ddof=0")
    return config


def prepare_source(path: Path, excluded_sizes: list[str]) -> pd.DataFrame:
    source = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = REQUIRED_COLUMNS - set(source.columns)
    if missing:
        raise DimensionStatisticsError(f"输入缺少字段: {sorted(missing)}")
    source = source.loc[
        source["自动尺码"].ne("") & ~source["自动尺码"].isin(excluded_sizes)
    ].copy()
    for column in ("W-MM", "H-MM"):
        source[column] = pd.to_numeric(source[column], errors="coerce")
    invalid = source[["W-MM", "H-MM"]].isna().any(axis=1) | source[["W-MM", "H-MM"]].le(0).any(axis=1)
    if invalid.any():
        examples = source.loc[invalid, "DIMENSION-ID"].head(5).tolist()
        raise DimensionStatisticsError(f"有效尺码记录存在非正或空宽高: {examples}")
    source.insert(0, "区域", source["DIMENSION-ID"].str.extract(r" (US|EU|RU)$", expand=False))
    missing_region = source["区域"].isna()
    if missing_region.any():
        examples = source.loc[missing_region, "DIMENSION-ID"].head(5).tolist()
        raise DimensionStatisticsError(f"DIMENSION-ID 缺少 US/EU/RU 区域后缀: {examples}")
    return source


def build_statistics(source: pd.DataFrame, ddof: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (region, size), group in source.groupby(["区域", "自动尺码"], sort=True):
        row: dict[str, object] = {"区域": region, "自动尺码": size, "车型数": len(group)}
        for column, label in (("W-MM", "宽"), ("H-MM", "高")):
            values = group[column]
            row.update({
                f"{label}最小-MM": values.min(),
                f"{label}最大-MM": values.max(),
                f"{label}平均-MM": values.mean(),
                f"{label}中位数-MM": values.median(),
                f"{label}方差-MM2": values.var(ddof=ddof),
            })
        rows.append(row)
    return pd.DataFrame(rows)


def build_extremes(source: pd.DataFrame) -> pd.DataFrame:
    identity = [column for column in ("MAKE", "MODEL", "TRIM", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类", "L-MM", "W-MM", "H-MM", "DIMENSION-CODE", "DIMENSION-ID") if column in source.columns]
    rows: list[dict[str, object]] = []
    for (region, size), group in source.groupby(["区域", "自动尺码"], sort=True):
        for column, metric in (("W-MM", "最宽"), ("H-MM", "最高")):
            extreme = group[column].max()
            tied = group.loc[group[column].eq(extreme), identity].sort_values("DIMENSION-ID", kind="stable")
            for _, vehicle in tied.iterrows():
                rows.append({"区域": region, "自动尺码": size, "指标": metric, "极值-MM": extreme, **vehicle.to_dict()})
    return pd.DataFrame(rows)


def build_outliers(source: pd.DataFrame, iqr_multiplier: float, zscore_threshold: float) -> pd.DataFrame:
    output_rows: list[dict[str, object]] = []
    source_columns = [column for column in ("MAKE", "MODEL", "TRIM", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类", "L-MM", "W-MM", "H-MM", "自动尺码", "DIMENSION-CODE", "DIMENSION-ID") if column in source.columns]
    for (region, size), group in source.groupby(["区域", "自动尺码"], sort=True):
        calculated: dict[str, pd.Series | float] = {}
        for column, label in (("W-MM", "宽"), ("H-MM", "高")):
            values = group[column]
            q1, q3 = values.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower, upper = q1 - iqr_multiplier * iqr, q3 + iqr_multiplier * iqr
            mean, std = values.mean(), values.std(ddof=0)
            z = (values - mean) / std if std else pd.Series(0.0, index=values.index)
            calculated.update({
                f"{label}IQR下界": lower, f"{label}IQR上界": upper,
                f"{label}均值": mean, f"{label}标准差": std, f"{label}Z分数": z,
                f"{label}IQR异常": values.lt(lower) | values.gt(upper),
                f"{label}3σ异常": z.abs().ge(zscore_threshold),
            })
        mask = calculated["宽IQR异常"] | calculated["宽3σ异常"] | calculated["高IQR异常"] | calculated["高3σ异常"]
        for index, vehicle in group.loc[mask, source_columns].iterrows():
            reasons = []
            for label in ("宽", "高"):
                if bool(calculated[f"{label}IQR异常"].loc[index]):
                    reasons.append(f"{label}超出{iqr_multiplier:g}×IQR")
                if bool(calculated[f"{label}3σ异常"].loc[index]):
                    reasons.append(f"{label}|z|≥{zscore_threshold:g}")
            output_rows.append({
                "区域": region,
                **vehicle.to_dict(),
                "异常原因": "；".join(reasons),
                "宽IQR下界-MM": calculated["宽IQR下界"], "宽IQR上界-MM": calculated["宽IQR上界"],
                "宽Z分数": calculated["宽Z分数"].loc[index],
                "高IQR下界-MM": calculated["高IQR下界"], "高IQR上界-MM": calculated["高IQR上界"],
                "高Z分数": calculated["高Z分数"].loc[index],
            })
    return pd.DataFrame(output_rows).sort_values(["区域", "自动尺码", "DIMENSION-ID"], kind="stable").reset_index(drop=True)


def next_artifact(artifacts_dir: Path) -> tuple[Path, str]:
    day = date.today().isoformat()
    used = []
    for path in artifacts_dir.glob(f"{day}_*"):
        match = re.match(rf"^{re.escape(day)}_(\d{{2}})_", path.name)
        if match:
            used.append(int(match.group(1)))
    number = max(used, default=0) + 1
    return artifacts_dir / f"{day}_{number:02d}_dimension-statistics", f"{day.replace('-', '')}_{number:02d}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n", float_format="%.4f")


def run(input_path: Path, config_path: Path, output_dir: Path, artifacts_dir: Path) -> dict[str, object]:
    config = read_config(config_path)
    source = prepare_source(input_path, list(config["excluded_sizes"]))
    frames = {
        STATS_NAME: build_statistics(source, int(config["variance_ddof"])),
        EXTREMES_NAME: build_extremes(source),
        OUTLIERS_NAME: build_outliers(source, float(config["iqr_multiplier"]), float(config["zscore_threshold"])),
    }
    group_count = source[["区域", "自动尺码"]].drop_duplicates().shape[0]
    if len(frames[STATS_NAME]) != group_count:
        raise DimensionStatisticsError("统计表区域尺码组合数校验失败")
    artifact, version = next_artifact(artifacts_dir)
    staging = artifacts_dir / f".{artifact.name}.tmp"
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "input").mkdir(parents=True)
    (staging / "rules").mkdir()
    (staging / "output").mkdir()
    shutil.copy2(input_path, staging / "input" / input_path.name)
    shutil.copy2(config_path, staging / "rules" / config_path.name)
    deliverables = []
    for name, frame in frames.items():
        stem, suffix = Path(name).stem, Path(name).suffix
        versioned = f"{stem}-{version}{suffix}"
        target = staging / "output" / versioned
        write_csv(frame, target)
        deliverables.append({"file": name, "artifact_file": f"output/{versioned}", "rows": len(frame), "sha256": sha256(target)})
    status = {
        "status": "passed", "version": version, "source_rows": len(source),
        "sizes": source["自动尺码"].nunique(), "region_size_groups": group_count,
        "regions": source["区域"].value_counts().sort_index().to_dict(), "deliverables": deliverables,
        "method": {"variance": "population", "outlier": f"{config['iqr_multiplier']}×IQR or |z|≥{config['zscore_threshold']}"},
    }
    (staging / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    os.replace(staging, artifact)
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in deliverables:
        source_path = artifact / item["artifact_file"]
        destination = output_dir / item["file"]
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        shutil.copy2(source_path, temporary)
        os.replace(temporary, destination)
    return {**status, "artifact": str(artifact)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args(argv)
    result = run(args.input.resolve(), args.config.resolve(), args.output_dir.resolve(), args.artifacts_dir.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
