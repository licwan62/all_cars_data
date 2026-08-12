from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "artifacts"
SOURCE = ROOT / "车型尺寸库.csv"
PROTECTED = ["车型尺寸库.csv", "车型尺寸库.xlsx", "车型数据尺码-只有长匹配.xlsx", "车型数据尺码.xlsx", "子车系维护表.csv"]
EXPECTED = {
    "audit_table1_corrections.csv": ["record_id","MAKE","MODEL","版本","YEAR","原结构","建议结构","原分类","建议分类","置信度","修改原因","主要依据","是否需要拆分记录"],
    "audit_table2_corrected.csv": ["record_id","MAKE","MODEL","版本","CAB","BED","结构","代际","YEAR","分类","L-IN","W-IN","H-IN","参考车型","备注","迭代状态"],
    "audit_table3_uncertain.csv": ["record_id","MAKE","MODEL","版本","YEAR","当前结构","疑似结构","问题","需要补充的信息","建议处理方式"],
    "audit_table4_split.csv": ["record_id","MAKE","MODEL","当前YEAR","当前结构","建议YEAR","建议结构","拆分原因"],
    "audit_table5_other.csv": ["record_id","字段","当前值","疑似问题","建议检查"],
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
        path = ROOT / name
        report["protected_files"][name] = {"exists": path.exists(), "sha256": sha(path) if path.exists() else None}
        if not path.exists(): report["passed"] = False
    source_header, source_rows = read(SOURCE)
    source_ids = [r["record_id"] for r in source_rows]
    tables = {}
    for name, expected in EXPECTED.items():
        path = OUT / name
        if not path.exists():
            report["checks"].append({"check": name, "passed": False, "error": "missing"}); report["passed"] = False; continue
        header, rows = read(path); tables[name] = rows
        ok = header == expected
        report["checks"].append({"check": f"{name}:schema", "passed": ok, "rows": len(rows), "actual": header})
        report["passed"] &= ok
    t2 = tables.get("audit_table2_corrected.csv", [])
    allowed_categories = {"两厢车", "跑车", "三厢车", "越野车", "皮卡"}
    illegal_categories = sorted({r.get("分类", "") for r in t2 if r.get("分类", "") not in allowed_categories})
    category_ok = not illegal_categories
    report["checks"].append({"check": "table2_uses_only_five_cover_categories", "passed": category_ok, "illegal_values": illegal_categories})
    report["passed"] &= category_ok
    same_ids = Counter(source_ids) == Counter(r.get("record_id", "") for r in t2)
    report["checks"].append({"check": "table2_preserves_all_record_ids", "passed": same_ids, "source_rows": len(source_rows), "table2_rows": len(t2)})
    report["passed"] &= same_ids
    source_by_id = {r["record_id"]: r for r in source_rows}
    t2_by_id = {r["record_id"]: r for r in t2}
    mismatches = []
    for correction in tables.get("audit_table1_corrections.csv", []):
        rid = correction["record_id"]
        if rid not in t2_by_id or t2_by_id[rid].get("结构") != correction.get("建议结构"):
            mismatches.append(rid)
        original = source_by_id.get(rid)
        if original and original.get("结构") != correction.get("原结构"):
            mismatches.append(rid)
    ok = not mismatches
    report["checks"].append({"check": "table1_applied_to_table2", "passed": ok, "mismatch_count": len(set(mismatches)), "examples": sorted(set(mismatches))[:10]})
    report["passed"] &= ok
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "validation_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
