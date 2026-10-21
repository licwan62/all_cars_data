"""审核既成皮卡发货表中的链接命名与车型事实。

本流程不改写 ``data/发货单明细.xlsx``，也不重新决定既成发货 SKU；它只验证
``上架明细`` 中的 CUSUMER_NAME、SIZE_NAME、适配车型，并按 data/ 规则把车型与年份
拆成独立字段后写入不可变批次。

本项目是 pipeline.json 登记的节点 ``link-analysis-pickup``：运行只写 run.json 与 output/，
manifest 由 ``scripts/publish_release.py`` 生成，对外发布由 ``scripts/publish_public.py`` 完成。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_DIR.parents[2]
WORKBOOK = PROJECT_DIR / "data" / "发货单明细.xlsx"
US_FULL_TABLE = REPO_ROOT / "nodes" / "A0.尺码计算" / "output" / "US" / "全量" / "全量表.csv"
sys.path.insert(0, str(REPO_ROOT / "lib"))

from artifact_batch import RunBatch, sha256  # noqa: E402


YEAR_RE = re.compile(
    r"(?<!\d)((?:19|20)\d{2}(?:-(?:19|20)\d{2})?"
    r"(?:/(?:19|20)\d{2}(?:-(?:19|20)\d{2})?)*)"
)
BED_RE = re.compile(r"\b\d(?:\.\d+)?(?=')")
CAB_TERMS = (
    "Regular", "SuperCab", "SuperCrew", "CrewMax", "Access", "XtraCab",
    "King", "Mega", "Double", "Extended", "Crew", "Club", "Quad",
)


def load_physical_sku_mapping() -> dict[str, str]:
    """读取皮卡旧尺码到当前通用尺码的发布映射。"""
    path = PROJECT_DIR / "data" / "PHYSICAL_SKU映射.json"
    mapping = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("PHYSICAL_SKU 映射必须是非空对象")
    return {str(old): str(new) for old, new in mapping.items()}


def update_physical_sku(frame: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """仅改写交付尺码名；缺少映射时失败，避免混用新旧命名。"""
    result = frame.copy()
    source = result["PHYSICAL_SKU"].astype(str)
    missing = sorted(set(source) - set(mapping))
    if missing:
        raise ValueError(f"PHYSICAL_SKU 缺少最新尺码映射：{missing}")
    result["PHYSICAL_SKU"] = source.map(mapping)
    return result


def add_us_size_extremes(audit: pd.DataFrame, us_full_table: pd.DataFrame) -> pd.DataFrame:
    """按 US 全量表当前自动尺码，为审核行补充匹配车型集合的尺寸极值。"""
    required = {"自动尺码", "L-MM", "W-MM", "H-MM"}
    missing_columns = sorted(required - set(us_full_table.columns))
    if missing_columns:
        raise ValueError(f"US 全量表缺少尺码极值字段：{missing_columns}")
    source = us_full_table.loc[:, ["自动尺码", "L-MM", "W-MM", "H-MM"]].copy()
    for column in ("L-MM", "W-MM", "H-MM"):
        source[column] = pd.to_numeric(source[column], errors="coerce")
    extremes = source.groupby("自动尺码", as_index=True)[["L-MM", "W-MM", "H-MM"]].max()
    output = audit.copy()
    missing_skus = sorted(set(output["PHYSICAL_SKU"].astype(str)) - set(extremes.index.astype(str)))
    if missing_skus:
        raise ValueError(f"US 全量表找不到当前 PHYSICAL_SKU 的匹配车型：{missing_skus}")
    for source_column, output_column in (
        ("L-MM", "最长-MM"),
        ("W-MM", "最宽-MM"),
        ("H-MM", "最高-MM"),
    ):
        output[output_column] = output["PHYSICAL_SKU"].map(extremes[source_column]).astype("Int64")
        if output[output_column].isna().any():
            raise ValueError(f"US 全量表的 {output_column} 存在空值")
    return output


def year_text(value: object) -> str:
    match = YEAR_RE.search(str(value or ""))
    return match.group(1) if match else ""


def expand_years(value: object) -> set[int]:
    text = year_text(value)
    years: set[int] = set()
    for part in text.split("/") if text else []:
        start = int(part[:4])
        end = int(part[-4:])
        years.update(range(start, end + 1))
    return years


def model_text(value: object) -> str:
    text = str(value or "")
    match = YEAR_RE.search(text)
    return text[: match.start()].strip() if match else ""


def split_fitment(value: object) -> tuple[str, str]:
    """兼容旧工作簿的“车型 年份”，返回独立的车型与年份。"""
    return model_text(value), year_text(value)


def bed_lengths(value: object) -> set[float]:
    return {float(item) for item in BED_RE.findall(str(value or ""))}


def cab_terms(value: object) -> set[str]:
    return {term for term in CAB_TERMS if re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", str(value or ""))}


def source_candidates(detail: pd.DataFrame, row: pd.Series) -> pd.DataFrame:
    parts = [part.strip() for part in str(row["CUSUMER_NAME"]).split("|")]
    consumer_cabs = cab_terms(parts[1] if len(parts) > 1 else "")
    consumer_beds = bed_lengths(parts[2] if len(parts) > 2 else "")
    candidates = detail[
        (detail["PHYSICAL_SKU"].astype(str) == str(row["PHYSICAL_SKU"]))
        & (detail["MAKE_MODEL"].astype(str) == model_text(row["适配车型"]))
    ].copy()
    if consumer_cabs:
        candidates = candidates[
            candidates["CAB"].astype(str).map(lambda value: bool(cab_terms(value) & consumer_cabs))
        ]
    if consumer_beds:
        lengths = pd.to_numeric(candidates["BED_LENGTH"], errors="coerce")
        candidates = candidates[
            lengths.map(lambda value: any(abs(value - target) < 0.011 for target in consumer_beds))
        ]
    return candidates


def candidate_years(candidates: pd.DataFrame) -> set[int]:
    years: set[int] = set()
    for start, end in zip(
        pd.to_numeric(candidates["YEAR_START"], errors="coerce"),
        pd.to_numeric(candidates["YEAR_END"], errors="coerce"),
    ):
        if pd.notna(start) and pd.notna(end) and int(end) >= int(start):
            years.update(range(int(start), int(end) + 1))
    return years


def consumer_fitment(value: object) -> tuple[str, str]:
    """把消费者名称拆成带 CAB/BED 的适配车型与独立年份。"""
    parts = [part.strip() for part in str(value or "").split("|") if part.strip()]
    first = parts[0] if parts else ""
    return " | ".join([model_text(first), *parts[1:]]), year_text(first)


def sku_shipment_report(
    facts: pd.DataFrame,
    listing: pd.DataFrame,
    sku_mapping: pd.DataFrame,
) -> pd.DataFrame:
    """按已确认 SKU 发货事实输出，不读取或分摊 Cluster 数量。"""
    required_facts = {"SKU_NAME", "PHYSICAL_SKU", "发货数量", "发货日期"}
    missing = sorted(required_facts - set(facts.columns))
    if missing:
        raise ValueError(f"发货事实缺少字段：{missing}")
    facts = facts.copy()
    dates = facts["发货日期"].fillna("").astype(str)
    if not dates.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        raise ValueError("发货日期必须使用 YYYY-MM-DD，且不能为空")
    pd.to_datetime(dates, format="%Y-%m-%d", errors="raise")
    if facts.duplicated(["SKU_NAME", "发货日期"]).any():
        raise ValueError("发货事实 SKU_NAME 与发货日期组合必须唯一")
    if sku_mapping["SKU_NAME"].astype(str).duplicated().any() or sku_mapping["workbook_sku"].astype(str).duplicated().any():
        raise ValueError("SKU上架映射两端都必须唯一")
    listing_fields = listing[["SKU_NAME", "PHYSICAL_SKU", "CUSUMER_NAME"]].rename(columns={
        "SKU_NAME": "workbook_sku",
        "PHYSICAL_SKU": "listing_size",
    })
    report = facts.merge(sku_mapping, on="SKU_NAME", how="left", validate="many_to_one")
    report = report.merge(listing_fields, on="workbook_sku", how="left", validate="many_to_one")
    if report[["workbook_sku", "CUSUMER_NAME"]].isna().any().any():
        raise ValueError("发货事实存在未映射的 SKU_NAME")
    mismatched = report[report["PHYSICAL_SKU"].astype(str) != report["listing_size"].astype(str)]
    if not mismatched.empty:
        raise ValueError("发货事实尺码与上架明细不一致：" + ", ".join(mismatched["SKU_NAME"].astype(str)))
    split = report["CUSUMER_NAME"].map(consumer_fitment)
    report["适配车型"] = split.map(lambda item: item[0])
    report["适配年份"] = split.map(lambda item: item[1])
    quantities = pd.to_numeric(report["发货数量"], errors="raise")
    if quantities.isna().any() or (quantities % 1 != 0).any():
        raise ValueError("发货数量必须是正整数")
    report["发货数量"] = quantities.astype(int)
    if (report["发货数量"] <= 0).any():
        raise ValueError("发货事实只应包含正向发货记录")
    return report[["SKU_NAME", "PHYSICAL_SKU", "适配车型", "适配年份", "发货数量", "发货日期"]].sort_values(
        ["发货数量", "SKU_NAME", "发货日期"], ascending=[False, True, True]
    )


def audit_row(row: pd.Series, detail: pd.DataFrame, rules: dict[str, object] | None = None) -> dict[str, object]:
    rules = rules or {"fitment_vehicle_include_year": False}
    consumer = str(row["CUSUMER_NAME"]).strip()
    size_name = str(row["SIZE_NAME"]).strip()
    source_fitment = str(row["适配车型"]).strip()
    fitment_model, fitment_year = split_fitment(source_fitment)
    fitment = source_fitment if rules.get("fitment_vehicle_include_year", False) else fitment_model
    consumer_years = expand_years(consumer)
    size_years = expand_years(size_name)
    fitment_years = expand_years(fitment_year)
    parts = [part.strip() for part in consumer.split("|")]
    consumer_cabs = cab_terms(parts[1] if len(parts) > 1 else "")
    size_cabs = cab_terms(size_name)
    consumer_beds = bed_lengths(parts[2] if len(parts) > 2 else "")
    size_beds = bed_lengths(size_name)
    qualifiers = " | ".join(parts[3:]) if len(parts) > 3 else ""

    consumer_errors: list[str] = []
    size_errors: list[str] = []
    fitment_errors: list[str] = []
    if not consumer or len(parts) < 3 or not consumer_years:
        consumer_errors.append("名称结构或年份缺失")
    if not fitment_years.issubset(consumer_years):
        consumer_errors.append("适配年份超出消费者名称年份")
    if consumer_years and fitment_years and (
        min(consumer_years) != min(fitment_years) or max(consumer_years) != max(fitment_years)
    ):
        consumer_errors.append("消费者名称与适配车型的年份端点不一致")

    if not size_name or size_years != consumer_years:
        size_errors.append("尺码名称年份与消费者名称不一致")
    if consumer_beds != size_beds:
        size_errors.append("尺码名称货斗长度与消费者名称不一致")
    missing_cabs = sorted(consumer_cabs - size_cabs)
    if missing_cabs:
        size_errors.append(f"尺码名称缺少驾驶舱：{','.join(missing_cabs)}")
    if "Excludes" in qualifiers and "Excl" not in size_name:
        size_errors.append("尺码名称缺少排除条件")
    if "Included" in qualifiers and "Included" not in size_name:
        size_errors.append("尺码名称缺少包含条件")
    if "RHO & TRX" in qualifiers and not {"RHO", "TRX"}.issubset(set(re.findall(r"RHO|TRX", size_name))):
        size_errors.append("尺码名称缺少 RHO/TRX 条件")

    source_row = row.copy()
    source_row["适配车型"] = source_fitment
    candidates = source_candidates(detail, source_row)
    supported_years = candidate_years(candidates)
    if not fitment_model or not fitment_years:
        fitment_errors.append("适配车型或适配年份缺失")
    if not rules.get("fitment_vehicle_include_year", False) and YEAR_RE.search(fitment):
        fitment_errors.append("适配车型不应包含年份")
    if candidates.empty:
        fitment_errors.append("找不到同尺码、车型、驾驶舱、货斗的来源事实")
    unsupported = sorted(fitment_years - supported_years)
    if unsupported:
        fitment_errors.append("来源事实不支持年份：" + ",".join(map(str, unsupported)))

    errors = consumer_errors + size_errors + fitment_errors
    return {
        "SKU_NAME": row["SKU_NAME"],
        "PHYSICAL_SKU": row["PHYSICAL_SKU"],
        "CUSUMER_NAME": consumer,
        "SIZE_NAME": size_name,
        "原适配车型": source_fitment,
        "适配车型": fitment,
        "消费者名称校验": "通过" if not consumer_errors else "不通过",
        "尺码名称校验": "通过" if not size_errors else "不通过",
        "适配车型校验": "通过" if not fitment_errors else "不通过",
        "来源事实行数": len(candidates),
        "适配年份": fitment_year,
        "校验结论": "通过" if not errors else "不通过",
        "问题明细": "；".join(errors),
    }


def apply_listing_overrides(final: pd.DataFrame, rules: dict) -> pd.DataFrame:
    result = final.copy()
    for sku, fields in rules.get("listing_overrides", {}).items():
        mask = result["SKU_NAME"].eq(sku)
        if mask.sum() != 1:
            raise ValueError(f"上架字段例外未唯一命中 SKU：{sku}")
        for field, value in fields.items():
            if field not in {"CUSUMER_NAME", "SIZE_NAME"}:
                raise ValueError(f"不支持的上架例外字段：{field}")
            result.loc[mask, field] = value
    return result


def apply_gray_compatibility(listing: pd.DataFrame, dimensions: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """用当前尺寸事实校验用户逐条确认的跨尺码兼容，不改自动尺码或发货 SKU。"""
    result = listing.copy()
    for sku, adjustment in rules.get("gray_compatibility", {}).items():
        mask = result["SKU_NAME"].eq(sku)
        if mask.sum() != 1:
            raise ValueError(f"灰色兼容规则未唯一命中 SKU：{sku}")
        row = result.loc[mask].iloc[0]
        if row["PHYSICAL_SKU"] != adjustment["physical_sku"]:
            raise ValueError(f"灰色兼容实物尺码不一致：{sku}")
        ids = adjustment["dimension_ids"]
        facts = dimensions[dimensions["DIMENSION-ID"].isin(ids)]
        if len(facts) != len(ids) or set(facts["DIMENSION-ID"]) != set(ids):
            raise ValueError(f"灰色兼容尺寸事实缺失或重复：{sku}")
        old_years = expand_years(row["适配年份"])
        added_years = expand_years(adjustment["added_years"])
        final_years = expand_years(adjustment["final_years"])
        if old_years & added_years or old_years | added_years != final_years:
            raise ValueError(f"灰色兼容新增年份与最终年份不一致：{sku}")
        parts = row["CUSUMER_NAME"].split("|")
        expected_cabs, expected_beds = cab_terms(parts[1]), bed_lengths(parts[2])
        supported: set[int] = set()
        for _, fact in facts.iterrows():
            if f"{fact['MAKE']} {fact['MODEL']}" != row["适配车型"]:
                raise ValueError(f"灰色兼容车型不一致：{sku}")
            if not cab_terms(fact["CAB"]).issubset(expected_cabs) or float(fact["BED"]) not in expected_beds:
                raise ValueError(f"灰色兼容驾驶室或货斗不一致：{sku}")
            if (pd.notna(fact["版本"]) and str(fact["版本"]).strip()) or fact["自动尺码"] != adjustment["source_automatic_sku"]:
                raise ValueError(f"灰色兼容版本或来源自动尺码不一致：{sku}")
            clearance = adjustment["length_limit_mm"] - float(fact["L-MM"])
            if not 0 <= clearance < adjustment["max_clearance_mm_exclusive"]:
                raise ValueError(f"灰色兼容长度余量不符合规则：{sku}，{clearance}mm")
            supported.update(expand_years(fact["YEAR"]))
        if not added_years.issubset(supported):
            raise ValueError(f"灰色兼容来源事实不支持新增年份：{sku}")
        result.loc[mask, "适配年份"] = adjustment["final_years"]
        result.loc[mask, "CUSUMER_NAME"] = YEAR_RE.sub(adjustment["final_years"], row["CUSUMER_NAME"], count=1)
    return result


def listing_title(value: str, rules: dict, sku: str = "") -> str:
    """按展示规则格式化标题，保留来源年份、货斗和限定条件。"""
    parts = [part.strip() for part in value.split("|")]
    if len(parts) < 3:
        raise ValueError(f"标题缺少车型、驾驶室或货斗：{value}")
    formatting = rules["listing_title_format"]
    model, years = split_fitment(parts[0])
    if not model or not years:
        raise ValueError(f"标题缺少车型或年份：{value}")
    cabs = [cab.strip() for cab in re.split(r"[,/]", parts[1])]
    cab_text = formatting["cab_separator"].join(
        formatting["cab_names"][cab] for cab in cabs
    )
    bed_match = re.fullmatch(r"(\d+(?:\.\d+)?'(?:-\d+(?:\.\d+)?')?)\s+((?:.+ )?Bed)", parts[2])
    if not bed_match:
        raise ValueError(f"无法识别标题货斗：{parts[2]}")
    length, bed = bed_match.groups()
    omitted = rules.get("listing_title_omissions", {}).get(sku, [])
    if any(qualifier not in parts[3:] for qualifier in omitted):
        raise ValueError(f"标题省略规则未命中来源限定条件：{sku}")
    return formatting["field_separator"].join([
        formatting["vehicle_year_template"].format(model=model, years=years),
        cab_text,
        formatting["bed_template"].format(bed=bed, length=length),
        *[part for part in parts[3:] if part and part not in omitted],
    ])


def run(workbook: Path, *, publish: bool = True) -> tuple[Path, dict[str, object]]:
    batch = RunBatch.create(PROJECT_DIR / "artifacts", "pickup-link-audit", data_dir=PROJECT_DIR / "data")
    try:
        # data/ 内的工作簿由规则快照登记；只有外部工作簿才作为输入复制进批次。
        if not workbook.resolve().is_relative_to((PROJECT_DIR / "data").resolve()):
            workbook = batch.input(workbook, name="发货单明细.xlsx")
        us_full_table_path = batch.input(US_FULL_TABLE)
        final = pd.read_excel(workbook, sheet_name="上架明细").fillna("")
        detail = pd.read_excel(workbook, sheet_name="ref_cluster_detail").fillna("")
        clusters = pd.read_excel(workbook, sheet_name="ref_cluster").fillna("")
        us_full_table = pd.read_csv(us_full_table_path, encoding="utf-8-sig")
        shipment_facts = pd.read_csv(PROJECT_DIR / "data" / "发货事实.csv", encoding="utf-8-sig")
        sku_mapping = pd.read_csv(PROJECT_DIR / "data" / "SKU上架映射.csv", encoding="utf-8-sig")
        rules = json.loads((PROJECT_DIR / "data" / "链接字段规则.json").read_text(encoding="utf-8"))
        physical_sku_mapping = load_physical_sku_mapping()

        required = {"SKU_NAME", "PHYSICAL_SKU", "CUSUMER_NAME", "SIZE_NAME", "适配车型"}
        missing = sorted(required - set(final.columns))
        if missing:
            raise ValueError(f"上架明细缺少字段：{missing}")
        final = apply_listing_overrides(final, rules)

        audit = pd.DataFrame([audit_row(row, detail, rules) for _, row in final.iterrows()])
        duplicate_skus = final["SKU_NAME"].astype(str).duplicated(False)
        if duplicate_skus.any():
            duplicated = set(final.loc[duplicate_skus, "SKU_NAME"].astype(str))
            mask = audit["SKU_NAME"].astype(str).isin(duplicated)
            audit.loc[mask, "校验结论"] = "不通过"
            audit.loc[mask, "问题明细"] = audit.loc[mask, "问题明细"].map(
                lambda value: (str(value) + "；" if value else "") + "SKU_NAME 重复"
            )

        exact_fitments = final["适配车型"].astype(str).isin(clusters["FITMENT_SUMMARY"].astype(str))
        audit["聚类汇总适配车型精确命中"] = exact_fitments.map({True: "是", False: "否"})

        reconciliation = shipment_facts.groupby("PHYSICAL_SKU", as_index=False).agg(
            SKU数量=("SKU_NAME", "nunique"),
            发货数量=("发货数量", "sum"),
        )

        listing = audit[[
            "SKU_NAME", "PHYSICAL_SKU", "CUSUMER_NAME", "SIZE_NAME", "适配车型", "适配年份",
        ]].copy()
        sku_shipments = sku_shipment_report(shipment_facts, final, sku_mapping)
        # 工作簿保留既成聚类与发货事实；四张交付表只统一更新尺码命名。
        audit = update_physical_sku(audit, physical_sku_mapping)
        audit = add_us_size_extremes(audit, us_full_table)
        listing = update_physical_sku(listing, physical_sku_mapping)
        listing = apply_gray_compatibility(listing, us_full_table, rules)
        audit["调整后适配年份"] = listing["适配年份"]
        audit["兼容调整说明"] = audit["SKU_NAME"].map(
            lambda sku: rules.get("gray_compatibility", {}).get(sku, {}).get("reason", "")
        )
        listing = listing.rename(columns={"CUSUMER_NAME": rules["listing_title_field"]})
        unknown_omissions = set(rules.get("listing_title_omissions", {})) - set(listing["SKU_NAME"])
        if unknown_omissions:
            raise ValueError(f"标题省略规则未命中 SKU：{sorted(unknown_omissions)}")
        listing[rules["listing_title_field"]] = [
            listing_title(value, rules, sku)
            for value, sku in zip(listing[rules["listing_title_field"]], listing["SKU_NAME"])
        ]
        listing["SIZE_NAME"] = rules["listing_size_name_prefix"] + listing[rules["listing_title_field"]]
        reconciliation = update_physical_sku(reconciliation, physical_sku_mapping)
        sku_shipments = update_physical_sku(sku_shipments, physical_sku_mapping)
        sku_shipments = sku_shipments[rules["shipment_output_fields"]]
        audit_path = batch.output("链接字段审核.csv")
        listing_path = batch.output("上架链接明细.csv")
        recon_path = batch.output("发货分配核对.csv")
        sku_shipment_path = batch.output("SKU发货数量.csv")
        report_path = batch.output("链接分析报告.md")
        audit.to_csv(audit_path, index=False, encoding="utf-8-sig")
        listing.to_csv(listing_path, index=False, encoding="utf-8-sig")
        reconciliation.to_csv(recon_path, index=False, encoding="utf-8-sig")
        sku_shipments.to_csv(sku_shipment_path, index=False, encoding="utf-8-sig")

        failed = int((audit["校验结论"] != "通过").sum())
        exact_count = int(exact_fitments.sum())
        split_count = len(final) - exact_count
        input_total = int(pd.to_numeric(reconciliation["发货数量"], errors="coerce").fillna(0).sum())
        allocated_total = input_total
        diff_lines = ["| 尺码 | SKU 数量 | 发货数量 |", "|---|---:|---:|"]
        for _, item in reconciliation.iterrows():
            diff_lines.append(
                f"| {item['PHYSICAL_SKU']} | {int(item['SKU数量'])} | {int(item['发货数量'])} |"
            )
        report = [
            "# 皮卡链接字段审核", "",
            f"- 输入工作簿 SHA256：`{sha256(workbook)}`",
            f"- 上架明细：{len(final)} 行；唯一 SKU：{final['SKU_NAME'].nunique()} 个。",
            f"- 三字段全部通过：{len(final) - failed} 行；不通过：{failed} 行。",
            "- `适配车型` 已移除年份；原年份完整写入独立的 `适配年份` 字段。",
            "- `最长-MM`、`最宽-MM`、`最高-MM` 取 US 全量表中当前 `PHYSICAL_SKU` 匹配车型集合各维度的最大值。",
            f"- `适配车型` 精确命中聚类汇总：{exact_count} 行；其余 {split_count} 行已按同尺码、车型、驾驶舱、货斗和年份反查原子事实。",
            f"- SKU 发货数量：{len(sku_shipments)} 个确认 SKU，合计 {int(sku_shipments['发货数量'].sum())}；与 Cluster 无关。",
            "- 上架明细标题字段使用 `TITLE_NAME`；发货表只交付 `SKU_NAME`、`发货数量`、`发货日期`。",
            "- `TITLE_NAME`：年份括号紧贴车型；标准驾驶室名称用 `/` 组合；字段用空格分隔；货斗为 `Short Bed(5.5'-6.5')` 形式，类型与长度按来源保留。",
            "- `SIZE_NAME`：使用 `Custom Fit ` 加完整 `TITLE_NAME`，保留年份、驾驶室、货斗与限定条件。",
            "- 标题省略例外：普通 Silverado 1500 标题与展示名省略 Trail Boss 排除短语；原始审核事实和既成 SKU 保留，Trail Boss 专用 SKU 仍单独展示。",
            "- 灰色兼容：按 gray_compatibility 逐条校验当前尺寸事实、来源尺码和长度余量后补充上架年份；审核表保留原适配年份，并列出调整后适配年份与说明。",
            "- 发货日期来自 data/发货事实.csv，按 SKU 与日期唯一；同 SKU 可追加不同日期，禁止缺失或无效日期。",
            "", "## 校验口径", "",
            "- `CUSUMER_NAME`：结构完整；年份覆盖适配事实，且首尾年份与适配事实一致。允许仅填补中间年份缺口。",
            "- `SIZE_NAME`：年份、驾驶舱、货斗长度和包含/排除限定与 `CUSUMER_NAME` 一致。",
            "- `适配车型`：只保留品牌与车型，不包含年份。",
            "- `适配年份`：从既成适配事实拆出；同尺码、车型、驾驶舱和货斗的 `ref_cluster_detail` 必须支持全部年份。",
            "", "## 发货事实汇总", "",
            f"确认发货事实合计 {input_total}；按 SKU_NAME 直接读取，不做 Cluster 分摊。",
            "", *diff_lines, "",
        ]
        report_path.write_text("\n".join(report), encoding="utf-8")
        (batch.directory / "REPORT.md").write_text(
            "# 本批次规则与交付说明\n\n"
            "上架标题按 data/链接字段规则.json 输出为 TITLE_NAME；"
            "本批次更新标题展示规则：车型(年份)、标准 cab 名称用 / 组合、空格分隔、货斗名称(长度)。"
            "普通 Silverado 1500 的 Trail Boss 排除短语按 listing_title_omissions 省略；不改来源审核事实或既成 SKU。"
            "本批次按用户确认的 gray_compatibility 补齐 Silverado HD 的2015-2019年份，478mm余量小于500mm；自动尺码事实不变。"
            "发货表仅保留 SKU_NAME、发货数量、发货日期。\n"
            "两条上架链接的 DRW 排除说明由 listing_overrides 保留，应用后再校验。\n"
            "发货日期按 data/发货事实.csv 原值保留，不使用运行日期；"
            "同 SKU 不同日期分行保留，同日重复记录拒绝发布。\n\n"
            f"详细审核报告见 output/{report_path.name}；规则快照与来源见 run.json。\n",
            encoding="utf-8",
        )

        if failed:
            raise ValueError(f"链接字段校验失败：{failed} 行；详见 {audit_path}")
        record = batch.finish(
            {
                "rows": len(final),
                "field_validation_failed": failed,
                "shipment_input_total": input_total,
                "allocated_total": allocated_total,
                "allocation_difference": allocated_total - input_total,
            },
            publish_to=PROJECT_DIR / "output" if publish else None,
        )
        return batch.directory, record
    except Exception as error:
        batch.fail(error)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="审核皮卡既成发货表的链接字段")
    parser.add_argument("--workbook", type=Path, default=WORKBOOK)
    parser.add_argument("--no-publish", action="store_true", help="只生成 artifact，不更新稳定 output")
    args = parser.parse_args()
    directory, record = run(args.workbook, publish=not args.no_publish)
    print(f"artifact={directory}")
    print(f"rows={record['status']['rows']} failed={record['status']['field_validation_failed']}")
    print(
        "shipment="
        f"{record['status']['shipment_input_total']} allocated={record['status']['allocated_total']} "
        f"difference={record['status']['allocation_difference']}"
    )


if __name__ == "__main__":
    main()
