"""发现字段、只读盘点、保留原值并按年展开身份；不推断市场/代际。"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ALIASES = {
    "source_row_id": ["source_row_id", "source_record_id", "DIMENSION-ID", "id"],
    "make": ["make", "MAKE", "品牌"], "model": ["model", "MODEL", "车型"],
    "model_year": ["model_year"], "year_range": ["YEAR", "year", "年份"],
    "year_start": ["year_start"], "year_end": ["year_end"],
    "body_type": ["body_type", "BODY_TYPE", "结构"],
    "generation": ["generation", "代际"], "trim": ["trim", "版本"],
    "market": ["market", "COUNTRY"],
    "length_mm": ["length_mm", "L-IN"], "width_mm": ["width_mm", "W-IN"],
    "height_mm": ["height_mm", "H-IN"], "wheelbase_mm": ["wheelbase_mm"],
    "front_overhang_mm": ["front_overhang_mm"], "rear_overhang_mm": ["rear_overhang_mm"],
}
DIMENSIONS = [k for k in ALIASES if k.endswith("_mm")]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_table(path: Path) -> tuple[list[str], list[dict]]:
    if path.suffix.lower() in {".csv", ".tsv"}:
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
            columns = reader.fieldnames or []
            if len(columns) != len(set(columns)) or not columns:
                raise ValueError("输入列名为空或重复")
            rows = list(reader)
            if any(None in r for r in rows):
                raise ValueError("CSV 行包含超出表头的值")
            return columns, [{k: v or "" for k, v in r.items()} for r in rows]
    if path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            records = iter(book.active.values)
            columns = [str(v) if v is not None else "" for v in next(records)]
            if not all(columns) or len(columns) != len(set(columns)):
                raise ValueError("XLSX 列名为空或重复")
            return columns, [dict(zip(columns, ["" if v is None else str(v) for v in row]))
                             for row in records if any(v is not None for v in row)]
        finally:
            book.close()
    raise ValueError("支持 CSV/TSV/XLSX；Parquet 尚未启用")


def discover(columns: list[str]) -> dict:
    mapping, ambiguities = {}, {}
    for logical, names in ALIASES.items():
        matches = [c for c in columns if c in names]
        if len(matches) == 1:
            mapping[logical] = matches[0]
        elif len(matches) > 1:
            ambiguities[logical] = matches
    return {"columns": mapping, "units": {k: "inch" if mapping.get(k, "").endswith("-IN") else "mm"
                                          for k in DIMENSIONS if k in mapping},
            "market_from_id_suffix": mapping.get("source_row_id") == "DIMENSION-ID",
            "width_definition": "unknown", "ambiguities": ambiguities}


def clean(value) -> str:
    return " ".join(str(value or "").split())


def identity(record: dict) -> str:
    # trim 也是分支，避免同年份不同车体版本混用；不包含原行 ID。
    parts = [clean(record.get(k)).casefold() for k in
             ("make", "model", "model_year", "generation", "body_type", "trim", "market")]
    return "v1:" + hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()[:24]


def years(row: dict, mapping: dict) -> list[int]:
    columns = mapping["columns"]
    def value(key):
        return clean(row.get(columns.get(key, "")))
    if value("model_year"):
        text = value("model_year")
    elif value("year_start"):
        text = value("year_start") + "-" + (value("year_end") or value("year_start"))
    else:
        text = value("year_range")
    match = re.fullmatch(r"(\d{4})(?:\s*[-–]\s*(\d{4}))?", text)
    if not match:
        raise ValueError(f"不明确的年份: {text!r}")
    start, end = int(match[1]), int(match[2] or match[1])
    if start < 1886 or end > 2100 or end < start or end - start > 100:
        raise ValueError(f"年份区间无效: {text}")
    return list(range(start, end + 1))


def normalize(rows: list[dict], mapping: dict, file_id: str) -> list[dict]:
    result = []
    for index, raw in enumerate(rows, start=2):
        record = {k: clean(raw.get(c)) for k, c in mapping["columns"].items() if k not in DIMENSIONS}
        record["source_record_id"] = record.pop("source_row_id", "") or f"{file_id}:row:{index}"
        if not record.get("make") or not record.get("model"):
            raise ValueError(f"第 {index} 行缺少品牌/车型")
        if not record.get("market") and mapping.get("market_from_id_suffix"):
            suffix = record["source_record_id"].rsplit(" ", 1)[-1]
            if suffix in {"US", "EU", "RU"}:
                record["market"] = suffix
        flags = ["MISSING_" + k.upper() for k in ("generation", "body_type", "market") if not record.get(k)]
        for key in DIMENSIONS:
            text = clean(raw.get(mapping["columns"].get(key, "")))
            record[key] = None
            if text:
                try:
                    unit = mapping.get("units", {}).get(key)
                    if unit not in {"mm", "cm", "inch"}:
                        raise ValueError("单位未声明")
                    v = float(text) * {"mm": 1, "cm": 10, "inch": 25.4}[unit]
                    if not math.isfinite(v) or v <= 0:
                        raise ValueError("尺寸非正数")
                    record[key] = round(v, 6)
                except ValueError:
                    flags.append("INVALID_" + key.upper())
        if record["width_mm"] and mapping.get("width_definition") != "excluding_mirrors":
            flags.append("WIDTH_DEFINITION_UNKNOWN")
        for year in years(raw, mapping):
            item = {**record, "model_year": year, "raw_fields": raw.copy(), "identity_flags": sorted(flags),
                    "width_definition": mapping.get("width_definition", "unknown")}
            item["variant_key"] = identity(item)
            result.append(item)
    return result


def inspect_table(path: Path) -> dict:
    before = digest(path)
    columns, rows = read_table(path)
    mapping = discover(columns)
    ids = Counter(clean(r.get(mapping["columns"].get("source_row_id", ""))) for r in rows)
    duplicates = {k: v for k, v in ids.items() if k and v > 1}
    coverage, errors, markets, generations = defaultdict(set), [], Counter(), Counter()
    physical = Counter()
    for index, row in enumerate(rows, 2):
        try:
            records = normalize([row], mapping, before)
            for r in records:
                coverage[(r["make"], r["model"], r.get("market", ""))].add(r["model_year"])
            r = records[0]
            markets[r.get("market", "")] += 1
            generations[r.get("generation", "")] += 1
            physical[tuple(r.get(k) for k in ("make", "model", "body_type", "generation", "trim", "market"))
                     + tuple(years(row, mapping)) + tuple(r.get(k) for k in DIMENSIONS)] += 1
        except ValueError as e:
            errors.append({"row": index, "error": str(e)})
    after = digest(path)
    if before != after:
        raise ValueError("盘点期间原文件发生变化")
    return {"input": str(path.resolve()), "sha256_before": before, "sha256_after": after,
            "source_unchanged": True, "rows": len(rows), "columns": columns, "column_map_draft": mapping,
            "unmapped_columns": [c for c in columns if c not in mapping["columns"].values()],
            "missing_by_column": {c: sum(not clean(r.get(c)) for r in rows) for c in columns},
            "duplicate_source_ids": duplicates, "exact_duplicate_rows": len(rows) - len({json.dumps(r, sort_keys=True) for r in rows}),
            "duplicate_physical_groups": sum(v > 1 for v in physical.values()), "normalization_errors": errors,
            "market_counts": dict(markets), "missing_generation": generations.get("", 0),
            "model_year_coverage": [{"make": k[0], "model": k[1], "market": k[2], "year_start": min(v),
                                     "year_end": max(v), "years": sorted(v)} for k, v in sorted(coverage.items())],
            "risks": ["BODY_TYPE/结构/分类/旧车形号不能直映 COVER_SHAPE", "跨代年份必须分别查证；缺失代际不得推定",
                      "宽度是否含后视镜未声明", "市场仅取显式列或已配置的 ID 后缀", "未知字段保留在 raw_fields"]}
