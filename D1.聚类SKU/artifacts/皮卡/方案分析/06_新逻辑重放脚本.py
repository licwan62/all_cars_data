# -*- coding: utf-8 -*-
"""Replay fx_size_match.pq with NEW ordering (档位序号 asc, 长 asc) and diff vs Excel matching."""
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

# 尺码池: 皮卡, CAB=null (尺码表皮卡 CAB 全空) —— 与新 PQ 一致(取通用池)
pool = sizes[(sizes["分类"] == "皮卡") & (sizes["档位序号"].notna())].copy()
pool = pool[pd.notna(pool["长上限"]) & pd.notna(pool["宽上限"]) & pd.notna(pool["高上限"]) & pd.notna(pool["粗上限"])]
pool = pool.sort_values(["档位序号", "长上限"]).reset_index(drop=True)
print("== 新 PQ 候选顺序(皮卡池):")
print(pool[["内部尺码", "档位序号", "长上限", "宽上限", "高上限", "粗上限"]].to_string(index=False))
print()

L_TOL, W_TOL, H_TOL, MARGIN_TOL = 0, 999, 999, 500


def replay(row):
    L, W, H, T = row["L-MM"], row["W-MM"], row["H-MM"], row["粗"]
    if pd.isna(L) or pd.isna(W) or pd.isna(H):
        return "数据不全", None
    # 基础候选: 第一个满足四维
    hit = None
    for _, s in pool.iterrows():
        if (s["长上限"] >= L - L_TOL and s["宽上限"] >= W - W_TOL
                and s["高上限"] >= H - H_TOL and s["粗上限"] >= T):
            hit = s
            break
    if hit is not None:
        margin = hit["长上限"] - L
        if margin > MARGIN_TOL:
            return "无可用尺码", hit["内部尺码"], "超余量", margin
        return hit["内部尺码"], margin
    # 最近行: 差值最小
    best, best_diff, best_reason = None, None, None
    for _, s in pool.iterrows():
        长缺 = (L - L_TOL) - s["长上限"]
        宽缺 = (W - W_TOL) - s["宽上限"]
        高缺 = (H - H_TOL) - s["高上限"]
        粗缺 = T - s["粗上限"]
        各缺 = [x for x in [长缺, 宽缺, 高缺, 粗缺] if pd.notna(x) and x > 0]
        余量 = s["长上限"] - L
        if not 各缺:
            差值 = max(余量, 0) if 余量 > MARGIN_TOL else 0
        else:
            差值 = max(各缺)
        if best_diff is None or 差值 < best_diff:
            best_diff = 差值
            best = s["内部尺码"]
            # reason
            if 长缺 > 0 and 长缺 >= 宽缺 and 长缺 >= 高缺 and 长缺 >= 粗缺:
                best_reason = "超长"
            elif 宽缺 > 0 and 宽缺 >= 高缺 and 宽缺 >= 粗缺:
                best_reason = "超宽"
            elif 高缺 > 0 and 高缺 >= 粗缺:
                best_reason = "超高"
            elif 粗缺 > 0:
                best_reason = "超粗"
            elif 余量 > MARGIN_TOL:
                best_reason = "超余量"
    return "无可用尺码", best, best_reason, best_diff


results = pk.apply(lambda r: replay(r), axis=1)
pk["新尺码"] = [r[0] for r in results]
pk["新余量"] = [r[1] if len(r) > 1 else None for r in results]
pk["新原因"] = [r[2] if len(r) > 2 else None for r in results]

old = pk["自动尺码"].astype(str)
new = pk["新尺码"].astype(str)
diff = pk[old != new]
print(f"== 与 Excel 现有匹配对比: 变化行 {len(diff)} / {len(pk)}")
print()
if len(diff):
    print("== 变化明细(按 旧→新):")
    d2 = diff.groupby([old.loc[diff.index].str.replace("无可用尺码", "无"), new.loc[diff.index].str.replace("无可用尺码", "无")]).agg(
        行数=("MAKE", "count"),
    )
    print(d2.to_string())
    print()
    print(diff[["MAKE", "MODEL", "版本", "CAB", "BED", "YEAR", "L-MM", "W-MM", "H-MM", "粗",
                "自动尺码", "自动长度余量", "新尺码", "新余量", "新原因"]].to_string(index=False))
print()
print("== 新匹配按规则分段(长度余量):")


def band(m):
    if pd.isna(m):
        return "无余量"
    if m > 500:
        return "不可用(>500)"
    if m >= 150:
        return "警戒(150-500)"
    if m >= 0:
        return "合适(0-150)"
    return "过紧(<0)"


ok = pk[pk["新尺码"].isin(["PK-M", "PK-M+", "PK-L", "PK-XL", "PK-XL+", "PK-XXL", "PK-XXXL", "PK-WX", "PK-WXXL"])].copy()
ok["分段"] = ok["新余量"].apply(band)
print(ok["分段"].value_counts().to_string())
print()
print("== 各尺码行数(新):")
print(ok["新尺码"].value_counts().to_string())
print()
print("== 仍异常(无可用尺码):", (pk["新尺码"] == "无可用尺码").sum(), "| 数据不全:", (pk["新尺码"] == "数据不全").sum())