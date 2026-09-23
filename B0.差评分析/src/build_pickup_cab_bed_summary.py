"""按 品牌+车型 汇总差评原文里能识别出的皮卡驾驶室/货斗信息，供下游拼进差评备注。

背景：原始台账的"提取驾驶室"/"提取货斗"结构化字段覆盖率很低（1217 行里各自只有 10 条
左右有值），但同样的信息其实大量直接写在"车型"原始文本里（如
"Chevrolet Silverado 1500(1998-24) Crew Cab SB Bed"、"C10(60-87)-Regular Cab LB"）。
所以这里优先解析"车型"文本，解析不出来时才退回结构化字段，尽量提高覆盖率。

驾驶室类型（大小写、空格不敏感）：Crew Cab（含 SuperCrew）、King Cab、Double Cab、
Quad Cab、Super Cab、Extended Cab、Regular Cab。
货斗长度：Long Bed（含缩写 LB）、Short Bed（含缩写 SB）。

一条差评可能同时有驾驶室和货斗信息，也可能只有其中一个；两者都没有则跳过（不是"没有驾驶室
信息"，而是"这条差评没提到"）。按 品牌+车型 聚合后统计每种组合出现的次数。
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "b0_build_size_analysis_summary", _HERE / "build_size_analysis_summary.py"
)
assert _spec and _spec.loader
size_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(size_mod)

PROJECT = _HERE.parent
SOURCE = PROJECT / "data" / "00.差评分析汇总.csv"
ANALYSIS = PROJECT / "output" / "差评分析表.csv"

SUMMARY_FIELDS = ("品牌", "车型", "驾驶室货斗备注", "证据条数")

CAB_PATTERNS = [
    (re.compile(r"super\s*crew", re.I), "Crew Cab"),
    (re.compile(r"crew\s*cab", re.I), "Crew Cab"),
    (re.compile(r"king\s*cab", re.I), "King Cab"),
    (re.compile(r"double\s*cab", re.I), "Double Cab"),
    (re.compile(r"quad\s*cab", re.I), "Quad Cab"),
    (re.compile(r"super\s*cab", re.I), "Super Cab"),
    (re.compile(r"extended\s*cab", re.I), "Extended Cab"),
    (re.compile(r"regular\s*cab", re.I), "Regular Cab"),
]
BED_PATTERNS = [
    (re.compile(r"long\s*bed", re.I), "Long Bed"),
    (re.compile(r"\blb\b", re.I), "Long Bed"),
    (re.compile(r"short\s*bed", re.I), "Short Bed"),
    (re.compile(r"\bsb\b", re.I), "Short Bed"),
]


def extract_cab_bed(row: dict[str, str]) -> tuple[str, str]:
    text = row.get("车型", "") or ""
    cab = next((label for pattern, label in CAB_PATTERNS if pattern.search(text)), "")
    bed = next((label for pattern, label in BED_PATTERNS if pattern.search(text)), "")
    if not cab:
        cab = (row.get("提取驾驶室") or "").strip()
    if not bed:
        bed = (row.get("提取货斗") or "").strip()
    return cab, bed


def build(source: Path = SOURCE, analysis: Path = ANALYSIS) -> tuple[list[dict], dict]:
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with analysis.open(encoding="utf-8-sig", newline="") as handle:
        analysis_rows = list(csv.DictReader(handle))

    by_model: dict[tuple[str, str], dict[str, int]] = {}
    matched_count = 0
    for row in rows:
        cab, bed = extract_cab_bed(row)
        if not cab and not bed:
            continue
        matched = size_mod.match_analysis_row(row, analysis_rows)
        if not matched:
            continue
        matched_count += 1
        label = "/".join(part for part in (cab, bed) if part)
        model_key = (matched.get("品牌", ""), matched.get("车型", ""))
        counts = by_model.setdefault(model_key, {})
        counts[label] = counts.get(label, 0) + 1

    summary = []
    for (brand, model), counts in sorted(by_model.items()):
        note = "；".join(f"{label}({count})" for label, count in sorted(counts.items(), key=lambda kv: -kv[1]))
        summary.append({
            "品牌": brand, "车型": model, "驾驶室货斗备注": note,
            "证据条数": sum(counts.values()),
        })

    report = {"驾驶室货斗相关差评条数": matched_count, "涉及车型数": len(summary)}
    return summary, report
