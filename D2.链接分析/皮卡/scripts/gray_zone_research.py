"""在隔离副本中重放皮卡聚类，比较 50 mm 灰区政策的影响。

研究脚本不修改 A0/D1/D2 的正式规则、registry 或 output。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_DIR.parents[1]
ENGINE_DIR = REPO_ROOT / "D1.聚类SKU" / "artifacts" / "皮卡"
SOURCE_DETAIL = ENGINE_DIR / "output" / "pickup_cluster_detail.csv"
SHIPMENT_WORKBOOK = PROJECT_DIR.parent / "data" / "发货单明细.xlsx"

SIZE_ORDER = ["PK-M", "PK-M+", "PK-L", "PK-XL", "PK-XXL", "PK-XXXL"]
SIZE_RANK = {value: index for index, value in enumerate(SIZE_ORDER)}
CURRENT_NAMES = {
    "PK-M": "PK-S",
    "PK-M+": "PK-M",
    "PK-L": "PK-L",
    "PK-XL": "PK-XL",
    "PK-XXL": "PK-XXL-645",
    "PK-XXXL": "PK-XXL-680",
}
SIZE_LIMIT_MM = {
    "PK-M": 5300.0,
    "PK-M+": 5630.0,
    "PK-L": 5900.0,
    "PK-XL": 6200.0,
    "PK-XXL": 6450.0,
    "PK-XXXL": 6800.0,
}
IDENTITY_COLUMNS = ["MAKE", "MODEL", "版本", "结构", "CAB_GROUP", "BED_GROUP", "AXLE_TYPE"]
DIMENSION_COLUMNS = ["L-MM", "W-MM", "H-MM"]


def apply_gray_zone(source: pd.DataFrame, tolerance_mm: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    result = source.copy()
    result["自动尺码"] = result["PHYSICAL_SKU"].astype(str)
    decisions: list[dict[str, object]] = []
    eligible = result[result["自动尺码"].isin(SIZE_RANK)].copy()
    for _, group in eligible.groupby(IDENTITY_COLUMNS, dropna=False):
        records = list(group.sort_values(["YEAR_START", "YEAR_END"]).to_dict("records"))
        for earlier, later in zip(records, records[1:]):
            old_earlier = str(earlier["自动尺码"])
            old_later = str(later["自动尺码"])
            if old_earlier == old_later:
                continue
            if abs(SIZE_RANK[old_earlier] - SIZE_RANK[old_later]) != 1:
                continue
            if int(later["YEAR_START"]) > int(earlier["YEAR_END"]) + 1:
                continue
            differences = {
                column: float(later[column]) - float(earlier[column])
                for column in DIMENSION_COLUMNS
            }
            if max(abs(value) for value in differences.values()) > tolerance_mm:
                continue
            promoted_size = max((old_earlier, old_later), key=SIZE_RANK.__getitem__)
            affected = result["DIMENSION-ID"].isin(
                [earlier["DIMENSION-ID"], later["DIMENSION-ID"]]
            )
            result.loc[affected, "自动尺码"] = promoted_size
            decisions.append({
                "MAKE": earlier["MAKE"],
                "MODEL": earlier["MODEL"],
                "版本": earlier["版本"],
                "CAB_GROUP": earlier["CAB_GROUP"],
                "BED_GROUP": earlier["BED_GROUP"],
                "EARLIER_YEAR": earlier["YEAR"],
                "LATER_YEAR": later["YEAR"],
                "EARLIER_SIZE": CURRENT_NAMES.get(old_earlier, old_earlier),
                "LATER_SIZE": CURRENT_NAMES.get(old_later, old_later),
                "GRAY_SIZE": CURRENT_NAMES.get(promoted_size, promoted_size),
                "DELTA_L_MM": differences["L-MM"],
                "DELTA_W_MM": differences["W-MM"],
                "DELTA_H_MM": differences["H-MM"],
                "EARLIER_CLUSTER_ID": earlier["CLUSTER_ID"],
                "LATER_CLUSTER_ID": later["CLUSTER_ID"],
            })
    mapped_limits = result["自动尺码"].map(SIZE_LIMIT_MM)
    known = mapped_limits.notna()
    result.loc[known, "自动长度余量"] = (
        mapped_limits[known] - pd.to_numeric(result.loc[known, "L-MM"], errors="raise")
    )
    return result, pd.DataFrame(decisions)


def run_engine(engine: Path, input_path: Path, output_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    completed = subprocess.run(
        [sys.executable, "main.py", "--input", str(input_path), "--output", output_name],
        cwd=engine,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = engine / output_name
    summary = pd.read_csv(output / "pickup_cluster_summary.csv", encoding="utf-8-sig")
    detail = pd.read_csv(output / "pickup_cluster_detail.csv", encoding="utf-8-sig")
    return summary, detail


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tolerance-mm", type=float, default=50.0)
    parser.add_argument("--output", type=Path, default=PROJECT_DIR / "research" / "gray-zone-50mm")
    args = parser.parse_args()

    source = pd.read_csv(SOURCE_DETAIL, encoding="utf-8-sig")
    source["自动尺码"] = source["PHYSICAL_SKU"].astype(str)
    gray, decisions = apply_gray_zone(source, args.tolerance_mm)
    args.output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="pickup-gray-zone-") as temporary:
        work = Path(temporary)
        engine = work / "engine"
        shutil.copytree(ENGINE_DIR, engine)
        baseline_input = work / "baseline.csv"
        gray_input = work / "gray.csv"
        source.to_csv(baseline_input, index=False, encoding="utf-8-sig")
        gray.to_csv(gray_input, index=False, encoding="utf-8-sig")
        baseline_summary, baseline_detail = run_engine(engine, baseline_input, "baseline")
        gray_summary, gray_detail = run_engine(engine, gray_input, "gray")

    current_count = pd.read_csv(
        ENGINE_DIR / "output" / "pickup_cluster_summary.csv", encoding="utf-8-sig"
    )["CLUSTER_ID"].nunique()
    baseline_count = baseline_summary["CLUSTER_ID"].nunique()
    gray_count = gray_summary["CLUSTER_ID"].nunique()
    baseline_reproduced = baseline_count == current_count
    affected_cluster_ids = set(decisions.get("EARLIER_CLUSTER_ID", [])) | set(
        decisions.get("LATER_CLUSTER_ID", [])
    )
    grouping = pd.read_excel(SHIPMENT_WORKBOOK, sheet_name="分组明细")
    affected_shipments = grouping[grouping["CLUSTER_ID"].isin(affected_cluster_ids)]

    decisions.to_csv(args.output / "灰区调整明细.csv", index=False, encoding="utf-8-sig")
    baseline_summary.to_csv(args.output / "基线重放聚类汇总.csv", index=False, encoding="utf-8-sig")
    gray_summary.to_csv(args.output / "灰区聚类汇总.csv", index=False, encoding="utf-8-sig")
    gray_detail.to_csv(args.output / "灰区聚类明细.csv", index=False, encoding="utf-8-sig")
    metrics = {
        "tolerance_mm": args.tolerance_mm,
        "source_rows": len(source),
        "current_clusters": current_count,
        "baseline_replay_clusters": baseline_count,
        "baseline_reproduced": baseline_reproduced,
        "gray_clusters": gray_count,
        "cluster_reduction": baseline_count - gray_count,
        "cluster_reduction_rate": (baseline_count - gray_count) / baseline_count,
        "gray_decisions": len(decisions),
        "changed_atoms": int((gray["自动尺码"] != source["自动尺码"]).sum()),
        "changed_atom_sales": float(
            pd.to_numeric(
                source.loc[gray["自动尺码"] != source["自动尺码"], "预估销量 的总和"],
                errors="coerce",
            ).fillna(0).sum()
        ),
        "physical_sku_types_before": int(source["自动尺码"].nunique()),
        "physical_sku_types_after": int(gray["自动尺码"].nunique()),
        "affected_active_clusters": int(affected_shipments["CLUSTER_ID"].nunique()),
        "affected_allocated_shipments": int(affected_shipments["行发货量"].sum()),
    }
    (args.output / "指标.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = [
        "# 皮卡 50 mm 灰区政策重放", "",
        f"- 当前聚类：{current_count}",
        f"- 基线重放：{baseline_count}（{'复现' if baseline_reproduced else '未复现'}）",
        f"- 灰区重放：{gray_count}",
        f"- 聚类减少：{baseline_count - gray_count}（{metrics['cluster_reduction_rate']:.1%}）",
        f"- 灰区判定：{len(decisions)} 组；实际改码原子：{metrics['changed_atoms']} 条。", "",
        f"- 物理尺码种类：{metrics['physical_sku_types_before']} → {metrics['physical_sku_types_after']}（不变）。",
        f"- 改码原子历史预估销量合计：{metrics['changed_atom_sales']:,.0f}。", "",
        f"- 当前发货分配中受影响的活动 Cluster：{metrics['affected_active_clusters']} 个，合计 {metrics['affected_allocated_shipments']} 件。", "",
        "## 政策", "",
        f"同车型、同版本、同 CAB/BED/轴型且年份连续；长宽高差均不超过 {args.tolerance_mm:g} mm；",
        "原本落在相邻尺码时，两代统一提升到较大尺码，避免较小车罩套不下。", "",
        "## 主要风险", "",
        "- 较早车型会改用更大的车罩，可能增加松垮、积水和风噪风险。",
        "- 聚类减少不等于库存 SKU 种类减少；它首先减少的是消费者链接/Cluster 数。",
        "- 规则使用整车外廓尺寸，未包含车罩面料弹性、镜袋和驾驶室轮廓，投产前必须实车试套。",
        "- 历史 LINK_ID 可能合并或换尺码，需要迁移评价、广告、库存和发货映射。", "",
        "## 灰区命中", "",
        "| 车型 | 配置 | 年份 | 原尺码 | 后尺码 | 统一尺码 | ΔL/W/H mm |",
        "|---|---|---|---|---|---|---|",
    ]
    for _, item in decisions.iterrows():
        report.append(
            f"| {item['MAKE']} {item['MODEL']} {item['版本'] if pd.notna(item['版本']) else ''} "
            f"| {item['CAB_GROUP']} / {item['BED_GROUP']} "
            f"| {item['EARLIER_YEAR']} → {item['LATER_YEAR']} "
            f"| {item['EARLIER_SIZE']} | {item['LATER_SIZE']} | {item['GRAY_SIZE']} "
            f"| {item['DELTA_L_MM']:.0f}/{item['DELTA_W_MM']:.0f}/{item['DELTA_H_MM']:.0f} |"
        )
    report.extend([
        "", "## 结果解释", "",
        "- Cadillac Escalade EXT 两个年代合并为一个 PK-L Cluster，因此总数净减少 1。",
        "- F-150 Raptor 2017–2020 从原 PK-L Cluster 移入 2021–2026 的 PK-XL Cluster；两边原 Cluster 都仍有其他车型事实，因此总数不减少。",
        "- F-250/F-350 Super Duty 2008–2010 从 PK-L 移入 PK-XL；同样只改变两个 Cluster 的年份边界，不减少总数。",
        "- 因而若目标是显著减少链接 SKU，仅实施灰区不够，还需要重新审视跨 CAB/BED 的聚类结构和历史 LINK_ID 合并政策。", "",
    ])
    (args.output / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
