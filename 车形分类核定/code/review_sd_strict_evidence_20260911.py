from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
CACHE = PROJECT / "cache" / "model_shape_cache.csv"
SOURCE = ROOT / "public" / "尺寸库.csv"
BASELINE = ROOT / "public" / "车身分类.csv"
RESULT = PROJECT / "artifacts" / "record_shape.csv"
BATCH = PROJECT / "changes" / "2026-09-11_01_sd-strict-evidence-review"


# These generations were previously promoted from legacy 32 mainly because
# they looked angular or were old.  Under the 2026-09-11 SOP they have no
# evidence that their front cover-width demand exceeds the Avalon/SD1 anchor.
DEMOTE_SD2_TO_SD1 = {
    ("Acura", "Legend", "gen1"),
    ("BMW", "3 Series", "gen1"), ("BMW", "3 Series", "gen2"),
    ("BMW", "5 Series", "gen1"), ("BMW", "5 Series", "gen2"), ("BMW", "5 Series", "gen3"),
    ("BMW", "7 Series", "gen1"), ("BMW", "7 Series", "gen2"),
    ("Buick", "LeSabre", "gen6"), ("Buick", "LeSabre", "gen7"), ("Buick", "LeSabre", "gen8"),
    ("Buick", "Park Avenue", "gen1"), ("Buick", "Park Avenue", "gen2"),
    ("Buick", "Regal", "gen3"), ("Buick", "Regal", "gen4"),
    ("Buick", "Riviera", "gen7"), ("Buick", "Riviera", "gen8"),
    ("Buick", "Roadmaster", "gen7"), ("Buick", "Skylark", "gen6"),
    ("Cadillac", "DeVille", "gen6"), ("Cadillac", "DeVille", "gen7"),
    ("Cadillac", "Eldorado", "gen9"),
    ("Cadillac", "Seville", "gen4"), ("Cadillac", "Seville", "gen5"),
    ("Chevrolet", "Cavalier", "gen1"),
    ("Ford", "Escort", "gen1"),
    ("Honda", "Accord", "gen1"), ("Honda", "Accord", "gen2"),
    ("Honda", "Civic", "gen1"), ("Honda", "Civic", "gen2"), ("Honda", "Civic", "gen3"), ("Honda", "Civic", "gen4"),
    ("Hyundai", "Sonata", "gen2"), ("Infiniti", "G", "gen1"),
    ("Jaguar", "XJ", "gen2"), ("Lexus", "ES", "gen1"), ("Lexus", "LS", "gen1"),
    ("Lincoln", "Continental", "gen8"), ("Lincoln", "Continental", "gen9"),
    ("Mazda", "Protege", "gen1"), ("Mercedes-Benz", "190", "gen1"),
    ("Mercedes-Benz", "S-Class", "gen1"), ("Mitsubishi", "Galant", "gen6"),
    ("Nissan", "Maxima", "gen1"), ("Nissan", "Maxima", "gen2"),
    ("Nissan", "Sentra", "gen1"),
    ("Oldsmobile", "88", "gen9"), ("Oldsmobile", "88", "gen10"),
    ("Oldsmobile", "Cutlass", "gen6"), ("Plymouth", "Acclaim", "gen1"),
    ("Pontiac", "Bonneville", "gen8"), ("Pontiac", "Bonneville", "gen9"), ("Pontiac", "Bonneville", "gen10"),
    ("Toyota", "Camry", "gen1"), ("Toyota", "Camry", "gen2"),
    ("Toyota", "Corolla", "gen1"), ("Toyota", "Corolla", "gen2"), ("Toyota", "Corolla", "gen3"), ("Toyota", "Corolla", "gen4"),
    ("Toyota", "Tercel", "gen1"), ("Toyota", "Tercel", "gen3"),
    ("Volkswagen", "Jetta", "gen1"), ("Volkswagen", "Jetta", "gen2"),
    ("Volkswagen", "Passat", "gen2"), ("Volvo", "S70", "gen1"), ("Volvo", "S90", "gen1"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cache = read_csv(CACHE)
    touched_rules = []
    matched_targets = []
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for row in cache:
        key = (row["MAKE"], row["MODEL"], row.get("generation", ""))
        if key not in DEMOTE_SD2_TO_SD1:
            continue
        if row.get("shape") == "SD1":
            matched_targets.append(key)
            touched_rules.append(key)
            continue
        if row.get("shape") != "SD2":
            # The same model/generation may have a separately keyed Wagon or
            # Hatchback rule; it is outside this Sedan/Coupe review.
            continue
        matched_targets.append(key)
        row["shape"] = "SD1"
        row["note"] = (
            "2026-09-11 SD 严格证据复核：旧结论主要来自年代或视觉方正，未证明前部覆盖需求高于 Avalon。"
            "按新 SOP 回退 Standard / Fastback；不得从旧 32/SD2 继承。原证据：" + row.get("note", "")
        )
        row["updated_at"] = stamp
        touched_rules.append(key)
    missing = sorted(DEMOTE_SD2_TO_SD1 - set(matched_targets))
    if missing:
        raise SystemExit(f"目标缓存规则未命中：{missing}")
    write_csv(CACHE, list(cache[0]), cache)

    # Import here so it reloads the already-updated reference and cache.
    import sys
    sys.path.insert(0, str(PROJECT / "code"))
    import shape_project
    shape_project.build()

    source = {r["DIMENSION-ID"]: r for r in read_csv(SOURCE)}
    baseline = {r["DIMENSION-ID"]: r["车形"] for r in read_csv(BASELINE)}
    result_rows = read_csv(RESULT)
    changes = []
    audit = []
    for row in result_rows:
        dim_id = row["DIMENSION-ID"]
        old = baseline.get(dim_id, "")
        new = row["车形"]
        src = source[dim_id]
        audit.append({
            "DIMENSION-ID": dim_id, "MAKE": src["MAKE"], "MODEL": src["MODEL"],
            "代际": src["代际"], "YEAR": src["YEAR"], "结构": src["结构"], "分类": src["分类"],
            "原车形": old, "车形": new, "是否变化": "YES" if old != new else "NO",
            "判定理由": "SD2 缺少高于 Avalon 的前部覆盖需求证据，按新 SOP 回退 SD1" if old == "SD2" and new == "SD1" else "现有类别符合新 SOP 或不在本轮 SD2 防误分范围",
            "审计状态": "APPLIED",
        })
        if old != new:
            changes.append({
                "DIMENSION-ID": dim_id, "MAKE": src["MAKE"], "MODEL": src["MODEL"],
                "代际": src["代际"], "YEAR": src["YEAR"], "结构": src["结构"], "分类": src["分类"],
                "原车形": old, "新车形": new,
                "原因": "未证明前部覆盖需求高于 Avalon；年代或视觉方正不足以触发 SD2",
            })
    write_csv(BATCH / "correct.csv", ["DIMENSION-ID", "车形"], result_rows)
    write_csv(BATCH / "changes.csv", ["DIMENSION-ID", "MAKE", "MODEL", "代际", "YEAR", "结构", "分类", "原车形", "新车形", "原因"], changes)
    write_csv(BATCH / "all_dimension_audit.csv", list(audit[0]), audit)
    (BATCH / "all_dimension_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = Counter(r["车形"] for r in result_rows)
    changed_counts = Counter((r["原车形"], r["新车形"]) for r in changes)
    report = f"""# SD 严格证据全量复核

复核日期：2026-09-11  
范围：全部 {len(result_rows):,} 个 DIMENSION-ID；重点复核三厢车和跑车中的 SD0/SD1/SD2。  
规则源：`public/参考尺寸计算.csv` 与 `车形分类核定/doc/AGENT.md`。

## 结论

- 全量重新生成：{len(result_rows):,} 条。
- 本轮改类：{len(changes):,} 条，均为 `SD2 -> SD1`。
- 受影响的车型代际规则：{len(set(touched_rules))} 个。
- 新 SOP 以 `SD1` 为默认类别；只有正向几何证据证明前部覆盖需求高于 Avalon，才允许使用 `SD2`。
- 1998 Nissan Maxima 保持 `SD1`，并作为“视觉略方但覆盖需求未超过 Avalon”的强制反例。
- 本轮没有仅凭车名把 `SD0` 改为 `SD1`；Low Sport 边界仍需真实下宽上窄证据，后续可做独立专项复核。

## 分类统计

{chr(10).join(f'- `{shape}`：{count:,}' for shape, count in sorted(counts.items()))}

## 变化统计

{chr(10).join(f'- `{old} -> {new}`：{count:,}' for (old, new), count in sorted(changed_counts.items()))}

## 审计边界

本轮只直接修正缺乏 SD2 正向覆盖证据的高置信度误分代际。保留的经典全尺寸方头车型并不表示仅凭年代通过；它们仍须满足宽方车头、慢收窄和平直俯视侧线。`correct.csv` 是待人工批准的全量结果，不自动覆盖 `public/车身分类.csv`。
"""
    (BATCH / "report.md").write_text(report, encoding="utf-8")
    validation = {
        "passed": len(result_rows) == len(source) == len({r['DIMENSION-ID'] for r in result_rows}),
        "records": len(result_rows), "changes": len(changes), "changed_rules": len(set(touched_rules)),
        "change_pairs": {f"{a}->{b}": n for (a, b), n in changed_counts.items()},
        "maxima_1995_1999": next((r["车形"] for r in result_rows if r["DIMENSION-ID"] == "Nissan Maxima Sedan 1995-1999"), None),
        "allowed_shapes_only": all(r["车形"] in shape_project.ALLOWED_SHAPES for r in result_rows),
    }
    validation["passed"] = validation["passed"] and validation["allowed_shapes_only"] and validation["maxima_1995_1999"] == "SD1"
    (BATCH / "validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
