"""区域原始 source 到公共 base 表的解析逻辑。

每个区域（EU、RU……）的抓取结果格式各不相同；本模块把"读 source 目录、
清洗字段、拼出 regional_size_common.BASE_COLUMNS 基表"这一步集中放在
01.整理尺寸库 节点里，供本节点自身的尺寸库压缩去重使用，也供 EU/RU 尺码
分析节点复用（它们只做后续的尺码匹配分析，不再各自解析 source）。
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regional_size_common import RegionalDataError, read_csv  # noqa: E402


def read_repaired_csv(path: Path) -> tuple[pd.DataFrame, int]:
    """读取 EU 抓取结果里偶发的错位分隔 CSV，尝试按已知列布局修复。"""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows: list[list[str]] = []
        repaired = 0
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                repaired += 1
                if path.name.startswith("DimensionGroup") and len(row) >= 8:
                    row = row[:6] + [",".join(row[6:-1]), row[-1]]
                elif path.name == "Ktype.csv" and len(row) >= 11:
                    row = row[:2] + [",".join(row[2:-8])] + row[-8:]
                elif path.name == "KtypeMatched.csv" and len(row) >= 10:
                    dimension_positions = [i for i, value in enumerate(row) if value.startswith("EU-")]
                    if len(dimension_positions) == 1:
                        position = dimension_positions[0]
                        row = (
                            row[:3]
                            + [",".join(row[3 : position - 2]), row[position - 2], row[position - 1]]
                            + [row[position], row[position + 1], ",".join(row[position + 2 : -1]), row[-1]]
                        )
            if len(row) != len(header):
                raise RegionalDataError(
                    f"{path.name} 第 {line_number} 行无法恢复：预期 {len(header)} 列，实际 {len(row)} 列"
                )
            rows.append(row)
    return pd.DataFrame(rows, columns=header), repaired


def _eu_year_range(start_value: object, end_value: object, as_of_year: int) -> str:
    start_match = re.search(r"(\d{4})", str(start_value))
    end_match = re.search(r"(\d{4})", str(end_value))
    if start_match is None:
        return ""
    start = int(start_match.group(1))
    end = int(end_match.group(1)) if end_match else as_of_year
    return f"{start}-{end}"


def _eu_source_variant(row: pd.Series) -> str:
    identifier = str(row.get("id", "")).strip()
    ktype = str(row.get("Ktype", "")).strip()
    suffix = identifier[len(ktype):].strip(" _-") if identifier.startswith(ktype) else ""
    return re.sub(r"[_-]+", " ", suffix).strip()


def build_eu_base(source_dir: Path, as_of_year: int) -> tuple[pd.DataFrame, dict[str, object]]:
    ktypes, repaired_ktypes = read_repaired_csv(source_dir / "Ktype.csv")
    matched, repaired_matched = read_repaired_csv(source_dir / "KtypeMatched.csv")
    dimension_path = next(source_dir.glob("DimensionGroup*.csv"))
    dimensions, repaired_dimensions = read_repaired_csv(dimension_path)

    if ktypes["Ktype"].duplicated().any():
        raise RegionalDataError("Ktype.csv 的 Ktype 必须唯一")
    if matched["id"].duplicated().any():
        raise RegionalDataError("KtypeMatched.csv 的 id 必须唯一")
    if dimensions["DIMENSION_GROUP_ID"].duplicated().any():
        raise RegionalDataError("DimensionGroup 尺寸表的 DIMENSION_GROUP_ID 必须唯一")

    merged = ktypes.merge(matched, on="Ktype", how="left", validate="one_to_many", indicator=True)
    merged = merged.merge(
        dimensions,
        on="DIMENSION_GROUP_ID",
        how="left",
        validate="many_to_one",
        indicator="dimension_join",
    )
    mapped = merged["id"].astype("string").fillna("").str.strip().ne("")
    merged["DIMENSION-ID"] = (
        "EU-KTYPE-MAP-" + merged["id"].astype("string")
    ).where(mapped, "EU-KTYPE-" + merged["Ktype"].astype("string") + "-UNMATCHED")
    merged["YEAR"] = [
        _eu_year_range(start, end, as_of_year)
        for start, end in zip(
            merged["Product Start Month-Year"], merged["Product End Month-Year"], strict=True
        )
    ]

    base = pd.DataFrame(
        {
            "MAKE": merged["Make"],
            "MODEL": merged["Model"],
            "TRIM": merged["VariantName"],
            "版本": merged["BodyCode"].fillna(""),
            "结构": merged["Type"].fillna(merged["NormalizedBodyStyle"]).fillna(merged["BodyStyle"]),
            "CAB": "",
            "BED": "",
            "代际": merged["Generation"].fillna(""),
            "YEAR": merged["YEAR"],
            "分类": merged["分类"].fillna(""),
            "L-MM": pd.to_numeric(merged["LengthMM"], errors="coerce"),
            "W-MM": pd.to_numeric(merged["WidthMM"], errors="coerce"),
            "H-MM": pd.to_numeric(merged["HeightMM"], errors="coerce"),
            "销量合计": 0,
            "DIMENSION-ID": merged["DIMENSION-ID"],
            "_source_variant": merged.apply(_eu_source_variant, axis=1),
            "_reference": merged.apply(
                lambda row: " ".join(
                    value for value in [
                        str(row["YEAR"]).strip(), str(row["Make"]).strip(),
                        str(row["Model"]).strip(), str(row["VariantName"]).strip(),
                        str(row["Type"]).strip(),
                    ] if value
                ),
                axis=1,
            ),
            "_notes": merged.apply(
                lambda row: " | ".join(
                    value for value in [
                        f"尺寸来源：{str(row['DimensionSource']).strip()}" if str(row["DimensionSource"]).strip() else "",
                        str(row["SourceURL"]).strip(),
                    ] if value
                ),
                axis=1,
            ),
            "_iteration": merged.apply(
                lambda row: (
                    "待补尺寸" if not str(row["id"]).strip()
                    else "可入库" if str(row["IterationStatus"]).strip().upper() == "READY"
                    else str(row["IterationStatus"]).strip()
                ),
                axis=1,
            ),
        }
    )
    extra = {
        "as_of_year": as_of_year,
        "source_rows": {
            "Ktype": int(len(ktypes)),
            "KtypeMatched": int(len(matched)),
            "DimensionGroup": int(len(dimensions)),
        },
        "repaired_csv_rows": {
            "Ktype": repaired_ktypes,
            "KtypeMatched": repaired_matched,
            "DimensionGroup": repaired_dimensions,
        },
        "unmatched_ktypes": int((~mapped).sum()),
        "unused_dimension_groups": int(
            (~dimensions["DIMENSION_GROUP_ID"].isin(set(matched["DIMENSION_GROUP_ID"]))).sum()
        ),
        "match_confidence": matched["MatchConfidence"].value_counts().to_dict(),
        "body_type_disagreements": int(
            (
                merged["NormalizedBodyStyle"].fillna("").astype("string")
                != merged["Type"].fillna("").astype("string")
            ).sum()
        ),
    }
    return base, extra


def _ru_url_key(series: pd.Series) -> pd.Series:
    return series.astype("string").str.extract(r"/cars/([^/]+/[^/]+)/", expand=False).fillna("")


def _ru_normalize_model(value: object) -> str:
    text = str(value).strip()
    match = re.fullmatch(r"(\d{1,2})月(\d{1,2})日", text)
    return f"{match.group(1)}-{match.group(2)}" if match else text


def _ru_category_for_body(body_type: object) -> str:
    body = str(body_type).strip()
    if body == "Pickup":
        return "皮卡"
    if body.startswith("SUV"):
        return "越野车"
    if body in {"Sedan", "Sedan 2-door", "Sedan-hardtop", "Limousine"}:
        return "三厢车"
    if body in {"Coupe", "Convertible", "Roadster", "Targa", "Phaeton", "Speedster"}:
        return "跑车"
    return "两厢车"


def _ru_structure_for_body(body_type: object) -> str:
    body = str(body_type).strip()
    if body == "Station Wagon":
        return "Wagon"
    if body in {"Compact MPV", "Minivan", "Microvan"}:
        return "MPV"
    if body == "Cargo Van":
        return "Van"
    if body in {"Sedan 2-door", "Sedan-hardtop", "Limousine"}:
        return "Sedan"
    return body


def _ru_cab_for_value(value: object) -> str:
    text = str(value).strip()
    return re.sub(r"\s+Cab$", "", text, flags=re.I)


def build_ru_base(
    source_dir: Path, sales_path: Path | None = None
) -> tuple[pd.DataFrame, dict[str, object]]:
    catalog = read_csv(source_dir / "auto_ru_catalog_rank.csv")
    catalog.columns = [column.strip() for column in catalog.columns]
    dimensions = read_csv(source_dir / "auto_ru_dimensions_with_match_key.csv")
    sales = read_csv(sales_path or source_dir / "auto_ru_model_sales_with_match_key.csv")

    catalog["url_key"] = _ru_url_key(catalog["link_url"])
    dimensions["url_key"] = _ru_url_key(dimensions["model_url"])
    sales["url_key"] = _ru_url_key(sales["link_url"])
    catalog["Rank_number"] = pd.to_numeric(catalog["Rank"], errors="coerce")
    catalog_unique = (
        catalog.sort_values("Rank_number", kind="stable")
        .drop_duplicates("url_key", keep="first")
        [["url_key", "Model", "Sale", "Rank_number"]]
    )

    for column in ["length_mm", "width_mm", "height_mm"]:
        dimensions[column] = pd.to_numeric(dimensions[column], errors="coerce")
    grouped = dimensions.groupby("match_key", sort=False, dropna=False)
    base_rows = grouped.agg(
        brand=("brand", "first"),
        model=("model", "first"),
        generation_norm=("generation_norm", "first"),
        years=("years", "first"),
        body_type_norm=("body_type_norm", "first"),
        cab_norm=("cab_norm", "first"),
        body_version=("body_version", "first"),
        model_url=("model_url", "first"),
        url_key=("url_key", "first"),
        length_mm=("length_mm", "max"),
        width_mm=("width_mm", "max"),
        height_mm=("height_mm", "max"),
        configuration_count=("modification", "nunique"),
        dimension_row_count=("modification", "size"),
    ).reset_index()
    dimension_tuple_count = (
        dimensions[["match_key", "length_mm", "width_mm", "height_mm"]]
        .drop_duplicates()
        .groupby("match_key", sort=False)
        .size()
        .rename("dimension_tuple_count")
    )
    base_rows = base_rows.merge(dimension_tuple_count, on="match_key", how="left", validate="one_to_one")

    sales["sale_detail_number"] = pd.to_numeric(sales["sale_detail"], errors="coerce")
    sales_by_key = (
        sales.loc[sales["match_key"].astype("string").str.strip().ne("")]
        .groupby("match_key", sort=False, as_index=False)["sale_detail_number"]
        .sum(min_count=1)
        .rename(columns={"sale_detail_number": "sales_total"})
    )
    base_rows = base_rows.merge(sales_by_key, on="match_key", how="left", validate="one_to_one")
    base_rows = base_rows.merge(catalog_unique, on="url_key", how="left", validate="many_to_one")

    base = pd.DataFrame(
        {
            "MAKE": base_rows["brand"],
            "MODEL": base_rows["model"].map(_ru_normalize_model),
            "TRIM": "",
            "版本": base_rows["body_version"],
            "结构": base_rows["body_type_norm"].map(_ru_structure_for_body),
            "CAB": base_rows["cab_norm"].map(_ru_cab_for_value),
            "BED": "",
            "代际": base_rows["generation_norm"],
            "YEAR": base_rows["years"],
            "分类": base_rows["body_type_norm"].map(_ru_category_for_body),
            "L-MM": base_rows["length_mm"],
            "W-MM": base_rows["width_mm"],
            "H-MM": base_rows["height_mm"],
            "销量合计": base_rows["sales_total"].fillna(0),
            "DIMENSION-ID": "RU|" + base_rows["match_key"].astype("string"),
            "_source_variant": base_rows["generation_norm"],
            "_reference": base_rows.apply(
                lambda row: " ".join(
                    value for value in [
                        str(row["years"]).strip(), str(row["brand"]).strip(),
                        _ru_normalize_model(row["model"]), str(row["generation_norm"]).strip(),
                        str(row["body_type_norm"]).strip(),
                    ] if value and value != "-"
                ),
                axis=1,
            ),
            "_notes": "",
            "_iteration": "可入库",
        }
    )

    catalog_keys = set(catalog_unique["url_key"])
    dimension_keys = set(base_rows["url_key"])
    sales_keys = set(sales.loc[sales["url_key"].ne(""), "url_key"])
    nonblank_sales_keys = set(sales.loc[sales["match_key"].ne(""), "match_key"])
    all_sales_total = int(sales["sale_detail_number"].sum())
    matched_sales_total = int(
        sales.loc[sales["match_key"].ne(""), "sale_detail_number"].sum()
    )
    extra = {
        "source_rows": {
            "catalog": int(len(catalog)),
            "dimensions": int(len(dimensions)),
            "sales": int(len(sales)),
        },
        "catalog_unique_url_keys": int(len(catalog_keys)),
        "catalog_duplicate_rows": int(len(catalog) - len(catalog_unique)),
        "dimension_match_keys": int(base_rows["match_key"].nunique()),
        "dimension_groups_with_multiple_tuples": int((base_rows["dimension_tuple_count"] > 1).sum()),
        "dimension_groups_without_sales": int((~base_rows["match_key"].isin(nonblank_sales_keys)).sum()),
        "sales_rows_without_match_key": int(sales["match_key"].eq("").sum()),
        "source_sales_total": all_sales_total,
        "matched_sales_total": matched_sales_total,
        "unmatched_sales_total": all_sales_total - matched_sales_total,
        "dimension_model_keys_not_in_catalog": int(len(dimension_keys - catalog_keys)),
        "catalog_model_keys_without_dimensions": int(len(catalog_keys - dimension_keys)),
        "catalog_model_keys_without_sales": int(len(catalog_keys - sales_keys)),
        "dimension_strategy": "每个 match_key 的长、宽、高分别取最大值；配置销量按 match_key 求和",
    }
    return base, extra
