#!/usr/bin/env python3
"""用当前 A0 US 全量表和已审核 TrimList 刷新 B1 交付物。"""

from __future__ import annotations

import json
import csv
import os
import re
import shutil
from datetime import date
from pathlib import Path

import pandas as pd
import sys

# 脚本位于 src/，以节点目录为包根导入 src.*
if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.size_analysis import build_size_analysis_files


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT.parent / "A0.尺码计算" / "output" / "全量表_US.csv"
DATA = PROJECT / "data"
TRIM_VALUES = DATA / "trim_values.csv"
ID_MIGRATION = DATA / "TrimList_ID迁移.csv"
OUTPUT = PROJECT / "output"
ARTIFACTS = PROJECT / "artifacts"
DELIVERABLES = ("尺寸TRIM映射.csv", "TRIM适配器.csv")


def next_artifact() -> Path:
    day = date.today().isoformat()
    used = [int(m.group(1)) for p in ARTIFACTS.glob(f"{day}_*")
            if (m := re.match(rf"{day}_(\d{{2}})_", p.name))]
    return ARTIFACTS / f"{day}_{max(used, default=0) + 1:02d}_refresh-size-analysis"


def load_id_migration(current_ids: set[str]) -> dict[str, dict[str, list[str]]]:
    """{旧ID: {Year 或 "": [新ID...]}}；新ID 为空表示按规则不映射。"""
    migration: dict[str, dict[str, list[str]]] = {}
    if not ID_MIGRATION.is_file():
        return migration
    with ID_MIGRATION.open(encoding="utf-8-sig", newline="") as handle:
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


def main() -> int:
    artifact = next_artifact()
    staging = artifact.with_name(f".{artifact.name}.tmp")
    if staging.exists() or artifact.exists():
        raise FileExistsError(artifact)
    try:
        (staging / "input").mkdir(parents=True)
        (staging / "output").mkdir()
        (staging / "reports").mkdir()
        source = pd.read_csv(SOURCE, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        if source["DIMENSION-ID"].duplicated().any() or not source["DIMENSION-ID"].str.endswith(" US").all():
            raise ValueError("A0 US 全量表 DIMENSION-ID 缺少 US 后缀或重复")
        source["DIMENSION-ID"] = source["DIMENSION-ID"].str.removesuffix(" US")
        current_ids = set(source["DIMENSION-ID"])
        migration = load_id_migration(current_ids)
        source_by_id = source.set_index("DIMENSION-ID")
        values = pd.read_csv(TRIM_VALUES, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        if values["DIMENSION-ID"].duplicated().any():
            raise ValueError("维护的 TRIM 值存在重复 DIMENSION-ID")
        trim_map = values.set_index("DIMENSION-ID")["Trims"].to_dict()
        for old_id, trims in list(trim_map.items()):
            for new_id in migrated_ids(migration, old_id, None) or []:
                trim_map.setdefault(new_id, trims)
        filled = source["TRIM"].eq("") & source["DIMENSION-ID"].isin(set(trim_map))
        source.loc[filled, "TRIM"] = source.loc[filled, "DIMENSION-ID"].map(trim_map)
        if ID_MIGRATION.is_file():
            shutil.copy2(ID_MIGRATION, staging / "input" / ID_MIGRATION.name)
        prepared = staging / "input" / "全量表_US_基础ID.csv"
        source.to_csv(prepared, index=False, encoding="utf-8-sig", lineterminator="\n")
        shutil.copy2(TRIM_VALUES, staging / "input" / TRIM_VALUES.name)
        excluded: dict[str, int] = {}
        migrated: dict[str, int] = {}
        dropped_by_rule: dict[str, int] = {}
        for name in ("TrimList.csv", "TrimList_audit.csv"):
            with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                fields = reader.fieldnames
                rows = list(reader)
            selected = [row for row in rows if row["DIMENSION-ID"] in current_ids]
            seen = {(row["DIMENSION-ID"], row["Year"], row["Make"], row["Model"]) for row in selected}
            migrated[name] = dropped_by_rule[name] = 0
            for row in rows:
                if row["DIMENSION-ID"] in current_ids:
                    continue
                targets = migrated_ids(migration, row["DIMENSION-ID"], row["Year"])
                if targets is None:
                    continue
                if not targets:
                    dropped_by_rule[name] += 1
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
                    migrated[name] += 1
            excluded[name] = len(rows) - sum(1 for row in rows if row["DIMENSION-ID"] in current_ids) - sum(
                1 for row in rows if row["DIMENSION-ID"] not in current_ids and migrated_ids(migration, row["DIMENSION-ID"], row["Year"])
            )
            with (staging / "input" / name).open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerows(selected)
        result = build_size_analysis_files(
            staging / "input" / "TrimList.csv",
            staging / "input" / "TrimList_audit.csv",
            prepared,
            "尺码匹配",
            staging / "output",
            staging / "reports",
        )
        status = {"status": "passed", "source": str(SOURCE), "rows": len(source),
                  "maintained_trim_values_used": int(filled.sum()),
                  "nonempty_trim_values": int(source["TRIM"].ne("").sum()),
                  "excluded_obsolete_trim_rows": excluded,
                  "migrated_trim_rows": migrated,
                  "dropped_by_migration_rule": dropped_by_rule,
                  "counts": result.report["counts"]}
        (staging / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(staging, artifact)
        for name in DELIVERABLES:
            target = OUTPUT / name
            temporary = target.with_name(f".{name}.tmp")
            shutil.copy2(artifact / "output" / name, temporary)
            os.replace(temporary, target)
        print(json.dumps({**status, "artifact": str(artifact)}, ensure_ascii=False))
        return 0
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
