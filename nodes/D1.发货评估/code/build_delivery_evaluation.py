"""覆盖 A0 US 全量表的发货评估：灰度聚合、市场潜力排序与 B0 差评标记。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / "lib"))
from artifact_batch import RunBatch, sha256  # noqa: E402


CONFIG = PROJECT / "data" / "发货评估.json"
FULL_TABLE = REPO / "nodes" / "A0.尺码计算" / "output" / "US" / "全量" / "全量表.csv"
SIZE_RULES = REPO / "nodes" / "A0.尺码计算" / "output" / "US" / "尺码规则.json"
REVIEWS = REPO / "nodes" / "B0.差评分析" / "output" / "差评分析表.csv"
CUSTOM_MODELS = PROJECT / "data" / "定制预定车型.csv"

OUTPUTS = {
    "detail": "全量车型发货评估明细.csv",
    "identity": "发货评估身份映射.csv",
    "w": "W型车发货评估.csv",
    "pickup": "皮卡发货评估.csv",
    "regular": "普通车发货评估.csv",
    "gray": "灰度匹配审核.csv",
}

CATEGORY_FILES = {
    "W型车": OUTPUTS["w"],
    "皮卡": OUTPUTS["pickup"],
    "普通车": OUTPUTS["regular"],
}

EVALUATION_COLUMNS = [
    "MAKE", "MODEL", "版本", "CAB", "BED", "YEAR", "结构", "评估类别", "定制标记", "代际",
    "供货尺码",
    "最小长-MM", "最大长-MM", "最小宽-MM", "最大宽-MM", "最小高-MM", "最大高-MM",
    "年份留存系数", "调整后市场潜力值", "市场潜力值", "市场调整增加值", "积加月销量估计", "全局市场潜力排名", "尺寸组销量合计", "类别市场潜力排名",
    "原始自动尺码", "灰度调整记录数", "灰度组ID", "差评标记", "差评数", "差评匹配方式",
    "差评年份", "差评尺码", "差评严重度", "差评原因", "差评备注",
    "差评模糊原因", "差评推理原因", "差评推理键", "差评推理来源",
]

IDENTITY_COLUMNS = [
    "DIMENSION-ID", "MAKE", "MODEL", "YEAR", "供货尺码", "评估类别", "灰度组ID", "灰度调整",
]

GRAY_COLUMNS = [
    "灰度组ID", "评估类别", "MAKE", "MODEL", "版本", "结构", "CAB", "BED",
    "源DIMENSION-ID", "源年份", "源尺码", "目标尺码", "判定", "原因",
    "长度跨度mm", "宽度跨度mm", "高度跨度mm", "目标最小长度余量mm",
]


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, keep_default_na=False, **kwargs)


def year_bounds(value: object) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", str(value).strip())
    if not match:
        raise ValueError(f"无法解析年份: {value!r}")
    start, end = int(match[1]), int(match[2] or match[1])
    if end < start:
        raise ValueError(f"年份倒序: {value!r}")
    return start, end


def interval_retention(value: object, policy: dict) -> float:
    start, end = year_bounds(value)
    evaluation_year = int(policy["evaluation_year"])
    full_weight_years = int(policy["full_weight_years"])
    half_life_years = float(policy["half_life_years"])
    if half_life_years <= 0 or full_weight_years < 0:
        raise ValueError("市场潜力参数不合法")
    years = np.arange(start, end + 1)
    ages = np.maximum(0, evaluation_year - years)
    weights = np.where(
        ages <= full_weight_years,
        1.0,
        2 ** (-(ages - full_weight_years) / half_life_years),
    )
    return float(weights.mean())


def classify_rows(frame: pd.DataFrame, config: dict) -> pd.Series:
    prefix = config["classification"]["w_size_prefix"]
    pickup = config["classification"]["pickup_category"]
    result = pd.Series("普通车", index=frame.index, dtype="object")
    result.loc[frame["分类"].eq(pickup)] = "皮卡"
    result.loc[frame["自动尺码"].astype(str).str.startswith(prefix)] = "W型车"
    return result


def size_catalog(payload: dict) -> pd.DataFrame:
    records = []
    for rule in payload["rules"]:
        if not str(rule.get("长上限", "")).strip():
            continue
        records.append({"自动尺码": rule["尺码"], "尺码池": rule["尺码池"], "长上限": float(rule["长上限"])})
    catalog = pd.DataFrame(records).drop_duplicates()
    ambiguous = catalog.groupby("自动尺码")[["尺码池", "长上限"]].nunique()
    if len(ambiguous) and (ambiguous > 1).any(axis=None):
        raise ValueError("尺码规则中同名尺码存在不同尺码池或长度上限")
    catalog = catalog.drop_duplicates("自动尺码").sort_values(["尺码池", "长上限", "自动尺码"])
    catalog["尺码序"] = catalog.groupby("尺码池").cumcount()
    return catalog


def prepare(full_table: pd.DataFrame, config: dict, rules: dict) -> pd.DataFrame:
    required = {
        "DIMENSION-ID", "MAKE", "MODEL", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类",
        "L-MM", "W-MM", "H-MM", "尺寸组销量", "自动尺码", "SHAPE",
    }
    missing = required - set(full_table.columns)
    if missing:
        raise ValueError(f"全量表缺字段: {sorted(missing)}")
    frame = full_table.copy()
    if frame["DIMENSION-ID"].eq("").any() or frame["DIMENSION-ID"].duplicated().any():
        raise ValueError("全量表 DIMENSION-ID 必须非空且唯一")
    numeric = ["L-MM", "W-MM", "H-MM", "尺寸组销量"]
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="raise")
    bounds = frame["YEAR"].map(year_bounds)
    frame["起始年"] = bounds.map(lambda item: item[0])
    frame["结束年"] = bounds.map(lambda item: item[1])
    frame["评估类别"] = classify_rows(frame, config)
    frame["年份留存系数"] = frame["YEAR"].map(lambda value: interval_retention(value, config["market_potential"]))
    frame["市场潜力值"] = frame["尺寸组销量"] * frame["年份留存系数"] / float(config["market_potential"].get("divisor", 1000))
    frame = frame.merge(size_catalog(rules), on="自动尺码", how="left", validate="many_to_one")
    return frame


def _year_components(frame: pd.DataFrame, gap: int) -> list[list[int]]:
    components: list[list[int]] = []
    current: list[int] = []
    current_end = -1
    for idx, row in frame.sort_values(["起始年", "结束年", "DIMENSION-ID"], kind="stable").iterrows():
        if not current or int(row["起始年"]) <= current_end + gap:
            current.append(idx)
            current_end = max(current_end, int(row["结束年"]))
        else:
            components.append(current)
            current = [idx]
            current_end = int(row["结束年"])
    if current:
        components.append(current)
    return components


def apply_gray_matching(frame: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    result = frame.copy()
    result["供货尺码"] = result["自动尺码"]
    result["灰度组ID"] = ""
    result["灰度调整"] = False
    policy = config["gray_match"]
    audits: list[dict] = []
    if not policy.get("enabled", False):
        return result, pd.DataFrame(columns=GRAY_COLUMNS)
    known = result[result["尺码池"].ne("") & result["尺码池"].notna()].copy()
    for identity, group in known.groupby(policy["identity_keys"], sort=True, dropna=False):
        for indices in _year_components(group, int(policy["max_year_gap"])):
            part = result.loc[indices]
            if part["自动尺码"].nunique() < 2:
                continue
            gid_text = "|".join(map(str, identity)) + f"|{part['起始年'].min()}|{part['结束年'].max()}"
            gid = "GRAY-" + hashlib.sha256(gid_text.encode("utf-8")).hexdigest()[:10].upper()
            spreads = {
                "length": float(part["L-MM"].max() - part["L-MM"].min()),
                "width": float(part["W-MM"].max() - part["W-MM"].min()),
                "height": float(part["H-MM"].max() - part["H-MM"].min()),
            }
            status, reason, target_size, target_margin = "拒绝", "", "", np.nan
            orders = sorted(part["尺码序"].astype(int).unique())
            if part["尺码池"].nunique() != 1:
                reason = "跨尺码池"
            elif policy["adjacent_sizes_only"] and max(orders) - min(orders) + 1 != len(orders):
                reason = "跨非相邻尺码"
            elif any(spreads[key] > float(policy["max_group_spread_mm"][key]) for key in spreads):
                reason = "整组长宽高跨度超阈值"
            else:
                target = part.sort_values(["长上限", "自动尺码"], kind="stable").iloc[-1]
                target_size = str(target["自动尺码"])
                smaller = part[part["尺码序"].lt(target["尺码序"])]
                smaller_limits = smaller.groupby("自动尺码", as_index=False)["长上限"].first()
                boundary_ok = all(
                    (smaller.loc[smaller["自动尺码"].eq(row["自动尺码"]), "L-MM"] - row["长上限"]).abs().le(
                        float(policy["boundary_band_mm"])
                    ).all()
                    for _, row in smaller_limits.iterrows()
                )
                target_margin = float(target["长上限"] - part["L-MM"].max())
                limits = policy["target_length_margin_mm"]
                if not boundary_ok:
                    reason = "较小档记录不在尺码边界灰区内"
                elif not (float(limits["min"]) <= target_margin < float(limits["max_exclusive"])):
                    reason = f"目标长度余量{target_margin:g}mm不合格"
                else:
                    status, reason = "通过", "同车型相邻年代尺寸接近，统一较大尺码"
                    result.loc[indices, "供货尺码"] = target_size
                    result.loc[indices, "灰度组ID"] = gid
                    result.loc[indices, "灰度调整"] = result.loc[indices, "自动尺码"].ne(target_size)
            audits.append({
                "灰度组ID": gid, **dict(zip(policy["identity_keys"], identity)),
                "源DIMENSION-ID": "；".join(part["DIMENSION-ID"].astype(str)),
                "源年份": "；".join(sorted(part["YEAR"].astype(str).unique())),
                "源尺码": "；".join(sorted(part["自动尺码"].astype(str).unique())),
                "目标尺码": target_size, "判定": status, "原因": reason,
                "长度跨度mm": spreads["length"], "宽度跨度mm": spreads["width"],
                "高度跨度mm": spreads["height"], "目标最小长度余量mm": target_margin,
            })
    audit = pd.DataFrame(audits, columns=GRAY_COLUMNS)
    return result, audit


def _join_unique(values, sep: str = "；") -> str:
    return sep.join(sorted({str(value).strip() for value in values if str(value).strip()}))


def add_custom_flag(evaluations: pd.DataFrame, custom_models: pd.DataFrame) -> pd.DataFrame:
    """按维护清单的 MAKE+MODEL 标记定制 SKU；清单尾部可带门数、代际等细分说明。"""
    if "车型" not in custom_models.columns:
        raise ValueError("定制预定车型清单缺少字段: 车型")
    entries = {
        " ".join(str(value).strip().casefold().split())
        for value in custom_models["车型"]
        if str(value).strip()
    }
    if not entries:
        raise ValueError("定制预定车型清单为空")

    result = evaluations.copy()
    model_keys = result.apply(
        lambda row: " ".join(f"{row['MAKE']} {row['MODEL']}".strip().casefold().split()), axis=1
    )
    known_keys = set(model_keys)
    selected_keys: set[str] = set()
    for entry in entries:
        candidates = [key for key in known_keys if entry == key or entry.startswith(key + " ")]
        if not candidates:
            continue
        longest = max(len(key) for key in candidates)
        winners = [key for key in candidates if len(key) == longest]
        if len(winners) != 1:
            raise ValueError(f"定制车型匹配不唯一: {entry} -> {sorted(winners)}")
        selected_keys.add(winners[0])
    result["定制标记"] = model_keys.map(lambda key: "是" if key in selected_keys else "否")
    return result


def format_business_output(frame: pd.DataFrame, policy: dict, category: str | None = None) -> pd.DataFrame:
    """合并内部差评追踪字段，并按业务表类型精简列。"""
    result = frame.copy()
    merge_fields = policy["merge_review_fields_into_notes"]
    missing = set(merge_fields) - set(result.columns)
    if missing:
        raise ValueError(f"业务输出缺少待合并的差评字段: {sorted(missing)}")
    if "差评备注" not in result.columns:
        raise ValueError("业务输出缺少差评备注")

    def merged_note(row: pd.Series) -> str:
        parts = []
        for item in re.split(r"；+", str(row["差评备注"]).strip()):
            item = item.strip()
            if not item:
                continue
            if item.startswith("车型已匹配全量表 MAKE="):
                continue
            if item.startswith("已从'") and "归并（语义明确可识别品牌/车型）" in item:
                continue
            if item.startswith("语义明确可识别品牌/车型，从'未识别'归并新建："):
                continue
            if item not in parts:
                parts.append(item)

        reason_labels = {
            "差评记录缺少年代": "缺年份",
            "年代未命中": "年份不符",
            "差评记录缺少尺码": "缺尺码",
            "尺码未命中": "尺码不符",
            "结构未命中": "结构不符",
            "仅按品牌+车型关联": "仅车型",
        }
        fuzzy = [
            reason_labels.get(item, item)
            for item in str(row["差评模糊原因"]).split("；")
            if item.strip()
        ]
        if fuzzy:
            parts.append("匹配：" + "/".join(dict.fromkeys(fuzzy)))
        if str(row["差评推理原因"]).strip():
            parts.append("推理：同车型同尺寸")
        if str(row["差评推理来源"]).strip():
            parts.append("源：" + str(row["差评推理来源"]).strip())
        return "；".join(parts)

    result["差评备注"] = result.apply(merged_note, axis=1)
    drop_columns = list(merge_fields) + list(policy["drop_from_business_outputs"])
    if category in {"W型车", "普通车"}:
        drop_columns.extend(policy["drop_from_nonpickup_category_outputs"])
    return result.drop(columns=[column for column in drop_columns if column in result.columns])


def build_identity_mapping(detail: pd.DataFrame, evaluations: pd.DataFrame) -> pd.DataFrame:
    """把业务表移除的上游身份独立保存，供追踪和身份承接校验。"""
    sku_keys = evaluations[["SKU", "MAKE", "MODEL", "YEAR", "供货尺码"]]
    mapping = detail[["DIMENSION-ID", "SKU", "评估类别", "灰度组ID", "灰度调整"]].merge(
        sku_keys, on="SKU", how="left", validate="many_to_one"
    )[IDENTITY_COLUMNS]
    if mapping["DIMENSION-ID"].eq("").any() or mapping["DIMENSION-ID"].duplicated().any():
        raise ValueError("发货评估身份映射的 DIMENSION-ID 必须非空且唯一")
    return mapping.sort_values("DIMENSION-ID", kind="stable")


def classify_review_flags(frame: pd.DataFrame, policy: dict) -> pd.DataFrame:
    """把内部是否命中标记转换为尺寸、质量、无三类业务标记。"""
    result = frame.copy()
    keywords = tuple(str(value).casefold() for value in policy["dimension_keywords"])

    def label(row: pd.Series) -> str:
        reason = str(row["差评原因"]).strip()
        count = pd.to_numeric(pd.Series([row["差评数"]]), errors="coerce").fillna(0).iloc[0]
        reason_items = [re.sub(r"\(\d+\)$", "", item).strip() for item in reason.split("；") if item.strip()]
        effective_items = [item for item in reason_items if item not in set(policy["empty_reason_tokens"])]
        if count <= 0 or not effective_items:
            return policy["none_label"]
        normalized = "；".join(effective_items).casefold()
        if any(keyword in normalized for keyword in keywords):
            return policy["dimension_label"]
        return policy["quality_label"]

    result["差评标记"] = result.apply(label, axis=1)
    return result


def _sku_id(keys: tuple, start: int, end: int) -> str:
    text = "|".join(map(str, (*keys, start, end)))
    return "SKU-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:12].upper()


def build_evaluations(frame: pd.DataFrame, policy: dict | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    policy = policy or {"group_keys": ["MAKE", "MODEL", "供货尺码"], "max_year_gap": 1}
    keys = list(policy["group_keys"])
    records: list[dict] = []
    detail_ids: dict[str, str] = {}
    for identity, group in frame.groupby(keys, sort=True, dropna=False):
        for indices in _year_components(group, int(policy["max_year_gap"])):
            part = frame.loc[indices]
            start, end = int(part["起始年"].min()), int(part["结束年"].max())
            sku = _sku_id(identity, start, end)
            for dimension_id in part["DIMENSION-ID"]:
                detail_ids[str(dimension_id)] = sku
            sales = float(part["尺寸组销量"].sum())
            potential = float(part["市场潜力值"].sum())
            categories = sorted(set(part["评估类别"]))
            if len(categories) != 1:
                raise ValueError(f"同一 SKU 跨评估类别: {identity}")
            records.append({
                "SKU": sku,
                **dict(zip(keys, identity)),
                "评估类别": categories[0],
                "版本": _join_unique(part["版本"]), "结构": _join_unique(part["结构"]),
                "CAB": _join_unique(part["CAB"]), "BED": _join_unique(part["BED"]),
                "代际": _join_unique(part["代际"]), "SHAPE": _join_unique(part["SHAPE"]),
                "YEAR": str(start) if start == end else f"{start}-{end}",
                "原始自动尺码": _join_unique(part["自动尺码"]),
                "最小长-MM": float(part["L-MM"].min()), "最大长-MM": float(part["L-MM"].max()),
                "最小宽-MM": float(part["W-MM"].min()), "最大宽-MM": float(part["W-MM"].max()),
                "最小高-MM": float(part["H-MM"].min()), "最大高-MM": float(part["H-MM"].max()),
                "尺寸组销量合计": sales,
                "年份留存系数": float((part["尺寸组销量"] * part["年份留存系数"]).sum()) / sales if sales else float(part["年份留存系数"].mean()),
                "市场潜力值": potential,
                "灰度调整记录数": int(part["灰度调整"].sum()),
                "灰度组ID": _join_unique(part["灰度组ID"]),
            })
    evaluations = pd.DataFrame(records)
    evaluations["类别市场潜力排名"] = evaluations.groupby("评估类别")["市场潜力值"].rank(
        method="first", ascending=False
    ).astype(int)
    evaluations["全局市场潜力排名"] = evaluations["市场潜力值"].rank(method="first", ascending=False).astype(int)
    detail = frame.copy()
    detail["SKU"] = detail["DIMENSION-ID"].map(detail_ids)
    return evaluations, detail


def adjust_market(evaluations: pd.DataFrame, sales: pd.DataFrame, policy: dict):
    """唯一车型匹配；每个 ASIN 的销量只分摊一次，未核实配置不冒认精确 SKU。"""
    result = evaluations.copy()
    columns = ["7天销量", "15天销量", "30天销量"]
    values = sales[columns].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(values.to_numpy()).all() or (values < 0).any(axis=None):
        raise ValueError("积加销量必须为有限非负数")
    if sales["ASIN"].duplicated().any():
        raise ValueError("积加 ASIN 重复，需先核对，禁止重复累计")
    if ((values["7天销量"] > values["15天销量"]) | (values["15天销量"] > values["30天销量"])).any():
        raise ValueError("积加累计窗口销量倒序")
    norm = lambda text: re.sub(r"[^a-z0-9]", "", str(text).casefold())
    models = result[["MAKE", "MODEL"]].drop_duplicates().values.tolist()
    result["积加月销量估计"] = 0.0
    targets = pd.Series(0.0, index=result.index)
    audit = []
    w = policy["monthly_weights"]
    for index, sale in sales.iterrows():
        name = re.sub(r"\(?\b(?:19|20)\d{2}\s*[-–]\s*\d{2,4}\)?", "", str(sale["车型"]))
        text = norm(name)
        candidates = [(make, model) for make, model in models if norm(model) and norm(model) in text
                      and (len(norm(model)) > 3 or re.search(
                          r"(?<![a-z0-9])" + r"[\s-]*".join(map(re.escape, norm(model))) + r"(?![a-z0-9])",
                          name.casefold()))]
        if candidates:
            longest = max(len(norm(model)) for _, model in candidates)
            candidates = [(make, model) for make, model in candidates if len(norm(model)) == longest]
            branded = [(make, model) for make, model in candidates if norm(make) in text]
            candidates = branded or candidates
        # 通用/跨车型产品不依据 MSKU 猜测适配。
        ambiguous = any(token in str(sale["车型"]) for token in [",", " and ", "未匹配", "/"])
        status = "车型匹配，按潜力分摊" if len(candidates) == 1 and not ambiguous else "待审核"
        monthly = sum(float(values.loc[index, col]) * factor * weight
                      for col, factor, weight in zip(columns, [30/7, 2, 1], w))
        target = monthly * float(values.loc[index, "30天销量"]) / (float(values.loc[index, "30天销量"]) + policy["confidence_units"]) * policy["score_per_monthly_unit"]
        if status != "待审核":
            make, model = candidates[0]
            mask = result["MAKE"].eq(make) & result["MODEL"].eq(model)
            weights = result.loc[mask, "市场潜力值"].clip(lower=0)
            weights = weights / weights.sum() if weights.sum() else pd.Series(1 / mask.sum(), index=weights.index)
            result.loc[mask, "积加月销量估计"] += monthly * weights
            targets.loc[mask] += target * weights
        audit.append({**sale.to_dict(), "匹配状态": status, "匹配车型": str(candidates), "月销量估计": monthly, "销量目标分": target})
    result["市场调整增加值"] = (targets - result["市场潜力值"]).clip(lower=0)
    result["调整后市场潜力值"] = result["市场潜力值"] + result["市场调整增加值"]
    return result, pd.DataFrame(audit)


def _split_tokens(value: object) -> set[str]:
    return {token.strip().casefold() for token in re.split(r"[；;,/]+", str(value)) if token.strip()}


def _review_years(value: object) -> set[int]:
    years: set[int] = set()
    for token in re.split(r"[；,，/]+", str(value)):
        token = token.strip()
        if not token:
            continue
        match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", token)
        if match:
            start, end = int(match[1]), int(match[2] or match[1])
            years.update(range(start, end + 1))
    return years


def _structure_matches(review_structure: str, evaluation_structure: str) -> bool:
    source = review_structure.strip().casefold()
    if not source or source == "未知":
        return True
    source_tokens = _split_tokens(source)
    target_tokens = _split_tokens(evaluation_structure)
    return any(
        source_token == target_token or source_token.split()[0] == target_token.split()[0]
        for source_token in source_tokens
        for target_token in target_tokens
    )


def _severity(values) -> str:
    order = {"": 0, "低": 1, "中": 2, "高": 3}
    cleaned = {str(value).strip() for value in values}
    return max(cleaned, key=lambda value: order.get(value, 0), default="")


def match_reviews(evaluations: pd.DataFrame, reviews: pd.DataFrame) -> pd.DataFrame:
    required = {"品牌", "车型", "结构", "尺码", "差评数量", "主要差评原因", "严重度评级", "备注", "年份"}
    missing = required - set(reviews.columns)
    if missing:
        raise ValueError(f"差评分析表缺字段: {sorted(missing)}")
    by_model = {
        key: group.copy()
        for key, group in reviews.groupby(
            [reviews["品牌"].str.strip().str.casefold(), reviews["车型"].str.strip().str.casefold()], sort=False
        )
    }
    result = evaluations.copy()
    review_columns = {column: [] for column in [
        "差评标记", "差评匹配方式", "差评数", "差评严重度", "差评原因", "差评备注",
        "差评年份", "差评尺码", "差评模糊原因", "差评推理原因", "差评推理键", "差评推理来源",
    ]}
    for row in result.itertuples(index=False):
        candidates = by_model.get((str(row.MAKE).casefold(), str(row.MODEL).casefold()))
        if candidates is None or candidates.empty:
            values = ["否", "未匹配", 0, "", "", "", "", "", "", "", "", ""]
        else:
            start, end = year_bounds(row.YEAR)
            evaluation_years = set(range(start, end + 1))
            evaluation_sizes = _split_tokens(row.原始自动尺码) | _split_tokens(row.供货尺码)
            assessments = []
            for idx, review in candidates.iterrows():
                years = _review_years(review["年份"])
                sizes = _split_tokens(review["尺码"])
                structure_ok = _structure_matches(str(review["结构"]), str(row.结构))
                assessments.append((
                    idx, structure_ok, bool(years), bool(sizes), bool(years & evaluation_years), bool(sizes & evaluation_sizes)
                ))
            exact_ids = [idx for idx, structure_ok, has_year, has_size, year_ok, size_ok in assessments
                         if structure_ok and has_year and has_size and year_ok and size_ok]
            if exact_ids:
                selected = candidates.loc[exact_ids]
                method, fuzzy_reason = "精确匹配", ""
            else:
                structure_ids = [idx for idx, structure_ok, *_ in assessments if structure_ok]
                selected = candidates.loc[structure_ids] if structure_ids else candidates
                reasons = []
                if not any(item[2] for item in assessments):
                    reasons.append("差评记录缺少年代")
                elif not any(item[4] for item in assessments):
                    reasons.append("年代未命中")
                if not any(item[3] for item in assessments):
                    reasons.append("差评记录缺少尺码")
                elif not any(item[5] for item in assessments):
                    reasons.append("尺码未命中")
                if not any(item[1] for item in assessments):
                    reasons.append("结构未命中")
                reasons.append("仅按品牌+车型关联")
                method, fuzzy_reason = "模糊匹配", "；".join(dict.fromkeys(reasons))
            count = int(pd.to_numeric(selected["差评数量"], errors="coerce").fillna(0).sum())
            values = [
                "是", method, count, _severity(selected["严重度评级"]),
                _join_unique(selected["主要差评原因"]), _join_unique(selected["备注"]),
                _join_unique(selected["年份"]), _join_unique(selected["尺码"]), fuzzy_reason, "", "", "",
            ]
        for column, value in zip(review_columns, values):
            review_columns[column].append(value)
    for column, values in review_columns.items():
        result[column] = values
    return result


INFERRED_REVIEW_VALUE_COLUMNS = [
    "差评数", "差评严重度", "差评原因", "差评备注", "差评年份", "差评尺码",
]


def _normalized_review_inference_key(row: pd.Series, key_fields: list[str]) -> tuple:
    values: list[object] = []
    for field in key_fields:
        value = row[field]
        if field == "MODEL":
            values.append(str(value).strip().casefold())
        elif field in {"L-MM", "W-MM", "H-MM"}:
            values.append(float(value))
        else:
            values.append(str(value).strip().casefold())
    return tuple(values)


def _display_inference_key(key: tuple) -> str:
    def display(value: object) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    return "|".join(display(value) for value in key)


def _summarize_inferred_reviews(frame: pd.DataFrame) -> dict[str, object]:
    unique = frame[INFERRED_REVIEW_VALUE_COLUMNS].drop_duplicates()
    return {
        "差评数": int(pd.to_numeric(unique["差评数"], errors="coerce").fillna(0).sum()),
        "差评严重度": _severity(unique["差评严重度"]),
        "差评原因": _join_unique(unique["差评原因"]),
        "差评备注": _join_unique(unique["差评备注"]),
        "差评年份": _join_unique(unique["差评年份"]),
        "差评尺码": _join_unique(unique["差评尺码"]),
    }


def propagate_review_inference(
    detail: pd.DataFrame, evaluations: pd.DataFrame, policy: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    """按全量表原始 MODEL+长宽高，把精确命中的差评传播到同尺寸的非精确记录。"""
    detail_result = detail.copy()
    evaluation_result = evaluations.copy()
    trace_columns = ["差评推理原因", "差评推理键", "差评推理来源"]
    for frame in (detail_result, evaluation_result):
        for column in trace_columns:
            if column not in frame:
                frame[column] = ""
    if not policy.get("enabled", False):
        return detail_result, evaluation_result, {
            "detail_rows": 0, "evaluation_rows": 0, "keys": 0,
        }

    key_fields = list(policy["key_fields"])
    required = set(key_fields) | {"SKU", "差评标记", "差评匹配方式", *INFERRED_REVIEW_VALUE_COLUMNS}
    missing = required - set(detail_result.columns)
    if missing:
        raise ValueError(f"差评推理缺字段: {sorted(missing)}")
    seed_methods = set(policy["seed_match_methods"])
    protected_methods = set(policy["protected_match_methods"])
    target_method = str(policy["target_match_method"])
    normalized_keys = detail_result.apply(
        lambda row: _normalized_review_inference_key(row, key_fields), axis=1
    )
    seed_mask = detail_result["差评标记"].eq("是") & detail_result["差评匹配方式"].isin(seed_methods)
    inferred_indices: set[int] = set()
    used_keys: set[tuple] = set()
    inference_reason = "与精确匹配记录共享 MODEL+L-MM+W-MM+H-MM"

    for key in sorted(set(normalized_keys.loc[seed_mask])):
        source_mask = seed_mask & normalized_keys.map(lambda value: value == key)
        target_mask = (
            normalized_keys.map(lambda value: value == key)
            & ~detail_result["差评匹配方式"].isin(protected_methods)
        )
        if not target_mask.any():
            continue
        source = detail_result.loc[source_mask]
        summary = _summarize_inferred_reviews(source)
        source_ids = _join_unique(source["SKU"])
        target_indices = detail_result.index[target_mask]
        detail_result.loc[target_indices, "差评标记"] = "是"
        detail_result.loc[target_indices, "差评匹配方式"] = target_method
        for column, value in summary.items():
            detail_result.loc[target_indices, column] = value
        detail_result.loc[target_indices, "差评推理原因"] = inference_reason
        detail_result.loc[target_indices, "差评推理键"] = _display_inference_key(key)
        detail_result.loc[target_indices, "差评推理来源"] = source_ids
        inferred_indices.update(int(index) for index in target_indices)
        used_keys.add(key)

    inferred_detail = detail_result.loc[sorted(inferred_indices)] if inferred_indices else detail_result.iloc[0:0]
    for sku, group in inferred_detail.groupby("SKU", sort=True):
        target = evaluation_result["SKU"].eq(sku)
        if not target.any() or evaluation_result.loc[target, "差评匹配方式"].isin(protected_methods).any():
            continue
        summary = _summarize_inferred_reviews(group)
        evaluation_result.loc[target, "差评标记"] = "是"
        evaluation_result.loc[target, "差评匹配方式"] = target_method
        for column, value in summary.items():
            evaluation_result.loc[target, column] = value
        evaluation_result.loc[target, "差评推理原因"] = _join_unique(group["差评推理原因"])
        evaluation_result.loc[target, "差评推理键"] = _join_unique(group["差评推理键"])
        evaluation_result.loc[target, "差评推理来源"] = _join_unique(group["差评推理来源"])

    return detail_result, evaluation_result, {
        "detail_rows": len(inferred_detail),
        "evaluation_rows": int(evaluation_result["差评匹配方式"].eq(target_method).sum()),
        "keys": len(used_keys),
    }


def validate(
    full_table: pd.DataFrame,
    detail: pd.DataFrame,
    evaluations: pd.DataFrame,
    category_tables: dict[str, pd.DataFrame],
    sku_policy: dict,
) -> None:
    if len(detail) != len(full_table):
        raise ValueError("评估明细未逐行覆盖全量表")
    if set(detail["DIMENSION-ID"]) != set(full_table["DIMENSION-ID"]):
        raise ValueError("评估明细 DIMENSION-ID 与全量表不一致")
    source_models = set(zip(full_table["MAKE"], full_table["MODEL"]))
    result_models = set(zip(evaluations["MAKE"], evaluations["MODEL"]))
    if result_models != source_models:
        raise ValueError("发货评估未覆盖全量表全部车型")
    if set(category_tables) != {"W型车", "皮卡", "普通车"}:
        raise ValueError("评估类别不完整")
    if sum(len(table) for table in category_tables.values()) != len(evaluations):
        raise ValueError("分类评估记录未守恒")
    forbidden = {column for column in evaluations.columns if "发货件" in column or "发货量" in column}
    if forbidden:
        raise ValueError(f"评估结果不应计算发货量: {sorted(forbidden)}")
    if evaluations["SKU"].eq("").any() or evaluations["SKU"].duplicated().any():
        raise ValueError("SKU 必须非空且唯一")
    natural_key = list(sku_policy["natural_key"])
    if evaluations.duplicated(natural_key).any():
        raise ValueError(f"SKU 组合键重复: {natural_key}")
    if detail["SKU"].eq("").any():
        raise ValueError("存在未归属 SKU 的 DIMENSION-ID")
    if not set(evaluations["差评标记"]).issubset({"尺寸", "质量", "无"}):
        raise ValueError("差评标记只能是尺寸、质量、无")


def run(config_path: Path = CONFIG):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    with RunBatch.create(PROJECT / "artifacts", "delivery-evaluation", data_dir=PROJECT / "data") as batch:
        full_path = batch.input(FULL_TABLE)
        rules_path = batch.input(SIZE_RULES)
        reviews_path = batch.input(REVIEWS)
        full_table = read_csv(full_path, dtype={"DIMENSION-ID": str})
        prepared = prepare(full_table, config, json.loads(rules_path.read_text(encoding="utf-8")))
        prepared, gray_audit = apply_gray_matching(prepared, config)
        evaluations, detail = build_evaluations(prepared, config["sku"])
        sales_path = batch.input(PROJECT / "data" / config["sales_adjustment"]["source_file"])
        evaluations, sales_audit = adjust_market(evaluations, read_csv(sales_path), config["sales_adjustment"])
        sales_audit.to_csv(batch.extra("积加销量匹配依据.csv"), index=False, encoding="utf-8-sig")
        evaluations = add_custom_flag(evaluations, read_csv(CUSTOM_MODELS))
        evaluations = match_reviews(evaluations, read_csv(reviews_path))
        review_fields = [column for column in evaluations.columns if column.startswith("差评")]
        detail = detail.merge(evaluations[["SKU", "类别市场潜力排名", "全局市场潜力排名", *review_fields]],
                              on="SKU", how="left", validate="many_to_one")
        detail, evaluations, inference_status = propagate_review_inference(
            detail, evaluations, config.get("review_inference", {"enabled": False})
        )
        detail = classify_review_flags(detail, config["review_flag"])
        evaluations = classify_review_flags(evaluations, config["review_flag"])
        category_tables = {}
        for category in CATEGORY_FILES:
            table = evaluations[evaluations["评估类别"].eq(category)].copy()
            table = table.sort_values(["类别市场潜力排名", "MAKE", "MODEL", "YEAR"], kind="stable")
            category_tables[category] = table[EVALUATION_COLUMNS]
        validate(full_table, detail, evaluations, category_tables, config["sku"])
        identity_mapping = build_identity_mapping(detail, evaluations)

        output_policy = config["output_schema"]
        detail_output = evaluations[EVALUATION_COLUMNS].sort_values(
            ["评估类别", "类别市场潜力排名", "MAKE", "MODEL", "YEAR"], kind="stable"
        )
        nonpickup_mask = detail_output["评估类别"].ne("皮卡")
        detail_output.loc[nonpickup_mask, output_policy["blank_in_nonpickup_detail"]] = ""
        format_business_output(detail_output, output_policy, category="混合").to_csv(
            batch.output(OUTPUTS["detail"]), index=False, encoding="utf-8-sig"
        )
        identity_mapping.to_csv(batch.output(OUTPUTS["identity"]), index=False, encoding="utf-8-sig")
        for category, table in category_tables.items():
            format_business_output(table, output_policy, category=category).to_csv(
                batch.output(CATEGORY_FILES[category]), index=False, encoding="utf-8-sig"
            )
        gray_output = gray_audit.sort_values(
            ["判定", "评估类别", "MAKE", "MODEL", "源年份"], kind="stable"
        ).drop(columns=output_policy["drop_from_gray_audit"])
        gray_output.loc[gray_output["评估类别"].ne("皮卡"), output_policy["blank_in_nonpickup_detail"]] = ""
        gray_output.to_csv(
            batch.output(OUTPUTS["gray"]), index=False, encoding="utf-8-sig"
        )
        status = {
            "source_rows": len(full_table),
            "source_models": len(set(zip(full_table["MAKE"], full_table["MODEL"]))),
            "evaluation_rows": len(evaluations),
            "category_rows": {name: len(table) for name, table in category_tables.items()},
            "custom_sku_rows": int(evaluations["定制标记"].eq("是").sum()),
            "review_exact_rows": int(evaluations["差评匹配方式"].eq("精确匹配").sum()),
            "review_fuzzy_rows": int(evaluations["差评匹配方式"].eq("模糊匹配").sum()),
            "review_inferred_rows": int(evaluations["差评匹配方式"].eq("推理匹配").sum()),
            "review_inferred_detail_rows": inference_status["detail_rows"],
            "review_inference_keys": inference_status["keys"],
            "gray_groups_passed": int(gray_audit["判定"].eq("通过").sum()) if len(gray_audit) else 0,
            "gray_adjusted_rows": int(prepared["灰度调整"].sum()),
            "sales_matched_rows": int(sales_audit["匹配状态"].ne("待审核").sum()),
            "sales_boosted_skus": int(evaluations["市场调整增加值"].gt(0).sum()),
            "code_sha256": sha256(Path(__file__)),
            "effective_config": config,
        }
        record = batch.finish(status, publish_to=PROJECT / "output")
        return batch.directory, record, evaluations, detail, gray_audit


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    directory, record, evaluations, detail, gray = run()
    print(directory)
    print(json.dumps(record["status"], ensure_ascii=False, indent=2))
