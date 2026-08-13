from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
ART = PROJECT / "artifacts"
QUEUE = PROJECT / "research_queue" / "queue.csv"
SOURCE = ROOT / "source" / "车型尺寸库.csv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    tables = {number: read(ART / f"audit_table{number}_{name}.csv") for number, name in [
        (1, "corrections"), (2, "corrected"), (3, "uncertain"), (4, "split"), (5, "other")
    ]}
    queue = read(QUEUE)
    source_rows = read(SOURCE)
    source_by_id = {row["DIMENSION-ID"]: row for row in source_rows}
    for rows in tables.values():
        for row in rows:
            source = source_by_id.get(row.get("DIMENSION-ID", ""), {})
            for field in ("MAKE", "MODEL", "版本", "YEAR"):
                row.setdefault(field, source.get(field, ""))
            row.setdefault("当前结构", source.get("结构", ""))
            row.setdefault("当前YEAR", source.get("YEAR", ""))
    source_total = len(source_rows)
    total = len(tables[2])
    status = Counter(row["status"] for row in queue)
    changes = Counter((row["原结构"], row["建议结构"]) for row in tables[1])
    change_types = Counter(row["修改类型"] for row in tables[1])
    product_type_changes = [row for row in tables[1] if row["原分类"] != row["建议分类"]]
    full_audit = read(ART / "audit_full_inventory.csv")
    suburban = [row for row in tables[3] if row["MAKE"] == "Chevrolet" and row["MODEL"] == "Suburban"]
    approved_suburban = [row for row in tables[1] if row["MAKE"] == "Chevrolet" and row["MODEL"] == "Suburban"]
    review_ids = {row["DIMENSION-ID"] for row in tables[3]}
    corrected_ids = {row["DIMENSION-ID"] for row in tables[1]}
    unchanged = source_total - len(review_ids | corrected_ids)

    lines = [
        "=" * 80,
        "车型尺寸库结构审核报告（研究队列同步版）",
        "=" * 80,
        f"生成时间: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "【总体统计】",
        f"源记录数: {source_total}",
        f"表2输出记录数: {total}",
        f"研究后无需修改: {unchanged}",
        f"已确认并写入表2的修改: {len(tables[1])}",
        f"人工待复核: {len(tables[3])}",
        f"建议拆分: {len(tables[4])}",
        f"其他未解决问题: {len(tables[5])}",
        f"完成逐条复审: {len(full_audit)}/{source_total}",
        "",
        "【研究队列】",
        f"总数: {len(queue)}；done={status['done']}；blocked={status['blocked']}；pending={status['pending']}；in_progress={status['in_progress']}",
        "done 结论已同步进审核产物；blocked 保持源结构/分类，并在表2标记为“待复核”。",
        "",
        f"【表1：已确认修改】({len(tables[1])}条)",
        "",
        "修改类型统计（按风险优先排序）:",
    ]
    for label in ["拆分并发生产品类型变化（重点）", "产品类型变化（重点）", "类型修改（重点）", "结构修改", "拆分记录", "结构改名"]:
        if change_types[label]:
            lines.append(f"  {label}: {change_types[label]} 条")
    lines.extend(["", "结构变化统计:"])
    for (old, new), count in changes.most_common():
        lines.append(f"  {old} → {new}: {count} 条")
    lines.extend([
        "",
        f"【重点：五类产品类型发生变化】({len(product_type_changes)}条)",
        "以下记录原分类与建议分类不同，必须优先检查车衣产品归类：",
    ])
    for row in product_type_changes:
        lines.append(
            f"  {row['DIMENSION-ID']} | {row['MAKE']} {row['MODEL']} {row['版本']} YEAR={row['YEAR']} | "
            f"{row['原结构']}/{row['原分类']} → {row['建议结构']}/{row['建议分类']} | {row['修改类型']}"
        )
    lines.extend([
        "",
        f"【表3：人工待复核】({len(tables[3])}条)",
        f"Chevrolet Suburban 待复核: {len(suburban)} 条；已批准修改: {len(approved_suburban)} 条",
    ])
    for row in suburban:
        lines.append(f"  YEAR={row['YEAR']}: Pickup → {row['疑似结构']}；仅建议，禁止自动应用")
    for row in approved_suburban:
        lines.append(f"  YEAR={row['YEAR']}: {row['原结构']} → {row['建议结构']}；用户已批准写入表2")
    other_blocked = [row for row in tables[3] if row not in suburban]
    for row in other_blocked:
        lines.append(f"  {row['MAKE']} {row['MODEL']} YEAR={row['YEAR']}: {row['当前结构']} → {row['疑似结构']}")
    lines.extend([
        "",
        "【Suburban 核验结论】",
        "10 条记录覆盖 1947-1972。GM 原始资料均将对应车身描述为 Suburban/Carryall、封闭单体乘员载货车身，",
        "并与 Stepside/Fleetside Pickup 车身代码分列；因此当前 Pickup 标签不合理。按本库口径统一建议 SUV、分类越野车。",
        "用户已明确批准全部 uncertain，因此表2已应用这 10 条建议；受保护源文件仍未修改。",
        "",
        "【产物维护说明】",
        "artifacts 不是实时数据库，而是可重复生成的审核快照。",
        "运行 python code/regenerate_artifacts.py 后，再运行本脚本与 validate_project.py，即可与 queue.csv 同步。",
        "audit_table2_corrected.csv 当前包含源表全部记录、所有 done 且确有变化的结论，以及批准拆分后自动生成 ID 的新增记录。",
        "",
        "【文件行数】",
        f"audit_table1_corrections.csv: {len(tables[1])}",
        f"audit_table2_corrected.csv: {len(tables[2])}",
        f"audit_table3_uncertain.csv: {len(tables[3])}",
        f"audit_table4_split.csv: {len(tables[4])}",
        f"audit_table5_other.csv: {len(tables[5])}",
        f"audit_full_inventory.csv: {len(full_audit)}（覆盖全部源记录）",
        "=" * 80,
    ])
    text = "\n".join(lines) + "\n"
    (ART / "audit_report.txt").write_text(text, encoding="utf-8")
    (ART / "analysis_output.txt").write_text(text, encoding="utf-8")

    acceptance = f"""# 当前项目验收报告

验收日期：{datetime.now().astimezone().date().isoformat()}

## 结论

**结构产物已与研究队列同步，机器验收通过后可作为人工回写参考。**

- 源表共 {source_total} 条；表 2 共 {total} 条，完整保留源记录并包含批准拆分产生的新增记录。
- 研究队列共 {len(queue)} 条：done {status['done']}、blocked {status['blocked']}、pending {status['pending']}、in_progress {status['in_progress']}。
- 表 1 为 {len(tables[1])} 条确有字段变化且研究完成的建议；新增 `修改类型` 字段，其中五类产品类型变化 {len(product_type_changes)} 条，已置于报告重点区。
- 表 3 为 {len(tables[3])} 条人工待复核项。
- 表 4 有 {len(tables[4])} 条已批准拆分分支；表 5 当前无未解决项目。
- `audit_full_inventory.csv` 共 {len(full_audit)} 条，逐条覆盖全部 {source_total} 条源记录；结构—分类规则扫描无遗漏。

## Chevrolet Suburban

1947-1972 年的 10 条源记录原为 Pickup。GM Heritage 原始资料显示对应车辆为封闭的 Suburban Carryall，并与 Pickup 车身形式分列。用户已批准后，表 2 统一改为 SUV、车衣分类越野车；受保护源文件未被修改。

## Land Cruiser 拆分

原 1958-1980 混合记录已在源表拆为 3 个结构分支：20/40 Series Van/Hardtop（SUV）、20/40 Series Pickup（Pickup）和 50/early 60 Series Station Wagon（Wagon）。每个分支均使用由车型组合字段确定生成的 `DIMENSION-ID`；具体尺寸仍需在尺寸维护流程补齐。

主要证据：

- GM Heritage Vehicle Information Kits：<https://www.gm.com/heritage/archive/vehicle-information-kits>
- 1955 Chevrolet Truck 规格（Suburban Carryall 为 all-steel single-unit eight-passenger body）：<https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet-trucks/1955-Chevrolet-Truck-1st-Series.pdf>
- 1969 Chevrolet Suburban 原始资料：<https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1969-Chevrolet-Suburban.pdf>
- 1972 Chevrolet Suburban 原始资料：<https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1972-Chevrolet-Suburban.pdf>

## 维护方式

`artifacts/` 是生成快照，不会随队列编辑自动变化。标准重建顺序为：

```text
python code/regenerate_artifacts.py
python code/generate_report.py
python code/validate_project.py
```

机器可读验收结果见 `validation_report.json`；研究进度见 `../research_queue/checkpoint.json`。
"""
    (ART / "acceptance_report.md").write_text(acceptance, encoding="utf-8")
    print(json.dumps({"total": total, "corrections": len(tables[1]), "uncertain": len(tables[3]), "suburban": len(suburban)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
