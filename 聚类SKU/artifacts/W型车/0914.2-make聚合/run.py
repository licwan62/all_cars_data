"""Experimentally aggregate W-car clusters by logical size and MAKE."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "0914" / "car_cluster_detail.csv"


def joined(values: pd.Series) -> str:
    return " / ".join(sorted({str(value).strip() for value in values if str(value).strip()}))


def make_cluster_id(size: str, make: str) -> str:
    digest = hashlib.sha1(f"{size}|{make}".encode("utf-8")).hexdigest()[:10].upper()
    return f"MAKE-{digest}"


def main() -> None:
    detail = pd.read_csv(SOURCE, encoding="utf-8-sig", dtype=str).fillna("")
    for column in ["L-MM", "W-MM", "H-MM", "销量合计"]:
        detail[column] = pd.to_numeric(detail[column], errors="coerce")

    detail.insert(
        0,
        "MAKE_CLUSTER_ID",
        detail.apply(lambda row: make_cluster_id(row["逻辑尺码"], row["MAKE"]), axis=1),
    )
    original_id_column = "CLUSTER_ID"
    detail = detail.rename(columns={original_id_column: "原MODEL_CLUSTER_ID"})

    summary = detail.groupby(
        ["MAKE_CLUSTER_ID", "逻辑尺码", "MAKE"], sort=False, dropna=False
    ).agg(
        MODEL_COUNT=("MODEL", "nunique"),
        MODELS=("MODEL", joined),
        原MODEL聚类数=("原MODEL_CLUSTER_ID", "nunique"),
        源记录数=("DIMENSION-ID", "count"),
        年份最小=("YEAR", lambda values: min(int(str(v)[:4]) for v in values)),
        年份最大=("YEAR", lambda values: max(int(str(v)[-4:]) for v in values)),
        车长最小毫米=("L-MM", "min"),
        车长最大毫米=("L-MM", "max"),
        车宽最小毫米=("W-MM", "min"),
        车宽最大毫米=("W-MM", "max"),
        车高最小毫米=("H-MM", "min"),
        车高最大毫米=("H-MM", "max"),
        预估销量=("销量合计", "sum"),
    ).reset_index()
    summary["车长跨度毫米"] = summary["车长最大毫米"] - summary["车长最小毫米"]
    summary["车宽跨度毫米"] = summary["车宽最大毫米"] - summary["车宽最小毫米"]
    summary["车高跨度毫米"] = summary["车高最大毫米"] - summary["车高最小毫米"]
    summary["聚合类型"] = summary["MODEL_COUNT"].map(lambda value: "跨MODEL聚合" if value > 1 else "单MODEL")
    summary = summary.sort_values(["逻辑尺码", "预估销量", "MAKE"], ascending=[True, False, True])

    mapping = detail[["原MODEL_CLUSTER_ID", "MAKE_CLUSTER_ID", "逻辑尺码", "MAKE", "MODEL"]].drop_duplicates()
    mapping = mapping.sort_values(["MAKE_CLUSTER_ID", "MODEL", "原MODEL_CLUSTER_ID"])
    review = summary.loc[summary["MODEL_COUNT"] > 1].copy()

    detail.to_csv(HERE / "make_cluster_detail.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(HERE / "make_cluster_summary.csv", index=False, encoding="utf-8-sig")
    mapping.to_csv(HERE / "model_to_make_cluster_mapping.csv", index=False, encoding="utf-8-sig")
    review.to_csv(HERE / "跨MODEL聚合审核.csv", index=False, encoding="utf-8-sig")

    original_clusters = mapping["原MODEL_CLUSTER_ID"].nunique()
    lines = [
        "# W 型车 MAKE 聚合实验", "",
        f"- 输入：`../0914/car_cluster_detail.csv`（{len(detail):,} 条记录）",
        "- 聚类主键：`逻辑尺码 + MAKE`；MODEL 不再参与聚类主键。",
        f"- 原 MODEL 聚类数：{original_clusters:,}",
        f"- MAKE 聚类数：{len(summary):,}",
        f"- 减少聚类数：{original_clusters - len(summary):,}",
        f"- 跨 MODEL 的 MAKE 聚类：{len(review):,}", "",
        "## 审核重点", "",
        "跨 MODEL 聚合只代表同品牌链接合并候选，不自动证明版型相同。优先检查长宽高跨度较大、年代跨度较大以及不同车形混合的聚合。", "",
        "## 输出", "",
        "- `make_cluster_summary.csv`：每个 `逻辑尺码 + MAKE` 一行。",
        "- `make_cluster_detail.csv`：保留全部源记录及原 MODEL 聚类 ID。",
        "- `model_to_make_cluster_mapping.csv`：原 MODEL 聚类到 MAKE 聚类的映射。",
        "- `跨MODEL聚合审核.csv`：只保留 MODEL_COUNT > 1 的审核对象。", "",
    ]
    (HERE / "report.md").write_text("\n".join(lines), encoding="utf-8-sig")
    print(
        f"records={len(detail)} original_clusters={original_clusters} "
        f"make_clusters={len(summary)} cross_model={len(review)}"
    )


if __name__ == "__main__":
    main()
