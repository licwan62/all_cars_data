"""按本节点评估交付生成一次性两批发货单；只写新RunBatch，不改变评估output。"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(PROJECT / 'code'))
sys.path.insert(0, str(REPO / "lib"))
from artifact_batch import RunBatch, sha256
from shipment_evidence import normalized, unavailable_models, version_labels, unique_labels


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


def plan(rows, config, blocked_models=None):
    import math
    keys = ["MAKE", "MODEL", "YEAR", "供货尺码"]
    pool = [dict(r) for r in rows if r["评估类别"] == config["category"]]
    identities = [tuple(r[k] for k in keys) for r in pool]
    if any(not r["YEAR"].strip() for r in pool):
        raise ValueError("源YEAR年份不能为空")
    if len(identities) != len(set(identities)):
        raise ValueError("源SKU自然键重复")
    for r in pool:
        w = float(r[config["weight"]])
        if not math.isfinite(w) or w < 0:
            raise ValueError("权重必须为有限非负数")
    pool = [r for r in pool if float(r[config["weight"]]) > 0]
    pool.sort(key=lambda r: (-float(r[config["weight"]]), *(r[k] for k in keys)))
    b1, b2 = config["batch_units"]
    cap = config["max_total_per_sku"]
    limit = config["max_skus_per_batch"]
    new_target = config["batch2_new_sku_target"]
    if not 0 < new_target < limit or cap < 1:
        raise ValueError("批次SKU上限或第二批新增目标不合法")
    weights = [float(r[config["weight"]]) for r in pool]

    def assign(indices, units, capacities):
        if not indices or len(indices) > units or any(capacities[i] < 1 for i in indices):
            raise ValueError("批次入选SKU与发货量不匹配")
        extra = allocate([weights[i] for i in indices], units - len(indices),
                         [capacities[i] - 1 for i in indices])
        quantities = [0] * len(pool)
        for i, n in zip(indices, extra):
            quantities[i] = n + 1
        return quantities

    blocked_models = blocked_models or set()
    eligible_first = [i for i, r in enumerate(pool)
                      if normalized(f"{r['MAKE']} {r['MODEL']}") not in blocked_models]
    first_indices = eligible_first[:min(limit, b1)]
    first = assign(first_indices, b1, [cap] * len(pool))
    remaining = [cap - n for n in first]
    old = [i for i in first_indices if remaining[i] > 0]
    new = [i for i in range(len(pool)) if first[i] == 0]
    selected = new[:new_target] + old[:limit - new_target]
    for i in sorted(set(old + new) - set(selected)):
        if len(selected) >= min(limit, b2):
            break
        selected.append(i)
    second = assign(sorted(selected), b2, remaining)
    output = []
    for i, r in enumerate(pool):
        record = {"第一批发货量": first[i],
                  "第二批发货量": second[i], "总发货量": first[i] + second[i],
                  **r}
        if r["定制标记"] == "是" and config["custom_size_blank"]:
            record["供货尺码"] = ""
        if record["总发货量"]:
            output.append(record)
    assert sum(r["第一批发货量"] for r in output) == b1
    assert sum(r["第二批发货量"] for r in output) == b2
    assert max(r["总发货量"] for r in output) <= cap
    assert sum(r["第一批发货量"] > 0 for r in output) <= limit
    assert sum(r["第二批发货量"] > 0 for r in output) <= limit
    return output


def business_rows(records, quantity_column):
    return [{"MAKE": r["MAKE"], "MODEL": r["MODEL"], "版本": r.get('发货版本', ''),
             "结构": '；'.join(unique_labels(r.get('结构', ''))), "YEAR": r["YEAR"], "尺码": r["供货尺码"],
             "定制标记": r["定制标记"], "差评标记": r["差评标记"], "发货量": r[quantity_column]}
            for r in records if r[quantity_column] > 0]


def run():
    config = json.loads((PROJECT / "data/普通车两批发货.json").read_text(encoding="utf-8"))
    with RunBatch.create(PROJECT / "artifacts", "regular-two-batch-shipment", data_dir=PROJECT / "data") as batch:
        source = batch.input(PROJECT / "output" / config["source"])
        with source.open(encoding="utf-8-sig", newline="") as f:
            evaluations = list(csv.DictReader(f))
        def read(path):
            with batch.input(path).open(encoding='utf-8-sig', newline='') as f:
                return list(csv.DictReader(f))
        availability = read(PROJECT / 'data' / config['availability_file'])
        blocked, availability_audit = unavailable_models(evaluations, availability)
        atoms = read(REPO / 'nodes/A0.尺码计算/output/US/全量/全量表.csv')
        identity = read(PROJECT / 'output/发货评估身份映射.csv')
        labels, evidence = version_labels(evaluations, atoms, identity, config['version_evidence'])
        for row in evaluations:
            row['发货版本'] = labels[tuple(row[c] for c in ['MAKE', 'MODEL', 'YEAR', '供货尺码'])]
        records = plan(evaluations, config, blocked)
        assert not any(normalized(f"{r['MAKE']} {r['MODEL']}") in blocked for r in records if r['第一批发货量'])
        import gzip
        for name, rows in [('版本尺寸证据.csv', evidence), ('首批可用性核对.csv', availability_audit)]:
            if rows:
                with gzip.open(batch.extra(name), 'wt', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
        for name, quantity_column in [("普通车两批发货单.csv", "总发货量"),
                                      ("普通车第一批发货单.csv", "第一批发货量"),
                                      ("普通车第二批发货单.csv", "第二批发货量")]:
            selected = business_rows(records, quantity_column)
            with batch.output(name).open("w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=config["export_columns"])
                writer.writeheader()
                writer.writerows(selected)
        stats = {"total_units": sum(r["总发货量"] for r in records), "total_skus": len(records),
                 "batch1_skus": sum(r["第一批发货量"] > 0 for r in records),
                 "batch2_skus": sum(r["第二批发货量"] > 0 for r in records),
                 "new_skus_batch2": sum(r["第一批发货量"] == 0 for r in records),
                 "batch2_new_units": sum(r["第二批发货量"] for r in records if not r["第一批发货量"]),
                 "batch2_replenishment_skus": sum(r["第一批发货量"] > 0 and r["第二批发货量"] > 0 for r in records),
                 "batch2_replenishment_units": sum(r["第二批发货量"] for r in records if r["第一批发货量"]),
                 "custom_skus": sum(r["定制标记"] == "是" for r in records),
                 "max_units_per_sku": max(r["总发货量"] for r in records),
                 "first_batch_blocked_models": sorted(blocked),
                 "dimension_evidence_pairs": len(evidence),
                 "version_labeled_rows": sum(bool(r['发货版本']) for r in records),
                 "evidence_code_sha256": sha256(PROJECT / 'code/shipment_evidence.py'),
                 "code_sha256": sha256(Path(__file__)), "config": config}
        report = batch.directory / "REPORT.md"
        report.write_text("# 普通车两批发货单\n\n" + config["policy"] + "\n\n" + json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        batch.finish(stats)
        print(batch.directory)
        print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    run()
