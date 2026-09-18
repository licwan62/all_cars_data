from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import Settings, load_settings
from src.exporter import (
    MAKE_FIELDS, MODEL_FIELDS, backup_mappings, create_artifact_batch, make_rows,
    model_rows, output_rows, read_make_mappings, read_model_mappings, write_csv_atomic,
)
from src.loader import load_vehicle_data
from src.make_mapper import aggregate_makes, update_make_mappings
from src.model_mapper import aggregate_models, update_model_mappings
from src.validator import validate_immutable, validate_make_mappings, validate_model_mappings


LOGGER = logging.getLogger(__name__)


def determine_mode(settings: Settings) -> str:
    make_exists = settings.make_mapping_path.exists()
    model_exists = settings.model_mapping_path.exists()
    if make_exists != model_exists:
        raise ValueError(
            "Mapping state is inconsistent. Both make_mapping.csv and model_mapping.csv must exist together."
        )
    return "UPDATE" if make_exists else "INITIAL"


def run(settings: Settings, dry_run: bool = False, publish: bool = False) -> dict[str, int | str]:
    mode = determine_mode(settings)
    records, input_rows = load_vehicle_data(
        settings.input_path, settings.encoding, settings.make_column,
        settings.model_column, settings.sales_column,
    )
    make_totals = aggregate_makes(records)
    model_totals = aggregate_models(records)
    old_makes = read_make_mappings(settings.make_mapping_path)
    old_models = read_model_mappings(settings.model_mapping_path)
    validate_make_mappings(old_makes, settings.code_width, settings.max_code)
    validate_model_mappings(old_models, old_makes, settings.code_width, settings.max_code)

    created_at = date.today().isoformat()
    new_makes, added_makes = update_make_mappings(
        make_totals, old_makes, created_at, settings.code_width, settings.max_code
    )
    new_models, added_models = update_model_mappings(
        model_totals, old_models, new_makes, created_at, settings.code_width, settings.max_code
    )
    validate_immutable(old_makes, new_makes, old_models, new_models)
    validate_make_mappings(new_makes, settings.code_width, settings.max_code)
    validate_model_mappings(new_models, new_makes, settings.code_width, settings.max_code)

    _print_report(mode, input_rows, make_totals, model_totals, old_makes, old_models, added_makes, added_models)
    if not dry_run:
        changed = make_rows(old_makes) != make_rows(new_makes) or model_rows(old_models) != model_rows(new_models)
        if changed and mode == "UPDATE" and settings.backup_enabled:
            backup_mappings(settings.make_mapping_path, settings.model_mapping_path, settings.backup_path)
        if changed or mode == "INITIAL":
            write_csv_atomic(settings.make_mapping_path, MAKE_FIELDS, make_rows(new_makes))
            write_csv_atomic(settings.model_mapping_path, MODEL_FIELDS, model_rows(new_models))
        artifact_path = create_artifact_batch(
            settings.artifact_root,
            settings.artifact_slug,
            new_makes,
            new_models,
            {
                "mode": mode,
                "input_rows": input_rows,
                "unique_makes": len(make_totals),
                "unique_make_models": len(model_totals),
                "existing_makes": len(old_makes),
                "new_makes": len(added_makes),
                "existing_models": len(old_models),
                "new_models": len(added_models),
                "published_path": str(settings.publish_path),
            },
            settings.input_path,
        )
        publish_fields = ["MAKE", "MODEL", "MAKE_CODE", "MODEL_CODE"]
        publish_rows = output_rows(new_models)
        write_csv_atomic(
            settings.publish_path,
            publish_fields,
            publish_rows,
        )
        print(f"Artifact created: {artifact_path}")
        print(f"Published: {settings.publish_path}")
        if publish:
            write_csv_atomic(settings.public_publish_path, publish_fields, publish_rows)
            print(f"Published (public): {settings.public_publish_path}")
        print("Mapping update completed successfully.")
    else:
        print("Dry run completed successfully. No files were modified.")
    return {
        "mode": mode, "input_rows": input_rows, "unique_makes": len(make_totals),
        "unique_models": len(model_totals), "new_makes": len(added_makes),
        "new_models": len(added_models),
    }


def report(settings: Settings) -> None:
    mode = determine_mode(settings)
    if mode == "INITIAL":
        print("No mapping files exist yet.")
        return
    makes = read_make_mappings(settings.make_mapping_path)
    models = read_model_mappings(settings.model_mapping_path)
    validate_make_mappings(makes, settings.code_width, settings.max_code)
    validate_model_mappings(models, makes, settings.code_width, settings.max_code)
    print(f"MAKE mappings: {len(makes)} ({sum(x.status == 'ACTIVE' for x in makes)} ACTIVE)")
    print(f"MODEL mappings: {len(models)} ({sum(x.status == 'ACTIVE' for x in models)} ACTIVE)")


def _print_report(mode, input_rows, make_totals, model_totals, old_makes, old_models, added_makes, added_models):
    print(f"Mode: {mode}")
    print(f"Input rows: {input_rows:,}")
    print(f"Unique MAKE: {len(make_totals):,}")
    print(f"Unique MAKE/MODEL: {len(model_totals):,}")
    print(f"Existing MAKE: {len(old_makes):,}")
    print(f"New MAKE: {len(added_makes):,}")
    print(f"Existing MODEL: {len(old_models):,}")
    print(f"New MODEL: {len(added_models):,}")
    if added_makes:
        print("\nNEW MAKE")
        for item in added_makes:
            print(f"{item.make_code} {item.make}")
    if added_models:
        print("\nNEW MODEL")
        current_make = None
        for item in sorted(added_models, key=lambda x: (int(x.make_code), int(x.model_code))):
            if item.make != current_make:
                print(f"\n{item.make}")
                current_make = item.make
            print(f"{item.model_code} {item.model}")


def parse_args(argv: list[str] | None = None):
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Persistent MAKE/MODEL code mapper")
    parser.add_argument("--config", default=str(project_root / "config.yaml"))
    parser.add_argument("--input", help="Temporarily override the configured full-data CSV")
    parser.add_argument("--dry-run", action="store_true", help="Validate and preview without writing files")
    parser.add_argument(
        "--publish", action="store_true", help="Also write the published mapping to the public_publish path"
    )
    parser.add_argument("--report", action="store_true", help="Show current mapping statistics only")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args(argv)
    try:
        settings = load_settings(args.config)
        if args.input:
            settings = replace(settings, input_path=Path(args.input).resolve())
        if args.report:
            report(settings)
        else:
            run(settings, dry_run=args.dry_run, publish=args.publish)
        return 0
    except (OSError, ValueError) as exc:
        LOGGER.error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
