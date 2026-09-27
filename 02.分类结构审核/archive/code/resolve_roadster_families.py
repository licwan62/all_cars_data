from __future__ import annotations

import csv
import json
from pathlib import Path

from research_queue import QUEUE_FILE, batch_update

OUT = Path(__file__).resolve().parents[1] / "research_queue" / "batch_2026-08-12_roadster_families.json"

SOURCES = {
    ("BMW", "Z3"): ("https://www.press.bmwgroup.com/usa/article/detail/T0454065EN_US/the-bmw-z4-final-edition?language=en_US", "BMW 官方历史把 Z3 定义为经典 open-top two-seater，并作为 Z4 Roadster 前身。"),
    ("BMW", "Z4"): ("https://www.press.bmwgroup.com/usa/article/detail/T0454065EN_US/the-bmw-z4-final-edition?language=en_US", "BMW 官方确认各代 Z4 分别采用电动软顶或可收折硬顶，属于开放式 Roadster。"),
    ("BMW", "i8"): ("https://www.press.bmwgroup.com/usa/article/detail/T0276421EN_US/the-first-ever-2019-bmw-i8-roadster-and-new-2019-bmw-i8-coupe?showMedia=video", "BMW 官方明确区分 i8 Roadster 与 Coupe；Roadster 为双座电动软顶。"),
    ("Honda", "S2000"): ("https://global.honda/en/newsroom/worldnews/2007/4070919S2000.html", "Honda 官方明确 S2000 为 two-seat open-topped roadster，软顶/可拆硬顶均属 Convertible。"),
    ("Porsche", "911"): ("https://newsroom.porsche.com/en/products/porsche-911-speedster-new-york-auto-show-2019-17343.html", "该记录版本为 Speedster；开放式低风挡特殊车身按 Convertible 标准化。"),
    ("Porsche", "Boxster"): ("https://newsroom.porsche.com/en/history/porsche-986-boxster-roadster-modern-classic-car-show-bockhorn-repairs-servicing-custom-fitting-14806.html", "Porsche 官方确认 Boxster Roadster 使用可收折软顶，按 Convertible 标准化。"),
}

MERCEDES_SOURCE = "https://media.mercedes-benz.com/en/article/db0f1f54-6480-42a6-aa28-0b191983a3ba | https://media.mercedes-benz.com/en/article/fed4e320-acc8-46ff-a67c-b6b47466b8d4"


def main() -> None:
    with QUEUE_FILE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    updates = []
    for row in rows:
        if row.get("status") != "pending" or row.get("current_structure") != "Roadster":
            continue
        make, model = row.get("MAKE", ""), row.get("MODEL", "")
        source_note = SOURCES.get((make, model))
        if make == "Mercedes-Benz" and model in {"SL-Class", "SLK-Class", "SLC-Class"}:
            source_note = (MERCEDES_SOURCE, "Mercedes-Benz 官方历史确认 SL/SLK/SLC 的 Roadster 车身使用可拆顶、Vario-Roof 或软顶；按统一结构名 Convertible。")
        if not source_note:
            continue
        source, note = source_note
        updates.append({
            "queue_key": row["queue_key"], "status": "done", "worker": "codex-web-research",
            "suggested_structure": "Convertible", "suggested_category": "跑车", "confidence": "高",
            "source_url": source, "note": f"YEAR={row.get('YEAR')}；{note}",
        })
    OUT.write_text(json.dumps(updates, ensure_ascii=False, indent=2), encoding="utf-8")
    batch_update(OUT)
    print(f"Roadster 家族完成 {len(updates)} 条")


if __name__ == "__main__":
    main()
