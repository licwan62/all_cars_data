"""US TRIM 匹配：用 data/US/TRIM 下已审核的 TrimList 与 TRIM 值，给 US 全量表回填 TRIM 并生成 TRIM适配器。

输入是本次计算的 US 全量表（DIMENSION-ID 带 " US" 后缀）。已不在 US 尺寸库中的旧 TrimList 行先按
TrimList_ID迁移.csv（旧ID、Year、新ID、依据；新ID 留空表示按规则不映射）迁移到当前 ID，并同步
trim_values.csv 的 Trims；仍无对应的才从本次输入中排除。原始 data/US/TRIM/*.csv 不改动。
输入快照、TrimList 关联报告和 TRIM适配器 写入调用方给定的工作目录（位于本次 artifact 内）。
"""

from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from trim.size_analysis import build_size_analysis_files

PROJECT = Path(__file__).resolve().parents[2]
DATA = PROJECT / "data" / "US" / "TRIM"
TRIM_VALUES = DATA / "trim_values.csv"
ID_MIGRATION = DATA / "TrimList_ID迁移.csv"
TRIM_LISTS = ("TrimList.csv", "TrimList_audit.csv")
ADAPTER_NAME = "TRIM适配器.csv"
REGION_SUFFIX = " US"


@dataclass(frozen=True)
class TrimMatch:
    trims: dict[str, str]  # 带 " US" 后缀的 DIMENSION-ID -> TRIM（规范化后的 Trims）
    adapter: Path
    status: dict[str, object]


def load_id_migration(current_ids: set[str], path: Path = ID_MIGRATION) -> dict[str, dict[str, list[str]]]:
    """{旧ID: {Year 或 "": [新ID...]}}；新ID 为空表示按规则不映射。"""
    migration: dict[str, dict[str, list[str]]] = {}
    if not path.is_file():
        return migration
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            new_id = row["新DIMENSION-ID"].strip()
            if new_id and new_id not in current_ids:
                raise ValueError(f"TrimList ID 迁移目标不在当前 US 全量表：{new_id}")
            targets = migration.setdefault(row["旧DIMENSION-ID"].strip(), {}).setdefault(row["Year"].strip(), [])
            if new_id:
                targets.append(new_id)
    return migration


def migrated_ids(migration: dict[str, dict[str, list[str]]], record_id: str, year: str | None) -> list[str] | None:
    by_year = migration.get(record_id)
    if by_year is None:
        return None
    if year is None:
        return sorted({new_id for targets in by_year.values() for new_id in targets})
    if year in by_year:
        return by_year[year]
    return by_year.get("")


def maintained_trims(current_ids: set[str], data_dir: Path = DATA) -> dict[str, str]:
    """已审核 TRIM 值（基础 ID -> Trims），并按 ID 迁移表补到新 ID。"""
    migration = load_id_migration(current_ids, data_dir / ID_MIGRATION.name)
    values = pd.read_csv(data_dir / TRIM_VALUES.name, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if values["DIMENSION-ID"].duplicated().any():
        raise ValueError("维护的 TRIM 值存在重复 DIMENSION-ID")
    trim_map = values.set_index("DIMENSION-ID")["Trims"].to_dict()
    for old_id, trims in list(trim_map.items()):
        for new_id in migrated_ids(migration, old_id, None) or []:
            trim_map.setdefault(new_id, trims)
    return trim_map


def _select_trim_rows(
    rows: list[dict[str, str]],
    current_ids: set[str],
    migration: dict[str, dict[str, list[str]]],
    source_by_id: pd.DataFrame,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    selected = [row for row in rows if row["DIMENSION-ID"] in current_ids]
    seen = {(row["DIMENSION-ID"], row["Year"], row["Make"], row["Model"]) for row in selected}
    counts = {"migrated": 0, "dropped_by_rule": 0, "excluded": 0}
    for row in rows:
        if row["DIMENSION-ID"] in current_ids:
            continue
        targets = migrated_ids(migration, row["DIMENSION-ID"], row["Year"])
        if targets is None:
            counts["excluded"] += 1
            continue
        if not targets:
            counts["dropped_by_rule"] += 1
            counts["excluded"] += 1
        for new_id in targets:
            key = (new_id, row["Year"], row["Make"], row["Model"])
            if key in seen:
                continue
            seen.add(key)
            moved = {**row, "DIMENSION-ID": new_id}
            for field in ("结构", "版本", "CAB", "BED"):
                if field in moved:
                    moved[field] = source_by_id.at[new_id, field]
            if "说明" in moved:
                moved["说明"] = f"{moved['说明']}；ID 迁移自 {row['DIMENSION-ID']}".lstrip("；")
            selected.append(moved)
            counts["migrated"] += 1
    return selected, counts


def match_trims(us_full: pd.DataFrame, work_dir: Path, data_dir: Path = DATA) -> TrimMatch:
    """对本次 US 全量表做 TRIM 匹配；work_dir 下写 input/（快照）、reports/（关联报告）与 TRIM适配器。"""
    source = us_full.copy()
    if source["DIMENSION-ID"].duplicated().any() or not source["DIMENSION-ID"].str.endswith(REGION_SUFFIX).all():
        raise ValueError("US 全量表 DIMENSION-ID 缺少 US 后缀或重复")
    source["DIMENSION-ID"] = source["DIMENSION-ID"].str.removesuffix(REGION_SUFFIX)
    current_ids = set(source["DIMENSION-ID"])
    migration = load_id_migration(current_ids, data_dir / ID_MIGRATION.name)
    trim_map = maintained_trims(current_ids, data_dir)
    source["TRIM"] = source["DIMENSION-ID"].map(trim_map).fillna("")

    inputs, reports = work_dir / "input", work_dir / "reports"
    inputs.mkdir(parents=True)
    reports.mkdir()
    for path in (data_dir / TRIM_VALUES.name, data_dir / ID_MIGRATION.name):
        if path.is_file():
            shutil.copy2(path, inputs / path.name)
    prepared = inputs / "全量表_US_基础ID.csv"
    source.to_csv(prepared, index=False, encoding="utf-8-sig", lineterminator="\n")
    source_by_id = source.set_index("DIMENSION-ID")
    trim_counts: dict[str, dict[str, int]] = {}
    for name in TRIM_LISTS:
        with (data_dir / name).open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames
            rows = list(reader)
        selected, trim_counts[name] = _select_trim_rows(rows, current_ids, migration, source_by_id)
        with (inputs / name).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(selected)
    result = build_size_analysis_files(
        inputs / TRIM_LISTS[0], inputs / TRIM_LISTS[1], prepared, "尺码匹配", work_dir, reports,
    )
    trims = {f"{row['DIMENSION-ID']}{REGION_SUFFIX}": row["Trims"] for row in result.dimension_trim_rows}
    status = {
        "rows": len(source),
        "maintained_trim_values_used": int(source["TRIM"].ne("").sum()),
        "nonempty_trims": sum(1 for value in trims.values() if value),
        "trim_rows": trim_counts,
        "counts": result.report["counts"],
    }
    return TrimMatch(trims=trims, adapter=work_dir / ADAPTER_NAME, status=status)
