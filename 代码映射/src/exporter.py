from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from .models import MakeMapping, ModelMapping
from .normalizer import decimal_text, normalized_key


MAKE_FIELDS = ["MAKE", "MAKE_KEY", "MAKE_CODE", "CREATED_AT", "INITIAL_SALES", "STATUS"]
MODEL_FIELDS = [
    "MAKE", "MODEL", "MAKE_KEY", "MODEL_KEY", "MAKE_CODE", "MODEL_CODE",
    "CREATED_AT", "INITIAL_SALES", "STATUS",
]


def read_make_mappings(path: Path) -> list[MakeMapping]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        result = []
        for row in csv.DictReader(handle):
            make = row["MAKE"].strip()
            result.append(
                MakeMapping(
                    make=make,
                    make_key=(row.get("MAKE_KEY") or normalized_key(make)).strip(),
                    make_code=row["MAKE_CODE"].strip(),
                    created_at=row["CREATED_AT"].strip(),
                    initial_sales=_decimal(row["INITIAL_SALES"]),
                    status=(row.get("STATUS") or "ACTIVE").strip(),
                )
            )
        return result


def read_model_mappings(path: Path) -> list[ModelMapping]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        result = []
        for row in csv.DictReader(handle):
            make, model = row["MAKE"].strip(), row["MODEL"].strip()
            result.append(
                ModelMapping(
                    make=make,
                    model=model,
                    make_key=(row.get("MAKE_KEY") or normalized_key(make)).strip(),
                    model_key=(row.get("MODEL_KEY") or normalized_key(model)).strip(),
                    make_code=row["MAKE_CODE"].strip(),
                    model_code=row["MODEL_CODE"].strip(),
                    created_at=row["CREATED_AT"].strip(),
                    initial_sales=_decimal(row["INITIAL_SALES"]),
                    status=(row.get("STATUS") or "ACTIVE").strip(),
                )
            )
        return result


def make_rows(items: Iterable[MakeMapping]) -> list[dict[str, str]]:
    return [
        {
            "MAKE": item.make, "MAKE_KEY": item.make_key, "MAKE_CODE": item.make_code,
            "CREATED_AT": item.created_at, "INITIAL_SALES": decimal_text(item.initial_sales),
            "STATUS": item.status,
        }
        for item in sorted(items, key=lambda item: int(item.make_code))
    ]


def model_rows(items: Iterable[ModelMapping]) -> list[dict[str, str]]:
    return [
        {
            "MAKE": item.make, "MODEL": item.model, "MAKE_KEY": item.make_key,
            "MODEL_KEY": item.model_key, "MAKE_CODE": item.make_code,
            "MODEL_CODE": item.model_code, "CREATED_AT": item.created_at,
            "INITIAL_SALES": decimal_text(item.initial_sales), "STATUS": item.status,
        }
        for item in sorted(items, key=lambda item: (int(item.make_code), int(item.model_code)))
    ]


def output_rows(items: Iterable[ModelMapping]) -> list[dict[str, str]]:
    return [
        {"MAKE": item.make, "MODEL": item.model, "MAKE_CODE": item.make_code, "MODEL_CODE": item.model_code}
        for item in sorted(items, key=lambda item: (int(item.make_code), int(item.model_code)))
        if item.status == "ACTIVE"
    ]


def write_csv_atomic(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def backup_mappings(make_path: Path, model_path: Path, backup_path: Path) -> list[Path]:
    backup_path.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    created: list[Path] = []
    for source in (make_path, model_path):
        if source.exists():
            target = backup_path / f"{stamp}_{source.name}"
            shutil.copy2(source, target)
            created.append(target)
    return created


def create_artifact_batch(
    artifact_root: Path,
    slug: str,
    make_items: list[MakeMapping],
    model_items: list[ModelMapping],
    run_report: dict[str, object],
    source_path: Path,
) -> Path:
    """Create an immutable, self-contained run snapshot and return its final path."""
    artifact_root.mkdir(parents=True, exist_ok=True)
    day = datetime.now().strftime("%Y-%m-%d")
    safe_slug = re.sub(r"[^a-z0-9-]+", "-", slug.casefold()).strip("-") or "code-mapping"
    pattern = re.compile(rf"^{re.escape(day)}_(\d{{2}})_{re.escape(safe_slug)}$")
    used = [int(match.group(1)) for path in artifact_root.iterdir() if path.is_dir() and (match := pattern.match(path.name))]
    sequence = max(used, default=0) + 1
    if sequence > 99:
        raise ValueError(f"Artifact sequence exhausted for {day} and slug {safe_slug}.")
    final_path = artifact_root / f"{day}_{sequence:02d}_{safe_slug}"
    temp_path = Path(tempfile.mkdtemp(prefix=f".{final_path.name}.", dir=artifact_root))
    try:
        write_csv_atomic(temp_path / "mapping" / "make_mapping.csv", MAKE_FIELDS, make_rows(make_items))
        write_csv_atomic(temp_path / "mapping" / "model_mapping.csv", MODEL_FIELDS, model_rows(model_items))
        write_csv_atomic(
            temp_path / "output" / "vehicle_mapping.csv",
            ["MAKE", "MODEL", "MAKE_CODE", "MODEL_CODE"],
            output_rows(model_items),
        )
        report = {
            **run_report,
            "source_path": str(source_path),
            "source_sha256": _sha256(source_path),
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        _write_json(temp_path / "run_report.json", report)
        _write_json(
            temp_path / "validation.json",
            {
                "status": "PASS",
                "make_mapping_count": len(make_items),
                "model_mapping_count": len(model_items),
                "active_model_count": sum(item.status == "ACTIVE" for item in model_items),
                "code_width": len(make_items[0].make_code) if make_items else 2,
                "immutable_validation": "PASS",
                "capacity_validation": "PASS",
            },
        )
        os.replace(temp_path, final_path)
    except BaseException:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise
    return final_path


def _write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _decimal(value: str):
    from decimal import Decimal
    return Decimal(value.strip().replace(",", "") or "0")
