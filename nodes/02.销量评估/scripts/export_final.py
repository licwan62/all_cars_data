from __future__ import annotations

import argparse
from collections import defaultdict

from common import load_config, read_csv, require_fields, write_csv


FINAL_FIELDS = ["atom_record_id", "预估销量"]
PENDING_FIELDS = ["atom_record_id", "MAKE", "MODEL", "YEAR", "状态", "待核原因", "SOURCE_URL"]


def run(config_path: str = "data/config.json") -> dict[str, int]:
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
    pending_path = config.get("pending_sales_review_csv")
    if pending_path:
        pending = [{
            "atom_record_id": row["ATOM_ROW_ID"], "MAKE": row["MAKE"], "MODEL": row["MODEL"],
            "YEAR": row["YEAR"], "状态": "PENDING", "待核原因": row.get("NOTES", ""),
            "SOURCE_URL": row.get("SOURCE_URL", ""),
        } for row in rows if row.get("ITERATION_STATUS") == "PENDING"]
        write_csv(pending_path, PENDING_FIELDS, pending)
    return {
        "atom_rows": len(output),
        "estimated_rows": sum(bool(row["预估销量"]) for row in output),
        "pending_rows": sum(not row["预估销量"] for row in output),
        "pending_review_rows": sum(row.get("ITERATION_STATUS") == "PENDING" for row in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export atom_record_id to estimated US sales.")
    parser.add_argument("--config", default="data/config.json")
    args = parser.parse_args()
    stats = run(args.config)
    print(
        f"wrote {stats['atom_rows']} atom sales rows; "
        f"{stats['estimated_rows']} estimated and {stats['pending_rows']} pending"
    )


if __name__ == "__main__":
    main()
