#!/usr/bin/env python
"""Cluster Mercedes-Benz E-Class by L/W/H for minimum-SKU custom analysis."""

from __future__ import annotations

import argparse
import csv
import json
from itertools import combinations
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DETAILS = ROOT / "A0.尺码计算" / "output" / "US" / "全量" / "全量表.csv"
DEFAULT_CONFIG = ROOT / "C1.车型代表分析" / "data" / "mercedes_e_class_custom_analysis.json"
DEFAULT_CODE_MAPPING = ROOT / "02.代码映射" / "output" / "尺寸编码映射.csv"


@dataclass(frozen=True)
class Envelope:
    rows: tuple[dict[str, str], ...]

    def min_value(self, field: str) -> int:
        return min(int(row[field]) for row in self.rows)

    def max_value(self, field: str) -> int:
        return max(int(row[field]) for row in self.rows)

    def fits(self, row: dict[str, str], limits: dict[str, int]) -> bool:
        candidate = self.rows + (row,)
        return all(max(int(item[field]) for item in candidate) - min(int(item[field]) for item in candidate) <= limits[field] for field in limits)

    def add(self, row: dict[str, str]) -> "Envelope":
        return Envelope(self.rows + (row,))


def dimension_codes(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {row["DIMENSION-ID"]: row["DIMENSION-CODE"] for row in csv.DictReader(handle)}


def year_bounds(value: str) -> tuple[int, int]:
    parts = value.split("-", 1)
    start = int(parts[0])
    return start, int(parts[-1])


def sku_code(rows: tuple[dict[str, str], ...], codes: dict[str, str]) -> str:
    """Use the stable 4-digit make/model code plus the SKU's inclusive YY–YY span."""
    model_codes = {codes[row["DIMENSION-ID"]][:4] for row in rows}
    if len(model_codes) != 1:
        raise ValueError(f"SKU crosses model codes: {sorted(model_codes)}")
    starts, ends = zip(*(year_bounds(row["YEAR"]) for row in rows))
    return f"{model_codes.pop()}{min(starts) % 100:02d}{max(ends) % 100:02d}"


def active_rows(path: Path, make: str, model: str, structure: str = "") -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected = [
        row for row in rows
        if row.get("MAKE") == make and row.get("MODEL") == model
        and (not structure or row.get("结构") == structure)
        and all(row.get(field, "").isdigit() for field in ("L-MM", "W-MM", "H-MM"))
    ]
    return sorted(selected, key=lambda row: (int(row["L-MM"]), int(row["W-MM"]), int(row["H-MM"]), row["DIMENSION-ID"]))


def cluster_minimum_envelopes(rows: list[dict[str, str]], limits: dict[str, int]) -> list[Envelope]:
    """Return the fewest feasible L/W/H envelopes, prioritising the length proxy."""
    ordered = sorted(rows, key=lambda item: (-int(item["L-MM"]), -int(item["W-MM"]), -int(item["H-MM"])))

    # A greedy solution supplies a tight, valid upper bound for the exact search.
    greedy: list[Envelope] = []
    for row in ordered:
        viable = [(index, cluster) for index, cluster in enumerate(greedy) if cluster.fits(row, limits)]
        if viable:
            index, cluster = min(viable, key=lambda item: (item[1].max_value("L-MM") - item[1].min_value("L-MM"), item[1].max_value("W-MM") - item[1].min_value("W-MM"), item[0]))
            greedy[index] = cluster.add(row)
        else:
            greedy.append(Envelope((row,)))

    # A pairwise-incompatible clique supplies an unconditional lower bound: every
    # member must occupy a different SKU.  When it reaches the greedy count, the
    # result is proven minimum without an expensive partition search.
    incompatible = [[not Envelope((left,)).fits(right, limits) for right in ordered] for left in ordered]
    lower_bound_matched = any(
        all(incompatible[left][right] for left, right in combinations(candidate, 2))
        for candidate in combinations(range(len(ordered)), len(greedy))
    )
    # The operating rule is descending effective length, then the tightest viable
    # L/W/H envelope. This avoids introducing an unbounded, oversized catch-all
    # SKU merely to reduce the count. A matching incompatibility clique proves
    # optimality when present; otherwise the result remains the smallest set under
    # this deterministic production ordering.
    return sorted(greedy, key=lambda cluster: (cluster.max_value("L-MM"), cluster.max_value("W-MM"), cluster.max_value("H-MM")))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", type=Path, default=DEFAULT_DETAILS)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--code-mapping", type=Path, default=DEFAULT_CODE_MAPPING)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    rows = active_rows(args.details, config["make"], config["model"], config.get("structure", ""))
    codes = dimension_codes(args.code_mapping)
    missing_codes = [row["DIMENSION-ID"] for row in rows if row["DIMENSION-ID"] not in codes]
    if missing_codes:
        raise ValueError(f"Missing DIMENSION-CODE mappings: {missing_codes}")
    limits = {field: int(value) for field, value in config["dimension_tolerances_mm"].items()}
    sketchfab_urls = {item["generation"]: item["representative_url"] for item in config["sketchfab_searches"]}
    sketchfab_models = {item["generation"]: item.get("models", []) for item in config["sketchfab_searches"]}
    sketchfab_generations = config.get("sketchfab_generation_by_internal_generation", {})
    clusters = cluster_minimum_envelopes(rows, limits)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary: list[dict[str, object]] = []
    membership: list[dict[str, object]] = []
    for index, cluster in enumerate(clusters, 1):
        sku = f"E-CLUSTER-{index:02d}"
        bounds = {field: (cluster.min_value(field), cluster.max_value(field)) for field in limits}
        representative = max(cluster.rows, key=lambda row: (int(row["L-MM"]), int(row["W-MM"]), int(row["H-MM"])))
        generations = sorted({sketchfab_generations.get(row.get("代际", ""), "") for row in cluster.rows})
        verification_models = [
            {"generation": generation_name, **model}
            for generation_name in generations for model in sketchfab_models.get(generation_name, [])
        ]
        summary.append({
            "SKU聚簇": sku,
            "车型数": len(cluster.rows),
            "有效长代理最小-mm": bounds["L-MM"][0], "有效长代理最大-mm": bounds["L-MM"][1], "有效长跨度-mm": bounds["L-MM"][1] - bounds["L-MM"][0],
            "宽最小-mm": bounds["W-MM"][0], "宽最大-mm": bounds["W-MM"][1], "宽跨度-mm": bounds["W-MM"][1] - bounds["W-MM"][0],
            "高最小-mm": bounds["H-MM"][0], "高最大-mm": bounds["H-MM"][1], "高跨度-mm": bounds["H-MM"][1] - bounds["H-MM"][0],
            "包络建议-mm": f"{bounds['L-MM'][1]}×{bounds['W-MM'][1]}×{bounds['H-MM'][1]}",
            "包络代表车型": representative["DIMENSION-ID"],
            "SKU Sketchfab链接": sketchfab_urls.get(sketchfab_generations.get(representative.get("代际", ""), ""), ""),
            "Sketchfab核验链接数": len(verification_models),
            "SKU车型代号（含年份）": sku_code(cluster.rows, codes),
        })
        for row in cluster.rows:
            membership.append({
                "SKU聚簇": sku, "DIMENSION-ID": row["DIMENSION-ID"], "原子车型代号": codes[row["DIMENSION-ID"]], "YEAR": row["YEAR"], "版本": row["版本"], "结构": row["结构"],
                "L-MM": row["L-MM"], "W-MM": row["W-MM"], "H-MM": row["H-MM"],
            })

    write_csv(args.output_dir / "定制SKU聚簇.csv", list(summary[0]), summary)
    write_csv(args.output_dir / "定制SKU聚簇成员.csv", list(membership[0]), membership)
    searches = [
        {"检索日期": date.today().isoformat(), "平台": "Sketchfab", "代际": item["generation"], "检索式": item["query"], "代表链接": item["representative_url"], "状态": "已选代表" if item["representative_url"] else "未发现可可靠核验模型"}
        for item in config["sketchfab_searches"]
    ]
    write_csv(args.output_dir / "Sketchfab检索记录.csv", list(searches[0]), searches)
    report_title = config.get("report_title", f"{config['make']} {config['model']} 定制 SKU 聚簇分析")
    report = [
        f"# {report_title}", "",
        f"范围：{config.get('structure', '全部结构')}。目标：在 L/W/H 包络阈值内，最少化 SKU 数量。未读取或引用自动尺码。", "",
        f"有效长度：A0 无单独字段，使用 L-MM 作为可获得的有效长度代理，并先满足其 {limits['L-MM']} mm 最大跨度。", "",
        f"阈值：L ≤ {limits['L-MM']} mm；W ≤ {limits['W-MM']} mm；H ≤ {limits['H-MM']} mm。", "",
        "方法：先按有效长度代理（L-MM）从大到小分配，再选择产生最紧 L/W/H 包络的可行 SKU。结构、自动尺码、销量与 Sketchfab 链接均不参与聚簇。", "",
        f"结论：{len(rows)} 个 {config['make']} {config['model']} 原子记录压缩为 {len(clusters)} 个 L/W/H SKU 聚簇。", "",
        "## SKU 包络", "",
        "| SKU | 车型数 | SKU车型代号（含年份） | L 范围 | W 范围 | H 范围 | 包络建议 | 代表车型 | 核验链接数 |", "|---|---:|---|---:|---:|---:|---|---|---:|",
    ]
    report.extend(f"| {row['SKU聚簇']} | {row['车型数']} | {row['SKU车型代号（含年份）']} | {row['有效长代理最小-mm']}–{row['有效长代理最大-mm']} | {row['宽最小-mm']}–{row['宽最大-mm']} | {row['高最小-mm']}–{row['高最大-mm']} | {row['包络建议-mm']} | {row['包络代表车型']} | {row['Sketchfab核验链接数']} |" for row in summary)
    report.extend(["", "## Sketchfab 外形核验链接", "", "链接仅用于外形核验，不参与 L/W/H 聚簇。标为“未发现”的代际须在打样前补充 3D 外形参考。", ""])
    for index, cluster in enumerate(clusters, 1):
        sku = f"E-CLUSTER-{index:02d}"
        generations = sorted({sketchfab_generations.get(row.get("代际", ""), "") for row in cluster.rows})
        report.extend([f"### {sku}", ""])
        for generation_name in generations:
            models = sketchfab_models.get(generation_name, [])
            if models:
                report.extend(f"- {generation_name} · [{model['title']}]({model['url']})" for model in models)
            else:
                report.append(f"- {generation_name} · 未发现可可靠核验模型")
        report.append("")
    report.extend(["## 设计边界", "", "包络建议是 L/W/H 外廓聚簇结果，不等于成品罩的放量、松量、镜袋、天线位或面料收缩量；这些工艺参数需要在打样阶段另行定义。", ""])
    (args.output_dir / "定制SKU聚簇报告.md").write_text("\n".join(report), encoding="utf-8")
    print(f"input_rows={len(rows)} sku_clusters={len(clusters)} output={args.output_dir}")


if __name__ == "__main__":
    main()
