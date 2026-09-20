from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import Settings, load_settings, region_names
from src.dimension_code import DIMENSION_CODE_FIELDS, dimension_code_rows, duplicate_code_count
from src.exporter import (
    MAKE_FIELDS, MODEL_FIELDS, backup_mappings, create_artifact_batch, create_multi_artifact_batch, make_rows,
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


@dataclass
class Plan:
    settings: Settings
    mode: str
    records: list
    input_rows: int
    make_totals: list
    model_totals: list
    old_makes: list
    old_models: list
    new_makes: list
    new_models: list
    added_makes: list
    added_models: list

    def changed(self) -> bool:
        return make_rows(self.old_makes) != make_rows(self.new_makes) or model_rows(self.old_models) != model_rows(
            self.new_models
        )

    def summary(self) -> dict[str, int | str]:
        return {
            "mode": self.mode, "input_rows": self.input_rows, "unique_makes": len(self.make_totals),
            "unique_models": len(self.model_totals), "new_makes": len(self.added_makes),
            "new_models": len(self.added_models),
        }


def plan_region(settings: Settings) -> Plan:
    """计算并校验某个区域的映射更新，不写任何文件。"""
    mode = determine_mode(settings)
    records, input_rows = load_vehicle_data(
        settings.input_path, settings.encoding, settings.make_column,
        settings.model_column, settings.sales_column,
        settings.dimension_id_column, settings.year_column, settings.region_suffix,
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
    return Plan(
        settings, mode, records, input_rows, make_totals, model_totals,
        old_makes, old_models, new_makes, new_models, added_makes, added_models,
    )


def apply_region(plan: Plan) -> None:
    """把已校验的计划写入该区域的持久映射（变更前备份）。"""
    settings = plan.settings
    if plan.changed() and plan.mode == "UPDATE" and settings.backup_enabled:
        backup_mappings(settings.make_mapping_path, settings.model_mapping_path, settings.backup_path)
    if plan.changed() or plan.mode == "INITIAL":
        write_csv_atomic(settings.make_mapping_path, MAKE_FIELDS, make_rows(plan.new_makes))
        write_csv_atomic(settings.model_mapping_path, MODEL_FIELDS, model_rows(plan.new_models))


VEHICLE_FIELDS = ["MAKE", "MODEL", "MAKE_CODE", "MODEL_CODE"]


def run(settings: Settings, dry_run: bool = False, publish: bool = False) -> dict[str, int | str]:
    """单区域运行（区域参数由 settings 决定）。"""
    plan = plan_region(settings)
    _print_report(
        plan.mode, plan.input_rows, plan.make_totals, plan.model_totals,
        plan.old_makes, plan.old_models, plan.added_makes, plan.added_models,
    )
    if dry_run:
        print("Dry run completed successfully. No files were modified.")
        return plan.summary()
    apply_region(plan)
    artifact_path = create_artifact_batch(
        settings.artifact_root, settings.artifact_slug, plan.new_makes, plan.new_models,
        {**plan.summary(), "existing_makes": len(plan.old_makes), "existing_models": len(plan.old_models),
         "published_path": str(settings.publish_path)},
        settings.input_path,
    )
    publish_rows = output_rows(plan.new_models)
    write_csv_atomic(settings.publish_path, VEHICLE_FIELDS, publish_rows)
    if settings.dimension_code_path is not None:
        code_rows = dimension_code_rows(plan.records, plan.new_models, settings.code_prefix)
        write_csv_atomic(settings.dimension_code_path, DIMENSION_CODE_FIELDS, code_rows)
    print(f"Artifact created: {artifact_path}")
    print(f"Published: {settings.publish_path}")
    if publish:
        write_csv_atomic(settings.public_publish_path, VEHICLE_FIELDS, publish_rows)
        print(f"Published (public): {settings.public_publish_path}")
    print("Mapping update completed successfully.")
    return plan.summary()


def run_all(config_path, input_override=None, dry_run=False, publish=False) -> dict[str, dict]:
    """US/EU/RU 各自独立编码，共用一个 artifact 批次与两份合并交付物。

    交付物：output/车型编码映射.csv（REGION + MAKE/MODEL 编码）、
    output/尺寸编码映射.csv（DIMENSION-ID -> DIMENSION-CODE）。
    """
    plans: list[Plan] = []
    for name in region_names(config_path):
        settings = load_settings(config_path, name)
        if input_override:
            settings = replace(settings, input_path=input_override)
        plan = plan_region(settings)
        print(f"== {name}")
        _print_report(
            plan.mode, plan.input_rows, plan.make_totals, plan.model_totals,
            plan.old_makes, plan.old_models, plan.added_makes, plan.added_models,
        )
        plans.append(plan)

    vehicle_rows: list[dict[str, str]] = []
    code_rows: list[dict[str, str]] = []
    for plan in plans:
        vehicle_rows += [{"REGION": plan.settings.region, **row} for row in output_rows(plan.new_models)]
        code_rows += dimension_code_rows(plan.records, plan.new_models, plan.settings.code_prefix)
    code_rows.sort(key=lambda row: row["DIMENSION-ID"])
    ids = [row["DIMENSION-ID"] for row in code_rows]
    if len(ids) != len(set(ids)):
        raise ValueError("DIMENSION-ID is not unique across regions; refusing to publish.")
    duplicates = duplicate_code_count(code_rows)
    summary = {plan.settings.region: plan.summary() for plan in plans}
    print(f"DIMENSION-CODE rows: {len(code_rows):,}; rows sharing a code with another row: {duplicates:,}")
    if dry_run:
        print("Dry run completed successfully. No files were modified.")
        return summary

    base = plans[0].settings
    for plan in plans:
        apply_region(plan)
    artifact_path = create_multi_artifact_batch(
        base.artifact_root, base.artifact_slug,
        {plan.settings.region: (plan.new_makes, plan.new_models) for plan in plans},
        {"车型编码映射.csv": (["REGION", *VEHICLE_FIELDS], vehicle_rows),
         "尺寸编码映射.csv": (DIMENSION_CODE_FIELDS, code_rows)},
        {"regions": summary, "dimension_code_rows": len(code_rows), "shared_code_rows": duplicates},
        base.input_path,
    )
    write_csv_atomic(base.publish_path, ["REGION", *VEHICLE_FIELDS], vehicle_rows)
    write_csv_atomic(base.dimension_code_path, DIMENSION_CODE_FIELDS, code_rows)
    print(f"Artifact created: {artifact_path}")
    print(f"Published: {base.publish_path}")
    print(f"Published: {base.dimension_code_path}")
    if publish:
        write_csv_atomic(base.public_publish_path, ["REGION", *VEHICLE_FIELDS], vehicle_rows)
    print("Mapping update completed successfully.")
    return summary


def report(settings: Settings) -> None:
    print(f"[{settings.region or 'default'}]")
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
    parser.add_argument("--region", help="仅运行单个区域（US/EU/RU），不合并交付物，仅调试用")
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
            for name in region_names(args.config):
                report(load_settings(args.config, name))
        elif args.region:
            regional = load_settings(args.config, args.region)
            if args.input:
                regional = replace(regional, input_path=Path(args.input).resolve())
            run(regional, dry_run=args.dry_run, publish=args.publish)
        else:
            run_all(args.config, Path(args.input).resolve() if args.input else None,
                    dry_run=args.dry_run, publish=args.publish)
        return 0
    except (OSError, ValueError) as exc:
        LOGGER.error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
