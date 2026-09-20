"""Publish the current stable full tables to the public exchange directory.

This intentionally reads only pipeline `output/` files and swaps a staged
directory into `public/data/full_tables` after hashes and row counts verify.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA = ROOT / "public" / "data"
TARGET = PUBLIC_DATA / "full_tables"
FILES = {
    "全量表_US.csv": ROOT / "A0.尺码计算" / "output" / "全量表_US.csv",
    "全量表_EU.csv": ROOT / "A0.尺码计算" / "output" / "全量表_EU.csv",
    "全量表_RU.csv": ROOT / "A0.尺码计算" / "output" / "全量表_RU.csv",
    "全量表_汇总.csv": ROOT / "A1.全量汇总" / "output" / "全量表_汇总.csv",
    "尺码匹配报告_US.json": ROOT / "A0.尺码计算" / "output" / "尺码匹配报告_US.json",
    "尺码匹配报告_EU.json": ROOT / "A0.尺码计算" / "output" / "尺码匹配报告_EU.json",
    "尺码匹配报告_RU.json": ROOT / "A0.尺码计算" / "output" / "尺码匹配报告_RU.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> None:
    missing = [str(source) for source in FILES.values() if not source.is_file()]
    if missing:
        raise SystemExit("Missing stable pipeline output(s):\n" + "\n".join(missing))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stage = PUBLIC_DATA / f".full_tables.stage-{stamp}"
    if stage.exists():
        raise SystemExit(f"Staging path already exists: {stage}")
    stage.mkdir(parents=True)

    try:
        entries: list[dict[str, object]] = []
        for name, source in FILES.items():
            destination = stage / name
            shutil.copy2(source, destination)
            source_hash = sha256(source)
            if sha256(destination) != source_hash:
                raise RuntimeError(f"Hash verification failed for {name}")
            entry: dict[str, object] = {
                "file": name,
                "sha256": source_hash,
                "bytes": destination.stat().st_size,
            }
            if source.suffix.lower() == ".csv":
                entry["rows"] = csv_rows(destination)
            entries.append(entry)

        manifest = {
            "schema_version": 1,
            "published_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "purpose": "public exchange snapshot of current stable full tables",
            "upstream_releases": {
                "A0.尺码计算": "20260921_10",
                "A1.全量汇总": "20260921_07",
            },
            "files": entries,
            "regional_methodology": {
                "US": "Published atomic-sales based full table.",
                "EU": "Coverage-first full table; sales are zero placeholders and shapes include lenient candidates pending quality research.",
                "RU": "Coverage-first full table; sales use Auto.ru listing-sample proxies and shapes include lenient candidates pending quality research.",
            },
        }
        (stage / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        backup = None
        if TARGET.exists():
            backup = PUBLIC_DATA / f"full_tables.previous-{stamp}"
            os.replace(TARGET, backup)
        try:
            os.replace(stage, TARGET)
        except Exception:
            if backup is not None and backup.exists():
                os.replace(backup, TARGET)
            raise

        print(json.dumps({"published": str(TARGET), "backup": str(backup) if backup else None, "files": entries}, ensure_ascii=False))
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


if __name__ == "__main__":
    main()
