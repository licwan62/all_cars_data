from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
CODE = PROJECT / "code"
for path in (ROOT, CODE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from id_scheme import append_country_code, dimension_id
from regional_size_common import build_dimension_library, read_csv
from regional_sources import build_ru_base


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


merge = load_module(CODE / "merge_dimension_library.py", "merge_dimension_library_analysis")
rules = merge.load_structure_rules()

for region in ("eu", "ru"):
    source = read_csv(merge.region_library_path(region))
    rows = source.to_dict("records")
    proposed = []
    changed = 0
    for row in rows:
        row["结构"] = merge.normalize_structure(row["结构"], rules)
        new_id = append_country_code(dimension_id(row), region.upper())
        proposed.append(new_id)
        changed += new_id != append_country_code(row["DIMENSION-ID"], region.upper())
    duplicates = Counter(proposed)
    collisions = {key: count for key, count in duplicates.items() if count > 1}
    print(region.upper(), {"rows": len(rows), "changed_ids": changed, "duplicate_rows": sum(collisions.values()), "duplicate_ids": len(collisions)})
    for key, count in list(collisions.items())[:10]:
        print(" collision", count, key)
        for row, proposed_id in zip(rows, proposed, strict=True):
            if proposed_id == key:
                print("  row", {column: row[column] for column in ["DIMENSION-ID", "版本", "结构", "代际", "YEAR", "L-IN", "W-IN", "H-IN"]})

source_dir = PROJECT / "data" / "ru" / "0916" / "source"
base, extra = build_ru_base(source_dir)
rebuilt, _ = build_dimension_library(base)
official = read_csv(PROJECT / "data" / "ru" / "0916" / "00_RU尺寸库.csv")
print("RU source join", extra)
print("RU 00 reproduction", {
    "rebuilt_rows": len(rebuilt),
    "official_rows": len(official),
    "exact_equal": rebuilt.equals(official),
    "different_cells": int((rebuilt != official).to_numpy().sum()) if rebuilt.shape == official.shape else None,
})
for column in rebuilt.columns:
    left = rebuilt[column].astype("string").fillna("")
    right = official[column].astype("string").fillna("")
    print(" column", column, "different", int((left != right).sum()), "rebuilt sample", left.iloc[0], "official sample", right.iloc[0])
