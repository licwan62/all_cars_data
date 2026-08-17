"""Load and filter pickup data from CSV."""

import pandas as pd
from pathlib import Path


def detect_encoding(filepath: str) -> str:
    """Detect file encoding by trying common Chinese encodings first."""
    encodings = ["gbk", "gb2312", "gb18030", "utf-8", "utf-8-sig", "latin-1"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                f.read(1024)
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return "utf-8"


def load_data(filepath: str) -> pd.DataFrame:
    """Load the sales CSV and return the full DataFrame."""
    encoding = detect_encoding(filepath)
    df = pd.read_csv(filepath, encoding=encoding)
    df.columns = df.columns.str.strip()
    return df


def filter_pickups(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to only pickup rows."""
    return df[df["分类"].str.strip() == "皮卡"].copy()