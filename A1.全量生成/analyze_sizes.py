from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.size_analysis import build_size_analysis_files


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将 TrimList 按 DIMENSION-ID 关联自动尺码并输出多 Size 展开报告"
    )
    parser.add_argument("--trim-list", type=Path, default=DATA / "TrimList.csv")
    parser.add_argument(
        "--trim-audit", type=Path, default=DATA / "TrimList_audit.csv"
    )
    parser.add_argument(
        "--size-source",
        "--size-workbook",
        dest="size_source",
        type=Path,
        default=WORKSPACE / "source" / "尺码分析.csv",
        help="统一尺码分析 CSV；--size-workbook 保留为旧参数别名",
    )
    parser.add_argument("--size-sheet", default="尺码匹配")
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_size_analysis_files(
        args.trim_list.resolve(),
        args.trim_audit.resolve(),
        args.size_source.resolve(),
        args.size_sheet,
        args.output_dir.resolve(),
        args.data_dir.resolve(),
    )
    print(json.dumps(result.report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
