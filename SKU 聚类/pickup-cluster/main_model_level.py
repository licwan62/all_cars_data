"""Pickup Fitment Clustering - Model-Level (one cluster per model).

每个消费者聚类对应一个车型（MAKE + MODEL_FAMILY），不做跨车型合并。

Usage:
    python main_model_level.py
    python main_model_level.py --output "output_model_level"
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from load_data import load_data, load_fitment_with_atom_sales, filter_pickups
from normalize import run_normalize
from year_parser import parse_years
from pickup_classifier import classify_truck_type
from clustering import run_clustering
from cluster_score import score_clusters, assign_confidence
from consumer_name import generate_consumer_name, generate_fitment_summary, generate_year_compact, generate_merged_consumer_name
from export import export_cluster_summary, export_cluster_detail, export_exceptions, export_gap_investigation


def main():
    parser = argparse.ArgumentParser(description="Pickup Fitment Clustering - Model Level")
    parser.add_argument("--input", default=None, help="Path to 销量统计.CSV")
    parser.add_argument("--size-input", default=None, help="Path to 尺码分析 CSV/Excel（默认读取 source/尺码分析.csv）")
    parser.add_argument("--sales-input", default=None, help="Path to atom_sales.csv（默认读取仓库 source）")
    parser.add_argument("--output", default="output_model_level", help="Output directory")
    args = parser.parse_args()

    project_dir = Path(__file__).parent
    source_dir = project_dir.parents[1] / "source"
    config_dir = project_dir / "config"
    output_dir = project_dir / args.output

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Pickup Fitment Clustering - Model Level")
    print("=" * 60)

    # 1. Load data
    if args.input:
        input_path = Path(args.input)
        print(f"\nLoading legacy combined data from: {input_path}")
        df = load_data(str(input_path))
    else:
        size_path = Path(args.size_input) if args.size_input else source_dir / "尺码分析.csv"
        sales_path = Path(args.sales_input) if args.sales_input else source_dir / "atom_sales.csv"
        print(f"\nLoading fitment dimensions from: {size_path}")
        print(f"Loading atom sales from: {sales_path}")
        df = load_fitment_with_atom_sales(str(size_path), str(sales_path))
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

    # 5. Run clustering (model_level=True)
    print("\nRunning model-level clustering...")
    clusters, valid_df, exceptions_df = run_clustering(df, str(config_dir), model_level=True)

    print(f"  Valid rows: {len(valid_df):,}")
    print(f"  Exception rows: {len(exceptions_df):,}")
    print(f"  Model-level clusters: {len(clusters)}")

    # 6. Score clusters
    clusters = score_clusters(clusters, str(config_dir))

    # 7. Generate consumer names — split by variant composition
    from consumer_name import generate_variant_split_names
    print("\nGenerating variant-split consumer names...")
    split_count = 0
    for c in clusters:
        splits = generate_variant_split_names(c, clusters)
        c["_split_names"] = splits
        if len(splits) > 1:
            split_count += 1
            # Build split-specific CLUSTER_ID mapping for detail export
            split_cid_map = {}
            for sp in splits:
                for idx in sp["rows"].index:
                    split_cid_map[idx] = sp["split_cluster_id"]
            c["_split_cluster_map"] = split_cid_map
        # Primary name: merged name with variant inclusion
        c["CONSUMER_NAME"] = generate_merged_consumer_name(c, clusters)
        c["FITMENT_SUMMARY"] = generate_fitment_summary(c)
        c["YEAR_COMPACT"] = generate_year_compact(c)
        c["CONFIDENCE"] = assign_confidence(c)
    print(f"  Clusters split by variant: {split_count}")

    # 7b. Optimize year gaps
    from year_gap_filler import optimize_consumer_name
    print("\nOptimizing year gaps...")
    gap_filled_count = 0
    for c in clusters:
        optimized = optimize_consumer_name(c, valid_df)
        if optimized:
            c["CONSUMER_NAME_OPTIMIZED"] = optimized
            c["YEAR_GAP_FILLED"] = 1
            gap_filled_count += 1
        else:
            c["CONSUMER_NAME_OPTIMIZED"] = ""
            c["YEAR_GAP_FILLED"] = 0
    print(f"  Clusters with filled gaps: {gap_filled_count}")

    # 8. Export
    print("\nExporting results...")
    summary_path = export_cluster_summary(clusters, str(output_dir))
    detail_path = export_cluster_detail(clusters, valid_df, str(output_dir))
    exc_path = export_exceptions(exceptions_df, str(output_dir))

    # 8b. Gap investigation
    from year_gap_filler import generate_gap_investigation
    gap_df = generate_gap_investigation(clusters, valid_df, df)
    gap_path = export_gap_investigation(gap_df, str(output_dir))

    print(f"  Summary: {summary_path}")
    print(f"  Detail:  {detail_path}")
    print(f"  Exceptions: {exc_path}")
    if gap_path:
        print(f"  Gap Investigation: {gap_path}")

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
    print(f"Model-level clusters:     {len(clusters)}")
    print(f"Safety check failures:    {len(safety_fail)}")

    total_sales = df["预估销量 的总和"].sum()
    clustered_sales = sum(c["estimated_sales"] for c in clusters)
    coverage = (clustered_sales / total_sales * 100) if total_sales > 0 else 0
    print(f"\nEstimated sales coverage: {coverage:.1f}%")

    # Top 20 clusters
    print(f"\nTop 20 Model-Level Clusters by Sales:")
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
