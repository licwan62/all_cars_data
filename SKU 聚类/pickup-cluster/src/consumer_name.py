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
    cab_segment = "/".join(str(c) for c in cab_values) if cab_values else cluster.get("CAB_GROUP", "")

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

    return f"{model_segment} {cab_segment} {bed_segment}"


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


def format_bed_segment(rows: pd.DataFrame, include_group: bool = False) -> str:
    """Format actual bed range; add a group only when the full range fits it."""
    lengths = pd.to_numeric(rows.get("BED_LENGTH", pd.Series(dtype=float)), errors="coerce").dropna()
    if lengths.empty:
        return "Bed"
    low, high = float(lengths.min()), float(lengths.max())
    length_text = f"{low:.1f}'" if low == high else f"{low:.1f}'-{high:.1f}'"
    label = ""
    if include_group:
        if high < 6.0:
            label = "Short"
        elif low >= 6.0 and high < 7.0:
            label = "Standard"
        elif low >= 7.0:
            label = "Long"
    return f"{length_text} {label + ' ' if label else ''}Bed"


def _canonical_cab(value: str) -> str:
    """Collapse only explicitly approved consumer-facing CAB synonyms."""
    value = str(value).strip()
    return "Club/Quad" if value in {"Club/Quad", "Quad"} else value


def format_cab_segment(rows: pd.DataFrame, optimize: bool = False) -> str:
    values = [str(v).strip() for v in rows["CAB"].dropna().unique()]
    if optimize:
        values = [_canonical_cab(v) for v in values]
    return "/".join(sorted(set(values)))


def assign_required_exclusions(clusters: list[dict]) -> None:
    """Attach cross-SKU semantic exclusions to broad/versionless candidates.

    A versionless consumer name semantically includes named variants. When a
    named variant (or a child model such as ``1500 Classic``) occupies another
    PHYSICAL_SKU for an overlapping YEAR+CAB+BED, the broad name must exclude
    that exact version/year range.
    """
    for cluster in clusters:
        rows = cluster.get("rows", pd.DataFrame())
        cluster["_required_exclusions"] = []
        if rows.empty:
            continue
        versions = {str(v).strip().lower() for v in rows["版本"].fillna("")}
        model = str(rows["MODEL_FAMILY"].iloc[0]).strip()
        if "" not in versions or model.lower().endswith(" classic"):
            continue
        make = str(rows["MAKE_NORMALIZED"].iloc[0]).strip()
        target_sku = cluster.get("自动尺码", "")
        ranges_by_label = {}
        for other in clusters:
            if other is cluster or other.get("自动尺码", "") == target_sku:
                continue
            other_rows = other.get("rows", pd.DataFrame())
            if other_rows.empty:
                continue
            for _, left in rows.iterrows():
                for _, right in other_rows.iterrows():
                    if str(right.get("MAKE_NORMALIZED", "")).strip() != make:
                        continue
                    other_model = str(right.get("MODEL_FAMILY", "")).strip()
                    version = str(right.get("版本", "") or "").strip().lower()
                    if other_model.lower() == model.lower():
                        label = SPECIAL_VARIANT_MAP.get(version)
                    elif other_model.lower() == f"{model.lower()} classic":
                        label = "Classic"
                    else:
                        continue
                    if not label:
                        continue
                    if _canonical_cab(left.get("CAB", "")) != _canonical_cab(right.get("CAB", "")):
                        continue
                    try:
                        if abs(float(left.get("BED")) - float(right.get("BED"))) > 0.01:
                            continue
                    except (TypeError, ValueError):
                        if str(left.get("BED", "")) != str(right.get("BED", "")):
                            continue
                    start = max(int(left["YEAR_START"]), int(right["YEAR_START"]))
                    end = min(int(left["YEAR_END"]), int(right["YEAR_END"]))
                    if start <= end:
                        ranges_by_label.setdefault(label, []).append((start, end))
        exclusions = []
        for label, ranges in ranges_by_label.items():
            merged = merge_year_ranges(ranges)
            exclusions.append((merged[0][0], f"{format_year_ranges(merged)} {label}"))
        cluster["_required_exclusions"] = [text for _, text in sorted(exclusions)]


# ── Special variant labeling (Raptor / DRW / TRX / RHO / etc.) ─────

# Map raw 版本 values → display labels for special variants
SPECIAL_VARIANT_MAP = {
    "raptor": "Raptor",
    "drw": "DRW",
    "classic drw": "DRW",
    "r/v drw": "DRW",
    "trx": "TRX",
    "rho": "RHO",
    "lightning": "Lightning",
    "ev": "EV",
    "at4x": "AT4X",
    "zr2": "ZR2",
    "trail boss": "Trail Boss",
    "trd pro": "TRD Pro",
    "trd pro/trailhunter": "TRD Pro",
    "rubicon": "Rubicon",
    "rubicon/mojave": "Rubicon",
    "mojave": "Mojave",
    "xtreme": "Xtreme",
    "xrt": "XRT",
    "lobo": "Lobo",
    "longhorn": "Longhorn",
    "sport trac": "Sport Trac",
    "dual/quad/adventure": "Adventure",
}


def _get_variant_labels(row) -> set[str]:
    """Get the set of special variant labels for a row."""
    version = str(row.get("版本", "")).strip().lower()
    labels = set()
    if version in SPECIAL_VARIANT_MAP:
        labels.add(SPECIAL_VARIANT_MAP[version])
    return labels


def _is_special_variant_row(row) -> bool:
    """Check if a row is any special variant."""
    return len(_get_variant_labels(row)) > 0


def _cluster_variant_labels(cluster: dict) -> set[str]:
    """Get all unique variant labels in the cluster."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return set()
    labels = set()
    for _, row in rows.iterrows():
        labels |= _get_variant_labels(row)
    return labels


def _cluster_has_special_variant(cluster: dict) -> bool:
    """Check if any row in the cluster is a special variant."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return False
    return rows.apply(_is_special_variant_row, axis=1).any()


def _cluster_is_all_special_variant(cluster: dict) -> bool:
    """Check if ALL rows in the cluster are special variants."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return False
    return rows.apply(_is_special_variant_row, axis=1).all()


def _same_model_has_special_cluster(cluster: dict, all_clusters: list[dict]) -> set[str]:
    """Get variant labels from other clusters of the same model."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return set()

    makes = set(rows["MAKE_NORMALIZED"].unique())
    models = set(rows["MODEL_FAMILY"].unique())

    other_labels = set()
    for other in all_clusters:
        if other is cluster:
            continue
        other_rows = other.get("rows", pd.DataFrame())
        if other_rows.empty:
            continue
        other_makes = set(other_rows["MAKE_NORMALIZED"].unique())
        other_models = set(other_rows["MODEL_FAMILY"].unique())
        if makes & other_makes and models & other_models:
            if _cluster_has_special_variant(other):
                other_labels |= _cluster_variant_labels(other)
    return other_labels


def add_variant_label(name: str, cluster: dict, all_clusters: list[dict]) -> str:
    """Insert special variant label into a consumer name, right after the model name.

    Rules:
    - All rows are special variants → "(Variant1, Variant2)"
    - Mixed special + normal → "(Includes Variant1, Variant2)"
    - No special, but same model has special cluster → "(Excludes Variant1, Variant2)"
    - Otherwise → no change

    Format: "Make Model (Includes Raptor, DRW) YYYY-YYYY | CAB | BED"
    """
    import re

    if not name:
        return name

    my_labels = _cluster_variant_labels(cluster)
    has_special = _cluster_has_special_variant(cluster)
    all_special = _cluster_is_all_special_variant(cluster)
    other_labels = _same_model_has_special_cluster(cluster, all_clusters)

    # Exclude labels from "other" that we already have
    exclusive_labels = other_labels - my_labels

    if all_special and my_labels:
        # Pure variant: "Ford F-150 Raptor 2010-2019 | ..."
        label = ", ".join(sorted(my_labels))
    elif has_special and my_labels:
        # Mixed: "Ford F-150 (Includes Raptor, Tremor) ..."
        label_str = ", ".join(sorted(my_labels))
        label = f"(Includes {label_str})"
    elif exclusive_labels:
        # Excluded: "Ford F-150 (Excludes Lightning, Raptor) ..."
        label_str = ", ".join(sorted(exclusive_labels))
        label = f"(Excludes {label_str})"
    else:
        return name

    m = re.search(r'\b(\d{4})(?:-|/|\s)', name)
    if m:
        pos = m.start()
        # name[:pos] ends with a trailing space (e.g. "Ford F-150 ")
        return name[:pos].rstrip() + " " + label + " " + name[pos:]

    return f"{name} {label}"


def generate_merged_consumer_name(cluster: dict, all_clusters: list[dict]) -> str:
    """Generate a merged consumer name that includes all variants.

    Format for single-model clusters:
        Ford F-150 2001-2026 | SuperCrew | 5.5' Short Bed | Raptor & Tremor Included

    Pure variant cluster:
        Ford F-150 Raptor 2010-2020 | SuperCab | 5.5' Short Bed

    No variants:
        Ford F-150 1997-2026 | Regular | 8.0' Long Bed
    """
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return "Unknown"

    # Merge all year ranges across all rows
    year_ranges = []
    for _, row in rows.iterrows():
        if pd.notna(row.get("YEAR_START")) and pd.notna(row.get("YEAR_END")):
            year_ranges.append((int(row["YEAR_START"]), int(row["YEAR_END"])))
    merged_years = merge_year_ranges(year_ranges)
    year_str = format_year_ranges(merged_years)

    make = rows["MAKE_NORMALIZED"].iloc[0]
    model = rows["MODEL_FAMILY"].iloc[0]

    cab_values = sorted(rows["CAB"].dropna().unique().tolist())
    cab_segment = "/".join(str(c) for c in cab_values)

    # Base name states only the observed range. Classification belongs to the
    # optimized name and must be valid for the entire range.
    bed_segment = format_bed_segment(rows, include_group=False)

    # Determine variant labeling
    has_special = _cluster_has_special_variant(cluster)
    all_special = _cluster_is_all_special_variant(cluster)
    my_labels = _cluster_variant_labels(cluster)

    base_name = f"{make} {model} {year_str} {cab_segment} {bed_segment}"

    if all_special and len(my_labels) == 1:
        # Pure single variant: "Ford F-150 Raptor 2010-2020 SuperCab ..."
        variant = list(my_labels)[0]
        base_name = f"{make} {model} {variant} {year_str} {cab_segment} {bed_segment}"
    elif has_special and not all_special:
        # Mixed: "Ford F-150 2001-2026 SuperCrew ... Raptor & Tremor Included"
        included = " & ".join(sorted(my_labels))
        base_name = f"{base_name} {included} Included"
    elif has_special and all_special and len(my_labels) > 1:
        # Multiple pure variants: "Ford F-150 2001-2026 ... Raptor & Tremor"
        included = " & ".join(sorted(my_labels))
        base_name = f"{base_name} {included}"

    return base_name


def generate_variant_split_names(cluster: dict, all_clusters: list[dict]) -> list[dict]:
    """Split a cluster into sub-records by variant composition.

    Each sub-record has its own year range and variant label.
    Returns a list of dicts with keys: name, year_compact, variant_label, rows, sales.

    This prevents conflicts where "(Includes Raptor)" is applied to years
    that actually have a separate pure-Raptor cluster.
    """
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return []

    # Create a variant key column for grouping
    rows_copy = rows.copy()
    rows_copy["_variant_key"] = rows_copy.apply(
        lambda r: ", ".join(sorted(_get_variant_labels(r))) if _get_variant_labels(r) else "__NONE__",
        axis=1
    )

    groups = []
    base_cid = cluster.get("CLUSTER_ID", "")
    for key, group in rows_copy.groupby("_variant_key", sort=False):
        # Merge year ranges for this group
        year_ranges = []
        for _, row in group.iterrows():
            if pd.notna(row.get("YEAR_START")) and pd.notna(row.get("YEAR_END")):
                year_ranges.append((int(row["YEAR_START"]), int(row["YEAR_END"])))
        merged = merge_year_ranges(year_ranges)
        year_str = format_year_ranges(merged)

        make = group["MAKE_NORMALIZED"].iloc[0]
        model = group["MODEL_FAMILY"].iloc[0]
        cab_values = sorted(group["CAB"].dropna().unique().tolist())
        cab_segment = "/".join(str(c) for c in cab_values)
        bed_group = cluster.get("BED_GROUP", "")
        bed_display = {"SHORT": "Short Bed", "STANDARD": "Standard Bed",
                       "LONG": "Long Bed"}.get(bed_group, bed_group)
        bed_lengths = group["BED_LENGTH"].dropna()
        if len(bed_lengths) > 0:
            bed_min = bed_lengths.min()
            bed_max = bed_lengths.max()
            if bed_min == bed_max:
                bed_segment = f"{bed_display} ({bed_min:.1f}')"
            else:
                bed_segment = f"{bed_display} ({bed_min:.1f}'-{bed_max:.1f}')"
        else:
            bed_segment = bed_display

        variant_labels = set()
        if key != "__NONE__":
            variant_labels = set(key.split(", "))

        # Build the name with variant label
        if variant_labels:
            label_str = ", ".join(sorted(variant_labels))
            name = f"{make} {model} {label_str} {year_str} {cab_segment} {bed_segment}"
        else:
            name = f"{make} {model} {year_str} {cab_segment} {bed_segment}"

        # Build split-specific CLUSTER_ID
        if key != "__NONE__":
            variant_slug = key.replace(", ", "-").replace(" ", "-")
            split_cluster_id = f"{base_cid}__{variant_slug}"
        else:
            split_cluster_id = base_cid

        groups.append({
            "name": name,
            "year_compact": year_str,
            "variant_label": key if key != "__NONE__" else "",
            "rows": group,
            "sales": group["预估销量 的总和"].sum(),
            "split_cluster_id": split_cluster_id,
        })

    return groups
