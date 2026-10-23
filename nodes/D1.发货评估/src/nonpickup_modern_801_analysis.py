"""从A1压缩尺码表生成非皮卡、非老车、排除指定车型的801件研究方案。"""
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

CONFIG_PATH = PROJECT / "data" / "非皮卡非老车801上架分析.json"
COMPRESSED = REPO / "nodes" / "A1.压缩尺寸信息" / "output" / "US" / "压缩尺码表.csv"
SIZE_RULES = REPO / "nodes" / "A0.尺码计算" / "output" / "US" / "尺码规则.json"


def read_compressed_csv(path: Path) -> pd.DataFrame:
    """Read A1 output without coercing CODE business identifiers to numbers."""
    return pd.read_csv(path, keep_default_na=False, dtype={"CODE": str})


def year_bounds(value: object) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", str(value).strip())
    if not match:
        raise ValueError(f"无法解析年份: {value}")
    start, end = int(match[1]), int(match[2] or match[1])
    if end < start:
        raise ValueError(f"年份倒序: {value}")
    return start, end


def largest_remainder(weights, budget: int) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    if budget <= 0 or len(weights) == 0 or (weights < 0).any() or not np.isfinite(weights).all() or weights.sum() <= 0:
        raise ValueError("预算和权重不合法")
    exact = budget * weights / weights.sum()
    result = np.floor(exact).astype(int)
    order = np.argsort(-(exact - result), kind="stable")
    result[order[:budget - int(result.sum())]] += 1
    return result


def exclusion_mask(frame: pd.DataFrame, rule: dict) -> pd.Series:
    mask = frame["MAKE"].str.casefold().eq(rule["MAKE"].casefold()) & frame["MODEL"].str.casefold().eq(rule["MODEL"].casefold())
    if rule.get("VERSION_CONTAINS"):
        mask &= frame["VERSION"].str.casefold().str.contains(rule["VERSION_CONTAINS"].casefold(), regex=False)
    return mask


def size_catalog(payload: dict) -> pd.DataFrame:
    records = []
    for rule in payload["rules"]:
        if not str(rule.get("长上限", "")).strip():
            continue
        records.append({"BACKSIZE": rule["尺码"], "尺码池": rule["尺码池"], "长上限": float(rule["长上限"])})
    result = pd.DataFrame(records).drop_duplicates()
    ambiguous = result.groupby("BACKSIZE")[["尺码池", "长上限"]].nunique()
    if (ambiguous > 1).any(axis=None):
        raise ValueError("尺码规则中同名尺码存在不同尺码池或长度上限")
    result = result.drop_duplicates("BACKSIZE").sort_values(["尺码池", "长上限", "BACKSIZE"])
    result["尺码序"] = result.groupby("尺码池").cumcount()
    return result


def prepare(source: pd.DataFrame, config: dict, rules: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = source.copy()
    required = {"CODE", "MAKE", "MODEL", "YEAR", "VERSION", "CONST", "BACKSIZE", "尺码销量总和",
                "最大长-MM", "最小长-MM", "最大宽-MM", "最小宽-MM", "最大高-MM", "最小高-MM"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"压缩尺码表缺字段: {sorted(missing)}")
    # CODE is a compressed business key and is not row-unique (different bodies can share it).
    frame.insert(0, "源行ID", [f"A1-US-{number:04d}" for number in range(1, len(frame) + 1)])
    numeric = ["尺码销量总和", "最大长-MM", "最小长-MM", "最大宽-MM", "最小宽-MM", "最大高-MM", "最小高-MM"]
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="raise")
    bounds = frame["YEAR"].map(year_bounds)
    frame["源起始年"] = bounds.map(lambda x: x[0])
    frame["源结束年"] = bounds.map(lambda x: x[1])
    frame["建议起始年"] = frame["源起始年"].clip(lower=config["min_fitment_year"])
    frame["建议结束年"] = frame["源结束年"].clip(upper=config["max_fitment_year"])
    frame["范围判定"] = "范围内"
    frame.loc[frame["源结束年"].lt(config["min_fitment_year"]), "范围判定"] = "排除老车"
    old_size = pd.Series(False, index=frame.index)
    for prefix in config["exclude_size_prefixes"]:
        old_size |= frame["BACKSIZE"].str.startswith(prefix)
    frame.loc[old_size, "范围判定"] = "排除老车尺码系列"
    # This source is the non-pickup table; guard against accidental pickup rows anyway.
    pickup = frame["CONST"].str.casefold().eq("pickup") | frame["BACKSIZE"].str.startswith("PK-")
    frame.loc[pickup, "范围判定"] = "排除皮卡"
    matched = []
    for rule in config["excluded_models"]:
        hit = exclusion_mask(frame, rule)
        frame.loc[hit, "范围判定"] = "排除指定车型"
        matched.append({"排除条目": rule["label"], "命中压缩记录数": int(hit.sum()), "命中销量权重": float(frame.loc[hit, "尺码销量总和"].sum())})
    catalog = size_catalog(rules)
    frame = frame.merge(catalog, on="BACKSIZE", how="left", validate="many_to_one")
    frame.loc[frame["尺码池"].isna(), "范围判定"] = "排除未知尺码"
    return frame, pd.DataFrame(matched)


def apply_gray_matching(frame: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    result = frame.copy()
    if "源行ID" not in result:
        result["源行ID"] = [f"ROW-{number:04d}" for number in range(1, len(result) + 1)]
    result["供货尺码"] = result["BACKSIZE"]
    result["灰度组ID"] = ""
    result["灰度调整"] = False
    result["灰度说明"] = "保持原尺码"
    policy = config["gray_match"]
    audits = []
    eligible = result[result["范围判定"].eq("范围内")].copy()
    for identity, group in eligible.groupby(policy["identity_keys"], sort=True, dropna=False):
        if group["BACKSIZE"].nunique() < 2 or group["尺码池"].nunique() != 1:
            continue
        ordered = group.sort_values(["建议起始年", "建议结束年", "尺码序", "CODE"])
        components, current = [], []
        for idx, row in ordered.iterrows():
            if not current or row["建议起始年"] <= max(result.loc[current, "建议结束年"]) + policy["max_year_gap"]:
                current.append(idx)
            else:
                components.append(current); current = [idx]
        if current:
            components.append(current)
        for indices in components:
            part = result.loc[indices]
            if part["BACKSIZE"].nunique() < 2:
                continue
            spreads = {
                "length": part["最大长-MM"].max() - part["最小长-MM"].min(),
                "width": part["最大宽-MM"].max() - part["最小宽-MM"].min(),
                "height": part["最大高-MM"].max() - part["最小高-MM"].min(),
            }
            status, reason = "拒绝", ""
            size_orders = sorted(part["尺码序"].unique())
            if policy["adjacent_sizes_only"] and (max(size_orders) - min(size_orders) + 1 != len(size_orders)):
                reason = "跨非相邻尺码"
            elif any(spreads[k] > policy["max_group_spread_mm"][k] for k in spreads):
                reason = "整组长宽高跨度超阈值"
            else:
                target = part.sort_values(["长上限", "BACKSIZE"]).iloc[-1]
                margin = target["长上限"] - part["最大长-MM"].max()
                limits = policy["target_length_margin_mm"]
                if not (limits["min"] <= margin < limits["max_exclusive"]):
                    reason = f"目标长度余量{margin:g}mm不合格"
                else:
                    status, reason = "通过", "同车型相邻年代尺寸接近，统一较大尺码"
                    gid = "GRAY-" + hashlib.sha256("|".join(map(str, identity)).encode("utf-8")).hexdigest()[:10].upper()
                    result.loc[indices, "供货尺码"] = target["BACKSIZE"]
                    result.loc[indices, "灰度组ID"] = gid
                    result.loc[indices, "灰度调整"] = result.loc[indices, "BACKSIZE"].ne(target["BACKSIZE"])
                    result.loc[indices, "灰度说明"] = reason
            audits.append({**dict(zip(policy["identity_keys"], identity)), "源行ID": "/".join(part["源行ID"]), "源CODE": "/".join(map(str, part["CODE"])),
                           "源尺码": "/".join(sorted(part["BACKSIZE"].unique())), "判定": status, "原因": reason,
                           "长度跨度mm": spreads["length"], "宽度跨度mm": spreads["width"], "高度跨度mm": spreads["height"]})
    return result, pd.DataFrame(audits)


def build_portfolio(frame: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    scope = frame[frame["范围判定"].eq("范围内")].copy()
    keys = ["MAKE", "MODEL", "VERSION", "CONST", "供货尺码"]
    records = []
    for identity, group in scope.groupby(keys, sort=True, dropna=False):
        years = sorted({year for row in group.itertuples() for year in range(row.建议起始年, row.建议结束年 + 1)})
        records.append({**dict(zip(keys, identity)), "源压缩记录数": len(group), "源行ID": "/".join(group["源行ID"]), "源CODE": "/".join(map(str, sorted(group["CODE"]))),
                        "适配年份": f"{min(years)}-{max(years)}", "销量权重": group["尺码销量总和"].sum(),
                        "灰度调整记录数": int(group["灰度调整"].sum()), "最小目标长度余量mm": group["长上限"].max() - group["最大长-MM"].max()})
    candidates = pd.DataFrame(records).sort_values(["销量权重", "MAKE", "MODEL"], ascending=[False, True, True]).reset_index(drop=True)
    selected = candidates.head(config["portfolio_cluster_count"]).copy()
    if len(selected) < config["portfolio_cluster_count"]:
        raise ValueError("可选聚类少于目标链接数")
    selected["建议发货件数"] = largest_remainder(selected["销量权重"], config["shipment_budget"])
    selected["建议顺序"] = range(1, len(selected) + 1)
    return candidates, selected


def run(config_path: Path = CONFIG_PATH):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    description = "nonpickup-modern-801-gray-research"
    with RunBatch.create(PROJECT / "artifacts", description, data_dir=PROJECT / "data") as batch:
        source_path = batch.input(COMPRESSED)
        rules_path = batch.input(SIZE_RULES)
        frame, exclusions = prepare(read_compressed_csv(source_path), config,
                                    json.loads(rules_path.read_text(encoding="utf-8")))
        frame, gray_audit = apply_gray_matching(frame, config)
        candidates, selected = build_portfolio(frame, config)
        stock = selected.groupby("供货尺码", as_index=False).agg(建议发货件数=("建议发货件数", "sum"), 建议链接数=("供货尺码", "size"))
        stock = stock.sort_values(["建议发货件数", "供货尺码"], ascending=[False, True])
        for name, table in [("推荐上架与801件分配.csv", selected), ("物理尺码备货汇总.csv", stock),
                            ("全部候选聚类.csv", candidates), ("灰度匹配审核.csv", gray_audit), ("指定车型排除核对.csv", exclusions)]:
            table.to_csv(batch.output(name), index=False, encoding="utf-8-sig")
        frame.to_csv(batch.extra("压缩源范围与灰度归属.csv"), index=False, encoding="utf-8-sig", compression="gzip")
        excluded_selected = []
        for rule in config["excluded_models"]:
            if exclusion_mask(selected.rename(columns={"VERSION": "VERSION"}), rule).any():
                excluded_selected.append(rule["label"])
        if excluded_selected:
            raise ValueError(f"入选组合仍含指定排除车型: {excluded_selected}")
        if int(selected["建议发货件数"].sum()) != config["shipment_budget"] or int(stock["建议发货件数"].sum()) != config["shipment_budget"]:
            raise ValueError("801件分配未守恒")
        if frame.loc[frame["范围判定"].eq("范围内"), "建议结束年"].lt(config["min_fitment_year"]).any():
            raise ValueError("范围内仍含老车")
        metrics = {"budget": config["shipment_budget"], "selected_clusters": len(selected), "candidate_clusters": len(candidates),
                   "source_rows": len(frame), "scope_counts": frame["范围判定"].value_counts().to_dict(),
                   "gray_groups_passed": int(gray_audit["判定"].eq("通过").sum()) if len(gray_audit) else 0,
                   "gray_adjusted_rows": int(frame["灰度调整"].sum()), "allocated_units": int(selected["建议发货件数"].sum()),
                   "excluded_entries_verified": len(config["excluded_models"]), "code_sha256": sha256(Path(__file__)),
                   "effective_config": config, "publication": "research_only_not_published"}
        lines = ["# 非皮卡、非老车801件推荐上架研究", "",
                 f"从A1 US压缩尺码表筛选，建议{len(selected)}个研究链接，合计{config['shipment_budget']}件；未发布正式output或NAS。", "",
                 "## 口径", "",
                 f"- 非老车：压缩记录结束年不早于{config['min_fitment_year']}，并排除{'、'.join(config['exclude_size_prefixes'])}*老车/W尺码系列；建议适配年份裁为{config['min_fitment_year']}–{config['max_fitment_year']}，不把更早年份写入本轮链接。",
                 "- 排除指定清单中的车型与门数版本；Corvette C3/C8和C4-C7合计覆盖C3至C8，因此本轮排除全部Chevrolet Corvette。",
                 "- 候选销量权重直接使用压缩尺码表的“尺码销量总和”；取前24个聚类，按权重用最大余数法分配801件。这是配货试算，不是订单预测。",
                 f"- 灰度政策通过{metrics['gray_groups_passed']}组，实际调整{metrics['gray_adjusted_rows']}条压缩记录；仅同车型、版本、结构、连续年代、相邻尺码，且整组长宽高跨度各≤50mm时升到较大尺码。目标长度余量须为50–499mm。", "",
                 "## 推荐组合", "",
                 "| 顺序 | 车型 | 版本 | 结构 | 年份 | 供货尺码 | 灰度调整记录 | 销量权重 | 件数 |",
                 "|---:|---|---|---|---|---|---:|---:|---:|"]
        for row in selected.itertuples():
            lines.append(f"| {row.建议顺序} | {row.MAKE} {row.MODEL} | {row.VERSION} | {row.CONST} | {row.适配年份} | {row.供货尺码} | {row.灰度调整记录数} | {row.销量权重:g} | {row.建议发货件数} |")
        lines += ["", "## 校验", "", f"- 推荐表与尺码汇总均合计{config['shipment_budget']}件。",
                  f"- {len(config['excluded_models'])}条排除规则逐项核对，入选结果命中0条；明细见“指定车型排除核对.csv”。",
                  "- 灰度通过与拒绝原因完整保留在“灰度匹配审核.csv”；源记录及最终供货尺码保留在extra压缩明细。",
                  "- 本批次为研究交付，不修改D1稳定output、流水线状态或NAS。"]
        batch.output("REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        batch.finish(metrics)
        return batch.directory, selected, stock, gray_audit, exclusions


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    directory, selected, stock, gray, exclusions = run()
    print(directory)
    print(selected[["建议顺序", "MAKE", "MODEL", "VERSION", "CONST", "适配年份", "供货尺码", "建议发货件数"]].to_string(index=False))
    print(stock.to_string(index=False))
