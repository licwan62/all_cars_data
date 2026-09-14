"""Build versioned link-analysis artifacts from MAKE-level W-car clusters."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path


TOTAL_SUPPLY = 801
MULTIPLE = 3
HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[4]
CLUSTER_ARTIFACT = REPO / "聚类SKU" / "artifacts" / "W型车" / "0914.2-make聚合"
MAKE_ABBREVIATIONS = {
    "Acura": "ACURA", "BMW": "BMW", "Buick": "BUICK", "Cadillac": "CADI",
    "Chevrolet": "CHEV", "Dodge": "DODGE", "Ford": "FORD", "Hyundai": "HYUNDAI",
    "Jaguar": "JAG", "Lexus": "LEXUS", "Lincoln": "LINC", "Mercedes-Benz": "MB",
    "Mercury": "MERC", "Oldsmobile": "OLDS", "Plymouth": "PLYM", "Pontiac": "PONT",
    "Volvo": "VOLVO",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def years(value: str) -> list[int]:
    found = [int(item) for item in re.findall(r"\d{4}", value)]
    if not found:
        return []
    return list(range(found[0], found[-1] + 1))


def compact_years(values: list[str]) -> str:
    ordered = sorted({year for value in values for year in years(value)})
    spans: list[str] = []
    start = end = ordered[0]
    for year in ordered[1:]:
        if year == end + 1:
            end = year
        else:
            spans.append(str(start) if start == end else f"{start}-{end}")
            start = end = year
    spans.append(str(start) if start == end else f"{start}-{end}")
    return "/".join(spans)


def concentration(rows: list[dict[str, str]]) -> float:
    weighted_cv = 0.0
    for column, weight in (("L-MM", 0.60), ("W-MM", 0.25), ("H-MM", 0.15)):
        values = [float(row[column]) for row in rows if row[column]]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        weighted_cv += weight * math.sqrt(variance) / mean
    return round(100 * math.exp(-10 * weighted_cv), 1)


def allocate(summary: list[dict[str, str]]) -> dict[str, int]:
    units = TOTAL_SUPPLY // MULTIPLE
    total_sales = sum(int(row["预估销量"]) for row in summary)
    quotas = []
    for row in summary:
        numerator = int(row["预估销量"]) * units
        base, remainder = divmod(numerator, total_sales)
        quotas.append([row["MAKE_CLUSTER_ID"], base, remainder])
    remaining = units - sum(item[1] for item in quotas)
    for item in sorted(quotas, key=lambda value: (-value[2], value[0]))[:remaining]:
        item[1] += 1
    return {item[0]: item[1] * MULTIPLE for item in quotas}


def main() -> None:
    summary = read_csv(CLUSTER_ARTIFACT / "make_cluster_summary.csv")
    detail = read_csv(CLUSTER_ARTIFACT / "make_cluster_detail.csv")
    allocations = allocate(summary)
    groups: dict[str, list[dict[str, str]]] = {}
    for row in detail:
        groups.setdefault(row["MAKE_CLUSTER_ID"], []).append(row)
    total_sales = sum(int(row["预估销量"]) for row in summary)

    master: list[dict[str, object]] = []
    publish: list[dict[str, object]] = []
    for row in summary:
        cid, make, size = row["MAKE_CLUSTER_ID"], row["MAKE"], row["逻辑尺码"]
        records = groups[cid]
        fitment_years = compact_years([record["YEAR"] for record in records])
        boundary_years = [int(value) for value in re.findall(r"\d{4}", fitment_years)]
        year_span = str(min(boundary_years)) if min(boundary_years) == max(boundary_years) else f"{min(boundary_years)}-{max(boundary_years)}"
        models = sorted({record["MODEL"] for record in records})
        fitments = [f"{make} {model}" for model in models]
        shipped = allocations[cid]
        sales = int(row["预估销量"])
        dimensions = {
            "车长最小毫米": min(float(record["L-MM"]) for record in records),
            "车长最大毫米": max(float(record["L-MM"]) for record in records),
            "车宽最小毫米": min(float(record["W-MM"]) for record in records),
            "车宽最大毫米": max(float(record["W-MM"]) for record in records),
            "车高最小毫米": min(float(record["H-MM"]) for record in records),
            "车高最大毫米": max(float(record["H-MM"]) for record in records),
        }
        dimensions = {key: int(value) if value.is_integer() else value for key, value in dimensions.items()}
        master_row = {
            "MAKE_CLUSTER_ID": cid, "逻辑尺码": size, "品牌": make,
            "车型数量": len(models), "车型": " / ".join(models), "适配年份": fitment_years,
            "适配记录数": len(records), "预估销量": sales,
            "销量占比": f"{sales / total_sales:.6%}", "理论发货量": f"{sales * TOTAL_SUPPLY / total_sales:.6f}",
            "发货数量": shipped, **dimensions, "尺寸集中度": concentration(records),
        }
        master.append(master_row)
        if shipped:
            token = (
                f"Y{str(min(boundary_years))[-2:]}"
                if min(boundary_years) == max(boundary_years)
                else f"Y{str(min(boundary_years))[-2:]}-{str(max(boundary_years))[-2:]}"
            )
            publish.append({
                "SKU_NAME": f"{MAKE_ABBREVIATIONS.get(make, make.upper())}_MULTI_{token}_{size}",
                "MAKE_CLUSTER_ID": cid, "链接名称": f"{make} Multi-Model {year_span}",
                "尺码": size, "预估销量": sales, "销量占比": master_row["销量占比"],
                "发货数量": shipped, "适配车型": " / ".join(fitments), "适配年份": fitment_years,
                "适配记录数": len(records), **dimensions, "尺寸集中度": master_row["尺寸集中度"],
            })

    master_columns = list(master[0])
    publish_columns = list(publish[0])
    write_csv(HERE / "02_聚类数据" / "MAKE聚类主表.csv", master_columns, master)
    write_csv(HERE / "02_聚类数据" / "MAKE聚类原子明细.csv", list(detail[0]), detail)
    write_csv(HERE / "05_输出" / "链接发货适配表.csv", publish_columns, publish)

    size_rows: list[dict[str, object]] = []
    for size in dict.fromkeys(row["逻辑尺码"] for row in summary):
        selected = [row for row in master if row["逻辑尺码"] == size]
        sales = sum(int(row["预估销量"]) for row in selected)
        shipped = sum(int(row["发货数量"]) for row in selected)
        size_rows.append({
            "最终发货尺码": size, "聚类数量": len(selected), "预估销量": sales,
            "销量占比": f"{sales / total_sales:.6%}", "发货数量": shipped,
            "发货占比": f"{shipped / TOTAL_SUPPLY:.6%}",
        })
    size_rows.append({
        "最终发货尺码": "合计", "聚类数量": len(master), "预估销量": total_sales,
        "销量占比": "100.000000%", "发货数量": TOTAL_SUPPLY, "发货占比": "100.000000%",
    })
    size_columns = list(size_rows[0])
    write_csv(HERE / "01_发货方案" / "尺码发货汇总.csv", size_columns, size_rows)
    write_csv(HERE / "05_输出" / "尺码发货汇总.csv", size_columns, size_rows)

    report = [
        "# W 型车 MAKE 聚合链接分析", "",
        f"- 聚类口径：逻辑尺码 + MAKE",
        f"- 聚类数：{len(master)}",
        f"- 发布链接数：{len(publish)}",
        f"- 预估销量：{total_sales:,}",
        f"- 发货总量：{sum(int(row['发货数量']) for row in publish):,}",
        "- 分配方法：按聚类销量使用最大余数法分配，最小单位 3 件。", "",
        "该结果是 MAKE 跨 MODEL 聚合实验，不覆盖正式发布目录。", "",
    ]
    (HERE / "report.md").write_text("\n".join(report), encoding="utf-8-sig")
    print(f"clusters={len(master)} published={len(publish)} shipment={sum(int(row['发货数量']) for row in publish)}")


if __name__ == "__main__":
    main()
