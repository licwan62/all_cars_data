"""Core clustering engine for pickup fitment groups."""

import pandas as pd
import yaml
from pathlib import Path
from itertools import groupby


def load_config(config_dir: str) -> dict:
    """Load cluster_config.yaml."""
    config_path = Path(config_dir) / "cluster_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def filter_valid_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separate valid and exception rows.

    Exceptions: missing auto-size, missing L/W/H, length margin < 0,
    CAB/BED missing, YEAR unparseable.
    """
    exceptions = pd.DataFrame(columns=df.columns.tolist() + ["EXCEPTION_REASON"])
    valid = df.copy()

    reasons = []

    for idx, row in df.iterrows():
        row_reasons = []

        auto_size = str(row.get("自动尺码", "")).strip()
        if auto_size in ("", "nan", "数据不全", "无可用尺码"):
            row_reasons.append("自动尺码无效")

        if pd.isna(row.get("L-MM")) or pd.isna(row.get("W-MM")) or pd.isna(row.get("H-MM")):
            row_reasons.append("尺寸缺失")

        if pd.isna(row.get("YEAR_START")) or pd.isna(row.get("YEAR_END")):
            row_reasons.append("YEAR解析失败")

        if pd.isna(row.get("自动长度余量")):
            row_reasons.append("自动长度余量缺失")
        elif row["自动长度余量"] < 0:
            row_reasons.append("自动长度余量<0")

        if str(row.get("CAB", "")).strip() == "" or str(row.get("CAB", "")).strip() == "nan":
            row_reasons.append("CAB缺失")

        if str(row.get("BED", "")).strip() == "" or str(row.get("BED", "")).strip() == "nan":
            row_reasons.append("BED缺失")

        if row_reasons:
            reasons.append("; ".join(row_reasons))
        else:
            reasons.append("")

    df["EXCEPTION_REASON"] = reasons
    exceptions = df[df["EXCEPTION_REASON"] != ""].copy()
    valid = df[df["EXCEPTION_REASON"] == ""].copy()

    return valid, exceptions


def build_initial_clusters(df: pd.DataFrame, config: dict) -> list[dict]:
    """Build initial clusters driven by cluster_config.yaml.

    Group columns derived from config:
      - 自动尺码, TRUCK_TYPE (always)
      - AXLE_TYPE, CAB_GROUP, BED_GROUP, MAKE_NORMALIZED, MODEL_FAMILY
        added only when the corresponding allow_cross_* is false.
    """
    cfg = config["pickup"]

    group_cols = ["自动尺码", "TRUCK_TYPE"]
    if not cfg.get("allow_drw_srw_merge", False):
        group_cols.append("AXLE_TYPE")
    if not cfg.get("allow_cross_cab", False):
        group_cols.append("CAB_GROUP")
    if not cfg.get("allow_cross_bed_group", False):
        group_cols.append("BED_GROUP")
    if not cfg.get("allow_cross_make", False):
        group_cols.append("MAKE_NORMALIZED")
    if not cfg.get("allow_cross_model", False):
        group_cols.append("MODEL_FAMILY")

    clusters = []
    cluster_id = 0

    for keys, group in df.groupby(group_cols, dropna=False):
        cluster_id += 1
        key_dict = dict(zip(group_cols, keys))

        cluster = {
            "cluster_id": cluster_id,
            "自动尺码": key_dict.get("自动尺码", ""),
            "AXLE_TYPE": key_dict.get("AXLE_TYPE", group["AXLE_TYPE"].iloc[0]),
            "TRUCK_TYPE": key_dict.get("TRUCK_TYPE", ""),
            "CAB_GROUP": key_dict.get("CAB_GROUP", group["CAB_GROUP"].iloc[0]),
            "BED_GROUP": key_dict.get("BED_GROUP", group["BED_GROUP"].iloc[0]),
            "rows": group,
            "makes": sorted(group["MAKE_NORMALIZED"].unique()),
            "models": sorted(group["MODEL_FAMILY"].unique()),
            "fitment_count": len(group),
            "estimated_sales": group["预估销量 的总和"].sum(),
            "l_min": group["L-MM"].min(),
            "l_max": group["L-MM"].max(),
            "w_min": group["W-MM"].min(),
            "w_max": group["W-MM"].max(),
            "h_min": group["H-MM"].min(),
            "h_max": group["H-MM"].max(),
            "l_spread": group["L-MM"].max() - group["L-MM"].min(),
            "w_spread": group["W-MM"].max() - group["W-MM"].min(),
            "h_spread": group["H-MM"].max() - group["H-MM"].min(),
            "length_margin_min": group["自动长度余量"].min(),
            "length_margin_median": group["自动长度余量"].median(),
            "year_min": int(group["YEAR_START"].min()),
            "year_max": int(group["YEAR_END"].max()),
        }
        clusters.append(cluster)

    return clusters


def check_cluster_safety(cluster: dict, config: dict) -> bool:
    """Check if a cluster passes dimension safety thresholds."""
    cfg = config["pickup"]

    if cluster["l_spread"] > cfg["max_length_spread_mm"]:
        return False
    if cluster["w_spread"] > cfg["max_width_spread_mm"]:
        return False
    if cluster["h_spread"] > cfg["max_height_spread_mm"]:
        return False
    if cluster["length_margin_min"] < cfg["min_length_margin_mm"]:
        return False

    return True


def merge_model_years(df: pd.DataFrame) -> pd.DataFrame:
    """Merge years for the same MAKE+MODEL_FAMILY+CAB_GROUP+BED_GROUP+自动尺码.

    Returns a DataFrame with merged year ranges per model.
    """
    from year_parser import merge_year_ranges, format_year_ranges, year_range_to_compact

    group_cols = ["MAKE_NORMALIZED", "MODEL_FAMILY", "CAB_GROUP", "BED_GROUP", "自动尺码"]

    records = []
    for keys, group in df.groupby(group_cols, dropna=False):
        make, model, cab, bed, size = keys

        # collect all year ranges
        year_ranges = []
        for _, row in group.iterrows():
            if pd.notna(row["YEAR_START"]) and pd.notna(row["YEAR_END"]):
                year_ranges.append((int(row["YEAR_START"]), int(row["YEAR_END"])))

        merged = merge_year_ranges(year_ranges)

        # Use the first row as template
        template = group.iloc[0].to_dict()
        template["YEAR_START"] = min(s for s, e in merged) if merged else group["YEAR_START"].min()
        template["YEAR_END"] = max(e for s, e in merged) if merged else group["YEAR_END"].max()
        template["YEAR_RANGES"] = merged
        template["YEAR_COMPACT"] = format_year_ranges(merged)
        template["预估销量 的总和"] = group["预估销量 的总和"].sum()
        template["_row_count"] = len(group)
        records.append(template)

    return pd.DataFrame(records)


def generate_cluster_id(cluster: dict, config: dict) -> str:
    """Generate CLUSTER_ID from config-driven grouping.

    Parts: 自动尺码-TRUCK_TYPE[-AXLE_TYPE][-CAB_GROUP][-BED_GROUP][-MAKE-MODEL]
    AXLE_TYPE / CAB_GROUP / BED_GROUP / MAKE-MODEL only included when they
    were part of the grouping (allow_cross_* is false).
    """
    cfg = config["pickup"]
    parts = [cluster["自动尺码"], cluster["TRUCK_TYPE"]]
    if not cfg.get("allow_drw_srw_merge", False):
        parts.append(cluster["AXLE_TYPE"])
    if not cfg.get("allow_cross_cab", False):
        parts.append(cluster["CAB_GROUP"])
    if not cfg.get("allow_cross_bed_group", False):
        parts.append(cluster["BED_GROUP"])
    if not cfg.get("allow_cross_make", False):
        make = cluster.get("makes", [""])[0] if cluster.get("makes") else ""
        model = cluster.get("models", [""])[0] if cluster.get("models") else ""
        model_slug = f"{make}-{model}".replace(" ", "-").replace("/", "-")
        parts.append(model_slug)
    return "-".join(parts)


def run_clustering(df: pd.DataFrame, config_dir: str) -> tuple[list[dict], pd.DataFrame, pd.DataFrame]:
    """Run the full clustering pipeline.

    Returns (clusters, valid_df, exceptions_df).
    """
    config = load_config(config_dir)

    valid, exceptions = filter_valid_rows(df)

    clusters = build_initial_clusters(valid, config)

    for c in clusters:
        c["safety_pass"] = check_cluster_safety(c, config)
        c["CLUSTER_ID"] = generate_cluster_id(c, config)

    return clusters, valid, exceptions