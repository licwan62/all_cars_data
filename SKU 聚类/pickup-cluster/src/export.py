"""Export clustering results to CSV files."""

import pandas as pd
from pathlib import Path


def export_cluster_summary(clusters: list[dict], output_dir: str) -> str:
    """Export pickup_cluster_summary.csv.

    If a cluster has _split_names (variant splits), each split becomes a row
    with its own unique CLUSTER_ID (split_cluster_id).
    """
    rows = []
    for c in clusters:
        splits = c.get("_split_names", [])
        if splits and len(splits) > 1:
            # Multiple variant groups: one row per split with unique CLUSTER_ID
            for sp in splits:
                rows.append({
                    "CLUSTER_ID": sp.get("split_cluster_id", c.get("CLUSTER_ID", "")),
                    "PHYSICAL_SKU": c.get("自动尺码", ""),
                    "TRUCK_TYPE": c.get("TRUCK_TYPE", ""),
                    "CAB_GROUP": c.get("CAB_GROUP", ""),
                    "BED_GROUP": c.get("BED_GROUP", ""),
                    "AXLE_TYPE": c.get("AXLE_TYPE", ""),
                    "CONSUMER_NAME": c.get("CONSUMER_NAME", ""),
                    "CONSUMER_NAME_OPTIMIZED": c.get("CONSUMER_NAME_OPTIMIZED", ""),
                    "YEAR_GAP_FILLED": c.get("YEAR_GAP_FILLED", 0),
                    "YEAR_COMPACT": sp.get("year_compact", ""),
                    "FITMENT_SUMMARY": "",
                    "MAKE_COUNT": len(c.get("makes", [])),
                    "MODEL_COUNT": len(c.get("models", [])),
                    "FITMENT_COUNT": len(sp.get("rows", pd.DataFrame())),
                    "YEAR_MIN": c.get("year_min", 0),
                    "YEAR_MAX": c.get("year_max", 0),
                    "L_MIN": c.get("l_min", 0),
                    "L_MAX": c.get("l_max", 0),
                    "L_SPREAD": c.get("l_spread", 0),
                    "W_MIN": c.get("w_min", 0),
                    "W_MAX": c.get("w_max", 0),
                    "W_SPREAD": c.get("w_spread", 0),
                    "H_MIN": c.get("h_min", 0),
                    "H_MAX": c.get("h_max", 0),
                    "H_SPREAD": c.get("h_spread", 0),
                    "LENGTH_MARGIN_MIN": c.get("length_margin_min", 0),
                    "LENGTH_MARGIN_MEDIAN": c.get("length_margin_median", 0),
                    "ESTIMATED_SALES": sp.get("sales", 0),
                    "CLUSTER_SCORE": c.get("CLUSTER_SCORE", 0),
                    "CONFIDENCE": c.get("CONFIDENCE", ""),
                    "SAFETY_PASS": c.get("safety_pass", True),
                    "MERGE_STATUS": c.get("MERGE_STATUS", ""),
                    "ORIGINAL_ATOM_COUNT": c.get("_diagnostics", {}).get("ORIGINAL_ATOM_COUNT", 0),
                    "EXPANDED_ATOM_COUNT": c.get("_diagnostics", {}).get("EXPANDED_ATOM_COUNT", 0),
                    "NEW_ATOM_COUNT": c.get("_diagnostics", {}).get("NEW_ATOM_COUNT", 0),
                    "EXISTING_ATOM_COUNT": c.get("_diagnostics", {}).get("EXISTING_ATOM_COUNT", 0),
                    "UNRESOLVED_NEW_ATOM_COUNT": c.get("_diagnostics", {}).get("UNRESOLVED_NEW_ATOM_COUNT", 0),
                    "INFERRED_NEW_ATOM_COUNT": c.get("_diagnostics", {}).get("INFERRED_NEW_ATOM_COUNT", 0),
                    "INFERRED_CLUSTER_ID": c.get("_diagnostics", {}).get("INFERRED_CLUSTER_ID", ""),
                    "MULTI_CLUSTER_ATOM_COUNT": c.get("_diagnostics", {}).get("MULTI_CLUSTER_ATOM_COUNT", 0),
                    "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": c.get("_diagnostics", {}).get("PHYSICAL_SKU_CONFLICT_ATOM_COUNT", 0),
                    "TARGET_PHYSICAL_SKU": c.get("_diagnostics", {}).get("TARGET_PHYSICAL_SKU", ""),
                    "REJECT_REASON": c.get("_diagnostics", {}).get("REJECT_REASON", ""),
                })
        else:
            # Single group: one row
            rows.append({
            "CLUSTER_ID": c.get("CLUSTER_ID", ""),
            "PHYSICAL_SKU": c.get("自动尺码", ""),
            "TRUCK_TYPE": c.get("TRUCK_TYPE", ""),
            "CAB_GROUP": c.get("CAB_GROUP", ""),
            "BED_GROUP": c.get("BED_GROUP", ""),
            "AXLE_TYPE": c.get("AXLE_TYPE", ""),
            "CONSUMER_NAME": c.get("CONSUMER_NAME", ""),
            "CONSUMER_NAME_OPTIMIZED": c.get("CONSUMER_NAME_OPTIMIZED", ""),
            "YEAR_GAP_FILLED": c.get("YEAR_GAP_FILLED", 0),
            "YEAR_COMPACT": c.get("YEAR_COMPACT", ""),
            "FITMENT_SUMMARY": c.get("FITMENT_SUMMARY", ""),
            "MAKE_COUNT": len(c.get("makes", [])),
            "MODEL_COUNT": len(c.get("models", [])),
            "FITMENT_COUNT": c.get("fitment_count", 0),
            "YEAR_MIN": c.get("year_min", 0),
            "YEAR_MAX": c.get("year_max", 0),
            "L_MIN": c.get("l_min", 0),
            "L_MAX": c.get("l_max", 0),
            "L_SPREAD": c.get("l_spread", 0),
            "W_MIN": c.get("w_min", 0),
            "W_MAX": c.get("w_max", 0),
            "W_SPREAD": c.get("w_spread", 0),
            "H_MIN": c.get("h_min", 0),
            "H_MAX": c.get("h_max", 0),
            "H_SPREAD": c.get("h_spread", 0),
            "LENGTH_MARGIN_MIN": c.get("length_margin_min", 0),
            "LENGTH_MARGIN_MEDIAN": c.get("length_margin_median", 0),
            "ESTIMATED_SALES": c.get("estimated_sales", 0),
            "CLUSTER_SCORE": c.get("CLUSTER_SCORE", 0),
            "CONFIDENCE": c.get("CONFIDENCE", ""),
            "SAFETY_PASS": c.get("safety_pass", True),
            "MERGE_STATUS": c.get("MERGE_STATUS", ""),
            "ORIGINAL_ATOM_COUNT": c.get("_diagnostics", {}).get("ORIGINAL_ATOM_COUNT", 0),
            "EXPANDED_ATOM_COUNT": c.get("_diagnostics", {}).get("EXPANDED_ATOM_COUNT", 0),
            "NEW_ATOM_COUNT": c.get("_diagnostics", {}).get("NEW_ATOM_COUNT", 0),
            "EXISTING_ATOM_COUNT": c.get("_diagnostics", {}).get("EXISTING_ATOM_COUNT", 0),
            "UNRESOLVED_NEW_ATOM_COUNT": c.get("_diagnostics", {}).get("UNRESOLVED_NEW_ATOM_COUNT", 0),
            "INFERRED_NEW_ATOM_COUNT": c.get("_diagnostics", {}).get("INFERRED_NEW_ATOM_COUNT", 0),
            "INFERRED_CLUSTER_ID": c.get("_diagnostics", {}).get("INFERRED_CLUSTER_ID", ""),
            "MULTI_CLUSTER_ATOM_COUNT": c.get("_diagnostics", {}).get("MULTI_CLUSTER_ATOM_COUNT", 0),
            "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": c.get("_diagnostics", {}).get("PHYSICAL_SKU_CONFLICT_ATOM_COUNT", 0),
            "TARGET_PHYSICAL_SKU": c.get("_diagnostics", {}).get("TARGET_PHYSICAL_SKU", ""),
            "REJECT_REASON": c.get("_diagnostics", {}).get("REJECT_REASON", ""),
            "OPTIMIZED_MERGE_STATUS": c.get("_optimized_diagnostics", {}).get("MERGE_STATUS", ""),
            "OPTIMIZED_EXPANDED_ATOM_COUNT": c.get("_optimized_diagnostics", {}).get("EXPANDED_ATOM_COUNT", 0),
            "OPTIMIZED_NEW_ATOM_COUNT": c.get("_optimized_diagnostics", {}).get("NEW_ATOM_COUNT", 0),
            "OPTIMIZED_PHYSICAL_SKU_CONFLICT_ATOM_COUNT": c.get("_optimized_diagnostics", {}).get("PHYSICAL_SKU_CONFLICT_ATOM_COUNT", 0),
            "OPTIMIZED_REJECT_REASON": c.get("_optimized_diagnostics", {}).get("REJECT_REASON", ""),
        })

    df = pd.DataFrame(rows)
    out_path = Path(output_dir) / "pickup_cluster_summary.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return str(out_path)


def export_cluster_detail(clusters: list[dict], valid_df: pd.DataFrame, output_dir: str) -> str:
    """Export pickup_cluster_detail.csv with each original row annotated with its split CLUSTER_ID."""
    row_cluster_map = {}
    for c in clusters:
        split_map = c.get("_split_cluster_map", {})
        if split_map:
            # Split cluster: use per-split CLUSTER_ID
            for idx, cid in split_map.items():
                row_cluster_map[idx] = {
                    "CLUSTER_ID": cid,
                    "PHYSICAL_SKU": c["自动尺码"],
                    "CLUSTER_SCORE": c.get("CLUSTER_SCORE", 0),
                }
        else:
            # Non-split cluster: use base CLUSTER_ID
            for idx in c["rows"].index:
                row_cluster_map[idx] = {
                    "CLUSTER_ID": c["CLUSTER_ID"],
                    "PHYSICAL_SKU": c["自动尺码"],
                    "CLUSTER_SCORE": c.get("CLUSTER_SCORE", 0),
                }

    detail = valid_df.copy()
    detail["CLUSTER_ID"] = detail.index.map(lambda i: row_cluster_map.get(i, {}).get("CLUSTER_ID", ""))
    detail["PHYSICAL_SKU"] = detail.index.map(lambda i: row_cluster_map.get(i, {}).get("PHYSICAL_SKU", ""))
    detail["CLUSTER_SCORE"] = detail.index.map(lambda i: row_cluster_map.get(i, {}).get("CLUSTER_SCORE", 0))

    out_path = Path(output_dir) / "pickup_cluster_detail.csv"
    detail.to_csv(out_path, index=False, encoding="utf-8-sig")
    return str(out_path)


def export_exceptions(exceptions_df: pd.DataFrame, output_dir: str) -> str:
    """Export pickup_cluster_exceptions.csv."""
    out_path = Path(output_dir) / "pickup_cluster_exceptions.csv"
    exceptions_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return str(out_path)


def export_gap_investigation(gap_df: pd.DataFrame, output_dir: str) -> str:
    """Export gap_investigation.csv."""
    if gap_df.empty:
        return ""
    out_path = Path(output_dir) / "gap_investigation.csv"
    gap_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return str(out_path)


def export_candidate_audit(records: list[dict], output_dir: str) -> str:
    """Export every attempted candidate, including rejected combinations."""
    out_path = Path(output_dir) / "pickup_cluster_candidate_audit.csv"
    pd.DataFrame(records).to_csv(out_path, index=False, encoding="utf-8-sig")
    return str(out_path)
