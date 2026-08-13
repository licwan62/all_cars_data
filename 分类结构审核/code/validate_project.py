from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from id_scheme import dimension_id
OUT = PROJECT / "artifacts"
SOURCE_DIR = ROOT / "source"
SOURCE = SOURCE_DIR / "车型尺寸库.csv"
QUEUE = PROJECT / "research_queue" / "queue.csv"
SPLITS = PROJECT / "research_queue" / "approved_splits.json"
PROTECTED = ["车型尺寸库.csv", "车型尺寸库.xlsx", "车型数据尺码-只有长匹配.xlsx", "车型数据尺码.xlsx", "子车系维护表.csv"]
EXPECTED = {
    "audit_table1_corrections.csv": ["DIMENSION-ID","修改类型","原结构","建议结构","原分类","建议分类","置信度","修改原因","主要依据","是否需要拆分记录"],
    "audit_table2_corrected.csv": ["DIMENSION-ID","结构","分类","迭代状态"],
    "corrected.csv": ["DIMENSION-ID","MAKE","MODEL","版本","CAB","BED","结构","代际","YEAR","分类","L-IN","W-IN","H-IN","参考车型","备注","迭代状态"],
    "audit_table3_uncertain.csv": ["DIMENSION-ID","疑似结构","问题","需要补充的信息","建议处理方式"],
    "audit_table4_split.csv": ["DIMENSION-ID","建议YEAR","建议结构","拆分原因"],
    "audit_table5_other.csv": ["DIMENSION-ID","字段","当前值","疑似问题","建议检查"],
    "audit_full_inventory.csv": ["DIMENSION-ID","输出结构","输出分类","审核结果","修改类型","审核依据"],
}


def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "passed": True, "checks": [], "protected_files": {}}
    for name in PROTECTED:
        path = SOURCE_DIR / name
        report["protected_files"][name] = {"exists": path.exists(), "sha256": sha(path) if path.exists() else None}
        if not path.exists(): report["passed"] = False
    source_header, source_rows = read(SOURCE)
    source_ids = [r["DIMENSION-ID"] for r in source_rows]
    dimension_ids_ok = all(row.get("DIMENSION-ID") == dimension_id(row) for row in source_rows)
    report["checks"].append({"check": "source_dimension_group_ids", "passed": dimension_ids_ok})
    report["passed"] &= dimension_ids_ok
    tables = {}
    for name, expected in EXPECTED.items():
        path = OUT / name
        if not path.exists():
            report["checks"].append({"check": name, "passed": False, "error": "missing"}); report["passed"] = False; continue
        header, rows = read(path); tables[name] = rows
        ok = header == expected
        report["checks"].append({"check": f"{name}:schema", "passed": ok, "rows": len(rows), "actual": header})
        report["passed"] &= ok
    process_t2 = tables.get("audit_table2_corrected.csv", [])
    t2 = tables.get("corrected.csv", [])
    expected_process = {}
    for row in t2:
        projected = {
            field: row.get(field, "") for field in EXPECTED["audit_table2_corrected.csv"]
        }
        previous = expected_process.get(row["DIMENSION-ID"])
        if previous:
            statuses = list(dict.fromkeys(filter(None, previous["迭代状态"].split(" | ") + [projected["迭代状态"]])))
            previous["迭代状态"] = " | ".join(statuses)
        else:
            expected_process[row["DIMENSION-ID"]] = projected
    corrected_alias_ok = process_t2 == list(expected_process.values())
    report["checks"].append({
        "check": "corrected_alias_matches_table2",
        "passed": corrected_alias_ok,
        "table2_rows": len(process_t2),
        "corrected_rows": len(t2),
    })
    report["passed"] &= corrected_alias_ok
    allowed_categories = {"两厢车", "跑车", "三厢车", "越野车", "皮卡"}
    illegal_categories = sorted({r.get("分类", "") for r in t2 if r.get("分类", "") not in allowed_categories})
    category_ok = not illegal_categories
    report["checks"].append({"check": "table2_uses_only_five_cover_categories", "passed": category_ok, "illegal_values": illegal_categories})
    report["passed"] &= category_ok
    split_manifest = json.loads(SPLITS.read_text(encoding="utf-8")) if SPLITS.exists() else []
    polluted_split_dimensions = [
        part.get("DIMENSION-ID", "")
        for item in split_manifest
        for part in item.get("records", [])
        if any("MAKE=" in part.get(field, "") for field in ("L-IN", "W-IN", "H-IN"))
    ]
    split_dimensions_ok = not polluted_split_dimensions
    report["checks"].append({
        "check": "split_dimensions_are_numeric_or_blank",
        "passed": split_dimensions_ok,
        "examples": polluted_split_dimensions[:10],
    })
    report["passed"] &= split_dimensions_ok
    split_originals = {
        item["original_dimension_id"]
        for item in split_manifest
        if any(part["DIMENSION-ID"] not in set(source_ids) for part in item.get("records", []))
    }
    generated_ids = {part["DIMENSION-ID"] for item in split_manifest for part in item.get("records", []) if part["DIMENSION-ID"] != item["original_dimension_id"]}
    output_ids = [r.get("DIMENSION-ID", "") for r in t2]
    preserves_source = Counter(output_ids) == Counter(source_ids)
    generated_present = generated_ids.issubset(set(output_ids))
    id_ok = preserves_source and generated_present and all(output_ids)
    report["checks"].append({
        "check": "table2_preserves_source_and_generated_ids",
        "passed": id_ok,
        "source_rows": len(source_rows), "table2_rows": len(t2), "generated_rows": len(generated_ids),
        "generated_missing": sorted(generated_ids - set(output_ids)),
        "shared_dimension_group_ids": sum(count > 1 for rid, count in Counter(output_ids).items() if rid),
    })
    report["passed"] &= id_ok
    source_by_id = {r["DIMENSION-ID"]: r for r in source_rows}
    t2_by_id = {r["DIMENSION-ID"]: r for r in t2}
    mismatches = []
    for correction in tables.get("audit_table1_corrections.csv", []):
        rid = correction["DIMENSION-ID"]
        if rid not in t2_by_id or t2_by_id[rid].get("结构") != correction.get("建议结构"):
            mismatches.append(rid)
        original = source_by_id.get(rid)
        if original and original.get("结构") != correction.get("原结构"):
            mismatches.append(rid)
    ok = not mismatches
    report["checks"].append({"check": "table1_applied_to_table2", "passed": ok, "mismatch_count": len(set(mismatches)), "examples": sorted(set(mismatches))[:10]})
    report["passed"] &= ok

    _, queue_rows = read(QUEUE)
    blocked_by_id = {r["DIMENSION-ID"]: r for r in queue_rows if r.get("status") == "blocked"}
    table3_ids = {r.get("DIMENSION-ID", "") for r in tables.get("audit_table3_uncertain.csv", [])}
    blocked_sync = set(blocked_by_id) == table3_ids
    report["checks"].append({
        "check": "blocked_queue_equals_table3",
        "passed": blocked_sync,
        "blocked_rows": len(blocked_by_id),
        "table3_rows": len(table3_ids),
        "missing_from_table3": sorted(set(blocked_by_id) - table3_ids)[:10],
        "extra_in_table3": sorted(table3_ids - set(blocked_by_id))[:10],
    })
    report["passed"] &= blocked_sync

    blocked_mismatches = []
    for rid in blocked_by_id:
        source = source_by_id.get(rid)
        output = t2_by_id.get(rid)
        if not source or not output or output.get("结构") != source.get("结构") or output.get("分类") != source.get("分类") or output.get("迭代状态") != "待复核":
            blocked_mismatches.append(rid)
    blocked_ok = not blocked_mismatches
    report["checks"].append({
        "check": "blocked_rows_preserved_and_marked_for_review",
        "passed": blocked_ok,
        "mismatch_count": len(blocked_mismatches),
        "examples": blocked_mismatches[:10],
    })
    report["passed"] &= blocked_ok

    evidence_missing = [r.get("DIMENSION-ID", "") for r in tables.get("audit_table1_corrections.csv", []) if not r.get("主要依据", "").strip()]
    evidence_ok = not evidence_missing
    report["checks"].append({
        "check": "table1_has_traceable_evidence",
        "passed": evidence_ok,
        "missing_count": len(evidence_missing),
        "examples": evidence_missing[:10],
    })
    report["passed"] &= evidence_ok

    done_findings = {}
    for row in queue_rows:
        if row.get("status") == "done" and row.get("suggested_structure"):
            done_findings[row["DIMENSION-ID"]] = row
    expected_changed = {
        rid for rid, finding in done_findings.items()
        if rid in source_by_id and rid not in split_originals and "/" not in finding.get("suggested_structure", "") and (
            source_by_id[rid].get("结构") != finding.get("suggested_structure")
            or (finding.get("suggested_category") and source_by_id[rid].get("分类") != finding.get("suggested_category"))
        )
    }
    expected_changed.update(split_originals)
    table1_ids = {r.get("DIMENSION-ID", "") for r in tables.get("audit_table1_corrections.csv", [])}
    done_sync = expected_changed == table1_ids
    report["checks"].append({
        "check": "done_changed_findings_equal_table1",
        "passed": done_sync,
        "expected_changes": len(expected_changed),
        "table1_rows": len(table1_ids),
        "missing_from_table1": sorted(expected_changed - table1_ids)[:10],
        "extra_in_table1": sorted(table1_ids - expected_changed)[:10],
    })
    report["passed"] &= done_sync

    full_audit = tables.get("audit_full_inventory.csv", [])
    identity_fields = ("DIMENSION-ID",)
    source_fingerprints = Counter(set(tuple(row.get(field, "") for field in identity_fields) for row in source_rows))
    audit_fingerprints = Counter(set(tuple(row.get(field, "") for field in identity_fields) for row in full_audit))
    full_audit_ok = source_fingerprints == audit_fingerprints
    report["checks"].append({
        "check": "full_inventory_audit_covers_every_source_row", "passed": full_audit_ok,
        "source_rows": len(source_rows), "audit_rows": len(full_audit),
        "missing_fingerprints": sum((source_fingerprints - audit_fingerprints).values()),
        "extra_fingerprints": sum((audit_fingerprints - source_fingerprints).values()),
    })
    report["passed"] &= full_audit_ok

    allowed_change_types = {"拆分并发生产品类型变化（重点）", "产品类型变化（重点）", "类型修改（重点）", "结构修改", "拆分记录", "结构改名"}
    bad_change_types = [row["DIMENSION-ID"] for row in tables.get("audit_table1_corrections.csv", []) if row.get("修改类型") not in allowed_change_types]
    change_type_ok = not bad_change_types
    report["checks"].append({"check": "table1_change_types_are_precise", "passed": change_type_ok, "invalid_count": len(bad_change_types), "examples": bad_change_types[:10]})
    report["passed"] &= change_type_ok

    category_changes = [row for row in tables.get("audit_table1_corrections.csv", []) if row.get("原分类") != row.get("建议分类")]
    unflagged_category_changes = [row["DIMENSION-ID"] for row in category_changes if "重点" not in row.get("修改类型", "")]
    category_focus_ok = not unflagged_category_changes
    report["checks"].append({
        "check": "every_product_category_change_is_highlighted", "passed": category_focus_ok,
        "category_change_rows": len(category_changes), "unflagged_count": len(unflagged_category_changes), "examples": unflagged_category_changes[:10],
    })
    report["passed"] &= category_focus_ok
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "validation_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
