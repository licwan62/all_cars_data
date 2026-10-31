"""Create a relabel-only W-car release that uses the new 4-series size names.

This does not rerun clustering, year merging or allocation.  It copies the
0915.3 artifact and renames the five generic W-size labels (including SKU name
suffixes, free-text details and the ``-0`` sports-car variants) in one pass, so
``4XXXXL -> 4XXL`` is never renamed again to ``4L``.  Custom sizes
(BEL-AIR-5357, CHALLENGER, MODEL-X) are kept.
"""

from __future__ import annotations

import csv
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
SOURCE = ROOT / "artifacts" / "0915.3-compact-plus-custom-skus"
TARGET = ROOT / "artifacts" / "0915.4-new-size-codes"
GLOBAL_MAPPING = REPO / "nodes" / "A0.尺码计算" / "data" / "参考" / "历史全域新旧尺码对应.csv"
MAPPING_OUTPUT = Path("00_输入") / "新旧尺码映射.csv"
SIZE_TOKEN = re.compile(rb"(?<![A-Za-z0-9-])4X{0,4}L(?![A-Za-z0-9])")
# global 文件老爷车行的“老尺码”为空，旧名→尺码代码按 A0 参考表 新旧尺码对应.csv 抄录于此，新名以 global 为准核对。
SIZE_RENAMES = {
    "4L": ("4S", "L0"),
    "4XL": ("4M", "L1"),
    "4XXL": ("4L", "L2"),
    "4XXXL": ("4XL", "L3"),
    "4XXXXL": ("4XXL", "L4"),
}


def check_global_mapping() -> None:
    with GLOBAL_MAPPING.open(encoding="utf-8-sig", newline="") as handle:
        new_by_code = {row["尺码代码"]: row["新尺码"] for row in csv.DictReader(handle) if row["分类"] == "老爷车"}
    for old, (new, code) in SIZE_RENAMES.items():
        if new_by_code.get(code) != new:
            raise ValueError(f"{old}: {code} 应为 {new}，global 为 {new_by_code.get(code)}")


def main() -> None:
    check_global_mapping()
    renames = SIZE_RENAMES
    if TARGET.exists():
        if "--replace" not in sys.argv:
            raise FileExistsError(f"refusing to overwrite existing artifact: {TARGET}")
        if TARGET.parent != ROOT / "artifacts" or TARGET.name != "0915.4-new-size-codes":
            raise RuntimeError(f"unexpected replacement target: {TARGET}")
        shutil.rmtree(TARGET)
    shutil.copytree(SOURCE, TARGET)
    by_bytes = {old.encode("ascii"): new.encode("ascii") for old, (new, _) in renames.items()}
    for path in TARGET.rglob("*"):
        if path.is_file():
            path.write_bytes(SIZE_TOKEN.sub(lambda match: by_bytes[match.group(0)], path.read_bytes()))
    with (TARGET / MAPPING_OUTPUT).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["老尺码", "新尺码", "尺码代码"])
        writer.writerows((old, new, code) for old, (new, code) in renames.items())
    print(TARGET)


if __name__ == "__main__":
    main()
