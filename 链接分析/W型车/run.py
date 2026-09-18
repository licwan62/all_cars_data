"""Regenerate the W-car cluster candidate and its independent link analysis."""

from __future__ import annotations

import argparse
import csv
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path


TOTAL_SUPPLY = 801
SHIPMENT_MULTIPLE = 3


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def normalize_csv_columns(path: Path, *, rename: dict[str, str] | None = None, drop: set[str] | None = None) -> None:
    """Apply presentation-only column cleanup to an exported CSV."""
    rename = rename or {}
    drop = drop or set()
    rows = read_csv(path)
    if not rows:
        return
    columns = [rename.get(column, column) for column in rows[0] if column not in drop]
    normalized = [
        {rename.get(column, column): value for column, value in row.items() if column not in drop}
        for row in rows
    ]
    write_csv(path, columns, normalized)


def compact_years(values: list[str]) -> str:
    expanded: set[int] = set()
    for value in values:
        for part in str(value).split("/"):
            years_in_part = [int(year) for year in re.findall(r"\d{4}", part)]
            if len(years_in_part) == 1:
                expanded.add(years_in_part[0])
            elif len(years_in_part) >= 2:
                expanded.update(range(years_in_part[0], years_in_part[-1] + 1))
    years = sorted(expanded)
    ranges: list[str] = []
    start = end = years[0]
    for year in years[1:]:
        if year == end + 1:
            end = year
            continue
        ranges.append(str(start) if start == end else f"{start}-{end}")
        start = end = year
    ranges.append(str(start) if start == end else f"{start}-{end}")
    return "/".join(ranges)


def sku_year_code(year_text: str) -> str:
    """Encode the already-approved fitment years for a SKU name."""
    parts: list[str] = []
    for part in year_text.split("/"):
        match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", part)
        if not match:
            raise ValueError(f"SKU 年份无法编码：{year_text}")
        start, end = match.group(1)[-2:], match.group(2)
        parts.append(start if end is None else f"{start}-{end[-2:]}")
    return "Y" + "+".join(parts)


def expanded_year_span(year_text: str) -> str:
    """Use the first and last actual year for concise public naming."""
    values = [int(year) for year in re.findall(r"\d{4}", year_text)]
    if not values:
        raise ValueError(f"年份无法扩张：{year_text}")
    return str(min(values)) if min(values) == max(values) else f"{min(values)}-{max(values)}"


def expanded_sku_name(sku_name: str, year_span: str) -> str:
    """Replace a segmented SKU year token with the concise boundary span."""
    prefix, _, physical_size = sku_name.rpartition("_")
    name_prefix, separator, old_year_token = prefix.rpartition("_")
    if not separator or not old_year_token.startswith("Y"):
        raise ValueError(f"SKU_NAME 格式无法更新年份：{sku_name}")
    return f"{name_prefix}_{sku_year_code(year_span)}_{physical_size}"


def format_dimension(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:g}"


def dimension_summary(rows: list[dict[str, str]], column: str) -> tuple[str, str, float]:
    values = [float(row[column]) for row in rows if row[column]]
    return format_dimension(min(values)), format_dimension(max(values)), max(values) - min(values)


def dimension_concentration(rows: list[dict[str, str]]) -> float:
    """Return a 0-100 weighted concentration score for L/W/H dimensions.

    The score uses population coefficient of variation so dimensions with
    different units/scales remain comparable. Length carries the largest
    weight: L=60%, W=25%, H=15%. An exponential transform keeps the score
    bounded and makes 100 mean that all recorded dimensions are identical.
    """
    weighted_cv = 0.0
    for column, weight in (("L-MM", 0.60), ("W-MM", 0.25), ("H-MM", 0.15)):
        values = [float(row[column]) for row in rows if row[column]]
        if not values:
            continue
        mean = sum(values) / len(values)
        if mean <= 0:
            continue
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        weighted_cv += weight * math.sqrt(variance) / mean
    return round(100 * math.exp(-10 * weighted_cv), 1)


def format_fitment(row: dict[str, str]) -> str:
    parts: list[str] = []
    for value in (row["MAKE"], row["MODEL"], row["TRIM"], row["版本"]):
        value = value.strip()
        if value and value.casefold() not in {part.casefold() for part in parts}:
            parts.append(value)
    return " ".join(parts)


def allocate_shipments(rows: list[dict[str, str]], total_supply: int, sales_multipliers: dict[str, float] | None = None) -> list[dict[str, object]]:
    """Allocate fixed 3-piece shipment units with the largest-remainder method."""
    sales_multipliers = sales_multipliers or {}
    if total_supply % SHIPMENT_MULTIPLE:
        raise ValueError(f"总供给必须是 {SHIPMENT_MULTIPLE} 的倍数：{total_supply}")
    shipment_units = total_supply // SHIPMENT_MULTIPLE
    total_sales = sum(int(row["ESTIMATED_SALES"]) * sales_multipliers.get(row["逻辑尺码"], 1.0) for row in rows)
    allocated: list[dict[str, object]] = []
    for row in rows:
        sales = int(row["ESTIMATED_SALES"])
        multiplier = sales_multipliers.get(row["逻辑尺码"], 1.0)
        weighted_sales = sales * multiplier
        numerator = weighted_sales * shipment_units
        base = math.floor(numerator / total_sales)
        remainder = numerator - base * total_sales
        allocated.append({"source": row, "sales": sales, "multiplier": multiplier, "weighted_sales": weighted_sales, "base": base, "remainder": remainder})

    remaining = shipment_units - sum(int(item["base"]) for item in allocated)
    for item in sorted(allocated, key=lambda value: (-int(value["remainder"]), value["source"]["CLUSTER_ID"]))[:remaining]:
        item["base"] = int(item["base"]) + 1
    for item in allocated:
        item["shipment"] = int(item["base"]) * SHIPMENT_MULTIPLE
    return allocated


def build_shipment_outputs(output: Path, total_supply: int = TOTAL_SUPPLY, sales_multipliers: dict[str, float] | None = None) -> None:
    """Create the decision-ready master table, size summary, and report."""
    raw_master = output / "合并后聚类主表.csv"
    sales_multipliers = sales_multipliers or {}
    allocations = allocate_shipments(read_csv(raw_master), total_supply, sales_multipliers)
    master_rows: list[dict[str, object]] = []
    shipment_rows: list[dict[str, object]] = []
    full_shipment_rows: list[dict[str, object]] = []
    total_sales = sum(int(item["sales"]) for item in allocations)
    total_weighted_sales = sum(float(item["weighted_sales"]) for item in allocations)

    for item in allocations:
        source = item["source"]
        size = source["逻辑尺码"]
        sales = int(item["sales"])
        multiplier = float(item["multiplier"])
        weighted_sales = float(item["weighted_sales"])
        shipped = int(item["shipment"])
        master_rows.append({
            "聚类ID": source["CLUSTER_ID"], "逻辑尺码": size, "链接名称": source["链接名称"],
            "兄弟链接数量": source["兄弟链接数量"], "品牌": source["MAKE"], "车型": source["MODEL"],
            "年份汇总": source["YEAR_COMPACT"], "最早年份": source["YEAR_MIN"], "最晚年份": source["YEAR_MAX"],
            "预估销量": sales, "销量倍率": multiplier, "加权销量": weighted_sales,
            "聚类状态": "通过" if source["MERGE_STATUS"] == "ACCEPT" else source["MERGE_STATUS"],
        })
        theoretical = weighted_sales * total_supply / total_weighted_sales
        allocation_row = {
            "聚类ID": source["CLUSTER_ID"], "发货逻辑尺码": size,
            "链接名称": source["链接名称"], "预估销量": sales, "销量倍率": multiplier, "加权销量": weighted_sales,
            "全局销量占比": f"{weighted_sales / total_weighted_sales:.6%}",
            "理论发货量": f"{theoretical:.6f}", "发货数量": shipped,
            "取整补量": shipped - (int(theoretical / SHIPMENT_MULTIPLE) * SHIPMENT_MULTIPLE),
        }
        full_shipment_rows.append({**allocation_row, "是否发货": "是" if shipped else "否"})
        if shipped > 0:
            shipment_rows.append(allocation_row)

    # Remove only folders created by this workflow before recreating the
    # final deliverables and their supporting analysis files.
    for folder in ("00_输入", "01_发货方案", "02_聚类数据", "03_分析明细", "04_校验报告", "05_输出"):
        target = output / folder
        if target.exists():
            shutil.rmtree(target)

    master_dir = output / "02_聚类数据"
    shipment_dir = output / "01_发货方案"
    publish_dir = output / "05_输出"
    master_dir.mkdir(parents=True, exist_ok=True)
    shipment_dir.mkdir(parents=True, exist_ok=True)
    publish_dir.mkdir(parents=True, exist_ok=True)
    master_columns = [
        "聚类ID", "逻辑尺码", "链接名称", "兄弟链接数量", "品牌", "车型", "年份汇总", "最早年份", "最晚年份",
        "预估销量", "销量倍率", "加权销量", "聚类状态",
    ]
    shipment_columns = [
        "聚类ID", "发货逻辑尺码", "链接名称", "预估销量", "销量倍率", "加权销量", "全局销量占比",
        "理论发货量", "发货数量", "取整补量",
    ]
    detail_by_cluster = read_csv(output / "合并后聚类明细.csv")
    listing_rows = read_csv(output / "listing_detail.csv")
    listing_by_link = {row["消费者名称"]: row for row in listing_rows}
    publish_columns = [
        "SKU_NAME", "CLUSTER_ID", "链接名称", "尺码", "预估销量", "销量倍率", "加权销量", "销量占比", "发货数量", "适配车型", "适配年份", "适配记录数",
        "车长最小毫米", "车长最大毫米", "车宽最小毫米", "车宽最大毫米", "车高最小毫米", "车高最大毫米",
        "尺寸集中度",
    ]
    detail_groups: dict[str, list[dict[str, str]]] = {}
    for row in detail_by_cluster:
        detail_groups.setdefault(row["CLUSTER_ID"], []).append(row)

    dimension_columns = [
        "车长最小毫米", "车长最大毫米", "车宽最小毫米", "车宽最大毫米", "车高最小毫米", "车高最大毫米", "尺寸集中度",
    ]

    def with_dimensions(row: dict[str, object]) -> dict[str, object]:
        records = detail_groups.get(str(row["聚类ID"]), [])
        if not records:
            raise ValueError(f"分析明细缺少尺寸记录：{row['聚类ID']}")
        length_min, length_max, _ = dimension_summary(records, "L-MM")
        width_min, width_max, _ = dimension_summary(records, "W-MM")
        height_min, height_max, _ = dimension_summary(records, "H-MM")
        return {
            **row,
            "车长最小毫米": length_min, "车长最大毫米": length_max,
            "车宽最小毫米": width_min, "车宽最大毫米": width_max,
            "车高最小毫米": height_min, "车高最大毫米": height_max,
            "尺寸集中度": dimension_concentration(records),
        }

    enriched_full_shipment_rows = [with_dimensions(row) for row in full_shipment_rows]
    publish_rows: list[dict[str, object]] = []
    for shipment in shipment_rows:
        listing = listing_by_link.get(shipment["链接名称"])
        if listing is None:
            raise ValueError(f"链接名称缺少 SKU_NAME：{shipment['链接名称']}")
        records = detail_groups[shipment["聚类ID"]]
        fitment_years = compact_years([row["YEAR"] for row in records])
        naming_span = expanded_year_span(fitment_years)
        sku_name = expanded_sku_name(listing["SKU名称"], naming_span)
        expected_year_token = sku_year_code(naming_span)
        expected_suffix = f"_{expected_year_token}_{shipment['发货逻辑尺码']}"
        if not sku_name.endswith(expected_suffix):
            raise ValueError(
                f"SKU_NAME 年份或尺码不符合已批准适配范围：{sku_name}，应以 {expected_suffix} 结尾"
            )
        fitments = sorted({f"{row['MAKE']} {row['MODEL']}" for row in records})
        length_min, length_max, _ = dimension_summary(records, "L-MM")
        width_min, width_max, _ = dimension_summary(records, "W-MM")
        height_min, height_max, _ = dimension_summary(records, "H-MM")
        link_name = f"{records[0]['MAKE']} {records[0]['MODEL']} {naming_span}"
        publish_rows.append({
            "SKU_NAME": sku_name, "CLUSTER_ID": shipment["聚类ID"], "链接名称": link_name, "尺码": shipment["发货逻辑尺码"],
            "预估销量": shipment["预估销量"], "销量倍率": shipment["销量倍率"], "加权销量": shipment["加权销量"], "销量占比": shipment["全局销量占比"],
            "发货数量": shipment["发货数量"], "适配车型": " / ".join(fitments),
            "适配年份": fitment_years, "适配记录数": len(records),
            "车长最小毫米": length_min, "车长最大毫米": length_max,
            "车宽最小毫米": width_min, "车宽最大毫米": width_max,
            "车高最小毫米": height_min, "车高最大毫米": height_max,
            "尺寸集中度": dimension_concentration(records),
        })
    if len({row["链接名称"] for row in publish_rows}) != len(publish_rows):
        raise ValueError("扩张年份后的链接名称不唯一")
    if len({row["SKU_NAME"] for row in publish_rows}) != len(publish_rows):
        raise ValueError("扩张年份后的 SKU_NAME 不唯一")
    write_csv(publish_dir / "链接发货适配表.csv", publish_columns, publish_rows)

    # 聚类主表、全量发货分析和上架明细均以聚类ID为一行。合并为一个
    # 权威主表，避免同粒度数据分散在多个目录并产生口径漂移。
    allocation_by_cluster = {str(row["聚类ID"]): row for row in enriched_full_shipment_rows}
    listing_by_cluster = {str(row["聚类ID"]): row for row in listing_rows}
    consolidated_columns = master_columns + [
        "全局销量占比", "理论发货量", "发货数量", "取整补量", "是否发货",
        *dimension_columns,
        "SKU名称", "尺码名称", "适配车型", "原始年份", "命名年份",
        "年份合并结论", "新增年份数", "年份冲突明细",
    ]
    consolidated_rows: list[dict[str, object]] = []
    for master in master_rows:
        cluster_id = str(master["聚类ID"])
        allocation = allocation_by_cluster[cluster_id]
        listing = listing_by_cluster[cluster_id]
        consolidated_rows.append({
            **master,
            **{column: allocation[column] for column in [
                "全局销量占比", "理论发货量", "发货数量", "取整补量", "是否发货", *dimension_columns,
            ]},
            **{column: listing.get(column, "") for column in [
                "SKU名称", "尺码名称", "适配车型", "原始年份", "命名年份",
                "年份合并结论", "新增年份数", "年份冲突明细",
            ]},
        })
    write_csv(master_dir / "聚类主表.csv", consolidated_columns, consolidated_rows)

    final_size_totals: dict[str, dict[str, int]] = {}
    for row in consolidated_rows:
        size = str(row["逻辑尺码"])
        values = final_size_totals.setdefault(size, {"clusters": 0, "sales": 0, "weighted_sales": 0.0, "shipped": 0})
        values["clusters"] += 1
        values["sales"] += int(row["预估销量"])
        values["weighted_sales"] += float(row["加权销量"])
        values["shipped"] += int(row["发货数量"])

    summary_rows: list[dict[str, object]] = []
    for size, values in final_size_totals.items():
        summary_rows.append({
            "最终发货尺码": size, "聚类数量": values["clusters"], "预估销量": values["sales"],
            "销量倍率": sales_multipliers.get(size, 1.0), "加权销量": values["weighted_sales"],
            "销量占比": f"{values['weighted_sales'] / total_weighted_sales:.6%}", "发货数量": values["shipped"],
            "发货占比": f"{values['shipped'] / total_supply:.6%}",
        })
    summary_rows.append({
        "最终发货尺码": "合计", "聚类数量": len(master_rows), "预估销量": total_sales, "销量倍率": "", "加权销量": total_weighted_sales,
        "销量占比": "100.000000%", "发货数量": total_supply, "发货占比": "100.000000%",
    })
    summary_columns = ["最终发货尺码", "聚类数量", "预估销量", "销量倍率", "加权销量", "销量占比", "发货数量", "发货占比"]
    write_csv(shipment_dir / "尺码发货汇总.csv", summary_columns, summary_rows)
    write_csv(publish_dir / "尺码发货汇总.csv", summary_columns, summary_rows)
    input_dir = output / "00_输入"
    input_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        input_dir / "尺码发货配额输入.csv", ["逻辑尺码", "发货量"],
        [{"逻辑尺码": row["最终发货尺码"], "发货量": row["发货数量"]} for row in summary_rows[:-1]],
    )

    table = ["| 最终发货尺码 | 聚类数量 | 预估销量 | 销量占比 | 发货数量 |", "|---|---:|---:|---:|---:|"]
    for row in summary_rows:
        table.append(f"| {row['最终发货尺码']} | {row['聚类数量']:,} | {row['预估销量']:,} | {row['销量占比']} | {row['发货数量']:,} |")
    report = [
        "# W 型车发货方案", "",
        "## 分配口径", "",
        f"- 总供给：{total_supply:,}",
        f"- 聚类数：{len(master_rows):,}",
        f"- 原始预计销量合计：{total_sales:,}",
        f"- 加权销量合计：{total_weighted_sales:,.0f}",
        f"- 销量倍率：{', '.join(f'{size}×{value:g}' for size, value in sales_multipliers.items()) or '无'}",
        "- 分配方法：以 3 件为最小发货单位，按聚类预计销量占比采用最大余数法分配，确保每个发货数量及合计均为 3 的倍数。",
        "",
        "## 按最终发货尺码汇总", "",
        *table,
        "",
        "## 输出说明", "",
        "- `尺码发货汇总.csv`：在流程末端按最终发货尺码汇总的发货计划。",
        "- `../02_聚类数据/聚类主表.csv`：聚类档案、车型适配、发货分配、取整依据和尺寸范围。",
        "- `../05_输出/链接发货适配表.csv`：可直接发布的链接发货、车型、年份与尺寸适配表。",
    ]
    (shipment_dir / "发货方案报告.md").write_text("\n".join(report) + "\n", encoding="utf-8-sig")

    # Preserve supporting data, but separate it from the two final publishing
    # tables. `grouping_detail.csv` is intentionally retained: unlike the
    # all-cluster analysis it contains only the clusters with shipment volume.
    destinations = {
        "合并后聚类明细.csv": (master_dir, "聚类原子明细.csv"),
        "新聚类ID映射.csv": (master_dir, "聚类ID映射.csv"),
        "兄弟链接明细.csv": (master_dir, "关联链接明细.csv"),
        "年份合并测试报告.csv": (output / "04_校验报告", "年份合并校验.csv"),
        "聚类合并测试.csv": (output / "04_校验报告", "聚类合并校验.csv"),
    }
    for filename, (destination, target_name) in destinations.items():
        source = output / filename
        if not source.exists():
            continue
        destination.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination / target_name))

    # The enriched master table above supersedes this raw engine export.  The
    # legacy final report also repeats the new report with an older allocation
    # basis, so both are deliberately excluded.
    for filename in ("合并后聚类主表.csv", "grouping_detail.csv", "listing_detail.csv", "sku_shipment_analysis.csv", "shipment_input.csv", "最终报告.md"):
        path = output / filename
        if path.exists():
            path.unlink()


def publish_final_output(repo: Path, output: Path) -> None:
    """Replace the public W-car release with the approved final export."""
    sources = [
        output / "05_输出" / "链接发货适配表.csv",
        output / "05_输出" / "尺码发货汇总.csv",
    ]
    missing = [source for source in sources if not source.exists()]
    if missing:
        raise FileNotFoundError(f"缺少待发布文件：{missing}")

    release_dir = repo / "public" / "sku_cluster" / "W型车"
    obsolete_files = (
        "car_cluster_atom_audit.csv", "car_cluster_detail.csv", "car_cluster_summary.csv",
        "兄弟链接明细.csv", "新聚类ID映射.csv", "聚类合并测试.csv",
    )
    for filename in obsolete_files:
        target = release_dir / filename
        if target.exists():
            target.unlink()
    for source in sources:
        shutil.copy2(source, release_dir / source.name)


def run(*args: object, cwd: Path | None = None) -> None:
    subprocess.run([sys.executable, *map(str, args)], cwd=cwd, check=True)


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="生成并发布版本化 W 型车聚类与链接分析")
    parser.add_argument("--data", type=Path, default=repo / "03.尺码计算" / "output" / "全尺码全量.csv")
    parser.add_argument("--rules", type=Path, default=repo / "03.尺码计算" / "output" / "尺码匹配规则.csv")
    parser.add_argument("--version", default="0914")
    parser.add_argument("--total-supply", type=int, default=TOTAL_SUPPLY)
    parser.add_argument("--sales-multiplier", action="append", default=[], metavar="SIZE=FACTOR")
    parser.add_argument("--publish", action="store_true", help="发布最终两张表到 public/sku_cluster/W型车")
    args = parser.parse_args()
    sales_multipliers: dict[str, float] = {}
    for value in args.sales_multiplier:
        size, separator, factor = value.partition("=")
        if not separator or not size.strip() or float(factor) <= 0:
            parser.error(f"销量倍率格式错误：{value}，应为 SIZE=正数")
        sales_multipliers[size.strip()] = float(factor)
    cluster_project = repo / "聚类SKU" / "artifacts" / "W型车"
    cluster_output = cluster_project / args.version
    engine = repo / "链接分析" / "sku_shipment_analysis"
    output = Path(__file__).resolve().parent / "artifacts" / args.version

    run(
        cluster_project / "run_cluster.py",
        "--data", args.data,
        "--rules", args.rules,
        "--output", cluster_output,
    )
    run(
        engine / "build_merged_clusters.py",
        "--cluster-dir", cluster_output,
        "--output-dir", output,
        "--publish",
        cwd=engine,
    )
    run(
        engine / "main.py",
        "--cluster-dir", cluster_output,
        "--output-dir", output,
        cwd=engine,
    )
    build_shipment_outputs(output, args.total_supply, sales_multipliers)
    if args.publish:
        publish_final_output(repo, output)


if __name__ == "__main__":
    main()
