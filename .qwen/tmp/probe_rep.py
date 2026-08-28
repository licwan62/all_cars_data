# -*- coding: utf-8 -*-
"""Quick data probe for representative-car analysis."""
import pandas as pd

SRC = r"d:\Licheng\Workflow\all_cars_data\source"

dims = pd.read_csv(f"{SRC}\\车型尺寸库.csv", encoding="utf-8-sig", dtype={"DIMENSION-ID": str})
shapes = pd.read_csv(f"{SRC}\\车型形状分类.csv", encoding="utf-8-sig", dtype={"DIMENSION-ID": str})
sales = pd.read_csv(f"{SRC}\\atom_sales.csv", encoding="utf-8-sig", dtype={"atom_record_id": str})

print("dims rows:", len(dims), "unique ID:", dims["DIMENSION-ID"].nunique())
print("shapes rows:", len(shapes), "unique ID:", shapes["DIMENSION-ID"].nunique())
print("sales rows:", len(sales), "unique atom:", sales["atom_record_id"].nunique())

print("\n== 迭代状态 top 40 ==")
print(dims["迭代状态"].value_counts(dropna=False).head(40))

print("\n== 车形分布 (shapes csv) ==")
print(shapes["车形"].value_counts().sort_index())

print("\n== 车形分布 (dims joined) ==")
m = dims.merge(shapes, on="DIMENSION-ID", how="left")
print(m["车形"].value_counts(dropna=False).sort_index())

print("\n== dims 缺 L/W/H ==")
for c in ["L-IN", "W-IN", "H-IN"]:
    print(c, "null:", dims[c].isna().sum(), "| non-numeric:", pd.to_numeric(dims[c], errors="coerce").isna().sum())

# sales join: strip |ATOM_YEAR=
sales["DIMENSION-ID"] = sales["atom_record_id"].str.split("|ATOM_YEAR=", regex=False).str[0]
sales_agg = sales.groupby("DIMENSION-ID")["预估销量"].sum().rename("销量")
print("\n== sales agg rows:", len(sales_agg), "==")

m2 = m.merge(sales_agg, on="DIMENSION-ID", how="left")
print("\n== per shape: n, n_with_sales, total_sales ==")
g = m2.groupby("车形").agg(n=("DIMENSION-ID", "count"),
                            n_sales=("销量", lambda s: s.notna().sum()),
                            total_sales=("销量", "sum"))
g["n_no_sales"] = g["n"] - g["n_sales"]
print(g.to_string())

print("\n== 可入库 subset: per shape n / with sales ==")
ok = m2[m2["迭代状态"] == "可入库"]
g2 = ok.groupby("车形").agg(n=("DIMENSION-ID", "count"),
                            n_sales=("销量", lambda s: s.notna().sum()),
                            total_sales=("销量", "sum"))
print(g2.to_string())

print("\n== shapes not in dims ==")
print(len(set(shapes["DIMENSION-ID"]) - set(dims["DIMENSION-ID"])))
print("\n== dims not in shapes ==")
print(len(set(dims["DIMENSION-ID"]) - set(shapes["DIMENSION-ID"])))