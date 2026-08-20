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


def load_fitment_with_atom_sales(workbook_path: str, atom_sales_path: str,
                                 sheet_name: str = "尺码匹配") -> pd.DataFrame:
    """Join fitment dimensions to annual atom sales by DIMENSION-ID."""
    fitment = pd.read_excel(workbook_path, sheet_name=sheet_name)
    fitment.columns = fitment.columns.str.strip()
    sales = load_data(atom_sales_path)
    if "DIMENSION-ID" not in fitment.columns:
        raise ValueError("尺码匹配缺少字段: DIMENSION-ID")
    missing = {"atom_record_id", "预估销量"} - set(sales.columns)
    if missing:
        raise ValueError(f"atom_sales.csv 缺少字段: {sorted(missing)}")
    sales = sales.copy()
    sales["DIMENSION-ID"] = sales["atom_record_id"].astype(str).str.replace(
        r"\|ATOM_YEAR=\d{4}$", "", regex=True)
    sales["预估销量"] = pd.to_numeric(sales["预估销量"], errors="coerce").fillna(0)
    totals = sales.groupby("DIMENSION-ID", as_index=False)["预估销量"].sum()
    totals = totals.rename(columns={"预估销量": "预估销量 的总和"})
    result = fitment.merge(totals, on="DIMENSION-ID", how="left", validate="many_to_one")
    result["预估销量 的总和"] = result["预估销量 的总和"].fillna(0)
    return result


def filter_pickups(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to only pickup rows."""
    return df[df["分类"].astype(str).str.strip() == "皮卡"].copy()
