from __future__ import annotations

import csv
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_ROOTS = [ROOT / "source", ROOT / "车形分类核定", ROOT / "分类结构审核", ROOT / "销量评估"]
CODE_ROOTS = [ROOT / "车形分类核定", ROOT / "分类结构审核", ROOT / "销量评估"]
PREFIX = "DIMENSION-GROUP|"
HEADER_RENAMES = {
    "record_id": "DIMENSION-ID",
    "original_record_id": "original_dimension_id",
    "old_record_id": "old_dimension_id",
}


def clean(value: str) -> str:
    return (value or "").replace(PREFIX, "")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, path)


def migrate_csv(path: Path) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        old_fields = list(reader.fieldnames or [])
        rows = list(reader)
    fields = [HEADER_RENAMES.get(field, field) for field in old_fields]
    migrated = []
    for row in rows:
        migrated.append({HEADER_RENAMES.get(key, key): clean(value) for key, value in row.items()})
    write_csv(path, fields, migrated)


def migrate_json(path: Path) -> None:
    value = json.loads(path.read_text(encoding="utf-8-sig"))

    def convert(item):
        if isinstance(item, str):
            return clean(item)
        if isinstance(item, list):
            return [convert(child) for child in item]
        if isinstance(item, dict):
            return {HEADER_RENAMES.get(key, key): convert(child) for key, child in item.items()}
        return item

    path.write_text(json.dumps(convert(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def migrate_code(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    replacements = [
        ('"original_record_id"', '"original_dimension_id"'),
        ("'original_record_id'", "'original_dimension_id'"),
        ('"record_id"', '"DIMENSION-ID"'),
        ("'record_id'", "'DIMENSION-ID'"),
        (PREFIX, ""),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    csv_count = json_count = code_count = 0
    for root in DATA_ROOTS:
        for path in root.rglob("*.csv"):
            migrate_csv(path)
            csv_count += 1
        for path in root.rglob("*.json"):
            migrate_json(path)
            json_count += 1
    for root in CODE_ROOTS:
        for path in root.rglob("*.py"):
            migrate_code(path)
            code_count += 1
    for path in (ROOT / "id_scheme.py", ROOT / "verify_dimension_group_ids.py"):
        migrate_code(path)
        code_count += 1
    print(f"migrated schema in {csv_count} CSV, {json_count} JSON, and {code_count} Python files")


if __name__ == "__main__":
    main()
