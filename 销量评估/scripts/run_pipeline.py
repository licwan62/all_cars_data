from __future__ import annotations

import argparse

import build_atoms
import expand_years
import merge_results
import validate_sales
import export_final
import normalize_cache


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the complete vehicle sales preparation pipeline.")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()

    normalized = normalize_cache.run(args.config)
    expanded = expand_years.run(args.config)
    atoms = build_atoms.run(args.config)
    merged = merge_results.run(args.config)
    validated = validate_sales.run(args.config)
    final = export_final.run(args.config)
    print(
        "pipeline complete: "
        f"{normalized['rows']} cache rows normalized, "
        f"{expanded['expanded_rows']} expanded rows, "
        f"{atoms['model_years']} model-year tasks, "
        f"{merged['ready_groups']} allocated, "
        f"{validated['pending']} pending, "
        f"{validated['fail']} failed, "
        f"{final['atom_rows']} final atom sales rows"
    )


if __name__ == "__main__":
    main()
