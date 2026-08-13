from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "output" / "artifacts"
QUEUE = ROOT / "output" / "research_queue" / "queue.csv"
QUEUE_FIELDS = ["queue_key", "DIMENSION-ID", "MAKE", "MODEL", "版本", "YEAR", "issue_type", "current_structure", "suspected_structure", "status", "worker", "suggested_structure", "suggested_category", "confidence", "source_url", "note", "updated_at"]
SUBURBAN_SOURCE = "https://media.chevrolet.com/content/dam/Media/images/INTL/chevrolet/company-tab/2013/history/chevrolet_history_en_2013.pdf"
SUBURBAN_SPEC = "https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet-trucks/1955-Chevrolet-Truck-1st-Series.pdf"


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)
    os.replace(temp, path)


def main() -> None:
    source_fields, source = read(ROOT / "车型尺寸库.csv")
    source_by_id = {row["DIMENSION-ID"]: row for row in source}

    t1_fields, t1 = read(ART / "audit_table1_corrections.csv")
    suburban_ids = {r["DIMENSION-ID"] for r in t1 if r.get("MAKE") == "Chevrolet" and r.get("MODEL") == "Suburban" and r.get("原结构") == "Pickup"}
    t1 = [r for r in t1 if r["DIMENSION-ID"] not in suburban_ids]
    allowed_categories = {"两厢车", "跑车", "三厢车", "越野车", "皮卡"}
    for row in t1:
        source_category = source_by_id.get(row["DIMENSION-ID"], {}).get("分类", row.get("原分类", ""))
        if row.get("建议分类") not in allowed_categories:
            row["建议分类"] = source_category
    write(ART / "audit_table1_corrections.csv", t1_fields, t1)

    t2_fields, t2 = read(ART / "audit_table2_corrected.csv")
    t2 = [source_by_id.get(r["DIMENSION-ID"], r) if r["DIMENSION-ID"] in suburban_ids else r for r in t2]
    for row in t2:
        if row.get("分类") not in allowed_categories:
            row["分类"] = source_by_id.get(row["DIMENSION-ID"], {}).get("分类", row.get("分类", ""))
    write(ART / "audit_table2_corrected.csv", t2_fields, t2)

    t3_fields, t3 = read(ART / "audit_table3_uncertain.csv")
    t3 = [r for r in t3 if r["DIMENSION-ID"] not in suburban_ids]
    for rid in sorted(suburban_ids, key=lambda x: source_by_id[x].get("YEAR", "")):
        row = source_by_id[rid]
        t3.append({"DIMENSION-ID": rid, "MAKE": row["MAKE"], "MODEL": row["MODEL"], "版本": row["版本"],
                   "YEAR": row["YEAR"], "当前结构": row["结构"], "疑似结构": "Wagon/SUV",
                   "问题": "历史 Suburban 为卡车底盘上的封闭 Carryall；结构标签需按 YEAR 人工裁定",
                   "需要补充的信息": "当年官方规格、车身照片、是否有独立开放货斗",
                   "建议处理方式": "仅供用户人工复核，禁止自动应用"})
    write(ART / "audit_table3_uncertain.csv", t3_fields, t3)

    t5_fields, t5 = read(ART / "audit_table5_other.csv")
    wagon_issue = "结构 Wagon 通常对应分类 旅行车"
    removed = [r for r in t5 if r.get("疑似问题") == wagon_issue]
    t5 = [r for r in t5 if r.get("疑似问题") != wagon_issue]
    write(ART / "audit_table5_other.csv", t5_fields, t5)

    _, queue = read(QUEUE)
    queue = [row for row in queue if not (
        row.get("issue_type") == "uncertain" and row.get("MAKE") == "Chevrolet" and row.get("MODEL") == "Suburban"
    )]
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for row in queue:
        if row.get("issue_type") == "other" and row.get("note") == wagon_issue:
            row.update(status="done", worker="business-rule", suggested_category="两厢车", confidence="高",
                       source_url="doc/车衣分类业务规则.md",
                       note="按固定五类车衣业务规则，Wagon 保持分类=两厢车；原异常为误报。", updated_at=stamp)
        if row.get("DIMENSION-ID") in suburban_ids and row.get("issue_type") == "correction":
            row.update(status="blocked", worker="manual-review-required", suggested_structure="Wagon/SUV",
                       suggested_category="越野车", confidence="中",
                       source_url=f"{SUBURBAN_SOURCE} | {SUBURBAN_SPEC}",
                       note=f"YEAR={row.get('YEAR')}。官方历史称其为卡车底盘上的封闭乘员车/早期 station wagon 与 SUV 原型；1955 规格为 8 座全钢封闭 Carryall。不得按底盘判 Pickup，也不得自动改 SUV，须用户逐年份人工复核。", updated_at=stamp)
    write(QUEUE, QUEUE_FIELDS, queue)
    print(f"已撤下 Suburban 自动修正 {len(suburban_ids)} 条；Wagon 分类误报已解决 {len(removed)} 条。")


if __name__ == "__main__":
    main()
