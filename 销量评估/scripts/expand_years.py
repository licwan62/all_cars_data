from __future__ import annotations

import argparse

from common import dimension_id, expand_year, load_config, read_csv, require_fields, write_csv


REQUIRED_FIELDS = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际", "YEAR"]


def run(config_path: str = "config.json") -> dict[str, int]:
    config = load_config(config_path)
    fields, source_rows = read_csv(config["input_csv"])
    require_fields(fields, REQUIRED_FIELDS, config["input_csv"])

    expanded_rows: list[dict[str, str]] = []
    for line_number, row in enumerate(source_rows, start=2):
        if not row["DIMENSION-ID"]:
            raise ValueError(f"line {line_number}: DIMENSION-ID is required")
        expected_id = dimension_id(row)
        if row["DIMENSION-ID"] != expected_id:
            raise ValueError(f"line {line_number}: DIMENSION-ID does not match its component fields")
        if not row["MAKE"] or not row["MODEL"]:
            raise ValueError(f"line {line_number}: MAKE and MODEL are required")
        original_year = row["YEAR"]
        for year in expand_year(original_year):
            expanded = dict(row)
            expanded["YEAR"] = str(year)
            expanded["SOURCE_YEAR_RANGE"] = original_year
            expanded_rows.append(expanded)

    output_fields = fields + [
        field for field in ("SOURCE_YEAR_RANGE", "DATA_QUALITY_NOTES") if field not in fields
    ]
    write_csv(config["expanded_csv"], output_fields, expanded_rows)
    return {"source_rows": len(source_rows), "expanded_rows": len(expanded_rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand YEAR ranges into one row per calendar year.")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    stats = run(args.config)
    print(f"expanded {stats['source_rows']} source rows to {stats['expanded_rows']} rows")


if __name__ == "__main__":
    main()
