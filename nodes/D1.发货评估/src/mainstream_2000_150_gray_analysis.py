"""普通车池（排除W型车和皮卡）2000件、150 SKU灰度聚类研究。"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import pandas as pd
import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / "lib"))
sys.path.insert(0, str(PROJECT / "src"))
from artifact_batch import RunBatch, sha256  # noqa: E402
from nonpickup_modern_801_analysis import (  # noqa: E402
    apply_gray_matching,
    prepare as prepare_base,
    read_compressed_csv,
)

CONFIG_PATH = PROJECT / "data" / "普通车2000件150SKU灰度聚类.json"
COMPRESSED = REPO / "nodes" / "A1.压缩尺寸信息" / "output" / "US" / "压缩尺码表.csv"
SIZE_RULES = REPO / "nodes" / "A0.尺码计算" / "output" / "US" / "尺码规则.json"


def capped_largest_remainder(weights, budget: int, cap: int) -> np.ndarray:
    """按权重比例分配整数，封顶后把余量重新分给未封顶项。"""
    weights = np.asarray(weights, dtype=float)
    if budget <= 0 or cap <= 0 or len(weights) == 0 or (weights < 0).any() or not np.isfinite(weights).all():
        raise ValueError("预算、上限或权重不合法")
    if budget > len(weights) * cap:
        raise ValueError("预算超过SKU数与单SKU上限可承载的总量")
    result = np.zeros(len(weights), dtype=int)
    remaining = int(budget)
    active = np.arange(len(weights))
    while remaining:
        available = cap - result[active]
        positive = available > 0
        active, available = active[positive], available[positive]
        if len(active) == 0:
            raise ValueError("无剩余容量")
        active_weights = weights[active]
        if active_weights.sum() <= 0:
            active_weights = np.ones(len(active))
        exact = remaining * active_weights / active_weights.sum()
        proposed = np.floor(exact).astype(int)
        proposed = np.minimum(proposed, available)
        if proposed.sum() == 0:
            order = np.argsort(-(exact - np.floor(exact)), kind="stable")
            proposed[order[:min(remaining, len(order))]] = 1
        result[active] += proposed
        remaining -= int(proposed.sum())
    return result


def add_market_potential(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    """按YEAR区间逐年计算当前市场留存权重。"""
    policy = config["market_potential"]
    evaluation_year = int(policy["evaluation_year"])
    full_weight_years = int(policy["full_weight_years"])
    half_life_years = float(policy["half_life_years"])
    if half_life_years <= 0 or full_weight_years < 0:
        raise ValueError("市场潜力参数不合法")

    def interval_factor(value: object) -> float:
        match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", str(value).strip())
        if not match:
            raise ValueError(f"YEAR格式不合法: {value!r}")
        start = int(match.group(1))
        end = min(int(match.group(2) or start), evaluation_year)
        if start > end:
            raise ValueError(f"YEAR超出评估年或区间倒置: {value!r}")
        ages = np.maximum(0, evaluation_year - np.arange(start, end + 1))
        weights = np.where(ages <= full_weight_years, 1.0,
                           2 ** (-(ages - full_weight_years) / half_life_years))
        return float(weights.mean())

    result = frame.copy()
    result["年份留存系数"] = result["YEAR"].map(interval_factor)
    result["市场潜力"] = result["尺码销量总和"] * result["年份留存系数"]
    return result


def prepare(source: pd.DataFrame, config: dict, rules: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_config = {
        "min_fitment_year": config["min_fitment_year"],
        "max_fitment_year": config["max_fitment_year"],
        "exclude_size_prefixes": [],
        "excluded_models": [],
    }
    frame, _ = prepare_base(source, base_config, rules)
    w_mask = pd.Series(False, index=frame.index)
    for prefix in config["w_size_prefixes"]:
        w_mask |= frame["BACKSIZE"].str.startswith(prefix)
    w_audit = []
    for rule in config["w_models"]:
        hit = frame["MAKE"].str.casefold().eq(rule["MAKE"].casefold()) & frame["MODEL"].str.casefold().eq(rule["MODEL"].casefold())
        w_mask |= hit
        w_audit.append({"排除条目": rule["label"], "命中压缩记录数": int(hit.sum()), "命中销量权重": float(frame.loc[hit, "尺码销量总和"].sum())})
    bel_air = (frame["MAKE"].eq("Chevrolet") & frame["MODEL"].eq("Bel Air") &
               frame["CONST"].ne("Wagon") &
               frame["源结束年"].le(config["bel_air_dedicated_max_year"]))
    w_mask |= bel_air
    w_audit.append({"排除条目": "Chevrolet Bel Air dedicated years", "命中压缩记录数": int(bel_air.sum()),
                    "命中销量权重": float(frame.loc[bel_air, "尺码销量总和"].sum())})
    frame.loc[frame["范围判定"].eq("范围内") & w_mask, "范围判定"] = "排除W型车"
    return frame, pd.DataFrame(w_audit)


def build_skus(frame: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    scope = frame[frame["范围判定"].eq("范围内")].copy()
    keys = config["sku_keys"]
    records = []
    for identity, group in scope.groupby(keys, sort=True, dropna=False):
        records.append({
            **dict(zip(keys, identity)),
            "销量权重": float(group["尺码销量总和"].sum()),
            "市场潜力": float(group["市场潜力"].sum()),
            "源压缩记录数": len(group),
            "源行ID": "/".join(group["源行ID"]),
            "源CODE": "/".join(map(str, sorted(group["CODE"]))),
            "版本": "/".join(sorted(set(group["VERSION"]) - {""})),
            "结构": "/".join(sorted(set(group["CONST"]) - {""})),
            "原尺码": "/".join(sorted(group["BACKSIZE"].unique())),
            "灰度调整记录数": int(group["灰度调整"].sum()),
        })
    candidates = pd.DataFrame(records).sort_values(
        ["市场潜力", "MAKE", "MODEL", "YEAR", "供货尺码"],
        ascending=[False, True, True, True, True],
    ).reset_index(drop=True)
    selected = candidates.head(config["portfolio_sku_count"]).copy()
    if len(selected) != config["portfolio_sku_count"]:
        raise ValueError("可选SKU少于目标数")
    selected["建议发货件数"] = capped_largest_remainder(
        selected["市场潜力"], config["shipment_budget"], config["max_units_per_sku"])
    selected.insert(0, "建议顺序", range(1, len(selected) + 1))
    return candidates, selected


def run(config_path: Path = CONFIG_PATH):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    with RunBatch.create(PROJECT / "artifacts", "mainstream-2000-150sku-gray-research", data_dir=PROJECT / "data") as batch:
        source_path = batch.input(COMPRESSED)
        rules_path = batch.input(SIZE_RULES)
        source = read_compressed_csv(source_path)
        frame, w_audit = prepare(source, config, json.loads(rules_path.read_text(encoding="utf-8")))
        frame, gray_audit = apply_gray_matching(frame, config)
        frame = add_market_potential(frame, config)
        candidates, selected = build_skus(frame, config)
        stock = selected.groupby("供货尺码", as_index=False).agg(
            建议发货件数=("建议发货件数", "sum"), 入选SKU数=("供货尺码", "size"),
            销量权重=("销量权重", "sum"), 市场潜力=("市场潜力", "sum"))
        stock = stock.sort_values(["建议发货件数", "供货尺码"], ascending=[False, True])
        outputs = [
            ("推荐SKU与2000件分配.csv", selected), ("物理尺码备货汇总.csv", stock),
            ("全部候选SKU.csv", candidates), ("灰度匹配审核.csv", gray_audit), ("W型车排除核对.csv", w_audit),
        ]
        for name, table in outputs:
            table.to_csv(batch.output(name), index=False, encoding="utf-8-sig")
        frame.to_csv(batch.extra("压缩源范围与灰度归属.csv"), index=False, encoding="utf-8-sig", compression="gzip")

        if selected.duplicated(config["sku_keys"]).any():
            raise ValueError("SKU组合键重复")
        if len(selected) != 150 or int(selected["建议发货件数"].sum()) != 2000:
            raise ValueError("150 SKU / 2000件约束未守恒")
        if selected["建议发货件数"].gt(config["max_units_per_sku"]).any():
            raise ValueError("单SKU发货件数超过上限")
        selected_ids = {item for value in selected["源行ID"] for item in value.split("/")}
        selected_source = frame[frame["源行ID"].isin(selected_ids)]
        if not selected_source["范围判定"].eq("范围内").all():
            raise ValueError("入选SKU含排除记录")

        passed = int(gray_audit["判定"].eq("通过").sum()) if len(gray_audit) else 0
        adjusted = int(frame["灰度调整"].sum())
        report = ["# 普通车2000件、150 SKU灰度聚类研究", "",
                  f"从A1 US压缩尺码表的普通车池中选出150个SKU，合计2000件；未发布到稳定output或NAS。", "",
                  "## 口径", "",
                  "- 排除皮卡（Pickup结构或PK-尺码）和W型车范围（4*尺码系列、Dodge Challenger、Tesla Model X、Bel Air专用年份）。",
                  "- SKU唯一粒度为MAKE + MODEL + 原YEAR年份区间 + 灰度后供货尺码；版本和结构作为核对字段保留，不进入SKU主键。",
                  f"- 市场潜力=尺码销量总和×YEAR区间平均留存系数；评估年{config['market_potential']['evaluation_year']}，车龄{config['market_potential']['full_weight_years']}年内权重1，之后按{config['market_potential']['half_life_years']}年半衰期衰减。",
                  f"- 候选按市场潜力降序取前150个；2000件按市场潜力分配，单SKU最多{config['max_units_per_sku']}件。",
                  f"- 灰度匹配启用：通过{passed}组，调整{adjusted}条压缩记录；策略与参考批次一致。", "",
                  "## 校验", "",
                  f"- 入选SKU：{len(selected)}；分配合计：{int(selected['建议发货件数'].sum())}件。",
                  f"- 单SKU最大分配：{int(selected['建议发货件数'].max())}件；封顶SKU：{int(selected['建议发货件数'].eq(config['max_units_per_sku']).sum())}个。",
                  f"- 候选SKU：{len(candidates)}；供货物理尺码：{selected['供货尺码'].nunique()}种。",
                  "- SKU主键无重复，入选源记录全部为范围内；本批次仅作研究交付。", "",
                  "## 推荐组合", "",
                  "| 顺序 | 车型 | 年份区间 | 供货尺码 | 销量权重 | 市场潜力 | 建议发货件数 |",
                  "|---:|---|---|---|---:|---:|---:|"]
        for row in selected.itertuples(index=False):
            report.append(
                f"| {row.建议顺序} | {row.MAKE} {row.MODEL} | {row.YEAR} | {row.供货尺码} | "
                f"{row.销量权重:g} | {row.市场潜力:.0f} | {row.建议发货件数} |"
            )
        batch.output("REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        metrics = {"budget": 2000, "selected_skus": len(selected), "candidate_skus": len(candidates),
                   "allocated_units": int(selected["建议发货件数"].sum()), "physical_skus": selected["供货尺码"].nunique(),
                   "max_units_per_sku": config["max_units_per_sku"],
                   "actual_max_units_per_sku": int(selected["建议发货件数"].max()),
                   "capped_skus": int(selected["建议发货件数"].eq(config["max_units_per_sku"]).sum()),
                   "scope_counts": frame["范围判定"].value_counts().to_dict(), "gray_groups_passed": passed,
                   "gray_adjusted_rows": adjusted, "code_sha256": sha256(Path(__file__)), "effective_config": config,
                   "publication": "research_only_not_published"}
        batch.finish(metrics)
        return batch.directory, selected, stock, gray_audit


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    directory, selected, stock, _ = run()
    print(directory)
    print(selected[["建议顺序", "MAKE", "MODEL", "YEAR", "供货尺码", "销量权重", "市场潜力", "建议发货件数"]].to_string(index=False))
    print(stock.to_string(index=False))
