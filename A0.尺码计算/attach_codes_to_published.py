#!/usr/bin/env python3
"""给已发布的区域表补写 DIMENSION-CODE（来自 02.代码映射/output/尺寸编码映射.csv）。

用于上游代码映射后置到尺码计算之前、而现有全量表还是旧批次产物的过渡：不重算任何尺码，
只按 DIMENSION-ID 插入 DIMENSION-CODE 列。任何 ID 缺码都会整体失败，且不改动文件。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR.parent))

from full_table_schema import attach_dimension_code  # noqa: E402


def attach_file(path: Path, code_map: Path | None = None) -> int:
    table = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    result = attach_dimension_code(table, code_map)
    temporary = path.with_suffix(path.suffix + ".tmp")
    result.to_csv(temporary, index=False, encoding="utf-8-sig", lineterminator="\n")
    os.replace(temporary, path)
    return len(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="output/ 下要补码的表")
    parser.add_argument("--code-map", type=Path)
    args = parser.parse_args(argv)
    try:
        # 先全部校验（读入并关联），再逐个写入，避免一部分表已改、一部分失败
        for path in args.files:
            attach_dimension_code(
                pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig"), args.code_map
            )
    except ValueError as error:
        print(f"补码失败：{error}", file=sys.stderr)
        return 2
    for path in args.files:
        print(f"{path.name}: {attach_file(path, args.code_map)} 行")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
