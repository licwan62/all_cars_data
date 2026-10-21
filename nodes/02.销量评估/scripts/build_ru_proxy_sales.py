#!/usr/bin/env python3
"""按 RU DIMENSION-ID 汇总 Auto.ru 在售样本的代理销量，发布 output/RU代理销量.csv。

输入：
  data/ru/auto_ru_model_sales_with_match_key.csv   本节点维护的 Auto.ru 销量样本（按 match_key）
  01.整理尺寸库/output/来源映射_RU.csv             来源ID（"RU|<match_key>"）-> 最终 RU DIMENSION-ID
  01.整理尺寸库/output/尺寸库_RU.csv               RU 尺寸库（输出覆盖全部 RU ID，无样本的为 0）
输出：DIMENSION-ID, 销量合计（整数）；审计信息写入 artifacts/<批次>/status.json。
先写入新的 artifacts 批次，校验通过后原子更新 output/。
"""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
UPSTREAM = PROJECT.parent / "01.整理尺寸库" / "output"
SALES_PATH = PROJECT / "data" / "ru" / "auto_ru_model_sales_with_match_key.csv"
SOURCE_MAP_PATH = UPSTREAM / "来源映射_RU.csv"
DIMENSIONS_PATH = UPSTREAM / "尺寸库_RU.csv"
OUTPUT_NAME = "RU代理销量.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build(sales_rows, source_rows, dimension_rows) -> tuple[list[dict[str, object]], dict[str, object]]:
    by_key: dict[str, float] = defaultdict(float)
    for row in sales_rows:
        key = (row.get("match_key") or "").strip()
        value = number(row.get("sale_detail", ""))
        if key and value is not None:
            by_key[key] += value
    source_to_id = {row["来源ID"]: row["DIMENSION-ID"] for row in source_rows}
    totals: dict[str, float] = {row["DIMENSION-ID"]: 0.0 for row in dimension_rows}
    if set(source_to_id.values()) - set(totals):
        raise ValueError("来源映射_RU.csv 含尺寸库_RU.csv 以外的 DIMENSION-ID")
    matched = 0.0
    for key, value in by_key.items():
        dimension_id = source_to_id.get(f"RU|{key}")
        if dimension_id is not None:
            totals[dimension_id] += value
            matched += value
    if any(value % 1 for value in totals.values()):
        raise ValueError("RU 代理销量汇总结果不是整数")
    result = [{"DIMENSION-ID": dimension_id, "销量合计": int(value)} for dimension_id, value in sorted(totals.items())]
    source_total = sum(value for row in sales_rows if (value := number(row.get("sale_detail", ""))) is not None)
    audit = {
        "sales_source_rows": len(sales_rows),
        "sales_source_positive_rows": sum(1 for row in sales_rows if (number(row.get("sale_detail", "")) or 0) > 0),
        "sales_rows_without_match_key": sum(1 for row in sales_rows if not (row.get("match_key") or "").strip()),
        "sales_source_total": int(source_total),
        "matched_sales_total": int(matched),
        "unmatched_sales_total": int(source_total - matched),
        "dimension_rows": len(result),
        "dimension_rows_with_positive_proxy_sales": sum(1 for row in result if row["销量合计"] > 0),
    }
    return result, audit


def next_artifact_dir() -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = [int(m.group(1)) for p in (PROJECT / "artifacts").glob(f"{prefix}*") if (m := re.match(rf"{prefix}(\d{{2}})_", p.name))]
    return PROJECT / "artifacts" / f"{prefix}{max(used, default=0) + 1:02d}_ru-proxy-sales"


def main() -> int:
    result, audit = build(read_rows(SALES_PATH), read_rows(SOURCE_MAP_PATH), read_rows(DIMENSIONS_PATH))
    artifact = next_artifact_dir()
    staging = artifact.with_name(f".{artifact.name}.tmp")
    (staging / "output").mkdir(parents=True)
    target = staging / "output" / OUTPUT_NAME
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["DIMENSION-ID", "销量合计"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(result)
    status = {"status": "passed", "inputs": [str(SALES_PATH), str(SOURCE_MAP_PATH), str(DIMENSIONS_PATH)], **audit}
    (staging / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(staging, artifact)
    destination = PROJECT / "output" / OUTPUT_NAME
    temporary = destination.with_name(f".{OUTPUT_NAME}.tmp")
    shutil.copy2(artifact / "output" / OUTPUT_NAME, temporary)
    os.replace(temporary, destination)
    print(json.dumps({**audit, "artifact": str(artifact)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
