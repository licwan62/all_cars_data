"""综合差评分析表、人工维护进度、车耳状态登记，给出定制需求度（通用版型偏离度）。

打分规则是初版简单规则，权重和分档阈值都放在 data/定制评分规则.json 里，
后续要调整时改配置即可，不需要改代码。

三个维度独立打分到 0~1（数值越大表示越需要定制/偏离通用版型越多），
维度打分方式：
- 差评：优先用"差评占比"字段（已经是 0~1）；缺失时退化用"严重度评级"的分档映射。
- 人工维护进度："当前状态"字段按 status_map 映射（未开始/进行中的分数更高，
  表示这条车型的定制判断还没有维护完成，需求度先按未完成对待）。
- 车耳状态："车耳状态"字段按 status_map 映射（异常/需定制分数更高）。

综合得分 = 有值的维度按配置权重加权平均（缺失维度不参与、权重按剩余维度重新归一）；
三个维度都没有记录时输出 None，定级为"数据不足"，不当作"不需要定制"处理。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import NamedTuple

KEY_COLUMNS = ("品牌", "车型", "结构")

DEFAULT_RULES = {
    "weights": {"差评": 1.0, "人工维护进度": 1.0, "车耳状态": 1.0},
    "差评": {
        "占比字段": "差评占比",
        "分档字段": "严重度评级",
        "分档映射": {"低": 0.2, "中": 0.5, "高": 0.8},
    },
    "人工维护进度": {
        "状态字段": "当前状态",
        "状态映射": {"未开始": 1.0, "进行中": 0.5, "已完成": 0.0, "无需处理": 0.0},
    },
    "车耳状态": {
        "状态字段": "车耳状态",
        "状态映射": {"异常": 1.0, "需定制": 1.0, "待验证": 0.5, "正常": 0.0},
    },
    "thresholds": {"低": 0.34, "中": 0.67},
}


class ModelKey(NamedTuple):
    brand: str
    model: str
    structure: str


def canonicalize_structure(structure: str, mapping: dict[str, str] | None = None) -> str:
    """跨区域结构归并（仅用于打分键，不改写压缩表/上游数据）。

    背景：美区原始数据从不标注车门数（一律记成 "SUV"），欧/俄区门数计入尾门，
    一台常规四门 SUV 在欧俄计为 "SUV 5dr"；因此美区未标注的 "SUV" 与欧俄的
    "SUV 5dr" 是同一种车身，打分时应算作同一个 品牌+车型+结构 键，否则同一台车
    会因为区域标注习惯不同而在评分表里出现两行。"SUV 3dr"（对应美区 2 门车型）
    不在此列，继续保留为单独结构。
    """
    return (mapping or {}).get(structure, structure)


def read_csv_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def index_by_key(rows: list[dict]) -> tuple[dict[ModelKey, dict], list[dict]]:
    """按 品牌+车型+结构 建索引；同键多行时取最后一行，其余记为冲突。"""
    indexed: dict[ModelKey, dict] = {}
    duplicates: list[dict] = []
    for row in rows:
        key = ModelKey(*(row.get(column, "").strip() for column in KEY_COLUMNS))
        if not key.brand or not key.model:
            continue
        if key in indexed:
            duplicates.append({"key": key._asdict(), "row": row})
        indexed[key] = row
    return indexed, duplicates


def _to_float(value: str) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return min(max(parsed, 0.0), 1.0)


def score_negative_review(row: dict | None, rules: dict) -> float | None:
    if row is None:
        return None
    config = rules["差评"]
    ratio = _to_float(row.get(config["占比字段"], ""))
    if ratio is not None:
        return ratio
    bucket = (row.get(config["分档字段"]) or "").strip()
    return config["分档映射"].get(bucket)


def score_manual_progress(row: dict | None, rules: dict) -> float | None:
    if row is None:
        return None
    config = rules["人工维护进度"]
    status = (row.get(config["状态字段"]) or "").strip()
    return config["状态映射"].get(status)


def score_ear_status(row: dict | None, rules: dict) -> float | None:
    if row is None:
        return None
    config = rules["车耳状态"]
    status = (row.get(config["状态字段"]) or "").strip()
    return config["状态映射"].get(status)


def combine(components: dict[str, float | None], weights: dict[str, float]) -> tuple[float | None, int]:
    available = {name: value for name, value in components.items() if value is not None}
    if not available:
        return None, 0
    weight_sum = sum(weights.get(name, 0.0) for name in available) or 1.0
    score = sum(value * weights.get(name, 0.0) for name, value in available.items()) / weight_sum
    return score, len(available)


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
    manual_progress_rows: list[dict],
    ear_status_rows: list[dict],
    rules: dict | None = None,
) -> tuple[list[dict], dict]:
    rules = rules or DEFAULT_RULES
    negative_review_by_key, nr_dupes = index_by_key(negative_review_rows)
    manual_progress_by_key, mp_dupes = index_by_key(manual_progress_rows)
    ear_status_by_key, es_dupes = index_by_key(ear_status_rows)

    scored: list[dict] = []
    for key in keys:
        components = {
            "差评": score_negative_review(negative_review_by_key.get(key), rules),
            "人工维护进度": score_manual_progress(manual_progress_by_key.get(key), rules),
            "车耳状态": score_ear_status(ear_status_by_key.get(key), rules),
        }
        score, n_components = combine(components, rules["weights"])
        scored.append(
            {
                "品牌": key.brand, "车型": key.model, "结构": key.structure,
                "差评评分": components["差评"], "人工维护进度评分": components["人工维护进度"],
                "车耳状态评分": components["车耳状态"], "综合定制需求度": score,
                "定制需求等级": bucket_level(score, rules["thresholds"]),
                "参与评分维度数": n_components,
            }
        )
    scored.sort(key=lambda row: (row["品牌"], row["车型"], row["结构"]))
    report = {
        "车型数": len(keys),
        "差评表重复键数": len(nr_dupes),
        "人工维护进度表重复键数": len(mp_dupes),
        "车耳状态登记表重复键数": len(es_dupes),
        "数据不足车型数": sum(1 for row in scored if row["定制需求等级"] == "数据不足"),
    }
    return scored, report
