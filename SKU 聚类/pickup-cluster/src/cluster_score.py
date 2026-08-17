"""Cluster scoring for prioritization and ranking."""

import numpy as np
import yaml
from pathlib import Path


def load_scoring_config(config_dir: str) -> dict:
    """Load scoring weights from cluster_config.yaml."""
    config_path = Path(config_dir) / "cluster_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("scoring", {})


def _normalize(values: list[float]) -> list[float]:
    """Min-max normalize a list of values to [0, 1]."""
    arr = np.array(values, dtype=float)
    min_v = arr.min()
    max_v = arr.max()
    if max_v == min_v:
        return [0.5] * len(arr)
    return ((arr - min_v) / (max_v - min_v)).tolist()


def score_clusters(clusters: list[dict], config_dir: str) -> list[dict]:
    """Compute CLUSTER_SCORE for each cluster."""
    weights = load_scoring_config(config_dir)

    if not clusters:
        return clusters

    sales = [c["estimated_sales"] for c in clusters]
    fitments = [c["fitment_count"] for c in clusters]
    models = [len(c["models"]) for c in clusters]
    # dimension compactness: lower spread = higher score
    l_spreads = [c["l_spread"] for c in clusters]
    year_spans = [c["year_max"] - c["year_min"] for c in clusters]

    sales_norm = _normalize(sales)
    fitment_norm = _normalize(fitments)
    model_norm = _normalize(models)
    # invert: lower spread = better
    l_spread_norm = _normalize([-s for s in l_spreads])
    year_span_norm = _normalize(year_spans)

    for i, c in enumerate(clusters):
        score = (
            sales_norm[i] * weights.get("sales_weight", 0.45)
            + fitment_norm[i] * weights.get("fitment_weight", 0.20)
            + model_norm[i] * weights.get("model_weight", 0.15)
            + year_span_norm[i] * weights.get("year_continuity_weight", 0.10)
            + l_spread_norm[i] * weights.get("dimension_compactness_weight", 0.10)
        )
        c["CLUSTER_SCORE"] = round(score, 4)

    # Sort by score descending
    clusters.sort(key=lambda c: c["CLUSTER_SCORE"], reverse=True)
    return clusters


def assign_confidence(cluster: dict) -> str:
    """Assign a confidence label based on score and safety."""
    score = cluster.get("CLUSTER_SCORE", 0)
    safety = cluster.get("safety_pass", True)

    if not safety:
        return "LOW"
    if score >= 0.7:
        return "HIGH"
    elif score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"