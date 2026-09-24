#!/usr/bin/env python3
"""把 US/EU/RU 三个区域全量表汇总为 output/全量表_汇总.csv。

输入是上游 A0.尺码计算/output/ 下已发布的 全量表_US.csv、全量表_EU.csv、全量表_RU.csv；
每张表都必须带 DIMENSION-CODE（由 02.代码映射 提供）且 DIMENSION-ID 不跨区域重复。
汇总表列 = 各区域列的并集（区域独有列，如 RU 的 OZON尺码/发货尺码，在其他区域留空），
DIMENSION-CODE、DIMENSION-ID 固定为最后两列。

运行先创建不可覆盖的 artifacts/<批次>/，校验通过后才原子更新 output/。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
UPSTREAM_OUTPUT = PROJECT_DIR.parent / "A0.尺码计算" / "output"
TRIM_MAPPING = PROJECT_DIR / "output" / "尺寸TRIM映射.csv"
REGIONS = ("US", "EU", "RU")
TRIM_COLUMN = "Trims"
TAIL_COLUMNS = ["DIMENSION-CODE", "DIMENSION-ID"]
OUTPUT_NAME = "全量表_汇总.csv"


class ConsolidationError(ValueError):
    pass


def region_table_path(output_dir: Path, region: str) -> Path:
    return output_dir / f"全量表_{region}.csv"


def read_region_table(path: Path, region: str) -> pd.DataFrame:
    if not path.is_file():
        raise ConsolidationError(f"缺少 {region} 全量表：{path}")
    table = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = [column for column in TAIL_COLUMNS if column not in table.columns]
    if missing:
        raise ConsolidationError(f"{path.name} 缺少列 {missing}；请先用最新代码映射重跑该区域全量表")
    suffix = f" {region}"
    wrong = table.loc[~table["DIMENSION-ID"].str.endswith(suffix), "DIMENSION-ID"]
    if len(wrong):
        raise ConsolidationError(f"{path.name} 含非 {region} 的 DIMENSION-ID，例如：{wrong.head(3).tolist()}")
    return table


def consolidate(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    body_columns: list[str] = []
    for table in tables.values():
        for column in table.columns:
            if column not in TAIL_COLUMNS and column not in body_columns:
                body_columns.append(column)
    combined = pd.concat(
        [table.reindex(columns=[*body_columns, *TAIL_COLUMNS], fill_value="") for table in tables.values()],
        ignore_index=True,
    )
    if combined["DIMENSION-ID"].duplicated().any():
        raise ConsolidationError("汇总后 DIMENSION-ID 不唯一")
    return combined.sort_values("DIMENSION-ID", kind="stable").reset_index(drop=True)


def attach_trims(combined: pd.DataFrame, mapping_path: Path) -> tuple[pd.DataFrame, dict[str, int]]:
    if not mapping_path.is_file():
        raise ConsolidationError(f"缺少尺寸 TRIM 映射：{mapping_path}")
    mapping = pd.read_csv(mapping_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if not {"DIMENSION-ID", TRIM_COLUMN}.issubset(mapping.columns):
        raise ConsolidationError(f"{mapping_path.name} 缺少 DIMENSION-ID 或 {TRIM_COLUMN} 列")
    if mapping["DIMENSION-ID"].eq("").any() or mapping["DIMENSION-ID"].duplicated().any():
        raise ConsolidationError("尺寸 TRIM 映射的 DIMENSION-ID 为空或重复")
    if TRIM_COLUMN in combined.columns:
        raise ConsolidationError(f"区域全量表已包含 {TRIM_COLUMN} 列")
    values = mapping.set_index("DIMENSION-ID")[TRIM_COLUMN]
    us_mask = combined["DIMENSION-ID"].str.endswith(" US")
    combined.insert(len(combined.columns) - 2, TRIM_COLUMN, "")
    us_ids = combined.loc[us_mask, "DIMENSION-ID"].str.removesuffix(" US")
    combined.loc[us_mask, TRIM_COLUMN] = us_ids.map(values).fillna("").to_numpy()
    matched = int(us_ids.isin(values.index).sum())
    return combined, {"mapping_rows": len(mapping), "matched_us_rows": matched,
                      "nonempty_trims_rows": int(combined[TRIM_COLUMN].ne("").sum()),
                      "unmatched_us_rows": len(us_ids) - matched,
                      "mapping_ids_outside_us": int((~mapping["DIMENSION-ID"].isin(us_ids)).sum())}


def next_artifact_dir(artifacts_dir: Path, description: str) -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = [
        int(match.group(1))
        for path in artifacts_dir.glob(f"{prefix}*")
        if (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))
    ]
    return artifacts_dir / f"{prefix}{max(used, default=0) + 1:02d}_{description}"


def write_csv_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8-sig", lineterminator="\n")
    os.replace(temporary, path)


def run(
    source_dir: Path, output_dir: Path, artifacts_dir: Path, regions: tuple[str, ...] = REGIONS,
    trim_mapping: Path = TRIM_MAPPING,
) -> dict[str, object]:
    tables = {region: read_region_table(region_table_path(source_dir, region), region) for region in regions}
    combined = consolidate(tables)
    combined, trim_status = attach_trims(combined, trim_mapping)
    artifact = next_artifact_dir(artifacts_dir, "consolidated-full-table")
    (artifact / "input").mkdir(parents=True)
    for region in regions:
        shutil.copy2(region_table_path(source_dir, region), artifact / "input")
    shutil.copy2(trim_mapping, artifact / "input")
    write_csv_atomic(combined, artifact / "output" / OUTPUT_NAME)
    status = {
        "status": "passed",
        "regions": {region: len(table) for region, table in tables.items()},
        "rows": len(combined),
        "trim_lookup": trim_status,
        "output": OUTPUT_NAME,
    }
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    os.replace(
        _stage(artifact / "output" / OUTPUT_NAME, output_dir / OUTPUT_NAME),
        output_dir / OUTPUT_NAME,
    )
    return {**status, "artifact": str(artifact)}


def _stage(source: Path, destination: Path) -> Path:
    staged = destination.with_suffix(destination.suffix + ".tmp")
    shutil.copy2(source, staged)
    return staged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="汇总 US/EU/RU 全量表")
    parser.add_argument("--source-dir", type=Path, default=UPSTREAM_OUTPUT)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--artifacts-dir", type=Path, default=PROJECT_DIR / "artifacts")
    parser.add_argument("--trim-mapping", type=Path, default=TRIM_MAPPING)
    args = parser.parse_args(argv)
    try:
        result = run(args.source_dir.resolve(), args.output_dir.resolve(), args.artifacts_dir.resolve(), trim_mapping=args.trim_mapping.resolve())
    except ConsolidationError as error:
        print(f"汇总失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
