"""按 02.分类结构审核/output/车型结构.csv 刷新三国车形接口 output/车形分类.csv。

- US：沿用既有 US核定 车形（按基础 ID）。
- EU/RU：同基础 ID 有 US 车形时参考 US；否则继承上一版研究/缓存车形（上游 ID 改名时按
  区域+MAKE+MODEL+结构族+代际+YEAR+长宽高 迁移），但必须与该行分类兼容；其余用
  data/区域车形代理规则.json 的代理车形，并进入质量复核队列。
- data/参考尺寸计算.csv（车身号→系数）校验后原样发布为 output/参考尺寸计算.csv，供下游计算。
- 全部校验通过后才原子写入 output/ 与 research_queue/。
"""

from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "02.分类结构审核" / "output" / "车型结构.csv"
OUTPUT = PROJECT / "output" / "车形分类.csv"
MANIFEST = PROJECT / "output" / "manifest.json"
QUEUE = PROJECT / "research_queue" / "regional_queue.csv"
RULES = PROJECT / "data" / "区域车形代理规则.json"
US_ID_MIGRATION = PROJECT / "data" / "US车形ID迁移.csv"
GENERIC_SHAPE_OVERRIDES = PROJECT / "data" / "通用车身号覆盖.csv"
REFERENCE = PROJECT / "data" / "参考尺寸计算.csv"
REFERENCE_OUTPUT = PROJECT / "output" / "参考尺寸计算.csv"
REFERENCE_COEFFICIENTS = ("前宽系数", "后宽系数", "弧长系数", "周长系数")
COUNTRIES = {"US", "EU", "RU"}
PROXY_STATUS = "参考US-结构分类代理"
ALLOWED = {"DUAL", "H0", "H1", "H2", "H3", "JP", "P0", "P1", "P2", "SD0", "SD1", "SD2", "SU0", "SU1", "SU2", "V0", "V1"}
OUTPUT_FIELDS = ["DIMENSION-ID", "COUNTRY", "车形", "处理状态"]
QUEUE_FIELDS = ["DIMENSION-ID", "COUNTRY", "MAKE", "MODEL", "版本", "结构", "代际", "YEAR", "状态", "研究问题"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def read_generic_shape_overrides(path: Path, rules: dict) -> dict[tuple[str, str, str, str], str]:
    required = {"MAKE", "MODEL", "代际", "结构", "通用车身号", "判定优先级", "判定理由"}
    rows = read_rows(path)
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"通用车身号覆盖缺少字段: {path}")
    overrides: dict[tuple[str, str, str, str], str] = {}
    for row in rows:
        shape = row["通用车身号"]
        key = (row["MAKE"].casefold(), row["MODEL"].casefold(), row["代际"].casefold(), family(row["结构"], rules).casefold())
        if not all(key) or shape not in ALLOWED:
            raise ValueError(f"通用车身号覆盖无效: {row}")
        if key in overrides:
            raise ValueError(f"通用车身号覆盖重复: {key}")
        overrides[key] = shape
    return overrides


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def split_region(record_id: str) -> tuple[str, str]:
    head, separator, tail = record_id.rpartition(" ")
    if separator and tail.upper() in COUNTRIES:
        return head, tail.upper()
    return record_id, "US"


def family(structure: str, rules: dict) -> str:
    return re.sub(rules["door_suffix_pattern"], "", structure or "").strip()


def physical_key(row: dict[str, str], rules: dict) -> tuple:
    _, country = split_region(row["DIMENSION-ID"])
    return (country, row["MAKE"], row["MODEL"], family(row["结构"], rules), row["代际"], row["YEAR"],
            row["L-IN"], row["W-IN"], row["H-IN"])


def generic_override(row: dict[str, str], rules: dict, overrides: dict[tuple[str, str, str, str], str]) -> str:
    key = (row["MAKE"].casefold(), row["MODEL"].casefold(), row["代际"].casefold(), family(row["结构"], rules).casefold())
    return overrides.get(key, "")


def compatible(shape: str, row: dict[str, str], rules: dict) -> bool:
    fam = family(row["结构"], rules)
    if fam in rules["compatible_by_structure"]:
        return shape in rules["compatible_by_structure"][fam]
    allowed = rules["compatible_by_category"].get(row["分类"])
    return allowed is None or shape in allowed


def proxy_shape(row: dict[str, str], rules: dict) -> str:
    fam = family(row["结构"], rules)
    if fam in rules["proxy_by_structure"]:
        return rules["proxy_by_structure"][fam]
    return rules["proxy_by_category"].get(row["分类"], rules["proxy_by_category"][""])


def previous_library() -> list[dict[str, str]]:
    """上一版车形所依据的尺寸库（取自本节点 manifest 记录的上游 artifact），用于 ID 迁移。"""
    if not MANIFEST.is_file():
        return []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for upstream in manifest.get("upstream", []):
        for item in upstream.get("files", []):
            if item.get("file") in ("尺寸库.csv", "车型结构.csv"):
                path = ROOT / item["artifact_file"]
                if path.is_file():
                    return read_rows(path)
    return []


def build(
    source: list[dict[str, str]], prior: list[dict[str, str]], prior_library: list[dict[str, str]], rules: dict,
    us_id_migration: dict[str, str] | None = None, generic_overrides: dict[tuple[str, str, str, str], str] | None = None,
) -> dict:
    us_shapes: dict[str, str] = {}
    prior_by_id = {row["DIMENSION-ID"]: row for row in prior}
    for row in prior:
        record_id = (us_id_migration or {}).get(row["DIMENSION-ID"], row["DIMENSION-ID"])
        base_id, country = split_region(record_id)
        if country == "US" and row["车形"]:
            if us_shapes.get(base_id, row["车形"]) != row["车形"]:
                raise ValueError(f"US 基础 ID 存在多个车形：{base_id}")
            us_shapes[base_id] = row["车形"]

    migrated: dict[tuple, set[tuple[str, str]]] = defaultdict(set)
    for row in prior_library:
        shape_row = prior_by_id.get(row["DIMENSION-ID"])
        if shape_row and shape_row["处理状态"] != PROXY_STATUS:
            migrated[physical_key(row, rules)].add((shape_row["车形"], shape_row["处理状态"]))

    output, queue, counters = [], [], Counter()
    for row in source:
        record_id = row["DIMENSION-ID"]
        base_id, country = split_region(record_id)
        shape = status = ""
        override = generic_override(row, rules, generic_overrides or {})
        if override:
            shape, status = override, "US核定" if country == "US" else "通用规则核定"
        elif country == "US":
            shape, status = us_shapes.get(base_id, ""), "US核定"
            if not shape:
                raise ValueError(f"US 记录缺少已核定车形：{record_id}")
        elif base_id in us_shapes:
            shape, status = us_shapes[base_id], "参考US-同基础ID"
        else:
            candidates = set()
            previous = prior_by_id.get(record_id)
            if previous and previous["处理状态"] != PROXY_STATUS:
                candidates = {(previous["车形"], previous["处理状态"])}
                counters["继承-同ID"] += 1
            elif physical_key(row, rules) in migrated:
                candidates = migrated[physical_key(row, rules)]
                counters["继承-ID迁移"] += 1
            if len({shape for shape, _ in candidates}) == 1:
                inherited, inherited_status = next(iter(candidates))
                if compatible(inherited, row, rules):
                    shape, status = inherited, inherited_status
                else:
                    counters["继承车形与分类不兼容-改代理"] += 1
            if not shape:
                shape, status = proxy_shape(row, rules), PROXY_STATUS
        output.append({"DIMENSION-ID": record_id, "COUNTRY": country, "车形": shape, "处理状态": status})
        if status == PROXY_STATUS:
            queue.append({
                "DIMENSION-ID": record_id, "COUNTRY": country, "MAKE": row["MAKE"], "MODEL": row["MODEL"],
                "版本": row["版本"], "结构": row["结构"], "代际": row["代际"], "YEAR": row["YEAR"],
                "状态": "待质量复核",
                "研究问题": f"按 结构={family(row['结构'], rules)} / 分类={row['分类'] or '空'} 代理为 {shape}；需核对轮廓细分类",
            })
    return {"output": output, "queue": queue, "counters": dict(counters)}


def validate_reference(rows: list[dict[str, str]]) -> dict[str, bool]:
    """下游按车身号取系数：车身号唯一、覆盖全部合法车形、所需系数为正数。"""
    shapes = [row.get("车身号", "") for row in rows]

    def positive(value: str) -> bool:
        try:
            return float(value) > 0
        except ValueError:
            return False

    return {
        "reference_shapes_unique": len(shapes) == len(set(shapes)) and "" not in shapes,
        "reference_covers_allowed_shapes": ALLOWED <= set(shapes),
        "reference_coefficients_numeric": all(
            positive(row.get(column, "")) for row in rows if row["车身号"] in ALLOWED
            for column in REFERENCE_COEFFICIENTS
        ),
    }


def publish_reference() -> None:
    temporary = REFERENCE_OUTPUT.with_suffix(REFERENCE_OUTPUT.suffix + ".tmp")
    temporary.write_bytes(REFERENCE.read_bytes())
    os.replace(temporary, REFERENCE_OUTPUT)


def validate(source: list[dict[str, str]], result: dict, rules: dict) -> dict:
    output = result["output"]
    by_id = {row["DIMENSION-ID"]: row for row in source}
    ids = [row["DIMENSION-ID"] for row in output]
    checks = {
        "complete_source_coverage": ids == [row["DIMENSION-ID"] for row in source],
        "output_ids_unique": len(ids) == len(set(ids)),
        "allowed_shapes_only": all(row["车形"] in ALLOWED for row in output),
        "no_blank_shape_or_status": all(row["车形"] and row["处理状态"] for row in output),
        "all_us_rows_nuclear": all(row["处理状态"] == "US核定" for row in output if row["COUNTRY"] == "US"),
        "regional_shapes_match_category": all(
            compatible(row["车形"], by_id[row["DIMENSION-ID"]], rules)
            for row in output if row["COUNTRY"] != "US" and row["处理状态"] != "参考US-同基础ID"
        ),
    }
    return {"status": "passed" if all(checks.values()) else "failed", "checks": checks}


def run() -> dict:
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    source = read_rows(SOURCE)
    migration = {row["旧DIMENSION-ID"]: row["新DIMENSION-ID"] for row in read_rows(US_ID_MIGRATION)} if US_ID_MIGRATION.is_file() else {}
    overrides = read_generic_shape_overrides(GENERIC_SHAPE_OVERRIDES, rules)
    result = build(source, read_rows(OUTPUT), previous_library(), rules, migration, overrides)
    validation = validate(source, result, rules)
    reference_checks = validate_reference(read_rows(REFERENCE))
    validation["checks"].update(reference_checks)
    if not all(reference_checks.values()):
        validation["status"] = "failed"
    if validation["status"] != "passed":
        raise SystemExit(f"车形接口校验失败：{validation['checks']}")
    write_rows(OUTPUT, OUTPUT_FIELDS, result["output"])
    write_rows(QUEUE, QUEUE_FIELDS, result["queue"])
    publish_reference()
    summary = {
        "source": len(source),
        "by_country": dict(Counter(row["COUNTRY"] for row in result["output"])),
        "status_counts": dict(Counter(row["处理状态"] for row in result["output"])),
        "inheritance": result["counters"],
        "quality_review": len(result["queue"]),
        "validation": validation,
    }
    (PROJECT / "output" / "regional_shape_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
