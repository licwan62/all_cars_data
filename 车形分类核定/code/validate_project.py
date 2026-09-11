from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from id_scheme import dimension_id

DEFAULT_SOURCE = ROOT / "public" / "尺寸库.csv"
SOURCE = Path(os.environ.get("SHAPE_SOURCE", DEFAULT_SOURCE)).resolve()
REFERENCE = ROOT / "public" / "参考尺寸计算.csv"
CACHE = PROJECT / "cache" / "model_shape_cache.csv"
QUEUE = PROJECT / "research_queue" / "queue.csv"
RESULT = PROJECT / "artifacts" / "record_shape.csv"
AUDIT_CANDIDATES = sorted((PROJECT / "changes").glob("*/all_dimension_audit.csv"))
ALL_ID_AUDIT = (
    Path(os.environ["SHAPE_AUDIT"]).resolve()
    if os.environ.get("SHAPE_AUDIT")
    else AUDIT_CANDIDATES[-1]
    if AUDIT_CANDIDATES
    else PROJECT / "artifacts" / "all_dimension_shape_audit_2026-09-06.csv"
)
# Historical summary files are optional.  A current immutable batch audit is
# authoritative when selected above, so do not pair it with an older summary.
AUDIT_SUMMARY = (
    PROJECT / "artifacts" / "all_dimension_shape_audit_2026-09-06.json"
    if ALL_ID_AUDIT.parent == PROJECT / "artifacts"
    else ALL_ID_AUDIT.parent / "validation.json"
)
LEGACY_SHAPES = {
    "0", "1", "10", "11", "20", "21", "25", "26",
    "30", "31", "32", "40", "41", "42", "50",
}


def read(path: Path):
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, **detail: object) -> None:
        checks.append({"check": name, "passed": passed, **detail})

    reference_header, reference = read(REFERENCE)
    reference_ids = [row.get("车身号", "") for row in reference]
    allowed = set(reference_ids)
    check(
        "reference_schema",
        reference_header == [
            "车身号", "分类", "结构细分", "描述", "参考车型", "下摆上限",
            "后宽系数", "前宽系数", "颈宽系数", "弧长系数", "周长系数",
        ],
        actual=reference_header,
    )
    check(
        "reference_shape_ids_nonempty_unique",
        bool(reference_ids)
        and all(reference_ids)
        and len(reference_ids) == len(allowed),
        ids=reference_ids,
    )
    check(
        "reference_has_no_legacy_ids",
        not (allowed & LEGACY_SHAPES),
        failures=sorted(allowed & LEGACY_SHAPES),
    )

    source_header, source = read(SOURCE)
    _, cache = read(CACHE)
    _, queue = read(QUEUE)
    expected_source = [
        "DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构",
        "代际", "YEAR", "分类", "L-IN", "W-IN", "H-IN", "参考车型",
        "备注", "迭代状态",
    ]
    check("source_schema", source_header == expected_source, rows=len(source), actual=source_header)
    check("source_dimension_ids", all(row.get("DIMENSION-ID") == dimension_id(row) for row in source))
    source_ids = [row.get("DIMENSION-ID", "") for row in source]
    check(
        "source_dimension_ids_unique",
        len(source_ids) == len(set(source_ids)),
        unique_ids=len(set(source_ids)),
    )

    check(
        "cache_shapes_from_reference",
        bool(cache) and all(row.get("shape") in allowed for row in cache),
        rows=len(cache),
    )
    cache_legacy = sorted({row.get("shape", "") for row in cache} & LEGACY_SHAPES)
    check("cache_has_no_legacy_shapes", not cache_legacy, failures=cache_legacy)
    structural_sd = [
        row
        for row in cache
        if row.get("shape") in {"SD0", "SD1", "SD2"}
        and re.search(
            r"STRUCTURE\s*=\s*(?:Sedan|Coupe|Convertible|Hardtop|Roadster|Targa)",
            row.get("match_pattern", ""),
            re.IGNORECASE,
        )
    ]
    unsupported_structural_sd = [
        row for row in structural_sd
        if "reference.csv" not in row.get("note", "")
    ]
    check(
        "cache_sd_structure_selectors_are_reviewed",
        not unsupported_structural_sd,
        selectors=len(structural_sd),
        unsupported=len(unsupported_structural_sd),
    )
    identities = [
        tuple(
            row.get(field, "")
            for field in (
                "MAKE", "MODEL", "match_pattern", "generation",
                "year_start", "year_end",
            )
        )
        for row in cache
    ]
    check("cache_keys_unique", len(identities) == len(set(identities)))
    check(
        "queue_status_valid",
        all(row.get("status") in {"pending", "in_progress", "blocked"} for row in queue),
        rows=len(queue),
    )

    if RESULT.exists():
        result_header, result = read(RESULT)
        result_ids = [row.get("DIMENSION-ID", "") for row in result]
        result_map = {row["DIMENSION-ID"]: row["车形"] for row in result}
        check("result_schema", result_header == ["DIMENSION-ID", "车形"], actual=result_header)
        check(
            "result_exact_coverage",
            result_ids == source_ids,
            source_rows=len(source),
            result_rows=len(result),
        )
        check(
            "result_dimension_ids_unique",
            len(result_ids) == len(set(result_ids)),
            unique_ids=len(set(result_ids)),
        )
        check("result_shapes_from_reference", all(row.get("车形") in allowed for row in result))
        result_legacy = sorted({row.get("车形", "") for row in result} & LEGACY_SHAPES)
        check("result_has_no_legacy_shapes", not result_legacy, failures=result_legacy)

        challenger = [
            row for row in source
            if row.get("MAKE") == "Dodge" and row.get("MODEL") == "Challenger"
        ]
        check(
            "dodge_challenger_custom_shape",
            bool(challenger)
            and all(result_map.get(row["DIMENSION-ID"]) == "dodge-challenger" for row in challenger),
            rows=len(challenger),
        )

        expectations = [
            ("Honda", "Civic", "Hatchback", "", "H0"),
            ("Kia", "Soul", "", "", "H1"),
            ("Nissan", "Cube", "", "", "H1"),
            ("Audi", "RS6", "Wagon", "", "H2"),
            ("Volvo", "V60", "Wagon", "", "H2"),
            ("Buick", "Roadmaster", "Wagon", "gen7", "H3"),
            ("Oldsmobile", "Custom Cruiser", "Wagon", "", "H3"),
            ("Ford", "F-150", "Pickup", "gen9", "P0"),
            ("Toyota", "Tacoma", "", "", "P1"),
            ("Ford", "Mustang", "Coupe", "", "SD0"),
            ("Toyota", "Camry", "Sedan", "gen9", "SD1"),
            ("Chevrolet", "Bel Air", "Sedan", "", "SD2"),
            ("Tesla", "Model Y", "", "", "SU0"),
            ("Tesla", "Model Y L", "", "", "SU0"),
            ("Porsche", "Macan", "", "", "SU0"),
            ("Genesis", "GV60", "", "", "SU0"),
            ("Volkswagen", "ID.4", "", "", "SU0"),
            ("BMW", "X6", "", "", "SU1"),
            ("Audi", "Q8", "", "", "SU1"),
            ("Land Rover", "Range Rover Velar", "", "", "SU1"),
            ("Volvo", "C40", "", "", "SU1"),
            ("Volvo", "EX40", "", "", "SU1"),
            ("Honda", "CR-V", "", "", "SU1"),
            ("Toyota", "4Runner", "", "", "SU2"),
            ("Jeep", "Wrangler", "", "", "JP"),
            ("Toyota", "Sienna", "", "", "V0"),
            ("Chevrolet", "Express", "", "", "V1"),
        ]
        reference_failures = []
        for make, model, structure, generation, expected in expectations:
            matched = [
                row for row in source
                if row.get("MAKE") == make
                and row.get("MODEL") == model
                and (not structure or row.get("结构") == structure)
                and (not generation or row.get("代际") == generation)
            ]
            if not matched or any(
                result_map.get(row["DIMENSION-ID"]) != expected for row in matched
            ):
                reference_failures.append(
                    f"{make} {model} {structure or '*'} {generation or '*'} -> {expected}"
                )
        check("reference_examples", not reference_failures, failures=reference_failures)

        split_failures = []
        split_count = 0
        for row in source:
            pair = row['MAKE'], row['MODEL']
            if pair not in {('Acura', 'ZDX'), ('Land Rover', 'Range Rover Sport')}:
                continue
            last_year = max(int(x) for x in re.findall(r'(?:19|20)\d{2}', row['YEAR']))
            expected = ('SU0' if last_year <= 2013 else 'SU1') if pair[0] == 'Acura' else ('SU2' if last_year <= 2013 else 'SU1')
            split_count += 1
            if result_map.get(row['DIMENSION-ID']) != expected:
                split_failures.append(row['DIMENSION-ID'])
        check('suv_taper_generation_boundaries', split_count == 14 and not split_failures, rows=split_count, failures=split_failures)

        audit_header, audit = read(ALL_ID_AUDIT)
        audit_ids = [row.get("DIMENSION-ID", "") for row in audit]
        check(
            "all_dimension_audit_exact_coverage",
            bool(audit)
            and audit_ids == source_ids
            and all(row.get("审计状态") == "APPLIED" for row in audit),
            rows=len(audit),
            actual=audit_header,
        )
        check(
            "all_dimension_audit_matches_result",
            all(result_map.get(row.get("DIMENSION-ID", "")) == row.get("车形") for row in audit),
        )
        if AUDIT_SUMMARY.exists():
            summary = json.loads(AUDIT_SUMMARY.read_text(encoding="utf-8-sig"))
            summary_matches = (
                set(summary.get("reference_shape_ids", [])) == allowed
                and not summary.get("legacy_shape_values_remaining")
                and summary.get("records") == len(source)
                if "reference_shape_ids" in summary
                else summary.get("passed") is True
                and summary.get("records") == len(source)
                and summary.get("allowed_shapes_only") is True
            )
            check(
                "audit_summary_matches_reference",
                summary_matches,
            )
        else:
            check("audit_summary_exists", False)
    else:
        check("result_not_generated_until_complete", bool(queue), unresolved_models=len(queue))

    report = {
        "passed": all(item["passed"] for item in checks),
        "source": str(SOURCE),
        "reference": str(REFERENCE),
        "checks": checks,
    }
    output = PROJECT / "artifacts" / "validation_report.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
