from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.fitment_coverage import build_fitment_coverage_files


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "source"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="建立4A到DIMENSION-ID的全量尝试覆盖台账")
    parser.add_argument(
        "--fitment", type=Path, default=SOURCE / "4afitment_data.csv"
    )
    parser.add_argument(
        "--dimensions", type=Path, default=SOURCE / "车型尺寸库.csv"
    )
    parser.add_argument("--trim", type=Path, default=ROOT / "output" / "TrimList.csv")
    parser.add_argument(
        "--review",
        type=Path,
        default=ROOT / "output" / "TrimList_online_review.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_fitment_coverage_files(
        args.fitment.resolve(),
        args.dimensions.resolve(),
        args.trim.resolve(),
        args.review.resolve(),
        args.output_dir.resolve(),
    )
    print(json.dumps(result.report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
