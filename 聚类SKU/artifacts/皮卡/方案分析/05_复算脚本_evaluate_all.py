# -*- coding: utf-8 -*-
"""Full evaluation: matching bands (with sales) + cluster layer. Output report data."""
import sys
import io
import pandas as pd
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent  # 指向 pickup-cluster 项目根
OUT = BASE / "评价报告"
OUT.mkdir(exist_ok=True)

# sales lookup by DIMENSION-ID (independent of matching columns)
sales_src = pd.read_csv(BASE / "input" / "销量统计.csv", encoding="utf-8-sig")
sales_src.columns = [c.strip() for c in sales_src.columns]
sales_map = sales_src.set_index("DIMENSION-ID")["预估销量 的总和"].to_dict()

xl = pd.ExcelFile(str(BASE / "input" / "车型数据尺码.xlsx"))
sizes = xl.parse("尺码")
match = xl.parse("尺码匹配")
match.columns = [c.strip() for c in match.columns]
pk = match[match["分类"].astype(str).str.strip() == "皮卡"].copy()

size_tbl = sizes[sizes["分类"] == "皮卡"][["逻辑尺码", "长上限", "粗上限", "档位序号"]].set_index("逻辑尺码")

def band(m):
    if m > 500:
        return "不可用(>500)"
    if m >= 150:
        return "警戒(150-500)"
    if m >= 0:
        return "合适(0-150)"
    return "过紧(<0)"

pk = pk.copy()
pk["粗"] = pk["W-MM"] + 2 * pk["H-MM"]
pk["销量"] = pk["DIMENSION-ID"].map(sales_map).fillna(0)
alloc = pk[pk["自动尺码"].notna() & ~pk["自动尺码"].isin(["无可用尺码", "数据不全"])].copy()
alloc["余量"] = alloc["自动长度余量"]
alloc["分段"] = alloc["余量"].apply(band)
alloc["粗裕量"] = alloc.apply(
    lambda r: (size_tbl.loc[r["自动尺码"], "粗上限"] - r["粗"]) if r["自动尺码"] in size_tbl.index else None, axis=1)

def rep(title, df):
    print()
    print("=" * 20, title, "=" * 20)
    g = df.groupby("分段").agg(行数=("MAKE", "count"), 销量=("销量", "sum"), 余量min=("余量", "min"), 余量max=("余量", "max"))
    print(g.round(0).to_string())

print("已适配总销量:", f"{alloc['销量'].sum():,.0f}")
rep("长度分段(已适配 598 行)", alloc)
print()
print("分段 x 尺码(行数 / 销量):")
ct = pd.crosstab(alloc["自动尺码"], alloc["分段"])
ct_s = pd.crosstab(alloc["自动尺码"], alloc["分段"], values=alloc["销量"], aggfunc="sum").round(0)
for sz in ct.index:
    print(f"  {sz:<8} 行数 {dict(ct.loc[sz])} 销量 {ct_s.loc[sz].to_dict()}")
print()
print("== 粗裕量<0 行:", len(alloc[alloc["粗裕量"] < 0]))
print("== 粗裕量 0~30 行:", len(alloc[alloc["粗裕量"].between(0, 30, inclusive="both")]))
print()

for b in ["不可用(>300)", "警戒(150-300)"]:
    sub = alloc[alloc["分段"] == b]
    print(f"== [{b}] {len(sub)} 行 销量 {sub['销量'].sum():,.0f}, 按车系:")
    g = sub.groupby(["MAKE", "MODEL", "自动尺码", "CAB"]).agg(行数=("MAKE", "count"), 销量=("销量", "sum"),
                                                             余量min=("余量", "min"), 余量max=("余量", "max"))
    print(g.sort_values("销量", ascending=False).to_string())
    print()

exc = pk[pk["原因"].notna()].copy()
print("== 异常行:", len(exc))
print(exc.groupby("原因").agg(行数=("MAKE", "count"), 销量=("销量", "sum")).to_string())
print()

# cluster layer
summ = pd.read_csv(BASE / "output_评价" / "pickup_cluster_summary.csv", encoding="utf-8-sig")
summ.columns = [c.strip() for c in summ.columns]
summ["MIN分段"] = summ["LENGTH_MARGIN_MIN"].apply(band)
print("== 聚类: 集群", len(summ), "| 实体尺码", summ["PHYSICAL_SKU"].nunique(), "| 总销量",
      f"{summ['ESTIMATED_SALES'].sum():,.0f}")
print("== 集群MIN分段(集群数 / 销量):")
print(summ.groupby("MIN分段").agg(集群数=("CLUSTER_ID", "count"), 销量=("ESTIMATED_SALES", "sum")).round(0).to_string())
print()
print("== SAFETY_PASS=False:", len(summ[summ["SAFETY_PASS"] == False]),
      "| 其中新尺码集群:", len(summ[(summ["SAFETY_PASS"] == False) & summ["PHYSICAL_SKU"].isin(["PK-WX", "PK-WXXL"])]))
print()
newc = summ[summ["PHYSICAL_SKU"].isin(["PK-WX", "PK-WXXL"])]
print("== 新尺码集群明细:")
print(newc[["CLUSTER_ID", "PHYSICAL_SKU", "CONSUMER_NAME", "ESTIMATED_SALES",
            "L_MIN", "L_MAX", "LENGTH_MARGIN_MIN", "LENGTH_MARGIN_MEDIAN", "SAFETY_PASS"]].to_string(index=False))

# save detail CSVs for the report folder
alloc_out = alloc[["MAKE", "MODEL", "版本", "CAB", "BED", "YEAR", "L-MM", "W-MM", "H-MM",
                   "自动尺码", "自动长度余量", "粗", "粗裕量", "分段", "销量"]]
alloc_out.to_csv(OUT / "匹配评价明细.csv", index=False, encoding="utf-8-sig")
summ[["CLUSTER_ID", "PHYSICAL_SKU", "CONSUMER_NAME", "ESTIMATED_SALES", "L_MIN", "L_MAX",
      "W_MIN", "W_MAX", "LENGTH_MARGIN_MIN", "LENGTH_MARGIN_MEDIAN", "MIN分段", "SAFETY_PASS"]].to_csv(
    OUT / "集群评价明细.csv", index=False, encoding="utf-8-sig")
print("\n明细已导出到", OUT)