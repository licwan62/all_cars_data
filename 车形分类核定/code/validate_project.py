from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from id_scheme import dimension_id
DEFAULT_SOURCE = ROOT / "分类结构审核" / "changes" / "2026-08-24_03_sedan-coupe" / "correct.csv"
SOURCE = Path(os.environ.get("SHAPE_SOURCE", DEFAULT_SOURCE)).resolve()
CACHE = PROJECT / "cache" / "model_shape_cache.csv"
QUEUE = PROJECT / "research_queue" / "queue.csv"
RESULT = PROJECT / "artifacts" / "record_shape.csv"
ALLOWED = {"0", "1", "10", "11", "20", "21", "22", "23", "30", "31", "32", "40", "41", "42", "50"}


def read(path: Path, delimiter: str = ","):
    if not path.exists(): return [], []
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f, delimiter=delimiter); return r.fieldnames or [], list(r)


def main() -> None:
    checks = []
    source_header, source = read(SOURCE); cache_header, cache = read(CACHE); queue_header, queue = read(QUEUE)
    def check(name: str, passed: bool, **detail): checks.append({"check": name, "passed": passed, **detail})
    expected_source = ["DIMENSION-ID","MAKE","MODEL","版本","CAB","BED","结构","代际","YEAR","分类","L-IN","W-IN","H-IN","参考车型","备注","迭代状态"]
    check("source_schema", source_header == expected_source, rows=len(source), actual=source_header)
    check("source_dimension_ids", all(row.get("DIMENSION-ID") == dimension_id(row) for row in source))
    source_ids = [row.get("DIMENSION-ID", "") for row in source]
    check("source_dimension_ids_unique", len(source_ids) == len(set(source_ids)), unique_ids=len(set(source_ids)))
    check("cache_shapes_valid", bool(cache) and all(x.get("shape") in ALLOWED for x in cache), rows=len(cache))
    identities = [(x.get("MAKE"), x.get("MODEL"), x.get("match_pattern"), x.get("generation"), x.get("year_start"), x.get("year_end")) for x in cache]
    check("cache_keys_unique", len(identities) == len(set(identities)))
    check("queue_status_valid", all(x.get("status") in {"pending", "in_progress", "blocked"} for x in queue), rows=len(queue))
    if RESULT.exists():
        header, result = read(RESULT); result_ids = [x.get("DIMENSION-ID", "") for x in result]
        check("result_schema", header == ["DIMENSION-ID", "车形"], actual=header)
        check("result_exact_coverage", result_ids == source_ids, source_rows=len(source), result_rows=len(result))
        check("result_dimension_ids_unique", len(result_ids) == len(set(result_ids)), unique_ids=len(set(result_ids)))
        check("result_shapes_valid", all(x.get("车形") in ALLOWED for x in result))
    else: check("result_not_generated_until_complete", bool(queue), unresolved_models=len(queue))
    report = {"passed": all(x["passed"] for x in checks), "source": str(SOURCE), "checks": checks}
    out = PROJECT / "artifacts" / "validation_report.json"; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2)); raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__": main()
