from __future__ import annotations

import re
from collections.abc import Iterable

from .models import ModelMapping, VehicleRecord


DIMENSION_CODE_FIELDS = ["DIMENSION-ID", "DIMENSION-CODE"]
_YEAR = re.compile(r"(\d{4})(?:\s*-\s*(\d{4}))?")


def year_code(year: str) -> str:
    """年份区间两端后两位拼接：1956-2012 -> 5612；单年份重复：1994 -> 9494。"""
    match = _YEAR.fullmatch(year.strip())
    if not match:
        raise ValueError(f"Unsupported YEAR value for YEARCODE: {year!r}")
    start = match.group(1)
    end = match.group(2) or start
    return start[2:] + end[2:]


def dimension_code(prefix: str, make_code: str, model_code: str, year: str) -> str:
    """DIMENSION-CODE = 区域前缀 + MAKECODE + MODELCODE + YEARCODE。"""
    return f"{prefix}{make_code}{model_code}{year_code(year)}"


def dimension_code_rows(
    records: Iterable[VehicleRecord], models: Iterable[ModelMapping], prefix: str
) -> list[dict[str, str]]:
    codes = {(item.make_key, item.model_key): (item.make_code, item.model_code) for item in models}
    rows = []
    for record in records:
        if not record.dimension_id:
            continue
        make_code, model_code = codes[(record.make_key, record.model_key)]
        rows.append(
            {
                "DIMENSION-ID": record.dimension_id,
                "DIMENSION-CODE": dimension_code(prefix, make_code, model_code, record.year),
            }
        )
    return sorted(rows, key=lambda row: row["DIMENSION-ID"])


def duplicate_code_count(rows: Iterable[dict[str, str]]) -> int:
    """报告共用同一 DIMENSION-CODE 的行数（该码是分组码，不保证唯一）。"""
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["DIMENSION-CODE"]] = counts.get(row["DIMENSION-CODE"], 0) + 1
    return sum(count for count in counts.values() if count > 1)


__all__ = ["DIMENSION_CODE_FIELDS", "dimension_code", "dimension_code_rows", "duplicate_code_count", "year_code"]
