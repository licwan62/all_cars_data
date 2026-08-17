"""Generate consumer-facing cluster names and fitment summaries."""

import pandas as pd
from year_parser import merge_year_ranges, format_year_ranges


def _make_display_name(make: str, model: str, display_config: dict | None = None) -> str:
    """Get a consumer-friendly display name for a make+model combination."""
    if display_config:
        key = (make.strip(), model.strip())
        if key in display_config:
            return display_config[key]
    return f"{make} {model}"


def load_display_names(config_dir: str) -> dict:
    """Load model display name overrides from config."""
    from pathlib import Path
    csv_path = Path(config_dir) / "model_display_name.csv"
    if not csv_path.exists():
        return {}
    df = pd.read_csv(csv_path)
    lookup = {}
    for _, row in df.iterrows():
        key = (str(row["make"]).strip(), str(row["model"]).strip())
        lookup[key] = str(row["display_name"]).strip()
    return lookup


def generate_consumer_name(cluster: dict) -> str:
    """Generate consumer-facing cluster name.

    Format:
        Ford F-150 2001-2026 / Chevrolet Silverado 1500 2004-2026 | Crew, SuperCrew, CrewMax | Short Bed (5.3'-5.8')
    """
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return "Unknown"

    # --- Models with year ranges, sorted by sales ---
    model_sales = rows.groupby(["MAKE_NORMALIZED", "MODEL_FAMILY"])["预估销量 的总和"].sum()
    model_sales = model_sales.sort_values(ascending=False)

    model_parts = []
    for (make, model), _ in model_sales.items():
        # get merged year range for this make-model pair
        model_rows = rows[(rows["MAKE_NORMALIZED"] == make) & (rows["MODEL_FAMILY"] == model)]
        year_ranges = []
        for _, row in model_rows.iterrows():
            if pd.notna(row.get("YEAR_START")) and pd.notna(row.get("YEAR_END")):
                year_ranges.append((int(row["YEAR_START"]), int(row["YEAR_END"])))
        merged = merge_year_ranges(year_ranges)
        year_str = format_year_ranges(merged)
        model_parts.append(f"{make} {model} {year_str}")

    if not model_parts:
        return "Unknown"

    # Limit to first 5 models for readability
    if len(model_parts) > 5:
        model_parts = model_parts[:5]
        model_parts.append("...")

    model_segment = " / ".join(model_parts)

    # --- CAB: all distinct raw CAB values from the cluster ---
    cab_values = sorted(rows["CAB"].dropna().unique().tolist())
    cab_segment = ", ".join(str(c) for c in cab_values) if cab_values else cluster.get("CAB_GROUP", "")

    # --- BED: group label + length range ---
    bed_group = cluster.get("BED_GROUP", "")
    bed_display = {"SHORT": "Short Bed", "STANDARD": "Standard Bed",
                   "LONG": "Long Bed"}.get(bed_group, bed_group)
    bed_lengths = rows["BED_LENGTH"].dropna()
    if len(bed_lengths) > 0:
        bed_min = bed_lengths.min()
        bed_max = bed_lengths.max()
        if bed_min == bed_max:
            bed_segment = f"{bed_display} ({bed_min:.1f}')"
        else:
            bed_segment = f"{bed_display} ({bed_min:.1f}'-{bed_max:.1f}')"
    else:
        bed_segment = bed_display

    return f"{model_segment} | {cab_segment} | {bed_segment}"


def generate_fitment_summary(cluster: dict) -> str:
    """Generate per-model fitment summary for the cluster.

    Example:
        Ford F-150 2000-2025
        Chevy Silverado 1500 2000-2025
        Ram 1500 2002-2025
    """
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return ""

    lines = []
    for (make, model), group in rows.groupby(["MAKE_NORMALIZED", "MODEL_FAMILY"]):
        year_ranges = []
        for _, row in group.iterrows():
            if pd.notna(row.get("YEAR_START")) and pd.notna(row.get("YEAR_END")):
                year_ranges.append((int(row["YEAR_START"]), int(row["YEAR_END"])))
        merged = merge_year_ranges(year_ranges)
        year_str = format_year_ranges(merged)
        lines.append(f"{make} {model} {year_str}")

    return "\n".join(lines)


def generate_year_compact(cluster: dict) -> str:
    """Generate compact year range for the whole cluster."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return ""

    year_ranges = []
    for _, row in rows.iterrows():
        if pd.notna(row.get("YEAR_START")) and pd.notna(row.get("YEAR_END")):
            year_ranges.append((int(row["YEAR_START"]), int(row["YEAR_END"])))
    merged = merge_year_ranges(year_ranges)
    return format_year_ranges(merged)


# ── Raptor / Widebody variant labeling ──────────────────────────────

def _is_raptor_row(row) -> bool:
    """Check if a row is a Raptor/TRX/widebody variant."""
    version = str(row.get("版本", "")).strip()
    return version.lower() in ("raptor", "trx")


def _is_trx_row(row) -> bool:
    """Check if a row is a TRX variant."""
    version = str(row.get("版本", "")).strip()
    return version.lower() == "trx"


def _cluster_has_raptor(cluster: dict) -> bool:
    """Check if any row in the cluster is a Raptor variant."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return False
    return rows.apply(_is_raptor_row, axis=1).any()


def _cluster_is_all_raptor(cluster: dict) -> bool:
    """Check if ALL rows in the cluster are Raptor variants."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return False
    return rows.apply(_is_raptor_row, axis=1).all()


def _same_model_has_raptor_cluster(cluster: dict, all_clusters: list[dict]) -> bool:
    """Check if the same model (MAKE + MODEL_FAMILY) has a Raptor-only cluster elsewhere."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return False

    makes = set(rows["MAKE_NORMALIZED"].unique())
    models = set(rows["MODEL_FAMILY"].unique())

    for other in all_clusters:
        if other is cluster:
            continue
        other_rows = other.get("rows", pd.DataFrame())
        if other_rows.empty:
            continue
        other_makes = set(other_rows["MAKE_NORMALIZED"].unique())
        other_models = set(other_rows["MODEL_FAMILY"].unique())
        # Check if there's overlap in make+model
        if makes & other_makes and models & other_models:
            if _cluster_has_raptor(other):
                return True
    return False


def add_raptor_label(name: str, cluster: dict, all_clusters: list[dict]) -> str:
    """Append Raptor/TRX label to a consumer name.

    Rules:
    - All Raptor rows → "(Raptor)"
    - Mixed Raptor + non-Raptor → "(Includes Raptor)"
    - No Raptor, but same model has Raptor cluster → "(Excludes Raptor)"
    - Otherwise → no change
    """
    if not name:
        return name

    has_raptor = _cluster_has_raptor(cluster)
    all_raptor = _cluster_is_all_raptor(cluster)
    has_other_raptor = _same_model_has_raptor_cluster(cluster, all_clusters)

    if all_raptor:
        return f"{name} (Raptor)"
    elif has_raptor:
        return f"{name} (Includes Raptor)"
    elif has_other_raptor:
        return f"{name} (Excludes Raptor)"

    return name