from __future__ import annotations

import argparse
from collections import defaultdict

from common import load_config, read_csv, require_fields, write_csv


FINAL_FIELDS = ["atom_record_id", "预估销量"]


def run(config_path: str = "config.json") -> dict[str, int]:
    config = load_config(config_path)
    fields, rows = read_csv(config["atomic_output_csv"])
    require_fields(fields, ["ATOM_ROW_ID", "US_SALES_ESTIMATE"], config["atomic_output_csv"])

    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[row["ATOM_ROW_ID"]].append(row["US_SALES_ESTIMATE"])
    output = []
    for atom_id in sorted(grouped):
        estimates = grouped[atom_id]
        output.append({
            "atom_record_id": atom_id,
            "预估销量": str(sum(int(value) for value in estimates)) if all(value != "" for value in estimates) else "",
        })
    atom_ids = [row["atom_record_id"] for row in output]
    if any(not atom_id for atom_id in atom_ids):
        raise ValueError("final atom sales contains a blank atom_record_id")
    if len(atom_ids) != len(set(atom_ids)):
        raise ValueError("final atom sales contains duplicate atom_record_id values")

    write_csv(config["atom_sales_output_csv"], FINAL_FIELDS, output)
    return {
        "atom_rows": len(output),
        "estimated_rows": sum(bool(row["预估销量"]) for row in output),
        "pending_rows": sum(not row["预估销量"] for row in output),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export atom_record_id to estimated US sales.")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    stats = run(args.config)
    print(
        f"wrote {stats['atom_rows']} atom sales rows; "
        f"{stats['estimated_rows']} estimated and {stats['pending_rows']} pending"
    )


if __name__ == "__main__":
    main()
