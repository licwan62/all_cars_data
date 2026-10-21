"""尺码规则的稳定标识（规则ID）。

规则ID 由规则行规范化后的字段内容生成：去掉首尾空白、数值统一格式（4140 与 4140.0 相同）、空值统一为空，
按列名排序后取 SHA-256 前 10 位，前缀 ``R``。``备注`` 只是说明文字，不参与标识。
同一内容在不同规则文件版本中得到同一个 ID；ID 的含义以生成该全量表时 ``data/当前规则.yaml`` 指定的规则文件为准
（报告「规则表」末列给出每行的规则ID，全量表的 ``规则ID`` 列与之对应）。
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Iterable, Mapping

import pandas as pd

RULE_ID_COLUMN = "规则ID"
# 不影响匹配语义的说明列
IGNORED_COLUMNS = frozenset({"备注", RULE_ID_COLUMN})


def _normalized(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    if not text:
        return ""
    try:
        number = float(text.replace(",", ""))
    except ValueError:
        return " ".join(text.split())
    if math.isfinite(number):
        return f"{number:.6f}".rstrip("0").rstrip(".") or "0"
    return text


def rule_id(row: Mapping[str, object], columns: Iterable[str]) -> str:
    canonical = {
        str(column).strip(): _normalized(row.get(column))
        for column in columns
        if str(column).strip() and str(column).strip() not in IGNORED_COLUMNS and not str(column).startswith("_")
    }
    digest = hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return f"R{digest[:10]}"


def rule_ids(rules: pd.DataFrame) -> pd.Series:
    """规则表每行的规则ID（按原始列计算，与行序无关）。"""
    columns = list(rules.columns)
    return pd.Series(
        [rule_id(row, columns) for row in rules.to_dict(orient="records")],
        index=rules.index,
        dtype="string",
    )
