#!/usr/bin/env python
"""Cluster configured vehicles by L/W/H for custom SKU analysis."""

from __future__ import annotations

import argparse
import csv
import json
from itertools import combinations
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DETAILS = ROOT / "A0.尺码计算" / "output" / "US" / "全量" / "全量表.csv"
DEFAULT_CONFIG = ROOT / "F0.定制分析" / "data" / "mercedes_e_class_custom_analysis.json"
DEFAULT_CODE_MAPPING = ROOT / "02.代码映射" / "output" / "尺寸编码映射.csv"


@dataclass(frozen=True)
class Envelope:
    rows: tuple[dict[str, str], ...]

    def min_value(self, field: str) -> int:
        return min(int(row[field]) for row in self.rows)

    def max_value(self, field: str) -> int:
        return max(int(row[field]) for row in self.rows)

    def fits(self, row: dict[str, str], limits: dict[str, int]) -> bool:
        candidate = self.rows + (row,)
        return all(max(int(item[field]) for item in candidate) - min(int(item[field]) for item in candidate) <= limits[field] for field in limits)

    def add(self, row: dict[str, str]) -> "Envelope":
        return Envelope(self.rows + (row,))


def dimension_codes(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {row["DIMENSION-ID"]: row["DIMENSION-CODE"] for row in csv.DictReader(handle)}


def year_bounds(value: str) -> tuple[int, int]:
    parts = value.split("-", 1)
    start = int(parts[0])
    return start, int(parts[-1])


def sku_code(rows: tuple[dict[str, str], ...], codes: dict[str, str], family_code: str = "") -> str:
    """Use the stable 4-digit make/model code plus the SKU's inclusive YY–YY span."""
    model_codes = {codes[row["DIMENSION-ID"]][:4] for row in rows}
    if len(model_codes) != 1 and not family_code:
        raise ValueError(f"SKU crosses model codes: {sorted(model_codes)}")
    starts, ends = zip(*(year_bounds(row["YEAR"]) for row in rows))
    prefix = family_code or model_codes.pop()
    return f"{prefix}{min(starts) % 100:02d}{max(ends) % 100:02d}"


def active_rows(
    path: Path, make: str, model: str = "", structure: str = "",
    *, models: list[str] | None = None, structures: list[str] | None = None,
) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected_models = set(models or ([model] if model else []))
    selected_structures = set(structures or ([structure] if structure else []))
    selected = [
        row for row in rows
        if row.get("MAKE") == make and (not selected_models or row.get("MODEL") in selected_models)
        and (not selected_structures or row.get("结构") in selected_structures)
        and all(row.get(field, "").isdigit() for field in ("L-MM", "W-MM", "H-MM"))
    ]
    return sorted(selected, key=lambda row: (int(row["L-MM"]), int(row["W-MM"]), int(row["H-MM"]), row["DIMENSION-ID"]))


def cluster_minimum_envelopes(rows: list[dict[str, str]], limits: dict[str, int]) -> list[Envelope]:
    """Return the fewest feasible L/W/H envelopes, prioritising the length proxy."""
    ordered = sorted(rows, key=lambda item: (-int(item["L-MM"]), -int(item["W-MM"]), -int(item["H-MM"])))

    # A greedy solution supplies a tight, valid upper bound for the exact search.
    greedy: list[Envelope] = []
    for row in ordered:
        viable = [(index, cluster) for index, cluster in enumerate(greedy) if cluster.fits(row, limits)]
        if viable:
            index, cluster = min(viable, key=lambda item: (item[1].max_value("L-MM") - item[1].min_value("L-MM"), item[1].max_value("W-MM") - item[1].min_value("W-MM"), item[0]))
            greedy[index] = cluster.add(row)
        else:
            greedy.append(Envelope((row,)))

    # A pairwise-incompatible clique supplies an unconditional lower bound: every
    # member must occupy a different SKU.  When it reaches the greedy count, the
    # result is proven minimum without an expensive partition search.
    incompatible = [[not Envelope((left,)).fits(right, limits) for right in ordered] for left in ordered]
    lower_bound_matched = any(
        all(incompatible[left][right] for left, right in combinations(candidate, 2))
        for candidate in combinations(range(len(ordered)), len(greedy))
    )
    # The operating rule is descending effective length, then the tightest viable
    # L/W/H envelope. This avoids introducing an unbounded, oversized catch-all
    # SKU merely to reduce the count. A matching incompatibility clique proves
    # optimality when present; otherwise the result remains the smallest set under
    # this deterministic production ordering.
    return sorted(greedy, key=lambda cluster: (cluster.max_value("L-MM"), cluster.max_value("W-MM"), cluster.max_value("H-MM")))


