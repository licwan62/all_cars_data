#!/usr/bin/env python3
"""生成 EU 版本列整改的 DIMENSION-ID 迁移表 data/EU_ID迁移.csv（一次性工具，结果纳入 data/ 维护）。

EU 版本列由“整段 BodyCode（底盘代号）”改为“只保留关键版本”（data/eu_key_versions.json）。版本是
EU DIMENSION-ID 的组成部分，因此绝大多数 EU ID 会变化。本脚本在同一份 source 上分别按旧口径
（版本 = BodyCode）与新口径建库，逐个 source 行追溯两套最终 DIMENSION-ID，输出去重后的对应关系：

  旧DIMENSION-ID, 新DIMENSION-ID, 关系（一对一 / 合并 / 拆分 / 合并且拆分）, 旧版本, 新版本

旧口径必须精确复现当前 output/尺寸库_EU.csv 的 ID 集合，否则失败（说明 source 或规则已变，迁移表不可信）。
新口径的 ID 集合即整改后的 EU 尺寸库；merge_dimension_library.py 发布前会再校验迁移表与之一致。
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
ROOT = PROJECT_DIR.parent
for path in (ROOT / "lib", PROJECT_DIR / "code"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from merge_dimension_library import latest_batch, transform_region_rows_traced  # noqa: E402
from regional_size_common import (  # noqa: E402
    RegionalDataError,
    build_dimension_library_rows,
    read_csv,
    write_dimension_library,
)
from regional_sources import build_eu_base  # noqa: E402

MIGRATION_PATH = PROJECT_DIR / "data" / "EU_ID迁移.csv"
MIGRATION_COLUMNS = ["旧DIMENSION-ID", "新DIMENSION-ID", "关系", "旧版本", "新版本"]


def final_ids(base: pd.DataFrame, work_dir: Path, label: str) -> tuple[pd.Series, dict[str, str]]:
    """返回 (每个 source 行的最终 DIMENSION-ID, 最终 ID -> 版本)。"""
    library, _, row_ids = build_dimension_library_rows(base)
    stage_path = work_dir / f"00_EU尺寸库_{label}.csv"
    write_dimension_library(library, stage_path)
    rows, mapping = transform_region_rows_traced(read_csv(stage_path).to_dict("records"), "eu")
    versions = {row["DIMENSION-ID"]: row["版本"] for row in rows}
    return row_ids.map(mapping), versions


def legacy_base(base: pd.DataFrame) -> pd.DataFrame:
    """旧口径：版本 = 整段 BodyCode，冲突时只追加整段源变体与尺寸。"""
    legacy = base.copy()
    legacy["版本"] = legacy["_raw_body_code"]
    legacy["_source_variant"] = legacy["_raw_source_variant"]
    legacy["_body_code"] = ""
    return legacy


def build_migration(base: pd.DataFrame, current_ids: set[str]) -> pd.DataFrame:
    with tempfile.TemporaryDirectory() as temporary:
        work_dir = Path(temporary)
        old_ids, old_versions = final_ids(legacy_base(base), work_dir, "legacy")
        new_ids, new_versions = final_ids(base, work_dir, "key")
    if old_ids.isna().any() or new_ids.isna().any():
        raise RegionalDataError("存在无法追溯到最终 DIMENSION-ID 的 source 行")
    if set(old_ids) != current_ids:
        raise RegionalDataError(
            f"旧口径未能复现当前 EU 尺寸库：仅旧口径 {len(set(old_ids) - current_ids)}，仅当前 {len(current_ids - set(old_ids))}"
        )
    pairs = pd.DataFrame({"旧DIMENSION-ID": old_ids, "新DIMENSION-ID": new_ids}).drop_duplicates()
    olds_per_new = pairs.groupby("新DIMENSION-ID")["旧DIMENSION-ID"].transform("nunique")
    news_per_old = pairs.groupby("旧DIMENSION-ID")["新DIMENSION-ID"].transform("nunique")
    relation = {(False, False): "一对一", (True, False): "合并", (False, True): "拆分", (True, True): "合并且拆分"}
    pairs["关系"] = [relation[(merged > 1, split > 1)] for merged, split in zip(olds_per_new, news_per_old, strict=True)]
    pairs["旧版本"] = pairs["旧DIMENSION-ID"].map(old_versions)
    pairs["新版本"] = pairs["新DIMENSION-ID"].map(new_versions)
    return pairs[MIGRATION_COLUMNS].sort_values(["旧DIMENSION-ID", "新DIMENSION-ID"], kind="stable").reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="默认 data/eu/ 下最新的批次")
    parser.add_argument("--current", type=Path, default=PROJECT_DIR / "output" / "尺寸库_EU.csv", help="整改前发布的 EU 尺寸库")
    parser.add_argument("--as-of-year", type=int, default=date.today().year)
    parser.add_argument("--output", type=Path, default=MIGRATION_PATH)
    args = parser.parse_args()
    try:
        base, _ = build_eu_base((args.source_dir or latest_batch("eu")).resolve(), args.as_of_year)
        current_ids = set(read_csv(args.current)["DIMENSION-ID"])
        migration = build_migration(base, current_ids)
    except (RegionalDataError, FileNotFoundError) as error:
        print(f"EU ID 迁移表生成失败：{error}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    migration.to_csv(args.output, index=False, encoding="utf-8-sig", lineterminator="\n")
    summary = migration["关系"].value_counts().to_dict()
    changed = int(migration["旧DIMENSION-ID"].ne(migration["新DIMENSION-ID"]).sum())
    print(
        f"旧 ID {migration['旧DIMENSION-ID'].nunique()} → 新 ID {migration['新DIMENSION-ID'].nunique()}；"
        f"对应 {len(migration)} 条，其中 ID 变化 {changed} 条；关系 {summary} -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
