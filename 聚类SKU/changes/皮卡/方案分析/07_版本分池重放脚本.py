# -*- coding: utf-8 -*-
"""重放新版 fx_size_match.pq 逻辑:
- 尺码表: 删宽高列; 新增版本列(PK-WX/WXXL 版本=DRW); 通用档粗上限 6280->6400
- 匹配: 同CAB同版本池 -> 同版本通用CAB池 -> 通用池; 判定仅 长/粗, 无容差
"""
import sys
import io
import pandas as pd
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = Path(__file__).parent
xl = pd.ExcelFile(str(BASE / "input" / "车型数据尺码.xlsx"))
sizes = xl.parse("尺码")
match = xl.parse("尺码匹配")
match.columns = [c.strip() for c in match.columns]
pk = match[match["分类"].astype(str).str.strip() == "皮卡"].copy()
pk["粗"] = pk["W-MM"] + 2 * pk["H-MM"]

# ---- 构造新版尺码表(内存, 不落盘) ----
pool = sizes[sizes["分类"] == "皮卡"][["内部尺码", "档位序号", "长上限", "粗上限"]].copy()
pool["长_in"] = pool["长上限"]
pool["粗_in"] = pool["粗上限"]
pool = pool.drop(columns=["长上限", "粗上限"])
pool["版本"] = None
pool["分类"] = "皮卡"
pool["CAB"] = None
pool.loc[pool["内部尺码"].isin(["PK-WX", "PK-WXXL"]), "版本"] = "DRW"
pool.loc[~pool["内部尺码"].isin(["PK-WX", "PK-WXXL"]), "粗_in"] = 6400.0  # 通用档包容宽体粗
pool = pool.reset_index(drop=True)
pool = pool[pool["档位序号"].notna() & pool["长_in"].notna() & pool["粗_in"].notna()].reset_index(drop=True)
pool = pool.sort_values(["档位序号", "长_in"]).reset_index(drop=True)
print("== 新版尺码池:")
print(pool[["内部尺码", "版本", "档位序号", "长_in", "粗_in"]].to_string(index=False))
print()

MARGIN_TOL = 500


def get_pool(cat, cab, ver):
    sub = pool
    if cat is not None:
        sub = sub[sub["分类"] == cat]
    if cab is not None:
        sub = sub[sub["CAB"].astype(object) == cab]
    if ver is not None:
        sub = sub[sub["版本"].astype(object) == ver]
    else:
        sub = sub[sub["版本"].isna()]
    return sub.sort_values(["档位序号", "长_in"])


def calc_single(p, L, T):
    hit = p[(p["长_in"] >= L) & (p["粗_in"] >= T)]
    if len(hit):
        s = hit.iloc[0]
        margin = s["长_in"] - L
        if margin > MARGIN_TOL:
            return ("无可用尺码", s["内部尺码"], "超余量")
        return (s["内部尺码"], margin)
    return ("无可用尺码", None, "无候选")


def calc_size(分类, CAB, 版本, L, T):
    for cat, cab, ver in [(分类, CAB, 版本), (分类, None, 版本), (分类, None, None)]:
        p = get_pool(cat, cab, ver)
        r = calc_single(p, L, T)
        if r[0] not in ("无可用尺码",):
            return r
    return calc_single(get_pool(分类, None, None), L, T)


pk["IS_DRW"] = pk["版本"].fillna("").str.contains("DRW", case=False, na=False)
pk["版本池键"] = pk["版本"].fillna("")
results = []
for _, r in pk.iterrows():
    if pd.isna(r["L-MM"]) or pd.isna(r["W-MM"]) or pd.isna(r["H-MM"]):
        results.append(("数据不全", None))
    else:
        v = "DRW" if r["IS_DRW"] else str(r["版本"] or "")
        results.append(calc_size("皮卡", str(r["CAB"] or ""), v if len(v) > 0 else None, r["L-MM"], r["粗"]))

pk["新尺码"] = [x[0] for x in results]
pk["新余量"] = [x[1] for x in results]

old = pk["自动尺码"].astype(str)
new = pk["新尺码"].astype(str)
diff = pk[old != new]
print("== vs Excel 现有匹配: 变化行", len(diff), "/", len(pk))
if len(diff):
    print(diff[["MAKE", "MODEL", "版本", "CAB", "YEAR", "L-MM", "W-MM", "H-MM", "粗",
                "自动尺码", "新尺码", "新余量"]].to_string(index=False))
print()

# focus 宽体SRW
f = pk[pk["版本"].fillna("").str.contains("TRX|RHO|Raptor R", case=False, na=False)]
print("== 宽体SRW(TRX/RHO/Raptor R)结果:")
print(f[["MAKE", "MODEL", "版本", "YEAR", "粗", "自动尺码", "新尺码", "新余量"]].to_string(index=False))
print()
print("== 新构成:")
ok = pk[pk["新尺码"].notna() & ~pk["新尺码"].isin(["无可用尺码", "数据不全"])]
print(ok["新尺码"].value_counts().to_string())
print()
print("== PK-WX 剩余:", len(ok[ok["新尺码"] == "PK-WX"]), "行, 全部DRW:",
      (ok.loc[ok["新尺码"] == "PK-WX", "IS_DRW"] == True).all())
print("== 异常: 无可用尺码", (pk["新尺码"] == "无可用尺码").sum(), "| 数据不全", (pk["新尺码"] == "数据不全").sum())
seg = ok.copy()
seg["分段"] = seg["新余量"].apply(lambda m: "合适" if 0 <= m <= 150 else ("警戒" if 150 < m <= 500 else ("过紧" if m < 0 else "无")))
print("== 分段:", seg["分段"].value_counts().to_dict())