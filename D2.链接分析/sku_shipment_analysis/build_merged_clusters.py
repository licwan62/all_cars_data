"""Run cluster-level merge tests, issue new IDs, and optionally publish the result."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

import pandas as pd

from main import (
    build_year_ownership,
    compact_years,
    load_abbreviations,
    merge_test_year,
    parse_years,
    size_length_capacities,
)


# Dedicated patterns are intentionally not collapsed into a sibling's generic
# size merely because the fitment years overlap.
DEDICATED_SIZE_CAPACITIES = {
    "BEL-AIR-5357": 5080.0,
    "CHALLENGER": 5050.0,
    "MODEL-X": 5057.0,
}


def new_cluster_id(size: str, make: str, model: str) -> str:
    digest = hashlib.sha1(f"{size}|{make}|{model}".encode("utf-8")).hexdigest()[:10].upper()
    return f"CAR-{digest}"


def joined(values: pd.Series) -> str:
    return " / ".join(sorted({str(value).strip() for value in values if str(value).strip()}))


def sibling_size_merge_targets(
    summary: pd.DataFrame,
    detail: pd.DataFrame,
    capacities: dict[str, float],
    tolerance: float,
) -> dict[str, str]:
    """Merge same-model sibling clusters when source years overlap and one size fits all.

    An overlapping source year is strong evidence that two size clusters describe the
    same consumer link.  Prefer the smallest existing sibling size whose length limit,
    including the configured tolerance, covers every source row in the component.
    """
    cluster_years = {
        str(row["CLUSTER_ID"]): set(parse_years(row["YEAR_COMPACT"]))
        for _, row in summary.iterrows()
    }
    cluster_max_lengths = (
        detail.groupby("CLUSTER_ID")["L-MM"].max().dropna().astype(float).to_dict()
    )
    targets: dict[str, str] = {}

    for _, siblings in summary.groupby(["MAKE", "MODEL"], sort=False):
        ids = [str(value) for value in siblings["CLUSTER_ID"]]
        parent = {cid: cid for cid in ids}

        def find(cid: str) -> str:
            while parent[cid] != cid:
                parent[cid] = parent[parent[cid]]
                cid = parent[cid]
            return cid

        def union(left: str, right: str) -> None:
            left_root, right_root = find(left), find(right)
            if left_root != right_root:
                parent[right_root] = left_root

        for position, left in enumerate(ids):
            for right in ids[position + 1:]:
                if cluster_years.get(left, set()) & cluster_years.get(right, set()):
                    union(left, right)

        components: dict[str, list[str]] = {}
        for cid in ids:
            components.setdefault(find(cid), []).append(cid)

        sibling_sizes = siblings.set_index("CLUSTER_ID")["逻辑尺码"].astype(str).to_dict()
        for component in components.values():
            if len(component) < 2:
                continue
            if any(sibling_sizes[cid] in DEDICATED_SIZE_CAPACITIES for cid in component):
                continue
            max_length = max(cluster_max_lengths.get(cid, float("inf")) for cid in component)
            candidate_sizes = sorted(
                {sibling_sizes[cid] for cid in component},
                key=lambda size: (float(capacities.get(size, float("inf"))), size),
            )
            target = next(
                (size for size in candidate_sizes if max_length <= float(capacities.get(size, -float("inf"))) + tolerance),
                None,
            )
            if target is not None:
                targets.update({cid: target for cid in component})
    return targets


def build_atom_audit(detail: pd.DataFrame) -> pd.DataFrame:
    atoms: list[dict[str, object]] = []
    for _, row in detail.iterrows():
        trims = [value.strip() for value in str(row.get("TRIM", "")).split(",") if value.strip()] or [""]
        for trim in trims:
            for year in parse_years(row.get("YEAR", "")):
                atoms.append({
                    "品牌": row["MAKE"], "车型": row["MODEL"], "款型": trim, "版本": row.get("版本", ""),
                    "结构": row.get("结构", ""), "年份": year, "逻辑尺码": row["逻辑尺码"],
                    "聚类ID": row["CLUSTER_ID"], "源行号": row.get("SOURCE_ROW", ""),
                })
    atoms_frame = pd.DataFrame(atoms)
    keys = ["品牌", "车型", "款型", "版本", "结构", "年份"]
    audit = atoms_frame.groupby(keys, dropna=False).agg(
        逻辑尺码数量=("逻辑尺码", "nunique"), 聚类数量=("聚类ID", "nunique"),
        逻辑尺码=("逻辑尺码", joined), 聚类ID=("聚类ID", joined),
        源行号=("源行号", lambda values: ",".join(map(str, sorted(set(values))))),
    ).reset_index()
    audit["状态"] = "正常"
    audit.loc[audit["聚类数量"] > 1, "状态"] = "多聚类"
    audit.loc[audit["逻辑尺码数量"] > 1, "状态"] = "跨尺码冲突"
    return audit


def build_summary(
    detail: pd.DataFrame,
    audit: pd.DataFrame,
    consumer_years: dict[str, str],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (cid, size, make, model), group in detail.groupby(["CLUSTER_ID", "逻辑尺码", "MAKE", "MODEL"], sort=False):
        years = [year for value in group["YEAR"] for year in parse_years(value)]
        year_text = consumer_years.get(cid, compact_years(years))
        rows.append({
            "CLUSTER_ID": cid, "逻辑尺码": size,
            "链接名称": f"{make} {model} {year_text}".strip(), "MAKE": make, "MODEL": model,
            "YEAR_COMPACT": year_text,
            "YEAR_MIN": min(parse_years(year_text)), "YEAR_MAX": max(parse_years(year_text)),
            "ESTIMATED_SALES": group["销量合计"].sum(), "MERGE_STATUS": "ACCEPT",
        })
    summary = pd.DataFrame(rows).sort_values(
        ["逻辑尺码", "ESTIMATED_SALES", "MAKE", "MODEL"],
        ascending=[True, False, True, True],
    )
    summary.insert(summary.columns.get_loc("链接名称") + 1, "兄弟链接数量", 0)
    return summary


def build_sibling_detail(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, siblings in summary.groupby(["MAKE", "MODEL"], sort=False):
        if len(siblings) < 2:
            continue
        for index, row in siblings.iterrows():
            for _, sibling in siblings.drop(index=index).iterrows():
                rows.append({
                    "CLUSTER_ID": row["CLUSTER_ID"], "链接名称": row["链接名称"],
                    "兄弟CLUSTER_ID": sibling["CLUSTER_ID"], "兄弟链接名称": sibling["链接名称"],
                    "分开原因": f"同MAKE+MODEL、不同年份；逻辑尺码不同（{row['逻辑尺码']} / {sibling['逻辑尺码']}），已有原子事实不跨链接合并",
                })
            summary.at[index, "兄弟链接数量"] = len(siblings) - 1
    return pd.DataFrame(rows)


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="合并 W 型车尺码簇并生成新 Cluster ID")
    parser.add_argument("--cluster-dir", type=Path, default=repo / "D1.聚类SKU" / "output" / "W型车")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    summary = pd.read_csv(args.cluster_dir / "car_cluster_summary.csv", encoding="utf-8-sig")
    detail = pd.read_csv(args.cluster_dir / "car_cluster_detail.csv", encoding="utf-8-sig")
    for column in ["L-MM", "W-MM", "H-MM", "销量合计", "自动长度余量", "相差数值"]:
        detail[column] = pd.to_numeric(detail[column], errors="coerce")
    config = load_abbreviations(Path(__file__).resolve().parent / "config" / "sku_abbreviations.json")
    tolerance = float(config.get("year_merge_length_tolerance_mm", 0))
    ownership = build_year_ownership(detail)
    capacities = size_length_capacities(detail)
    capacities.update(DEDICATED_SIZE_CAPACITIES)
    sibling_targets = sibling_size_merge_targets(summary, detail, capacities, tolerance)

    tests: list[dict[str, object]] = []
    mappings: list[dict[str, object]] = []
    for _, row in summary.iterrows():
        test_row = pd.Series({
            "MAKE": row["MAKE"], "MODEL": row["MODEL"], "FITMENT_YEAR": row["YEAR_COMPACT"],
            "PHYSICAL_SIZE": row["逻辑尺码"],
        })
        result = merge_test_year(test_row, ownership, capacities, tolerance)
        final_size = sibling_targets.get(str(row["CLUSTER_ID"]), str(result["FINAL_SIZE"]))
        merge_status = str(result["YEAR_MERGE_STATUS"])
        if str(row["CLUSTER_ID"]) in sibling_targets:
            merge_status = "MERGED_SIBLING_SIZE_TOLERANCE"
        cid = new_cluster_id(final_size, str(row["MAKE"]), str(row["MODEL"]))
        tests.append({
            "原聚类ID": row["CLUSTER_ID"], "原逻辑尺码": row["逻辑尺码"], "品牌": row["MAKE"], "车型": row["MODEL"],
            "原始年份": result["SOURCE_YEAR"], "候选合并年份": result["CANDIDATE_YEAR"], "最终命名年份": result["CONSUMER_YEAR"],
            "建议最终尺码": final_size, "最大超出毫米": result["MAX_LENGTH_OVERFLOW"],
            "合并测试状态": merge_status, "尺码簇分析明细": result["SIZE_REVIEW_DETAIL"],
            "冲突明细": result["YEAR_CONFLICT_DETAIL"],
        })
        mappings.append({
            "原聚类ID": row["CLUSTER_ID"], "原逻辑尺码": row["逻辑尺码"], "品牌": row["MAKE"], "车型": row["MODEL"],
            "建议最终尺码": final_size, "新聚类ID": cid,
            "是否变更": "是" if cid != row["CLUSTER_ID"] else "否",
        })
    test_frame = pd.DataFrame(tests)
    mapping_frame = pd.DataFrame(mappings)
    size_map = mapping_frame.set_index("原聚类ID")["建议最终尺码"].to_dict()
    id_map = mapping_frame.set_index("原聚类ID")["新聚类ID"].to_dict()

    merged_detail = detail.copy()
    merged_detail["原聚类ID"] = merged_detail["CLUSTER_ID"]
    merged_detail["原逻辑尺码"] = merged_detail["逻辑尺码"]
    merged_detail["逻辑尺码"] = merged_detail["原聚类ID"].map(size_map)
    merged_detail["CLUSTER_ID"] = merged_detail["原聚类ID"].map(id_map)
    merged_detail["自动长度余量"] = merged_detail.apply(
        lambda row: capacities[row["逻辑尺码"]] - row["L-MM"] if pd.notna(row["L-MM"]) else pd.NA, axis=1
    )
    audit = build_atom_audit(merged_detail)
    if (audit["状态"] != "正常").any():
        raise ValueError("合并后仍存在原子事实跨尺码或多聚类冲突")
    consumer_years = {}
    for cid, group in test_frame.assign(
        新聚类ID=test_frame["原聚类ID"].map(id_map)
    ).groupby("新聚类ID"):
        years = [year for value in group["最终命名年份"] for year in parse_years(value)]
        consumer_years[cid] = compact_years(years)
    merged_summary = build_summary(merged_detail, audit, consumer_years)
    sibling_detail = build_sibling_detail(merged_summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    test_frame.to_csv(args.output_dir / "聚类合并测试.csv", index=False, encoding="utf-8-sig")
    mapping_frame.to_csv(args.output_dir / "新聚类ID映射.csv", index=False, encoding="utf-8-sig")
    merged_summary.to_csv(args.output_dir / "合并后聚类主表.csv", index=False, encoding="utf-8-sig")
    sibling_detail.to_csv(args.output_dir / "兄弟链接明细.csv", index=False, encoding="utf-8-sig")
    merged_detail.to_csv(args.output_dir / "合并后聚类明细.csv", index=False, encoding="utf-8-sig")

    if args.publish:
        merged_summary.to_csv(args.cluster_dir / "car_cluster_summary.csv", index=False, encoding="utf-8-sig")
        merged_detail.drop(columns=["原聚类ID", "原逻辑尺码"]).to_csv(
            args.cluster_dir / "car_cluster_detail.csv", index=False, encoding="utf-8-sig"
        )
        audit.to_csv(args.cluster_dir / "car_cluster_atom_audit.csv", index=False, encoding="utf-8-sig")
        shutil.copy2(args.output_dir / "聚类合并测试.csv", args.cluster_dir / "聚类合并测试.csv")
        shutil.copy2(args.output_dir / "新聚类ID映射.csv", args.cluster_dir / "新聚类ID映射.csv")
        shutil.copy2(args.output_dir / "兄弟链接明细.csv", args.cluster_dir / "兄弟链接明细.csv")
    print(f"原聚类={len(summary)} 合并后聚类={len(merged_summary)} ID变更={(mapping_frame['是否变更'] == '是').sum()} 发布={args.publish}")


if __name__ == "__main__":
    main()
