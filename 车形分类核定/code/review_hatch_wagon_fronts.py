from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone

import shape_project as project


REPORT = project.PROJECT / "artifacts" / "hatch_wagon_front_review_2026-08-25.json"
RULE_NOTE_PREFIX = "按新版 AGENT 20/21"

SOURCES = {
    "Buick": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Chevrolet": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Ford": "https://fordheritagevault.com/",
    "Honda": "https://www.honda.com/heritage",
    "Mercury": "https://fordheritagevault.com/",
    "Nissan": "https://www.nissan-global.com/EN/HERITAGE/",
    "Oldsmobile": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Plymouth": "https://www.stellantis.com/en/company/heritage",
    "Pontiac": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Toyota": "https://toyota-automobile-museum.jp/en/archives/car-database/",
    "Volkswagen": "https://www.volkswagen-newsroom.com/en/history-3693",
    "Volvo": "https://www.volvocars.com/intl/media/press-releases/",
}

# MAKE, MODEL, GENERATION, structure regex, optional start/end year.
# 只登记需要从 Rounded Front 改为 Boxy Front 的代际；其余两厢/旅行车保留 20。
BOXY_DECISIONS = [
    ("Buick", "Century", "gen1", "Wagon", "", ""),
    ("Buick", "Century", "gen2", "Wagon", "", ""),
    ("Buick", "Century", "gen3", "Wagon", "", ""),
    ("Buick", "Century", "gen4", "Wagon", "", ""),
    ("Buick", "LeSabre", "gen1", "Wagon", "", ""),
    ("Buick", "LeSabre", "gen2", "Wagon", "", ""),
    ("Buick", "LeSabre", "gen4", "Wagon", "", ""),
    ("Buick", "LeSabre", "gen5", "Wagon", "", ""),
    ("Buick", "Roadmaster", "gen7", "Wagon", "", ""),
    ("Buick", "Skylark", "gen3", "Hatchback", "", ""),
    ("Buick", "Skylark", "gen4", "Hatchback", "", ""),
    ("Chevrolet", "Caprice", "gen1", "Wagon", "", ""),
    ("Chevrolet", "Cavalier", "gen1", "Hatchback|Wagon", "", "1989"),
    ("Chevrolet", "Chevelle", "gen1", "Wagon", "", ""),
    ("Chevrolet", "Chevelle", "gen2", "Wagon", "", ""),
    ("Chevrolet", "Chevelle", "gen3", "Wagon", "", ""),
    ("Chevrolet", "Impala", "gen3", "Wagon", "", ""),
    ("Chevrolet", "Impala", "gen4", "Wagon", "", ""),
    ("Chevrolet", "Nova", "gen1", "Wagon", "", ""),
    ("Chevrolet", "Nova", "gen2", "Wagon", "", ""),
    ("Chevrolet", "Nova", "gen3", "Hatchback", "", ""),
    ("Chevrolet", "Nova", "gen4", "Hatchback", "", ""),
    ("Chevrolet", "Nova", "gen5", "Hatchback", "", ""),
    ("Ford", "Escort", "gen1", "Hatchback|Wagon", "", ""),
    ("Mercury", "Cougar", "gen4", "Wagon", "", ""),
    ("Mercury", "Cougar", "gen5", "Wagon", "", ""),
    ("Mercury", "Marquis", "gen3", "Wagon", "", ""),
    ("Mercury", "Marquis", "gen4", "Wagon", "", ""),
    ("Mercury", "Marquis", "gen5", "Wagon", "", ""),
    ("Mercury", "Monterey", "gen1", "Wagon", "", ""),
    ("Mercury", "Monterey", "gen2", "Wagon", "", ""),
    ("Mercury", "Monterey", "gen4", "Wagon", "", ""),
    ("Mercury", "Monterey", "gen7", "Wagon", "", ""),
    ("Nissan", "Maxima", "gen1", "Wagon", "", ""),
    ("Nissan", "Sentra", "gen1", "Hatchback|Wagon", "", ""),
    ("Oldsmobile", "88", "gen5", "Wagon", "", ""),
    ("Oldsmobile", "88", "gen7", "Wagon", "", ""),
    ("Oldsmobile", "88", "gen8", "Wagon", "", ""),
    ("Oldsmobile", "Custom Cruiser", "gen1", "Wagon", "", ""),
    ("Oldsmobile", "Cutlass", "gen1", "Wagon", "", ""),
    ("Oldsmobile", "Cutlass", "gen3", "Wagon", "", ""),
    ("Oldsmobile", "Cutlass", "gen6", "Wagon", "", ""),
    ("Plymouth", "Fury", "gen2", "Wagon", "", ""),
    ("Plymouth", "Valiant", "gen1", "Wagon", "", ""),
    ("Plymouth", "Valiant", "gen2", "Wagon", "", ""),
    ("Pontiac", "Astre", "gen1", "Hatchback|Wagon", "", ""),
    ("Pontiac", "Bonneville", "gen3", "Wagon", "", ""),
    ("Pontiac", "Bonneville", "gen4", "Wagon", "", ""),
    ("Pontiac", "Bonneville", "gen5", "Wagon", "", ""),
    ("Pontiac", "Bonneville", "gen6", "Wagon", "", ""),
    ("Pontiac", "Grand Safari", "gen1", "Wagon", "", ""),
    ("Pontiac", "LeMans", "gen1", "Wagon", "", ""),
    ("Pontiac", "LeMans", "gen2", "Wagon", "", ""),
    ("Pontiac", "LeMans", "gen3", "Wagon", "", ""),
    ("Pontiac", "LeMans", "gen4", "Wagon", "", ""),
    ("Pontiac", "LeMans", "gen5", "Wagon", "", ""),
    ("Toyota", "Corolla", "gen1", "Wagon", "", ""),
    ("Toyota", "Corolla", "gen2", "Wagon", "", ""),
    ("Toyota", "Corolla", "gen3", "Hatchback|Wagon", "", ""),
    ("Toyota", "Corolla", "gen4", "Hatchback", "", ""),
    ("Toyota", "Corolla", "gen5", "Wagon", "", ""),
    ("Toyota", "Tercel", "gen1", "Hatchback", "", ""),
    ("Toyota", "Tercel", "gen2", "Wagon", "", ""),
    ("Volkswagen", "Dasher", "gen1", "Hatchback|Wagon", "", ""),
    ("Volkswagen", "Passat", "gen1", "Hatchback|Wagon", "", ""),
    ("Volkswagen", "Passat", "gen2", "Wagon", "", ""),
    ("Volkswagen", "Rabbit", "gen1", "Hatchback", "", ""),
    ("Volvo", "V90", "gen1", "Wagon", "", ""),
]

FORMER_TALL_UPRIGHT = {
    ("BMW", "i3"): "20",
    ("Chevrolet", "Bolt"): "20",
    ("Chevrolet", "HHR"): "21",
    ("Chrysler", "PT Cruiser"): "20",
    ("Ford", "C-MAX"): "20",
    ("Kia", "Soul"): "21",
    ("Mercedes-Benz", "B-Class"): "20",
    ("Mitsubishi", "i-MiEV"): "20",
    ("Nissan", "Cube"): "21",
    ("Scion", "xB"): "21",
}

LEGACY_MINIVAN_MODELS = {
    ("Chevrolet", "Astro"),
    ("Chevrolet", "City Express"),
    ("Chevrolet", "Lumina APV"),
    ("Chevrolet", "Uplander"),
    ("Chevrolet", "Venture"),
    ("Chrysler", "Pacifica"),
    ("Chrysler", "Town & Country"),
    ("Chrysler", "Voyager"),
    ("Dodge", "Caravan"),
    ("FIAT", "500L"),
    ("Honda", "Odyssey"),
    ("Kia", "Carnival"),
    ("Kia", "Rondo"),
    ("Mazda", "5"),
    ("Mercury", "Monterey"),
    ("Toyota", "Sienna"),
}


def selected_shape(row: dict[str, str], cache: list[dict[str, str]]) -> str:
    selected = project.select_cache(row, cache)
    return selected["shape"] if selected else ""


def apply_review() -> None:
    source = project.read_csv(project.SOURCE)
    original_cache = project.read_csv(project.CACHE)
    cache = []
    for row in original_cache:
        note = row.get("note", "")
        if note.startswith(f"{RULE_NOTE_PREFIX}：该代"):
            continue
        # 清理由旧脚本误把刚新增的 Boxy 21 当成 Minivan 迁移所得的规则。
        if note.startswith(f"{RULE_NOTE_PREFIX}：新版固定编号将 Minivan") and (row["MAKE"], row["MODEL"]) not in LEGACY_MINIVAN_MODELS:
            continue
        cache.append(row)
    before_cache = [dict(row) for row in cache]
    stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    migrations = []
    for row in cache:
        before = row["shape"]
        if row.get("note", "").startswith(RULE_NOTE_PREFIX):
            continue
        model_key = (row["MAKE"], row["MODEL"])
        legacy_minivan = model_key in LEGACY_MINIVAN_MODELS and (
            model_key != ("Mercury", "Monterey") or "MPV" in row.get("match_pattern", "")
        )
        if before == "21" and legacy_minivan:
            row["shape"] = "25"
            row["note"] = f"{RULE_NOTE_PREFIX}：新版固定编号将 Minivan 从旧 21 迁移至 25；" + row.get("note", "")
        elif before == "22":
            row["shape"] = "26"
            row["note"] = f"{RULE_NOTE_PREFIX}：新版固定编号将 Full-size Van 从旧 22 迁移至 26；" + row.get("note", "")
        elif before == "23":
            target = FORMER_TALL_UPRIGHT.get((row["MAKE"], row["MODEL"]))
            if not target:
                raise SystemExit(f"旧 23 未登记新去向：{row['MAKE']} {row['MODEL']}")
            row["shape"] = target
            front = "Rounded Front" if target == "20" else "Boxy Front"
            row["note"] = f"{RULE_NOTE_PREFIX}：旧 Tall Upright 编号已取消；按俯视车头收窄与前角重新归 {front}。"
        if row["shape"] != before:
            migrations.append({"make": row["MAKE"], "model": row["MODEL"], "before": before, "after": row["shape"]})

    added_rules = []
    for make, model, generation, structures, year_start, year_end in BOXY_DECISIONS:
        pattern = rf"结构=(?:{structures})(?:\s|\||$)"
        rule = {
            "MAKE": make,
            "MODEL": model,
            "match_pattern": pattern,
            "generation": generation,
            "year_start": year_start,
            "year_end": year_end,
            "shape": "21",
            "source_url": SOURCES[make],
            "note": f"{RULE_NOTE_PREFIX}：该代俯视车头宽且较方，两侧向前收窄少；按代际边界归 Boxy Front。",
            "updated_at": stamp,
        }
        matched = [row for row in source if project.matches(rule, row)]
        if not matched:
            raise SystemExit(f"20/21 规则未命中：{make} {model} {generation} {pattern} {year_start}-{year_end}")
        identity = tuple(rule[key] for key in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end"))
        cache = [row for row in cache if tuple(row.get(key, "") for key in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end")) != identity]
        cache.append(rule)
        added_rules.append({"make": make, "model": model, "generation": generation, "structures": structures, "records": len(matched)})

    project.atomic_write(
        project.CACHE,
        project.CACHE_FIELDS,
        sorted(cache, key=lambda row: (project.norm(row["MAKE"]), project.norm(row["MODEL"]), -project.specificity(row))),
    )

    reviewed = []
    changed_records = 0
    migration_records = 0
    invalid_after = []
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    for row in source:
        before = selected_shape(row, before_cache)
        after = selected_shape(row, cache)
        selected_after = project.select_cache(row, cache)
        if selected_after and selected_after.get("note", "").startswith(RULE_NOTE_PREFIX) and (
            "迁移至" in selected_after.get("note", "") or "旧 Tall Upright" in selected_after.get("note", "")
        ):
            migration_records += 1
        if after in {"22", "23"}:
            invalid_after.append(row["DIMENSION-ID"])
        if row.get("结构") in {"Hatchback", "Wagon"} or before in {"20", "21", "22", "23", "25", "26"} or after in {"20", "21", "25", "26"}:
            groups.setdefault((row["MAKE"], row["MODEL"], row.get("代际", ""), row.get("结构", "")), []).append(row)
        if before != after:
            changed_records += 1
    if invalid_after:
        raise SystemExit(f"仍有旧 22/23 结果：{invalid_after[:10]}")

    for (make, model, generation, structure), rows in sorted(groups.items()):
        before_shapes = sorted({selected_shape(row, before_cache) for row in rows})
        after_shapes = sorted({selected_shape(row, cache) for row in rows})
        reviewed.append(
            {
                "make": make,
                "model": model,
                "generation": generation,
                "structure": structure,
                "years": sorted({row.get("YEAR", "") for row in rows}),
                "before_shapes": before_shapes,
                "after_shapes": after_shapes,
                "decision": "changed" if before_shapes != after_shapes else "retained",
            }
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "agent_rule": "20=Hatchback/Wagon Rounded Front; 21=Hatchback/Wagon Boxy Front; 25=Minivan; 26=Full-size Van",
        "scope": "All Hatchback/Wagon records plus every record previously or subsequently assigned 20/21/22/23/25/26",
        "source_records_reviewed": sum(len(items) for items in groups.values()),
        "generation_body_groups_reviewed": len(groups),
        "models_reviewed": len({(item["make"], item["model"]) for item in reviewed}),
        "cache_code_migrations_applied_this_run": len(migrations),
        "migrated_cache_rules_present": sum(
            row.get("note", "").startswith(RULE_NOTE_PREFIX)
            and ("迁移至" in row.get("note", "") or "旧 Tall Upright" in row.get("note", ""))
            for row in cache
        ),
        "records_reassigned_by_number_migration": migration_records,
        "boxy_override_rules": len(added_rules),
        "records_changed_to_boxy_21": changed_records,
        "records_changed_from_pre_review_baseline": migration_records + changed_records,
        "remaining_legacy_22_23": 0,
        "migrations": migrations,
        "boxy_overrides": added_rules,
        "groups": reviewed,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("source_records_reviewed", "generation_body_groups_reviewed", "models_reviewed", "migrated_cache_rules_present", "records_reassigned_by_number_migration", "boxy_override_rules", "records_changed_to_boxy_21", "records_changed_from_pre_review_baseline", "remaining_legacy_22_23")}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="按新版 AGENT 复核 20/21，并迁移旧 21/22/23 编号。")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        raise SystemExit("请显式使用 --apply")
    apply_review()


if __name__ == "__main__":
    main()
