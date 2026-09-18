from __future__ import annotations

import argparse
from collections import Counter

from common import (
    CACHE_FIELDS,
    OVERRIDE_FIELDS,
    ensure_csv_template,
    load_config,
    model_year_key,
    read_csv,
    require_fields,
    sales_atom_key,
    make_atom_record_id,
    write_csv,
)


REQUIRED_FIELDS = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "YEAR"]


def run(config_path: str = "config.json") -> dict[str, int]:
    config = load_config(config_path)
    fields, rows = read_csv(config["expanded_csv"])
    require_fields(fields, REQUIRED_FIELDS, config["expanded_csv"])

    atoms: list[dict[str, str]] = []
    key_counts: Counter[str] = Counter()
    for row in rows:
        atom = dict(row)
        atom["SALES_ATOM_KEY"] = sales_atom_key(row)
        atom["ATOM_ROW_ID"] = make_atom_record_id(row["DIMENSION-ID"], row["YEAR"])
        key_counts[atom["SALES_ATOM_KEY"]] += 1
        atoms.append(atom)

    atom_fields = fields + [field for field in ("SALES_ATOM_KEY", "ATOM_ROW_ID") if field not in fields]
    write_csv(config["atoms_csv"], atom_fields, atoms)

    duplicates = [
        {
            "SALES_ATOM_KEY": key,
            "DUPLICATE_COUNT": count,
            "ATOM_ROW_IDS": ";".join(atom["ATOM_ROW_ID"] for atom in atoms if atom["SALES_ATOM_KEY"] == key),
            "STATUS": "REVIEW",
        }
        for key, count in sorted(key_counts.items())
        if count > 1
    ]
    write_csv(
        config["duplicate_report_csv"],
        ["SALES_ATOM_KEY", "DUPLICATE_COUNT", "ATOM_ROW_IDS", "STATUS"],
        duplicates,
    )

    ensure_csv_template(config["model_year_cache_csv"], CACHE_FIELDS)
    ensure_csv_template(config["allocation_overrides_csv"], OVERRIDE_FIELDS)
    _, cache_rows = read_csv(config["model_year_cache_csv"])
    allowed_scopes = {scope.upper() for scope in config.get("allowed_us_scopes", ["", "US", "USA"])}
    cached = {
        model_year_key(row)
        for row in cache_rows
        if row.get("MODEL_YEAR_US_SALES", "").strip()
        and row.get("SALES_SCOPE", "").strip().upper() in allowed_scopes
    }

    queue = []
    for make, model, year in sorted({model_year_key(atom) for atom in atoms}):
        queue.append(
            {
                "MAKE": make,
                "MODEL": model,
                "YEAR": year,
                "CACHE_STATUS": "READY" if (make, model, year) in cached else "PENDING",
                "SEARCH_QUERY": f'"{year} {make} {model} US sales"',
            }
        )
    write_csv(
        config["research_queue_csv"],
        ["MAKE", "MODEL", "YEAR", "CACHE_STATUS", "SEARCH_QUERY"],
        queue,
    )
    return {
        "atom_rows": len(atoms),
        "model_years": len(queue),
        "duplicate_atom_keys": len(duplicates),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sales atom keys and a deduplicated research queue.")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    stats = run(args.config)
    print(
        f"built {stats['atom_rows']} atom rows and {stats['model_years']} model-year tasks; "
        f"{stats['duplicate_atom_keys']} semantic atom keys need review"
    )


if __name__ == "__main__":
    main()
