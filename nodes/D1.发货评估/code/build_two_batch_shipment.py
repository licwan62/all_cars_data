"""按本节点评估交付生成一次性两批发货单；只写新RunBatch，不改变评估output。"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / "lib"))
from artifact_batch import RunBatch, sha256


def allocate(weights, units, capacities):
    """封顶后重算比例；最终最大余数取整，同分按已排序SKU顺序。"""
    if units < 0 or sum(capacities) < units:
        raise ValueError("剩余容量不足")
    exact = [0.0] * len(weights)
    active = [i for i, w in enumerate(weights) if w > 0 and capacities[i] > 0]
    remaining = units
    while active and remaining:
        total = sum(weights[i] for i in active)
        capped = [i for i in active if remaining * weights[i] / total >= capacities[i]]
        if not capped:
            for i in active:
                exact[i] = remaining * weights[i] / total
            remaining = 0
            break
        for i in capped:
            exact[i] = capacities[i]
            remaining -= capacities[i]
        active = [i for i in active if i not in capped]
    if remaining:
        raise ValueError("正权重SKU容量不足")
    result = [int(x) for x in exact]
    for i in sorted(range(len(weights)), key=lambda i: (-(exact[i] - result[i]), i)):
        if sum(result) == units:
            break
        if result[i] < capacities[i] and weights[i] > 0:
            result[i] += 1
    assert sum(result) == units and all(n <= c for n, c in zip(result, capacities))
    return result


def plan(rows, config):
    import math
    keys = ["MAKE", "MODEL", "YEAR", "供货尺码"]
    pool = [dict(r) for r in rows if r["评估类别"] == config["category"]]
    identities = [tuple(r[k] for k in keys) for r in pool]
    if len(identities) != len(set(identities)):
        raise ValueError("源SKU自然键重复")
    for r in pool:
        w = float(r[config["weight"]])
        if not math.isfinite(w) or w < 0:
            raise ValueError("权重必须为有限非负数")
    pool = [r for r in pool if float(r[config["weight"]]) > 0]
    pool.sort(key=lambda r: (-float(r[config["weight"]]), *(r[k] for k in keys)))
    b1, b2 = config["batch_units"]
    if len(pool) <= b1 or len(pool) > b1 + b2:
        raise ValueError("当前覆盖政策要求首批留有新SKU且两批能覆盖全部正权重SKU")
    first = [int(i < b1) for i in range(len(pool))]
    second = [1 - n for n in first]
    cap = config["max_total_per_sku"]
    extra = allocate([float(r[config["weight"]]) for r in pool], b2 - sum(second),
                     [cap - a - b for a, b in zip(first, second)])
    total_weight = sum(float(r[config["weight"]]) for r in pool)
    output = []
    for i, r in enumerate(pool):
        sku = "SKU-" + hashlib.sha256("|".join(r[k] for k in keys).encode()).hexdigest()[:12].upper()
        record = {"SKU": sku, "权重顺序": i + 1, "第一批发货量": first[i],
                  "第二批发货量": second[i] + extra[i], "总发货量": first[i] + second[i] + extra[i],
                  "第二批类型": "补货" if first[i] else "新增SKU",
                  "分配权重占比": float(r[config["weight"]]) / total_weight, **r}
        if r["定制标记"] == "是" and config["custom_size_blank"]:
            record["供货尺码"] = ""
        output.append(record)
    assert sum(r["第一批发货量"] for r in output) == b1
    assert sum(r["第二批发货量"] for r in output) == b2
    assert max(r["总发货量"] for r in output) <= cap
    return output


def run():
    config = json.loads((PROJECT / "data/普通车两批发货.json").read_text(encoding="utf-8"))
    with RunBatch.create(PROJECT / "artifacts", "regular-two-batch-shipment", data_dir=PROJECT / "data") as batch:
        source = batch.input(PROJECT / "output" / config["source"])
        with source.open(encoding="utf-8-sig", newline="") as f:
            records = plan(list(csv.DictReader(f)), config)
        for name, selected in [("普通车两批发货单.csv", records),
                               ("普通车第一批发货单.csv", [r for r in records if r["第一批发货量"]]),
                               ("普通车第二批发货单.csv", [r for r in records if r["第二批发货量"]])]:
            with batch.output(name).open("w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(records[0]))
                writer.writeheader()
                writer.writerows(selected)
        stats = {"total_units": sum(r["总发货量"] for r in records), "total_skus": len(records),
                 "batch1_skus": sum(r["第一批发货量"] > 0 for r in records),
                 "batch2_skus": sum(r["第二批发货量"] > 0 for r in records),
                 "new_skus_batch2": sum(r["第一批发货量"] == 0 for r in records),
                 "batch2_new_units": sum(r["第二批发货量"] for r in records if not r["第一批发货量"]),
                 "custom_skus": sum(r["定制标记"] == "是" for r in records),
                 "max_units_per_sku": max(r["总发货量"] for r in records),
                 "code_sha256": sha256(Path(__file__)), "config": config}
        payload = batch.extra("workbook.json", compress=False)
        payload.write_text(json.dumps({"records": records, "stats": stats}, ensure_ascii=False), encoding="utf-8")
        workbook = batch.output("普通车两批发货单.xlsx")
        subprocess.run(["node", str(PROJECT / "code/export_shipment_workbook.mjs"), str(payload), str(workbook)], check=True)
        report = batch.directory / "REPORT.md"
        report.write_text("# 普通车两批发货单\n\n" + config["policy"] + "\n\n" + json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        batch.finish(stats)
        print(batch.directory)
        print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    run()
