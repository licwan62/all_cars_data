from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.fitment_coverage import build_fitment_coverage_files


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "source"
DATA = ROOT / "data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="建立4A到DIMENSION-ID的全量尝试覆盖台账")
    parser.add_argument(
        "--fitment", type=Path, default=SOURCE / "4A全数据.csv"
    )
    parser.add_argument(
        "--dimensions", type=Path, default=SOURCE / "车型尺寸库.csv"
    )
    parser.add_argument("--trim", type=Path, default=DATA / "TrimList.csv")
    parser.add_argument(
        "--review",
        type=Path,
        default=DATA / "TrimList_online_review.csv",
    )
    parser.add_argument(
        "--data-dir",
        "--output-dir",
        dest="data_dir",
        type=Path,
        default=DATA,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_fitment_coverage_files(
        args.fitment.resolve(),
        args.dimensions.resolve(),
        args.trim.resolve(),
        args.review.resolve(),
        args.data_dir.resolve(),
    )
    print(json.dumps(result.report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
