"""Add the approved Challenger and Model X custom SKUs to the compact W release."""

from __future__ import annotations

import csv
import math
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "artifacts"
BASE = ROOT / "0915.2-previous-shrink-current-sizes"
CUSTOM = ROOT / "0915.1-tolerance-550"
TARGET = ROOT / "0915.3-compact-plus-custom-skus"
CUSTOM_SIZES = {"CHALLENGER", "MODEL-X"}
MULTIPLIERS = {"CHALLENGER": 5.0, "MODEL-X": 5.0}
SUPPLY = 801


def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle)), csv.DictReader


def load(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames


def save(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def custom_rows(relative: Path):
    rows, _ = load(CUSTOM / relative)
    return [row for row in rows if row.get("逻辑尺码") in CUSTOM_SIZES or row.get("尺码") in CUSTOM_SIZES or row.get("发货逻辑尺码") in CUSTOM_SIZES]


def main():
    if TARGET.exists():
        raise FileExistsError(TARGET)
    shutil.copytree(BASE, TARGET)
    master_rel = Path("02_聚类数据/聚类主表.csv")
    master, master_fields = load(TARGET / master_rel)
    special_master = custom_rows(master_rel)
    assert len(special_master) == 2
    rows = master + special_master
    weighted_total = sum(float(row["预估销量"]) * MULTIPLIERS.get(row["逻辑尺码"], 1.0) for row in rows)
    units = SUPPLY // 3
    work = []
    for row in rows:
        multiplier = MULTIPLIERS.get(row["逻辑尺码"], 1.0)
        weighted = float(row["预估销量"]) * multiplier
        exact = weighted * units / weighted_total
        base = math.floor(exact)
        work.append((row, multiplier, weighted, exact, base, exact - base))
    remainder = units - sum(item[4] for item in work)
    bonus = {id(item[0]) for item in sorted(work, key=lambda item: (-item[5], item[0]["聚类ID"]))[:remainder]}
    for row, multiplier, weighted, exact, base, _ in work:
        shipped = 3 * (base + (id(row) in bonus))
        row.update({"销量倍率": str(multiplier), "加权销量": f"{weighted:.1f}", "全局销量占比": f"{weighted / weighted_total:.6%}", "理论发货量": f"{weighted * SUPPLY / weighted_total:.6f}", "发货数量": str(shipped), "取整补量": str(shipped - 3 * base), "是否发货": "是" if shipped else "否"})
    save(TARGET / master_rel, master_fields, rows)

    old_listing, listing_fields = load(TARGET / "05_输出/链接发货适配表.csv")
    special_listing = custom_rows(Path("05_输出/链接发货适配表.csv"))
    allocation = {row["聚类ID"]: row for row in rows}
    listing = [row for row in old_listing + special_listing if int(allocation[row["CLUSTER_ID"]]["发货数量"]) > 0]
    for row in listing:
        source = allocation[row["CLUSTER_ID"]]
        row.update({"销量倍率": source["销量倍率"], "加权销量": source["加权销量"], "销量占比": source["全局销量占比"], "发货数量": source["发货数量"]})
    save(TARGET / "05_输出/链接发货适配表.csv", listing_fields, listing)

    grouped = defaultdict(lambda: {"clusters": 0, "sales": 0, "weighted": 0.0, "shipped": 0})
    for row in rows:
        item = grouped[row["逻辑尺码"]]; item["clusters"] += 1; item["sales"] += int(row["预估销量"]); item["weighted"] += float(row["加权销量"]); item["shipped"] += int(row["发货数量"])
    summary_fields = ["最终发货尺码", "聚类数量", "预估销量", "销量倍率", "加权销量", "销量占比", "发货数量", "发货占比"]
    summary = []
    for size, item in grouped.items():
        summary.append({"最终发货尺码": size, "聚类数量": item["clusters"], "预估销量": item["sales"], "销量倍率": MULTIPLIERS.get(size, 1.0), "加权销量": f"{item['weighted']:.1f}", "销量占比": f"{item['weighted'] / weighted_total:.6%}", "发货数量": item["shipped"], "发货占比": f"{item['shipped'] / SUPPLY:.6%}"})
    summary.append({"最终发货尺码": "合计", "聚类数量": len(rows), "预估销量": sum(int(r["预估销量"]) for r in rows), "加权销量": f"{weighted_total:.1f}", "销量占比": "100.000000%", "发货数量": SUPPLY, "发货占比": "100.000000%"})
    for rel in (Path("01_发货方案/尺码发货汇总.csv"), Path("05_输出/尺码发货汇总.csv")):
        save(TARGET / rel, summary_fields, summary)
    print(TARGET)


if __name__ == "__main__":
    main()
