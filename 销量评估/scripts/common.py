from __future__ import annotations

import csv
import json
import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from id_scheme import atom_record_id as make_atom_record_id, dimension_id
YEAR_PATTERN = re.compile(r"^(\d{4})(?:\s*[-–—]\s*(\d{4}))?$")

CACHE_FIELDS = [
    "MAKE",
    "MODEL",
    "YEAR",
    "SALES_MODEL_NAME",
    "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES",
    "RAW_SALES",
    "SALES_SCOPE",
    "SALES_PERIOD",
    "SALES_PERIOD_END",
    "SALES_SOURCE_TYPE",
    "SALES_SOURCE",
    "SOURCE_URL",
    "SECONDARY_SOURCE_URL",
    "SOURCE_CONFIDENCE",
    "NOTES",
]

OVERRIDE_FIELDS = [
    "SALES_ATOM_KEY",
    "ALLOCATION_WEIGHT",
    "ALLOCATION_METHOD",
    "SALES_CONFIDENCE",
    "NOTES",
]

SALES_FIELDS = [
    "DIMENSION-ID",
    "MAKE",
    "MODEL",
    "版本",
    "CAB",
    "BED",
    "结构",
    "代际",
    "YEAR",
    "SALES_ATOM_KEY",
    "ATOM_ROW_ID",
    "SALES_MODEL_NAME",
    "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES",
    "ALLOCATION_WEIGHT",
    "US_SALES_ESTIMATE",
    "SALES_ESTIMATE_TYPE",
    "ALLOCATION_METHOD",
    "SALES_CONFIDENCE",
    "SALES_SOURCE_TYPE",
    "SALES_SOURCE",
    "SOURCE_URL",
    "SECONDARY_SOURCE_URL",
    "SALES_SCOPE",
    "SALES_PERIOD",
    "SALES_PERIOD_END",
    "NOTES",
    "ITERATION_STATUS",
]


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_config(config_path: str | Path = "config.json") -> dict:
    path = resolve_path(config_path)
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    config["_config_path"] = str(path)
    return config


def read_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    resolved = resolve_path(path)
    with resolved.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {resolved}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"CSV has duplicate headers: {resolved}")
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    return list(reader.fieldnames), rows


def write_csv(path: str | Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    temporary = resolved.with_suffix(resolved.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    os.replace(temporary, resolved)


def write_json(path: str | Path, value: object) -> None:
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    temporary = resolved.with_suffix(resolved.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, resolved)


def ensure_csv_template(path: str | Path, fieldnames: Sequence[str]) -> None:
    resolved = resolve_path(path)
    if not resolved.exists():
        write_csv(resolved, fieldnames, [])


def expand_year(value: str) -> list[int]:
    match = YEAR_PATTERN.fullmatch(value.strip())
    if not match:
        raise ValueError(f"invalid YEAR value: {value!r}")
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise ValueError(f"YEAR range is reversed: {value!r}")
    if start < 1886 or end > 2100:
        raise ValueError(f"YEAR is outside the supported range: {value!r}")
    return list(range(start, end + 1))


def model_year_key(row: Mapping[str, str]) -> tuple[str, str, str]:
    return row.get("MAKE", "").strip(), row.get("MODEL", "").strip(), row.get("YEAR", "").strip()


def sales_atom_key(row: Mapping[str, str]) -> str:
    return "|".join(row.get(field, "").strip() for field in ("MAKE", "MODEL", "版本", "CAB", "BED", "结构", "YEAR"))


def parse_nonnegative_integer(value: str, label: str) -> int:
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{label} is not numeric: {value!r}") from exc
    if number < 0 or number != number.to_integral_value():
        raise ValueError(f"{label} must be a non-negative integer: {value!r}")
    return int(number)


def decimal_text(value: Decimal, places: int = 12) -> str:
    text = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return text or "0"


def require_fields(fieldnames: Sequence[str], required: Sequence[str], source: str) -> None:
    missing = [field for field in required if field not in fieldnames]
    if missing:
        raise ValueError(f"{source} is missing required columns: {', '.join(missing)}")
