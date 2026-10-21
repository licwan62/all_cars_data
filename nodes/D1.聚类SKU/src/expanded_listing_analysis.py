"""在800件基线候选上追加指定车型，综合900件试销配额研究。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd

import mainstream_listing_analysis as base

PROJECT = base.PROJECT
REPO = base.REPO
CONFIG_PATH = PROJECT / "data" / "指定车型追加900.json"


def request_mask(frame, segment, config, max_year):
    mask = frame["MAKE"].str.casefold().eq(segment["MAKE"].casefold()) & frame["MODEL"].str.casefold().eq(segment["MODEL"].casefold())
    if "version_pattern" in segment:
        mask &= frame["版本"].str.contains(segment["version_pattern"], case=False, regex=True)
    if "generation" in segment:
        mask &= frame["代际"].eq(segment["generation"])
    first = segment.get("min_year", config["default_min_fitment_year"])
    last = min(segment.get("max_year", max_year), max_year)
    mask &= frame["YEAR"].map(lambda value: bool(set(base.parse_years(value)) & set(range(first, last + 1))))
    return mask


def extend_scope(full, atoms, rules, config, base_config):
    full = full.copy()
    full["原范围判定"] = full["范围判定"]
    full["请求细分ID"] = ""
    full["请求条目"] = ""
    full["追加候选"] = False
    full["研究适配年份"] = full["YEAR"]
    known = {row["尺码"] for row in rules["rules"]}
    valid = (full["自动尺码"].isin(known) & full[["L-MM", "W-MM", "H-MM", "自动长度余量"]].notna().all(axis=1)
             & full["自动长度余量"].ge(0) & full["范围判定"].ne("排除皮卡"))
    for segment in config["segments"]:
        mask = request_mask(full, segment, config, base_config["fitment_max_year"])
        if full.loc[mask, "请求细分ID"].ne("").any():
            raise ValueError(f"指定范围重叠: {segment['id']}")
        full.loc[mask, "请求细分ID"] = segment["id"]
        full.loc[mask, "请求条目"] = segment["parent"]
        full.loc[mask & valid, "追加候选"] = True
        full.loc[mask & valid, "范围判定"] = "范围内"
        first = segment.get("min_year", config["default_min_fitment_year"])
        last = min(segment.get("max_year", base_config["fitment_max_year"]), base_config["fitment_max_year"])
        full.loc[mask, "研究适配年份"] = full.loc[mask, "YEAR"].map(
            lambda value: base.compact_years(year for year in base.parse_years(value) if first <= year <= last))
        if segment.get("generation"):
            # Corvette不同代际不能因结构/版本/尺码相同而重新混成一个代表簇。
            full.loc[mask, "CLUSTER_ID"] = full.loc[mask, "CLUSTER_ID"].map(
                lambda value: "MAIN-" + hashlib.sha256(f"{value}|{segment['id']}".encode()).hexdigest()[:12].upper())
        if segment.get("note"):
            full.loc[mask, "质量提醒"] = full.loc[mask, "质量提醒"].map(lambda value: "；".join(v for v in [value, segment["note"]] if v))
    # 重建关联，避免沿用原范围或原Cluster身份。
    atom_columns = ["atom_record_id", "预估销量", "DIMENSION-ID", "ATOM_YEAR", "期外销量缺失"]
    atoms = atoms[atom_columns].merge(full, on="DIMENSION-ID", how="left", validate="many_to_one")
    return full, atoms


def pick_requested(candidates, config):
    selected = {}
    audit = []
    for segment in config["segments"]:
        group = candidates[candidates["请求细分ID"].eq(segment["id"])]
        eligible = group[group["候选状态"].eq("可参与试算")].sort_values(
            ["近期销量估值", "参考期销量估值", "生命周期已知销量估值", "CLUSTER_ID"], ascending=[False, False, False, True])
        record = {"请求细分ID": segment["id"], "指定细分": segment["label"], "原始请求条目": segment["parent"],
                  "候选簇数": len(group), "暂缓簇数": int(group["候选状态"].eq("暂缓").sum()),
                  "选择说明": segment.get("note", "每细分首轮选一个代表簇，其他版本不自动覆盖")}
        if eligible.empty:
            record.update({"覆盖状态": "待处理：无可用代表簇", "CLUSTER_ID": "", "PHYSICAL_SKU": "", "适配年份": "", "版本": "", "结构": "", "代表选择依据": ""})
        else:
            row = eligible.iloc[0]
            selected[segment["id"]] = row["CLUSTER_ID"]
            basis = "2020-2025近期销量" if row["近期销量估值"] > 0 else "2010-2025参考期销量" if row["参考期销量估值"] > 0 else "生命周期已知销量（仅用于挑选代表）"
            record.update({"覆盖状态": "代表簇已纳入；非全系覆盖", "CLUSTER_ID": row["CLUSTER_ID"],
                           "PHYSICAL_SKU": row["PHYSICAL_SKU"], "适配年份": row["适配年份"],
                           "版本": row["版本"], "结构": row["结构"], "代表选择依据": basis})
        audit.append(record)
    return selected, pd.DataFrame(audit)


def allocate(selected, requested_cluster_ids, budget, minimum):
    selected = selected.sort_values(["近期销量估值", "CLUSTER_ID"], ascending=[False, True]).copy()
    if budget <= 0 or minimum < 0 or int(budget) != budget or int(minimum) != minimum:
        raise ValueError("总预算须为正整数、保底须为非负整数")
    selected["指定试销保底件数"] = selected["CLUSTER_ID"].isin(requested_cluster_ids).astype(int) * minimum
    remaining = budget - int(selected["指定试销保底件数"].sum())
    if remaining < 0:
        raise ValueError("指定细分保底总量超过预算")
    selected["销量权重分配件数"] = base.largest_remainder(selected["近期销量估值"], remaining) if remaining else 0
    selected["综合试算件数"] = selected["指定试销保底件数"] + selected["销量权重分配件数"]
    selected["综合配额占比"] = selected["综合试算件数"] / budget
    return selected


def run():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    base_config = json.loads((PROJECT / "data" / config["base_config"]).read_text(encoding="utf-8"))
    w_config = json.loads((PROJECT / "data" / "W型车目标尺码.json").read_text(encoding="utf-8"))
    budget = config["shipment_budget"]
    with base.RunBatch.create(PROJECT / "artifacts", f"mainstream-listing-{budget}-expanded-research", data_dir=PROJECT / "data") as batch:
        inputs = [batch.input(path) for path in [base.FULL_TABLE, base.SALES, base.RULES, base.SHELVES]]
        rules, shelves = [json.loads(path.read_text(encoding="utf-8")) for path in inputs[2:]]
        full, atoms = base.prepare(pd.read_csv(inputs[0], keep_default_na=False), pd.read_csv(inputs[1]), rules, base_config, w_config)
        _, baseline_candidates, _ = base.make_candidates(full, atoms, base_config, shelves)
        baseline = base.select_portfolio(baseline_candidates, base_config["portfolio_cluster_count"], base_config["shipment_budget"])
        baseline_ids = set(baseline["CLUSTER_ID"])
        full, atoms = extend_scope(full, atoms, rules, config, base_config)
        effective = {**base_config, "shipment_budget": budget}
        scope, candidates, conflicts = base.make_candidates(full, atoms, effective, shelves, include_historical=True)
        candidates = candidates.rename(columns={"全范围800件比例配额": "扩展范围基准比例配额"})
        loose_mask = candidates["最大长度余量mm"].gt(config["loose_margin_review_above_mm"])
        for index in candidates.index[loose_mask]:
            note = f"最大长度余量{candidates.at[index, '最大长度余量mm']:g}mm，超过本轮松量提醒值{config['loose_margin_review_above_mm']}mm，核对轮廓和松量后试销"
            candidates.at[index, "质量提醒"] = "；".join(value for value in [candidates.at[index, "质量提醒"], note] if value)
        requested, coverage = pick_requested(candidates, config)
        requested_ids = set(requested.values())
        ids = baseline_ids | requested_ids
        selected = candidates[candidates["CLUSTER_ID"].isin(ids)].copy()
        if set(selected["CLUSTER_ID"]) != ids:
            raise ValueError("基线或指定代表簇丢失")
        selected = allocate(selected, requested_ids, budget, config["requested_segment_minimum_units"])
        selected["组合来源"] = selected["CLUSTER_ID"].map(lambda value: "原组合+指定（去重）" if value in baseline_ids & requested_ids else "原24簇保留" if value in baseline_ids else "指定追加")
        selected["建议顺序"] = range(1, len(selected) + 1)
        coverage["综合试算件数"] = coverage["CLUSTER_ID"].map(selected.set_index("CLUSTER_ID")["综合试算件数"]).fillna(0).astype(int)
        coverage["与原组合重合"] = coverage["CLUSTER_ID"].isin(baseline_ids)
        stock = selected.groupby("PHYSICAL_SKU", as_index=False).agg(
            综合试算件数=("综合试算件数", "sum"), 研究链接数=("CLUSTER_ID", "nunique"),
            指定试销保底件数=("指定试销保底件数", "sum"), 最小长度余量mm=("最小长度余量mm", "min"))
        stock = stock.sort_values(["综合试算件数", "PHYSICAL_SKU"], ascending=[False, True])
        candidate_details = candidates[candidates["请求细分ID"].ne("")].copy()
        candidate_details["选为指定代表"] = candidate_details["CLUSTER_ID"].isin(requested_ids)
        quality = candidates[candidates["暂缓原因"].ne("") | candidates["质量提醒"].ne("")].copy()
        quality["入选900件组合"] = quality["CLUSTER_ID"].isin(ids)
        comparison = selected.merge(baseline[["CLUSTER_ID", "800件试算分配"]], on="CLUSTER_ID", how="left", validate="one_to_one")
        comparison["原800件方案件数"] = comparison["800件试算分配"].fillna(0).astype(int)
        comparison["件数变化"] = comparison["综合试算件数"] - comparison["原800件方案件数"]
        comparison = comparison.drop(columns="800件试算分配")
        scenarios = []
        for minimum in config["minimum_units_comparison"]:
            case = allocate(selected, requested_ids, budget, minimum)
            scenarios.append({"指定代表保底件数": minimum, "指定代表数": len(requested_ids),
                              "保底合计": int(case["指定试销保底件数"].sum()), "近期销量比例分配合计": int(case["销量权重分配件数"].sum()),
                              "综合件数": int(case["综合试算件数"].sum()), "零近期销量细分件数": int(case.loc[case["近期销量估值"].eq(0), "综合试算件数"].sum())})
        scenarios = pd.DataFrame(scenarios)
        for name, frame in [("指定车型覆盖与分配.csv", coverage), ("追加候选细分.csv", candidate_details),
                            (f"推荐上架与{budget}件分配.csv", selected), ("物理尺码备货汇总.csv", stock),
                            ("资料质量待处理.csv", quality), ("与800件基线对比.csv", comparison), ("配额假设比较.csv", scenarios)]:
            frame.to_csv(batch.output(name), index=False, encoding="utf-8-sig", float_format="%.6f")
        included_rows = full[full["范围判定"].eq("范围内") & (full["近期销量估值"].gt(0) | full["追加候选"])]
        detail = included_rows[included_rows["CLUSTER_ID"].isin(ids)].copy()
        full.to_csv(batch.extra("范围筛选与源记录.csv"), index=False, encoding="utf-8-sig", compression="gzip")
        detail.to_csv(batch.extra("入选适配依据.csv"), index=False, encoding="utf-8-sig", compression="gzip")
        atoms[atoms["CLUSTER_ID"].isin(ids)].to_csv(batch.extra("入选原子销量依据.csv"), index=False, encoding="utf-8-sig", compression="gzip")
        # 独立对账：只统计入选证据实际包含的尺寸ID，避免历史追加导致重复计数。
        recent_atoms = atoms[atoms["DIMENSION-ID"].isin(detail["DIMENSION-ID"]) & atoms["ATOM_YEAR"].between(*base_config["ranking_years"])]
        if not np.isclose(recent_atoms["预估销量"].sum(), selected["近期销量估值"].sum()):
            raise ValueError("入选近期销量与年度原子不守恒")
        if selected["CLUSTER_ID"].duplicated().any() or detail["DIMENSION-ID"].duplicated().any():
            raise ValueError("入选身份重复")
        if selected["暂缓原因"].ne("").any() or int(stock["综合试算件数"].sum()) != budget:
            raise ValueError("配额守恒或质量暂缓检查失败")
        if not baseline_ids.issubset(ids) or len(baseline) != base_config["portfolio_cluster_count"]:
            raise ValueError("原24簇未完整保留")
        tight = selected[selected["最小长度余量mm"].lt(base_config["fit_review_length_margin_below_mm"])]
        shelf_missing = selected[selected["已有匹配货架"].eq("当前店铺未登记该匹配尺码")]
        denominator = scope["近期销量估值"].sum()
        coverage_rate = selected["近期销量估值"].sum() / denominator
        metrics = {"budget": budget, "effective_config": config, "base_config": base_config,
                   "code_sha256": base.sha256(Path(__file__)), "base_code_sha256": base.sha256(Path(base.__file__)),
                   "baseline_reconstruction": "current_upstream_outputs_same_method_not_historical_artifact_input",
                   "baseline_clusters": len(baseline), "requested_parent_items": coverage["原始请求条目"].nunique(),
                   "requested_segments": len(coverage), "covered_segments": len(requested), "requested_representatives": len(requested_ids),
                   "overlap_with_baseline": len(baseline_ids & requested_ids), "added_clusters": len(ids - baseline_ids),
                   "selected_clusters": len(selected), "selected_models": len(selected[["MAKE", "MODEL"]].drop_duplicates()),
                   "physical_skus": selected["PHYSICAL_SKU"].nunique(), "allocated_units": int(selected["综合试算件数"].sum()),
                   "reserved_units": int(selected["指定试销保底件数"].sum()),
                   "scope_recent_sales": denominator, "recent_sales_coverage": coverage_rate,
                   "conflicting_model_version_body_year_keys": conflicts, "tight_margin_clusters": len(tight),
                   "tight_margin_units": int(tight["综合试算件数"].sum()), "missing_shelf_units": int(shelf_missing["综合试算件数"].sum()),
                   "publication": "research_only_not_published"}
        # 按用户原21条清单汇总；同一簇只出现一次，不能再次与原组合相加。
        parent_summary = coverage.groupby("原始请求条目", sort=False, as_index=False).agg(
            综合试算件数=("综合试算件数", "sum"), 代表细分数=("CLUSTER_ID", lambda values: sum(bool(v) for v in values)),
            物理尺码=("PHYSICAL_SKU", lambda values: " / ".join(sorted(set(values) - {""}))))
        summary = selected.copy()
        summary["车型配置"] = summary.apply(lambda row: " ".join(str(row[key]) for key in ["MAKE", "MODEL", "版本", "结构"] if row[key]), axis=1)
        report = ["# 原组合追加指定车型：综合900件研究", "",
                  f"保留原{len(baseline)}个候选簇，追加{metrics['added_clusters']}个去重代表簇；共{len(selected)}个链接、{metrics['selected_models']}个车型、{metrics['physical_skus']}个物理尺码，综合{budget}件。未发布正式output或NAS。", "",
                  "## 口径与分配方法", "",
                  config["scope_note"], "", config["allocation_note"], "", config["coverage_note"], "",
                  f"- 21条原始请求拆为{len(coverage)}个细分，已匹配可用代表{len(requested)}个；与原组合重合{metrics['overlap_with_baseline']}个，只计一次。保底合计{metrics['reserved_units']}件，其余{budget - metrics['reserved_units']}件按近期销量分配。",
                  "- 2020–2025年度销量估值作为共同分配权重；2010–2025及生命周期已知销量仅用于零近期销量细分的代表筛选，未伪造老款的近期需求，也未与近期销量混权。",
                  f"- 普通指定对象以{config['default_min_fitment_year']}年及以后源适配为候选；Bronco从2021、Challenger从2008开始，Corvette按指定代际年份。均是本轮可调范围，未自动覆盖所有历史年代。",
                  f"- 扩展范围内近期销量估值{denominator:,.0f}，入选占{coverage_rate:.2%}。若{budget}件表示整个扩展范围需求，入选的近期销量比例只对应{budget * coverage_rate:.1f}件；当前{budget}件是集中配额并含试销保底，不是自然需求预测。",
                  "- 原24簇按相同方法从当前上游output重建；比较的是原800配额与本轮900配额，不从历史artifacts作为默认数据输入。保留车型/版本/结构/SHAPE/尺码差异，不启用灰区升码。", "",
                  "## 指定21条车型清单汇总", "",
                  *base.markdown_table(parent_summary, ["原始请求条目", "综合试算件数", "代表细分数", "物理尺码"]), "",
                  "以上包含原组合已有的Model Y、Model 3，不能与原组合总量重复相加。其余原组合车型的配额见完整组合。", "",
                  "## 指定细分的实际代表与年份", "",
                  *base.markdown_table(coverage, ["指定细分", "版本", "结构", "适配年份", "PHYSICAL_SKU", "综合试算件数", "代表选择依据"]), "",
                  "- Bronco、Wrangler两门/四门分别匹配版本字段，Bronco Sport不在指定Bronco内。",
                  "- Corvette C3和C8分别选代表，C4–C7逐代选择，不假定同尺码即同代际版型。C6/C7源数据普通版年份不完整，实际选中版本不能写成全系。",
                  f"- Corvette代际映射按库内gen3–gen8，并参考[雪佛兰官方代际时间线]({config['corvette_generation_source']})。",
                  "- Outback 2020–2025 Wilderness仍质量暂缓，本轮代表为其他可用记录；新款缺口不靠旧款替代声明。",
                  "- Tesla Model Y未从2020–2024普通Crossover自动延伸到2025–2026 Performance SUV；MINI Cooper未混入其他MODEL。", "",
                  "## 完整900件组合", "",
                  *base.markdown_table(summary, ["建议顺序", "车型配置", "适配年份", "PHYSICAL_SKU", "组合来源", "指定试销保底件数", "销量权重分配件数", "综合试算件数"]), "",
                  "## 物理尺码备货", "",
                  *base.markdown_table(stock, list(stock.columns)), "",
                  f"- 最小长度余量小于50mm的{len(tight)}个链接共{metrics['tight_margin_units']}件，先试套；当前店铺货架未登记匹配尺码的配额{metrics['missing_shelf_units']}件，先确认目标店铺与实物库存。两类可能重叠。",
                  "- 两门Wrangler等车型可能有较大长度余量，须关注轮廓与松量；相同物理尺码不能代替实物验证。", "",
                  "## 保底假设比较", "", *base.markdown_table(scenarios, list(scenarios.columns)), "",
                  "## 质量和可追溯性", "",
                  "原有Nissan Rogue PHEV、Outback Wilderness、Forester Wilderness暂缓不变。所有指定范围候选（包括暂缓、未选中版本）在追加候选细分表，入选源记录与原子销量依据在extra/压缩明细；质量待处理表保留提醒。",
                  f"原24簇保留、指定代表去重、源尺寸ID唯一、近期销量与原子对账、配额与物理尺码合计{budget}件均已校验；排名期跨簇身份冲突{conflicts}组。",
                  "研究ID不是持久LINK_ID，未生成全版本或TRIM通配声明。900为组合试算，未校准车罩购买率、广告效率、价格或订单转化率。", "",
                  "## 复算", "",
                  "在D1目录运行 `python src/expanded_listing_analysis.py`；规则为data/指定车型追加900.json，基线规则保留在data/非皮卡非W上架分析.json。每次用RunBatch新建不可变批次，只读自身data和上游output，不改流水线状态。" ]
        batch.output("REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        batch.finish(metrics)
        return batch.directory, selected, coverage, stock


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    directory, selected, coverage, stock = run()
    print(directory)
    print(coverage[["指定细分", "适配年份", "PHYSICAL_SKU", "综合试算件数"]].to_string(index=False))
    print(stock.to_string(index=False))
