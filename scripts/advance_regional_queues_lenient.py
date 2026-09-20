#!/usr/bin/env python3
"""Advance EU/RU shape and sales queues with explicitly labelled loose proxies."""

from __future__ import annotations

import csv
import json
import os
import shutil
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def next_batch(directory: Path, slug: str) -> Path:
    prefix = date.today().isoformat()
    used = []
    for path in directory.glob(f"{prefix}_*_{slug}"):
        try:
            used.append(int(path.name.split("_", 2)[1]))
        except (IndexError, ValueError):
            pass
    return directory / f"{prefix}_{max(used, default=0) + 1:02d}_{slug}"


def one_shape(value: str) -> str:
    shapes = sorted({item.strip() for item in value.split(";") if item.strip()})
    return shapes[0] if len(shapes) == 1 else ""


def advance_shapes() -> dict[str, object]:
    project = ROOT / "03.车形分类核定"
    queue_path = project / "research_queue" / "regional_queue.csv"
    fields, rows = read_csv(queue_path)
    before = [dict(row) for row in rows]
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    resolved = []
    remaining = []
    for row in rows:
        shape = one_shape(row.get("当前车形", ""))
        if shape:
            row["状态"] = "done_lenient_single_shape"
            row["worker"] = "lenient-regional-pass"
            row["updated_at"] = stamp
            resolved.append({**row, "宽松核定车形": shape, "核定依据": "区域现有结果在模型键内只有一个车形"})
        else:
            remaining.append(row)
    batch = next_batch(project / "artifacts", "regional-shape-lenient")
    batch.mkdir(parents=True)
    write_csv(batch / "queue_before.csv", fields, before)
    write_csv(batch / "resolved_lenient.csv", fields + ["宽松核定车形", "核定依据"], resolved)
    write_csv(batch / "remaining_review.csv", fields, remaining)
    write_csv(queue_path, fields, rows)
    summary = {
        "status": "passed",
        "policy": "single existing regional shape per model key",
        "queue_rows": len(rows),
        "resolved_lenient": len(resolved),
        "remaining_review": len(remaining),
        "resolved_by_region": dict(Counter(row["地区"] for row in resolved)),
        "artifact": str(batch.relative_to(ROOT)).replace("\\", "/"),
    }
    (batch / "status.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def advance_sales() -> dict[str, object]:
    project = ROOT / "02.销量评估"
    queue_path = project / "research_queue" / "regional_sales_queue.csv"
    fields, rows = read_csv(queue_path)
    before = [dict(row) for row in rows]
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    advanced = []
    for row in rows:
        if row.get("REGION") not in {"EU", "RU"}:
            continue
        metric = row.get("CURRENT_METRIC", "")
        if metric == "DIMENSION_CATALOG_ROW_COUNT_PROXY":
            status = "READY_LOOSE_CATALOG_COVERAGE_PROXY"
            basis = "以该模型键的尺寸目录行数作为研究排序代理；不是销量"
        elif metric and metric != "UNAVAILABLE":
            status = "READY_LOOSE_EXISTING_REGIONAL_METRIC"
            basis = "保留区域事实或既有代理指标，不提升其口径"
        else:
            status = "READY_LOOSE_CATALOG_COVERAGE_PROXY"
            row["CURRENT_METRIC"] = "DIMENSION_CATALOG_ROW_COUNT_PROXY"
            row["CURRENT_VALUE_SUM"] = row.get("DIMENSION_ROWS", "0")
            basis = "以该模型键的尺寸目录行数作为研究排序代理；不是销量"
        row["STATUS"] = status
        row["worker"] = "lenient-regional-pass"
        row["updated_at"] = stamp
        advanced.append({**row, "宽松依据": basis})
    batch = next_batch(project / "artifacts", "regional-sales-lenient")
    batch.mkdir(parents=True)
    write_csv(batch / "queue_before.csv", fields, before)
    write_csv(batch / "advanced_lenient.csv", fields + ["宽松依据"], advanced)
    write_csv(queue_path, fields, rows)
    summary = {
        "status": "passed",
        "policy": "existing regional metric, otherwise dimension catalog row-count proxy",
        "warning": "DIMENSION_CATALOG_ROW_COUNT_PROXY is a prioritization proxy, not vehicle sales",
        "advanced_rows": len(advanced),
        "by_region": dict(Counter(row["REGION"] for row in advanced)),
        "by_status": dict(Counter(row["STATUS"] for row in advanced)),
        "artifact": str(batch.relative_to(ROOT)).replace("\\", "/"),
    }
    (batch / "status.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def loose_shape(row: dict[str, str]) -> tuple[str, str, str]:
    """Return shape, confidence and an auditable coverage-first method."""
    existing = one_shape(row.get("当前车形", ""))
    if existing:
        return existing, "medium", "regional-single-shape"
    structure = row.get("结构", "").casefold()
    category = row.get("分类", "")
    if "pickup" in structure or category == "皮卡":
        return "P0", "low", "structure-category-proxy"
    if any(token in structure for token in ("van", "bus", "mpv")) or category == "MPV":
        return "V0", "low", "structure-category-proxy"
    if "suv" in structure or category in {"越野车", "SUV"}:
        return "SU1", "low", "structure-category-proxy"
    if any(token in structure for token in ("hatch", "wagon", "estate")) or category == "两厢车":
        return "H0", "low", "structure-category-proxy"
    if category == "跑车" or any(token in structure for token in ("coupe", "convertible", "roadster", "targa")):
        return "SD0", "low", "structure-category-proxy"
    return "SD1", "low", "category-default-proxy"


def build_coverage_candidates() -> dict[str, object]:
    shape_project = ROOT / "03.车形分类核定"
    sales_project = ROOT / "02.销量评估"
    shape_queue_fields, shape_queue = read_csv(shape_project / "research_queue" / "regional_queue.csv")
    by_model = {(row["地区"], row["MAKE"].casefold(), row["MODEL"].casefold()): row for row in shape_queue}
    shape_batch = next_batch(shape_project / "artifacts", "regional-coverage-candidates")
    sales_batch = next_batch(sales_project / "artifacts", "regional-coverage-candidates")
    shape_batch.mkdir(parents=True)
    sales_batch.mkdir(parents=True)
    shape_rows: list[dict[str, str]] = []
    for region in ("EU", "RU"):
        _, dimensions = read_csv(ROOT / "01.整理尺寸库" / "output" / f"尺寸库_{region}.csv")
        for row in dimensions:
            key = (region, row["MAKE"].casefold(), row["MODEL"].casefold())
            queue = by_model.get(key)
            if queue is None:
                # A shared EU;RU model can safely provide only a consensus shape.
                queue = by_model.get(("EU;RU", key[1], key[2]))
            context = {**row, "当前车形": queue.get("当前车形", "") if queue else ""}
            shape, confidence, method = loose_shape(context)
            shape_rows.append({
                "地区": region, "DIMENSION-ID": row["DIMENSION-ID"], "MAKE": row["MAKE"], "MODEL": row["MODEL"],
                "结构": row.get("结构", ""), "分类": row.get("分类", ""), "车形候选": shape,
                "置信度": confidence, "方法": method,
                "来源队列": queue.get("queue_key", "") if queue else "", "需质量复核": "yes" if confidence == "low" else "no",
            })
    shape_fields = list(shape_rows[0])
    write_csv(shape_batch / "regional_shape_coverage_candidates.csv", shape_fields, shape_rows)
    shape_summary = {
        "status": "passed", "rows": len(shape_rows), "by_region": dict(Counter(row["地区"] for row in shape_rows)),
        "by_method": dict(Counter(row["方法"] for row in shape_rows)),
        "low_confidence": sum(row["置信度"] == "low" for row in shape_rows),
        "note": "coverage candidates only; does not replace formal shape output",
    }
    (shape_batch / "status.json").write_text(json.dumps(shape_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    _, sales_queue = read_csv(sales_project / "research_queue" / "regional_sales_queue.csv")
    sales_rows = []
    for row in sales_queue:
        if row.get("REGION") not in {"EU", "RU"}:
            continue
        metric = row.get("CURRENT_METRIC", "")
        value = row.get("CURRENT_VALUE_SUM", "")
        is_catalog_proxy = metric == "DIMENSION_CATALOG_ROW_COUNT_PROXY"
        sales_rows.append({
            "REGION": row["REGION"], "MAKE": row["MAKE"], "MODEL": row["MODEL"], "YEAR_RANGE": row["YEAR_RANGE"],
            "coverage_proxy_value": value, "metric": metric, "proxy_kind": "catalog-coverage" if is_catalog_proxy else "regional-existing-metric",
            "confidence": "low" if is_catalog_proxy else "medium", "queue_key": row["queue_key"],
            "note": "not vehicle sales; use only for research prioritization" if is_catalog_proxy else "regional metric retained without relabelling as annual sales",
        })
    sales_fields = list(sales_rows[0])
    write_csv(sales_batch / "regional_sales_coverage_candidates.csv", sales_fields, sales_rows)
    sales_summary = {
        "status": "passed", "rows": len(sales_rows), "by_region": dict(Counter(row["REGION"] for row in sales_rows)),
        "by_proxy_kind": dict(Counter(row["proxy_kind"] for row in sales_rows)),
        "note": "coverage/prioritization candidates only; not annual sales",
    }
    (sales_batch / "status.json").write_text(json.dumps(sales_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"shape": {**shape_summary, "artifact": str(shape_batch.relative_to(ROOT)).replace("\\", "/")}, "sales": {**sales_summary, "artifact": str(sales_batch.relative_to(ROOT)).replace("\\", "/")}}


def main() -> int:
    shape = advance_shapes()
    sales = advance_sales()
    coverage = build_coverage_candidates()
    print(json.dumps({"shape": shape, "sales": sales, "coverage": coverage}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
