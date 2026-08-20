# -*- coding: utf-8 -*-
"""方案B验证: DRW 粗硬限(0容差), 非DRW 粗容差200; 档位序号升序优先 —— 对比现有 Excel."""
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
pk["IS_DRW"] = pk["版本"].fillna("").str.contains("DRW", case=False, na=False)

pool = sizes[(sizes["分类"] == "皮卡") & (sizes["档位序号"].notna())].copy()
pool = pool[pd.notna(pool["长上限"]) & pd.notna(pool["宽上限"]) & pd.notna(pool["高上限"]) & pd.notna(pool["粗上限"])]
pool = pool.sort_values(["档位序号", "长上限"]).reset_index(drop=True)

L_TOL, W_TOL, H_TOL, MARGIN_TOL = 0, 999, 999, 500
G_TOL_DRW, G_TOL_SRW = 0, 200  # 方案B: DRW 粗硬限, 非DRW 粗容差200


def replay(row):
    L, W, H, T = row["L-MM"], row["W-MM"], row["H-MM"], row["粗"]
    if pd.isna(L) or pd.isna(W) or pd.isna(H):
        return "数据不全", None
    g_tol = G_TOL_DRW if row["IS_DRW"] else G_TOL_SRW
    hit = None
    for _, s in pool.iterrows():
        if (s["长上限"] >= L - L_TOL and s["宽上限"] >= W - W_TOL
                and s["高上限"] >= H - H_TOL and s["粗上限"] >= T - g_tol):
            hit = s
            break
    if hit is not None:
        margin = hit["长上限"] - L
        if margin > MARGIN_TOL:
            return "无可用尺码", hit["内部尺码"], "超余量", margin
        return hit["内部尺码"], margin
    return "无可用尺码", None, "无匹配", None


results = pk.apply(lambda r: replay(r), axis=1)
pk["新尺码"] = [r[0] for r in results]
pk["新余量"] = [r[1] for r in results]

old = pk["自动尺码"].astype(str)
new = pk["新尺码"].astype(str)
diff = pk[old != new]
print("== 方案B vs Excel 现有匹配: 变化行", len(diff), "/", len(pk))
if len(diff):
    print(diff[["MAKE", "MODEL", "版本", "CAB", "BED", "YEAR", "L-MM", "W-MM", "H-MM", "粗",
                "自动尺码", "自动长度余量", "新尺码", "新余量"]].to_string(index=False))
print()

# 关注: TRX / RHO / Raptor R
focus = pk[pk["版本"].fillna("").str.contains("TRX|RHO|Raptor", case=False, na=False)]
print("== 宽体SRW 三款车 (TRX/RHO/Raptor) 新旧对比:")
print(focus[["MAKE", "MODEL", "版本", "YEAR", "L-MM", "W-MM", "H-MM", "粗", "自动尺码", "新尺码", "新余量"]].to_string(index=False))
print()
print("== 新构成: 各尺码行数")
ok = pk[pk["新尺码"].isin(pool["内部尺码"])]
print(ok["新尺码"].value_counts().to_string())
print()
print("== PK-WX 剩余行(应全部为 DRW):")
wx = ok[ok["新尺码"] == "PK-WX"]
print(wx[["MAKE", "MODEL", "版本", "CAB", "YEAR", "L-MM", "粗", "IS_DRW"]].to_string(index=False))
print("  PK-WX 中非DRW:", (wx["IS_DRW"] == False).sum(), "| DRW:", (wx["IS_DRW"] == True).sum())
print()


def band(m):
    if pd.isna(m):
        return "无"
    if m > 500:
        return "不可用(>500)"
    if m >= 150:
        return "警戒(150-500)"
    if m >= 0:
        return "合适(0-150)"
    return "过紧"


ok["分段"] = ok["新余量"].apply(band)
print("== 新匹配分段: 合适", (ok["分段"] == "合适(0-150)").sum(), "| 警戒", (ok["分段"] == "警戒(150-500)").sum(),
      "| 不可用", (ok["分段"] == "不可用(>500)").sum(), "| 过紧", (ok["分段"] == "过紧").sum())
print("== 异常: 无可用尺码", (pk["新尺码"] == "无可用尺码").sum(), "| 数据不全", (pk["新尺码"] == "数据不全").sum())