from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import shape_project as project


CUTOFF = 1993
REPORT = project.PROJECT / "artifacts" / "classic_shape_review_2026-08-25.json"

SOURCES = {
    "Acura": "https://www.honda.com/heritage",
    "BMW": "https://www.bmwgroup-classic.com/en/history/historic-modeloverview-bmw.html",
    "Buick": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Cadillac": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Chevrolet": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Ford": "https://fordheritagevault.com/",
    "Honda": "https://www.honda.com/heritage",
    "Hyundai": "https://www.hyundai.com/worldwide/en/footer/corporate/heritage",
    "Lexus": "https://toyota-automobile-museum.jp/en/archives/car-database/",
    "Lincoln": "https://fordheritagevault.com/",
    "Mercury": "https://fordheritagevault.com/",
    "Nissan": "https://www.nissan-global.com/EN/HERITAGE/",
    "Oldsmobile": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Plymouth": "https://www.stellantis.com/en/company/heritage",
    "Pontiac": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Saturn": "https://www.gm.com/heritage/archive/vehicle-information-kits",
    "Toyota": "https://toyota-automobile-museum.jp/en/archives/car-database/",
}

# Only groups whose existing result changes are listed here. Every pre-1994
# Sedan/Coupe group is still emitted to REPORT, including retained decisions.
# Each tuple is MAKE, MODEL, GENERATION, DIMENSION-ID regex, SHAPE.
DECISIONS = [
    ("Acura", "Legend", "gen1", r"结构=Sedan", "32"),
    ("BMW", "3 Series", "gen1", r"结构=Coupe", "32"),
    ("BMW", "3 Series", "gen2", r"结构=Sedan", "32"),
    ("BMW", "5 Series", "gen1", r"结构=Sedan", "32"),
    ("BMW", "5 Series", "gen2", r"结构=Sedan", "32"),
    ("BMW", "5 Series", "gen3", r"结构=Sedan", "32"),
    ("BMW", "7 Series", "gen1", r"结构=Sedan", "32"),
    ("BMW", "7 Series", "gen2", r"结构=Sedan", "32"),
    ("Buick", "LeSabre", "gen1", r"结构=Sedan", "32"),
    ("Buick", "LeSabre", "gen2", r"结构=(?:Coupe|Sedan)", "32"),
    ("Buick", "LeSabre", "gen3", r"结构=(?:Coupe|Sedan)", "32"),
    ("Buick", "LeSabre", "gen4", r"结构=(?:Coupe|Sedan)", "32"),
    ("Buick", "LeSabre", "gen5", r"结构=(?:Coupe|Sedan)", "32"),
    ("Buick", "LeSabre", "gen6", r"结构=(?:Coupe|Sedan)", "32"),
    ("Buick", "Regal", "gen1", r"结构=Coupe", "32"),
    ("Buick", "Regal", "gen2", r"结构=Coupe", "32"),
    ("Buick", "Riviera", "gen5", r"结构=Coupe", "32"),
    ("Buick", "Riviera", "gen6", r"结构=Coupe", "32"),
    ("Buick", "Skylark", "gen2", r"结构=(?:Coupe|Sedan)", "32"),
    ("Buick", "Skylark", "gen3", r"结构=Sedan", "32"),
    ("Buick", "Skylark", "gen4", r"结构=(?:Coupe|Sedan)", "32"),
    ("Buick", "Skylark", "gen5", r"结构=(?:Coupe|Sedan)", "32"),
    ("Buick", "Skylark", "gen6", r"结构=(?:Coupe|Sedan)", "32"),
    ("Cadillac", "Eldorado", "gen3", r"结构=Coupe", "32"),
    ("Cadillac", "Eldorado", "gen4", r"结构=Coupe", "32"),
    ("Chevrolet", "Caprice", "gen1", r"结构=Coupe", "32"),
    ("Chevrolet", "Caprice", "gen2", r"结构=Coupe", "32"),
    ("Chevrolet", "Cavalier", "gen1", r"结构=Sedan", "32"),
    ("Chevrolet", "Chevelle", "gen1", r"结构=Coupe", "32"),
    ("Chevrolet", "Impala", "gen5", r"结构=Coupe", "32"),
    ("Chevrolet", "Impala", "gen6", r"结构=Coupe", "32"),
    ("Chevrolet", "Malibu", "gen1", r"结构=(?:Coupe|Sedan)", "32"),
    ("Chevrolet", "Malibu", "gen2", r"结构=Coupe", "31"),
    ("Chevrolet", "Malibu", "gen2", r"结构=Sedan", "32"),
    ("Chevrolet", "Malibu", "gen3", r"结构=Coupe", "31"),
    ("Chevrolet", "Malibu", "gen3", r"结构=Sedan", "32"),
    ("Chevrolet", "Malibu", "gen4", r"结构=(?:Coupe|Sedan)", "32"),
    ("Chevrolet", "Nova", "gen1", r"结构=Coupe", "32"),
    ("Chevrolet", "Nova", "gen2", r"结构=Coupe", "32"),
    ("Ford", "Thunderbird", "gen5", r"结构=Sedan", "32"),
    ("Honda", "Accord", "gen1", r"结构=Sedan", "32"),
    ("Honda", "Accord", "gen2", r"结构=Sedan", "32"),
    ("Honda", "Civic", "gen1", r"结构=Sedan", "32"),
    ("Honda", "Civic", "gen2", r"结构=Sedan", "32"),
    ("Honda", "Civic", "gen3", r"结构=Sedan", "32"),
    ("Honda", "Civic", "gen4", r"结构=Sedan", "32"),
    ("Hyundai", "Sonata", "gen2", r"结构=Sedan", "32"),
    ("Lexus", "ES", "gen1", r"结构=Sedan", "32"),
    ("Lincoln", "Continental", "gen5", r"结构=Coupe", "32"),
    ("Lincoln", "Continental", "gen6", r"结构=Coupe", "32"),
    ("Mercury", "Cougar", "gen4", r"结构=Coupe", "32"),
    ("Mercury", "Cougar", "gen5", r"结构=Coupe", "32"),
    ("Mercury", "Marquis", "gen1", r"结构=Coupe", "32"),
    ("Mercury", "Marquis", "gen2", r"结构=Coupe", "32"),
    ("Mercury", "Marquis", "gen3", r"结构=Coupe", "32"),
    ("Mercury", "Marquis", "gen4", r"结构=Coupe", "32"),
    ("Mercury", "Monterey", "gen5", r"结构=Coupe", "32"),
    ("Mercury", "Monterey", "gen6", r"结构=Coupe", "32"),
    ("Mercury", "Monterey", "gen7", r"结构=Coupe", "32"),
    ("Nissan", "Sentra", "gen1", r"结构=Coupe", "32"),
    ("Oldsmobile", "88", "gen4", r"结构=Coupe", "32"),
    ("Oldsmobile", "88", "gen5", r"结构=Coupe", "32"),
    ("Oldsmobile", "88", "gen6", r"结构=Coupe", "32"),
    ("Oldsmobile", "88", "gen7", r"结构=Coupe", "32"),
    ("Oldsmobile", "88", "gen8", r"结构=Coupe", "32"),
    ("Oldsmobile", "88", "gen9", r"结构=Coupe", "32"),
    ("Oldsmobile", "Cutlass", "gen1", r"结构=Coupe", "32"),
    ("Oldsmobile", "Cutlass", "gen2", r"结构=Coupe", "32"),
    ("Oldsmobile", "Cutlass", "gen6", r"VERSION=Ciera.*结构=(?:Coupe|Sedan)", "32"),
    ("Plymouth", "Fury", "gen0", r"结构=Coupe", "32"),
    ("Plymouth", "Fury", "gen1", r"结构=Coupe", "32"),
    ("Plymouth", "Fury", "gen2", r"结构=Coupe", "32"),
    ("Plymouth", "Fury", "gen3", r"结构=Coupe", "32"),
    ("Plymouth", "Fury", "gen4", r"结构=Coupe", "32"),
    ("Plymouth", "Fury", "gen5", r"结构=Coupe", "32"),
    ("Plymouth", "Valiant", "gen2", r"结构=Coupe", "32"),
    ("Plymouth", "Valiant", "gen3", r"结构=Coupe", "32"),
    ("Plymouth", "Valiant", "gen4", r"结构=Coupe", "32"),
    ("Pontiac", "Bonneville", "gen2", r"结构=Coupe", "32"),
    ("Pontiac", "Bonneville", "gen3", r"结构=Coupe", "32"),
    ("Pontiac", "Bonneville", "gen4", r"结构=Coupe", "32"),
    ("Pontiac", "Bonneville", "gen5", r"结构=Coupe", "32"),
    ("Pontiac", "Bonneville", "gen6", r"结构=Coupe", "32"),
    ("Pontiac", "Grand Prix", "gen4", r"结构=Coupe", "32"),
    ("Pontiac", "Grand Prix", "gen5", r"结构=Coupe", "32"),
    ("Pontiac", "LeMans", "gen5", r"结构=Coupe", "32"),
    ("Saturn", "S-Series", "gen1", r"结构=Sedan", "30"),
    ("Toyota", "Camry", "gen1", r"结构=Sedan", "32"),
    ("Toyota", "Camry", "gen2", r"结构=Sedan", "32"),
    ("Toyota", "Corolla", "gen1", r"结构=Coupe", "32"),
    ("Toyota", "Corolla", "gen3", r"结构=Coupe", "32"),
    ("Toyota", "Tercel", "gen3", r"结构=Coupe", "32"),
]


def is_classic_record(row: dict[str, str]) -> bool:
    if not re.search(r"Sedan|Coupe", row.get("结构", ""), re.IGNORECASE):
        return False
    lo, _ = project.years(row.get("YEAR", ""))
    return lo is not None and lo <= CUTOFF


def note_for(shape: str) -> str:
    if shape == "32":
        return "按新版 AGENT 以换代为边界复核：该代具有平直车顶、相对直立柱体及明确三段式方正轮廓，Boxy Classic 优先于名称或双门属性。"
    if shape == "31":
        return "按新版 AGENT 以换代为边界复核：该代 Coupe 的低 CAB 和快速后降轮廓强于方正特征，归 Low Sport。"
    return "按新版 AGENT 以换代为边界复核：该代已呈现代流线 CAB，不满足 Boxy Classic，归 Standard-Fastback。"


def apply_review() -> None:
    source = project.read_csv(project.SOURCE)
    cache = project.read_csv(project.CACHE)
    before_cache = [dict(row) for row in cache]
    stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    matched_decisions: list[dict[str, object]] = []

    for make, model, generation, pattern, shape in DECISIONS:
        rule = {
            "MAKE": make,
            "MODEL": model,
            "match_pattern": pattern,
            "generation": generation,
            "year_start": "",
            "year_end": "",
            "shape": shape,
            "source_url": SOURCES[make],
            "note": note_for(shape),
            "updated_at": stamp,
        }
        matched = [row for row in source if project.matches(rule, row)]
        if not matched:
            raise SystemExit(f"复核规则未命中源记录: {make} {model} {generation} {pattern}")
        identity = tuple(rule[key] for key in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end"))
        cache = [row for row in cache if tuple(row.get(key, "") for key in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end")) != identity]
        cache.append(rule)
        matched_decisions.append({"make": make, "model": model, "generation": generation, "pattern": pattern, "shape": shape, "records": len(matched)})

    project.atomic_write(
        project.CACHE,
        project.CACHE_FIELDS,
        sorted(cache, key=lambda row: (project.norm(row["MAKE"]), project.norm(row["MODEL"]), -project.specificity(row))),
    )

    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    changed_records = 0
    for row in source:
        if not is_classic_record(row):
            continue
        key = (row["MAKE"], row["MODEL"], row.get("代际", ""), row.get("结构", ""))
        groups.setdefault(key, []).append(row)
        before = project.select_cache(row, before_cache)
        after = project.select_cache(row, cache)
        if before and after and before["shape"] != after["shape"]:
            changed_records += 1

    reviewed_groups = []
    for (make, model, generation, structure), rows in sorted(groups.items()):
        before_shapes = sorted({project.select_cache(row, before_cache)["shape"] for row in rows})
        after_shapes = sorted({project.select_cache(row, cache)["shape"] for row in rows})
        reviewed_groups.append({
            "make": make,
            "model": model,
            "generation": generation,
            "structure": structure,
            "years": sorted({row.get("YEAR", "") for row in rows}),
            "before_shapes": before_shapes,
            "after_shapes": after_shapes,
            "decision": "changed" if before_shapes != after_shapes else "retained",
        })

    report = {
        "cutoff_start_year": CUTOFF,
        "scope": "All source Sedan/Coupe records whose year range starts no later than 1993",
        "source_records_reviewed": sum(len(rows) for rows in groups.values()),
        "generation_body_groups_reviewed": len(groups),
        "models_reviewed": len({(item["make"], item["model"]) for item in reviewed_groups}),
        "override_rules_applied": len(DECISIONS),
        "records_changed": changed_records,
        "overrides": matched_decisions,
        "groups": reviewed_groups,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("source_records_reviewed", "generation_body_groups_reviewed", "models_reviewed", "override_rules_applied", "records_changed")}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="按 AGENT 的逐代规则复核历史 Sedan/Coupe")
    parser.add_argument("--apply", action="store_true", help="更新缓存并生成审计报告")
    args = parser.parse_args()
    if not args.apply:
        raise SystemExit("请显式使用 --apply")
    apply_review()


if __name__ == "__main__":
    main()
