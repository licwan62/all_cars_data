"""从差评原文推断每个 品牌+车型 的耳位（车罩后视镜开口位置：普通/靠前/靠后）。

背景：车罩后视镜开口位置不对是一类反复出现的差评（"后视镜袋位置太靠前/靠后"），过去靠
B1.压缩定制评分 自己的 data/车耳状态登记.csv 人工登记，长期只登记了个别车型。现在改成从
差评原文自动提取信号，作为 B0 的稳定输出，供下游按 品牌+车型 直接读取、不再人工登记。

规则：
- 差评文本先命中 data/耳位筛选规则.json 里的"车耳信号"（mirror/后视镜/...），才算是耳位相关
  差评；否则跳过（不当作"耳位正常"，而是"没有信号"）。
- 命中车耳信号后，再看是否命中"靠前信号"/"靠后信号"；只命中一侧记对应方向，两侧都命中或
  都没命中记"普通"。
- 单条差评的车型（如 "Chrysler Pacifica"）不含结构，借用
  build_size_analysis_summary.match_analysis_row 的匹配逻辑对到 差评分析表.csv 的
  品牌+车型（丢弃结构，因为耳位是整车型属性，与具体结构无关）。
- 按 品牌+车型 聚合：只要有一条 靠前 证据就记 靠前；否则只要有 靠后 证据就记 靠后；否则
  （只有普通证据）记 普通。没有任何耳位相关差评的 品牌+车型 不出现在汇总表里（没有信号，
  不是"耳位正常"）。
"""

from __future__ import annotations

import csv
import importlib.util
import json
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
RULES = PROJECT / "data" / "耳位筛选规则.json"
ANALYSIS = PROJECT / "output" / "差评分析表.csv"
DETAIL_OUTPUT = PROJECT / "data" / "03.耳位问题清单.csv"

DETAIL_FIELDS = (
    "耳位问题主键", "差评汇总外键", "车型", "耳位(普通/靠前/靠后)",
    "差评分析表-品牌", "差评分析表-车型", "英文", "翻译", "差评点",
)
SUMMARY_FIELDS = ("品牌", "车型", "耳位(普通/靠前/靠后)", "证据条数")

_DIRECTION_PRIORITY = ("靠前", "靠后", "普通")


def classify_ear_position(text: str, rules: dict) -> str | None:
    folded = size_mod.normalise(text)
    if not any(size_mod.normalise(signal) in folded for signal in rules["车耳信号"]):
        return None
    forward = any(size_mod.normalise(signal) in folded for signal in rules["靠前信号"])
    backward = any(size_mod.normalise(signal) in folded for signal in rules["靠后信号"])
    if forward and not backward:
        return "靠前"
    if backward and not forward:
        return "靠后"
    return "普通"


def build(
    source: Path = SOURCE,
    rules_path: Path = RULES,
    analysis: Path = ANALYSIS,
    detail_output: Path = DETAIL_OUTPUT,
) -> tuple[list[dict], dict]:
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with analysis.open(encoding="utf-8-sig", newline="") as handle:
        analysis_rows = list(csv.DictReader(handle))

    details = []
    by_model: dict[tuple[str, str], dict[str, int]] = {}
    for row in rows:
        text = " ".join((row.get("英文", ""), row.get("翻译", ""), row.get("差评点", "")))
        direction = classify_ear_position(text, rules)
        if direction is None:
            continue
        matched = size_mod.match_analysis_row(row, analysis_rows)
        details.append({
            "耳位问题主键": size_mod.stable_key("B0-EAR", (row.get("差评汇总主键", ""),)),
            "差评汇总外键": row.get("差评汇总主键", ""),
            "车型": row.get("车型", ""),
            "耳位(普通/靠前/靠后)": direction,
            "差评分析表-品牌": matched.get("品牌", "") if matched else "",
            "差评分析表-车型": matched.get("车型", "") if matched else "",
            "英文": row.get("英文", ""), "翻译": row.get("翻译", ""), "差评点": row.get("差评点", ""),
        })
        if not matched:
            continue
        model_key = (matched.get("品牌", ""), matched.get("车型", ""))
        counts = by_model.setdefault(model_key, {"靠前": 0, "靠后": 0, "普通": 0})
        counts[direction] += 1

    summary = []
    for (brand, model), counts in sorted(by_model.items()):
        direction = next(label for label in _DIRECTION_PRIORITY if counts[label])
        summary.append({
            "品牌": brand, "车型": model, "耳位(普通/靠前/靠后)": direction,
            "证据条数": sum(counts.values()),
        })

    with detail_output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(DETAIL_FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(details)

    report = {"耳位相关差评条数": len(details), "涉及车型数": len(summary)}
    return summary, report
