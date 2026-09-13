# -*- coding: utf-8 -*-
"""使用用户修改后的 方案分析/数据源/车型数据尺码.xlsx:
- 重放方案A(版本池优先) 预期匹配
- 对比 Excel 当前匹配(方案B刷新结果)
- 分析异常行结构"""
import sys
import io
import pandas as pd
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent  # pickup-cluster 项目根
XLSX = BASE / "方案分析" / "数据源" / "车型数据尺码.xlsx"
xl = pd.ExcelFile(str(XLSX))
sizes = xl.parse("尺码")
match = xl.parse("尺码匹配")
match.columns = [c.strip() for c in match.columns]
pk = match[match["分类"].astype(str).str.strip() == "皮卡"].copy()
pk["粗"] = pk["W-MM"] + 2 * pk["H-MM"]
pk["不完整"] = pk["L-MM"].isna() | pk["W-MM"].isna() | pk["H-MM"].isna()

# 尺码池: 直接用用户 Excel(已含版本列/粗上限)
pool = sizes[sizes["分类"] == "皮卡"].copy()
pool = pool[pool["档位序号"].notna() & pool["长上限"].notna() & pool["粗上限"].notna()]
pool = pool.sort_values(["档位序号", "长上限"]).reset_index(drop=True)
print("== 尺码池(用户Excel):")
print(pool[["内部尺码", "版本", "档位序号", "长上限", "粗上限", "使用"]].to_string(index=False))
print()

MARGIN_TOL = 500

def calc_single(p, L, T):
    hit = p[(p["长上限"] >= L) & (p["粗上限"] >= T)]
    if len(hit):
        s = hit.iloc[0]
        margin = s["长上限"] - L
        if margin > MARGIN_TOL:
            # 超余量 = 无最终候选(与 PQ 语义一致), 调用方继续回退下一池
            return ("无可用尺码", s["内部尺码"], False)
        return (s["内部尺码"], margin, True)
    return (None, None, False)

def calc(分类, CAB, 版本, L, T, 不完整):
    if 不完整:
        return ("数据不全", None)
    # 方案A: 同CAB同版本 -> 同版本通用CAB -> 通用版本; 超余量/无候选继续回退
    tried = []
    for cat, cab, ver in [(分类, CAB, 版本), (分类, None, 版本), (分类, None, None)]:
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
        if r[2]:
            return r
        tried.append(r)
    # 兜底: 最后尝试的池(与 PQ: else 通用结果 一致)
    last = tried[-1] if tried else (None, None, False)
    return (last[0], last[1])

pk["IS_DRW"] = pk["版本"].fillna("").str.contains("DRW", case=False, na=False)
out = []
for _, r in pk.iterrows():
    v = "DRW" if r["IS_DRW"] else None
    res = calc("皮卡", str(r["CAB"] or "") or None, v, r["L-MM"], r["粗"], r["不完整"])
    out.append(res)
pk["重放尺码"] = [x[0] for x in out]
pk["重放余量"] = [x[1] for x in out]

print("== 用户当前匹配(方案B刷新) vs 方案A重放: 差异行")
diff = pk[pk["自动尺码"].astype(str) != pk["重放尺码"].astype(str)]
print("  差异行数:", len(diff), "/", len(pk))
if len(diff):
    print(diff[["MAKE", "MODEL", "版本", "CAB", "YEAR", "L-MM", "粗",
                "自动尺码", "自动长度余量", "重放尺码", "重放余量"]].to_string(index=False))
print()

print("== 方案A 重放构成:")
ok = pk[pk["重放尺码"].notna() & ~pk["重放尺码"].isin(["无可用尺码", "数据不全"])]
print(ok["重放尺码"].value_counts().to_string())
print()
for s in ["PK-WX", "PK-WXXL"]:
    sub = ok[ok["重放尺码"] == s]
    print(f"  {s}: {len(sub)} 行 | 全DRW: {(sub['IS_DRW'] == True).all()} | 车型: {sorted(sub['MAKE'].unique())}")
print()
print("== 异常行结构(用户当前匹配):")
exc = pk[pk["自动尺码"].isna() | pk["自动尺码"].astype(str).isin(["无可用尺码", "数据不全"])]
print(exc.groupby(["原因", "自动尺码"]).size().to_string())
print()
print("== 用户匹配 超余量/无可用 明细:")
bad = pk[pk["自动尺码"].astype(str) == "无可用尺码"]
print(bad[bad["原因"].notna()][["MAKE", "MODEL", "版本", "CAB", "YEAR", "L-MM", "粗", "自动长度余量", "候选", "原因", "相差数值"]].to_string(index=False))
print("  原因NaN但无可用尺码的行数:", len(bad[bad["原因"].isna()]))
print(bad[bad["原因"].isna()][["MAKE", "MODEL", "版本", "CAB", "YEAR", "L-MM", "粗"]].to_string(index=False))
print()
print("== 方案A重放 异常:")
print(pk[pk["重放尺码"].isin(["无可用尺码", "数据不全"])].groupby("重放尺码").size().to_string())