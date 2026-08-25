from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone

import shape_project as project


REPORT = project.PROJECT / "artifacts" / "generation_shape_cache_review_2026-08-25.json"
THREE_X = {"30", "31", "32"}
THREE_X_STRUCTURES = {"Sedan", "Coupe", "Convertible", "Hardtop", "Roadster", "Targa"}
NOTE_PREFIX = "按新版 AGENT 代际复用"
STRUCTURE_PATTERN = re.compile(r"Sedan|Coupe|Convertible|Hardtop|Roadster|Targa|STRUCTURE\s*=|结构\s*=", re.IGNORECASE)

# 独立于旧分类结果登记的运动产品线。只有先排除方形宽车头后才允许归 31。
SPORTY_MODELS = {
    ("Acura", "CL"), ("Acura", "Integra"), ("Acura", "NSX"), ("Acura", "RSX"),
    ("Alfa Romeo", "4C"), ("Audi", "A5/S5"), ("Audi", "A5/S5/RS5"), ("Audi", "Cabriolet"),
    ("Audi", "e-tron GT/RS e-tron GT"), ("Audi", "e-tron GT/S e-tron GT/RS e-tron GT"),
    ("Audi", "R8/R8 GT"), ("Audi", "TT/TTS/TT RS"),
    ("BMW", "1 Series"), ("BMW", "2 Series"), ("BMW", "4 Series"), ("BMW", "6 Series"),
    ("BMW", "8 Series"), ("BMW", "i8"), ("BMW", "Z3"), ("BMW", "Z4"),
    ("Buick", "Cascada"), ("Buick", "Reatta"), ("Buick", "Riviera"),
    ("Cadillac", "ATS"), ("Cadillac", "CTS"), ("Cadillac", "Eldorado"), ("Cadillac", "ELR"), ("Cadillac", "XLR"),
    ("Chevrolet", "Beretta"), ("Chevrolet", "Camaro"), ("Chevrolet", "Corvette"), ("Chevrolet", "Monte Carlo"),
    ("Chrysler", "Crossfire"), ("Chrysler", "Sebring"),
    ("Dodge", "Avenger"), ("Dodge", "Challenger"), ("Dodge", "Charger"), ("Dodge", "Stealth"), ("Dodge", "Viper"),
    ("Fiat", "124 Spider"), ("Ford", "GT"), ("Ford", "Mustang"), ("Ford", "Thunderbird"),
    ("Honda", "CR-Z"), ("Honda", "Prelude"), ("Honda", "S2000"), ("Hyundai", "Tiburon"),
    ("Infiniti", "G"), ("Infiniti", "M"), ("Infiniti", "Q60"),
    ("Jaguar", "F-Type"), ("Jaguar", "XJS"), ("Jaguar", "XK"),
    ("Karma Automotive", "GS-6"), ("Karma Automotive", "Revero"),
    ("Lexus", "LC"), ("Lexus", "LFA"), ("Lexus", "RC"), ("Lexus", "SC"),
    ("Lincoln", "Mark VII"), ("Lincoln", "Mark VIII"),
    ("Maserati", "GranTurismo"), ("Maserati", "MC20"),
    ("Mazda", "Miata"), ("Mazda", "MX-5"), ("Mazda", "MX-6"), ("Mazda", "RX-7"), ("Mazda", "RX-8"),
    ("Mercedes-Benz", "CL-Class"), ("Mercedes-Benz", "CLK-Class"), ("Mercedes-Benz", "CLS-Class"),
    ("Mercedes-Benz", "SLC-Class"), ("Mercedes-Benz", "SL-Class"), ("Mercedes-Benz", "SLK-Class"),
    ("Mercury", "Cougar"), ("MINI", "Coupe"), ("MINI", "Roadster"),
    ("Mitsubishi", "3000GT"), ("Mitsubishi", "Eclipse"),
    ("Nissan", "240SX"), ("Nissan", "300ZX"), ("Nissan", "350Z"), ("Nissan", "370Z"), ("Nissan", "GT-R"), ("Nissan", "Z"),
    ("Plymouth", "Barracuda"), ("Plymouth", "Laser"), ("Plymouth", "Road Runner"),
    ("Polestar", "1"), ("Pontiac", "Firebird"), ("Pontiac", "G5"), ("Pontiac", "Grand Prix"),
    ("Pontiac", "GTO"), ("Pontiac", "Solstice"),
    ("Porsche", "911"), ("Porsche", "912"), ("Porsche", "Boxster"), ("Porsche", "Cayman"), ("Porsche", "Taycan"),
    ("Saab", "900"), ("Saturn", "Sky"), ("Scion", "FR-S"), ("Scion", "tC"), ("Subaru", "BRZ"),
    ("Toyota", "86"), ("Toyota", "Celica"), ("Toyota", "MR2"), ("Toyota", "Solara"), ("Toyota", "Supra"),
    ("Volkswagen", "Eos"), ("Volkswagen", "Passat CC"), ("Volvo", "C70"),
}

# 早期缓存曾把 Sedan 留在 30、Coupe/Convertible 放在 31；实际整代均是方正经典轮廓。
CLASSIC_BOXY_CORRECTIONS = {
    ("Buick", "Roadmaster", "gen1"),
    ("Buick", "Roadmaster", "gen2"),
    ("Buick", "Roadmaster", "gen3"),
    ("Buick", "Roadmaster", "gen4"),
    ("Buick", "Roadmaster", "gen5"),
    ("Mercury", "Monterey", "gen1"),
    ("Mercury", "Monterey", "gen2"),
    ("Mercury", "Monterey", "gen3"),
    ("Mercury", "Monterey", "gen4"),
    ("Oldsmobile", "88", "gen1"),
    ("Oldsmobile", "88", "gen2"),
    ("Oldsmobile", "88", "gen3"),
    ("Cadillac", "Eldorado", "gen1"), ("Cadillac", "Eldorado", "gen2"),
    ("Cadillac", "Eldorado", "gen5"), ("Cadillac", "Eldorado", "gen6"),
    ("Cadillac", "Eldorado", "gen7"), ("Cadillac", "Eldorado", "gen8"),
    ("Chevrolet", "Monte Carlo", "gen1"), ("Chevrolet", "Monte Carlo", "gen2"),
    ("Dodge", "Challenger", "gen1"),
    ("Dodge", "Charger", "gen1"), ("Dodge", "Charger", "gen2"),
    ("Dodge", "Charger", "gen3"), ("Dodge", "Charger", "gen4"),
    ("Ford", "Thunderbird", "gen2"), ("Ford", "Thunderbird", "gen3"), ("Ford", "Thunderbird", "gen4"),
    ("Mercury", "Cougar", "gen1"), ("Mercury", "Cougar", "gen2"), ("Mercury", "Cougar", "gen3"),
    ("Plymouth", "Barracuda", "gen1"), ("Plymouth", "Barracuda", "gen2"), ("Plymouth", "Barracuda", "gen3"),
    ("Plymouth", "Road Runner", "gen1"), ("Plymouth", "Road Runner", "gen2"), ("Plymouth", "Road Runner", "gen3"),
    ("Pontiac", "Bonneville", "gen0"),
    ("Pontiac", "Grand Prix", "gen1"), ("Pontiac", "Grand Prix", "gen2"), ("Pontiac", "Grand Prix", "gen3"),
    ("Pontiac", "GTO", "gen1"), ("Pontiac", "GTO", "gen2"), ("Pontiac", "GTO", "gen3"),
    ("Pontiac", "LeMans", "gen1"),

    # 全量代际重建曾把未列入专项 DECISIONS 的旧 32 默认降为 30/31。
    # 以下代际已重新按正面轮廓确认：车头宽、前角方、向前收窄少。
    ("Cadillac", "DeVille", "gen0"), ("Cadillac", "DeVille", "gen1"),
    ("Cadillac", "DeVille", "gen2"), ("Cadillac", "DeVille", "gen3"),
    ("Cadillac", "DeVille", "gen4"), ("Cadillac", "DeVille", "gen5"),
    ("Cadillac", "Seville", "gen1"), ("Cadillac", "Seville", "gen2"),
    ("Cadillac", "Seville", "gen3"),
    ("Chevrolet", "Bel Air", "gen1"), ("Chevrolet", "Bel Air", "gen2"),
    ("Chevrolet", "Bel Air", "gen3"), ("Chevrolet", "Bel Air", "gen4"),
    ("Chevrolet", "Bel Air", "gen5"), ("Chevrolet", "Bel Air", "gen6"),
    ("Chevrolet", "Bel Air", "gen7"),
    ("Chevrolet", "Chevelle", "gen2"), ("Chevrolet", "Chevelle", "gen3"),
    ("Chevrolet", "Nova", "gen3"), ("Chevrolet", "Nova", "gen4"),
    ("Ford", "Crown Victoria", "gen1"), ("Ford", "Escort", "gen1"),
    ("Infiniti", "G", "gen1"),
    ("Jaguar", "XJ", "gen2"),
    ("Lexus", "LS", "gen1"),
    ("Lincoln", "Continental", "gen3"), ("Lincoln", "Continental", "gen4"),
    ("Lincoln", "Continental", "gen7"),
    ("Lincoln", "Town Car", "gen1"), ("Lincoln", "Town Car", "gen2"),
    ("Mazda", "Protege", "gen1"),
    ("Mercedes-Benz", "190", "gen1"), ("Mercedes-Benz", "S-Class", "gen1"),
    ("Mercury", "Grand Marquis", "gen0"), ("Mercury", "Grand Marquis", "gen1"),
    ("Mercury", "Marquis", "gen5"),
    ("Mitsubishi", "Galant", "gen6"),
    ("Nissan", "Maxima", "gen1"), ("Nissan", "Maxima", "gen2"),
    ("Oldsmobile", "Cutlass", "gen3"), ("Oldsmobile", "Cutlass", "gen4"),
    ("Oldsmobile", "Cutlass", "gen5"),
    ("Plymouth", "Acclaim", "gen1"), ("Plymouth", "Valiant", "gen1"),
    ("Pontiac", "Astre", "gen1"), ("Pontiac", "Bonneville", "gen7"),
    ("Pontiac", "LeMans", "gen2"), ("Pontiac", "LeMans", "gen3"),
    ("Pontiac", "LeMans", "gen4"),
    ("Toyota", "Corolla", "gen2"), ("Toyota", "Corolla", "gen4"),
    ("Toyota", "Tercel", "gen1"),
    ("Volkswagen", "Jetta", "gen1"), ("Volkswagen", "Jetta", "gen2"),
    ("Volkswagen", "Passat", "gen2"),
    ("Volvo", "S70", "gen1"), ("Volvo", "S90", "gen1"),
}

# 旧快照中曾为 32，但按新版“方形宽车头”优先级重核后排除的代际。
# 显式登记可防止它们落入无证据的默认 30，也证明旧 32 候选已全部复核。
REVIEWED_PREVIOUS_BOXY_EXCLUSIONS = {
    ("Infiniti", "Q45", "gen1"): ("30", "车头向前收窄且前角圆化，不满足方形宽车头。"),
    ("Infiniti", "Q45", "gen2"): ("30", "车头和前角进一步圆化，不满足 32。"),
    ("Jaguar", "XJ", "gen1"): ("30", "发动机盖和前翼子板向车头明显收窄，不是方形宽头。"),
    ("Lexus", "LS", "gen2"): ("30", "第二代前角与车头已圆化收窄，排除 32。"),
    ("Lincoln", "Continental", "gen8"): ("30", "该代为空气动力学圆化车头，且不是 Low Sport。"),
    ("Subaru", "Legacy", "gen1"): ("30", "车头呈楔形收窄，前角不足以支持 32。"),
    ("Toyota", "Corolla", "gen5"): ("30", "该代已采用圆化、向前收窄的车头。"),
    ("Volkswagen", "Passat", "gen3"): ("30", "无格栅楔形前脸向前收窄，排除方形宽车头。"),
}

NON_3X_EXCEPTIONS = [
    {
        "MAKE": "Porsche",
        "MODEL": "Panamera",
        "match_pattern": r"\bSport Turismo\b",
        "generation": "gen2",
        "year_start": "",
        "year_end": "",
        "shape": "20",
        "source_url": "https://newsroom.porsche.com/en/products/porsche-panamera-sport-turismo-2017-13453.html",
        "note": f"{NOTE_PREFIX}：Sport Turismo 是独立旅行车轮廓，使用版本证据保留 20；不以 STRUCTURE 字段直映射。",
    },
]


def selected_shape(row: dict[str, str], cache: list[dict[str, str]]) -> str:
    selected = project.select_cache(row, cache)
    return selected["shape"] if selected else ""


def researched_boxy_generations() -> set[tuple[str, str, str]]:
    from review_classic_shapes import DECISIONS
    return CLASSIC_BOXY_CORRECTIONS | {
        (make, model, generation)
        for make, model, generation, _pattern, shape in DECISIONS
        if generation and shape == "32"
    }


def decide(key: tuple[str, str, str], rows: list[dict[str, str]]) -> tuple[str, str]:
    make, model, generation = key
    if (make, model) == ("Fiat", "500"):
        return "20", "500C 保留圆头两厢主体；敞篷结构不触发 3x。"
    if (make, model) in {
        ("Land Rover", "Evoque"), ("Land Rover", "Range Rover Evoque"),
        ("Mercedes-Benz", "GLE-Class"), ("Porsche", "Cayenne"),
    }:
        return "41", "该记录实际为 Fastback SUV/Coupe SUV，结构名称不改变 SUV 主体。"
    if key in researched_boxy_generations():
        return "32", "该代已独立核定为方形宽车头、前角较方且向前收窄少；32 具有最高优先级。"
    if key in REVIEWED_PREVIOUS_BOXY_EXCLUSIONS:
        return REVIEWED_PREVIOUS_BOXY_EXCLUSIONS[key]
    if (make, model) in SPORTY_MODELS:
        return "31", "排除方形宽车头后，该产品线具备低矮、下宽上窄的实际运动比例。"
    return "30", "独立轮廓核定未发现方形宽车头或 Low Sport 比例，归普通现代乘用车。"


def apply_review() -> None:
    source = project.read_csv(project.SOURCE)
    original_cache = project.read_csv(project.CACHE)
    stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    target_groups: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in source:
        if row.get("结构") in THREE_X_STRUCTURES or selected_shape(row, original_cache) in THREE_X:
            generation = row.get("代际", "")
            if not generation:
                raise SystemExit(f"3x 记录缺少代际，不能复用缓存：{row['DIMENSION-ID']}")
            target_groups.setdefault((row["MAKE"], row["MODEL"], generation), []).append(row)

    before_shapes = {
        key: {selected_shape(row, original_cache) for row in rows}
        for key, rows in target_groups.items()
    }
    # 旧结果只进入 before_shapes 作为审计对照，绝不作为新结论的输入。
    decisions = {key: decide(key, rows) for key, rows in target_groups.items()}

    # 删除所有用结构名称直接决定 30/31/32 的规则，以及本脚本上一轮生成的代际规则。
    cache = []
    removed_direct_rules = []
    removed_structural_rules = []
    removed_legacy_3x_rules = []
    target_rows = [row for rows in target_groups.values() for row in rows]
    for row in original_cache:
        structural_3x = row.get("shape") in THREE_X and STRUCTURE_PATTERN.search(row.get("match_pattern", ""))
        legacy_3x = row.get("shape") in THREE_X
        direct_3x = (
            (row.get("shape") in THREE_X or STRUCTURE_PATTERN.search(row.get("match_pattern", "")))
            and project.specificity(row) > 0
            and any(project.matches(row, source_row) for source_row in target_rows)
        )
        generated = row.get("note", "").startswith(NOTE_PREFIX)
        if structural_3x:
            removed_structural_rules.append(row)
        if legacy_3x:
            removed_legacy_3x_rules.append(row)
        if direct_3x:
            removed_direct_rules.append(row)
        if legacy_3x or direct_3x or structural_3x or generated:
            continue
        cache.append(row)

    added = []
    for (make, model, generation), rows in sorted(target_groups.items()):
        shape, reason = decisions[(make, model, generation)]
        # 同身份的旧代际宽规则由新结论替换；版本/性能专用规则仍可保留。
        cache = [
            row for row in cache
            if not (
                project.norm(row.get("MAKE", "")) == project.norm(make)
                and project.norm(row.get("MODEL", "")) == project.norm(model)
                and project.norm(row.get("generation", "")) == project.norm(generation)
                and not row.get("match_pattern")
                and not row.get("year_start")
                and not row.get("year_end")
            )
        ]
        source_url = ""
        for source_row in rows:
            prior = project.select_cache(source_row, original_cache)
            if prior and prior.get("source_url"):
                source_url = prior["source_url"]
                break
        rule = {
            "MAKE": make,
            "MODEL": model,
            "match_pattern": "",
            "generation": generation,
            "year_start": "",
            "year_end": "",
            "shape": shape,
            "source_url": source_url,
            "note": f"{NOTE_PREFIX}：{reason} 结论由实际轮廓得出，不以 STRUCTURE 字段直接映射。",
            "updated_at": stamp,
        }
        cache.append(rule)
        added.append({
            "make": make,
            "model": model,
            "generation": generation,
            "structures": sorted({row["结构"] for row in rows}),
            "years": sorted({row["YEAR"] for row in rows}),
            "before_shapes": sorted(before_shapes[(make, model, generation)]),
            "after_shape": shape,
            "reason": reason,
            "records": len(rows),
        })

    for exception in NON_3X_EXCEPTIONS:
        rule = {**exception, "updated_at": stamp}
        identity = tuple(rule[key] for key in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end"))
        cache = [row for row in cache if tuple(row.get(key, "") for key in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end")) != identity]
        cache.append(rule)

    # 在落盘前确认没有缓存冲突，且非 3x 分支不会被代际规则意外改写。
    target_ids = {row["DIMENSION-ID"] for rows in target_groups.values() for row in rows}
    non_target_changes = []
    for row in source:
        before = selected_shape(row, original_cache)
        after = selected_shape(row, cache)
        if row["DIMENSION-ID"] in target_ids:
            expected = decisions[(row["MAKE"], row["MODEL"], row["代际"])][0]
            if after != expected:
                raise SystemExit(f"代际规则未生效：{row['DIMENSION-ID']} expected={expected} actual={after}")
        elif before != after:
            non_target_changes.append({"dimension_id": row["DIMENSION-ID"], "before": before, "after": after})
    unexpected_non_target = [
        item for item in non_target_changes
        if not (
            item["dimension_id"].startswith("MAKE=Porsche|MODEL=Panamera|VERSION=|STRUCTURE=Hatchback|")
            and item["after"] == "30"
        )
    ]
    if unexpected_non_target:
        raise SystemExit(f"代际规则意外改变非 3x 分支：{unexpected_non_target[:10]}")

    remaining_structural = [
        row for row in cache
        if row.get("shape") in THREE_X and STRUCTURE_PATTERN.search(row.get("match_pattern", ""))
    ]
    if remaining_structural:
        raise SystemExit(f"仍存在结构直映射 3x：{remaining_structural[:5]}")

    project.atomic_write(
        project.CACHE,
        project.CACHE_FIELDS,
        sorted(cache, key=lambda row: (project.norm(row["MAKE"]), project.norm(row["MODEL"]), -project.specificity(row))),
    )

    changed_records = sum(
        selected_shape(row, original_cache) != decisions[key][0]
        for key, rows in target_groups.items()
        for row in rows
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "30/31/32 are independently inferred from actual generation silhouette; old classifications are audit-only; square wide front always maps to 32 with highest priority",
        "generation_groups_reviewed": len(target_groups),
        "records_reviewed": len(target_ids),
        "mixed_generation_groups_before": sum(len(shapes) > 1 for shapes in before_shapes.values()),
        "old_3x_cache_rules_discarded": len(removed_legacy_3x_rules),
        "structural_3x_cache_rules_removed": len(removed_structural_rules),
        "direct_branch_3x_cache_rules_removed": len(removed_direct_rules),
        "generation_cache_rules_written": len(added),
        "records_changed": changed_records,
        "after_shape_counts": dict(sorted(Counter(item["after_shape"] for item in added).items())),
        "remaining_structural_3x_rules": 0,
        "non_3x_records_changed": len(non_target_changes),
        "non_3x_changes": non_target_changes,
        "decisions": added,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("generation_groups_reviewed", "records_reviewed", "mixed_generation_groups_before", "old_3x_cache_rules_discarded", "structural_3x_cache_rules_removed", "direct_branch_3x_cache_rules_removed", "generation_cache_rules_written", "records_changed", "after_shape_counts", "remaining_structural_3x_rules", "non_3x_records_changed")}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="把 30/31/32 缓存从结构条件改为经过轮廓判断的代际结论。")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        raise SystemExit("请显式使用 --apply")
    apply_review()


if __name__ == "__main__":
    main()
