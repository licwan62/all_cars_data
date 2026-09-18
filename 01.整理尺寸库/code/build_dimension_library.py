"""01.整理尺寸库 节点的入口：把某个区域的 source 压缩去重为 00_XX尺寸库.csv。

输入：data/<region>/<批次>/source/ 下该区域的原始抓取结果。
输出：data/<region>/<批次>/00_<REGION>尺寸库.csv（DIMENSION_COLUMNS 结构，
已按物理尺寸去重）。销量、车型（TRIM）等信息由下游节点（EU/RU 尺码分析、
02.销量评估）各自维护，不在本节点的产物范围内。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
ROOT = PROJECT_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regional_size_common import (  # noqa: E402
    RegionalDataError,
    build_dimension_library,
    write_dimension_library,
)
from regional_sources import build_eu_base, build_ru_base  # noqa: E402

REGION_LABELS = {"eu": "EU", "ru": "RU"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成区域尺寸库（source -> 压缩去重后的 00_XX尺寸库.csv）")
    parser.add_argument("--region", required=True, choices=sorted(REGION_LABELS))
    parser.add_argument("--batch", default="0916", help="批次目录名，默认 0916")
    parser.add_argument("--source-dir", type=Path, help="默认 data/<region>/<batch>/source")
    parser.add_argument("--output", type=Path, help="默认 data/<region>/<batch>/00_<REGION>尺寸库.csv")
    parser.add_argument("--as-of-year", type=int, default=date.today().year, help="仅 EU 需要，用于补全在售年份区间")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    label = REGION_LABELS[args.region]
    source_dir = args.source_dir or PROJECT_DIR / "data" / args.region / args.batch / "source"
    output_path = args.output or PROJECT_DIR / "data" / args.region / args.batch / f"00_{label}尺寸库.csv"

    try:
        if args.region == "eu":
            base, extra = build_eu_base(source_dir.resolve(), args.as_of_year)
        elif args.region == "ru":
            base, extra = build_ru_base(source_dir.resolve())
        else:  # pragma: no cover - 由 argparse choices 保证
            raise RegionalDataError(f"暂不支持的区域：{args.region}")
        library, _metadata = build_dimension_library(base)
        write_dimension_library(library, output_path.resolve())
    except (RegionalDataError, FileNotFoundError, pd.errors.ParserError) as error:
        print(f"{label} 尺寸库整理失败：{error}", file=sys.stderr)
        return 2

    summary = {
        "region": label,
        "source_dir": str(source_dir.resolve()),
        "output": str(output_path.resolve()),
        "library_rows": int(len(library)),
        **extra,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
