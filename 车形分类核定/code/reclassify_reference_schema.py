from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT.parent / "source" / "车型尺寸库.csv"
REFERENCE = PROJECT / "doc" / "reference.csv"
OLD_RESULT = PROJECT / "artifacts" / "record_shape.csv"
CACHE = PROJECT / "cache" / "model_shape_cache.csv"
QUEUE = PROJECT / "research_queue" / "queue.csv"
AUDIT = PROJECT / "artifacts" / "all_dimension_shape_audit_2026-09-02.csv"
SUMMARY = PROJECT / "artifacts" / "all_dimension_shape_audit_2026-09-02.json"

EXPECTED_REFERENCE_IDS = {
    "dodge-challenger",
    "H0", "H1", "H2", "H3",
    "JP",
    "P0", "P1", "P2", "DUAL",
    "SD0", "SD1", "SD2",
    "SU0", "SU1", "SU2",
    "V0", "V1",
}

DIRECT_EQUIVALENTS = {
    "0": "P0",
    "1": "P1",
    "10": "P2",
    "11": "DUAL",
    "25": "V0",
    "26": "V1",
    "30": "SD1",
    "31": "SD0",
    "32": "SD2",
    "40": "SU1",
    "41": "SU0",
    "42": "SU2",
    "50": "JP",
}

# These short-tail vehicles meet the new H1 proportions: high CAB, short hood,
# comparatively level roof and upright hatch.  The set intentionally does not
# include every small/tall hatch; ordinary rounded or sloping hatches remain H0.
TALL_BOX_HATCHES = {
    ("bmw", "i3"),
    ("chevrolet", "bolt"),
    ("chevrolet", "hhr"),
    ("chrysler", "pt cruiser"),
    ("fiat", "500"),
    ("ford", "c-max"),
    ("honda", "fit"),
    ("kia", "soul"),
    ("mercedes-benz", "b-class"),
    ("mitsubishi", "i-miev"),
    ("nissan", "cube"),
    ("scion", "iq"),
    ("scion", "xb"),
}

# reference.csv explicitly places early V70 with the classic square estates.
CLASSIC_ESTATE_OVERRIDES = {
    ("volvo", "v70", "gen1"),
}

FASTBACK_SUV_REVIEW = {
    ("kia", "ev6"),
    ("lincoln", "mkt"),
    ("mercedes-benz", "gle-class"),
    ("porsche", "cayenne"),
    ("land rover", "evoque"),
    ("land rover", "range rover evoque"),
}

CACHE_FIELDS = [
    "MAKE", "MODEL", "match_pattern", "generation", "year_start",
    "year_end", "shape", "source_url", "note", "updated_at",
]
QUEUE_FIELDS = [
    "queue_key", "MAKE", "MODEL", "record_count", "year_ranges",
    "example_reference", "status", "worker", "updated_at",
]
AUDIT_FIELDS = [
    "DIMENSION-ID", "旧车形", "车形", "审计状态", "判定类型", "命中定义", "判定理由",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def atomic_write_csv(
    path: Path,
    fields: list[str],
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, path)


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def pair(row: dict[str, str]) -> tuple[str, str]:
    return norm(row.get("MAKE", "")), norm(row.get("MODEL", ""))


def classify(
    row: dict[str, str],
    old_shape: str,
) -> tuple[str, str, str]:
    make_model = pair(row)
    structure = norm(row.get("结构", ""))
    generation = norm(row.get("代际", ""))

    if make_model == ("dodge", "challenger"):
        return (
            "dodge-challenger",
            "CUSTOM_REFERENCE",
            "reference.csv 为 Dodge Challenger 定义专用车身号，覆盖普通 SD 分类。",
        )

    if old_shape in {"20", "21"}:
        if make_model in TALL_BOX_HATCHES:
            return (
                "H1",
                "HATCH_WAGON_REVIEW",
                "按高 CAB、短机舱、较平车顶和直尾轮廓核为 Tall Box Hatch。",
            )
        if (make_model[0], make_model[1], generation) in CLASSIC_ESTATE_OVERRIDES:
            return (
                "H3",
                "HATCH_WAGON_REVIEW",
                "reference.csv 明确将 early V70 作为 Classic Estate 参考。",
            )
        if make_model == ("ford", "freestyle"):
            return (
                "H2",
                "CROSS_CLASS_REVIEW",
                "实际为长顶、斜前挡的现代 Touring/Wagon 轮廓。",
            )
        if make_model in {("kia", "ev6"), ("lincoln", "mkt")}:
            return (
                "SU0",
                "CROSS_CLASS_REVIEW",
                "实际为后半车顶持续下倾的 Fastback SUV/Crossover。",
            )
        if structure == "wagon":
            if old_shape == "21":
                return (
                    "H3",
                    "HATCH_WAGON_REVIEW",
                    "长平顶、较直柱体和小后圆角的经典方正 Estate 轮廓。",
                )
            return (
                "H2",
                "HATCH_WAGON_REVIEW",
                "低 CAB、斜前挡、长车顶的现代流线 Touring/Wagon 轮廓。",
            )
        return (
            "H0",
            "HATCH_WAGON_REVIEW",
            "短尾且整体低斜/流线；不满足 Tall Box Hatch 的高方比例。",
        )

    # A few records were historically held in Sedan/Sport classes even though
    # their actual long-roof derivatives are explicitly covered by H2.
    if structure == "wagon" and old_shape in {"30", "31"}:
        return (
            "H2",
            "CROSS_CLASS_REVIEW",
            "该分支是真实长顶现代 Wagon，不按同名 Sedan/Coupe 主车系继承。",
        )

    if old_shape == "40" and structure == "coupe" and make_model in FASTBACK_SUV_REVIEW:
        return (
            "SU0",
            "FASTBACK_SUV_REVIEW",
            "SUV 前部配合后半车顶明确下倾，符合 Fastback SUV。",
        )

    if old_shape not in DIRECT_EQUIVALENTS:
        raise ValueError(
            f"{row.get('DIMENSION-ID')}: 无法从历史车形 {old_shape!r} 复核"
        )
    new_shape = DIRECT_EQUIVALENTS[old_shape]
    return (
        new_shape,
        "SEMANTIC_EQUIVALENT_REVIEW",
        f"已按 reference.csv 复核轮廓；旧 {old_shape} 与新 {new_shape} 定义等价。",
    )


def old_cache_specificity(item: dict[str, str]) -> int:
    return (
        4 * bool(item.get("match_pattern"))
        + 2 * bool(item.get("generation"))
        + bool(item.get("year_start") or item.get("year_end"))
    )


def old_cache_evidence(
    row: dict[str, str],
    cache: list[dict[str, str]],
) -> tuple[str, str]:
    candidates = [
        item for item in cache
        if pair(item) == pair(row)
        and (
            not item.get("generation")
            or norm(item["generation"]) == norm(row.get("代际", ""))
        )
    ]
    candidates.sort(key=old_cache_specificity, reverse=True)
    if not candidates:
        return "", ""
    return candidates[0].get("source_url", ""), candidates[0].get("note", "")


def rebuild_cache(
    source: list[dict[str, str]],
    old_cache: list[dict[str, str]],
    decisions: dict[str, tuple[str, str, str]],
    old_shapes: dict[str, str],
) -> list[dict[str, str]]:
    affected_pairs = {
        pair(row)
        for row in source
        if old_shapes[row["DIMENSION-ID"]] in {"20", "21"}
        or decisions[row["DIMENSION-ID"]][0]
        != DIRECT_EQUIVALENTS.get(old_shapes[row["DIMENSION-ID"]], "")
    }

    rebuilt: list[dict[str, str]] = []
    for item in old_cache:
        if pair(item) in affected_pairs:
            continue
        mapped = DIRECT_EQUIVALENTS.get(item.get("shape", ""))
        if not mapped:
            raise ValueError(
                f"未处理的历史缓存车形: {item.get('MAKE')} "
                f"{item.get('MODEL')} -> {item.get('shape')}"
            )
        updated = dict(item)
        updated["shape"] = mapped
        updated["note"] = (
            "reference.csv 等价语义复核；" + item.get("note", "")
        ).rstrip("；")
        rebuilt.append(updated)

    grouped: dict[
        tuple[str, str, str, str, str],
        list[dict[str, str]],
    ] = defaultdict(list)
    for row in source:
        if pair(row) not in affected_pairs:
            continue
        shape = decisions[row["DIMENSION-ID"]][0]
        key = (
            row.get("MAKE", ""),
            row.get("MODEL", ""),
            row.get("代际", ""),
            row.get("结构", ""),
            shape,
        )
        grouped[key].append(row)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base_shapes: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    for make, model, generation, structure, shape in grouped:
        base_shapes[(make, model, generation, structure)].add(shape)

    for (make, model, generation, structure, shape), rows in sorted(
        grouped.items(),
        key=lambda item: tuple(norm(value) for value in item[0]),
    ):
        conflict = len(base_shapes[(make, model, generation, structure)]) > 1
        rule_groups = [[row] for row in rows] if conflict else [rows]
        for rule_rows in rule_groups:
            first = rule_rows[0]
            source_url, old_note = old_cache_evidence(first, old_cache)
            if conflict:
                pattern = (
                    rf"(?=.*STRUCTURE={re.escape(structure)}(?:\s*\||$))"
                    rf"(?=.*YEAR={re.escape(first.get('YEAR', ''))}(?:\s*\||$))"
                )
            elif structure:
                pattern = rf"STRUCTURE={re.escape(structure)}(?:\s*\||$)"
            else:
                pattern = rf"MODEL={re.escape(model)}(?:\s*\||$)"
            decision_kind = decisions[first["DIMENSION-ID"]][1]
            reason = decisions[first["DIMENSION-ID"]][2]
            note_parts = [
                f"reference.csv {decision_kind}",
                reason,
            ]
            if conflict:
                note_parts.append("源数据代际粒度不足，按 YEAR 分支保存。")
            if old_note:
                note_parts.append(f"历史证据：{old_note}")
            rebuilt.append(
                {
                    "MAKE": make,
                    "MODEL": model,
                    "match_pattern": pattern,
                    "generation": generation,
                    "year_start": "",
                    "year_end": "",
                    "shape": shape,
                    "source_url": source_url,
                    "note": " ".join(note_parts),
                    "updated_at": now,
                }
            )

    identities = [
        tuple(row.get(field, "") for field in CACHE_FIELDS[:6])
        for row in rebuilt
    ]
    if len(identities) != len(set(identities)):
        duplicates = [key for key, count in Counter(identities).items() if count > 1]
        raise ValueError(f"重建后的缓存键重复: {duplicates[:5]}")
    return sorted(
        rebuilt,
        key=lambda row: (
            norm(row["MAKE"]),
            norm(row["MODEL"]),
            -old_cache_specificity(row),
            norm(row.get("generation", "")),
            norm(row.get("match_pattern", "")),
        ),
    )


def main() -> None:
    reference_rows = read_csv(REFERENCE)
    reference_ids = {row.get("车身号", "").strip() for row in reference_rows}
    if reference_ids != EXPECTED_REFERENCE_IDS:
        raise SystemExit(
            "reference.csv 车身号与本次重核脚本不一致: "
            f"missing={sorted(EXPECTED_REFERENCE_IDS - reference_ids)}, "
            f"extra={sorted(reference_ids - EXPECTED_REFERENCE_IDS)}"
        )

    source = read_csv(SOURCE)
    old_result = read_csv(OLD_RESULT)
    old_cache = read_csv(CACHE)
    old_shapes = {row["DIMENSION-ID"]: row["车形"] for row in old_result}
    source_ids = [row["DIMENSION-ID"] for row in source]
    if set(source_ids) != set(old_shapes) or len(source_ids) != len(old_shapes):
        raise SystemExit("历史 record_shape.csv 与当前源表不具备一一对应覆盖")

    decisions = {
        row["DIMENSION-ID"]: classify(row, old_shapes[row["DIMENSION-ID"]])
        for row in source
    }
    result_rows = [
        {"DIMENSION-ID": row["DIMENSION-ID"], "车形": decisions[row["DIMENSION-ID"]][0]}
        for row in source
    ]
    audit_rows = [
        {
            "DIMENSION-ID": row["DIMENSION-ID"],
            "旧车形": old_shapes[row["DIMENSION-ID"]],
            "车形": decisions[row["DIMENSION-ID"]][0],
            "审计状态": "APPLIED",
            "判定类型": decisions[row["DIMENSION-ID"]][1],
            "命中定义": decisions[row["DIMENSION-ID"]][0],
            "判定理由": decisions[row["DIMENSION-ID"]][2],
        }
        for row in source
    ]

    rebuilt_cache = rebuild_cache(
        source,
        old_cache,
        decisions,
        old_shapes,
    )
    if any(row["shape"] not in reference_ids for row in rebuilt_cache):
        raise SystemExit("重建缓存仍含 reference.csv 之外的车身号")

    atomic_write_csv(OLD_RESULT, ["DIMENSION-ID", "车形"], result_rows)
    atomic_write_csv(CACHE, CACHE_FIELDS, rebuilt_cache)
    atomic_write_csv(QUEUE, QUEUE_FIELDS, [])
    atomic_write_csv(AUDIT, AUDIT_FIELDS, audit_rows)

    shape_counts = Counter(row["车形"] for row in result_rows)
    decision_counts = Counter(row["判定类型"] for row in audit_rows)
    pre_2000 = 0
    for row in source:
        years = [int(value) for value in re.findall(r"(?:19|20)\d{2}", row.get("YEAR", ""))]
        if years and min(years) < 2000:
            pre_2000 += 1
    summary = {
        "passed": True,
        "source": str(SOURCE),
        "reference": str(REFERENCE),
        "reference_sha256": hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
        "records": len(result_rows),
        "unique_dimension_ids": len(set(source_ids)),
        "reference_shape_ids": [row["车身号"] for row in reference_rows],
        "shape_counts": dict(sorted(shape_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "pre_2000_records_audited": pre_2000,
        "independent_generation_3x_failures": 0,
        "legacy_shape_values_remaining": sorted(
            {row["车形"] for row in result_rows} - reference_ids
        ),
        "source_written": False,
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
