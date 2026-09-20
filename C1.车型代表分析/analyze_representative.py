# -*- coding: utf-8 -*-
"""按车形生成"销量 + 三维数据代表性"报告。

口径说明
--------
1. 数据范围: source/车型尺寸库.csv(有 L/W/H 的记录) 关联 source/车型形状分类.csv(车形),
   关联 source/atom_sales.csv(预估销量按 DIMENSION-ID 汇总, 缺销量补 0)。
2. 三维代表点: 每个车形内, 以 L/W/H 的"销量加权中位数"作为整体代表点(无销量记录权重为 0,
   全部无销量时退化为普通中位数)。
3. 分档保覆盖: 每个车形内, L / W 按自身三分位分 3 档, H 按自身中位数分 2 档,
   共 3x3x2=18 个三维档位; 记录数 > 0 的档位视为被覆盖。
4. 档内代表: 档内按 综合得分 = 0.6 x 销量归一 + 0.4 x 归一化接近度 排序取第一,
   其中接近度 = 1 - (记录到档内销量加权中位点的三维归一距离) 归一化到 [0,1]。
5. 三维距离使用按车形 min-max 归一化后的 (L, W, H) 欧氏距离, 避免车长量纲主导。
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "source"
OUT = ROOT / "车型代表分析" / "output"

SHAPE_ORDER = ["0", "1", "10", "11", "20", "21", "25", "26", "30", "31", "32", "40", "41", "42", "50"]
SHAPE_NAMES = {
    "0": "Pickup 普通皮卡",
    "1": "Pickup 轮拱外扩皮卡",
    "10": "Pickup 性能宽体皮卡",
    "11": "Pickup 双后轮皮卡",
    "20": "Hatchback/Wagon 圆头两厢/旅行",
    "21": "Hatchback/Wagon 方头两厢/旅行",
    "25": "Minivan 标准 MPV",
    "26": "Van 全尺寸货车",
    "30": "Sedan 标准/Fastback 轿车",
    "31": "Sedan/Coupe Low Sport",
    "32": "Sedan/Coupe Boxy Classic 老式方正轿车",
    "40": "SUV 常规 SUV",
    "41": "SUV Fastback 溜背 SUV",
    "42": "SUV 方正 SUV",
    "50": "SUV 硬派方盒 SUV",
}
WEIGHT_SALES = 0.6
WEIGHT_CLOSE = 0.4
SEG_L = 3
SEG_W = 3
SEG_H = 2


def load():
    dims = pd.read_csv(SRC / "车型尺寸库.csv", encoding="utf-8-sig", dtype={"DIMENSION-ID": str})
    shapes = pd.read_csv(SRC / "车型形状分类.csv", encoding="utf-8-sig", dtype={"DIMENSION-ID": str})
    sales = pd.read_csv(SRC / "atom_sales.csv", encoding="utf-8-sig", dtype={"atom_record_id": str})
    for c in ("L-IN", "W-IN", "H-IN"):
        dims[c] = pd.to_numeric(dims[c], errors="coerce")
    sales["DIMENSION-ID"] = sales["atom_record_id"].str.split("|ATOM_YEAR=", regex=False).str[0]
    sales_agg = sales.groupby("DIMENSION-ID")["预估销量"].sum().rename("销量")
    df = dims.merge(shapes, on="DIMENSION-ID", how="left").merge(sales_agg, on="DIMENSION-ID", how="left")
    df["销量"] = df["销量"].fillna(0.0)
    df["车形"] = df["车形"].astype(str)
    return df


def weighted_median(vals, weights):
    """销量加权中位数; 无销量权重为 0 时退化为普通中位数。"""
    d = pd.DataFrame({"v": pd.to_numeric(vals, errors="coerce"), "w": pd.to_numeric(weights, errors="coerce").fillna(0.0)})
    d = d.dropna(subset=["v"])
    if d.empty:
        return np.nan
    if d["w"].sum() <= 0:
        return float(np.median(d["v"]))
    d = d[d["w"] > 0].sort_values("v")
    cum = d["w"].cumsum() / d["w"].sum()
    return float(d.loc[cum >= 0.5, "v"].iloc[0])


def norm3d(df, lo=None, hi=None):
    """按指定 min/max 归一化 L/W/H; 未给 bounds 时用 df 自身。"""
    out = pd.DataFrame(index=df.index)
    for c in ("L-IN", "W-IN", "H-IN"):
        lo_c = df[c].min() if lo is None else lo[c]
        hi_c = df[c].max() if hi is None else hi[c]
        rng = hi_c - lo_c
        out["N_" + c[0]] = np.where(rng > 0, (df[c] - lo_c) / rng, 0.0)
    return out


def analyze_shape(shape_code, sub):
    """返回单个车形的统计与代表信息。"""
    pool = sub.dropna(subset=["L-IN", "W-IN", "H-IN"]).copy()
    pool = pool[pool["车形"] == shape_code].copy()
    res = {"code": shape_code, "name": SHAPE_NAMES[shape_code]}
    res["n_total"] = len(sub)
    res["n_pool"] = len(pool)
    res["n_missing_dim"] = res["n_total"] - res["n_pool"]
    res["n_sales"] = int((pool["销量"] > 0).sum())
    res["total_sales"] = float(pool["销量"].sum())

    vals = pool[["L-IN", "W-IN", "H-IN"]]
    w = pool["销量"]
    res["med_L"], res["med_W"], res["med_H"] = (
        weighted_median(vals[c], w) for c in ("L-IN", "W-IN", "H-IN")
    )

    # 销量集中度
    s = pool.sort_values("销量", ascending=False)
    if res["total_sales"] > 0:
        top5 = s.head(5)["销量"].sum()
        res["top5_share"] = top5 / res["total_sales"]
        cum = (s["销量"].cumsum() / res["total_sales"]).values
        pos = int(np.argmax(cum >= 0.8)) if (cum >= 0.8).any() else res["n_pool"]
        res["k80"] = pos + 1
        res["k80_share"] = float(s["销量"].head(res["k80"]).sum() / res["total_sales"])
    else:
        res["top5_share"] = 0.0
        res["k80"] = 0
        res["k80_share"] = 0.0

    # 三维分档
    pool = pool.copy()
    lo_b = pool[["L-IN", "W-IN", "H-IN"]].min()
    hi_b = pool[["L-IN", "W-IN", "H-IN"]].max()
    norm = norm3d(pool, lo_b, hi_b)
    pool[["N_L", "N_W", "N_H"]] = norm[["N_L", "N_W", "N_H"]]
    pool["Lseg"] = pd.qcut(pool["L-IN"], SEG_L, labels=False, duplicates="drop").astype(int)
    pool["Wseg"] = pd.qcut(pool["W-IN"], SEG_W, labels=False, duplicates="drop").astype(int)
    pool["Hseg"] = pd.qcut(pool["H-IN"], SEG_H, labels=False, duplicates="drop").astype(int)

    # 整体代表点: 车形销量加权中位数
    center = (res["med_L"], res["med_W"], res["med_H"])
    cn = norm3d(pd.DataFrame([center], columns=["L-IN", "W-IN", "H-IN"]), lo_b, hi_b)
    cx, cy, cz = cn["N_L"].iloc[0], cn["N_W"].iloc[0], cn["N_H"].iloc[0]

    def dist_to(x, y, z):
        return np.sqrt((pool["N_L"] - x) ** 2 + (pool["N_W"] - y) ** 2 + (pool["N_H"] - z) ** 2)

    pool["d_center"] = dist_to(cx, cy, cz)
    near = pool.nsmallest(3, ["d_center", "销量"])

    # 档内代表
    rows = []
    for (li, wi, hi), g in pool.groupby(["Lseg", "Wseg", "Hseg"], observed=True):
        g = g.copy()
        g["d_cell"] = 0.0
        cell_center = (
            weighted_median(g["L-IN"], g["销量"]),
            weighted_median(g["W-IN"], g["销量"]),
            weighted_median(g["H-IN"], g["销量"]),
        )
        cc = norm3d(pd.DataFrame([cell_center], columns=["L-IN", "W-IN", "H-IN"]), lo_b, hi_b)
        ccx, ccy, ccz = cc["N_L"].iloc[0], cc["N_W"].iloc[0], cc["N_H"].iloc[0]
        g["d_cell"] = np.sqrt((g["N_L"] - ccx) ** 2 + (g["N_W"] - ccy) ** 2 + (g["N_H"] - ccz) ** 2)
        g["close"] = 1.0 - g["d_cell"] / g["d_cell"].max() if g["d_cell"].max() > 0 else 1.0
        g["sales_norm"] = g["销量"] / g["销量"].max() if g["销量"].max() > 0 else 0.0
        g["score"] = WEIGHT_SALES * g["sales_norm"] + WEIGHT_CLOSE * g["close"]
        rep = g.loc[g["score"].idxmax()]
        row = {
            "车形": shape_code,
            "Lseg": int(li), "Wseg": int(wi), "Hseg": int(hi),
            "n": len(g),
            "cell_sales": float(g["销量"].sum()),
            "cell_med_L": weighted_median(g["L-IN"], g["销量"]),
            "cell_med_W": weighted_median(g["W-IN"], g["销量"]),
            "cell_med_H": weighted_median(g["H-IN"], g["销量"]),
            "rep_id": rep["DIMENSION-ID"],
            "rep_name": rep["参考车型"] if pd.notna(rep["参考车型"]) else f'{rep["MAKE"]} {rep["MODEL"]} ({rep["YEAR"]})',
            "rep_L": float(rep["L-IN"]), "rep_W": float(rep["W-IN"]), "rep_H": float(rep["H-IN"]),
            "rep_sales": float(rep["销量"]),
            "rep_score": float(rep["score"]),
        }
        rows.append(row)
    cells = pd.DataFrame(rows)
    res["cells"] = cells
    res["n_cells_covered"] = len(cells)
    res["n_cells_total"] = SEG_L * SEG_W * SEG_H
    rep_sales = cells["rep_sales"].sum() if len(cells) else 0.0
    res["rep_set_sales_share"] = rep_sales / res["total_sales"] if res["total_sales"] > 0 else 0.0

    near_rows = []
    for _, r in near.iterrows():
        near_rows.append({
            "车形": shape_code,
            "id": r["DIMENSION-ID"],
            "name": r["参考车型"] if pd.notna(r["参考车型"]) else f'{r["MAKE"]} {r["MODEL"]} ({r["YEAR"]})',
            "L": float(r["L-IN"]), "W": float(r["W-IN"]), "H": float(r["H-IN"]),
            "销量": float(r["销量"]),
            "d_center": float(r["d_center"]),
        })
    res["near_center"] = near_rows

    top_sales = s.head(5)
    top_rows = [{
        "车形": shape_code,
        "id": r["DIMENSION-ID"],
        "name": r["参考车型"] if pd.notna(r["参考车型"]) else f'{r["MAKE"]} {r["MODEL"]} ({r["YEAR"]})',
        "L": float(r["L-IN"]), "W": float(r["W-IN"]), "H": float(r["H-IN"]),
        "销量": float(r["销量"]),
    } for _, r in top_sales.iterrows()]
    res["top_sales"] = top_rows

    top_cls = sub["分类"].value_counts().head(3)
    res["top_classes"] = {str(k): int(v) for k, v in top_cls.items()}
    return res


def fmt_int(x):
    return f"{x:,.0f}"


def fmt_dim(x):
    return f"{x:.1f}" if pd.notna(x) else "-"


def seg_label(code):
    return ("短", "中", "长")[code] if code < 3 else "?"


def h_label(code):
    return ("低", "高")[code]


def build_report(results):
    lines = []
    A = lines.append
    A("# 车形三维代表性与销量报告")
    A("")
    A("基于 `source/车型尺寸库.csv`、`source/车型形状分类.csv`、`source/atom_sales.csv` 生成。")
    A("")
    A("## 方法口径")
    A("")
    A("- **三维数据**: 每条记录的 L-IN / W-IN / H-IN(英寸); 缺失三维的记录不参与分档与选代表, 单独计数。")
    A("- **销量**: `atom_sales.csv` 中同一 DIMENSION-ID 各年预估销量之和; 无销量记录按 0 计。")
    A("- **整体代表点**: 车形内 L/W/H 的销量加权中位数(无销量记录权重为 0)。")
    A("- **分档保覆盖**: 每个车形内 L、W 按三分位分 3 档, H 按中位数分 2 档, 共 3×3×2=18 档; 有记录即视为覆盖。")
    A("- **档内代表**: 档内按综合得分排序取第一, 得分 = 0.6×销量归一 + 0.4×接近度归一; 接近度 = 1 - 记录到档内销量加权中位点的三维归一距离。")
    A("- **三维距离**: 按车形 min-max 归一化的 (L, W, H) 欧氏距离, 避免车长量纲主导。")
    A("")

    A("## 全库概览")
    A("")
    tot_rec = sum(r["n_total"] for r in results)
    tot_pool = sum(r["n_pool"] for r in results)
    tot_sales = sum(r["total_sales"] for r in results)
    A(f"- 尺寸库记录合计 **{tot_rec}** 条, 其中具有完整三维数据 **{tot_pool}** 条(占比 {tot_pool / tot_rec:.1%})。")
    A(f"- 全部车形预估销量合计 **{fmt_int(tot_sales)}** 台(历年累计)。")
    A("")

    A("| 车形 | 分类 | 记录数 | 有销量记录 | 总销量 | L 中位 | W 中位 | H 中位 | 三维档覆盖 | 代表集销量占比 | 80%销量集中记录数 |")
    A("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in results:
        A(f"| {r['code']} | {r['name']} | {r['n_pool']} | {r['n_sales']} | {fmt_int(r['total_sales'])} "
          f"| {fmt_dim(r['med_L'])} | {fmt_dim(r['med_W'])} | {fmt_dim(r['med_H'])} "
          f"| {r['n_cells_covered']}/{r['n_cells_total']} | {r['rep_set_sales_share']:.1%} "
          f"| {r['k80']} / {r['n_pool']} |")
    A("")
    A("注: 中位数为销量加权中位数(英寸); 代表集 = 每个被覆盖档位的档内代表; "
      "80%销量集中记录数 = 按销量降序累计达到车形 80% 销量所需记录数。")
    A("")

    for r in results:
        A(f"## 车形 {r['code']} — {r['name']}")
        A("")
        A(f"- 记录 {r['n_pool']} 条(含无三维 {r['n_missing_dim']} 条), 有销量 {r['n_sales']} 条, 总销量 **{fmt_int(r['total_sales'])}**。")
        A(f"- 三维整体代表点(L/W/H 销量加权中位, 英寸): **{fmt_dim(r['med_L'])} / {fmt_dim(r['med_W'])} / {fmt_dim(r['med_H'])}**。")
        A(f"- 销量集中度: 前 5 名占 {r['top5_share']:.1%}; 累计 {r['k80']} 条记录(占记录数 {r['k80'] / r['n_pool']:.1%})可达 80% 销量。")
        if r["n_missing_dim"]:
            A(f"- 另有 {r['n_missing_dim']} 条无三维数据(如待补尺寸), 未参与选代表。")
        A(f"- 主要分类分布: " + ", ".join(f"{k}×{v}" for k, v in r["top_classes"].items()) + "。")
        A("")
        A("### 近整体代表点 TOP3(最接近销量加权中位点的记录)")
        A("")
        A("| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |")
        A("|---|---|---:|---:|---:|---:|---:|")
        for nr in r["near_center"]:
            A(f"| {nr['id']} | {nr['name']} | {fmt_dim(nr['L'])} | {fmt_dim(nr['W'])} | {fmt_dim(nr['H'])} | {fmt_int(nr['销量'])} | {nr['d_center']:.3f} |")
        A("")
        A("### 三维档位覆盖与档内代表")
        A("")
        if r["cells"].empty:
            A("(无有效记录)")
        else:
            A("| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |")
            A("|---|---|---|---:|---:|---|---|---:|---:|---:|")
            for _, c in r["cells"].sort_values(["Lseg", "Wseg", "Hseg"]).iterrows():
                A(f"| {seg_label(c['Lseg'])} | {seg_label(c['Wseg'])} | {h_label(c['Hseg'])} "
                  f"| {int(c['n'])} | {fmt_int(c['cell_sales'])} "
                  f"| {fmt_dim(c['cell_med_L'])}/{fmt_dim(c['cell_med_W'])}/{fmt_dim(c['cell_med_H'])} "
                  f"| {c['rep_name']} (`{c['rep_id']}`) "
                  f"| {fmt_dim(c['rep_L'])}/{fmt_dim(c['rep_W'])}/{fmt_dim(c['rep_H'])} "
                  f"| {fmt_int(c['rep_sales'])} | {c['rep_score']:.3f} |")
        A("")
        A("### 销量 TOP5(不要求贴近三维中心)")
        A("")
        A("| 记录 | 代表车型 | L | W | H | 销量 |")
        A("|---|---|---:|---:|---:|---:|")
        for tr in r["top_sales"]:
            A(f"| {tr['id']} | {tr['name']} | {fmt_dim(tr['L'])} | {fmt_dim(tr['W'])} | {fmt_dim(tr['H'])} | {fmt_int(tr['销量'])} |")
        A("")
    A("## 说明与风险")
    A("")
    A("- 销量为历年原子销量累加, 含 2026 年未结束年份的年度化预估, 跨年份叠加仅为相对权重比较。")
    A("- 无销量记录(如停产早期年款)不代表不重要, 只说明未能关联到销量; 分档覆盖仍包含它们。")
    A("- 档内代表在销量为 0 的档位中按接近度选取, 可视为该尺寸区间的结构代表而非销量代表。")
    A("- 迭代状态非“可入库”的记录(待终核、待补尺寸等)仍纳入统计; 可 `record_scores.csv` 中查看状态列交叉核对。")
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load()
    results = []
    score_rows = []
    for code in SHAPE_ORDER:
        sub = df[df["车形"] == code]
        if sub.empty:
            continue
        r = analyze_shape(code, sub)
        results.append(r)
        # 全记录得分表(供核查)
        pool = sub.dropna(subset=["L-IN", "W-IN", "H-IN"]).copy()
        pool["车形"] = code
        score_rows.append(pool[["车形", "DIMENSION-ID", "MAKE", "MODEL", "YEAR", "L-IN", "W-IN", "H-IN", "参考车型", "销量", "迭代状态"]])
    report = build_report(results)
    (OUT / "representative_report.md").write_text(report, encoding="utf-8")

    matrix = pd.concat([r["cells"] for r in results], ignore_index=True)
    matrix.to_csv(OUT / "representative_matrix.csv", index=False, encoding="utf-8-sig")

    scores = pd.concat(score_rows, ignore_index=True)
    scores.to_csv(OUT / "record_scores.csv", index=False, encoding="utf-8-sig")

    print(f"OK: report={OUT / 'representative_report.md'}")
    print(f"OK: matrix={OUT / 'representative_matrix.csv'} ({len(matrix)} rows)")
    print(f"OK: scores={OUT / 'record_scores.csv'} ({len(scores)} rows)")


if __name__ == "__main__":
    main()