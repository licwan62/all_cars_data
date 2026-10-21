"""Create the slimmed W-car release from the new-size-code artifact.

This does not rerun clustering, year merging or allocation.  It copies 0915.4,
backfills the atom and check rows that 0915.3 left out when it appended the
Challenger and Model X custom SKUs (taken from 0915.1, where those clusters were
built), then applies the same slimming, validation and report as ``run.py``.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from run import read_csv, read_table, slim_release, validate_release, write_report, write_table


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "artifacts" / "0915.4-new-size-codes"
CUSTOM = ROOT / "artifacts" / "0915.1-tolerance-550"
TARGET = ROOT / "artifacts" / "0915.5-slim-new-size-codes"
CUSTOM_SIZES = {"CHALLENGER", "MODEL-X"}
BACKFILL = {
    Path("02_聚类数据/聚类原子明细.csv"): "CLUSTER_ID",
    Path("02_聚类数据/聚类ID映射.csv"): "原聚类ID",
    Path("04_校验报告/聚类合并校验.csv"): "原聚类ID",
    Path("04_校验报告/年份合并校验.csv"): "聚类ID",
}


def backfill_custom_rows() -> None:
    master = read_csv(TARGET / "02_聚类数据" / "聚类主表.csv")
    custom_ids = {row["聚类ID"] for row in master if row["逻辑尺码"] in CUSTOM_SIZES}
    if len(custom_ids) != len(CUSTOM_SIZES):
        raise ValueError(f"主表中的定制尺码聚类数量不对：{sorted(custom_ids)}")
    for relative, id_column in BACKFILL.items():
        columns, rows = read_table(TARGET / relative)
        if custom_ids & {row[id_column] for row in rows}:
            raise ValueError(f"{relative} 已含定制尺码行，无需补齐")
        source_columns, source_rows = read_table(CUSTOM / relative)
        if source_columns != columns:
            raise ValueError(f"{relative} 在 {CUSTOM.name} 中的列与当前批次不同")
        added = [row for row in source_rows if row[id_column] in custom_ids]
        if {row[id_column] for row in added} != custom_ids:
            raise ValueError(f"{CUSTOM.name}/{relative} 缺少定制尺码行")
        write_table(TARGET / relative, columns, rows + added)


def main() -> None:
    if TARGET.exists():
        if "--replace" not in sys.argv:
            raise FileExistsError(f"refusing to overwrite existing artifact: {TARGET}")
        if TARGET.parent != ROOT / "artifacts" or TARGET.name != "0915.5-slim-new-size-codes":
            raise RuntimeError(f"unexpected replacement target: {TARGET}")
        shutil.rmtree(TARGET)
    shutil.copytree(SOURCE, TARGET)
    renames = read_csv(TARGET / "00_输入" / "新旧尺码映射.csv")
    # 配额输入是旧汇总的派生副本（且未含定制 SKU），01 的汇总与 05 逐字节相同，报告改写到批次根目录。
    for folder in ("00_输入", "01_发货方案"):
        shutil.rmtree(TARGET / folder)
    backfill_custom_rows()
    slim_release(TARGET)
    validate_release(TARGET)
    write_report(TARGET, notes=(
        f"- 来源：`{SOURCE.name}`（尺码改名自 `0915.3-compact-plus-custom-skus`），未重跑聚类、年份合并与分配。",
        "- 尺码改名（老爷车，L0–L4）：" + "，".join(f"{row['老尺码']}→{row['新尺码']}" for row in renames)
        + "；原子明细“自动尺码”中的跑车 `-0` 后缀保留。定制尺码 BEL-AIR-5357、CHALLENGER、MODEL-X 不变。",
        f"- CHALLENGER、MODEL-X 的原子明细与校验行从 `{CUSTOM.name}` 补齐。",
    ))
    print(TARGET)


if __name__ == "__main__":
    main()
