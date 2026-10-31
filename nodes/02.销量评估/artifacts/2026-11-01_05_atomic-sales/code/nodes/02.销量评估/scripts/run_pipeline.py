from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from common import PROJECT_ROOT, resolve_path, load_config
from artifact_batch import RunBatch

import build_atoms
import expand_years
import merge_results
import validate_sales
import export_final
import normalize_cache


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the complete vehicle sales preparation pipeline.")
    parser.add_argument("--config", default="data/config.json")
    args = parser.parse_args()

    with RunBatch.create(PROJECT_ROOT / "artifacts", "atomic-sales", data_dir=PROJECT_ROOT / "data") as batch:
        config = load_config(args.config)
        batch.input(resolve_path(config["input_csv"]))
        config["atom_sales_output_csv"] = str(batch.output("原子销量.csv"))
        with tempfile.TemporaryDirectory(prefix="sales-config-") as temp:
            config_path = Path(temp) / "config.json"
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
            normalized = normalize_cache.run(str(config_path))
            expanded = expand_years.run(str(config_path))
            atoms = build_atoms.run(str(config_path))
            merged = merge_results.run(str(config_path))
            validated = validate_sales.run(str(config_path))
            final = export_final.run(str(config_path))
        batch.finish(final, publish_to=PROJECT_ROOT / "output")
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
