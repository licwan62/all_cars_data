# -*- coding: utf-8 -*-
"""方案A定稿评价: 匹配层(方案A CSV) + 聚类层(output_评价) → 更新报告."""
import sys
import io
import pandas as pd
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = Path(__file__).parent
OUT = BASE / "评价报告"

match = pd.read_csv(BASE / "方案分析" / "数据源" / "匹配_方案A_完整.csv", encoding="utf-8-sig")
match.columns = [c.strip() for c in match.columns]
pk = match[match["分类"].astype(str).str.strip() == "皮卡"].copy()
pk["粗"] = pk["W-MM"] + 2 * pk["H-MM"]
alloc = pk[pk["自动尺码"].notna() & ~pk["自动尺码"].isin(["无可用尺码", "数据不全"])].copy()


def band(m):
    if pd.isna(m):
        return "无"
    if m > 500:
        return "不可用(>500)"
    if m >= 150:
        return "警戒(150-500)"
    if m >= 0:
        return "合适(0-150)"
    return "过紧(<0)"


alloc["分段"] = alloc["自动长度余量"].apply(band)
alloc["粗裕量"] = alloc.apply(
    lambda r: ({"PK-M": 6400, "PK-M+": 6400, "PK-L": 6400, "PK-XL": 6400, "PK-XL+": 6280,
                "PK-XXL": 6400, "PK-XXXL": 6400, "PK-WX": 6900, "PK-WXXL": 6900}
               .get(r["自动尺码"], 6280) - r["粗"]), axis=1)

seg = alloc.groupby("分段").agg(行数=("MAKE", "count"), 销量=("预估销量 的总和", "sum"))
print("== 匹配层分段:")
print(seg.round(0).to_string())
print("  粗裕量<0:", (alloc["粗裕量"] < 0).sum(), "| 合计销量:", f"{alloc['预估销量 的总和'].sum():,.0f}")
excp = pk[pk["自动尺码"].astype(str) == "无可用尺码"]
print("  异常: 无可用", len(excp), "(原因分布:", excp["原因"].value_counts(dropna=False).to_dict(), ")",
      "| 数据不全", (pk["自动尺码"].astype(str) == "数据不全").sum())
print()

summ = pd.read_csv(BASE / "output_评价" / "pickup_cluster_summary.csv", encoding="utf-8-sig")
summ.columns = [c.strip() for c in summ.columns]
print("== 聚类: 集群", len(summ), "| 实体尺码", summ["PHYSICAL_SKU"].nunique(),
      "| 销量", f"{summ['ESTIMATED_SALES'].sum():,.0f}",
      "| SAFETY_FAIL", (summ["SAFETY_PASS"] == False).sum())
print("  实体尺码:", summ["PHYSICAL_SKU"].value_counts().to_dict())
new = summ[summ["PHYSICAL_SKU"].isin(["PK-WX", "PK-WXXL"])]
print("  新尺码集群数:", len(new))
print(new[["CLUSTER_ID", "ESTIMATED_SALES", "L_MIN", "L_MAX", "LENGTH_MARGIN_MIN", "SAFETY_PASS"]].to_string(index=False))

# 明细导出
alloc_out = alloc[["MAKE", "MODEL", "版本", "CAB", "BED", "YEAR", "L-MM", "W-MM", "H-MM",
                   "自动尺码", "自动长度余量", "粗", "粗裕量", "分段", "预估销量 的总和"]]
alloc_out.to_csv(OUT / "匹配评价明细.csv", index=False, encoding="utf-8-sig")
summ[["CLUSTER_ID", "PHYSICAL_SKU", "CONSUMER_NAME", "ESTIMATED_SALES", "L_MIN", "L_MAX",
      "W_MIN", "W_MAX", "LENGTH_MARGIN_MIN", "LENGTH_MARGIN_MEDIAN", "SAFETY_PASS"]].to_csv(
    OUT / "集群评价明细.csv", index=False, encoding="utf-8-sig")
print("明细已导出")