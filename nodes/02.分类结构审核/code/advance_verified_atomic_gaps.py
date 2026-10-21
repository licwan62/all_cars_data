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


EPA = "https://www.fueleconomy.gov/ws/rest/vehicle/menu/model"
GM_WAR = "https://www.gm.com/heritage"
LINCOLN_WAR = "https://media.lincoln.com/content/dam/lincolnmedia/lna/us/history/100/vehicles/Lincoln%20100th%20Anniversary%20Fact%20Sheet.pdf"
FORD_2019_EXPLORER = "https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2019/explorer/2019-explorer.pdf"


# Only records whose exact model year and body atom were independently confirmed.
# value=(new year interval, generation, donor side, evidence)
CONFIRMED_ADDITIONS = {
    ("Acura", "RDX", "", "", "", "SUV", "2019"):
        ("2019", "gen3", "RIGHT", f"{EPA}?year=2019&make=Acura"),
    ("Ford", "Explorer", "", "", "", "SUV", "2019"):
        ("2019", "gen5", "LEFT", FORD_2019_EXPLORER),
    ("Honda", "HR-V", "", "", "", "SUV", "2022"):
        ("2022", "gen1", "LEFT", f"{EPA}?year=2022&make=Honda"),
    ("Ford", "Crown Victoria", "", "", "", "Sedan", "1989-1991"):
        ("1989-1991", "gen1", "LEFT", f"{EPA}?year=1989&make=Ford"),
    ("Ford", "Thunderbird", "", "", "", "Coupe", "1987-1988"):
        ("1987-1988", "gen9", "LEFT", f"{EPA}?year=1987&make=Ford"),
}


# These are real rows with one inconsistent body label, not missing parallel atoms.
STRUCTURE_CORRECTIONS = {
    "Scion xB Wagon 2008-2010": {
        "结构": "Hatchback",
        "reason": "同一代 xB 单一五门车身被前后记录登记为 Hatchback；Wagon 不是独立并行分支。",
        "evidence": f"{EPA}?year=2008&make=Scion",
    }
}


# key matches a gap candidate. These candidates must remain absent; they are not
# permission to synthesize one record per missing year.
CONFIRMED_HIATUS = {
    ("Buick", "Roadmaster", "", "", "", "Convertible", "1943-1945"): ("战时停止民用乘用车生产。", GM_WAR),
    ("Buick", "Roadmaster", "", "", "", "Coupe", "1943-1945"): ("战时停止民用乘用车生产。", GM_WAR),
    ("Buick", "Roadmaster", "", "", "", "Sedan", "1943-1945"): ("战时停止民用乘用车生产。", GM_WAR),
    ("Chevrolet", "Suburban", "", "", "", "SUV", "1942-1945"): ("GM 转入战时生产，不补民用 Suburban 原子。", GM_WAR),
    ("Lincoln", "Continental", "", "", "", "Convertible", "1943-1945"): ("Lincoln 于 1942-01-30 停止常规生产，1946 年款恢复。", LINCOLN_WAR),
    ("Lincoln", "Continental", "", "", "", "Coupe", "1943-1945"): ("Lincoln 于 1942-01-30 停止常规生产，1946 年款恢复。", LINCOLN_WAR),
    ("Chevrolet", "Silverado 1500HD", "", "Crew", "6.6", "Pickup", "2004"): ("EPA 2004 Chevrolet 车型菜单无 Silverado 1500HD；不以普通 1500/2500HD 替代。", f"{EPA}?year=2004&make=Chevrolet"),
    ("Dodge", "Viper", "", "", "", "Coupe", "2007"): ("EPA 2007 Dodge 车型菜单无 Viper。", f"{EPA}?year=2007&make=Dodge"),
    ("Porsche", "911", "GT3 RS", "", "", "Coupe", "2017-2018"): ("GT3 RS 衍生版本年款空档。", f"{EPA}?year=2017&make=Porsche"),
    ("Porsche", "911", "Turbo", "", "", "Coupe", "1981-1985"): ("美国市场 Turbo 年款空档，不用欧洲生产年补齐。", f"{EPA}?year=1985&make=Porsche"),
    ("Acura", "CL", "", "", "", "Coupe", "2000"): ("EPA 2000 Acura 车型菜单无 CL。", f"{EPA}?year=2000&make=Acura"),
    ("Acura", "MDX", "", "", "", "SUV", "2021"): ("EPA 2021 Acura 车型菜单无 MDX。", f"{EPA}?year=2021&make=Acura"),
    ("Nissan", "Maxima", "", "", "", "Sedan", "2015"): ("EPA 2015 Nissan 车型菜单无 Maxima。", f"{EPA}?year=2015&make=Nissan"),
    ("Volkswagen", "Passat", "", "", "", "Sedan", "2011"): ("EPA 2011 Volkswagen 车型菜单无 Passat。", f"{EPA}?year=2011&make=Volkswagen"),
    ("Scion", "xB", "", "", "", "Hatchback", "2007"): ("EPA 2007 Scion 车型菜单无 xB；第二代从 2008 年款开始。", f"{EPA}?year=2007&make=Scion"),
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def identity(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in IDENTITY)


def gap_key(row: dict[str, str]) -> tuple[str, ...]:
    return (*identity(row), row["MISSING_YEAR"])


def find_donor(rows: list[dict[str, str]], gap: dict[str, str], side: str) -> dict[str, str]:
    donor_year = gap["LEFT_YEAR"] if side == "LEFT" else gap["RIGHT_YEAR"]
    matches = [row for row in rows if identity(row) == identity(gap) and row["YEAR"] == donor_year]
    if len(matches) != 1:
        raise SystemExit(f"donor not unique: {gap_key(gap)} side={side} count={len(matches)}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Advance only verified atomic branch gaps.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--gap-report", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true", help="Regenerate the same in-progress batch directory.")
    args = parser.parse_args()
    ensure_not_source(args.package)
    args.package.mkdir(parents=True, exist_ok=args.overwrite)

    fields, rows = read_csv(args.input)
    _, prior_gaps = read_csv(args.gap_report)
    changes: list[dict[str, str]] = []

    # Correct aliases before detecting or adding gaps. This changes the ID rather
    # than creating a second record for the same physical car.
    corrected_old_ids: set[str] = set()
    for row in rows:
        old_id = row["DIMENSION-ID"]
        spec = STRUCTURE_CORRECTIONS.get(old_id)
        if not spec:
            continue
        corrected_old_ids.add(old_id)
        row["结构"] = spec["结构"]
        row["备注"] = (row.get("备注", "") + "；" if row.get("备注") else "") + spec["reason"]
        row["DIMENSION-ID"] = dimension_id(row)
        changes.append({
            "ACTION": "CORRECT_STRUCTURE_ALIAS", "DIMENSION_ID_BEFORE": old_id,
            "DIMENSION_ID_AFTER": row["DIMENSION-ID"], "MAKE": row["MAKE"], "MODEL": row["MODEL"],
            "VERSION": row.get("版本", ""), "CAB": row.get("CAB", ""), "BED": row.get("BED", ""),
            "STRUCTURE": row["结构"], "GENERATION": row["代际"], "YEAR": row["YEAR"],
            "DONOR_DIMENSION_ID": "", "REASON": spec["reason"], "EVIDENCE": spec["evidence"],
        })

    additions: list[dict[str, str]] = []
    applied_gap_keys: set[tuple[str, ...]] = set()
    for gap in prior_gaps:
        key = gap_key(gap)
        spec = CONFIRMED_ADDITIONS.get(key)
        if not spec:
            continue
        year, generation, side, evidence = spec
        donor = find_donor(rows, gap, side)
        record = dict(donor)
        record["YEAR"] = year
        record["代际"] = generation
        record["参考车型"] = f"{year} {gap['MAKE']} {gap['MODEL']} {gap['结构']}"
        record["备注"] = f"存在性已核实；外廓暂沿用 {donor['YEAR']} 同分支记录，尺寸待专项复核。"
        record["迭代状态"] = "待补尺寸"
        record["DIMENSION-ID"] = dimension_id(record)
        additions.append(record)
        applied_gap_keys.add(key)
        changes.append({
            "ACTION": "ADD_VERIFIED_ATOM", "DIMENSION_ID_BEFORE": "",
            "DIMENSION_ID_AFTER": record["DIMENSION-ID"], "MAKE": record["MAKE"], "MODEL": record["MODEL"],
            "VERSION": record.get("版本", ""), "CAB": record.get("CAB", ""), "BED": record.get("BED", ""),
            "STRUCTURE": record["结构"], "GENERATION": generation, "YEAR": year,
            "DONOR_DIMENSION_ID": donor["DIMENSION-ID"],
            "REASON": "年款与车身原子均已确认存在；独立补建，不跨代合并。", "EVIDENCE": evidence,
        })

    output = rows + additions
    output.sort(key=lambda r: (r["MAKE"], r["MODEL"], r.get("版本", ""), r.get("结构", ""), r["YEAR"], r.get("CAB", ""), r.get("BED", "")))
    ids = [row["DIMENSION-ID"] for row in output]
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if count > 1)
    id_mismatches = [row["DIMENSION-ID"] for row in output if row["DIMENSION-ID"] != dimension_id(row)]
    gaps_after = audit_gaps(output)

    decisions: list[dict[str, str]] = []
    for gap in gaps_after:
        key = gap_key(gap)
        if key in CONFIRMED_HIATUS:
            reason, evidence = CONFIRMED_HIATUS[key]
            disposition = "CONFIRMED_HIATUS_DO_NOT_ADD"
        else:
            reason, evidence = "尚未确认缺失区间内存在同一原子记录。", ""
            disposition = "PENDING_REVIEW"
        decisions.append({**gap, "DISPOSITION": disposition, "REVIEW_REASON": reason, "REVIEW_EVIDENCE": evidence})
    pending = [row for row in decisions if row["DISPOSITION"] == "PENDING_REVIEW"]

    generations = audit_generations(output)
    conflicts = audit_interval_conflicts(output, Decimal("0.1"))
    unresolved_generation = [row for row in generations if row.get("DECISION") == "REVIEW_ONLY"]
    unresolved_conflicts = [row for row in conflicts if row.get("DECISION") == "REVIEW_ONLY"]
    remaining_keys = {gap_key(row) for row in gaps_after}
    unresolved_applied = sorted(" | ".join(key) for key in applied_gap_keys & remaining_keys)
    passed = not duplicate_ids and not id_mismatches and not unresolved_applied and not unresolved_generation and not unresolved_conflicts

    write_csv(args.package / "correct.csv", fields, output)
    change_fields = ["ACTION", "DIMENSION_ID_BEFORE", "DIMENSION_ID_AFTER", "MAKE", "MODEL", "VERSION", "CAB", "BED", "STRUCTURE", "GENERATION", "YEAR", "DONOR_DIMENSION_ID", "REASON", "EVIDENCE"]
    write_csv(args.package / "changes.csv", change_fields, changes)
    decision_fields = [*gaps_after[0].keys(), "DISPOSITION", "REVIEW_REASON", "REVIEW_EVIDENCE"] if gaps_after else []
    write_csv(args.package / "candidate_decisions.csv", decision_fields, decisions)
    write_csv(args.package / "gap_candidates.csv", list(gaps_after[0].keys()) if gaps_after else [], gaps_after)
    write_csv(args.package / "pending_gap_candidates.csv", decision_fields, pending)
    write_csv(args.package / "generation_findings.csv", list(generations[0].keys()) if generations else [], generations)
    write_csv(args.package / "interval_conflicts.csv", list(conflicts[0].keys()) if conflicts else [], conflicts)

    validation = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "passed": passed,
        "input_rows": len(rows), "output_rows": len(output), "records_added": len(additions),
        "records_corrected": len(corrected_old_ids), "raw_gap_candidates": len(gaps_after),
        "confirmed_hiatus_candidates": sum(row["DISPOSITION"] == "CONFIRMED_HIATUS_DO_NOT_ADD" for row in decisions),
        "pending_gap_candidates": len(pending), "unresolved_applied_gaps": unresolved_applied,
        "duplicate_dimension_ids": duplicate_ids, "dimension_id_mismatches": id_mismatches,
        "unresolved_generation_findings": len(unresolved_generation), "unresolved_interval_conflicts": len(unresolved_conflicts),
        "source_directory_written": False,
    }
    (args.package / "validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    report = f"""# 已核实原子缺口推进

本轮坚持“原子存在性优先”：只有年款、车型和车身分支同时得到证据支持才新增；结构别名纠正原记录；停产/跳过年款登记为空档，不生成记录。

## 结果

- 输入 {len(rows):,} 条，输出 {len(output):,} 条。
- 新增已核实原子 {len(additions)} 条：2019 Acura RDX、2019 Ford Explorer、2022 Honda HR-V、1989–1991 Ford Crown Victoria、1987–1988 Ford Thunderbird。
- 纠正结构别名 {len(corrected_old_ids)} 条：2008–2010 Scion xB `Wagon` 改为 `Hatchback`，未复制平行原子。
- 已确认且禁止补建的空档候选 {validation['confirmed_hiatus_candidates']} 个，包括二战民用生产中止、2004 Silverado 1500HD、2007 Viper，以及已核实的跳年款。
- 原始连续性候选 {len(gaps_after)} 个；剔除已确认空档后，实际待复核 {len(pending)} 个。
- 已应用缺口仍残留 {len(unresolved_applied)} 个；机器验收：{'PASS' if passed else 'FAIL'}。

## 边界

- 新增记录的尺寸只是邻近同分支占位，均标为 `待补尺寸`，没有把尺寸相同当作存在性证据。
- `candidate_decisions.csv` 保留所有候选及处理结论；`pending_gap_candidates.csv` 才是下一轮工作队列。
- 本轮未写入 `source` 目录。
"""
    (args.package / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
