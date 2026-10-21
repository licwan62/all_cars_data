"""US 基础尺码结果之后的可审计 SHAPE 调整；不改变基础分类与计算量。"""
from __future__ import annotations

from pathlib import Path
import math

import pandas as pd
import yaml

PROJECT = Path(__file__).resolve().parents[1]
CONFIG = PROJECT / "data/US/规则/SHAPE调整.yaml"
SOURCE = PROJECT.parent / "03.车形分类核定/output/COVER_SHAPE.csv"
MATCH_COLUMNS = ["自动尺码", "自动长度余量", "候选", "原因", "相差数值", "规则ID"]


def load_config(path=CONFIG):
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    for field in ("shapes", "structures", "categories", "statuses", "target_sizes"):
        if not isinstance(config.get(field), list) or not config[field]:
            raise ValueError(f"SHAPE调整 {field} 必须为非空列表")
    height = float(config["height_max_mm"])
    if not math.isfinite(height) or height <= 0:
        raise ValueError("SHAPE调整车高上限必须为正有限数")
    if config["preserve_whitelist"] is not True or config["on_target_unavailable"] != "keep_base":
        raise ValueError("SHAPE调整必须保留白名单，目标不可用时保留基础结果")
    if config["source_file"] != SOURCE.name:
        raise ValueError("SHAPE调整仅支持正式上游 COVER_SHAPE.csv")
    return config


def adjust(frame, parameters, rules, allowed_sizes=None, *, config=None, shapes=None):
    import pandas_analysis as analysis

    config = load_config() if config is None else config
    result = frame.copy()
    audit = []
    if not config["enabled"]:
        return result, audit
    shapes = analysis._read_csv(SOURCE) if shapes is None else shapes
    analysis._require_columns(shapes, ["DIMENSION-ID", "COUNTRY", "SHAPE", "SHAPE_STATUS"], "SHAPE调整来源")
    if shapes["DIMENSION-ID"].duplicated().any():
        raise ValueError("SHAPE调整来源 DIMENSION-ID 不唯一")
    lookup = shapes.loc[shapes["COUNTRY"].eq("US")].set_index("DIMENSION-ID")
    base_matcher = analysis.SizeMatcher(parameters, rules, allowed_sizes=allowed_sizes)
    size_column = "内部尺码" if "内部尺码" in rules else "尺码"
    missing = set(config["target_sizes"]) - set(rules[size_column].dropna())
    if missing:
        raise ValueError(f"SHAPE调整目标尺码不在基础规则中：{sorted(missing)}")
    # 在原规则中选目标行，因此规则ID、上下限、白名单和禁用规则语义保持一致。
    target_rules = rules.loc[rules[size_column].isin(config["target_sizes"])].copy()
    target = analysis.SizeMatcher(parameters, target_rules, allowed_sizes=allowed_sizes)
    for index, row in frame.iterrows():
        rid = str(row["DIMENSION-ID"])
        if rid.endswith((" EU", " RU")):
            continue
        rid = rid if rid.endswith(" US") else rid + " US"
        if rid not in lookup.index:
            raise ValueError(f"SHAPE调整缺少精确US来源：{rid}")
        shape = lookup.loc[rid]
        if row["分类"] not in config["categories"] or row["结构"] not in config["structures"] or shape["SHAPE"] not in config["shapes"]:
            continue
        height = pd.to_numeric(row.get("H-MM"), errors="coerce")
        if pd.isna(height) or height <= 0 or height > config["height_max_mm"]:
            continue
        entry = {"DIMENSION-ID": rid, "结构": row["结构"], "分类": row["分类"],
                 "SHAPE": shape["SHAPE"], "SHAPE_STATUS": shape["SHAPE_STATUS"], "H-MM": height,
                 "基础尺码": row["自动尺码"], "调整尺码": row["自动尺码"], "处理": ""}
        values = [pd.to_numeric(row[spec.source_column], errors="coerce") for spec in base_matcher.limits]
        whitelisted, _ = base_matcher._whitelist_result(row, values)
        if whitelisted:
            entry["处理"] = "保留车型白名单"
        elif shape["SHAPE_STATUS"] not in config["statuses"]:
            entry["处理"] = "证据状态不足，保留基础结果"
        else:
            candidate = target.match("三厢车", row["CAB"], row["版本"], values)
            if not candidate.has_final_candidate:
                entry["处理"] = "目标3X不满足约束或货架，保留基础结果"
            else:
                entry["调整尺码"] = candidate.auto_size
                entry["处理"] = "已调整" if candidate.auto_size != row["自动尺码"] else "目标与基础一致"
                values_out = [candidate.auto_size, candidate.length_margin, candidate.candidate,
                              candidate.reason, candidate.difference, candidate.rule_id or ""]
                for column, value in zip(MATCH_COLUMNS, values_out):
                    if isinstance(result[column].dtype, pd.StringDtype) and isinstance(value, (int, float)):
                        value = f"{value:g}"
                    result.at[index, column] = value
        audit.append(entry)
    return result, audit
