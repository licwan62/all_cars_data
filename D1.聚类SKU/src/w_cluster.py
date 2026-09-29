"""按 data/W型车目标尺码.json 的逻辑尺码，从 A0 US 全量表聚类大尺码消费者车型簇。

结果只写入本节点 artifacts 批次，不改写任何上游数据。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
import re
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
# 目标尺码与专用尺码是业务配置，维护在 data/W型车目标尺码.json
CONFIG = json.loads((PROJECT / "data" / "W型车目标尺码.json").read_text(encoding="utf-8"))
TARGET_SIZES = list(CONFIG["target_sizes"])

# Chevrolet Bel Air 1953-1957 has a notably taller cabin and hood profile
# than the later, wider/lower full-size cars.  It is a protected dedicated
# pattern, rather than a new global size rule: only the explicitly matched
# non-wagon records below may use it.
DEDICATED_SIZE = CONFIG["dedicated_size"]
DEDICATED_MAX_YEAR = int(CONFIG["dedicated_max_year"])
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


def is_bel_air_high_pattern(row: pd.Series) -> bool:
    """Return whether a source row belongs to the dedicated high-profile pattern."""
    years = parse_years(row["YEAR"])
    return (
        row["MAKE"] == "Chevrolet"
        and row["MODEL"] == "Bel Air"
        and row["结构"] != "Wagon"
        and years
        and max(years) <= DEDICATED_MAX_YEAR
    )


def next_artifact_dir() -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = [int(p.name[len(prefix):len(prefix) + 2]) for p in (PROJECT / "artifacts").glob(f"{prefix}[0-9][0-9]_*")]
    return PROJECT / "artifacts" / f"{prefix}{max(used, default=0) + 1:02d}_w-cluster"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=REPO / "A0.尺码计算" / "output" / "US" / "全量" / "全量表.csv")
    parser.add_argument("--rules", type=Path, help="可选：含 内部尺码/逻辑尺码 双列的映射表；缺省时逻辑尺码 = 自动尺码")
    parser.add_argument("--output", type=Path, help="默认在 artifacts/ 下新建 <日期>_<序号>_w-cluster/ 批次")
    args = parser.parse_args()
    args.output = args.output or next_artifact_dir()
    args.output.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(args.data, encoding="utf-8-sig", dtype=str).fillna("")
    # A0 全量表的逐行销量为 尺寸组销量；本节点输出沿用 销量合计 供 D2 读取
    data = data.rename(columns={"尺寸组销量": "销量合计"})
    rules = pd.read_csv(args.rules, encoding="utf-8-sig", dtype=str).fillna("") if args.rules else pd.DataFrame(columns=["尺码"])
    if {"内部尺码", "逻辑尺码"}.issubset(rules.columns):
        internal_to_logical = dict(zip(rules["内部尺码"], rules["逻辑尺码"]))
        rule_schema = "逻辑尺码/内部尺码双列结构"
    elif "尺码" in rules.columns:
        internal_to_logical = {size: size for size in rules["尺码"] if size}
        rule_schema = "尺码单列结构" if args.rules else "无映射表（逻辑尺码 = 自动尺码）"
    else:
        raise ValueError("尺码匹配规则缺少‘尺码’或‘内部尺码/逻辑尺码’字段")
    data["逻辑尺码"] = data["自动尺码"].map(internal_to_logical).fillna(data["自动尺码"])
    data.loc[data.apply(is_bel_air_high_pattern, axis=1), "逻辑尺码"] = DEDICATED_SIZE
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
        if pd.isna(row["聚类数"]):
            continue
        table_lines.append(
            f"| {size} | {int(row['聚类数'])} | {int(row['记录数'])} | {int(row['原子数'])} | {int(row['销量合计'])} |"
        )
    report = [
        "# 大尺码 SKU 聚类报告", "",
        f"输入：`{args.data}`（{len(data):,} 条）", "",
        f"范围：{', '.join(TARGET_SIZES)}；命中 {len(selected):,} 条记录。", "",
        "## 结果概览", "", *table_lines, "",
        f"共形成 {len(summary):,} 个消费者车型簇，覆盖 {atom_df[ATOM_FIELDS].drop_duplicates().shape[0]:,} 个唯一原子事实。", "",
        f"跨逻辑尺码原子冲突：{int((ownership['PHYSICAL_SKU_COUNT'] > 1).sum()):,}。", "",
        f"多 Cluster 原子重叠：{int((ownership['CLUSTER_COUNT'] > 1).sum()):,}。", "",
        f"无法解析年份的源记录：{len(invalid_year_rows):,}。", "",
        "## 聚类口径", "",
        f"- 规则表采用{rule_schema}；双列结构映射到逻辑尺码，单列结构直接使用尺码。",
        "- 消费者簇主键为 `逻辑尺码 + MAKE + MODEL`，车身结构、版本、TRIM、代际和年份作为簇内适配信息保留。",
        "- 原子事实为 `MAKE + MODEL + TRIM + 版本 + 结构 + YEAR`；年份与逗号分隔 TRIM 均展开后做全局唯一性检查。",
        "- 本轮不生成源数据中不存在的 YEAR / TRIM / 版本 / 结构组合。",
        "- 聚类结果写入本节点 artifacts 批次，不修改上游数据。", "",
        "## 输出", "",
        f"- `car_cluster_summary.csv`：{len(summary)} 个消费者簇及尺寸、销量和适配概览。",
        f"- `car_cluster_detail.csv`：{len(selected)} 条源记录及所属 Cluster。",
        "- `car_cluster_atom_audit.csv`：原子事实唯一性审计。", "",
    ]
    (args.output / "report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"rows={len(selected)} clusters={len(summary)} atoms={len(ownership)} conflicts={(ownership['PHYSICAL_SKU_COUNT'] > 1).sum()}")


if __name__ == "__main__":
    main()
