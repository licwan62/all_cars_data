from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.fitment_coverage import build_fitment_coverage_files
from src.size_analysis import build_size_analysis_files
from src.trimlist import build_files


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
SOURCE = WORKSPACE / "source"
LOCAL_INPUT = ROOT / "input"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生成按 DIMENSION-ID 映射的 TrimList v2"
    )
    parser.add_argument(
        "--dimensions",
        type=Path,
        default=SOURCE / "车型尺寸库.csv",
    )
    parser.add_argument(
        "--fitment",
        type=Path,
        default=SOURCE / "4afitment_data.csv",
    )
    parser.add_argument(
        "--maintenance",
        type=Path,
        default=SOURCE / "子车系维护表.csv",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=LOCAL_INPUT / "trim_overrides.csv",
    )
    parser.add_argument(
        "--online-evidence",
        type=Path,
        default=LOCAL_INPUT / "online_evidence.csv",
        help="非现有精确键候选的联网审核凭证",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "output",
    )
    parser.add_argument(
        "--size-source",
        "--size-workbook",
        dest="size_source",
        type=Path,
        default=SOURCE / "尺码分析.csv",
        help="统一尺码分析 CSV；--size-workbook 保留为旧参数别名",
    )
    parser.add_argument("--size-sheet", default="尺码匹配")
    parser.add_argument(
        "--skip-size-analysis",
        action="store_true",
        help="只生成 TrimList，不关联自动尺码和生成多 Size 展开报告",
    )
    parser.add_argument(
        "--skip-fitment-coverage",
        action="store_true",
        help="不生成4A全量DIMENSION-ID尝试覆盖报告",
    )
    parser.add_argument(
        "--fail-on-unmapped",
        action="store_true",
        help="存在未匹配 DIMENSION-ID 年份时返回失败",
    )
    parser.add_argument(
        "--fail-on-unreviewed",
        action="store_true",
        help="存在尚未由联网证据批准的候选时返回失败",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_files(
        args.dimensions.resolve(),
        args.fitment.resolve(),
        args.maintenance.resolve(),
        args.overrides.resolve() if args.overrides else None,
        args.online_evidence.resolve() if args.online_evidence else None,
        args.output_dir.resolve(),
    )
    counts = result.report["counts"]
    print(json.dumps(result.report, ensure_ascii=False, indent=2))
    print(f"\nTrimList: {(args.output_dir / 'TrimList.csv').resolve()}")

    if not args.skip_fitment_coverage:
        coverage_result = build_fitment_coverage_files(
            args.fitment.resolve(),
            args.dimensions.resolve(),
            (args.output_dir / "TrimList.csv").resolve(),
            (args.output_dir / "TrimList_online_review.csv").resolve(),
            args.output_dir.resolve(),
        )
        print("\n4A fitment coverage:")
        print(json.dumps(coverage_result.report, ensure_ascii=False, indent=2))

    if not args.skip_size_analysis:
        size_result = build_size_analysis_files(
            (args.output_dir / "TrimList.csv").resolve(),
            (args.output_dir / "TrimList_audit.csv").resolve(),
            args.size_source.resolve(),
            args.size_sheet,
            args.output_dir.resolve(),
        )
        print("\nSize analysis:")
        print(json.dumps(size_result.report, ensure_ascii=False, indent=2))

    failures: list[str] = []
    if args.fail_on_unmapped and counts["unmapped_dimension_year_atoms"]:
        failures.append(
            f"未匹配 DIMENSION-ID 年份: {counts['unmapped_dimension_year_atoms']}"
        )
    if (
        args.fail_on_unreviewed
        and counts["pending_or_rejected_online_candidate_rows"]
    ):
        failures.append(
            "待联网审核候选: "
            f"{counts['pending_or_rejected_online_candidate_rows']}"
        )
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
