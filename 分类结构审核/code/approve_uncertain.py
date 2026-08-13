from __future__ import annotations

import csv
import json
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

from research_queue import atomic_write, read_rows


ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "output" / "research_queue" / "queue.csv"
SOURCE = next(path for path in (ROOT / "车型尺寸库.csv", ROOT / "source" / "车型尺寸库.csv") if path.exists())
SPLITS = ROOT / "output" / "research_queue" / "approved_splits.json"
CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_record_id(used: set[str]) -> str:
    while True:
        value = (int(time.time() * 1000) << 80) | secrets.randbits(80)
        encoded = ""
        for _ in range(26):
            encoded = CROCKFORD[value & 31] + encoded
            value >>= 5
        record_id = f"CAR-{encoded}"
        if record_id not in used:
            used.add(record_id)
            return record_id


def main() -> None:
    queue = read_rows(QUEUE)
    source = read_rows(SOURCE)
    blocked = [row for row in queue if row.get("status") == "blocked"]
    if not blocked:
        print("没有待批准的 uncertain/blocked 项。")
        return

    used = {row.get("DIMENSION-ID", "") for row in source}
    existing_splits = json.loads(SPLITS.read_text(encoding="utf-8")) if SPLITS.exists() else []
    used.update(part["DIMENSION-ID"] for split in existing_splits for part in split.get("records", []))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    land_cruiser = next((row for row in blocked if row.get("MAKE") == "Toyota" and row.get("MODEL") == "Land Cruiser"), None)
    if land_cruiser and not any(item.get("original_dimension_id") == land_cruiser["DIMENSION-ID"] for item in existing_splits):
        original = next(row for row in source if row.get("DIMENSION-ID") == land_cruiser["DIMENSION-ID"])
        evidence = "https://global.toyota/en/mobility/toyota-brand/features/landcruiser/history/evolution/heavy-duty.html | https://global.toyota/en/mobility/toyota-brand/features/landcruiser/history/evolution/station-wagon.html"
        existing_splits.append({
            "original_dimension_id": original["DIMENSION-ID"],
            "approved_at": now,
            "reason": "用户批准按 Toyota 官方谱系拆分 1958-1980：20/40 Series Van/Hardtop、20/40 Series Pickup、50/early 60 Series Station Wagon。",
            "source_url": evidence,
            "records": [
                {
                    "DIMENSION-ID": original["DIMENSION-ID"],
                    "版本": "50 Series / early 60 Series Station Wagon",
                    "结构": "Wagon",
                    "YEAR": "1967-1980",
                    "分类": "两厢车",
                    "参考车型": "1967-1980 Toyota Land Cruiser FJ55 / early 60 Series Station Wagon",
                    "备注": "由原 1958-1980 混合记录拆分；Station Wagon 按车衣规则归两厢车",
                    "迭代状态": "可入库"
                },
                {
                    "DIMENSION-ID": new_record_id(used),
                    "版本": "20/40 Series Van/Hardtop",
                    "结构": "SUV",
                    "YEAR": "1958-1980",
                    "分类": "越野车",
                    "L-IN": "",
                    "W-IN": "",
                    "H-IN": "",
                    "参考车型": "1958-1980 Toyota Land Cruiser 20/40 Series Van/Hardtop",
                    "备注": "自动生成 record_id；结构拆分已批准，具体版本尺寸需另行维护",
                    "迭代状态": "待补尺寸"
                },
                {
                    "DIMENSION-ID": new_record_id(used),
                    "版本": "20/40 Series Pickup",
                    "结构": "Pickup",
                    "YEAR": "1958-1980",
                    "分类": "皮卡",
                    "L-IN": "",
                    "W-IN": "",
                    "H-IN": "",
                    "参考车型": "1958-1980 Toyota Land Cruiser 20/40 Series Pickup",
                    "备注": "自动生成 record_id；结构拆分已批准，CAB/BED 与具体版本尺寸需另行维护",
                    "迭代状态": "待补尺寸"
                }
            ]
        })

    for row in blocked:
        row["status"] = "done"
        row["worker"] = "user-approved"
        row["updated_at"] = now
        if row is land_cruiser:
            row["confidence"] = "高"
            row["note"] += " 用户已批准拆分；新增输出记录由脚本自动生成唯一 record_id。"
        else:
            row["note"] += " 用户已批准应用到 output 审核产物；受保护源文件仍不自动修改。"

    SPLITS.write_text(json.dumps(existing_splits, ensure_ascii=False, indent=2), encoding="utf-8")
    atomic_write(queue)
    print(f"已批准 {len(blocked)} 条；Land Cruiser 拆分清单已保存，新增记录自动生成 ID。")


if __name__ == "__main__":
    main()
