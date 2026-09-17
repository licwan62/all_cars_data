import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
LEGACY_PATH = ROOT / "data" / "lagacy" / "07-FULL.csv"
CURRENT_PATH = ROOT / "public" / "全量数据.csv"
KEY_COLUMNS = ["MAKE", "MODEL", "版本", "结构", "YEAR", "CAB", "BED"]
UNAVAILABLE = {"无可用尺码", "数据不全", ""}


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def normalized_key(frame):
    parts = pd.DataFrame(
        {column: frame[column].map(clean_text).str.casefold() for column in KEY_COLUMNS}
    )
    return parts.agg("\x1f".join, axis=1)


def number(value):
    value = float(value)
    return int(value) if value.is_integer() else round(value, 1)


def json_records(frame):
    return json.loads(frame.to_json(orient="records", force_ascii=False))


def require_unique_keys(frame, label):
    duplicates = frame.loc[frame["_key"].duplicated(keep=False), KEY_COLUMNS]
    if not duplicates.empty:
        raise ValueError(f"{label}标准化键不唯一：{len(duplicates)} 条记录")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    legacy = pd.read_csv(LEGACY_PATH, encoding="utf-8-sig", dtype=str).fillna("")
    current = pd.read_csv(CURRENT_PATH, encoding="utf-8-sig", dtype=str).fillna("")

    legacy["_key"] = normalized_key(legacy)
    current["_key"] = normalized_key(current)
    require_unique_keys(legacy, "legacy")
    require_unique_keys(current, "current")

    legacy["旧尺码"] = legacy["确认尺码"].where(
        legacy["确认尺码"].map(clean_text).ne(""), legacy["自动尺码"]
    ).map(clean_text)
    legacy["旧长度余量"] = pd.to_numeric(legacy["长度余量"], errors="coerce")
    legacy["销量合计"] = pd.to_numeric(legacy["销量合计"], errors="coerce").fillna(0)

    current_view = current[["_key", "DIMENSION-ID", "自动尺码", "自动长度余量"]].rename(
        columns={"DIMENSION-ID": "新DIMENSION-ID", "自动尺码": "新尺码", "自动长度余量": "新长度余量"}
    )
    current_view["新尺码"] = current_view["新尺码"].map(clean_text)
    current_view["新长度余量"] = pd.to_numeric(current_view["新长度余量"], errors="coerce")

    result = legacy.merge(current_view, on="_key", how="outer", indicator=True, validate="one_to_one")
    if not result["_merge"].eq("both").all():
        added = int(result["_merge"].eq("right_only").sum())
        missing = int(result["_merge"].eq("left_only").sum())
        raise ValueError(f"标准化键未完全对齐：新增 {added}，缺失 {missing}")

    result["是否变化"] = result["旧尺码"] != result["新尺码"]
    result["变更路径"] = result["旧尺码"] + " → " + result["新尺码"]
    changed = result.loc[result["是否变化"]].copy()

    detail_columns = [
        "MAKE", "MODEL", "SUB-MODEL", "版本", "代际", "YEAR", "分类", "结构", "CAB", "BED",
        "L-MM", "W-MM", "H-MM", "销量合计", "DIMENSION-ID", "新DIMENSION-ID", "旧尺码", "新尺码",
        "旧长度余量", "新长度余量", "变更路径",
    ]
    changed_detail = changed[detail_columns].sort_values(
        ["销量合计", "MAKE", "MODEL", "YEAR"], ascending=[False, True, True, True], kind="stable"
    )
    changed_detail.to_csv(OUT / "车型映射变动明细.csv", index=False, encoding="utf-8-sig")

    transitions = (
        changed.groupby(["分类", "旧尺码", "新尺码"], dropna=False)
        .agg(记录数=("DIMENSION-ID", "size"), 销量合计=("销量合计", "sum"))
        .reset_index()
        .sort_values(["记录数", "销量合计"], ascending=False, kind="stable")
    )
    transitions["变更路径"] = transitions["旧尺码"] + " → " + transitions["新尺码"]
    transitions.to_csv(OUT / "尺码迁移汇总.csv", index=False, encoding="utf-8-sig")

    category_summary = result.groupby("分类", dropna=False).agg(
        全量记录数=("DIMENSION-ID", "size"), 变动记录数=("是否变化", "sum"), 全量销量=("销量合计", "sum")
    ).reset_index()
    changed_sales = changed.groupby("分类", dropna=False)["销量合计"].sum()
    category_summary["变动销量"] = category_summary["分类"].map(changed_sales).fillna(0)
    category_summary["记录变动率"] = category_summary["变动记录数"] / category_summary["全量记录数"]
    category_summary["销量影响率"] = category_summary["变动销量"] / category_summary["全量销量"]
    category_summary = category_summary.sort_values("变动记录数", ascending=False, kind="stable")
    category_summary.to_csv(OUT / "分类影响汇总.csv", index=False, encoding="utf-8-sig")

    old_unavailable = changed["旧尺码"].isin(UNAVAILABLE)
    new_unavailable = changed["新尺码"].isin(UNAVAILABLE)
    newly_matched = changed.loc[old_unavailable & ~new_unavailable]
    newly_unavailable = changed.loc[~old_unavailable & new_unavailable]
    size_to_size = changed.loc[~old_unavailable & ~new_unavailable]
    unavailable_to_unavailable = changed.loc[old_unavailable & new_unavailable]

    match_audit = pd.DataFrame([
        {"校验项": "legacy 记录数", "结果": len(legacy)},
        {"校验项": "public 发布版记录数", "结果": len(current)},
        {"校验项": "legacy 标准化键唯一数", "结果": legacy["_key"].nunique()},
        {"校验项": "public 发布版标准化键唯一数", "结果": current["_key"].nunique()},
        {"校验项": "成功对齐记录数", "结果": len(result)},
        {"校验项": "DIMENSION-ID 字符串直接相等数", "结果": int(legacy["DIMENSION-ID"].isin(set(current["DIMENSION-ID"])).sum())},
    ])
    match_audit.to_csv(OUT / "匹配键校验.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# `data/lagacy` 与 `public` 当前发布版车型尺码映射变动报告", "", "## 结论", "",
        f"- 旧表与现行表各 **{len(result):,}** 条；标准化车型键全量一对一对齐。",
        f"- 其中 **{len(changed):,}** 条最终尺码发生变化，记录变动率 **{len(changed)/len(result):.1%}**，涉及销量 **{number(changed['销量合计'].sum()):,}**。",
        f"- 从不可用转为可匹配 **{len(newly_matched):,}** 条；从可匹配转为不可用 **{len(newly_unavailable):,}** 条；可用尺码之间迁移 **{len(size_to_size):,}** 条；不可用状态之间变化 **{len(unavailable_to_unavailable):,}** 条。",
        "- 两份 `DIMENSION-ID` 的文本格式完全不同，不再直接用它连接；改用 `MAKE + MODEL + 版本 + 结构 + YEAR + CAB + BED` 清洗后的业务键。",
        "", "## 分类影响", "", "| 分类 | 全量记录 | 变动记录 | 记录变动率 | 变动销量 | 销量影响率 |", "|---|---:|---:|---:|---:|---:|",
    ]
    for row in category_summary.itertuples(index=False):
        lines.append(f"| {row.分类} | {int(row.全量记录数):,} | {int(row.变动记录数):,} | {row.记录变动率:.1%} | {number(row.变动销量):,} | {row.销量影响率:.1%} |")
    lines += ["", "## 主要迁移路径", "", "| 分类 | 旧尺码 | 新尺码 | 记录数 | 销量合计 |", "|---|---|---|---:|---:|"]
    for row in transitions.head(15).itertuples(index=False):
        lines.append(f"| {row.分类} | {row.旧尺码} | {row.新尺码} | {int(row.记录数):,} | {number(row.销量合计):,} |")
    lines += [
        "", "## 口径与校验", "", "- 旧映射取 `确认尺码`，空值时回退 `自动尺码`；新映射取 `public/全量数据.csv` 的 `自动尺码`。",
        "- 两份表的标准化键都是 4,354 个唯一值，交集也是 4,354；无未匹配、无重复键。",
        "- 原始 `DIMENSION-ID` 字符串直接相等为 0 条，证明不能将它作为跨版本连接键。",
        "- 输入：`data/lagacy/07-FULL.csv`、`public/全量数据.csv`。", "",
    ]
    (OUT / "车型映射变动报告.md").write_text("\n".join(lines), encoding="utf-8")

    payload = {
        "metrics": {"全量记录数": len(result), "变动记录数": len(changed), "记录变动率": len(changed) / len(result), "变动销量": float(changed["销量合计"].sum()), "新增可匹配": len(newly_matched), "新增不可用": len(newly_unavailable), "可用尺码迁移": len(size_to_size), "不可用状态变化": len(unavailable_to_unavailable)},
        "category": json_records(category_summary), "transitions": json_records(transitions), "details": json_records(changed_detail), "match_audit": json_records(match_audit),
    }
    (OUT / "report_data.json").write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print({"rows": len(result), "changed": len(changed), "changed_sales": number(changed["销量合计"].sum()), "newly_matched": len(newly_matched), "newly_unavailable": len(newly_unavailable), "size_to_size": len(size_to_size)})


if __name__ == "__main__":
    main()
