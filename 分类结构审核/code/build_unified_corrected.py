from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path


if str(Path(__file__).resolve().parents[2]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from id_scheme import dimension_id


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
ARTIFACTS = PROJECT / "artifacts"
AUDIT = ARTIFACTS / "audit"
REVIEWS = ARTIFACTS / "reviews"
VALIDATION_DIR = ARTIFACTS / "validation"
SOURCE = ROOT / "source" / "车型尺寸库.csv"
CORRECTED = ARTIFACTS / "corrected.csv"
YEAR_REVIEW = REVIEWS / "year_reference_review.csv"
US_REVIEW = REVIEWS / "us_market_dimension_review.csv"
BODY_REVIEW = REVIEWS / "sedan_coupe_same_dimension_review.csv"
VERSION_DECISIONS = PROJECT / "research_queue" / "version_normalization_decisions.json"
VERSION_REVIEW = REVIEWS / "version_normalization_review.csv"
VERSION_REDUNDANCY_CANDIDATES = REVIEWS / "version_redundancy_candidates.csv"
LOG = AUDIT / "unified_corrected_application_log.csv"
VALIDATION = VALIDATION_DIR / "unified_corrected_validation.json"
STANDARD_VALIDATION = ARTIFACTS / "validation_report.json"

FIELDS = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际", "YEAR", "分类", "L-IN", "W-IN", "H-IN", "参考车型", "备注", "迭代状态"]
AUDIT2_FIELDS = ["DIMENSION-ID", "结构", "分类", "迭代状态"]
LOG_FIELDS = ["SOURCE_LINE", "LAYER", "ACTION", "DIMENSION-ID_BEFORE", "DIMENSION-ID_AFTER", "VALUE_BEFORE", "VALUE_AFTER", "REASON", "EVIDENCE"]
VERSION_REVIEW_FIELDS = ["SOURCE_LINE", "ACTION", "DIMENSION-ID_BEFORE", "DIMENSION-ID_AFTER", "MAKE", "MODEL", "STRUCTURE", "YEAR", "CURRENT_VERSION", "PROPOSED_VERSION", "LWH", "CANONICAL_DIMENSION-ID", "REASON"]
VERSION_CANDIDATE_FIELDS = ["DIMENSION-ID", "MAKE", "MODEL", "VERSION", "STRUCTURE", "YEAR", "CAB", "BED", "LWH", "DEFAULT_DIMENSION-ID", "DEFAULT_YEAR", "DEFAULT_LWH", "DELTA_L", "DELTA_W", "DELTA_H", "DECISION", "REASON"]

# Only deterministic year-reference conclusions are auto-applied. Rows with ranges,
# approximations, configuration dependence, or an explicit confirmation request stay pending.
YEAR_DELETE_LINES = {948, 968, 969, 970, 971, 974, 976, 978, 979, 980, 981, 982, 985, 3357}
YEAR_DIMENSION_LINES = {1344, 2082, 2659, 2980, 2986, 3025, 3032, 3083, 3443, 3522, 3879, 4226, 4335, 4435, 4490, 4491}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def lwh(row: dict[str, str]) -> str:
    return f'{row.get("L-IN", "")}x{row.get("W-IN", "")}x{row.get("H-IN", "")}'


def parse_lwh(value: str) -> tuple[str, str, str]:
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)\s*", value)
    if not match:
        raise ValueError(f"Not an exact numeric LWH value: {value!r}")
    return match.group(1), match.group(2), match.group(3)


def append_note(row: dict[str, str], note: str) -> None:
    current = row.get("备注", "").strip()
    if note not in current:
        row["备注"] = f"{current}；{note}" if current else note


def rebuild_dimension_id(row: dict[str, str]) -> str:
    return dimension_id(row)


def year_range(value: str) -> tuple[int, int] | None:
    years = [int(item) for item in re.findall(r"\d{4}", value or "")]
    return (years[0], years[-1]) if years else None


def year_contains(container: str, contained: str) -> bool:
    outer, inner = year_range(container), year_range(contained)
    return bool(outer and inner and outer[0] <= inner[0] and outer[1] >= inner[1])


def year_overlaps(left: str, right: str) -> bool:
    a, b = year_range(left), year_range(right)
    return bool(a and b and a[0] <= b[1] and b[0] <= a[1])


def is_already_unified(rows: list[dict[str, str]]) -> bool:
    by_id = {row.get("DIMENSION-ID", ""): row for row in rows}
    return all([
        "GMC Jimmy 2dr SUV 1983-1994" in by_id,
        "GMC Jimmy SUV 1983-1994" not in by_id,
        "Chevrolet Cobalt SS Coupe 2005-2010" not in by_id,
        "Toyota Tercel Sedan 1995-1998" in by_id,
        by_id.get("Audi A8/S8 Sedan 2019-2026", {}).get("L-IN") == "209.5",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build unified corrected.csv and optionally export historical stage snapshots.")
    parser.add_argument("--export-year-us-dir", type=Path, help="New directory for the year-reference + US-market stage package.")
    parser.add_argument("--export-sedan-coupe-dir", type=Path, help="New directory for the subsequent Sedan/Coupe stage package.")
    args = parser.parse_args()
    AUDIT.mkdir(parents=True, exist_ok=True)
    REVIEWS.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    def export_stage(directory: Path | None, stage_rows: list[dict[str, str]], stage_logs: list[dict[str, str]]) -> None:
        if directory is None:
            return
        directory = directory if directory.is_absolute() else ROOT / directory
        directory.mkdir(parents=True, exist_ok=False)
        write_csv(directory / "correct.csv", FIELDS, stage_rows)
        write_csv(directory / "changes.csv", LOG_FIELDS, stage_logs)

    source_probe = read_csv(SOURCE)
    if is_already_unified(source_probe):
        if args.export_year_us_dir or args.export_sedan_coupe_dir:
            raise SystemExit("源表已包含全部统一修复，不能从当前源表重新导出历史阶段快照；请使用 changes/ 中的既有快照。")
        subprocess.run([sys.executable, str(PROJECT / "code" / "regenerate_artifacts.py")], cwd=ROOT, check=True)
        # The migrated source is already the approved final dataset. Preserve
        # it byte-for-byte as the canonical corrected output; regeneration is
        # used only to refresh derived audit tables.
        shutil.copyfile(SOURCE, CORRECTED)
        rows = read_csv(CORRECTED)
        audit2_rows = read_csv(AUDIT / "audit_table2_corrected.csv")
        checks = {
            "source_detected_as_already_unified": True,
            "corrected_matches_source": rows == source_probe,
            "corrected_row_count": len(rows) == 4756,
            "audit_table2_present": bool(audit2_rows),
        }
        validation = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "passed": all(checks.values()),
            "mode": "source_already_unified",
            "corrected_rows": len(rows),
            "applied_actions": 0,
            "checks": checks,
            "note": "受保护源表已包含全部历史审核层；本次只重建派生产物，未重复套用旧 SOURCE_LINE。",
        }
        validation_text = json.dumps(validation, ensure_ascii=False, indent=2)
        VALIDATION.write_text(validation_text, encoding="utf-8")
        STANDARD_VALIDATION.write_text(validation_text, encoding="utf-8")
        print(validation_text)
        if not validation["passed"]:
            raise SystemExit(1)
        return

    # Always rebuild the structure-review base first. This makes the overlay
    # deterministic and prevents a second run from applying changes twice.
    subprocess.run([sys.executable, str(PROJECT / "code" / "regenerate_artifacts.py")], cwd=ROOT, check=True)

    source_rows = read_csv(SOURCE)
    rows = read_csv(CORRECTED)
    year_rows = read_csv(YEAR_REVIEW)
    us_rows = read_csv(US_REVIEW)
    body_rows = read_csv(BODY_REVIEW)
    version_decisions = json.loads(VERSION_DECISIONS.read_text(encoding="utf-8"))

    # Link review source-line numbers to their corresponding rows in the generated base.
    # Matching includes current dimensions so shared DIMENSION-IDs remain distinguishable.
    unassigned = set(range(len(rows)))
    row_by_source_line: dict[int, dict[str, str]] = {}
    for source_index, source_row in enumerate(source_rows):
        source_line = source_index + 2
        candidates = [
            index for index in unassigned
            if rows[index].get("DIMENSION-ID") == source_row.get("DIMENSION-ID") and lwh(rows[index]) == lwh(source_row)
        ]
        if candidates:
            chosen = candidates[0]
            unassigned.remove(chosen)
            row_by_source_line[source_line] = rows[chosen]
    source_line_by_object = {id(row): source_line for source_line, row in row_by_source_line.items()}

    logs: list[dict[str, str]] = []
    deleted_objects: set[int] = set()

    def target(source_line: int) -> dict[str, str]:
        row = row_by_source_line.get(source_line)
        if row is None:
            raise RuntimeError(f"Could not map source line {source_line} to regenerated corrected.csv")
        return row

    def log(source_line: int, layer: str, action: str, row: dict[str, str], before_id: str, before: str, after: str, reason: str, evidence: str) -> None:
        logs.append({
            "SOURCE_LINE": str(source_line), "LAYER": layer, "ACTION": action,
            "DIMENSION-ID_BEFORE": before_id, "DIMENSION-ID_AFTER": row.get("DIMENSION-ID", "") if action != "DELETE" else "",
            "VALUE_BEFORE": before, "VALUE_AFTER": after, "REASON": reason, "EVIDENCE": evidence,
        })

    def delete(source_line: int, layer: str, reason: str, evidence: str) -> None:
        row = target(source_line)
        if id(row) in deleted_objects:
            return
        before_id = row["DIMENSION-ID"]
        deleted_objects.add(id(row))
        log(source_line, layer, "DELETE", row, before_id, lwh(row), "", reason, evidence)

    def update_dimensions(source_line: int, proposed: str, layer: str, reason: str, evidence: str) -> None:
        row = target(source_line)
        before_id, before = row["DIMENSION-ID"], lwh(row)
        length, width, height = parse_lwh(proposed)
        row["L-IN"], row["W-IN"], row["H-IN"] = length, width, height
        append_note(row, f"{layer} 尺寸复核修正")
        log(source_line, layer, "UPDATE_DIMENSIONS", row, before_id, before, lwh(row), reason, evidence)

    year_by_line = {int(item["SOURCE_LINE"]): item for item in year_rows}
    for source_line in sorted(YEAR_DELETE_LINES):
        item = year_by_line[source_line]
        delete(source_line, "year_reference", item["RECOMMENDATION"], item["EVIDENCE"])
    for source_line in sorted(YEAR_DIMENSION_LINES):
        item = year_by_line[source_line]
        update_dimensions(source_line, item["PROPOSED_LWH"], "year_reference", item["RECOMMENDATION"], item["EVIDENCE"])

    for item in us_rows:
        source_line = int(item["SOURCE_LINE"])
        proposed = f'{item["PROPOSED_L"]}x{item["PROPOSED_W"]}x{item["PROPOSED_H"]}'
        update_dimensions(source_line, proposed, "us_market", item["REASON"], item["EVIDENCE"])

    # The corrected generic A8/S8 row now represents the actual US long-wheelbase body.
    # Remove the separate LWB-labelled duplicate to keep the consumer-facing US name canonical.
    delete(154, "us_market", "美规 A8/S8 已由通用显示名行按 209.5 英寸长轴车身覆盖；删除 LWB 重复适配项", "https://www.audiusa.com/en/models/a8/a8/2026/overview/")

    year_us_log_count = len(logs)
    export_stage(args.export_year_us_dir, [row for row in rows if id(row) not in deleted_objects], list(logs))

    for item in body_rows:
        source_line = int(item["SOURCE_LINE"])
        action = item["PROPOSED_ACTION"]
        if action == "DELETE_DUPLICATE":
            delete(source_line, "sedan_coupe", item["REASON"], item["EVIDENCE"])
        elif action == "UPDATE_DIMENSIONS":
            update_dimensions(source_line, item["PROPOSED_LWH"], "sedan_coupe", item["REASON"], item["EVIDENCE"])
        elif action == "REKEY_YEAR":
            row = target(source_line)
            before_id, before_year = row["DIMENSION-ID"], row["YEAR"]
            row["YEAR"] = item["PROPOSED_YEAR"]
            row["DIMENSION-ID"] = rebuild_dimension_id(row)
            if before_year in row.get("参考车型", ""):
                row["参考车型"] = row["参考车型"].replace(before_year, row["YEAR"])
            append_note(row, "美国市场年份复核修正")
            log(source_line, "sedan_coupe", "REKEY_YEAR", row, before_id, before_year, row["YEAR"], item["REASON"], item["EVIDENCE"])
        else:
            raise ValueError(f"Unsupported body review action {action!r}")

    export_stage(
        args.export_sedan_coupe_dir,
        [row for row in rows if id(row) not in deleted_objects],
        list(logs[year_us_log_count:]),
    )

    pre_version_rows = [dict(row) for row in rows if id(row) not in deleted_objects]
    version_review_rows: list[dict[str, str]] = []
    live_by_id = {row["DIMENSION-ID"]: row for row in rows if id(row) not in deleted_objects}

    for decision in version_decisions["version_updates"]:
        before_id = decision["dimension_id"]
        row = live_by_id.get(before_id)
        if row is None:
            raise RuntimeError(f"Version-normalization target missing: {before_id}")
        before_version = row.get("版本", "")
        row["版本"] = decision["proposed_version"]
        row["DIMENSION-ID"] = rebuild_dimension_id(row)
        append_note(row, "VERSION 门数/版本规范化")
        after_id = row["DIMENSION-ID"]
        live_by_id.pop(before_id)
        if after_id in live_by_id:
            raise RuntimeError(f"Version normalization would create duplicate DIMENSION-ID: {after_id}")
        live_by_id[after_id] = row
        source_line = source_line_by_object.get(id(row), 0)
        log(source_line, "version_normalization", "REKEY_VERSION", row, before_id, before_version, row["版本"], decision["reason"], "")
        version_review_rows.append({
            "SOURCE_LINE": str(source_line), "ACTION": "REKEY_VERSION", "DIMENSION-ID_BEFORE": before_id,
            "DIMENSION-ID_AFTER": after_id, "MAKE": row["MAKE"], "MODEL": row["MODEL"], "STRUCTURE": row["结构"],
            "YEAR": row["YEAR"], "CURRENT_VERSION": before_version, "PROPOSED_VERSION": row["版本"], "LWH": lwh(row),
            "CANONICAL_DIMENSION-ID": "", "REASON": decision["reason"],
        })

    redundant_ids = set(version_decisions["redundant_version_ids"])
    for redundant_id in version_decisions["redundant_version_ids"]:
        row = live_by_id.get(redundant_id)
        if row is None:
            raise RuntimeError(f"Redundant-version target missing: {redundant_id}")
        canonical_candidates = [
            other for other in rows
            if id(other) not in deleted_objects and other is not row
            and not other.get("版本", "")
            and (other.get("MAKE"), other.get("MODEL"), other.get("结构"), other.get("CAB"), other.get("BED"))
                == (row.get("MAKE"), row.get("MODEL"), row.get("结构"), row.get("CAB"), row.get("BED"))
            and lwh(other) == lwh(row) and year_contains(other.get("YEAR", ""), row.get("YEAR", ""))
        ]
        if not canonical_candidates:
            raise RuntimeError(f"No exact full-year default record covers redundant version: {redundant_id}")
        canonical = canonical_candidates[0]
        variant_reference = row.get("参考车型", "").strip()
        if variant_reference and variant_reference not in canonical.get("参考车型", ""):
            canonical["参考车型"] = f'{canonical.get("参考车型", "").strip()} / {variant_reference}'.strip(" / ")
        append_note(canonical, f'已并入 VERSION={row.get("版本", "")} 的同外廓记录')
        if row.get("备注", "").strip():
            append_note(canonical, f'原 {row.get("版本", "")} 备注：{row["备注"].strip()}')
        deleted_objects.add(id(row))
        live_by_id.pop(redundant_id)
        source_line = source_line_by_object.get(id(row), 0)
        reason = "默认 VERSION 记录已完整覆盖相同年份、结构、CAB/BED 与三维；版本不影响车罩外廓，合并到普通记录"
        log(source_line, "version_normalization", "DELETE_REDUNDANT_VERSION", row, redundant_id, lwh(row), canonical["DIMENSION-ID"], reason, "")
        version_review_rows.append({
            "SOURCE_LINE": str(source_line), "ACTION": "DELETE_REDUNDANT_VERSION", "DIMENSION-ID_BEFORE": redundant_id,
            "DIMENSION-ID_AFTER": "", "MAKE": row["MAKE"], "MODEL": row["MODEL"], "STRUCTURE": row["结构"],
            "YEAR": row["YEAR"], "CURRENT_VERSION": row["版本"], "PROPOSED_VERSION": "", "LWH": lwh(row),
            "CANONICAL_DIMENSION-ID": canonical["DIMENSION-ID"], "REASON": reason,
        })

    # Produce the broader near-dimension queue without auto-merging it. Small
    # differences can reflect ride height, aero kits, wheelbase, or body style.
    candidate_rows: list[dict[str, str]] = []
    for row in pre_version_rows:
        if not row.get("版本", ""):
            continue
        defaults = [
            other for other in pre_version_rows
            if not other.get("版本", "")
            and (other.get("MAKE"), other.get("MODEL"), other.get("结构"), other.get("CAB"), other.get("BED"))
                == (row.get("MAKE"), row.get("MODEL"), row.get("结构"), row.get("CAB"), row.get("BED"))
            and year_overlaps(other.get("YEAR", ""), row.get("YEAR", ""))
        ]
        scored = []
        for default in defaults:
            try:
                deltas = tuple(abs(float(row[field]) - float(default[field])) for field in ("L-IN", "W-IN", "H-IN"))
            except (TypeError, ValueError):
                continue
            if deltas[0] <= 1.0 and deltas[1] <= 0.5 and deltas[2] <= 1.0:
                scored.append((sum(deltas), deltas, default))
        if not scored:
            continue
        _, deltas, default = min(scored, key=lambda item: (item[0], item[2]["YEAR"]))
        selected = row["DIMENSION-ID"] in redundant_ids
        candidate_rows.append({
            "DIMENSION-ID": row["DIMENSION-ID"], "MAKE": row["MAKE"], "MODEL": row["MODEL"], "VERSION": row["版本"],
            "STRUCTURE": row["结构"], "YEAR": row["YEAR"], "CAB": row.get("CAB", ""), "BED": row.get("BED", ""), "LWH": lwh(row),
            "DEFAULT_DIMENSION-ID": default["DIMENSION-ID"], "DEFAULT_YEAR": default["YEAR"], "DEFAULT_LWH": lwh(default),
            "DELTA_L": f"{deltas[0]:.1f}", "DELTA_W": f"{deltas[1]:.1f}", "DELTA_H": f"{deltas[2]:.1f}",
            "DECISION": "AUTO_MERGE_EXACT" if selected else "REVIEW_ONLY",
            "REASON": "白名单确认三维和完整年份均由默认记录覆盖" if selected else "尺寸接近但可能存在车身、轴距、离地高度或套件差异，未自动合并",
        })

    write_csv(VERSION_REVIEW, VERSION_REVIEW_FIELDS, version_review_rows)
    write_csv(VERSION_REDUNDANCY_CANDIDATES, VERSION_CANDIDATE_FIELDS, candidate_rows)

    final_rows = [row for row in rows if id(row) not in deleted_objects]
    write_csv(CORRECTED, FIELDS, final_rows)

    audit2: OrderedDict[str, dict[str, str]] = OrderedDict()
    for row in final_rows:
        projected = {field: row.get(field, "") for field in AUDIT2_FIELDS}
        previous = audit2.get(row["DIMENSION-ID"])
        if previous:
            statuses = list(dict.fromkeys(filter(None, previous["迭代状态"].split(" | ") + [projected["迭代状态"]])))
            previous["迭代状态"] = " | ".join(statuses)
        else:
            audit2[row["DIMENSION-ID"]] = projected
    write_csv(AUDIT / "audit_table2_corrected.csv", AUDIT2_FIELDS, list(audit2.values()))
    write_csv(LOG, LOG_FIELDS, logs)

    duplicate_ids = [rid for rid, count in __import__("collections").Counter(row["DIMENSION-ID"] for row in final_rows).items() if count > 1]
    by_id = {row["DIMENSION-ID"]: row for row in final_rows}
    expected_results = {
        "audi_us_body": by_id.get("Audi A8/S8 Sedan 2019-2026", {}).get("L-IN") == "209.5",
        "audi_lwb_duplicate_removed": "Audi A8/S8 LWB Sedan 2019-2026" not in by_id,
        "bmw_e30_coupe_removed": "BMW 3 Series Coupe 1984-1991" not in by_id,
        "sentra_b13_coupe_removed": "Nissan Sentra Coupe 1991-1992" not in by_id,
        "tercel_coupe_removed": "Toyota Tercel Coupe 1995-1999" not in by_id,
        "tercel_sedan_year_corrected": "Toyota Tercel Sedan 1995-1998" in by_id,
        "cobalt_sedan_dimensions": lwh(by_id.get("Chevrolet Cobalt Sedan 2005-2010", {})) == "180.3x67.9x57.1",
        "cobalt_coupe_umbrella_dimensions": lwh(by_id.get("Chevrolet Cobalt Coupe 2005-2010", {})) == "180.5x67.9x55.5",
        "cobalt_ss_redundant_removed": "Chevrolet Cobalt SS Coupe 2005-2010" not in by_id,
        "jimmy_2dr_version": "GMC Jimmy 2dr SUV 1983-1994" in by_id,
        "jimmy_4dr_default": "GMC Jimmy SUV 1991-1994" in by_id,
        "wrangler_unlimited_rubicon": "Jeep Wrangler 2dr Unlimited Rubicon SUV 2005-2006" in by_id,
        "all_version_decisions_applied": len(version_review_rows) == len(version_decisions["version_updates"]) + len(version_decisions["redundant_version_ids"]),
        "audit_table2_matches_corrected": read_csv(AUDIT / "audit_table2_corrected.csv") == list(audit2.values()),
        "expected_action_count": len(logs) == 59 + len(version_review_rows),
        "expected_delete_count": len(deleted_objects) == 18 + len(version_decisions["redundant_version_ids"]),
    }
    validation = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": all(expected_results.values()),
        "base_rows": len(rows),
        "corrected_rows": len(final_rows),
        "deleted_rows": len(deleted_objects),
        "applied_actions": len(logs),
        "checks": expected_results,
        "dimension_id_note": "DIMENSION-ID is retained as the source traceability key for pre-existing structure corrections; only explicit identity corrections are re-keyed.",
        "duplicate_dimension_id_groups": len(duplicate_ids),
        "version_normalization_actions": len(version_review_rows),
        "version_redundancy_candidates": len(candidate_rows),
        "non_auto_applied_year_reference_rows": sorted(set(year_by_line) - YEAR_DELETE_LINES - YEAR_DIMENSION_LINES),
    }
    validation_text = json.dumps(validation, ensure_ascii=False, indent=2)
    VALIDATION.write_text(validation_text, encoding="utf-8")
    STANDARD_VALIDATION.write_text(validation_text, encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
