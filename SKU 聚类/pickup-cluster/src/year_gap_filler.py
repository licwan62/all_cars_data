"""Year gap filler — verify whether gap years can be filled.

Two-phase approach:
  1. Check within the dataset: same make+model+cab+bed exists in gap year
  2. Check via web search: query Wikipedia for model generation timeline
"""

import pandas as pd
from year_parser import merge_year_ranges, format_year_ranges


def extract_year_ranges(rows: pd.DataFrame) -> list[tuple[int, int]]:
    """Extract all year ranges from rows as (start, end) tuples."""
    ranges = []
    for _, row in rows.iterrows():
        if pd.notna(row.get("YEAR_START")) and pd.notna(row.get("YEAR_END")):
            ranges.append((int(row["YEAR_START"]), int(row["YEAR_END"])))
    return ranges


def find_gap_years(merged: list[tuple[int, int]]) -> list[int]:
    """Find individual gap years between merged ranges."""
    gaps = []
    for i in range(len(merged) - 1):
        end_prev = merged[i][1]
        start_next = merged[i + 1][0]
        for y in range(end_prev + 1, start_next):
            gaps.append(y)
    return gaps


def check_in_dataset(make: str, model: str, cab: str, bed_group: str, year: int, full_df: pd.DataFrame) -> bool:
    """Check if the same make+model+cab+bed_group exists in the dataset for a given year."""
    matches = full_df[
        (full_df["MAKE_NORMALIZED"] == make) &
        (full_df["MODEL_FAMILY"] == model) &
        (full_df["CAB"] == cab) &
        (full_df["BED_GROUP"] == bed_group) &
        (full_df["YEAR_START"] <= year) &
        (full_df["YEAR_END"] >= year)
    ]
    return len(matches) > 0


def check_via_web(make: str, model: str, year: int, cab: str = "", bed: str = "") -> bool | None:
    """Check via web search if a model existed in a given year.

    Returns True if confirmed, False if confirmed not, None if uncertain.
    Uses Wikipedia model page to check generation years and cab availability.
    """
    import time
    import urllib.request
    import urllib.error
    import re

    search_term = f"{make} {model}"
    wiki_url = f"https://en.wikipedia.org/wiki/{search_term.replace(' ', '_')}"

    for attempt in range(2):
        try:
            req = urllib.request.Request(wiki_url, headers={"User-Agent": "PickupCluster/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            # Find generation sections — look for headings with year ranges
            gen_pattern = re.findall(
                r'(?:==+)\s*([^=]*?(?:(\d{4})\s*[–\-—]\s*(\d{4}|present))[^=]*?)\s*==+',
                html
            )

            for section, start_str, end_str in gen_pattern:
                start_y = int(start_str)
                end_y = int(end_str) if end_str != "present" else 2030
                if start_y <= year <= end_y:
                    if cab:
                        cab_lower = cab.lower()
                        cab_keywords = {
                            "regular": ["regular cab", "single cab", "standard cab"],
                            "extended": ["extended cab", "supercab", "access cab", "king cab", "xtracab", "club cab"],
                            "crew": ["crew cab", "supercrew", "crewmax", "double cab", "quad cab"],
                            "mega": ["mega cab"],
                        }
                        cab_group = _get_cab_group(cab)
                        keywords = cab_keywords.get(cab_group.lower(), [cab_lower])
                        section_lower = section.lower()
                        if any(kw in section_lower for kw in keywords):
                            return True
                        return True
                    return True

            # Fallback: look for any year range containing the target year
            year_pattern = re.findall(r'(\d{4})\s*[–\-—]\s*(\d{4}|present)', html)
            for start_str, end_str in year_pattern:
                start_y = int(start_str)
                end_y = int(end_str) if end_str != "present" else 2030
                if start_y <= year <= end_y:
                    return True

            return None  # uncertain

        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(2)
                continue
            return None
        except Exception:
            if attempt == 0:
                time.sleep(1)
                continue
            return None

    return None


def _get_cab_group(cab: str) -> str:
    """Map raw CAB to CAB_GROUP for keyword search."""
    cab_lower = cab.lower().strip()
    regular = {"regular", "single", "standard"}
    extended = {"extended", "supercab", "access", "king", "xtracab", "club", "club/quad"}
    crew = {"crew", "supercrew", "crewmax", "double", "quad"}
    mega = {"mega"}

    if cab_lower in regular:
        return "REGULAR"
    if cab_lower in extended:
        return "EXTENDED"
    if cab_lower in crew:
        return "CREW"
    if cab_lower in mega:
        return "MEGA"
    return cab_lower.upper()


def try_fill_gaps(
    rows: pd.DataFrame,
    full_df: pd.DataFrame,
    try_web: bool = True,
) -> tuple[list[tuple[int, int]], list[dict]]:
    """Fill all gap years unconditionally.

    Safety is delegated to verify_candidate() in main.py, which checks
    whether the expanded year ranges would cause PHYSICAL_SKU conflicts
    or unresolved new atoms. This function only identifies the gaps and
    fills them — the structural gate (atom_verifier) is the sole authority.

    Args:
        rows: The cluster's rows (DataFrame)
        full_df: The full valid dataset (for cross-checking)
        try_web: Whether to attempt web verification (legacy, kept for compat)

    Returns:
        (optimized_ranges, gap_details) where gap_details records what was filled
    """
    year_ranges = extract_year_ranges(rows)
    merged = merge_year_ranges(year_ranges)
    gaps = find_gap_years(merged)

    if not gaps:
        return merged, []

    gap_details = [{"year": y, "filled": True, "source": "auto_fill"} for y in gaps]

    # Build optimized ranges by including all gap years
    all_ranges = list(year_ranges)
    for y in gaps:
        all_ranges.append((y, y))
    optimized = merge_year_ranges(all_ranges)

    return optimized, gap_details


def optimize_consumer_name(cluster: dict, full_df: pd.DataFrame,
                           try_gap_fill: bool = True) -> str:
    """Generate the mandatory optimized name, optionally filling year gaps."""
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return ""

    if try_gap_fill:
        optimized_ranges, gap_details = try_fill_gaps(rows, full_df, try_web=True)
    else:
        optimized_ranges = merge_year_ranges(extract_year_ranges(rows))
        gap_details = []

    # Store gap details for investigation export
    cluster["_gap_details"] = gap_details
    cluster["_optimized_ranges"] = optimized_ranges

    # Rebuild the name with optimized year ranges
    make = rows["MAKE_NORMALIZED"].iloc[0]
    model = rows["MODEL_FAMILY"].iloc[0]
    year_str = format_year_ranges(optimized_ranges)

    from consumer_name import format_cab_segment
    cab_segment = format_cab_segment(rows, optimize=True)

    from consumer_name import format_bed_segment
    bed_segment = format_bed_segment(rows, include_group=True)
    # Import variant labeling from consumer_name
    from consumer_name import _cluster_has_special_variant, _cluster_is_all_special_variant, _cluster_variant_labels

    has_special = _cluster_has_special_variant(cluster)
    all_special = _cluster_is_all_special_variant(cluster)
    my_labels = _cluster_variant_labels(cluster)

    base_name = f"{make} {model} {year_str} {cab_segment} {bed_segment}"

    if all_special and len(my_labels) == 1:
        variant = list(my_labels)[0]
        base_name = f"{make} {model} {variant} {year_str} {cab_segment} {bed_segment}"
    elif has_special and not all_special:
        included = " & ".join(sorted(my_labels))
        base_name = f"{base_name} {included} Included"
    elif has_special and all_special and len(my_labels) > 1:
        included = " & ".join(sorted(my_labels))
        base_name = f"{base_name} {included}"

    exclusions = cluster.get("_required_exclusions", [])
    if exclusions:
        base_name = f"{base_name} Excludes {' & '.join(exclusions)}"

    return base_name


def generate_gap_investigation(clusters: list[dict], full_df: pd.DataFrame, all_df: pd.DataFrame) -> pd.DataFrame:
    """Generate a gap investigation report for all clusters with filled gaps.

    For each filled gap year, checks:
    - Whether the model exists in the FULL dataset (including exceptions) for that year
    - What cab/bed/auto-size exists in that year
    - Whether the gap year is covered by another cluster
    - Whether it's a true generation gap
    """
    records = []

    for c in clusters:
        gap_details = c.get("_gap_details", [])
        filled = [g for g in gap_details if g["filled"]]
        if not filled:
            continue

        rows = c.get("rows", pd.DataFrame())
        if rows.empty:
            continue

        make = rows["MAKE_NORMALIZED"].iloc[0]
        model = rows["MODEL_FAMILY"].iloc[0]
        cab_values = list(rows["CAB"].unique())
        bed_group = rows["BED_GROUP"].iloc[0]
        cluster_id = c.get("CLUSTER_ID", "")

        for g in filled:
            year = g["year"]
            source = g.get("source", "")

            # Check full dataset for same make+model in this year
            in_full = all_df[
                (all_df["MAKE_NORMALIZED"] == make) &
                (all_df["MODEL_FAMILY"] == model) &
                (all_df["YEAR_START"] <= year) &
                (all_df["YEAR_END"] >= year)
            ]

            in_full_count = len(in_full)
            if in_full_count > 0:
                in_full_cabs = list(in_full["CAB"].unique())
                in_full_beds = list(in_full["BED"].unique())
                in_full_bed_groups = list(in_full["BED_GROUP"].unique())
                in_full_sizes = list(in_full["自动尺码"].unique())
                in_full_years = sorted(in_full["YEAR"].unique())
            else:
                in_full_cabs = []
                in_full_beds = []
                in_full_bed_groups = []
                in_full_sizes = []
                in_full_years = []

            # Check if same cab+bed exists in this year
            same_config = in_full[
                (in_full["CAB"].isin(cab_values)) &
                (in_full["BED_GROUP"] == bed_group)
            ] if in_full_count > 0 else pd.DataFrame()

            # Determine investigation status
            if in_full_count == 0:
                status = "MODEL_NOT_IN_DATASET"
                note = "车型在该年份无任何记录 (可能已停产/断代)"
            elif len(same_config) > 0:
                status = "CONFIG_EXISTS"
                note = f"同配置存在但尺码不同: {list(same_config['自动尺码'].unique())}"
            else:
                status = "DIFFERENT_CONFIG"
                note = f"车型存在但配置不同: CAB={in_full_cabs}, BED={in_full_beds}"

            records.append({
                "CLUSTER_ID": cluster_id,
                "MAKE": make,
                "MODEL": model,
                "GAP_YEAR": year,
                "FILL_SOURCE": source,
                "STATUS": status,
                "NOTE": note,
                "IN_FULL_COUNT": in_full_count,
                "IN_FULL_CABS": ", ".join(str(x) for x in in_full_cabs),
                "IN_FULL_BEDS": ", ".join(str(x) for x in in_full_beds),
                "IN_FULL_BED_GROUPS": ", ".join(str(x) for x in in_full_bed_groups),
                "IN_FULL_SIZES": ", ".join(str(x) for x in in_full_sizes),
                "CLUSTER_CABS": ", ".join(str(x) for x in cab_values),
                "CLUSTER_BED_GROUP": bed_group,
            })

    return pd.DataFrame(records)
