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


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def load_settings(config_path: str | Path) -> Settings:
    config_file = Path(config_path).resolve()
    with config_file.open("r", encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle) or {}
    base = config_file.parent
    try:
        return Settings(
            project_root=base,
            input_path=_resolve(base, raw["input"]["path"]),
            encoding=str(raw["input"].get("encoding", "utf-8-sig")),
            make_column=str(raw["columns"]["make"]),
            model_column=str(raw["columns"]["model"]),
            sales_column=str(raw["columns"]["sales"]),
            code_width=int(raw["code"].get("width", 2)),
            max_code=int(raw["code"].get("max_value", 99)),
            make_mapping_path=_resolve(base, raw["mapping"]["make_path"]),
            model_mapping_path=_resolve(base, raw["mapping"]["model_path"]),
            artifact_root=_resolve(base, raw["artifacts"]["path"]),
            artifact_slug=str(raw["artifacts"].get("slug", "code-mapping-publish")),
            publish_path=_resolve(base, raw["publish"]["path"]),
            public_publish_path=_resolve(
                base, raw.get("public_publish", {}).get("path", "../public/car_code/vehicle_mapping.csv")
            ),
            backup_enabled=bool(raw.get("backup", {}).get("enabled", True)),
            backup_path=_resolve(base, raw.get("backup", {}).get("path", "data/mapping/backups")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid configuration in {config_file}: {exc}") from exc
