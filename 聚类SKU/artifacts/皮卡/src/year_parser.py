"""Parse YEAR ranges into YEAR_START and YEAR_END."""

import pandas as pd
import re


def parse_year(year_str: str) -> tuple[int | None, int | None]:
    """Parse a year string like '2015-2018' or '2025' into (start, end)."""
    if pd.isna(year_str) or str(year_str).strip() == "":
        return None, None

    s = str(year_str).strip()
    # pattern: "YYYY-YYYY", "YYYY", "YYYY-YY"
    m = re.match(r"^(\d{4})\s*-\s*(\d{4})$", s)
    if m:
        return int(m.group(1)), int(m.group(2))

    m = re.match(r"^(\d{4})$", s)
    if m:
        y = int(m.group(1))
        return y, y

    return None, None


def parse_years(df: pd.DataFrame) -> pd.DataFrame:
    """Add YEAR_START and YEAR_END columns."""
    parsed = df["YEAR"].apply(parse_year)
    df["YEAR_START"] = parsed.apply(lambda x: x[0])
    df["YEAR_END"] = parsed.apply(lambda x: x[1])
    return df


def merge_year_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping/adjacent year ranges."""
    if not ranges:
        return []

    sorted_ranges = sorted(ranges)
    merged = []

    for start, end in sorted_ranges:
        if not merged:
            merged.append([start, end])
            continue
        if start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return [(s, e) for s, e in merged]


def format_year_ranges(ranges: list[tuple[int, int]]) -> str:
    """Format merged year ranges as a compact string like '1983-1992/1996-2000'."""
    if not ranges:
        return ""
    parts = []
    for s, e in ranges:
        if s == e:
            parts.append(str(s))
        else:
            parts.append(f"{s}-{e}")
    return "/".join(parts)


def year_range_to_compact(start: int, end: int) -> str:
    """Format a single year range."""
    if start == end:
        return str(start)
    return f"{start}-{end}"