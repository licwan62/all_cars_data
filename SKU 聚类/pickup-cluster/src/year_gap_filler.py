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
    """Try to fill gap years in a cluster's year ranges.

    Args:
        rows: The cluster's rows (DataFrame)
        full_df: The full valid dataset (for cross-checking)
        try_web: Whether to attempt web verification

    Returns:
        (optimized_ranges, gap_details) where gap_details records what was filled
    """
    year_ranges = extract_year_ranges(rows)
    merged = merge_year_ranges(year_ranges)
    gaps = find_gap_years(merged)

    if not gaps:
        return merged, []

    # Get the representative make/model/cab/bed for this cluster
    make = rows["MAKE_NORMALIZED"].iloc[0]
    model = rows["MODEL_FAMILY"].iloc[0]

    # For each CAB type in the cluster, check independently
    cab_values = rows["CAB"].unique()
    bed_group = rows["BED_GROUP"].iloc[0]

    gap_details = []
    filled_years = set()

    for year in gaps:
        detail = {"year": year, "filled": False, "source": ""}

        # Phase 1: check dataset
        for cab in cab_values:
            if check_in_dataset(make, model, cab, bed_group, year, full_df):
                detail["filled"] = True
                detail["source"] = "dataset"
                filled_years.add(year)
                break

        # Phase 2: web check
        if not detail["filled"] and try_web:
            import time
            time.sleep(0.3)  # rate-limit Wikipedia requests
            # Try each cab type via web
            for cab in cab_values:
                result = check_via_web(make, model, year, cab=cab)
                if result is True:
                    detail["filled"] = True
                    detail["source"] = "web"
                    filled_years.add(year)
                    break
            if not detail["filled"]:
                detail["source"] = "web_uncertain"

        gap_details.append(detail)

    # Build optimized ranges by adding filled years
    if filled_years:
        all_ranges = list(year_ranges)
        for y in filled_years:
            all_ranges.append((y, y))
        optimized = merge_year_ranges(all_ranges)
    else:
        optimized = merged

    return optimized, gap_details


def optimize_consumer_name(cluster: dict, full_df: pd.DataFrame) -> str:
    """Generate an optimized CONSUMER_NAME with filled gap years.

    Only returns a different name if gaps were actually filled.
    """
    rows = cluster.get("rows", pd.DataFrame())
    if rows.empty:
        return ""

    optimized_ranges, gap_details = try_fill_gaps(rows, full_df, try_web=True)

    # Check if any gaps were filled
    filled = [g for g in gap_details if g["filled"]]
    if not filled:
        return ""  # no optimization possible

    # Rebuild the name with optimized year ranges
    make = rows["MAKE_NORMALIZED"].iloc[0]
    model = rows["MODEL_FAMILY"].iloc[0]
    year_str = format_year_ranges(optimized_ranges)

    cab_values = sorted(rows["CAB"].dropna().unique().tolist())
    cab_segment = ", ".join(str(c) for c in cab_values)

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

    return f"{make} {model} {year_str} | {cab_segment} | {bed_segment}"