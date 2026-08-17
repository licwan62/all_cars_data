"""Normalize and standardize raw data fields."""

import json
import pandas as pd
from pathlib import Path


def normalize_strings(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Strip whitespace, normalize case for string columns."""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df


def normalize_numeric(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Convert a column to numeric, coercing errors to NaN."""
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def normalize_make(df: pd.DataFrame, config_dir: str) -> pd.DataFrame:
    """Standardize MAKE names using the alias config."""
    alias_path = Path(config_dir) / "make_alias.json"
    with open(alias_path, "r", encoding="utf-8") as f:
        aliases = json.load(f)

    df["MAKE_NORMALIZED"] = df["MAKE"].map(aliases).fillna(df["MAKE"])
    return df


def normalize_model_family(df: pd.DataFrame, config_dir: str) -> pd.DataFrame:
    """Add MODEL_FAMILY from truck_family.csv config."""
    family_path = Path(config_dir) / "truck_family.csv"
    family_df = pd.read_csv(family_path)

    # build lookup: (make_normalized, model) -> model_family
    family_df["make"] = family_df["make"].str.strip()
    family_df["model_family"] = family_df["model_family"].str.strip()

    lookup = {}
    for _, row in family_df.iterrows():
        key = (row["make"].lower(), row["model_family"].lower())
        lookup[key] = row["model_family"]

    def find_family(row):
        make = str(row.get("MAKE_NORMALIZED", "")).strip().lower()
        model = str(row.get("MODEL", "")).strip().lower()
        key = (make, model)
        if key in lookup:
            return lookup[key]
        return model.title()

    df["MODEL_FAMILY"] = df.apply(find_family, axis=1)
    return df


def normalize_cab(df: pd.DataFrame, config_dir: str) -> pd.DataFrame:
    """Map raw CAB to CAB_GROUP using cab_mapping.csv."""
    cab_path = Path(config_dir) / "cab_mapping.csv"
    cab_df = pd.read_csv(cab_path)
    cab_df["cab_raw"] = cab_df["cab_raw"].str.strip().str.lower()
    cab_df["cab_group"] = cab_df["cab_group"].str.strip()

    cab_map = dict(zip(cab_df["cab_raw"], cab_df["cab_group"]))

    def map_cab(raw):
        raw_lower = str(raw).strip().lower()
        return cab_map.get(raw_lower, "UNKNOWN")

    df["CAB_GROUP"] = df["CAB"].apply(map_cab)
    return df


def normalize_bed(df: pd.DataFrame) -> pd.DataFrame:
    """Parse BED length as float and assign BED_GROUP."""
    df["BED_LENGTH"] = pd.to_numeric(df["BED"], errors="coerce")

    def bed_group(length):
        if pd.isna(length):
            return "UNKNOWN"
        if length < 6.0:
            return "SHORT"
        elif length < 7.0:
            return "STANDARD"
        else:
            return "LONG"

    df["BED_GROUP"] = df["BED_LENGTH"].apply(bed_group)
    return df


def run_normalize(df: pd.DataFrame, config_dir: str) -> pd.DataFrame:
    """Run all normalization steps."""
    str_cols = ["MAKE", "MODEL", "SUB-MODEL", "版本", "结构", "CAB", "BED",
                "YEAR", "分类", "自动尺码", "DIMENSION-ID"]
    df = normalize_strings(df, str_cols)

    num_cols = ["L-MM", "W-MM", "H-MM", "自动长度余量", "相差数值", "预估销量 的总和"]
    for col in num_cols:
        df = normalize_numeric(df, col)

    df = normalize_make(df, config_dir)
    df = normalize_model_family(df, config_dir)
    df = normalize_cab(df, config_dir)
    df = normalize_bed(df)

    return df