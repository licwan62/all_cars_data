from __future__ import annotations

import csv
import json
from collections import OrderedDict
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
ARTIFACTS = PROJECT / "artifacts"
QUEUE = PROJECT / "research_queue" / "queue.csv"
SOURCE = ROOT / "source" / "车型尺寸库.csv"
SPLITS = PROJECT / "research_queue" / "approved_splits.json"

SOURCE_FIELDS = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际", "YEAR", "分类", "L-IN", "W-IN", "H-IN", "参考车型", "备注", "迭代状态"]
T1_FIELDS = ["DIMENSION-ID", "修改类型", "原结构", "建议结构", "原分类", "建议分类", "置信度", "修改原因", "主要依据", "是否需要拆分记录"]
T2_FIELDS = ["DIMENSION-ID", "结构", "分类", "迭代状态"]
T3_FIELDS = ["DIMENSION-ID", "疑似结构", "问题", "需要补充的信息", "建议处理方式"]
T4_FIELDS = ["DIMENSION-ID", "建议YEAR", "建议结构", "拆分原因"]
T5_FIELDS = ["DIMENSION-ID", "字段", "当前值", "疑似问题", "建议检查"]
FULL_FIELDS = ["DIMENSION-ID", "输出结构", "输出分类", "审核结果", "修改类型", "审核依据"]
ALLOWED_CATEGORIES = {"两厢车", "跑车", "三厢车", "越野车", "皮卡"}
RENAME_PAIRS = {
    ("CUV", "Crossover"),
    ("Roadster", "Convertible"),
    ("Coupe SUV", "SUV"),
    ("Minivan", "MPV"),
}
CATEGORY_RULES = {
    "Sedan": {"三厢车"}, "Fastback Sedan": {"三厢车"},
    "Hatchback": {"两厢车"}, "Wagon": {"两厢车"}, "MPV": {"两厢车"}, "Van": {"两厢车"}, "Minivan": {"两厢车"},
    "SUV": {"越野车"}, "Crossover": {"越野车"}, "CUV": {"越野车"}, "Coupe SUV": {"越野车"},
    "Pickup": {"皮卡"},
    "Coupe": {"跑车"}, "Convertible": {"跑车"}, "Roadster": {"跑车"}, "Targa": {"跑车"}, "Hardtop": {"跑车"},
    "Coupe/Convertible": {"跑车"}, "Coupe/Convertible/Targa": {"跑车"}, "Convertible/Targa": {"跑车"},
    # Liftback/Fastback 需要车型级判断；这些是本项目研究后允许的五类结果。
    "Liftback": {"三厢车", "两厢车", "跑车"}, "Fastback": {"三厢车", "跑车"},
}


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def merge_done(rows: list[dict[str, str]]) -> OrderedDict[str, dict[str, str]]:
    """Deduplicate queue findings by DIMENSION-ID and retain the strongest evidence."""
    rank = {"高": 3, "中": 2, "低": 1, "": 0}
    result: OrderedDict[str, dict[str, str]] = OrderedDict()
    for row in rows:
        if row.get("status") != "done" or not row.get("suggested_structure"):
            continue
        rid = row.get("DIMENSION-ID", "")
        previous = result.get(rid)
        if previous is None or rank.get(row.get("confidence", ""), 0) > rank.get(previous.get("confidence", ""), 0):
            result[rid] = row
    return result


def modification_type(old_structure: str, new_structure: str, old_category: str, new_category: str, *, split: bool = False) -> str:
    structure_changed = old_structure != new_structure
    category_changed = old_category != new_category
    if split and category_changed:
        return "拆分并发生产品类型变化（重点）"
    if split:
        return "拆分记录"
    if structure_changed and category_changed:
        return "产品类型变化（重点）"
    if category_changed:
        return "类型修改（重点）"
    if structure_changed and (old_structure, new_structure) in RENAME_PAIRS:
        return "结构改名"
    if structure_changed:
        return "结构修改"
    return "无需修改"


def main() -> None:
    source_fields, source_rows = read(SOURCE)
    _, queue_rows = read(QUEUE)
    if source_fields != SOURCE_FIELDS:
        raise SystemExit(f"源表字段与表2规范不一致：{source_fields}")

    source_by_id = {row["DIMENSION-ID"]: row for row in source_rows}
    done = merge_done(queue_rows)
    blocked = {row["DIMENSION-ID"]: row for row in queue_rows if row.get("status") == "blocked"}
    approved_splits = json.loads(SPLITS.read_text(encoding="utf-8")) if SPLITS.exists() else []
    # A migrated source may already contain every approved split branch.  Only
    # materialize a manifest again when at least one of its records is absent.
    splits_by_id = {
        item["original_dimension_id"]: item
        for item in approved_splits
        if any(part["DIMENSION-ID"] not in source_by_id for part in item.get("records", []))
    }

    corrections: list[dict[str, str]] = []
    corrected_rows: list[dict[str, str]] = []
    split_rows: list[dict[str, str]] = []
    for source in source_rows:
        rid = source["DIMENSION-ID"]
        if rid in splits_by_id:
            split = splits_by_id[rid]
            for part in split["records"]:
                output = dict(source)
                output.update(part)
                if output["分类"] not in ALLOWED_CATEGORIES:
                    raise SystemExit(f"批准拆分含非法车衣分类：{output['DIMENSION-ID']} {output['分类']}")
                corrected_rows.append(output)
                split_rows.append({
                    "DIMENSION-ID": rid,
                    "MAKE": source["MAKE"],
                    "MODEL": source["MODEL"],
                    "当前YEAR": source["YEAR"],
                    "当前结构": source["结构"],
                    "建议YEAR": output["YEAR"],
                    "建议结构": output["结构"],
                    "拆分原因": split["reason"] + f" 输出 DIMENSION-ID={output['DIMENSION-ID']}",
                })
            primary = split["records"][0]
            corrections.append({
                "DIMENSION-ID": rid, "MAKE": source["MAKE"], "MODEL": source["MODEL"], "版本": source["版本"],
                "YEAR": source["YEAR"], "修改类型": modification_type(source["结构"], primary["结构"], source["分类"], primary["分类"], split=True),
                "原结构": source["结构"], "建议结构": primary["结构"],
                "原分类": source["分类"], "建议分类": primary["分类"], "置信度": "高",
                "修改原因": split["reason"], "主要依据": split["source_url"], "是否需要拆分记录": "是",
            })
            continue
        output = dict(source)
        finding = done.get(rid)
        if finding and "/" not in finding["suggested_structure"]:
            suggested_structure = finding["suggested_structure"]
            suggested_category = finding.get("suggested_category", "") or source["分类"]
            if suggested_category not in ALLOWED_CATEGORIES:
                raise SystemExit(f"研究队列含非法车衣分类：{rid} {suggested_category}")
            changed = source["结构"] != suggested_structure or source["分类"] != suggested_category
            if changed:
                output["结构"] = suggested_structure
                output["分类"] = suggested_category
                output["迭代状态"] = "可入库"
                corrections.append({
                    "DIMENSION-ID": rid,
                    "MAKE": source["MAKE"],
                    "MODEL": source["MODEL"],
                    "版本": source["版本"],
                    "YEAR": source["YEAR"],
                    "修改类型": modification_type(source["结构"], suggested_structure, source["分类"], suggested_category),
                    "原结构": source["结构"],
                    "建议结构": suggested_structure,
                    "原分类": source["分类"],
                    "建议分类": suggested_category,
                    "置信度": finding.get("confidence", ""),
                    "修改原因": finding.get("note", ""),
                    "主要依据": finding.get("source_url", ""),
                    "是否需要拆分记录": "否",
                })
        if rid in blocked:
            # Blocked findings must remain unchanged until the user manually reviews them.
            output["结构"] = source["结构"]
            output["分类"] = source["分类"]
            output["迭代状态"] = "待复核"
        corrected_rows.append(output)

    uncertain: list[dict[str, str]] = []
    for rid, finding in blocked.items():
        source = source_by_id.get(rid)
        if not source:
            raise SystemExit(f"研究队列 DIMENSION-ID 不在源表：{rid}")
        is_suburban = source["MAKE"] == "Chevrolet" and source["MODEL"] == "Suburban"
        uncertain.append({
            "DIMENSION-ID": rid,
            "MAKE": source["MAKE"],
            "MODEL": source["MODEL"],
            "版本": source["版本"],
            "YEAR": source["YEAR"],
            "当前结构": source["结构"],
            "疑似结构": finding.get("suggested_structure", "") or finding.get("suspected_structure", ""),
            "问题": finding.get("note", ""),
            "需要补充的信息": "用户核对对应 YEAR/版本后决定是否手工修改源文件" if is_suburban else "补充版本/车身形式，按 YEAR 与版本拆分核对",
            "建议处理方式": "建议人工确认后将 Pickup 改为 SUV；禁止脚本自动应用" if is_suburban else "保持源值，待用户人工拆分或确认",
        })

    priority = {"拆分并发生产品类型变化（重点）": 0, "产品类型变化（重点）": 1, "类型修改（重点）": 2, "结构修改": 3, "拆分记录": 4, "结构改名": 5}
    corrections.sort(key=lambda row: (priority.get(row["修改类型"], 9), row["MAKE"], row["MODEL"], row["YEAR"], row["DIMENSION-ID"]))
    uncertain.sort(key=lambda row: (row["MAKE"], row["MODEL"], row["YEAR"], row["DIMENSION-ID"]))
    write(ARTIFACTS / "audit_table1_corrections.csv", T1_FIELDS, corrections)
    process_rows_by_id: OrderedDict[str, dict[str, str]] = OrderedDict()
    for row in corrected_rows:
        projected = {field: row.get(field, "") for field in T2_FIELDS}
        previous = process_rows_by_id.get(row["DIMENSION-ID"])
        if previous:
            if any(previous[field] != projected[field] for field in ("结构", "分类")):
                raise SystemExit(f"同一 DIMENSION-ID 存在冲突的结构/分类：{row['DIMENSION-ID']}")
            statuses = list(dict.fromkeys(filter(None, previous["迭代状态"].split(" | ") + [projected["迭代状态"]])))
            previous["迭代状态"] = " | ".join(statuses)
        else:
            process_rows_by_id[row["DIMENSION-ID"]] = projected
    write(ARTIFACTS / "audit_table2_corrected.csv", T2_FIELDS, process_rows_by_id.values())
    write(ARTIFACTS / "corrected.csv", SOURCE_FIELDS, corrected_rows)
    write(ARTIFACTS / "audit_table3_uncertain.csv", T3_FIELDS, uncertain)
    write(ARTIFACTS / "audit_table4_split.csv", T4_FIELDS, split_rows)
    write(ARTIFACTS / "audit_table5_other.csv", T5_FIELDS, [])

    correction_by_id = {row["DIMENSION-ID"]: row for row in corrections}
    output_by_id = {row["DIMENSION-ID"]: row for row in corrected_rows}
    full_audit: list[dict[str, str]] = []
    rule_errors: list[str] = []
    for source in source_rows:
        rid = source["DIMENSION-ID"]
        correction = correction_by_id.get(rid)
        if rid in splits_by_id:
            outputs = [output_by_id[part["DIMENSION-ID"]] for part in splits_by_id[rid]["records"]]
            output_structures = " | ".join(dict.fromkeys(row["结构"] for row in outputs))
            output_categories = " | ".join(dict.fromkeys(row["分类"] for row in outputs))
            result = "已批准拆分"
            basis = splits_by_id[rid]["source_url"]
        else:
            output = output_by_id[rid]
            outputs = [output]
            output_structures = output["结构"]
            output_categories = output["分类"]
            result = "已修正" if correction else "复审一致"
            basis = correction["主要依据"] if correction else "doc/车衣分类业务规则.md；全库结构—分类规则扫描"
        for output in outputs:
            allowed = CATEGORY_RULES.get(output["结构"])
            if allowed is None or output["分类"] not in allowed:
                rule_errors.append(f"{output['DIMENSION-ID']}:{output['结构']}/{output['分类']}")
        full_audit.append({
            "DIMENSION-ID": rid, "MAKE": source["MAKE"], "MODEL": source["MODEL"], "版本": source["版本"], "YEAR": source["YEAR"],
            "原结构": source["结构"], "原分类": source["分类"], "输出结构": output_structures, "输出分类": output_categories,
            "审核结果": result, "修改类型": correction["修改类型"] if correction else "无需修改", "审核依据": basis,
        })
    if rule_errors:
        raise SystemExit(f"全库结构—分类规则扫描失败 {len(rule_errors)} 条：{rule_errors[:10]}")
    full_audit_by_id: OrderedDict[str, dict[str, str]] = OrderedDict()
    for row in full_audit:
        previous = full_audit_by_id.get(row["DIMENSION-ID"])
        if previous:
            for field in FULL_FIELDS[1:]:
                values = list(dict.fromkeys(filter(None, previous[field].split(" | ") + [row[field]])))
                previous[field] = " | ".join(values)
        else:
            full_audit_by_id[row["DIMENSION-ID"]] = row
    write(ARTIFACTS / "audit_full_inventory.csv", FULL_FIELDS, full_audit_by_id.values())
    print(f"产物已从源表+研究队列重建：表1={len(corrections)}，表2={len(corrected_rows)}，表3={len(uncertain)}，表4={len(split_rows)}，表5=0；全库复审={len(full_audit)}")


if __name__ == "__main__":
    main()
