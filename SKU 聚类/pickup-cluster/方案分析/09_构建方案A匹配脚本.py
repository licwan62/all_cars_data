# -*- coding: utf-8 -*-
"""构建 方案A 完整匹配表(皮卡634行, 与PQ语义一致) + 销量, 生成 main.py --input 合并CSV."""
import sys
import io
import pandas as pd
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = Path(__file__).parent
XLSX = BASE / "input" / "车型数据尺码.xlsx"
xl = pd.ExcelFile(str(XLSX))
sizes = xl.parse("尺码")
match = xl.parse("尺码匹配")
match.columns = [c.strip() for c in match.columns]

# 尺码池
pool = sizes[sizes["分类"] == "皮卡"].copy()
pool = pool[pool["档位序号"].notna() & pool["长上限"].notna() & pool["粗上限"].notna()]
pool = pool.sort_values(["档位序号", "长上限"]).reset_index(drop=True)

MARGIN_TOL = 500


def calc_single(p, L, T):
    hit = p[(p["长上限"] >= L) & (p["粗上限"] >= T)]
    if len(hit):
        s = hit.iloc[0]
        margin = s["长上限"] - L
        if margin > MARGIN_TOL:
            return ("无可用尺码", None, "超余量", s["内部尺码"], False)
        return (s["内部尺码"], margin, None, None, True)
    return (None, None, None, None, False)


def calc(分类, CAB, 版本, L, T):
    # 方案A: 同CAB同版本 -> 同版本通用CAB -> 通用版本; 超余量/无候选继续回退
    tried = []
    steps = [(分类, CAB, 版本), (分类, None, 版本), (分类, None, None)]
    for cat, cab, ver in steps:
        sub = pool
        if cab is not None:
            sub = sub[sub["CAB"].astype(object) == cab]
        else:
            sub = sub[sub["CAB"].isna()]
        if ver is not None:
            sub = sub[sub["版本"].astype(object) == ver]
        else:
            sub = sub[sub["版本"].isna()]
        r = calc_single(sub, L, T)
        if r[4]:
            return r
        tried.append(r)
    last = tried[-1]
    return (last[0], last[1], last[2], last[3], False)


# 皮卡行: 版本归一化(含DRW -> DRW) + 重放
pk = match[match["分类"].astype(str).str.strip() == "皮卡"].copy()
pk["粗"] = pk["W-MM"] + 2 * pk["H-MM"]
pk["不完整"] = pk["L-MM"].isna() | pk["W-MM"].isna() | pk["H-MM"].isna()


def norm_ver(v):
    s = str(v or "").strip()
    if s.upper().find("DRW") >= 0:
        return "DRW"
    return s or None


out = []
for _, r in pk.iterrows():
    if r["不完整"]:
        out.append((None, None, None, None, True))
        continue
    res = calc("皮卡", str(r["CAB"] or "") or None, norm_ver(r["版本"]), r["L-MM"], r["粗"])
    out.append(res)

pk["新尺码"] = [o[0] for o in out]
pk["新余量"] = [round(o[1], 1) if o[1] is not None else None for o in out]
pk["新原因"] = [o[2] for o in out]
pk["新候选"] = [o[3] for o in out]
pk["无尺寸"] = [o[4] for o in out]

# 需要重写的行: 皮卡且有尺寸(数据不全行保持原样) 且 结果尺码非空
mask_rewrite = ~pk["无尺寸"] & pk["新尺码"].notna()
pk.loc[mask_rewrite, "自动尺码"] = pk.loc[mask_rewrite, "新尺码"]
pk.loc[mask_rewrite, "自动长度余量"] = pk.loc[mask_rewrite, "新余量"]
pk.loc[mask_rewrite, "原因"] = pk.loc[mask_rewrite, "新原因"]
pk.loc[mask_rewrite, "候选"] = pk.loc[mask_rewrite, "新候选"]

# 异常行原因补全: 数据不全保持原原因, 其余超余量行原因已设
print("== 方案A 匹配构成(皮卡):")
print(pk["自动尺码"].value_counts(dropna=False).to_string())
print("  原因分布:", pk["原因"].value_counts(dropna=False).to_dict())
print()

# 合并回全表
match = match.copy()
pk_only = pk[["DIMENSION-ID", "自动尺码", "自动长度余量", "候选", "原因"]]
for col in ["自动尺码", "自动长度余量", "候选", "原因"]:
    match[col] = match["DIMENSION-ID"].map(dict(zip(pk_only["DIMENSION-ID"], pk_only[col])))

# 销量 join (atom_sales)
sales = pd.read_csv(BASE / "input" / "atom_sales.csv", encoding="utf-8-sig")
sales.columns = [c.strip() for c in sales.columns]
sales = sales.copy()
sales["DIMENSION-ID"] = sales["atom_record_id"].astype(str).str.replace(r"\|ATOM_YEAR=\d{4}$", "", regex=True)
sales["预估销量"] = pd.to_numeric(sales["预估销量"], errors="coerce").fillna(0)
tot = sales.groupby("DIMENSION-ID", as_index=False)["预估销量"].sum().rename(columns={"预估销量": "预估销量 的总和"})
match = match.merge(tot, on="DIMENSION-ID", how="left")
match["预估销量 的总和"] = match["预估销量 的总和"].fillna(0)

out_path = BASE / "方案分析" / "数据源" / "匹配_方案A_完整.csv"
match.to_csv(out_path, index=False, encoding="utf-8-sig")
print("已写出:", out_path, "| 行数:", len(match))
print("皮卡行异常核对: 无可用尺码", (match["分类"].astype(str) == "皮卡").sum() - 0,
      "| 无可用:", ((match["分类"].astype(str) == "皮卡") & (match["自动尺码"].astype(str) == "无可用尺码")).sum(),
      "| 数据不全:", ((match["分类"].astype(str) == "皮卡") & (match["自动尺码"].astype(str) == "数据不全")).sum())