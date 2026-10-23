"""非皮卡、非W型车上架组合研究。仅生成RunBatch，不发布output或NAS。"""
from __future__ import annotations

import argparse
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

CONFIG_PATH = PROJECT / "data" / "非皮卡非W上架分析.json"
FULL_TABLE = REPO / "nodes" / "A0.尺码计算" / "output" / "US" / "全量" / "全量表.csv"
RULES = REPO / "nodes" / "A0.尺码计算" / "output" / "US" / "尺码规则.json"
SHELVES = REPO / "nodes" / "A0.尺码计算" / "output" / "US" / "店铺货架.json"
SALES = REPO / "nodes" / "02.销量评估" / "output" / "原子销量.csv"


def parse_years(value: str) -> list[int]:
    match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", str(value).strip())
    if not match:
        raise ValueError(f"无法解析年份: {value}")
    start, end = int(match[1]), int(match[2] or match[1])
    if end < start:
        raise ValueError(f"年份倒序: {value}")
    return list(range(start, end + 1))


def compact_years(values) -> str:
    years = sorted(set(values))
    spans: list[str] = []
    i = 0
    while i < len(years):
        start = end = years[i]
        i += 1
        while i < len(years) and years[i] == end + 1:
            end = years[i]
            i += 1
        spans.append(str(start) if start == end else f"{start}-{end}")
    return "/".join(spans)


def largest_remainder(weights, budget: int) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    if budget <= 0 or len(weights) == 0 or not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError("预算须为正整数，权重须非负且合计大于0")
    if int(budget) != budget:
        raise ValueError("预算须为整数")
    exact = budget * weights / weights.sum()
    result = np.floor(exact).astype(int)
    order = np.argsort(-(exact - result), kind="stable")
    result[order[:int(budget) - int(result.sum())]] += 1
    return result


def matching(frame: pd.DataFrame, rule: dict) -> pd.Series:
    mask = pd.Series(True, index=frame.index)
    for column in ("MAKE", "MODEL", "版本"):
        if column in rule:
            mask &= frame[column].eq(rule[column])
    return mask


def prepare(full: pd.DataFrame, sales: pd.DataFrame, rules: dict, config: dict, w_config: dict):
    full, sales = full.copy(), sales.copy()
    if full["DIMENSION-ID"].duplicated().any() or sales["atom_record_id"].duplicated().any():
        raise ValueError("上游身份重复")
    parsed = sales["atom_record_id"].str.extract(r"^(.*)\|ATOM_YEAR=(\d{4})$")
    if parsed.isna().any().any():
        raise ValueError("年度销量原子身份格式不合法")
    sales["DIMENSION-ID"], sales["ATOM_YEAR"] = parsed[0], parsed[1].astype(int)
    sales["预估销量"] = pd.to_numeric(sales["预估销量"], errors="raise")
    requested_years = sales["ATOM_YEAR"].between(*config["ranking_years"]) | sales["ATOM_YEAR"].between(*config["reference_years"])
    invalid = ~np.isfinite(sales["预估销量"])
    if (invalid & requested_years).any() or (sales["预估销量"] < 0).any():
        raise ValueError("分析期销量存在缺失/无效值，或源销量存在负值")
    sales["期外销量缺失"] = invalid
    if set(sales["DIMENSION-ID"]) != set(full["DIMENSION-ID"]):
        raise ValueError("A0与年度原子销量DIMENSION-ID未完全对齐")
    for column in ["L-MM", "W-MM", "H-MM", "自动长度余量", "尺寸组销量"]:
        full[column] = pd.to_numeric(full[column], errors="coerce")
    totals = sales.groupby("DIMENSION-ID")["预估销量"].sum(min_count=1)
    delta = full["DIMENSION-ID"].map(totals) - full["尺寸组销量"]
    if (delta.dropna().abs() > 1e-6).any():
        raise ValueError("年度销量与A0尺寸组销量未守恒")
    missing_count = sales[invalid].groupby("DIMENSION-ID").size()
    full["期外缺失年度数"] = full["DIMENSION-ID"].map(missing_count).fillna(0).astype(int)
    for name, period in [("近期销量估值", config["ranking_years"]), ("参考期销量估值", config["reference_years"])]:
        values = sales[sales["ATOM_YEAR"].between(*period)].groupby("DIMENSION-ID")["预估销量"].sum()
        full[name] = full["DIMENSION-ID"].map(values).fillna(0)

    full["范围判定"] = "范围内"
    pickup = full["分类"].eq("皮卡") | full["结构"].eq("Pickup") | full["自动尺码"].str.startswith("PK-")
    w = full["自动尺码"].isin(w_config["target_sizes"])
    for prefix in config["exclude_size_prefixes"]:
        w |= full["自动尺码"].str.startswith(prefix)
    for rule in config["exclude_models"]:
        w |= matching(full, rule)
    w |= ((full["MAKE"] == "Chevrolet") & (full["MODEL"] == "Bel Air") &
          (full["结构"] != "Wagon") & full["YEAR"].map(lambda value: max(parse_years(value)) <= w_config["dedicated_max_year"]))
    full.loc[w, "范围判定"] = "排除W范围"
    full.loc[pickup, "范围判定"] = "排除皮卡"
    known = {row["尺码"] for row in rules["rules"]}
    invalid = ~full["自动尺码"].isin(known) | full[["L-MM", "W-MM", "H-MM", "自动长度余量"]].isna().any(axis=1) | full["自动长度余量"].lt(0)
    full.loc[full["范围判定"].eq("范围内") & invalid, "范围判定"] = "无有效匹配或尺寸"
    full["暂缓原因"] = ""
    full["质量提醒"] = ""
    for rule in config["dimension_holds"]:
        full.loc[matching(full, rule), "暂缓原因"] = rule["reason"]
    for rule in config["allocation_review_models"]:
        full.loc[matching(full, rule), "质量提醒"] = rule["reason"]

    def cid(row):
        payload = json.dumps([row[key] for key in config["cluster_keys"]], ensure_ascii=False)
        return "MAIN-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12].upper()

    full["CLUSTER_ID"] = full.apply(cid, axis=1)
    atoms = sales.merge(full, on="DIMENSION-ID", how="left", validate="many_to_one")
    outside = ~atoms.apply(lambda row: int(row["ATOM_YEAR"]) in parse_years(row["YEAR"]), axis=1)
    if outside.any():
        raise ValueError("销量原子年份超出尺寸记录年份")
    return full, atoms


def make_candidates(full, atoms, config, shelves, include_historical=False):
    scope = full[full["范围判定"].eq("范围内")].copy()
    recent = atoms[atoms["范围判定"].eq("范围内") & atoms["ATOM_YEAR"].between(*config["ranking_years"])]
    owners = recent.groupby(["MAKE", "MODEL", "版本", "结构", "ATOM_YEAR"])["CLUSTER_ID"].nunique()
    conflicting_keys = set(owners[owners > 1].index)
    conflict_ids = set()
    for _, row in recent.iterrows():
        if (row["MAKE"], row["MODEL"], row["版本"], row["结构"], row["ATOM_YEAR"]) in conflicting_keys:
            conflict_ids.add(row["CLUSTER_ID"])
    records = []
    included = scope["近期销量估值"].gt(0)
    if include_historical:
        included |= scope["追加候选"]
    for cluster_id, group in scope[included].groupby("CLUSTER_ID", sort=True):
        first = group.iloc[0]
        year_column = "研究适配年份" if "研究适配年份" in group.columns else "YEAR"
        years = [year for value in group[year_column] for year in parse_years(value) if year <= config["fitment_max_year"]]
        holds = sorted(set(group["暂缓原因"]) - {""})
        notes = sorted(set(group["质量提醒"]) - {""})
        if group["期外缺失年度数"].gt(0).any():
            notes.append("存在分析期以外的缺失年度销量；未按0补齐，也不参与本期权重")
        if cluster_id in conflict_ids:
            holds.append("同车型/版本/结构/年度对应多个尺码或SHAPE，实际适配归属待核对")
        margin = group["自动长度余量"].min()
        if margin < config["fit_review_length_margin_below_mm"]:
            notes.append(f"原尺码最小长度余量{margin:g}mm，先试套；本轮不执行灰区升码")
        for column, threshold in config["spread_review_mm"].items():
            spread = group[column].max() - group[column].min()
            if spread > threshold:
                notes.append(f"簇内{column}跨度{spread:g}mm超过研究提醒值{threshold}mm，核对是否分代")
        shop_names = [name for name, rows in shelves["stores"].items() if any(item["匹配尺码"] == first["自动尺码"] for item in rows)]
        record = {key: first[key] for key in config["cluster_keys"]}
        record.update({
            "CLUSTER_ID": cluster_id, "PHYSICAL_SKU": first["自动尺码"],
            "适配年份": compact_years(years), "近期销量估值": group["近期销量估值"].sum(),
            "参考期销量估值": group["参考期销量估值"].sum(), "尺寸记录数": len(group),
            "最小长度余量mm": margin, "最大长度余量mm": group["自动长度余量"].max(),
            "已有匹配货架": "/".join(shop_names) or "当前店铺未登记该匹配尺码",
            "暂缓原因": "；".join(holds), "质量提醒": "；".join(notes),
            "上架前检查": "核对实物/版型、年度版本适配及上游销量分配；本表不是已发布链接",
        })
        for column in ["L-MM", "W-MM", "H-MM"]:
            record[f"{column}_MIN"] = group[column].min()
            record[f"{column}_MAX"] = group[column].max()
        record["候选状态"] = "暂缓" if holds else "可参与试算"
        if include_historical:
            segment_ids = sorted(set(group["请求细分ID"]) - {""})
            if len(segment_ids) > 1:
                raise ValueError("不同指定细分被归入同一簇，需先拆分身份")
            record["请求细分ID"] = segment_ids[0] if segment_ids else ""
            record["请求条目"] = " / ".join(sorted(set(group["请求条目"]) - {""}))
            record["生命周期已知销量估值"] = group["尺寸组销量"].sum()
        records.append(record)
    candidates = pd.DataFrame(records).sort_values(["近期销量估值", "CLUSTER_ID"], ascending=[False, True]).reset_index(drop=True)
    denominator = scope["近期销量估值"].sum()
    candidates["范围内销量占比"] = candidates["近期销量估值"] / denominator
    candidates["全范围800件比例配额"] = config["shipment_budget"] * candidates["范围内销量占比"]
    return scope, candidates, len(conflicting_keys)


def select_portfolio(candidates, count, budget):
    selected = candidates[candidates["候选状态"].eq("可参与试算")].head(count).copy()
    selected["组合内占比"] = selected["近期销量估值"] / selected["近期销量估值"].sum()
    selected["800件试算分配"] = largest_remainder(selected["近期销量估值"], budget)
    selected["建议顺序"] = range(1, len(selected) + 1)
    return selected


def markdown_table(frame, columns):
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    for _, row in frame.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, (float, np.floating)) and value.is_integer():
                value = int(value)
            values.append(str(value).replace("|", "/").replace("\n", " "))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def run(config_path=CONFIG_PATH, budget=None):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if budget is not None:
        config["shipment_budget"] = budget
    w_config = json.loads((PROJECT / "data" / "W型车目标尺码.json").read_text(encoding="utf-8"))
    with RunBatch.create(PROJECT / "artifacts", "mainstream-listing-800-research", data_dir=PROJECT / "data") as batch:
        full_path, atom_path = batch.input(FULL_TABLE), batch.input(SALES)
        rules_path, shelves_path = batch.input(RULES), batch.input(SHELVES)
        full, atoms = prepare(pd.read_csv(full_path, keep_default_na=False), pd.read_csv(atom_path),
                              json.loads(rules_path.read_text(encoding="utf-8")), config, w_config)
        scope, candidates, conflict_count = make_candidates(full, atoms, config, json.loads(shelves_path.read_text(encoding="utf-8")))
        selected = select_portfolio(candidates, config["portfolio_cluster_count"], config["shipment_budget"])
        models = scope.groupby(["MAKE", "MODEL"], as_index=False).agg(
            近期销量估值=("近期销量估值", "sum"), 参考期销量估值=("参考期销量估值", "sum"))
        denominator = models["近期销量估值"].sum()
        models = models[models["近期销量估值"].gt(0)].sort_values(["近期销量估值", "MAKE", "MODEL"], ascending=[False, True, True])
        models["范围内销量占比"] = models["近期销量估值"] / denominator
        model_units = selected.groupby(["MAKE", "MODEL"])["800件试算分配"].sum()
        models["入选组合分配件数"] = [int(model_units.get((r.MAKE, r.MODEL), 0)) for r in models.itertuples()]
        models["市场候选排名"] = range(1, len(models) + 1)
        held_models = set(candidates.loc[candidates["候选状态"].eq("暂缓"), ["MAKE", "MODEL"]].itertuples(index=False, name=None))
        models["组合决策说明"] = [
            "入选，按精确版本/结构/SHAPE/尺码分配" if row.入选组合分配件数 else
            "主要版本暂缓；其余单簇未进入本轮前列" if (row.MAKE, row.MODEL) in held_models else
            "销量分散到多个结构/版本/SHAPE/尺码簇，单簇未进入本轮前列"
            for row in models.itertuples()]
        stock = selected.groupby("PHYSICAL_SKU", as_index=False).agg(
            试算备货件数=("800件试算分配", "sum"), 建议链接数=("CLUSTER_ID", "nunique"),
            近期销量估值=("近期销量估值", "sum"), 最小长度余量mm=("最小长度余量mm", "min"))
        stock = stock.sort_values(["试算备货件数", "PHYSICAL_SKU"], ascending=[False, True])
        quality = candidates[candidates["暂缓原因"].ne("") | candidates["质量提醒"].ne("")].copy()
        quality["入选800件组合"] = quality["CLUSTER_ID"].isin(selected["CLUSTER_ID"])
        comparisons = []
        for count in config["comparison_cluster_counts"]:
            case = select_portfolio(candidates, count, config["shipment_budget"])
            coverage = case["近期销量估值"].sum() / denominator
            comparisons.append({"建议链接数": len(case), "车型数": len(case[["MAKE", "MODEL"]].drop_duplicates()),
                                "物理尺码数": case["PHYSICAL_SKU"].nunique(), "范围内销量覆盖占比": coverage,
                                "全范围800件覆盖配额": config["shipment_budget"] * coverage,
                                "组合内试算总件数": int(case["800件试算分配"].sum()),
                                "最小单链接配额": int(case["800件试算分配"].min()), "归一化倍数": 1 / coverage})
        comparisons = pd.DataFrame(comparisons)
        for name, frame in [("车型市场候选.csv", models), ("聚类候选.csv", candidates),
                            ("推荐上架与800件分配.csv", selected), ("物理尺码备货汇总.csv", stock),
                            ("资料质量待处理.csv", quality), ("情景比较.csv", comparisons)]:
            frame.to_csv(batch.output(name), index=False, encoding="utf-8-sig", float_format="%.6f")

        detail = scope[scope["CLUSTER_ID"].isin(selected["CLUSTER_ID"]) & scope["近期销量估值"].gt(0)].copy()
        detail["建议适配年份"] = detail["YEAR"].map(lambda value: compact_years(y for y in parse_years(value) if y <= config["fitment_max_year"]))
        full.to_csv(batch.extra("范围筛选与源记录.csv"), index=False, encoding="utf-8-sig", compression="gzip")
        detail.to_csv(batch.extra("入选适配依据.csv"), index=False, encoding="utf-8-sig", compression="gzip")
        atoms[atoms["ATOM_YEAR"].between(*config["ranking_years"])].to_csv(
            batch.extra("排名期年度原子依据.csv"), index=False, encoding="utf-8-sig", compression="gzip")
        coverage = selected["近期销量估值"].sum() / denominator
        fit_review = selected[selected["最小长度余量mm"].lt(config["fit_review_length_margin_below_mm"])]
        shelf_review = selected[selected["已有匹配货架"].eq("当前店铺未登记该匹配尺码")]
        metrics = {"budget": config["shipment_budget"], "effective_config": config, "code_sha256": sha256(Path(__file__)),
                   "source_dimensions": len(full), "source_annual_atoms": len(atoms),
                   "scope_counts": full["范围判定"].value_counts().to_dict(), "scope_recent_sales": denominator,
                   "candidate_clusters": len(candidates), "held_clusters": int(candidates["候选状态"].eq("暂缓").sum()),
                   "conflicting_model_version_body_year_keys": conflict_count,
                   "selected_clusters": len(selected), "selected_models": len(selected[["MAKE", "MODEL"]].drop_duplicates()),
                   "selected_physical_skus": selected["PHYSICAL_SKU"].nunique(), "coverage": coverage,
                   "normalization_multiplier": 1 / coverage, "allocated_units": int(selected["800件试算分配"].sum()),
                   "input_known_sales_reconciled": True, "missing_outside_period_atoms": int(atoms["期外销量缺失"].sum()),
                   "tight_margin_clusters": len(fit_review), "tight_margin_allocated_units": int(fit_review["800件试算分配"].sum()),
                   "missing_shelf_clusters": len(shelf_review), "missing_shelf_allocated_units": int(shelf_review["800件试算分配"].sum()),
                   "publication": "research_only_not_published"}
        if selected["CLUSTER_ID"].duplicated().any() or detail["DIMENSION-ID"].duplicated().any():
            raise ValueError("入选身份重复")
        if metrics["allocated_units"] != config["shipment_budget"] or int(stock["试算备货件数"].sum()) != config["shipment_budget"]:
            raise ValueError("800件分配未守恒")
        if selected["暂缓原因"].ne("").any() or not detail["范围判定"].eq("范围内").all():
            raise ValueError("入选组合包含排除或暂缓记录")
        # Reports contain actual source year ranges; no version/body Cartesian expansion.
        source_coverage = atoms[atoms["CLUSTER_ID"].isin(selected["CLUSTER_ID"]) & atoms["ATOM_YEAR"].between(*config["ranking_years"])]
        if not np.isclose(source_coverage["预估销量"].sum(), selected["近期销量估值"].sum()):
            raise ValueError("入选年度原子与簇权重未守恒")
        summary = selected.copy()
        summary["车型配置"] = summary.apply(lambda r: " ".join(str(r[k]) for k in ["MAKE", "MODEL", "版本", "结构"] if r[k]), axis=1)
        summary["范围内占比"] = summary["范围内销量占比"].map(lambda n: f"{n:.2%}")
        model_summary = models.head(15).copy()
        model_summary["范围内占比"] = model_summary["范围内销量占比"].map(lambda n: f"{n:.2%}")
        report = ["# 非皮卡、非W型车推荐上架研究", "",
                  f"本轮建议 {len(selected)} 个研究链接、{metrics['selected_models']} 个车型、{metrics['selected_physical_skus']} 个物理尺码，组合合计试算 {config['shipment_budget']} 件。未发布 output 或 NAS。", "",
                  "## 口径", "",
                  f"- 区域US；排名期{config['ranking_years'][0]}–{config['ranking_years'][1]}；参考期{config['reference_years'][0]}–{config['reference_years'][1]}。2026及以后不参与销量权重。原始YEAR保留，建议适配年份最多到{config['fitment_max_year']}，不补齐缺口。",
                  "- 排除皮卡、当前4*尺码系列、旧W专用车型Challenger/Model X和Bel Air专用年份；筛除无有效尺码、尺寸缺失及负长度余量。W范围为保守研究定义。",
                  "- 销量占比的分母为上述有效范围内的库内年度销量估值，不是全美国市场份额、实测保有量或车罩需求份额；原子输出不含来源置信度，本轮无法逐年区分实测和估算。",
                  "- 车型排名包含暂缓版本的原始估值，便于发现高市场潜力；链接分配排除暂缓项。车型/版本/结构/SHAPE/尺码分别聚类，不执行非皮卡灰区升码，不生成TRIM通配声明。",
                  f"- 全范围排名期销量估值 {denominator:,.0f}，入选覆盖 {coverage:.2%}；若{config['shipment_budget']}件代表全范围需求，入选部分仅对应 {config['shipment_budget'] * coverage:.1f} 件。将总件数全部配置到入选组合，归一化倍数为 {1 / coverage:.2f}，不能理解为需求自然增加。",
                  "- 分配公式：组合件数 × 入选簇销量 / 入选簇销量合计，最大余数法补齐整数。没有车罩转化率、广告、价格或真实订单校准，也未假设年份淘汰率。", "",
                  "## 高销量车型与组合取舍", "",
                  *markdown_table(model_summary, ["市场候选排名", "MAKE", "MODEL", "近期销量估值", "范围内占比", "入选组合分配件数", "组合决策说明"]), "",
                  "车型总量排行和链接排行分开：本轮按单簇销量选前24，Civic/Accord等高总量车型可能因结构或SHAPE分散而暂不入选。该选择适合控制首轮链接数，不代表这些车型市场潜力低，也未求解利润或广告转化最优组合。", "",
                  "## 推荐组合", "",
                  *markdown_table(summary, ["建议顺序", "车型配置", "适配年份", "PHYSICAL_SKU", "范围内占比", "800件试算分配", "最小长度余量mm"]), "",
                  "不同版本/结构的年份范围只对该行适用，不可合并成全版本适配。即使同一PHYSICAL_SKU，也须分别核对不同SHAPE的轮廓。紧边界先试套，不表示已通过实物适配。", "",
                  "## 物理尺码备货与上架前检查", "",
                  *markdown_table(stock, ["PHYSICAL_SKU", "试算备货件数", "建议链接数", "最小长度余量mm"]), "",
                  f"- {len(fit_review)}个链接、{metrics['tight_margin_allocated_units']}件的最小长度余量低于50mm，先核实试套；这部分仍列在试算总额内，不能当作已批准发货。",
                  f"- {len(shelf_review)}个链接、{metrics['missing_shelf_allocated_units']}件的匹配尺码未在当前店铺货架登记：" + "、".join(sorted(shelf_review["PHYSICAL_SKU"].unique())) + "。需要选择目标店铺并确认库存/发货映射，不自动改用店铺其他尺码。",
                  "- 上述检查集合可能重叠，不能将件数相加作为独立库存缺口；其余配额也仍需常规实物与适配审核。", "",
                  "## 组合规模比较", "", *markdown_table(comparisons.round(4), list(comparisons.columns)), "",
                  "24个链接是本轮可调研究假设，不是销量最优解；12/24/36组合分别披露覆盖率、归一化倍数和单链接最小配额。", "",
                  "## 数据质量与暂缓", "",
                  *[f"- {rule['MAKE']} {rule['MODEL']} {rule['版本']}：{rule['reason']}" + (f" [官方依据]({rule['source_url']})" if rule['source_url'] else "") for rule in config["dimension_holds"]],
                  *[f"- {rule['MAKE']} {rule['MODEL']}：{rule['reason']}" for rule in config["allocation_review_models"]],
                  "- 长度余量小于50mm和簇内跨度提醒在候选表、质量待处理表中逐项列示。阈值仅作本轮提醒，不修改A0规则，也不代表非皮卡灰区已启用。", "",
                  "## 校验与下一步", "",
                  f"- {len(full):,}个尺寸ID与{len(atoms):,}条年度销量原子完整对应；已知年度销量求和与A0尺寸组销量逐ID核对。期外缺失销量原子{metrics['missing_outside_period_atoms']}条，保留缺失，不将全缺失记录解释为真实0销量；分析期不含缺失。",
                  f"- 排名期同车型/版本/结构/年度跨Cluster身份冲突 {conflict_count} 组；存在冲突的候选暂缓。入选源记录唯一，年度销量权重与聚类、备货合计分别守恒。",
                  "- 本轮是研究候选，CLUSTER_ID为研究身份，不是已分配的持久LINK_ID。源TRIM不作为已核验适配事实；版本销量、跨年轮廓及实物试套尚需上架前核对。",
                  "- 后续优先核对暂缓的大销量车型、紧余量车型及结构分配；确认店铺、包装/最小起订量和真实订单转化后再调整配额。", "",
                  "## 复算与追踪", "",
                  "运行：在D1目录执行 `python src/mainstream_listing_analysis.py`；可用 `--budget` 改组合总件数。研究参数位于data/非皮卡非W上架分析.json，每次运行创建新RunBatch，不更新正式output、流水线状态或NAS。",
                  "run.json记录有效参数、源文件SHA256/上游版本和规则快照；大明细在extra/中gzip保存。" ]
        batch.output("REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        batch.finish(metrics)
        return batch.directory, selected, models, stock, comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=int, help="组合总件数，默认800")
    args = parser.parse_args()
    if args.budget is not None and args.budget <= 0:
        parser.error("--budget必须为正整数")
    directory, selected, models, stock, comparisons = run(budget=args.budget)
    print(directory)
    print(selected[["MAKE", "MODEL", "版本", "结构", "PHYSICAL_SKU", "800件试算分配"]].to_string(index=False))
    print(stock.to_string(index=False))
    print(comparisons.to_string(index=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
