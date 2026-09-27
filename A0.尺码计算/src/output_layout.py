"""A0 output/ 的稳定交付物布局：<国别>/<类别>/<文件>。

  <国别>/尺码匹配报告.md           所用规则（全文）、参数、大致匹配状况（US 另含店铺与 TRIM 概况）
  <国别>/全量/全量表.csv            各区域全量表（只有 US 带 TRIM 列）
  US/店铺/店铺全量_<店铺>.csv       店铺全量（US 行、店铺发货尺码、带 TRIM）
  US/TRIM/TRIM适配器.csv            Year+Make+Model -> DIMENSION-ID + 尺码

路径均相对节点 output/ 目录，使用 POSIX 分隔符，与 pipeline.json 的 outputs 一致。
"""

from __future__ import annotations

REGIONS = ("US", "EU", "RU")
STORE_REGION = "US"


def full_table(region: str) -> str:
    return f"{region}/全量/全量表.csv"


def match_report(region: str) -> str:
    return f"{region}/尺码匹配报告.md"


TRIM_ADAPTER = f"{STORE_REGION}/TRIM/TRIM适配器.csv"


def store_table(store: str) -> str:
    return f"{STORE_REGION}/店铺/店铺全量_{store}.csv"
