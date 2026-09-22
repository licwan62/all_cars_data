from __future__ import annotations

import csv
import json
import os
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "01.整理尺寸库" / "output" / "尺寸库.csv"
OUTPUT = PROJECT / "output" / "车形分类.csv"
QUEUE = PROJECT / "research_queue" / "regional_queue.csv"
CANDIDATES = PROJECT / "artifacts" / "2026-09-21_02_regional-coverage-candidates" / "regional_shape_coverage_candidates.csv"
COUNTRIES = {"US", "EU", "RU"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def split_region(record_id: str) -> tuple[str, str]:
    head, separator, tail = record_id.rpartition(" ")
    country = tail.upper() if separator and tail.upper() in COUNTRIES else "US"
    return (head if separator and tail.upper() in COUNTRIES else record_id), country


def run() -> dict[str, int]:
    prior = read_rows(OUTPUT)
    us_shapes: dict[str, str] = {}
    for row in prior:
        base_id, country = split_region(row["DIMENSION-ID"])
        if country == "US" and row.get("车形"):
            if base_id in us_shapes and us_shapes[base_id] != row["车形"]:
                raise ValueError(f"US 基础 ID 存在多个车形: {base_id}")
            us_shapes[base_id] = row["车形"]

    candidates = {row["DIMENSION-ID"]: row for row in read_rows(CANDIDATES)}

    output: list[dict[str, str]] = []
    queue: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in read_rows(SOURCE):
        record_id = row["DIMENSION-ID"]
        if record_id in seen:
            raise ValueError(f"区域 DIMENSION-ID 重复: {record_id}")
        seen.add(record_id)
        base_id, country = split_region(record_id)
        candidate = candidates.get(record_id, {}) if country != "US" else {}
        shape = us_shapes.get(base_id, "") or candidate.get("车形候选", "")
        if shape:
            if country == "US":
                status = "US核定"
            elif base_id in us_shapes:
                status = "参考US-同基础ID"
            elif candidate.get("方法") == "regional-single-shape":
                status = "区域缓存-同车型单一车形"
            else:
                status = "参考US-结构分类代理"
            output.append({
                "DIMENSION-ID": record_id,
                "COUNTRY": country,
                "车形": shape,
                "处理状态": status,
            })
        if not shape or candidate.get("需质量复核") == "yes":
            queue.append({
                "DIMENSION-ID": record_id, "COUNTRY": country,
                "MAKE": row.get("MAKE", ""), "MODEL": row.get("MODEL", ""),
                "版本": row.get("版本", ""), "结构": row.get("结构", ""),
                "代际": row.get("代际", ""), "YEAR": row.get("YEAR", ""),
                "状态": "待质量复核" if shape else "pending",
                "研究问题": (
                    f"当前以 {candidate.get('方法', '默认规则')} 参考 US 规则代理；需核对轮廓细分类"
                    if shape else "未找到 US 参考规则；需核对区域车身差异"
                ),
            })

    write_rows(OUTPUT, ["DIMENSION-ID", "COUNTRY", "车形", "处理状态"], output)
    write_rows(QUEUE, ["DIMENSION-ID", "COUNTRY", "MAKE", "MODEL", "版本", "结构", "代际", "YEAR", "状态", "研究问题"], queue)
    summary = Counter(row["COUNTRY"] for row in output)
    statuses = Counter(row["处理状态"] for row in output)
    summary.update({"resolved": len(output), "quality_review": len(queue), "source": len(seen)})
    summary["status_counts"] = dict(statuses)
    (PROJECT / "output" / "regional_shape_summary.json").write_text(
        json.dumps(dict(summary), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return dict(summary)


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
