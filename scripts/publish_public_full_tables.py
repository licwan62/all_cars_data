"""Publish the current stable full tables to the public exchange directory.

This intentionally reads only pipeline `output/` files and swaps a staged
directory into the NAS public `data/full_tables` after hashes and row counts verify.
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
PUBLIC_ROOT = Path(r"\\NAS8824B4\Public\PQData\pub_all_cars_data")
PUBLIC_DATA = PUBLIC_ROOT / "data"
TARGET = PUBLIC_DATA / "full_tables"
FILES = {
    "全量表_US.csv": ROOT / "A0.尺码计算" / "output" / "全量表_US.csv",
    "全量表_EU.csv": ROOT / "A0.尺码计算" / "output" / "全量表_EU.csv",
    "全量表_RU.csv": ROOT / "A0.尺码计算" / "output" / "全量表_RU.csv",
    "全量表_汇总.csv": ROOT / "A1.全量生成" / "output" / "全量表_汇总.csv",
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
