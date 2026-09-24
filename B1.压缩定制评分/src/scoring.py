"""综合上游差评分析表，给出 品牌+车型 粒度的定制需求度（通用版型偏离度）评分。

2026-09-23 起改为单一维度：人工维护进度、车耳状态两个人工登记维度已删除（长期只有个别
车型有登记，覆盖率太低；车耳状态现在由 B0.差评分析 从差评原文自动提取，见下）。评分粒度
从 品牌+车型+结构 收窄为 品牌+车型：同一 品牌+车型 下不同结构（如 Sedan/Coupe）的差评
按各自"差评数量"加权平均合并成一行。

耳位（车罩后视镜开口靠前/靠后/普通）完全来自上游 B0.差评分析/output/耳位分析表.csv，
按 品牌+车型 直接透传展示，不参与评分。

差评备注：把各结构"主要差评原因"里属于尺寸/耳位问题的条目拼起来（质量差、拉链、绑带、
收纳袋这类和车身尺寸/耳位无关的问题不统计——那不是这张表要衡量的"通用版型偏离度"）；
只有一个结构时不加结构前缀（没有歧义）；多个结构时才逐条打上结构前缀。皮卡车型另外从
上游 B0.差评分析/output/皮卡驾驶室货斗分析表.csv 拼入驾驶室/货斗信息（如
"Crew Cab/Short Bed(11)"），因为同一皮卡车型不同驾驶室/货斗组合的车身尺寸差异很大，
定制时需要参考。

尺码：差评分析表.csv 各结构行的"尺码"按 品牌+车型 合并去重后透传，不参与评分。

年份：从差评分析表.csv 各结构行的"年份"列（人工登记的差评涉及年款，逗号分隔的 4 位年份）
合并去重后，压缩成 "95-97/26" 这种两位数年份+连续区间的格式；没有任何年份记录时留空，
留空代表"未知或者具有普遍性"（不是"没有这一维度"）。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import NamedTuple

DEFAULT_RULES = {
    "差评": {
        "占比字段": "差评占比",
        "分档字段": "严重度评级",
        "分档映射": {"低": 0.2, "中": 0.5, "高": 0.8},
    },
    "差评备注": {
        "尺寸关键词": [
            "尺寸", "版型", "实际尺寸",
            "太大", "太小", "太短", "太长", "太紧", "太松",
            "偏大", "偏小", "偏短", "偏长", "偏紧", "偏松",
        ],
        "耳位关键词": ["后视镜", "镜子", "耳朵", "耳位"],
        "排除前缀": [
            "绑带", "绷带", "收纳袋", "拉链", "防风带", "遮阳挡", "毛巾", "盒子", "泡沫板",
        ],
    },
    "thresholds": {"低": 0.34, "中": 0.67},
}


class ModelKey(NamedTuple):
    brand: str
    model: str


def read_csv_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def index_negative_review_by_model(rows: list[dict]) -> tuple[dict[ModelKey, list[dict]], list[dict]]:
    """按 品牌+车型 分组，一个 品牌+车型 下允许多条不同结构的行。

    只有当同一 品牌+车型+结构 出现两次时才算数据问题（结构归并映射已不需要——品牌+车型
    粒度下同车身的跨区域结构标注差异本来就会分到同一组）。
    """
    grouped: dict[ModelKey, list[dict]] = {}
    seen_structures: dict[ModelKey, set[str]] = {}
    duplicates: list[dict] = []
    for row in rows:
        brand = (row.get("品牌") or "").strip()
        model = (row.get("车型") or "").strip()
        if not brand or not model:
            continue
        key = ModelKey(brand, model)
        structure = (row.get("结构") or "").strip()
        seen = seen_structures.setdefault(key, set())
        if structure in seen:
            duplicates.append({"key": key._asdict(), "结构": structure})
        seen.add(structure)
        grouped.setdefault(key, []).append(row)
    return grouped, duplicates


def _index_by_model(rows: list[dict]) -> dict[ModelKey, dict]:
    indexed: dict[ModelKey, dict] = {}
    for row in rows:
        brand = (row.get("品牌") or "").strip()
        model = (row.get("车型") or "").strip()
        if brand and model:
            indexed[ModelKey(brand, model)] = row
    return indexed


index_ear_position_by_model = _index_by_model
index_cab_bed_by_model = _index_by_model


def _to_float(value: str) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return min(max(parsed, 0.0), 1.0)


def _to_weight(value: str) -> float:
    try:
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        return 0.0


def score_negative_review(row: dict, rules: dict) -> float | None:
    config = rules["差评"]
    ratio = _to_float(row.get(config["占比字段"], ""))
    if ratio is not None:
        return ratio
    bucket = (row.get(config["分档字段"]) or "").strip()
    return config["分档映射"].get(bucket)


def is_size_or_ear_reason(token: str, rules: dict) -> bool:
    """只保留和车身尺寸/耳位相关的差评原因，质量/拉链/绑带这类和"通用版型偏离度"无关。"""
    config = rules["差评备注"]
    if any(prefix in token for prefix in config["排除前缀"]):
        return False
    if any(keyword in token for keyword in config["耳位关键词"]):
        return True
    return any(keyword in token for keyword in config["尺寸关键词"])


def format_years(years: set[int]) -> str:
    """把一组年份压缩成 "95-97/26" 这种两位数+连续区间的格式；没有年份时返回空字符串。"""
    if not years:
        return ""
    ordered = sorted(years)
    groups: list[tuple[int, int]] = []
    start = prev = ordered[0]
    for year in ordered[1:]:
        if year == prev + 1:
            prev = year
            continue
        groups.append((start, prev))
        start = prev = year
    groups.append((start, prev))

    def two_digit(year: int) -> str:
        return f"{year % 100:02d}"

    return "/".join(two_digit(a) if a == b else f"{two_digit(a)}-{two_digit(b)}" for a, b in groups)


def _collect_years(rows: list[dict]) -> str:
    years: set[int] = set()
    for row in rows:
        for token in (row.get("年份") or "").split(","):
            token = token.strip()
            if token.isdigit() and len(token) == 4:
                years.add(int(token))
    return format_years(years)


def _collect_sizes(rows: list[dict]) -> str:
    """合并各结构行的"尺码"（本身可能是"3XL+；3XL"这种多值），去重并保持首次出现的顺序。"""
    sizes: list[str] = []
    for row in rows:
        for token in (row.get("尺码") or "").split("；"):
            token = token.strip()
            if token and token not in sizes:
                sizes.append(token)
    return "；".join(sizes)


def score_negative_review_group(rows: list[dict], rules: dict) -> tuple[float | None, str]:
    """把同一 品牌+车型 下各结构的差评行合并成一个评分和一段尺寸/耳位相关的备注。

    评分：按各结构行的"差评数量"加权平均；都没有差评数量时退化为简单平均。
    备注：只有一个结构时不加结构前缀；多个结构时把每个结构"主要差评原因"里和尺寸/耳位
    相关的条目逐条打上结构前缀再拼接，如 "sedan 尺寸不合适(3)；coupe 后视镜位置不对(1)"，
    质量差、拉链问题这类和版型无关的原因不统计。
    """
    structures = sorted({(row.get("结构") or "").strip() for row in rows} - {""})
    single_structure = len(structures) <= 1

    weighted_sum = 0.0
    weight_total = 0.0
    scores: list[float] = []
    notes: list[str] = []
    for row in sorted(rows, key=lambda r: (r.get("结构") or "")):
        score = score_negative_review(row, rules)
        if score is not None:
            scores.append(score)
            weight = _to_weight(row.get("差评数量", ""))
            weighted_sum += score * weight
            weight_total += weight
        structure = (row.get("结构") or "").strip()
        reason = (row.get("主要差评原因") or "").strip()
        if not reason or reason == "/":
            continue
        for token in reason.split("；"):
            token = token.strip()
            if not token or not is_size_or_ear_reason(token, rules):
                continue
            notes.append(token if single_structure else f"{structure.lower()} {token}")
    if not scores:
        return None, "；".join(notes)
    combined = weighted_sum / weight_total if weight_total > 0 else sum(scores) / len(scores)
    return combined, "；".join(notes)


def bucket_level(score: float | None, thresholds: dict) -> str:
    if score is None:
        return "数据不足"
    if score < thresholds["低"]:
        return "低"
    if score < thresholds["中"]:
        return "中"
    return "高"


def score_keys(
    keys: list[ModelKey],
    negative_review_rows: list[dict],
    ear_position_rows: list[dict],
    cab_bed_rows: list[dict] | None = None,
    rules: dict | None = None,
) -> tuple[list[dict], dict]:
    rules = rules or DEFAULT_RULES
    cab_bed_rows = cab_bed_rows or []
    grouped, dupes = index_negative_review_by_model(negative_review_rows)
    ear_by_key = index_ear_position_by_model(ear_position_rows)
    cab_bed_by_key = index_cab_bed_by_model(cab_bed_rows)

    scored: list[dict] = []
    for key in keys:
        rows_for_key = grouped.get(key, [])
        score, note = score_negative_review_group(rows_for_key, rules)
        cab_bed_row = cab_bed_by_key.get(key)
        cab_bed_note = (cab_bed_row.get("驾驶室货斗备注") or "").strip() if cab_bed_row else ""
        if cab_bed_note:
            note = f"{note}；{cab_bed_note}" if note else cab_bed_note
        ear_row = ear_by_key.get(key)
        level = bucket_level(score, rules["thresholds"])
        scored.append(
            {
                "品牌": key.brand, "车型": key.model,
                "尺码": _collect_sizes(rows_for_key),
                "差评评分": score,
                "定制需求等级": "" if score is None else level,
                "差评备注": note,
                "耳位(普通/靠前/靠后)": ear_row.get("耳位(普通/靠前/靠后)", "") if ear_row else "",
                "年份": _collect_years(rows_for_key),
            }
        )
    scored.sort(key=lambda row: (row["品牌"], row["车型"]))
    report = {
        "车型数": len(keys),
        "差评表结构重复数": len(dupes),
        "数据不足车型数": sum(1 for row in scored if row["定制需求等级"] == ""),
    }
    return scored, report
