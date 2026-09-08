# -*- coding: utf-8 -*-
"""按素材名称同步代表车型的 Eagle 存在状态，并可追加尺码标签。"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "车型代表分析" / "output" / "代表车型.csv"
SNAPSHOT = (
    ROOT
    / "车型代表分析"
    / "changes"
    / "2026-09-07_01_all-size-representatives"
    / "代表车型.csv"
)
API = "http://localhost:41595"
TAG_PREFIX = "0907"


def api_get(path: str, **params):
    url = f"{API}{path}"
    if params:
        url += "?" + urlencode(params)
    with urlopen(url, timeout=30) as response:
        payload = json.load(response)
    if payload.get("status") != "success":
        raise RuntimeError(f"Eagle API failed: {payload}")
    return payload.get("data")


def api_post(path: str, payload: dict):
    request = Request(
        f"{API}{path}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get("status") != "success":
        raise RuntimeError(f"Eagle API failed: {result}")
    return result.get("data")


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply-tags", action="store_true", help="向命中素材追加 0907_<型号> 标签并写回 CSV")
    args = parser.parse_args()

    with OUTPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = list(rows[0]) if rows else []

    items = api_get("/api/item/list", limit=10000, offset=0, orderBy="NAME") or []
    by_name: dict[str, list[dict]] = {}
    for item in items:
        by_name.setdefault(normalize(item.get("name", "")), []).append(item)

    matched_rows = 0
    matched_items: dict[str, tuple[dict, set[str]]] = {}
    for row in rows:
        matches: dict[str, dict] = {}
        for field in ("dimension-id", "车型"):
            for item in by_name.get(normalize(row.get(field, "")), []):
                matches[item["id"]] = item
        row["in_eagle"] = "1" if matches else "0"
        if matches:
            matched_rows += 1
            label = f"{TAG_PREFIX}_{row['型号']}"
            for item in matches.values():
                if item["id"] not in matched_items:
                    matched_items[item["id"]] = (item, set())
                matched_items[item["id"]][1].add(label)

    pending = 0
    if args.apply_tags:
        for item, labels in matched_items.values():
            tags = list(item.get("tags") or [])
            missing = sorted(label for label in labels if label not in tags)
            if missing:
                api_post("/api/item/update", {"id": item["id"], "tags": tags + missing})
                pending += len(missing)
        for target in (OUTPUT, SNAPSHOT):
            with target.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

    print(
        json.dumps(
            {
                "eagle_items": len(items),
                "representative_rows": len(rows),
                "matched_rows": matched_rows,
                "matched_items": len(matched_items),
                "tags_added": pending if args.apply_tags else None,
                "applied": args.apply_tags,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
