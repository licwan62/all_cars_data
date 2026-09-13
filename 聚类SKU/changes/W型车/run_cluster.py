"""Cluster selected large-car logical sizes from public/全量数据.csv.

Outputs are analysis artifacts only.  The script never rewrites public inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import pandas as pd


TARGET_SIZES = ["3L-W", "3XL-W", "3XXL-W", "3XXXL", "3XXXXL"]
ATOM_FIELDS = ["MAKE", "MODEL", "TRIM_ATOM", "版本", "结构", "ATOM_YEAR"]


def split_values(value: object) -> list[str]:
    values = [part.strip() for part in str(value or "").split(",") if part.strip()]
    return values or [""]


def parse_years(value: object) -> list[int]:
    match = re.fullmatch(r"\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*", str(value or ""))
    if not match:
        return []
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        return []
    return list(range(start, end + 1))


def compact_years(years: list[int]) -> str:
    if not years:
        return ""
    ordered = sorted(set(years))
    spans: list[tuple[int, int]] = []
    start = end = ordered[0]
    for year in ordered[1:]:
        if year == end + 1:
            end = year
        else:
            spans.append((start, end))
            start = end = year
    spans.append((start, end))
    return "/".join(str(a) if a == b else f"{a}-{b}" for a, b in spans)


def joined(values: pd.Series) -> str:
    unique = sorted({str(v).strip() for v in values if str(v).strip()})
    return " / ".join(unique)


def cluster_id(size: str, make: str, model: str) -> str:
    digest = hashlib.sha1(f"{size}|{make}|{model}".encode("utf-8")).hexdigest()[:10].upper()
    return f"CAR-{digest}"


def main() -> None:
    parser = argparse.ArgumentParser()
    repo = Path(__file__).resolve().parents[2]
    parser.add_argument("--data", type=Path, default=repo / "public" / "全量数据.csv")
    parser.add_argument("--rules", type=Path, default=repo / "public" / "尺码匹配规则.csv")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(args.data, encoding="utf-8-sig", dtype=str).fillna("")
    rules = pd.read_csv(args.rules, encoding="utf-8-sig", dtype=str).fillna("")
    internal_to_logical = dict(zip(rules["内部尺码"], rules["逻辑尺码"]))
    data["逻辑尺码"] = data["自动尺码"].map(internal_to_logical).fillna(data["自动尺码"])
    selected = data[data["逻辑尺码"].isin(TARGET_SIZES)].copy()
    selected["SOURCE_ROW"] = selected.index + 2
    selected["CLUSTER_ID"] = selected.apply(
        lambda r: cluster_id(r["逻辑尺码"], r["MAKE"], r["MODEL"]), axis=1
    )

    atoms: list[dict[str, object]] = []
    invalid_year_rows: list[int] = []
    for idx, row in selected.iterrows():
        years = parse_years(row["YEAR"])
        if not years:
            invalid_year_rows.append(idx)
            continue
        for trim in split_values(row["TRIM"]):
            for year in years:
                atoms.append(
                    {
                        "MAKE": row["MAKE"], "MODEL": row["MODEL"], "TRIM_ATOM": trim,
                        "版本": row["版本"], "结构": row["结构"], "ATOM_YEAR": year,
                        "逻辑尺码": row["逻辑尺码"], "自动尺码": row["自动尺码"],
                        "CLUSTER_ID": row["CLUSTER_ID"], "SOURCE_ROW": row["SOURCE_ROW"],
                    }
                )
    atom_df = pd.DataFrame(atoms)
    ownership = atom_df.groupby(ATOM_FIELDS, dropna=False).agg(
        PHYSICAL_SKU_COUNT=("逻辑尺码", "nunique"),
        CLUSTER_COUNT=("CLUSTER_ID", "nunique"),
        LOGICAL_SIZES=("逻辑尺码", joined),
        CLUSTER_IDS=("CLUSTER_ID", joined),
        SOURCE_ROWS=("SOURCE_ROW", lambda s: ",".join(map(str, sorted(set(s))))),
    ).reset_index()
    ownership["STATUS"] = "OK"
    ownership.loc[ownership["CLUSTER_COUNT"] > 1, "STATUS"] = "MULTI_CLUSTER"
    ownership.loc[ownership["PHYSICAL_SKU_COUNT"] > 1, "STATUS"] = "PHYSICAL_SKU_CONFLICT"

    numeric = ["L-MM", "W-MM", "H-MM", "销量合计", "自动长度余量", "相差数值"]
    for col in numeric:
        selected[col] = pd.to_numeric(selected[col], errors="coerce")

    summaries: list[dict[str, object]] = []
    for (size, make, model), group in selected.groupby(["逻辑尺码", "MAKE", "MODEL"], sort=False):
        years = [year for value in group["YEAR"] for year in parse_years(value)]
        cid = cluster_id(size, make, model)
        cat = joined(group["分类"])
        structures = joined(group["结构"])
        variants = joined(group["版本"])
        trims = joined(group["TRIM"])
        generations = joined(group["代际"])
        label_parts = [f"{make} {model}", structures, compact_years(years)]
        consumer_name = " · ".join(part for part in label_parts if part)
        summaries.append({
            "CLUSTER_ID": cid, "逻辑尺码": size, "自动尺码": joined(group["自动尺码"]),
            "CONSUMER_NAME": consumer_name, "MAKE": make, "MODEL": model,
            "分类": cat, "结构": structures, "版本": variants, "TRIM": trims, "代际": generations,
            "YEAR_COMPACT": compact_years(years), "YEAR_MIN": min(years), "YEAR_MAX": max(years),
            "SOURCE_RECORD_COUNT": len(group),
            "ATOM_COUNT": len(atom_df[atom_df["CLUSTER_ID"] == cid]),
            "L_MIN": group["L-MM"].min(), "L_MAX": group["L-MM"].max(), "L_SPREAD": group["L-MM"].max() - group["L-MM"].min(),
            "W_MIN": group["W-MM"].min(), "W_MAX": group["W-MM"].max(), "W_SPREAD": group["W-MM"].max() - group["W-MM"].min(),
            "H_MIN": group["H-MM"].min(), "H_MAX": group["H-MM"].max(), "H_SPREAD": group["H-MM"].max() - group["H-MM"].min(),
            "LENGTH_MARGIN_MIN": group["自动长度余量"].min(),
            "LENGTH_MARGIN_MEDIAN": group["自动长度余量"].median(),
            "DIFF_MEDIAN": group["相差数值"].median(), "ESTIMATED_SALES": group["销量合计"].sum(),
            "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": int((ownership["STATUS"] == "PHYSICAL_SKU_CONFLICT").sum()),
            "MERGE_STATUS": "ACCEPT",
        })
    summary = pd.DataFrame(summaries)
    summary["__size_order"] = summary["逻辑尺码"].map({v: i for i, v in enumerate(TARGET_SIZES)})
    summary = summary.sort_values(["__size_order", "ESTIMATED_SALES", "MAKE", "MODEL"], ascending=[True, False, True, True]).drop(columns="__size_order")

    detail_cols = ["CLUSTER_ID", "逻辑尺码", "自动尺码", "MAKE", "MODEL", "TRIM", "版本", "结构", "代际", "YEAR", "分类", "L-MM", "W-MM", "H-MM", "销量合计", "自动长度余量", "相差数值", "DIMENSION-ID", "SOURCE_ROW"]
    selected[detail_cols].to_csv(args.output / "car_cluster_detail.csv", index=False, encoding="utf-8-sig", float_format="%.1f")
    summary.to_csv(args.output / "car_cluster_summary.csv", index=False, encoding="utf-8-sig", float_format="%.1f")
    ownership.to_csv(args.output / "car_cluster_atom_audit.csv", index=False, encoding="utf-8-sig")

    by_size = summary.groupby("逻辑尺码", sort=False).agg(
        聚类数=("CLUSTER_ID", "nunique"), 记录数=("SOURCE_RECORD_COUNT", "sum"),
        原子数=("ATOM_COUNT", "sum"), 销量合计=("ESTIMATED_SALES", "sum")
    ).reindex(TARGET_SIZES)
    table_lines = ["| 逻辑尺码 | 聚类数 | 记录数 | 原子数 | 销量合计 |", "|---|---:|---:|---:|---:|"]
    for size, row in by_size.iterrows():
        table_lines.append(
            f"| {size} | {int(row['聚类数'])} | {int(row['记录数'])} | {int(row['原子数'])} | {int(row['销量合计'])} |"
        )
    report = [
        "# public 全量数据大尺码 SKU 聚类报告", "",
        f"输入：`public/全量数据.csv`（{len(data):,} 条）", "",
        f"范围：{', '.join(TARGET_SIZES)}；命中 {len(selected):,} 条记录。", "",
        "## 结果概览", "", *table_lines, "",
        f"共形成 {len(summary):,} 个消费者车型簇，覆盖 {atom_df[ATOM_FIELDS].drop_duplicates().shape[0]:,} 个唯一原子事实。", "",
        f"跨逻辑尺码原子冲突：{int((ownership['PHYSICAL_SKU_COUNT'] > 1).sum()):,}。", "",
        f"多 Cluster 原子重叠：{int((ownership['CLUSTER_COUNT'] > 1).sum()):,}。", "",
        f"无法解析年份的源记录：{len(invalid_year_rows):,}。", "",
        "## 聚类口径", "",
        "- 先依据 `尺码匹配规则.csv` 将内部尺码映射为逻辑尺码。",
        "- 消费者簇主键为 `逻辑尺码 + MAKE + MODEL`，车身结构、版本、TRIM、代际和年份作为簇内适配信息保留。",
        "- 原子事实为 `MAKE + MODEL + TRIM + 版本 + 结构 + YEAR`；年份与逗号分隔 TRIM 均展开后做全局唯一性检查。",
        "- 本轮不生成源数据中不存在的 YEAR / TRIM / 版本 / 结构组合。",
        "- 聚类结果仅写入本项目 output，不修改 public 数据。", "",
        "## 输出", "",
        f"- `car_cluster_summary.csv`：{len(summary)} 个消费者簇及尺寸、销量和适配概览。",
        f"- `car_cluster_detail.csv`：{len(selected)} 条源记录及所属 Cluster。",
        "- `car_cluster_atom_audit.csv`：原子事实唯一性审计。", "",
    ]
    (args.output / "report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"rows={len(selected)} clusters={len(summary)} atoms={len(ownership)} conflicts={(ownership['PHYSICAL_SKU_COUNT'] > 1).sum()}")


if __name__ == "__main__":
    main()
