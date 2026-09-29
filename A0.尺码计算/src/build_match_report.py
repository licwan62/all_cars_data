#!/usr/bin/env python3
"""为 US/EU/RU 各生成一份 output/<国别>/尺码匹配报告.md，说明所用规则与大致匹配状况。

报告替代原先单独发布的 尺码匹配规则 CSV、店铺货架 CSV 和 尺码匹配报告 JSON：
  - 来源：全量表、规则、参数（US 另含货架配置与 TRIM 资料）的路径、行数和 SHA-256；
  - 匹配概况：车型数、已匹配/无可用尺码/数据不全的数量与占比，已匹配销量占比；
  - 尺码分布：按规则顺序列出各尺码车型数与销量占比；未匹配原因；
  - US：各店铺按发货尺码的分布、店铺货架映射，TRIM 回填与 TRIM适配器概况；
  - 尺码匹配规则：匹配步骤说明（计算量、候选池、上下限、余量容差、白名单、尺码池、店铺货架），数值取自当前参数与代码常量；
    随后附规则表全文（md 表格）。
报告内容只由输入决定（不写生成时间），同样输入重跑逐字节一致。
先在新的 artifacts/<批次>/output/ 生成，全部成功后原子更新 output/。
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

import data_layout
import output_layout as layout
import pandas_analysis as analysis

PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT / "output"
ARTIFACTS = PROJECT / "artifacts"
UNMATCHED = ("无可用尺码", "数据不全")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def content_sha256(path: Path) -> str:
    # 与 scripts/rules_snapshot.py 一致：CRLF→LF 归一，避免检出换行差异
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT).as_posix()
    except ValueError:
        return path.as_posix()


def cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def md_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    return lines


def percent(part: float, total: float) -> str:
    return f"{part / total:.1%}" if total else "—"


def shelf_rows(config_path: Path = data_layout.SHELF_CONFIG) -> list[list[str]]:
    """货架配置展开为 [店铺, 匹配尺码, 发货尺码]。"""
    stores = (yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}).get("店铺") or {}
    rows = []
    for store, body in stores.items():
        for item in (body or {}).get("尺码映射") or []:
            match, ship = item.get("匹配尺码"), item.get("发货尺码")
            if not match or not ship:
                raise ValueError(f"店铺 {store} 的尺码映射缺少匹配尺码或发货尺码：{item}")
            rows.append([str(store), str(match), str(ship)])
    if not rows:
        raise ValueError(f"{config_path} 没有店铺尺码映射")
    return rows


def region_sources(region: str) -> dict[str, tuple[Path, str]]:
    """区域 -> {说明: (文件, 规则尺码列)}；规则尺码列只对规则文件有意义。取自 data/当前规则.yaml。"""
    config = data_layout.current(region)
    sources = {"规则": (config.rules, config.size_column), "参数": (config.parameters, "")}
    if region == "US":
        sources["店铺货架配置"] = (data_layout.SHELF_CONFIG, "")
    return sources


def size_order(sizes: pd.Series, rule_sizes: list[str]) -> list[str]:
    present = list(dict.fromkeys(sizes))
    ordered = [size for size in dict.fromkeys(rule_sizes) if size in present]
    ordered += sorted(size for size in present if size not in ordered and size not in UNMATCHED)
    return ordered + [size for size in UNMATCHED if size in present]


def distribution(frame: pd.DataFrame, column: str, order: list[str]) -> list[list[object]]:
    sales = pd.to_numeric(frame[analysis.SIZE_GROUP_SALES], errors="coerce").fillna(0)
    total_rows, total_sales = len(frame), float(sales.sum())
    rows = []
    for size in order:
        mask = frame[column].eq(size)
        size_sales = float(sales[mask].sum())
        rows.append([size, f"{int(mask.sum()):,}", percent(mask.sum(), total_rows), f"{size_sales:,.0f}", percent(size_sales, total_sales)])
    return rows


def overview(frame: pd.DataFrame) -> list[str]:
    sales = pd.to_numeric(frame[analysis.SIZE_GROUP_SALES], errors="coerce").fillna(0)
    total, total_sales = len(frame), float(sales.sum())
    matched = ~frame["自动尺码"].isin(UNMATCHED) & frame["自动尺码"].ne("")
    rows = [["车型数（DIMENSION-ID）", f"{total:,}", "100.0%"],
            ["已匹配尺码", f"{int(matched.sum()):,}", percent(matched.sum(), total)]]
    rows += [[status, f"{int(frame['自动尺码'].eq(status).sum()):,}", percent(frame["自动尺码"].eq(status).sum(), total)]
             for status in UNMATCHED]
    rows.append(["销量合计", f"{total_sales:,.0f}", ""])
    rows.append(["已匹配车型销量", f"{float(sales[matched].sum()):,.0f}", percent(float(sales[matched].sum()), total_sales)])
    if total_sales == 0:
        rows.append(["说明", "本区域销量为零占位，销量占比不可用", ""])
    return md_table(["指标", "数值", "占比"], rows)


def unmatched_reasons(frame: pd.DataFrame) -> list[str]:
    subset = frame.loc[frame["自动尺码"].isin(UNMATCHED)]
    if subset.empty:
        return ["无。"]
    counts = subset.groupby(["自动尺码", "原因"]).size().reset_index(name="车型数")
    counts = counts.sort_values(["自动尺码", "车型数"], ascending=[True, False], kind="stable")
    return md_table(["状态", "原因", "车型数"], [[row.自动尺码, row.原因 or "（空）", f"{int(row.车型数):,}"] for row in counts.itertuples()])


def parameter_value(parameters: pd.DataFrame, name: str) -> str:
    found = parameters.loc[parameters["参数"].str.strip().eq(name), "值"]
    if found.empty:
        raise ValueError(f"参数表缺少 {name}")
    value = float(found.iloc[0])
    return f"{value:g}"


def number(value: float) -> str:
    return f"{value:g}"


def size_matcher_rules_text(region: str, rules: pd.DataFrame, parameters: pd.DataFrame) -> list[str]:
    """US/EU（SizeMatcher）的匹配步骤说明。"""
    tolerance = parameter_value(parameters, "余量长容差")
    offset = number(analysis.PANEL_OFFSET_MM)
    has = set(rules.columns)
    limits = [spec for spec in analysis.DEFAULT_LIMITS if spec.rule_column in has]
    lines = [
        "### 计算量",
        "",
        "- **长**：车型 `L-MM`，与规则的 `长上限` 比较。",
        f"- **插片指数**：`(前宽 + 后宽) / 4 − {offset}`；皮卡只看车头：`前宽 / 2 − {offset}`。"
        "其中 `前宽 = W-MM × 前宽系数`、`后宽 = W-MM × 后宽系数`，系数按车形取自 `03.车形分类核定/output/参考尺寸计算.csv`。",
        "- 长或插片指数缺失时结果为 **数据不全**。",
        "",
        "### 候选池",
        "",
        "- 按车型 `分类` 取规则中同分类的尺码作为候选池；规则 `分类` 写成 `跑车|三厢车` 表示该尺码同时属于两个分类。",
    ]
    if "CAB" in has or "版本" in has:
        lines.append("- 规则填写了 `CAB`/`版本` 时先在「分类+CAB+版本」池匹配，再退到「分类+版本」池，最后「分类」池；版本含 DRW 的统一按 DRW。")
    lines.append("- 三厢车若长超过三厢车所有尺码的最大长上限，改用跑车池匹配。")
    if "尺码池" in has:
        pools = "、".join(dict.fromkeys(value.strip() for value in rules["尺码池"] if value.strip()))
        lines.append(f"- `尺码池` 相同的尺码组成跨分类共享池（本规则表：{pools}）；本分类池无合格尺码时，才退到共享池再匹配一次。")
    if "车型白名单" in has:
        lines.append("- 填了 `车型白名单` 的规则不进入通用池，只对白名单车型生效：格式 `[仅] MAKE MODEL YYYY[-YYYY] [结构/结构]`，"
                     "车型年份需完全落在区间内、结构（如写）需命中；命中白名单的车型只在白名单尺码中匹配。")
    lines += ["", "### 选码", ""]
    upper = "、".join(f"`{spec.rule_column}`" for spec in limits)
    lines.append(f"1. 候选按 `长上限` 从小到大排序（相同时再比其他上限，最后按规则表顺序）。")
    if "插片指数下限" in has:
        lines.append("2. 规则填写了 `插片指数下限` 的尺码，只有车型插片指数 **大于** 下限时才进入候选（如宽头老爷车 4*-0 要求插片指数 > 120）。")
    else:
        lines.append("2. （本规则表未使用插片指数下限。）")
    lines.append(f"3. 依次检查：车型值不超过 {upper}（均为 ≤），且 `长上限 − 长` ≤ 余量长容差 **{tolerance} mm**；第一个满足的尺码即 `自动尺码`，"
                 "`自动长度余量 = 长上限 − 长`。")
    lines.append("4. 都不满足时记为 **无可用尺码**，并给出最接近的 `候选`、`原因` 与 `相差数值`：")
    lines.append("   - `超长`：长超过长上限；`插片指数超上限`：插片指数超过插片指数上限（取超出最多的一项）；")
    lines.append(f"   - `超余量`：尺码都装得下，但最小的也比车长出超过 {tolerance} mm，车衣过大。")
    if region == "US":
        lines += [
            "",
            "### 店铺发货尺码",
            "",
            "- 店铺全量表按 `data/US/店铺/货架.yaml`：先把候选池限定为该店铺的 `匹配尺码`，按上面同样的步骤选码，"
            "再把选中的匹配尺码换成对应的 `发货尺码`（多个匹配尺码可以发同一个发货尺码）。",
            "- 店铺货架中没有合适尺码的车型记为 **无可用尺码**，所以店铺的已匹配比例低于 US 全量表。",
        ]
    return lines


def ru_rules_text(parameters: pd.DataFrame) -> list[str]:
    tolerance = parameter_value(parameters, "余量长容差")
    return [
        "- 按车型 `分类` 取同分类规则；车型的长、宽、高都不超过规则的 `长_mm`、`宽_mm`、`高_mm` 时尺码合格。",
        f"- `长_mm − 长` 不得超过该尺码的 `余量长上限_mm`（规则表没有该列时统一用参数 余量长容差 {tolerance} mm）。",
        "- 合格尺码中取包络体积最小者（再按长、宽、高、亚马逊尺码排序），同时给出该行的 `OZON尺码` 与 `发货尺码`。",
        "- 无合格尺码时记为 **无可用尺码**，并给出最接近的候选与原因（超长/超宽/超高/超余量）；无同分类规则或尺寸缺失同样标注。",
    ]


def build_report(region: str, output_dir: Path) -> str:
    table_path = output_dir / layout.full_table(region)
    frame = read_csv(table_path)
    sources = region_sources(region)
    rule_path, size_column = sources["规则"]
    rules = read_csv(rule_path)
    if size_column not in rules.columns:
        raise ValueError(f"{rule_path.name} 缺少列 {size_column}")
    rule_sizes = [value for value in rules[size_column] if value]
    order = size_order(frame["自动尺码"], rule_sizes)

    lines = [f"# {region} 尺码匹配报告", "", "## 来源", ""]
    source_rows = [["全量表", f"output/{layout.full_table(region)}", f"{len(frame):,}", content_sha256(table_path)[:12]]]
    for label, (path, _) in sources.items():
        rows = f"{len(read_csv(path)):,}" if path.suffix.lower() == ".csv" else ""
        source_rows.append([label, relative(path), rows, content_sha256(path)[:12]])
    lines += md_table(["项目", "文件", "行数", "SHA-256（前 12 位）"], source_rows)
    lines += ["", "## 匹配概况", ""] + overview(frame)
    lines += ["", "## 尺码分布", ""]
    lines += md_table(["自动尺码", "车型数", "车型占比", "销量", "销量占比"], distribution(frame, "自动尺码", order))
    if region == "RU":
        ozon = frame["OZON尺码"].where(frame["OZON尺码"].ne(""), frame["自动尺码"])
        ship_order = [size for size in dict.fromkeys(rules["发货尺码"]) if size in set(frame["发货尺码"])]
        ship_order += [size for size in UNMATCHED if size in set(frame["发货尺码"])]
        lines += ["", "### 发货尺码分布", ""]
        lines += md_table(["发货尺码", "车型数", "车型占比", "销量", "销量占比"], distribution(frame, "发货尺码", ship_order))
        lines += ["", f"OZON 尺码共 {ozon.nunique()} 个取值。"]
    lines += ["", "## 未匹配原因", ""] + unmatched_reasons(frame)

    if region == "US":
        shelf = shelf_rows()
        lines += ["", "## 店铺", ""]
        store_summary = []
        for store in dict.fromkeys(row[0] for row in shelf):
            store_frame = read_csv(output_dir / layout.store_table(store))
            matched = ~store_frame["自动尺码"].isin(UNMATCHED) & store_frame["自动尺码"].ne("")
            ship_sizes = {row[2] for row in shelf if row[0] == store}
            store_summary.append([store, f"output/{layout.store_table(store)}", len(ship_sizes),
                                  f"{int(matched.sum()):,}", percent(matched.sum(), len(store_frame)),
                                  f"{int(store_frame['自动尺码'].eq('无可用尺码').sum()):,}"])
        lines += md_table(["店铺", "全量表", "发货尺码数", "已匹配", "占比", "无可用尺码"], store_summary)
        for store in dict.fromkeys(row[0] for row in shelf):
            store_frame = read_csv(output_dir / layout.store_table(store))
            ship_order = [row[2] for row in shelf if row[0] == store]
            lines += ["", f"### {store} 发货尺码分布", ""]
            lines += md_table(["发货尺码", "车型数", "车型占比", "销量", "销量占比"],
                              distribution(store_frame, "自动尺码", size_order(store_frame["自动尺码"], ship_order)))
        lines += ["", "### 店铺货架（匹配尺码 → 发货尺码）", ""]
        lines += md_table(["店铺", "匹配尺码", "发货尺码"], shelf)

        adapter = read_csv(output_dir / layout.TRIM_ADAPTER)
        with_trim = int(frame["TRIM"].ne("").sum())
        lines += ["", "## TRIM 匹配", ""]
        lines += md_table(["指标", "数值", "占比"], [
            ["全量表带 TRIM 的车型", f"{with_trim:,}", percent(with_trim, len(frame))],
            ["TRIM适配器行（Year+Make+Model）", f"{len(adapter):,}", ""],
            ["TRIM适配器中已匹配尺码的行", f"{int((~adapter['Size'].isin(UNMATCHED) & adapter['Size'].ne('')).sum()):,}",
             percent(int((~adapter["Size"].isin(UNMATCHED) & adapter["Size"].ne("")).sum()), len(adapter))],
        ])
        lines += ["", f"TRIM 资料：`{relative(data_layout.TRIM_DIR)}/`；适配器：`output/{layout.TRIM_ADAPTER}`。"]

    parameters_path, _ = sources["参数"]
    parameters = read_csv(parameters_path)
    lines += ["", "## 尺码规则", "",
              f"规则：`{relative(rule_path)}`；参数：`{relative(parameters_path)}`（当前版本由 `data/当前规则.yaml` 指定）。", ""]
    lines += ru_rules_text(parameters) if region == "RU" else size_matcher_rules_text(region, rules, parameters)
    lines += ["", f"### 规则表（{len(rules)} 条）", ""]
    lines += md_table(list(rules.columns), rules.values.tolist())
    lines += ["", "### 参数", ""]
    lines += md_table(list(parameters.columns), parameters.values.tolist())
    return "\n".join(lines) + "\n"


def next_artifact_dir() -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = [
        int(match.group(1))
        for path in ARTIFACTS.glob(f"{prefix}*")
        if (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))
    ]
    return ARTIFACTS / f"{prefix}{max(used, default=0) + 1:02d}_match-report"


def main() -> int:
    artifact = next_artifact_dir()
    staging = artifact.with_name(f".{artifact.name}.tmp")
    try:
        reports = {region: build_report(region, OUTPUT) for region in layout.REGIONS}
        for region, text in reports.items():
            target = staging / "output" / layout.match_report(region)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        os.replace(staging, artifact)
        for region in reports:
            name = layout.match_report(region)
            destination = OUTPUT / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_name(f".{destination.name}.tmp")
            shutil.copy2(artifact / "output" / name, temporary)
            os.replace(temporary, destination)
            print(f"{name}: {len(reports[region].splitlines())} 行")
        return 0
    except (OSError, ValueError, KeyError, yaml.YAMLError) as error:
        if staging.exists():
            shutil.rmtree(staging)
        print(f"生成尺码匹配报告失败：{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
