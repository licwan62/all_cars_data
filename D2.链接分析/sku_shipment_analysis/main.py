"""Analyze cluster-level SKU shipments and build listing details.

The public cluster CSVs are read-only inputs.  Edit the generated workbook's
`发货单` sheet and rerun this script with `--shipment <workbook>` to refresh.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd


SIZE_ALIASES = ["PHYSICAL_SIZE", "PHYSICAL_SKU", "逻辑尺码", "尺码", "SIZENAME"]
QTY_ALIASES = ["发货量", "SHIPMENT_QTY", "QUANTITY", "数量"]
CLUSTER_NAME_ALIASES = ["链接名称", "CONSUMER_NAME_OPTIMIZED", "CONSUMER_NAME"]
SALES_ALIASES = ["ESTIMATED_SALES", "销量合计", "预估销量 的总和"]

OUTPUT_COLUMN_NAMES = {
    "CLUSTER_ID": "聚类ID", "CONSUMER_NAME": "消费者名称", "MAKE": "品牌", "MODEL": "车型",
    "TRIM": "款型", "YEAR_COMPACT": "年份汇总", "YEAR_MIN": "最早年份", "YEAR_MAX": "最晚年份",
    "SOURCE_RECORD_COUNT": "源记录数", "ATOM_COUNT": "原子事实数",
    "L_MIN": "最小车长毫米", "L_MAX": "最大车长毫米", "L_SPREAD": "车长跨度毫米",
    "W_MIN": "最小车宽毫米", "W_MAX": "最大车宽毫米", "W_SPREAD": "车宽跨度毫米",
    "H_MIN": "最小车高毫米", "H_MAX": "最大车高毫米", "H_SPREAD": "车高跨度毫米",
    "LENGTH_MARGIN_MIN": "最小长度余量毫米", "LENGTH_MARGIN_MEDIAN": "长度余量中位数毫米",
    "DIFF_MEDIAN": "差值中位数", "ESTIMATED_SALES": "预估销量",
    "PHYSICAL_SKU_CONFLICT_ATOM_COUNT": "跨尺码冲突原子数", "MERGE_STATUS": "聚类状态",
    "PHYSICAL_SIZE": "发货逻辑尺码", "CLUSTER_SALES": "聚类销量", "SKU_SALES": "尺码总销量",
    "SALES_SHARE_IN_SKU": "尺码内销量占比", "SKU_NAME": "SKU名称", "SIZENAME": "尺码名称",
}


def chinese_output(frame: pd.DataFrame, *, physical_size_name: str | None = None) -> pd.DataFrame:
    """Rename exported columns to stable Chinese labels."""
    names = OUTPUT_COLUMN_NAMES.copy()
    if physical_size_name:
        names["PHYSICAL_SIZE"] = physical_size_name
    return frame.rename(columns=names)


def first_column(frame: pd.DataFrame, aliases: list[str], label: str) -> str:
    for name in aliases:
        if name in frame.columns:
            return name
    raise ValueError(f"缺少{label}字段；支持：{', '.join(aliases)}")


def parse_years(value: object) -> list[int]:
    years: list[int] = []
    for part in str(value or "").split("/"):
        match = re.fullmatch(r"\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*", part)
        if not match:
            continue
        start, end = int(match.group(1)), int(match.group(2) or match.group(1))
        if end >= start:
            years.extend(range(start, end + 1))
    return years


def compact_years(years: list[int]) -> str:
    ordered = sorted(set(years))
    if not ordered:
        return ""
    spans: list[tuple[int, int]] = []
    start = end = ordered[0]
    for year in ordered[1:]:
        if year == end + 1:
            end = year
        else:
            spans.append((start, end))
            start = end = year
    spans.append((start, end))
    return "/".join(str(a) if a == b else f"{a}-{b}" for a, b in spans)


def round_half_up(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def proportional_integer_allocation(weights: pd.Series, total: int) -> pd.Series:
    """Largest-remainder allocation that sums exactly to total."""
    if total < 0:
        raise ValueError("发货总量不能为负数")
    if weights.empty:
        return pd.Series(dtype="int64")
    clean = pd.to_numeric(weights, errors="coerce").fillna(0).clip(lower=0)
    if clean.sum() == 0:
        clean = pd.Series(1, index=clean.index, dtype=float)
    quota = clean / clean.sum() * total
    result = quota.apply(math.floor).astype(int)
    remaining = total - int(result.sum())
    order = pd.DataFrame({"remainder": quota - result, "weight": clean}, index=clean.index)
    order["key"] = order.index.astype(str)
    winners = order.sort_values(["remainder", "weight", "key"], ascending=[False, False, True]).index[:remaining]
    result.loc[winners] += 1
    return result


def load_clusters(cluster_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    summaries = sorted(cluster_dir.glob("*_cluster_summary.csv"))
    details = sorted(cluster_dir.glob("*_cluster_detail.csv"))
    if len(summaries) != 1 or len(details) != 1:
        raise ValueError(f"{cluster_dir} 必须各包含一份 *_cluster_summary.csv 和 *_cluster_detail.csv")
    summary = pd.read_csv(summaries[0], encoding="utf-8-sig")
    detail = pd.read_csv(details[0], encoding="utf-8-sig")
    size_col = first_column(summary, SIZE_ALIASES, "物理尺码")
    name_col = first_column(summary, CLUSTER_NAME_ALIASES, "消费者名称")
    sales_col = first_column(summary, SALES_ALIASES, "预估销量")
    required = ["CLUSTER_ID", size_col, name_col, sales_col]
    missing = [c for c in required if c not in summary.columns]
    if missing:
        raise ValueError(f"聚类主表缺少字段：{missing}")
    canonical = summary.copy()
    canonical["PHYSICAL_SIZE"] = canonical[size_col].astype(str).str.strip()
    canonical["CONSUMER_NAME"] = canonical[name_col].fillna("").astype(str).str.strip()
    canonical["CLUSTER_SALES"] = pd.to_numeric(canonical[sales_col], errors="coerce").fillna(0).clip(lower=0)
    if canonical["CLUSTER_ID"].duplicated().any():
        raise ValueError("聚类主表存在重复 CLUSTER_ID")
    if (canonical["PHYSICAL_SIZE"] == "").any():
        raise ValueError("聚类主表存在空 PHYSICAL_SIZE")
    return canonical, detail


def read_shipment(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path, encoding="utf-8-sig")
    else:
        frame = pd.read_excel(path, sheet_name="发货单")
    size_col = first_column(frame, SIZE_ALIASES, "物理尺码")
    qty_col = first_column(frame, QTY_ALIASES, "发货量")
    result = frame[[size_col, qty_col]].rename(columns={size_col: "PHYSICAL_SIZE", qty_col: "发货量"})
    result["PHYSICAL_SIZE"] = result["PHYSICAL_SIZE"].astype(str).str.strip()
    result["发货量"] = pd.to_numeric(result["发货量"], errors="raise")
    if result["PHYSICAL_SIZE"].duplicated().any():
        raise ValueError("发货单中 PHYSICAL_SIZE 重复")
    if (result["发货量"] < 0).any() or ((result["发货量"] % 1) != 0).any():
        raise ValueError("发货量必须是非负整数")
    result["发货量"] = result["发货量"].astype(int)
    return result


def example_shipment(summary: pd.DataFrame, total: int) -> pd.DataFrame:
    sales = summary.groupby("PHYSICAL_SIZE", sort=False)["CLUSTER_SALES"].sum()
    qty = proportional_integer_allocation(sales, total)
    return pd.DataFrame({"PHYSICAL_SIZE": sales.index, "发货量": qty.values})


def allocate(summary: pd.DataFrame, shipment: pd.DataFrame, pack_size: int) -> pd.DataFrame:
    if pack_size <= 0:
        raise ValueError("包装倍数必须大于 0")
    unknown = sorted(set(shipment["PHYSICAL_SIZE"]) - set(summary["PHYSICAL_SIZE"]))
    if unknown:
        raise ValueError(f"发货单包含聚类数据中不存在的 PHYSICAL_SIZE：{unknown}")
    result = summary.merge(shipment, on="PHYSICAL_SIZE", how="left")
    result["发货量"] = result["发货量"].fillna(0).astype(int)
    result["SKU_SALES"] = result.groupby("PHYSICAL_SIZE")["CLUSTER_SALES"].transform("sum")
    result["SALES_SHARE_IN_SKU"] = result["CLUSTER_SALES"] / result["SKU_SALES"].replace(0, pd.NA)
    result["SALES_SHARE_IN_SKU"] = result["SALES_SHARE_IN_SKU"].fillna(0.0)
    result["理论发货量"] = result["发货量"] * result["SALES_SHARE_IN_SKU"]
    result["基础发货量"] = (result["理论发货量"] // pack_size).astype(int) * pack_size
    result["分配余数"] = result["理论发货量"] - result["基础发货量"]
    result["行发货量"] = result["基础发货量"]
    for size, indexes in result.groupby("PHYSICAL_SIZE", sort=False).groups.items():
        idx = list(indexes)
        target = round_half_up(int(result.loc[idx[0], "发货量"]) / pack_size) * pack_size
        bonus_count = max(0, (target - int(result.loc[idx, "基础发货量"].sum())) // pack_size)
        rank = result.loc[idx].sort_values(
            ["分配余数", "CLUSTER_SALES", "CLUSTER_ID"], ascending=[False, False, True]
        )
        winners = rank.index[:bonus_count]
        result.loc[winners, "行发货量"] += pack_size
    result["分配差异"] = result.groupby("PHYSICAL_SIZE")["行发货量"].transform("sum") - result["发货量"]
    return result


def fitment_rows(detail: pd.DataFrame) -> pd.DataFrame:
    make_col = first_column(detail, ["MAKE_NORMALIZED", "MAKE"], "品牌")
    model_col = first_column(detail, ["MODEL_FAMILY", "MODEL"], "车型")
    rows: list[dict[str, str]] = []
    for (cid, make, model), group in detail.groupby(["CLUSTER_ID", make_col, model_col], dropna=False, sort=False):
        years = [year for value in group["YEAR"] for year in parse_years(value)] if "YEAR" in group else []
        model_name = " ".join(part for part in [str(make).strip(), str(model).strip()] if part and part != "nan")
        year_text = compact_years(years)
        rows.append({
            "CLUSTER_ID": cid, "FITMENT_MAKE": str(make).strip(), "FITMENT_MODEL": str(model).strip(),
            "MAKE_MODEL": model_name, "FITMENT_YEAR": year_text,
            "适配车型": f"{model_name} {year_text}".strip(),
        })
    return pd.DataFrame(rows)


def load_abbreviations(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def year_code(year_text: str, prefix: str = "Y") -> str:
    parts: list[str] = []
    for part in str(year_text or "").split("/"):
        match = re.fullmatch(r"\s*(\d{4})(?:-(\d{4}))?\s*", part)
        if not match:
            continue
        start = match.group(1)[-2:]
        end = match.group(2)[-2:] if match.group(2) else ""
        parts.append(start if not end else f"{start}-{end}")
    if not parts:
        raise ValueError(f"无法生成年份缩写：{year_text}")
    return prefix + "+".join(parts)


def bed_code(consumer_name: str, config: dict) -> str:
    values = re.findall(r"(\d+(?:\.\d+)?)'", str(consumer_name or ""))
    if not values:
        return ""
    multiplier = int(config.get("bed_decimal_multiplier", 10))
    codes = []
    for value in values:
        code = str(round(float(value) * multiplier))
        if code not in codes:
            codes.append(code)
    return config.get("bed_prefix", "B") + "-".join(codes)


def abbreviation(value: str, configured: dict[str, str], kind: str) -> str:
    """Return a configured token, or a deterministic ASCII token for new names."""
    if value in configured:
        return configured[value]
    token = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").upper()
    if not token:
        raise ValueError(f"无法为 {kind} 生成 SKU 缩写：{value}")
    return token


def sku_name(row: pd.Series, config: dict) -> str:
    make = str(row.get("MAKE", "")).strip()
    model = str(row.get("MODEL", "")).strip()
    make_map = config["make_abbreviations"]
    model_map = config["model_abbreviations"]
    tokens = [abbreviation(make, make_map, "MAKE"), abbreviation(model, model_map, "MODEL")]
    is_pickup = str(row.get("分类", "")).strip() == "皮卡" or bool(str(row.get("TRUCK_TYPE", "")).strip())
    if is_pickup:
        axle = str(row.get("AXLE_TYPE", "")).strip()
        axle_token = config.get("axle_abbreviations", {}).get(axle, "")
        if axle_token:
            tokens.append(axle_token)
        cab = str(row.get("CAB_GROUP", "")).strip()
        cab_token = config.get("cab_abbreviations", {}).get(cab, "")
        if cab_token:
            tokens.append(cab_token)
        bed_token = bed_code(str(row.get("CONSUMER_NAME", "")), config)
        if bed_token:
            tokens.append(bed_token)
    else:
        if config.get("non_pickup_include_cab", False):
            cab = str(row.get("CAB_GROUP", "")).strip()
            if cab in config.get("cab_abbreviations", {}):
                tokens.append(config["cab_abbreviations"][cab])
        if config.get("non_pickup_include_bed", False):
            bed_token = bed_code(str(row.get("CONSUMER_NAME", "")), config)
            if bed_token:
                tokens.append(bed_token)
    tokens.extend([
        year_code(str(row.get("CONSUMER_YEAR", row.get("FITMENT_YEAR", ""))), config.get("year_prefix", "Y")),
        str(row["PHYSICAL_SIZE"]).strip(),
    ])
    name = "_".join(token for token in tokens if token)
    return re.sub(r"[^A-Za-z0-9+./_-]+", "-", name.upper()).strip("_-")


def fixed_consumer_name(row: pd.Series, config: dict) -> str:
    """Build stable consumer-facing names, omitting structure for sedan/sports-car categories."""
    make_model = str(row.get("MAKE_MODEL", "")).strip()
    year_text = str(row.get("CONSUMER_YEAR", row.get("FITMENT_YEAR", ""))).strip()
    base = " ".join(part for part in [make_model, year_text] if part)
    parts = [base]
    is_pickup = str(row.get("分类", "")).strip() == "皮卡" or bool(str(row.get("TRUCK_TYPE", "")).strip())
    if is_pickup:
        source_name = str(row.get("CONSUMER_NAME", ""))
        source_parts = [value.strip() for value in source_name.split("|") if value.strip()]
        if len(source_parts) > 1:
            parts.extend(source_parts[1:])
        else:
            cab = str(row.get("CAB_GROUP", "")).strip()
            cab_display = config.get("cab_display", {}).get(cab, "")
            if cab_display:
                parts.append(cab_display)
            bed_match = re.search(r"(\d+(?:\.\d+)?'(?:-\d+(?:\.\d+)?')?\s+(?:Short|Standard|Long)?\s*Bed)", source_name, re.I)
            if bed_match:
                parts.append(re.sub(r"\s+", " ", bed_match.group(1)).strip())
    if not is_pickup:
        raw_structures = [part.strip() for part in str(row.get("结构", "")).split("/") if part.strip()]
        allowed_structures: list[str] = []
        for rule in config.get("non_pickup_structure_whitelist", []):
            checks = {
                "make": str(row.get("MAKE", "")).strip(),
                "model": str(row.get("MODEL", "")).strip(),
                "cluster_id": str(row.get("CLUSTER_ID", "")).strip(),
            }
            if all(not rule.get(key) or str(rule[key]).strip() == value for key, value in checks.items()):
                configured = rule.get("structures")
                allowed_structures = raw_structures if configured is None else [
                    value for value in raw_structures if value in configured
                ]
                break
        order = {name: i for i, name in enumerate(config.get("structure_order", []))}
        unique = sorted(set(allowed_structures), key=lambda name: (order.get(name, 999), name))
        display = config.get("structure_display", {})
        if unique:
            parts.append(" / ".join(display.get(name, name) for name in unique))
    return config.get("consumer_name_separator", " | ").join(part for part in parts if part)


def build_year_ownership(detail: pd.DataFrame) -> dict[tuple[str, str, int], dict[tuple[str, str], float | None]]:
    """Map each model-year atom to owners and their maximum known length."""
    make_col = first_column(detail, ["MAKE_NORMALIZED", "MAKE"], "品牌")
    model_col = first_column(detail, ["MODEL_FAMILY", "MODEL"], "车型")
    size_col = first_column(detail, SIZE_ALIASES, "物理尺码")
    ownership: dict[tuple[str, str, int], dict[tuple[str, str], float | None]] = {}
    for _, values in detail.iterrows():
        make = str(values[make_col]).strip()
        model = str(values[model_col]).strip()
        size = str(values[size_col]).strip()
        cid = str(values["CLUSTER_ID"]).strip()
        length = pd.to_numeric(values.get("L-MM", pd.NA), errors="coerce")
        length_value = None if pd.isna(length) else float(length)
        for year in parse_years(values.get("YEAR", "")):
            owners = ownership.setdefault((make, model, year), {})
            previous = owners.get((size, cid))
            if length_value is not None and (previous is None or length_value > previous):
                owners[(size, cid)] = length_value
            else:
                owners.setdefault((size, cid), None)
    return ownership


def size_length_capacities(detail: pd.DataFrame) -> dict[str, float]:
    """Infer each logical size's length ceiling from length plus recorded margin."""
    size_col = first_column(detail, SIZE_ALIASES, "物理尺码")
    lengths = pd.to_numeric(detail.get("L-MM"), errors="coerce")
    margins = pd.to_numeric(detail.get("自动长度余量"), errors="coerce")
    frame = pd.DataFrame({"尺码": detail[size_col].astype(str).str.strip(), "容量": lengths + margins}).dropna()
    return frame.groupby("尺码")["容量"].median().to_dict()


def summarize_size_checks(checks: list[tuple[int, str, str, float | None, float | None, bool]]) -> str:
    """Compact per-year size checks into one entry per conflicting cluster."""
    grouped: dict[tuple[str, str], list[tuple[int, float | None, float | None]]] = {}
    for year, size, cid, length, overflow, _ in checks:
        grouped.setdefault((size, cid), []).append((year, length, overflow))
    parts: list[str] = []
    for (size, cid), values in sorted(grouped.items()):
        years = compact_years([value[0] for value in values])
        lengths = [value[1] for value in values if value[1] is not None]
        overflows = [value[2] for value in values if value[2] is not None]
        if not lengths or not overflows:
            parts.append(f"{years}={size}:{cid},缺少长度或尺码上限")
            continue
        length_min, length_max = min(lengths), max(lengths)
        length_text = f"{length_min:g}" if length_min == length_max else f"{length_min:g}-{length_max:g}"
        parts.append(f"{years}={size}:{cid},车长={length_text}mm,最大超出={max(overflows):g}mm")
    return ";".join(parts)


def merge_test_year(
    row: pd.Series,
    ownership: dict[tuple[str, str, int], dict[tuple[str, str], float | None]],
    capacities: dict[str, float] | None = None,
    length_tolerance_mm: float = 0,
) -> dict[str, object]:
    """Expand only unowned year gaps; never overlap a sibling cluster's source facts."""
    source_text = str(row.get("FITMENT_YEAR", "")).strip()
    source_years = sorted(set(parse_years(source_text)))
    if not source_years:
        return {
            "SOURCE_YEAR": source_text, "CONSUMER_YEAR": source_text,
            "CANDIDATE_YEAR": source_text, "YEAR_MERGE_STATUS": "UNRESOLVED_YEAR",
            "NEW_YEAR_COUNT": 0, "NEW_YEARS": "", "YEAR_CONFLICT_DETAIL": "",
            "FINAL_SIZE": str(row.get("PHYSICAL_SIZE", "")).strip(), "TARGET_LENGTH_LIMIT": None,
            "MAX_LENGTH_OVERFLOW": None, "SIZE_REVIEW_DETAIL": "",
        }
    candidate_years = set(range(source_years[0], source_years[-1] + 1))
    new_years = candidate_years - set(source_years)
    unowned_new_years = {
        year for year in new_years if not ownership.get((str(row["MAKE"]).strip(), str(row["MODEL"]).strip(), year))
    }
    occupied_new_years = new_years - unowned_new_years
    candidate_text = str(source_years[0]) if source_years[0] == source_years[-1] else f"{source_years[0]}-{source_years[-1]}"
    target_size = str(row["PHYSICAL_SIZE"]).strip()
    make = str(row["MAKE"]).strip()
    model = str(row["MODEL"]).strip()
    candidate_owners = [
        (size, cid, length)
        for year in sorted(candidate_years)
        for (size, cid), length in ownership.get((make, model, year), {}).items()
    ]
    known_lengths = [length for _, _, length in candidate_owners if length is not None]
    observed_sizes = {size for size, _, _ in candidate_owners}
    final_size = target_size
    if known_lengths and capacities:
        model_max_length = max(known_lengths)
        current_capacity = capacities.get(target_size)
        fitting_sizes = [
            size for size in observed_sizes
            if size in capacities
            and current_capacity is not None
            and capacities[size] <= current_capacity
            and model_max_length <= capacities[size] + length_tolerance_mm
        ]
        if fitting_sizes:
            final_size = min(fitting_sizes, key=lambda size: (capacities[size], size))
    checks: list[tuple[int, str, str, float | None, float | None, bool]] = []
    target_limit = (capacities or {}).get(final_size)
    max_overflow = None if not known_lengths or target_limit is None else max(known_lengths) - target_limit
    for year in sorted(occupied_new_years):
        atom_owners = ownership.get((make, model, year), {})
        for (size, cid), length in sorted(atom_owners.items()):
            if size == final_size:
                continue
            overflow = None if length is None or target_limit is None else length - target_limit
            allowed = False
            checks.append((year, size, cid, length, overflow, allowed))
    failed_checks = [check for check in checks if not check[-1]]
    review_detail = summarize_size_checks(checks)
    conflict_detail = summarize_size_checks(failed_checks)
    expanded_years = set(source_years) | unowned_new_years
    consumer_text = compact_years(list(expanded_years))
    if failed_checks:
        status = "MERGED_SAFE_PARTIAL" if unowned_new_years else "REJECTED_SOURCE_OCCUPIED"
        return {
            "SOURCE_YEAR": source_text, "CONSUMER_YEAR": consumer_text,
            "CANDIDATE_YEAR": candidate_text, "YEAR_MERGE_STATUS": status,
            "NEW_YEAR_COUNT": len(new_years), "NEW_YEARS": compact_years(list(new_years)),
            "YEAR_CONFLICT_DETAIL": conflict_detail,
            "FINAL_SIZE": final_size, "TARGET_LENGTH_LIMIT": target_limit,
            "MAX_LENGTH_OVERFLOW": max_overflow, "SIZE_REVIEW_DETAIL": review_detail,
        }
    if final_size != target_size:
        merge_status = "MERGED_FINAL_SIZE_RECOMMENDED"
    elif checks:
        merge_status = "MERGED_SIZE_TOLERANCE"
    else:
        merge_status = "MERGED_SAFE" if new_years else "UNCHANGED"
    return {
        "SOURCE_YEAR": source_text, "CONSUMER_YEAR": consumer_text, "CANDIDATE_YEAR": candidate_text,
        "YEAR_MERGE_STATUS": merge_status,
        "NEW_YEAR_COUNT": len(new_years), "NEW_YEARS": compact_years(list(new_years)), "YEAR_CONFLICT_DETAIL": "",
        "FINAL_SIZE": final_size, "TARGET_LENGTH_LIMIT": target_limit,
        "MAX_LENGTH_OVERFLOW": max_overflow, "SIZE_REVIEW_DETAIL": review_detail,
    }


def listing_detail(allocated: pd.DataFrame, detail: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    fits = fitment_rows(detail)
    listing = allocated.copy().merge(fits, on="CLUSTER_ID", how="left")
    listing["MAKE"] = listing["FITMENT_MAKE"].fillna(listing.get("MAKE", ""))
    listing["MODEL"] = listing["FITMENT_MODEL"].fillna(listing.get("MODEL", ""))
    listing["MAKE_MODEL"] = listing["MAKE_MODEL"].fillna("")
    listing["适配车型"] = listing["适配车型"].fillna(listing["CONSUMER_NAME"])
    listing["SIZENAME"] = listing["CONSUMER_NAME"].str.replace(" · ", " ", regex=False)
    ownership = build_year_ownership(detail)
    capacities = size_length_capacities(detail)
    tolerance = float(config.get("year_merge_length_tolerance_mm", 0))
    diagnostics = pd.DataFrame([
        merge_test_year(row, ownership, capacities, tolerance) for _, row in listing.iterrows()
    ], index=listing.index)
    for column in diagnostics.columns:
        listing[column] = diagnostics[column]
    listing["CONSUMER_NAME"] = listing.apply(lambda r: fixed_consumer_name(r, config), axis=1)
    listing["SKU_NAME"] = listing.apply(lambda r: sku_name(r, config), axis=1)
    if listing["SKU_NAME"].duplicated().any():
        duplicates = sorted(listing.loc[listing["SKU_NAME"].duplicated(False), "SKU_NAME"].unique())
        raise ValueError(f"SKU_NAME 冲突，请在 JSON 中细化缩写规则：{duplicates}")
    status_cn = {
        "MERGED_SAFE": "安全合并：无跨尺码事实",
        "MERGED_SAFE_PARTIAL": "部分合并：扩张无来源年份，保留已占用年份缺口",
        "REJECTED_SOURCE_OCCUPIED": "保留分开：缺口年份已属于兄弟链接",
        "MERGED_SIZE_TOLERANCE": "安全合并：跨尺码但长度差在阈值内",
        "MERGED_FINAL_SIZE_RECOMMENDED": "安全合并：建议统一最终尺码",
        "REJECTED_CROSS_SIZE": "拒绝合并：长度差超过阈值",
        "UNCHANGED": "无需合并", "UNRESOLVED_YEAR": "年份无法解析",
    }
    report = listing[[
        "CLUSTER_ID", "PHYSICAL_SIZE", "MAKE", "MODEL", "SOURCE_YEAR", "CANDIDATE_YEAR", "CONSUMER_YEAR",
        "FINAL_SIZE", "TARGET_LENGTH_LIMIT", "MAX_LENGTH_OVERFLOW", "YEAR_MERGE_STATUS",
        "NEW_YEAR_COUNT", "NEW_YEARS", "SIZE_REVIEW_DETAIL", "YEAR_CONFLICT_DETAIL",
    ]].copy()
    report["YEAR_MERGE_STATUS"] = report["YEAR_MERGE_STATUS"].map(status_cn).fillna(report["YEAR_MERGE_STATUS"])
    report = report.rename(columns={
        "CLUSTER_ID": "聚类ID", "PHYSICAL_SIZE": "逻辑尺码", "MAKE": "品牌", "MODEL": "车型",
        "SOURCE_YEAR": "原始年份", "CANDIDATE_YEAR": "候选合并年份", "CONSUMER_YEAR": "最终命名年份",
        "FINAL_SIZE": "建议最终尺码", "TARGET_LENGTH_LIMIT": "目标尺码长度上限毫米",
        "MAX_LENGTH_OVERFLOW": "最大超出毫米",
        "YEAR_MERGE_STATUS": "合并结论", "NEW_YEAR_COUNT": "新增年份数", "NEW_YEARS": "新增年份",
        "SIZE_REVIEW_DETAIL": "尺码簇分析明细", "YEAR_CONFLICT_DETAIL": "冲突明细",
    }).sort_values(["合并结论", "逻辑尺码", "品牌", "车型"])
    listing = listing.rename(columns={
        "SOURCE_YEAR": "原始年份", "CONSUMER_YEAR": "命名年份", "YEAR_MERGE_STATUS": "年份合并结论",
        "NEW_YEAR_COUNT": "新增年份数", "YEAR_CONFLICT_DETAIL": "年份冲突明细",
    })
    listing["年份合并结论"] = listing["年份合并结论"].map(status_cn).fillna(listing["年份合并结论"])
    cols = [
        "SKU_NAME", "CLUSTER_ID", "PHYSICAL_SIZE", "CONSUMER_NAME", "SIZENAME", "适配车型", "行发货量",
        "原始年份", "命名年份", "年份合并结论", "新增年份数", "年份冲突明细",
    ]
    # Keep the full naming catalogue here.  The final W-car workflow performs
    # its own global allocation, so a cluster that is zero in this size-level
    # preview can still receive a shipment there.
    output = listing.loc[:, cols].sort_values(
        ["PHYSICAL_SIZE", "行发货量", "SKU_NAME"], ascending=[True, False, True]
    )
    return chinese_output(output, physical_size_name="逻辑尺码"), report


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="根据 public 聚类数据分配 SKU 发货量并生成上架明细")
    parser.add_argument("--cluster-dir", type=Path, default=repo / "D1.聚类SKU" / "output" / "W型车")
    parser.add_argument("--shipment", type=Path, default=None, help="含“发货单”工作表的 xlsx，或两列 CSV")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    parser.add_argument("--example-total", type=int, default=800, help="未提供发货单时生成的示例总量")
    parser.add_argument("--pack-size", type=int, default=3, help="Cluster 分配的包装倍数")
    parser.add_argument(
        "--abbreviations", type=Path,
        default=Path(__file__).resolve().parent / "config" / "sku_abbreviations.json",
        help="固定 MAKE、MODEL、CAB 等 SKU 缩写规则",
    )
    args = parser.parse_args()

    summary, detail = load_clusters(args.cluster_dir)
    shipment = read_shipment(args.shipment) if args.shipment else example_shipment(summary, args.example_total)
    allocated = allocate(summary, shipment, args.pack_size)
    abbreviations = load_abbreviations(args.abbreviations)
    listing, merge_report = listing_detail(allocated, detail, abbreviations)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    shipment_output = chinese_output(shipment, physical_size_name="逻辑尺码")
    analysis_output = chinese_output(allocated)
    grouping = allocated[allocated["行发货量"] > 0].copy()
    final_names = listing.set_index("聚类ID")["消费者名称"]
    grouping["CONSUMER_NAME"] = grouping["CLUSTER_ID"].map(final_names).fillna(grouping["CONSUMER_NAME"])
    grouping_output = chinese_output(grouping)
    shipment_output.to_csv(args.output_dir / "shipment_input.csv", index=False, encoding="utf-8-sig")
    analysis_output.to_csv(args.output_dir / "sku_shipment_analysis.csv", index=False, encoding="utf-8-sig", float_format="%.6f")
    grouping_output.to_csv(args.output_dir / "grouping_detail.csv", index=False, encoding="utf-8-sig", float_format="%.6f")
    listing.to_csv(args.output_dir / "listing_detail.csv", index=False, encoding="utf-8-sig")
    merge_report.to_csv(args.output_dir / "年份合并测试报告.csv", index=False, encoding="utf-8-sig")

    reconciliation = allocated.groupby("PHYSICAL_SIZE").agg(输入发货量=("发货量", "max"), 分配发货量=("行发货量", "sum"))
    reconciliation["差异"] = reconciliation["分配发货量"] - reconciliation["输入发货量"]
    status_counts = merge_report["合并结论"].value_counts()
    reconciliation_lines = ["| 逻辑尺码 | 输入发货量 | 分配发货量 | 差异 |", "|---|---:|---:|---:|"]
    for size, values in reconciliation.iterrows():
        reconciliation_lines.append(
            f"| {size} | {int(values['输入发货量'])} | {int(values['分配发货量'])} | {int(values['差异'])} |"
        )
    status_lines = ["| 合并结论 | Cluster 数 |", "|---|---:|"]
    for status, count in status_counts.items():
        status_lines.append(f"| {status} | {int(count)} |")
    report_lines = [
        "# SKU 发货量与年份合并最终报告", "",
        "## 处理范围", "",
        f"- 聚类目录：`{args.cluster_dir.name}`",
        f"- 全部 Cluster：{len(allocated)}",
        f"- 有发货量 Cluster：{int((allocated['行发货量'] > 0).sum())}",
        f"- 上架明细：{len(listing)} 条", "",
        "## 发货量核对", "", *reconciliation_lines, "",
        "## 年份与尺码簇结论", "", *status_lines, "",
        f"长度容差为 {float(abbreviations.get('year_merge_length_tolerance_mm', 0)):g} mm。冲突明细按年份区间和冲突 Cluster 汇总，不逐年展开。", "",
        "## 命名规则", "",
        "- 皮卡保留源名称中的驾驶舱和货斗名称。",
        "- 非皮卡默认不写入驾驶舱、货斗或结构；结构仅按 JSON 白名单写入。",
        "- `grouping_detail.csv` 的消费者名称与最终上架明细同步。",
        "- 所有输出 CSV 均使用中文字段名。", "",
        "## 输出文件", "",
        "- `shipment_input.csv`：逻辑尺码发货量输入。",
        "- `sku_shipment_analysis.csv`：全部 Cluster 发货分配过程。",
        "- `grouping_detail.csv`：有发货量 Cluster 及最终消费者名称。",
        "- `listing_detail.csv`：SKU 上架明细。",
        "- `年份合并测试报告.csv`：全量年份扩张与尺码簇审核。", "",
    ]
    (args.output_dir / "最终报告.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(reconciliation.to_string())
    print(f"clusters={len(summary)} positive_clusters={(allocated['行发货量'] > 0).sum()} listing_rows={len(listing)}")


if __name__ == "__main__":
    main()
