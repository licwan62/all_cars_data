"""Pickup Fitment Clustering — Unified Pipeline.

Grouping driven entirely by config/cluster_config.yaml.
Single entry point — no separate model_level variant needed.

Usage:
    python main.py
    python main.py --input "source/销量统计.CSV" --output "output"
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
from consumer_name import (
    generate_consumer_name,
    generate_merged_consumer_name,
    generate_variant_split_names,
    generate_fitment_summary,
    generate_year_compact,
    assign_required_exclusions,
)
from export import export_cluster_summary, export_cluster_detail, export_exceptions, export_gap_investigation
from atom_verifier import build_verified_candidates, build_atom_map, verify_candidate


def main():
    parser = argparse.ArgumentParser(description="Pickup Fitment Clustering")
    parser.add_argument("--input", default=None, help="Path to 销量统计.CSV")
    parser.add_argument("--size-input", default=None, help="Path to 车型数据尺码.xlsx")
    parser.add_argument("--sales-input", default=None, help="Path to atom_sales.csv")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    project_dir = Path(__file__).parent
    config_dir = project_dir / "config"
    output_dir = project_dir / args.output

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Pickup Fitment Clustering")
    print("=" * 60)

    # 1. Load data
    if args.input:
        input_path = Path(args.input)
        print(f"\nLoading legacy combined data from: {input_path}")
        df = load_data(str(input_path))
    else:
        size_path = Path(args.size_input) if args.size_input else project_dir / "input" / "车型数据尺码.xlsx"
        sales_path = Path(args.sales_input) if args.sales_input else project_dir / "input" / "atom_sales.csv"
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

    # 5. Run clustering (config-driven grouping)
    print("\nRunning clustering...")
    clusters, valid_df, exceptions_df = run_clustering(df, str(config_dir))

    print(f"  Valid rows: {len(valid_df):,}")
    print(f"  Exception rows: {len(exceptions_df):,}")
    print(f"  Initial clusters: {len(clusters)}")

    # 6. Score clusters
    clusters = score_clusters(clusters, str(config_dir))

    # 7. Candidate merge gate: only verified row combinations may become names.
    print("\nBuilding and verifying merge candidates...")
    clusters, candidate_audit = build_verified_candidates(clusters)
    assign_required_exclusions(clusters)
    print(f"  Final verified candidates: {len(clusters)}")
    print(f"  Rejected merge attempts: {sum(a['MERGE_STATUS'] == 'REJECT' for a in candidate_audit)}")

    # 8. Generate names from the exact rows of each verified candidate.
    print("\nGenerating consumer names...")
    for c in clusters:
        c["CONSUMER_NAME"] = generate_merged_consumer_name(c, clusters)
        c["FITMENT_SUMMARY"] = generate_fitment_summary(c)
        c["YEAR_COMPACT"] = generate_year_compact(c)
        c["CONFIDENCE"] = assign_confidence(c)

    # 9. Optimize year gaps, then run the optimized coverage through the same gate.
    from year_gap_filler import optimize_consumer_name
    print("\nOptimizing year gaps...")
    gap_filled_count = 0
    optimized_name_count = 0
    atom_map = build_atom_map(clusters)
    for c in clusters:
        optimized = optimize_consumer_name(c, valid_df)
        if optimized:
            diag = verify_candidate(c["rows"], c["自动尺码"], atom_map,
                                    c["CLUSTER_ID"], c.get("_optimized_ranges"))
            c["_optimized_diagnostics"] = diag
            candidate_audit.append({"BASE_CLUSTER_ID": c["CLUSTER_ID"],
                                    "CANDIDATE_TYPE": "YEAR_GAP_OPTIMIZATION",
                                    "CANDIDATE_ROW_COUNT": len(c["rows"]), **diag})
            if diag["MERGE_STATUS"] != "REJECT":
                c["CONSUMER_NAME_OPTIMIZED"] = optimized
                has_filled_gap = any(g.get("filled") for g in c.get("_gap_details", []))
                c["YEAR_GAP_FILLED"] = int(has_filled_gap)
                gap_filled_count += int(has_filled_gap)
                optimized_name_count += 1
            else:
                # Gap expansion was unsafe. Fall back to the original year
                # coverage while retaining the mandatory Bed optimization.
                c["_rejected_optimized_diagnostics"] = diag
                optimized = optimize_consumer_name(c, valid_df, try_gap_fill=False)
                fallback_diag = verify_candidate(
                    c["rows"], c["自动尺码"], atom_map, c["CLUSTER_ID"],
                    c.get("_optimized_ranges"))
                candidate_audit.append({"BASE_CLUSTER_ID": c["CLUSTER_ID"],
                                        "CANDIDATE_TYPE": "BED_ONLY_FALLBACK",
                                        "CANDIDATE_ROW_COUNT": len(c["rows"]),
                                        **fallback_diag})
                if fallback_diag["MERGE_STATUS"] == "REJECT":
                    raise RuntimeError(f"Safe optimized-name fallback rejected: {c['CLUSTER_ID']}")
                c["_optimized_diagnostics"] = fallback_diag
                c["CONSUMER_NAME_OPTIMIZED"] = optimized
                c["YEAR_GAP_FILLED"] = 0
                optimized_name_count += 1
        else:
            raise RuntimeError(f"Optimized name was not generated: {c['CLUSTER_ID']}")
    print(f"  Clusters with filled gaps: {gap_filled_count}")
    print(f"  Clusters with optimized names: {optimized_name_count}")

    # 10. Report final (already gated) statuses.
    statuses = {}
    for c in clusters:
        s = c.get("MERGE_STATUS", "UNKNOWN")
        statuses[s] = statuses.get(s, 0) + 1
    print(f"  ACCEPT: {statuses.get('ACCEPT', 0)}")
    print(f"  REVIEW: {statuses.get('REVIEW', 0)}")
    print(f"  REJECT: {statuses.get('REJECT', 0)}")

    # 11. Export
    print("\nExporting results...")
    summary_path = export_cluster_summary(clusters, str(output_dir))
    detail_path = export_cluster_detail(clusters, valid_df, str(output_dir))
    exc_path = export_exceptions(exceptions_df, str(output_dir))

    from year_gap_filler import generate_gap_investigation
    gap_df = generate_gap_investigation(clusters, valid_df, df)
    gap_path = export_gap_investigation(gap_df, str(output_dir))
    from export import export_candidate_audit
    audit_path = export_candidate_audit(candidate_audit, str(output_dir))

    print(f"  Summary: {summary_path}")
    print(f"  Detail:  {detail_path}")
    print(f"  Exceptions: {exc_path}")
    if gap_path:
        print(f"  Gap Investigation: {gap_path}")
    print(f"  Candidate Audit: {audit_path}")

    # 10. Console report
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
