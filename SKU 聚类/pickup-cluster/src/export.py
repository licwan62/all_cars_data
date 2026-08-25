"""Export clustering results to CSV files."""

import pandas as pd
from pathlib import Path


FLOAT_FORMAT = "%.1f"

SUMMARY_COLUMNS = [
    "CLUSTER_ID", "PHYSICAL_SKU", "TRUCK_TYPE", "AXLE_TYPE", "CAB_GROUP",
    "BED_GROUP", "CONSUMER_NAME_OPTIMIZED", "MAIN_PART", "ADDITION_PART",
    "YEAR_COMPACT", "FITMENT_SUMMARY", "FITMENT_COUNT", "YEAR_MIN", "YEAR_MAX",
    "L_MIN", "L_MAX", "W_MIN", "W_MAX", "H_MIN", "H_MAX",
    "LENGTH_MARGIN_MIN", "LENGTH_MARGIN_MEDIAN", "ESTIMATED_SALES",
    "CLUSTER_SCORE", "CONFIDENCE", "SAFETY_PASS", "FALLBACK_USED",
    "YEAR_GAP_FILLED", "VALIDATION_STATUS", "REAL_ATOM_COUNT",
    "TITLE_ATOM_COUNT", "INFERRED_ATOM_COUNT", "DUPLICATE_REAL_ATOM_COUNT",
    "PHYSICAL_SKU_CONFLICT_ATOM_COUNT",
]

AUDIT_COLUMNS = [
    "BASE_CLUSTER_ID", "CANDIDATE_TYPE", "CANDIDATE_ROW_COUNT",
    "TARGET_PHYSICAL_SKU", "MERGE_STATUS", "REJECT_REASON",
    "ORIGINAL_ATOM_COUNT", "EXPANDED_ATOM_COUNT", "EXISTING_ATOM_COUNT",
    "INFERRED_NEW_ATOM_COUNT", "MULTI_CLUSTER_ATOM_COUNT",
    "PHYSICAL_SKU_CONFLICT_ATOM_COUNT", "CONFLICT_ATOM_SAMPLES", "CONFLICT_ATOMS",
]


def _write_csv(df: pd.DataFrame, out_path: Path) -> str:
    """Write a consistent UTF-8 CSV with one decimal place for float values."""
    df.to_csv(
        out_path, index=False, encoding="utf-8-sig", float_format=FLOAT_FORMAT
    )
    return str(out_path)


def _summary_row(cluster: dict, split: dict | None = None) -> dict:
    """Build the compact business-facing summary row."""
    split = split or {}
    diagnostics = cluster.get("_optimized_diagnostics") or cluster.get("_diagnostics", {})
    rows = split.get("rows", cluster.get("rows", pd.DataFrame()))
    return {
        "CLUSTER_ID": split.get("split_cluster_id", cluster.get("CLUSTER_ID", "")),
        "PHYSICAL_SKU": cluster.get("自动尺码", ""),
        "TRUCK_TYPE": cluster.get("TRUCK_TYPE", ""),
        "AXLE_TYPE": cluster.get("AXLE_TYPE", ""),
        "CAB_GROUP": cluster.get("CAB_GROUP", ""),
        "BED_GROUP": cluster.get("BED_GROUP", ""),
        "CONSUMER_NAME_OPTIMIZED": cluster.get("CONSUMER_NAME_OPTIMIZED", ""),
        "MAIN_PART": cluster.get("MAIN_PART", ""),
        "ADDITION_PART": cluster.get("ADDITION_PART", ""),
        "YEAR_COMPACT": split.get("year_compact", cluster.get("YEAR_COMPACT", "")),
        "FITMENT_SUMMARY": "" if split else cluster.get("FITMENT_SUMMARY", ""),
        "FITMENT_COUNT": len(rows) if split else cluster.get("fitment_count", 0),
        "YEAR_MIN": cluster.get("year_min", 0),
        "YEAR_MAX": cluster.get("year_max", 0),
        "L_MIN": cluster.get("l_min", 0),
        "L_MAX": cluster.get("l_max", 0),
        "W_MIN": cluster.get("w_min", 0),
        "W_MAX": cluster.get("w_max", 0),
        "H_MIN": cluster.get("h_min", 0),
        "H_MAX": cluster.get("h_max", 0),
        "LENGTH_MARGIN_MIN": cluster.get("length_margin_min", 0),
        "LENGTH_MARGIN_MEDIAN": cluster.get("length_margin_median", 0),
        "ESTIMATED_SALES": split.get("sales", cluster.get("estimated_sales", 0)),
        "CLUSTER_SCORE": cluster.get("CLUSTER_SCORE", 0),
        "CONFIDENCE": cluster.get("CONFIDENCE", ""),
        "SAFETY_PASS": cluster.get("safety_pass", True),
        "FALLBACK_USED": int(bool(cluster.get("_fallback", {}))),
        "YEAR_GAP_FILLED": cluster.get("YEAR_GAP_FILLED", 0),
        "VALIDATION_STATUS": diagnostics.get("MERGE_STATUS", ""),
        "REAL_ATOM_COUNT": diagnostics.get("ORIGINAL_ATOM_COUNT", 0),
        "TITLE_ATOM_COUNT": diagnostics.get("EXPANDED_ATOM_COUNT", 0),
        "INFERRED_ATOM_COUNT": diagnostics.get("INFERRED_NEW_ATOM_COUNT", 0),
        "DUPLICATE_REAL_ATOM_COUNT": diagnostics.get("MULTI_CLUSTER_ATOM_COUNT", 0),
        "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": diagnostics.get(
            "PHYSICAL_SKU_CONFLICT_ATOM_COUNT", 0
        ),
    }


def export_cluster_summary(clusters: list[dict], output_dir: str) -> str:
    """Export the compact, business-facing pickup cluster summary."""
    rows = []
    for c in clusters:
        splits = c.get("_split_names", [])
        if splits and len(splits) > 1:
            for sp in splits:
                rows.append(_summary_row(c, sp))
        else:
            rows.append(_summary_row(c))

    df = pd.DataFrame(rows, columns=SUMMARY_COLUMNS)
    out_path = Path(output_dir) / "pickup_cluster_summary.csv"
    return _write_csv(df, out_path)


def export_cluster_detail(clusters: list[dict], valid_df: pd.DataFrame, output_dir: str) -> str:
    """Export source rows with only the final cluster and physical SKU annotations."""
    row_cluster_map = {}
    for c in clusters:
        split_map = c.get("_split_cluster_map", {})
        if split_map:
            for idx, cid in split_map.items():
                row_cluster_map[idx] = {
                    "CLUSTER_ID": cid,
                    "PHYSICAL_SKU": c["自动尺码"],
                }
        else:
            for idx in c["rows"].index:
                row_cluster_map[idx] = {
                    "CLUSTER_ID": c["CLUSTER_ID"],
                    "PHYSICAL_SKU": c["自动尺码"],
                }

    detail = valid_df.copy()
    detail["CLUSTER_ID"] = detail.index.map(lambda i: row_cluster_map.get(i, {}).get("CLUSTER_ID", ""))
    detail["PHYSICAL_SKU"] = detail.index.map(lambda i: row_cluster_map.get(i, {}).get("PHYSICAL_SKU", ""))
    detail = detail.drop(columns=["自动尺码", "EXCEPTION_REASON"], errors="ignore")
    leading = ["CLUSTER_ID", "PHYSICAL_SKU", "DIMENSION-ID"]
    detail = detail[leading + [col for col in detail.columns if col not in leading]]

    out_path = Path(output_dir) / "pickup_cluster_detail.csv"
    return _write_csv(detail, out_path)


def export_exceptions(exceptions_df: pd.DataFrame, output_dir: str) -> str:
    """Export pickup_cluster_exceptions.csv."""
    out_path = Path(output_dir) / "pickup_cluster_exceptions.csv"
    return _write_csv(exceptions_df, out_path)


def export_gap_investigation(gap_df: pd.DataFrame, output_dir: str) -> str:
    """Export gap_investigation.csv."""
    if gap_df.empty:
        return ""
    out_path = Path(output_dir) / "gap_investigation.csv"
    return _write_csv(gap_df, out_path)


def export_candidate_audit(records: list[dict], output_dir: str) -> str:
    """Export every attempted candidate, including rejected combinations."""
    out_path = Path(output_dir) / "pickup_cluster_candidate_audit.csv"
    audit = pd.DataFrame(records).reindex(columns=AUDIT_COLUMNS)
    return _write_csv(audit, out_path)


def export_fallback_conflicts(clusters: list[dict], output_dir: str) -> str:
    """Export one traceable row per real atom/source record that caused fallback."""
    from atom_verifier import atom_key

    source_records = {}
    for owner in clusters:
        owner_cid = owner.get("CLUSTER_ID", "")
        owner_sku = owner.get("自动尺码", "")
        rows = owner.get("rows", pd.DataFrame())
        for source_index, row in rows.iterrows():
            if pd.isna(row.get("YEAR_START")) or pd.isna(row.get("YEAR_END")):
                continue
            make = row.get("MAKE_NORMALIZED", row.get("MAKE", ""))
            model = row.get("MODEL_FAMILY", row.get("MODEL", ""))
            version = row.get("版本", "")
            cab = row.get("CAB", "")
            bed = row.get("BED", "")
            for year in range(int(row["YEAR_START"]), int(row["YEAR_END"]) + 1):
                key = atom_key(make, model, version, year, cab, bed)
                source_records.setdefault(key, []).append({
                    "EXISTING_PHYSICAL_SKU": owner_sku,
                    "EXISTING_CLUSTER_ID": owner_cid,
                    "SOURCE_DIMENSION_ID": row.get("DIMENSION-ID", ""),
                    "SOURCE_YEAR": row.get("YEAR", ""),
                    "SOURCE_YEAR_START": row.get("YEAR_START", ""),
                    "SOURCE_YEAR_END": row.get("YEAR_END", ""),
                    "SOURCE_L_MM": row.get("L-MM", ""),
                    "SOURCE_W_MM": row.get("W-MM", ""),
                    "SOURCE_H_MM": row.get("H-MM", ""),
                })

    records = []
    for cluster in clusters:
        attempt = cluster.get("_optimization_attempt", {})
        fallback = cluster.get("_fallback", {})
        if not fallback:
            continue
        diag = attempt.get("diagnostics", {})
        target_sku = cluster.get("自动尺码", "")
        conflict_atoms = [
            key for key in str(diag.get("CONFLICT_ATOMS", "")).split("; ") if key
        ]
        for conflict_no, key in enumerate(conflict_atoms, 1):
            make, model, version, year, cab, bed = key.split("|", 5)
            owners = [
                record for record in source_records.get(key, [])
                if record["EXISTING_PHYSICAL_SKU"] != target_sku
            ] or [{}]
            for owner in owners:
                records.append({
                    "CLUSTER_ID": cluster.get("CLUSTER_ID", ""),
                    "TARGET_PHYSICAL_SKU": target_sku,
                    "ATTEMPTED_CONSUMER_NAME": attempt.get("name", ""),
                    "ATTEMPTED_YEAR_RANGES": attempt.get("year_ranges", ""),
                    "ATTEMPTED_GAP_YEARS": attempt.get("gap_years", ""),
                    "ATTEMPT_STATUS": diag.get("MERGE_STATUS", ""),
                    "ATTEMPT_REJECT_REASON": diag.get("REJECT_REASON", ""),
                    "FALLBACK_CONSUMER_NAME": fallback.get("name", ""),
                    "FALLBACK_YEAR_RANGES": fallback.get("year_ranges", ""),
                    "FALLBACK_STATUS": fallback.get("diagnostics", {}).get("MERGE_STATUS", ""),
                    "CONFLICT_NO": conflict_no,
                    "CONFLICT_TYPE": "REAL_ATOM_CROSS_PHYSICAL_SKU",
                    "CONFLICT_ATOM": key,
                    "MAKE": make,
                    "MODEL": model,
                    "VERSION": version,
                    "YEAR": year,
                    "CAB": cab,
                    "BED": bed,
                    **owner,
                })

    columns = [
        "CLUSTER_ID", "TARGET_PHYSICAL_SKU", "ATTEMPTED_CONSUMER_NAME",
        "ATTEMPTED_YEAR_RANGES", "ATTEMPTED_GAP_YEARS", "ATTEMPT_STATUS",
        "ATTEMPT_REJECT_REASON", "FALLBACK_CONSUMER_NAME", "FALLBACK_YEAR_RANGES",
        "FALLBACK_STATUS", "CONFLICT_NO", "CONFLICT_TYPE", "CONFLICT_ATOM",
        "MAKE", "MODEL", "VERSION", "YEAR", "CAB", "BED",
        "EXISTING_PHYSICAL_SKU", "EXISTING_CLUSTER_ID", "SOURCE_DIMENSION_ID",
        "SOURCE_YEAR", "SOURCE_YEAR_START", "SOURCE_YEAR_END",
        "SOURCE_L_MM", "SOURCE_W_MM", "SOURCE_H_MM",
    ]
    out_path = Path(output_dir) / "pickup_cluster_fallback_conflicts.csv"
    return _write_csv(pd.DataFrame(records, columns=columns), out_path)
