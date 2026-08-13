from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from id_scheme import dimension_id


ROOT = Path(__file__).resolve().parent
PREFIX = "MAKE="


def main() -> None:
    errors: list[str] = []
    source_path = ROOT / "source" / "车型尺寸库.csv"
    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        source = list(csv.DictReader(handle))
    for line, row in enumerate(source, start=2):
        if row.get("DIMENSION-ID") != dimension_id(row):
            errors.append(f"{source_path}:{line}: derived DIMENSION-ID mismatch")

    for path in [ROOT / "车形分类核定", ROOT / "分类结构审核", ROOT / "销量评估"]:
        for csv_path in path.rglob("*.csv"):
            with csv_path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                for line, row in enumerate(reader, start=2):
                    for field in ("DIMENSION-ID", "original_dimension_id"):
                        value = row.get(field, "")
                        if value and not value.startswith(PREFIX):
                            errors.append(f"{csv_path}:{line}:{field}")
                    for field in ("ATOM_ROW_ID", "atom_record_id"):
                        value = row.get(field, "")
                        if value and (not value.startswith(PREFIX) or "|ATOM_YEAR=" not in value):
                            errors.append(f"{csv_path}:{line}:{field}")

        for json_path in path.rglob("*.json"):
            value = json.loads(json_path.read_text(encoding="utf-8-sig"))

            def inspect(item, location: str) -> None:
                if isinstance(item, dict):
                    for key, child in item.items():
                        if key in {"DIMENSION-ID", "original_dimension_id"} and isinstance(child, str) and child and not child.startswith(PREFIX):
                            errors.append(f"{json_path}:{location}.{key}")
                        inspect(child, f"{location}.{key}")
                elif isinstance(item, list):
                    for index, child in enumerate(item):
                        inspect(child, f"{location}[{index}]")

            inspect(value, "$")

    atom_path = ROOT / "销量评估" / "artifacts" / "atom_sales.csv"
    with atom_path.open(encoding="utf-8-sig", newline="") as handle:
        atom_ids = [row["atom_record_id"] for row in csv.DictReader(handle)]
    duplicates = [key for key, count in Counter(atom_ids).items() if count > 1]
    if duplicates:
        errors.append(f"{atom_path}: {len(duplicates)} duplicate atom_record_id values")

    if errors:
        raise SystemExit("identifier validation failed:\n" + "\n".join(errors[:50]))
    print(
        f"identifier validation passed: {len(source)} source rows, "
        f"{len(set(row['DIMENSION-ID'] for row in source))} dimension groups, "
        f"{len(atom_ids)} unique year atoms"
    )


if __name__ == "__main__":
    main()
