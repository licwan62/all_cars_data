"""Classify pickup trucks by type, axle, and identify DRW."""

import pandas as pd
from pathlib import Path


def classify_truck_type(df: pd.DataFrame, config_dir: str) -> pd.DataFrame:
    """Assign TRUCK_TYPE and AXLE_TYPE from truck_family.csv config."""
    family_path = Path(config_dir) / "truck_family.csv"
    family_df = pd.read_csv(family_path)

    family_df["make"] = family_df["make"].str.strip().str.lower()
    family_df["model_family"] = family_df["model_family"].str.strip().str.lower()
    family_df["truck_type"] = family_df["truck_type"].str.strip()
    family_df["axle_type"] = family_df["axle_type"].str.strip()

    lookup = {}
    for _, row in family_df.iterrows():
        key = (row["make"], row["model_family"])
        lookup[key] = (row["truck_type"], row["axle_type"])

    def classify(row):
        make = str(row.get("MAKE_NORMALIZED", "")).strip().lower()
        model = str(row.get("MODEL_FAMILY", "")).strip().lower()
        key = (make, model)
        if key in lookup:
            return lookup[key]
        return ("UNKNOWN", "SRW")

    result = df.apply(classify, axis=1, result_type="expand")
    df["TRUCK_TYPE"] = result[0]
    df["AXLE_TYPE"] = result[1]

    # Also detect DRW from version/sub-model fields
    drw_mask = df.apply(_detect_drw, axis=1)
    df.loc[drw_mask, "AXLE_TYPE"] = "DRW"
    df.loc[drw_mask, "TRUCK_TYPE"] = "DRW"

    return df


def _detect_drw(row) -> bool:
    """Detect DRW from version/sub-model/model fields."""
    fields = []
    for col in ["版本", "SUB-MODEL", "MODEL"]:
        if col in row.index:
            val = str(row[col]).upper()
            fields.append(val)
    combined = " ".join(fields)
    return any(kw in combined for kw in ["DRW", "DUAL REAR", "DUALLY", "DUAL-REAR"])


def classify_model_family_unknown(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows where MODEL_FAMILY couldn't be classified."""
    df["MODEL_FAMILY_UNKNOWN"] = df["TRUCK_TYPE"] == "UNKNOWN"
    return df