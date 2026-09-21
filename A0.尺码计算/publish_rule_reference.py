#!/usr/bin/env python3
"""把 US/EU/RU 三套独立维护的尺码规则和店铺货架配置整理进 output/，供网站参考页读取。

输入（都在本 agent 的 data/ 下）：
  data/us/0917.1-新命名.csv        -> output/尺码匹配规则.csv（US，沿用既有稳定文件名）
  data/eu/尺码匹配规则.csv          -> output/尺码匹配规则_EU.csv
  data/ru/尺寸/0921.2-真实上限.csv -> output/尺码匹配规则_RU.csv
  data/店铺分组/货架.yaml           -> output/店铺货架.csv（店铺,匹配尺码,发货尺码）

任何输入缺失或缺少必需列时失败，不改变 output/。之后由scripts/publish_release.py 生成带后缀的 artifact。
"""

from __future__ import annotations

import csv
import io
import os
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent
OUTPUT = PROJECT / "output"
RULE_SOURCES = {
    "尺码匹配规则.csv": (PROJECT / "data" / "us" / "0917.1-新命名.csv", "尺码"),
    "尺码匹配规则_EU.csv": (PROJECT / "data" / "eu" / "尺码匹配规则.csv", "尺码"),
    "尺码匹配规则_RU.csv": (PROJECT / "data" / "ru" / "尺寸" / "0921.2-真实上限.csv", "亚马逊尺码"),
}
SHELF_CONFIG = PROJECT / "data" / "店铺分组" / "货架.yaml"
SHELF_OUTPUT = "店铺货架.csv"


def shelf_rows(config_path: Path = SHELF_CONFIG) -> list[list[str]]:
    stores = (yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}).get("店铺") or {}
    rows = []
    for store, body in stores.items():
        for item in (body or {}).get("尺码映射") or []:
            match, ship = item.get("匹配尺码"), item.get("发货尺码")
            if not match or not ship:
                raise ValueError(f"店铺 {store} 的尺码映射缺少匹配尺码或发货尺码：{item}")
            rows.append([store, str(match), str(ship)])
    if not rows:
        raise ValueError(f"{config_path} 没有店铺尺码映射")
    return rows


def build_payloads() -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    for name, (source, size_column) in RULE_SOURCES.items():
        if not source.is_file():
            raise ValueError(f"缺少规则文件：{source}")
        data = source.read_bytes()
        header = next(csv.reader(io.StringIO(data.decode("utf-8-sig"))), [])
        if size_column not in header:
            raise ValueError(f"{source.name} 缺少列 {size_column}")
        payloads[name] = data
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["店铺", "匹配尺码", "发货尺码"])
    writer.writerows(shelf_rows())
    payloads[SHELF_OUTPUT] = ("﻿" + buffer.getvalue()).encode("utf-8")
    return payloads


def main() -> int:
    try:
        payloads = build_payloads()
    except ValueError as error:
        print(f"整理规则失败：{error}", file=sys.stderr)
        return 2
    OUTPUT.mkdir(exist_ok=True)
    for name, data in payloads.items():
        target = OUTPUT / name
        temporary = target.with_name(f".{name}.tmp")
        temporary.write_bytes(data)
        os.replace(temporary, target)
        print(f"{name}: {len(data)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
