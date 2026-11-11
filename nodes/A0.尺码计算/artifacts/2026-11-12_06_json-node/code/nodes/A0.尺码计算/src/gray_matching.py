"""Apply approved US pickup boundary exceptions after the ordinary size match."""
from pathlib import Path
import re

import pandas as pd
import yaml

import pandas_analysis as analysis


CONFIG = Path(__file__).resolve().parents[1] / "data/US/规则/同车型灰区.yaml"
IDENTITY = ["MAKE", "MODEL", "版本", "结构", "CAB", "BED", "分类"]
DIMENSIONS = ["L-MM", "W-MM", "H-MM"]


def apply_gray_matching(frame, parameters, rules, allowed_sizes=None, *, config=None):
    if config is None:
        config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    result = frame.copy()
    audit = []
    ids = frame["DIMENSION-ID"].map(
        lambda value: value if value.endswith(" US") else value + " US"
    )
    if ids.duplicated().any():
        raise ValueError("同车型灰区要求 DIMENSION-ID 唯一")
    index_by_id = dict(zip(ids, frame.index))

    for case in config["cases"]:
        index = index_by_id.get(case["dimension_id"])
        anchor_index = index_by_id.get(case["anchor_id"])
        if index is None or anchor_index is None:
            continue
        row, anchor = frame.loc[index], frame.loc[anchor_index]
        base, target = case["base_size"], case["target_size"]
        if row["自动尺码"] != base or anchor["自动尺码"] != target:
            continue
        if allowed_sizes is not None and target not in allowed_sizes:
            continue
        if not row[IDENTITY].equals(anchor[IDENTITY]) or row["结构"] != "Pickup":
            continue
        row_years = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", row["YEAR"])
        anchor_years = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", anchor["YEAR"])
        if not row_years or not anchor_years or int(row_years[1]) != int(anchor_years[2] or anchor_years[1]) + 1:
            continue
        current = pd.to_numeric(row[DIMENSIONS], errors="coerce")
        previous = pd.to_numeric(anchor[DIMENSIONS], errors="coerce")
        if not ((current > 0) & (previous > 0) & ((current - previous).abs() <= config["max_spread_mm"])).all():
            continue

        pair = rules.loc[rules["尺码"].isin((base, target))]
        if len(pair) != 2 or pair["尺码池"].nunique() != 1 or pair["分类"].nunique() != 1:
            continue
        if pair["尺码"].nunique() != 2 or pair["车型白名单"].fillna("").str.strip().ne("").any():
            continue
        limits = pair.set_index("尺码")["长上限"].astype(float)
        pool = rules.loc[rules["尺码池"].eq(pair.iloc[0]["尺码池"]), "长上限"].astype(float)
        if limits[target] >= limits[base] or ((pool > limits[target]) & (pool < limits[base])).any():
            continue
        overrun = float(current["L-MM"] - limits[target])
        anchor_margin = float(limits[target] - previous["L-MM"])
        if not (0 < overrun <= config["max_overrun_mm"] and 0 <= anchor_margin <= config["max_overrun_mm"]):
            continue

        matcher = analysis.SizeMatcher(parameters, pair.loc[pair["尺码"].eq(target)])
        values = [
            limits[target] if spec.source_column == "L-MM" else pd.to_numeric(row[spec.source_column], errors="coerce")
            for spec in matcher.limits
        ]
        match = matcher.match(row["分类"], row["CAB"], row["版本"], values)
        if not match.has_final_candidate or match.auto_size != target:
            continue
        reason = f"同车型灰区：{base} → {target}，车长超标称上限 {overrun:g} mm"
        result.at[index, "自动尺码"] = target
        result.at[index, "自动长度余量"] = f"{-overrun:g}" if isinstance(result["自动长度余量"].dtype, pd.StringDtype) else -overrun
        result.at[index, "原因"] = reason
        result.at[index, "规则ID"] = match.rule_id
        audit.append((case["dimension_id"], case["anchor_id"], base, target, f"{overrun:g}"))
    return result, audit
