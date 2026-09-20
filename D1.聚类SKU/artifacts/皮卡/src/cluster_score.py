"""Cluster scoring for prioritization and ranking."""

import numpy as np


def _normalize(values: list[float]) -> list[float]:
    """Min-max normalize to [0, 1]."""
    arr = np.array(values, dtype=float)
    lo, hi = arr.min(), arr.max()
    if hi == lo:
        return [0.5] * len(arr)
    return ((arr - lo) / (hi - lo)).tolist()


def _log_normalize(values: list[float]) -> list[float]:
    """Log-transform then min-max normalize to [0, 1]. Handles zeros gracefully."""
    arr = np.array(values, dtype=float)
    shifted = arr + 1.0
    logged = np.log(shifted)
    lo, hi = logged.min(), logged.max()
    if hi == lo:
        return [0.5] * len(arr)
    return ((logged - lo) / (hi - lo)).tolist()


def score_clusters(clusters: list[dict], config_dir: str = "") -> list[dict]:
    """Compute CLUSTER_SCORE for each cluster.

    Score components (0-1 each):
      - sales_score:       log-normalized estimated sales (0.35)
      - fitment_score:     normalized fitment count (0.20)
      - year_score:        normalized year span (0.15)
      - compactness_score: inverse of L/W/H spreads (0.30)

    Safety multiplier: 0.4 if safety fails, 1.0 if passes.
    """
    if not clusters:
        return clusters

    sales = [c["estimated_sales"] for c in clusters]
    fitments = [c["fitment_count"] for c in clusters]
    year_spans = [c["year_max"] - c["year_min"] for c in clusters]

    # Dimension compactness: combine L, W, H spreads (lower = better)
    l_spreads = np.array([c["l_spread"] for c in clusters], dtype=float)
    w_spreads = np.array([c["w_spread"] for c in clusters], dtype=float)
    h_spreads = np.array([c["h_spread"] for c in clusters], dtype=float)

    # Invert: compactness = 1 / (1 + spread) — large spread → low score
    l_compact = 1.0 / (1.0 + l_spreads)
    w_compact = 1.0 / (1.0 + w_spreads)
    h_compact = 1.0 / (1.0 + h_spreads)

    sales_norm = _log_normalize(sales)
    fitment_norm = _normalize(fitments)
    year_norm = _normalize(year_spans)
    l_compact_norm = _normalize(l_compact.tolist())
    w_compact_norm = _normalize(w_compact.tolist())
    h_compact_norm = _normalize(h_compact.tolist())

    for i, c in enumerate(clusters):
        compactness = (l_compact_norm[i] + w_compact_norm[i] + h_compact_norm[i]) / 3.0

        raw = (
            sales_norm[i] * 0.35
            + fitment_norm[i] * 0.20
            + year_norm[i] * 0.15
            + compactness * 0.30
        )

        safety_mult = 0.4 if not c.get("safety_pass", True) else 1.0
        c["CLUSTER_SCORE"] = round(raw * safety_mult, 4)

    clusters.sort(key=lambda c: c["CLUSTER_SCORE"], reverse=True)
    return clusters


def assign_confidence(cluster: dict) -> str:
    """Assign confidence based on score, safety, and dimensional compactness.

    HIGH:   safety_pass AND score >= 0.6 AND compact (l<200, w<100, h<100 mm)
    MEDIUM: safety_pass AND score >= 0.3
    LOW:    otherwise
    """
    score = cluster.get("CLUSTER_SCORE", 0)
    safety = cluster.get("safety_pass", True)
    l_spread = cluster.get("l_spread", 999)
    w_spread = cluster.get("w_spread", 999)
    h_spread = cluster.get("h_spread", 999)

    if not safety:
        return "LOW"
    if score >= 0.6 and l_spread < 200 and w_spread < 100 and h_spread < 100:
        return "HIGH"
    if score >= 0.3:
        return "MEDIUM"
    return "LOW"