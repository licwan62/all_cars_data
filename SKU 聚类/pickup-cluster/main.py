"""Pickup Fitment Clustering - Main Pipeline.

Usage:
    python main.py
    python main.py --input "source/销量统计.CSV" --output "output"
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from load_data import load_data, filter_pickups
from normalize import run_normalize
from year_parser import parse_years
from pickup_classifier import classify_truck_type
from clustering import run_clustering
from cluster_score import score_clusters, assign_confidence
from consumer_name import generate_consumer_name, generate_fitment_summary, generate_year_compact
from export import export_cluster_summary, export_cluster_detail, export_exceptions


def main():
    parser = argparse.ArgumentParser(description="Pickup Fitment Clustering")
    parser.add_argument("--input", default=None, help="Path to 销量统计.CSV")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    project_dir = Path(__file__).parent
    config_dir = project_dir / "config"
    output_dir = project_dir / args.output

    # Default input path
    if args.input:
        input_path = Path(args.input)
    else:
        input_path = project_dir.parent / "销量统计.CSV"

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Pickup Fitment Clustering")
    print("=" * 60)

    # 1. Load data
    print(f"\nLoading data from: {input_path}")
    df = load_data(str(input_path))
    total_rows = len(df)

    df = filter_pickups(df)
    pickup_rows = len(df)
    print(f"  Total rows: {total_rows:,}")
    print(f"  Pickup rows: {pickup_rows:,}")

    # 2. Normalize
    print("\nNormalizing data...")
    df = run_normalize(df, str(config_dir))

    # 3. Parse years
    df = parse_years(df)

    # 4. Classify
    df = classify_truck_type(df, str(config_dir))

    # 5. Run clustering
    print("\nRunning clustering...")
    clusters, valid_df, exceptions_df = run_clustering(df, str(config_dir))

    print(f"  Valid rows: {len(valid_df):,}")
    print(f"  Exception rows: {len(exceptions_df):,}")
    print(f"  Initial clusters: {len(clusters)}")

    # 6. Score clusters
    clusters = score_clusters(clusters, str(config_dir))

    # 7. Generate consumer names
    for c in clusters:
        c["CONSUMER_NAME"] = generate_consumer_name(c)
        c["FITMENT_SUMMARY"] = generate_fitment_summary(c)
        c["YEAR_COMPACT"] = generate_year_compact(c)
        c["CONFIDENCE"] = assign_confidence(c)

    # 8. Export
    print("\nExporting results...")
    summary_path = export_cluster_summary(clusters, str(output_dir))
    detail_path = export_cluster_detail(clusters, valid_df, str(output_dir))
    exc_path = export_exceptions(exceptions_df, str(output_dir))

    print(f"  Summary: {summary_path}")
    print(f"  Detail:  {detail_path}")
    print(f"  Exceptions: {exc_path}")

    # 9. Console report
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    physical_sizes = set(c["自动尺码"] for c in clusters)
    safety_fail = [c for c in clusters if not c["safety_pass"]]

    print(f"\nPickup rows:              {pickup_rows:,}")
    print(f"Valid rows:               {len(valid_df):,}")
    print(f"Exception rows:           {len(exceptions_df):,}")
    print(f"")
    print(f"Physical sizes:           {len(physical_sizes)}")
    print(f"Consumer clusters:        {len(clusters)}")
    print(f"Safety check failures:    {len(safety_fail)}")

    total_sales = df["预估销量 的总和"].sum()
    clustered_sales = sum(c["estimated_sales"] for c in clusters)
    coverage = (clustered_sales / total_sales * 100) if total_sales > 0 else 0
    print(f"\nEstimated sales coverage: {coverage:.1f}%")

    # Top 20 clusters
    print(f"\nTop 20 Clusters by Sales:")
    print("-" * 60)
    top = sorted(clusters, key=lambda c: c["estimated_sales"], reverse=True)[:20]
    for i, c in enumerate(top, 1):
        print(f"{i:02d} {c['CLUSTER_ID']}")
        print(f"    {c['CONSUMER_NAME']}")
        print(f"    {c['YEAR_COMPACT']}")
        print(f"    Sales: {c['estimated_sales']:,.0f}  |  Score: {c['CLUSTER_SCORE']:.3f}  |  Safety: {'PASS' if c['safety_pass'] else 'FAIL'}")
        print()

    print("=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()