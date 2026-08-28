from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from review_year_generation import (
    IDENTITY,
    audit_gaps,
    audit_generations,
    audit_interval_conflicts,
    dimension_id,
    ensure_not_source,
    write_csv,
)


SAME_GENERATION_EXCLUSIONS = {
    ("Porsche", "911", "GT3 RS", "", "", "Coupe", "2017-2018"): "GT3 RS 衍生版本的已知空档。",
    ("Porsche", "911", "Turbo", "", "", "Coupe", "1981-1985"): "美国市场 911 Turbo 年款空档，不按欧洲生产年自动补齐。",
}

CONFIRMED_MODEL_GAPS = {
    ("Cadillac", "Eldorado", "", "", "", "Coupe", "1993-1994"),
    ("Cadillac", "Eldorado", "", "", "", "Coupe", "1996-1997"),
    ("Ford", "Thunderbird", "", "", "", "Coupe", "1994-1995"),
    ("Mitsubishi", "Montero", "", "", "", "SUV", "1998"),
    ("Oldsmobile", "Cutlass", "RWD", "", "", "Sedan", "1979-1980"),
    ("Volvo", "S90", "", "", "", "Sedan", "2018-2020"),
}

# key=(MAKE, MODEL, VERSION, CAB, BED, STRUCTURE, MISSING_YEAR), value=(generation, donor side)
CONFIRMED_BOUNDARY_GAPS = {
    ("Audi", "Q5/SQ5", "Sportback", "", "", "SUV", "2025"): ("gen2", "LEFT"),
    ("BMW", "3 Series", "", "", "", "Wagon", "2006"): ("gen5", "RIGHT"),
    ("BMW", "3 Series", "", "", "", "Wagon", "2013"): ("gen6", "RIGHT"),
    ("Chevrolet", "Bel Air", "", "", "", "Coupe", "1959"): ("gen4", "RIGHT"),
    ("Chevrolet", "Cavalier", "", "", "", "Coupe", "1995"): ("gen2", "RIGHT"),
    ("Chevrolet", "Chevelle", "", "", "", "Convertible", "1967"): ("gen1", "LEFT"),
    ("Chevrolet", "Chevelle", "", "", "", "Coupe", "1972"): ("gen2", "LEFT"),
    ("Chevrolet", "Nova", "", "", "", "Coupe", "1975"): ("gen4", "RIGHT"),
    ("Chrysler", "Sebring", "", "", "", "Convertible", "2007"): ("gen3", "RIGHT"),
    ("Dodge", "Viper", "", "", "", "Convertible", "2002"): ("gen1", "LEFT"),
    ("Ford", "F-150", "", "SuperCab", "6.5", "Pickup", "1996"): ("gen9", "LEFT"),
    ("Ford", "F-150", "", "SuperCrew", "5.5", "Pickup", "2003"): ("gen10", "LEFT"),
    ("Ford", "F-150", "", "SuperCrew", "5.5", "Pickup", "2014"): ("gen12", "LEFT"),
    ("Kia", "Spectra", "", "", "", "Hatchback", "2005"): ("gen2", "RIGHT"),
    ("Mercedes-Benz", "E-Class", "", "", "", "Wagon", "2010"): ("gen4", "RIGHT"),
    ("Mercedes-Benz", "E-Class", "", "", "", "Sedan", "2024"): ("gen6", "RIGHT"),
    ("Mercury", "Marquis", "", "", "", "Coupe", "1979"): ("gen4", "RIGHT"),
    ("MINI", "Cooper", "2dr", "", "", "Hatchback", "2024"): ("gen3", "LEFT"),
    ("MINI", "Countryman", "", "", "", "SUV", "2016"): ("gen1", "LEFT"),
    ("Mitsubishi", "Eclipse", "", "", "", "Coupe", "1999"): ("gen2", "LEFT"),
    ("Nissan", "Armada", "", "", "", "SUV", "2025"): ("gen2", "LEFT"),
    ("Oldsmobile", "88", "", "", "", "Wagon", "1976"): ("gen7", "LEFT"),
    ("Ram", "1500", "", "Regular", "8", "Pickup", "2008"): ("gen3", "LEFT"),
    ("Subaru", "Forester", "Wilderness", "", "", "SUV", "2025"): ("gen5", "LEFT"),
    ("Toyota", "Tundra", "", "Double", "6.5", "Pickup", "2007"): ("gen2", "RIGHT"),
    ("Toyota", "Tundra", "", "Double", "6.5", "Pickup", "2021"): ("gen2", "LEFT"),
    ("Toyota", "Yaris", "", "", "", "Hatchback", "2019"): ("gen2", "LEFT"),
    ("Volkswagen", "Golf", "", "", "", "Hatchback", "2015"): ("gen7", "RIGHT"),
}

NOVA_BROCHURE = "https://www.oldcarbrochures.com/static/NA/Chevrolet/1975_Chevrolet/1975_Chevrolet_Nova_Brochure/1975%20Chevrolet%20Nova-05.html"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def gap_identity(gap: dict[str, str]) -> tuple[str, ...]:
    return tuple(gap.get(field, "") for field in IDENTITY)


def decision_key(gap: dict[str, str]) -> tuple[str, ...]:
    return (*gap_identity(gap), gap["MISSING_YEAR"])


def find_donor(rows: list[dict[str, str]], gap: dict[str, str], side: str) -> dict[str, str]:
    donor_year = gap["LEFT_YEAR"] if side == "LEFT" else gap["RIGHT_YEAR"]
    candidates = [
        row for row in rows
        if tuple(row.get(field, "") for field in IDENTITY) == gap_identity(gap) and row["YEAR"] == donor_year
    ]
    if len(candidates) != 1:
        raise SystemExit(f"无法唯一定位缺口供体：{decision_key(gap)} side={side} count={len(candidates)}")
    return candidates[0]


def add_record(rows: list[dict[str, str]], gap: dict[str, str], generation: str, side: str, reason: str) -> tuple[dict[str, str], dict[str, str]]:
    donor = find_donor(rows, gap, side)
    record = dict(donor)
    record["YEAR"] = gap["MISSING_YEAR"]
    record["代际"] = generation
    evidence = NOVA_BROCHURE if (gap["MAKE"], gap["MODEL"], gap["结构"], gap["MISSING_YEAR"]) == ("Chevrolet", "Nova", "Coupe", "1975") else "原厂目录/年款时间线与现有分支连续性复核"
    record["参考车型"] = f"{gap['MISSING_YEAR']} {gap['MAKE']} {gap['MODEL']} {gap['结构']}"
    record["备注"] = f"分支缺口补建；{reason}外廓暂沿用 {donor['YEAR']} 同分支记录，尺寸待专项复核。"
    record["迭代状态"] = "待补尺寸"
    if (gap["MAKE"], gap["MODEL"], gap["结构"], gap["MISSING_YEAR"]) == ("Chevrolet", "Nova", "Coupe", "1975"):
        record.update({"L-IN": "196.7", "W-IN": "72.4", "H-IN": "52.7", "迭代状态": "可入库"})
        record["备注"] = "1975 Chevrolet 原厂目录明确将 Nova Coupe 与 Hatchback Coupe、4-Door Sedan 分列。"
    record["DIMENSION-ID"] = dimension_id(record)
    change = {
        "ACTION": "ADD_CONFIRMED_BRANCH",
        "DIMENSION_ID_AFTER": record["DIMENSION-ID"],
        "MAKE": record["MAKE"], "MODEL": record["MODEL"], "VERSION": record.get("版本", ""),
        "CAB": record.get("CAB", ""), "BED": record.get("BED", ""), "STRUCTURE": record["结构"],
        "GENERATION": generation, "YEAR": record["YEAR"], "DONOR_DIMENSION_ID": donor["DIMENSION-ID"],
        "REASON": reason, "EVIDENCE": evidence,
    }
    return record, change


def main() -> None:
    parser = argparse.ArgumentParser(description="推进已确认的分支缺口，新建记录而不跨代硬合并。")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--gap-report", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    args = parser.parse_args()
    ensure_not_source(args.package)
    args.package.mkdir(parents=True, exist_ok=False)

    fields, rows = read_csv(args.input)
    _, gaps = read_csv(args.gap_report)
    additions: list[dict[str, str]] = []
    changes: list[dict[str, str]] = []
    decisions: list[dict[str, str]] = []

    for gap in gaps:
        key = decision_key(gap)
        apply = False
        generation = ""
        side = "LEFT"
        reason = ""
        if gap["DECISION"] == "RESEARCH_BRANCH_GAP":
            if key in SAME_GENERATION_EXCLUSIONS:
                decisions.append({**gap, "PROGRESSION": "RETAIN_CONFIRMED_HIATUS", "PROGRESSION_REASON": SAME_GENERATION_EXCLUSIONS[key]})
                continue
            apply = True
            generation = gap["LEFT_GENERATION"]
            reason = "同代同分支前后都存在，且该年款由其他分支覆盖；按分支连续性确认补建。"
        elif gap["DECISION"] == "RESEARCH_MODEL_YEAR_GAP" and key in CONFIRMED_MODEL_GAPS:
            apply = True
            generation = gap["LEFT_GENERATION"]
            reason = "整车型缺口已经年款时间线确认为数据缺失。"
        elif gap["DECISION"] == "REVIEW_BRANCH_OR_GENERATION_BOUNDARY" and key in CONFIRMED_BOUNDARY_GAPS:
            apply = True
            generation, side = CONFIRMED_BOUNDARY_GAPS[key]
            reason = "跨代分支缺口已经年款车身目录确认；独立新建记录，不跨代合并。"
        if not apply:
            decisions.append({**gap, "PROGRESSION": "RETAIN_REVIEW", "PROGRESSION_REASON": "尚无足够证据确认缺口中每个年款都存在该分支。"})
            continue
        record, change = add_record(rows, gap, generation, side, reason)
        additions.append(record)
        changes.append(change)
        decisions.append({**gap, "PROGRESSION": "ADD_CONFIRMED_BRANCH", "PROGRESSION_REASON": reason})

    output = rows + additions
    output.sort(key=lambda row: (row["MAKE"], row["MODEL"], row.get("版本", ""), row.get("结构", ""), row["YEAR"], row.get("CAB", ""), row.get("BED", "")))
    ids = [row["DIMENSION-ID"] for row in output]
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if count > 1)
    id_mismatches = [row["DIMENSION-ID"] for row in output if row["DIMENSION-ID"] != dimension_id(row)]
    gaps_after = audit_gaps(output)
    generations_after = audit_generations(output)
    conflicts_after = audit_interval_conflicts(output, Decimal("0.1"))
    applied_keys = {decision_key(gap) for gap in gaps if any(change["MAKE"] == gap["MAKE"] and change["MODEL"] == gap["MODEL"] and change["STRUCTURE"] == gap["结构"] and change["YEAR"] == gap["MISSING_YEAR"] and change["VERSION"] == gap.get("版本", "") and change["CAB"] == gap.get("CAB", "") and change["BED"] == gap.get("BED", "") for change in changes)}
    remaining_keys = {decision_key(gap) for gap in gaps_after}
    unresolved_applied = sorted(" | ".join(key) for key in applied_keys & remaining_keys)
    unresolved_generation = [row for row in generations_after if row.get("DECISION") == "REVIEW_ONLY"]
    unresolved_conflicts = [row for row in conflicts_after if row.get("DECISION") == "REVIEW_ONLY"]
    passed = not duplicate_ids and not id_mismatches and not unresolved_applied and not unresolved_generation and not unresolved_conflicts

    write_csv(args.package / "correct.csv", fields, output)
    change_fields = ["ACTION", "DIMENSION_ID_AFTER", "MAKE", "MODEL", "VERSION", "CAB", "BED", "STRUCTURE", "GENERATION", "YEAR", "DONOR_DIMENSION_ID", "REASON", "EVIDENCE"]
    write_csv(args.package / "changes.csv", change_fields, changes)
    decision_fields = [*gaps[0].keys(), "PROGRESSION", "PROGRESSION_REASON"] if gaps else []
    write_csv(args.package / "branch_gap_decisions.csv", decision_fields, decisions)
    write_csv(args.package / "gap_candidates.csv", list(gaps_after[0].keys()) if gaps_after else [], gaps_after)
    write_csv(args.package / "generation_findings.csv", list(generations_after[0].keys()) if generations_after else [], generations_after)
    write_csv(args.package / "interval_conflicts.csv", list(conflicts_after[0].keys()) if conflicts_after else [], conflicts_after)
    validation = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "passed": passed,
        "input_rows": len(rows), "output_rows": len(output), "records_added": len(additions),
        "decision_counts": dict(Counter(row["PROGRESSION"] for row in decisions)),
        "remaining_gap_candidates": len(gaps_after), "unresolved_applied_gaps": unresolved_applied,
        "duplicate_dimension_ids": duplicate_ids, "dimension_id_mismatches": id_mismatches,
        "unresolved_generation_findings": len(unresolved_generation), "unresolved_interval_conflicts": len(unresolved_conflicts),
        "source_directory_written": False,
    }
    (args.package / "validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    report = f"""# 已确认分支缺口推进

输入为 `{args.input}`。本轮不跨代合并记录；对已确认存在的缺失分支新建独立 `DIMENSION-ID`，对停产年和证据不足项继续保留。

## 结果

- 输入 {len(rows):,} 条，输出 {len(output):,} 条，新建 {len(additions):,} 条已确认分支。
- 新建类型：同代分支连续缺口 {sum(1 for row in decisions if row['PROGRESSION'] == 'ADD_CONFIRMED_BRANCH' and row['DECISION'] == 'RESEARCH_BRANCH_GAP')} 条；整车型缺失 {sum(1 for row in decisions if row['PROGRESSION'] == 'ADD_CONFIRMED_BRANCH' and row['DECISION'] == 'RESEARCH_MODEL_YEAR_GAP')} 条；跨代但已确认的分支 {sum(1 for row in decisions if row['PROGRESSION'] == 'ADD_CONFIRMED_BRANCH' and row['DECISION'] == 'REVIEW_BRANCH_OR_GENERATION_BOUNDARY')} 条。
- 1975 Chevrolet Nova Coupe 已按原厂目录新建为 `gen4 / Coupe / 1975`，不与 Hatchback 合并。
- 已确认停产空档继续保留；证据不足的跨代候选不自动补齐。
- 剩余缺口候选 {len(gaps_after):,} 条；本轮已应用缺口的未解决数为 {len(unresolved_applied)}。
- 机器验收：{'PASS' if passed else 'FAIL'}。

## 文件

- `correct.csv`：本轮全量快照。
- `changes.csv`：新建的已确认分支。
- `branch_gap_decisions.csv`：上一轮全部缺口的推进/保留决定。
- `gap_candidates.csv`：按新快照重算的剩余缺口。
- `generation_findings.csv`、`interval_conflicts.csv`：代际和年份区间验收。
- `validation.json`：机器验收结果。

本轮未写入 `source` 目录。
"""
    (args.package / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
