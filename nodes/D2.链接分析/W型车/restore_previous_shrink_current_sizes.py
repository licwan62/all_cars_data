"""Create a relabel-only W-car release from the last compact artifact.

This deliberately does not rerun clustering, year merging, allocation, or input
selection.  It retains the 0914.4 compact artifact byte-for-byte except for the
five generic W-size labels, which are renamed to the current 4-series labels.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "artifacts" / "0914.4-custom-sales-weight-900"
TARGET = ROOT / "artifacts" / "0915.2-previous-shrink-current-sizes"
SIZE_RENAMES = {
    "3XXL-W": "4XXL",
    "3XXXXL": "4XXXXL",
    "3XXXL": "4XXXL",
    "3XL-W": "4XL",
    "3L-W": "4L",
}


def main() -> None:
    if TARGET.exists():
        if "--replace" not in sys.argv:
            raise FileExistsError(f"refusing to overwrite existing artifact: {TARGET}")
        if TARGET.parent != ROOT / "artifacts" or TARGET.name != "0915.2-previous-shrink-current-sizes":
            raise RuntimeError(f"unexpected replacement target: {TARGET}")
        shutil.rmtree(TARGET)
    shutil.copytree(SOURCE, TARGET)
    for path in TARGET.rglob("*"):
        if not path.is_file():
            continue
        content = path.read_bytes()
        for old, new in SIZE_RENAMES.items():
            content = content.replace(old.encode("ascii"), new.encode("ascii"))
        path.write_bytes(content)
    print(TARGET)


if __name__ == "__main__":
    main()
