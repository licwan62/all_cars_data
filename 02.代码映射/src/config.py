from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Settings:
    project_root: Path
    input_path: Path
    encoding: str
    make_column: str
    model_column: str
    sales_column: str
    code_width: int
    max_code: int
    make_mapping_path: Path
    model_mapping_path: Path
    artifact_root: Path
    artifact_slug: str
    publish_path: Path
    public_publish_path: Path
    backup_enabled: bool
    backup_path: Path
    region: str = ""
    region_suffix: str = ""
    code_prefix: str = ""
    dimension_id_column: str = ""
    year_column: str = ""
    dimension_code_path: Path | None = None


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def region_names(config_path: str | Path) -> list[str]:
    with Path(config_path).open("r", encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle) or {}
    return [str(item["name"]).upper() for item in raw.get("regions", [])]


def load_settings(config_path: str | Path, region: str | None = None) -> Settings:
    config_file = Path(config_path).resolve()
    with config_file.open("r", encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle) or {}
    base = config_file.parent
    try:
        region_raw: dict[str, Any] = {}
        if region:
            region_raw = next(
                (item for item in raw.get("regions", []) if str(item["name"]).upper() == region.upper()), None
            )
            if region_raw is None:
                raise KeyError(f"unknown region {region}")
        width = int(region_raw.get("width", raw["code"].get("width", 2)))
        mapping_dir = region_raw.get("mapping_dir")
        make_path = f"{mapping_dir}/make_mapping.csv" if mapping_dir else raw["mapping"]["make_path"]
        model_path = f"{mapping_dir}/model_mapping.csv" if mapping_dir else raw["mapping"]["model_path"]
        backup_path = f"{mapping_dir}/backups" if mapping_dir else raw.get("backup", {}).get("path", "data/mapping/backups")
        dimension_code_path = raw["publish"].get("dimension_code_path")
        return Settings(
            project_root=base,
            input_path=_resolve(base, raw["input"]["path"]),
            encoding=str(raw["input"].get("encoding", "utf-8-sig")),
            make_column=str(raw["columns"]["make"]),
            model_column=str(raw["columns"]["model"]),
            sales_column=str(raw["columns"].get("sales") or ""),
            code_width=width,
            max_code=10**width - 1 if region else int(raw["code"].get("max_value", 99)),
            make_mapping_path=_resolve(base, make_path),
            model_mapping_path=_resolve(base, model_path),
            artifact_root=_resolve(base, raw["artifacts"]["path"]),
            artifact_slug=str(raw["artifacts"].get("slug", "code-mapping-publish")),
            publish_path=_resolve(base, raw["publish"]["path"]),
            public_publish_path=_resolve(
                base, raw.get("public_publish", {}).get("path", "../public/car_code/vehicle_mapping.csv")
            ),
            backup_enabled=bool(raw.get("backup", {}).get("enabled", True)),
            backup_path=_resolve(base, backup_path),
            region=str(region_raw.get("name", "")).upper(),
            region_suffix=f" {str(region_raw['name']).upper()}" if region else "",
            code_prefix=str(region_raw.get("prefix", "")),
            dimension_id_column=str(raw["columns"].get("dimension_id") or ""),
            year_column=str(raw["columns"].get("year") or ""),
            dimension_code_path=_resolve(base, dimension_code_path) if dimension_code_path else None,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid configuration in {config_file}: {exc}") from exc
