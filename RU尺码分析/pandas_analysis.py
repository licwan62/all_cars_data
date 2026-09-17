from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
ROOT = PROJECT_DIR.parent
sys.path.insert(0, str(ROOT))

from regional_size_common import (  # noqa: E402
    RegionalDataError,
    build_dimension_library,
    calculate_us_standard,
    dimension_library_to_base,
    output_summary,
    read_csv,
    write_dimension_library,
    write_analysis_outputs,
    write_outputs,
)


def url_key(series: pd.Series) -> pd.Series:
    return series.astype("string").str.extract(r"/cars/([^/]+/[^/]+)/", expand=False).fillna("")


def normalize_model(value: object) -> str:
    text = str(value).strip()
    match = re.fullmatch(r"(\d{1,2})月(\d{1,2})日", text)
    return f"{match.group(1)}-{match.group(2)}" if match else text


def category_for_body(body_type: object) -> str:
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


def structure_for_body(body_type: object) -> str:
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


def cab_for_value(value: object) -> str:
    text = str(value).strip()
    return re.sub(r"\s+Cab$", "", text, flags=re.I)


def build_base(source_dir: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    catalog = read_csv(source_dir / "auto_ru_catalog_rank.csv")
    catalog.columns = [column.strip() for column in catalog.columns]
    dimensions = read_csv(source_dir / "auto_ru_dimensions_with_match_key.csv")
    sales = read_csv(source_dir / "auto_ru_model_sales_with_match_key.csv")

    catalog["url_key"] = url_key(catalog["link_url"])
    dimensions["url_key"] = url_key(dimensions["model_url"])
    sales["url_key"] = url_key(sales["link_url"])
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
            "MODEL": base_rows["model"].map(normalize_model),
            "TRIM": "",
            "版本": base_rows["body_version"],
            "结构": base_rows["body_type_norm"].map(structure_for_body),
            "CAB": base_rows["cab_norm"].map(cab_for_value),
            "BED": "",
            "代际": base_rows["generation_norm"],
            "YEAR": base_rows["years"],
            "分类": base_rows["body_type_norm"].map(category_for_body),
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
                        normalize_model(row["model"]), str(row["generation_norm"]).strip(),
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成与 US 全量表同结构的 RU 尺码分析发布表")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=ROOT / "data" / "ru" / "0916" / "source",
    )
    parser.add_argument("--output", type=Path, default=PROJECT_DIR / "output" / "pandas_output.csv")
    parser.add_argument("--publish-output", type=Path)
    parser.add_argument("--analysis-output", type=Path, default=PROJECT_DIR / "output" / "尺寸分析表.csv")
    parser.add_argument("--publish-analysis-output", type=Path)
    parser.add_argument("--dimension-output", type=Path, default=PROJECT_DIR / "output" / "尺寸库.csv")
    parser.add_argument("--publish-dimension-output", type=Path)
    parser.add_argument("--status", type=Path, default=PROJECT_DIR / "output" / "status.json")
    parser.add_argument("--shape-map", type=Path, default=PROJECT_DIR / "rules" / "车形映射.csv")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source_base, extra = build_base(args.source_dir.resolve())
        library, metadata = build_dimension_library(source_base)
        base = dimension_library_to_base(library, metadata)
        result, analysis = calculate_us_standard(
            base,
            args.shape_map.resolve(),
            country_code="RU",
            include_analysis=True,
        )
        summary = output_summary(result, {
            **extra,
            "dimension_library_rows": int(len(library)),
            "dimension_analysis_rows": int(len(analysis)),
        })
        write_dimension_library(
            library,
            args.dimension_output.resolve(),
            args.publish_dimension_output.resolve() if args.publish_dimension_output else None,
        )
        write_analysis_outputs(
            analysis,
            args.analysis_output.resolve(),
            args.publish_analysis_output.resolve() if args.publish_analysis_output else None,
        )
        write_outputs(
            result,
            args.output.resolve(),
            args.status.resolve(),
            summary,
            args.publish_output.resolve() if args.publish_output else None,
        )
    except (RegionalDataError, FileNotFoundError, pd.errors.ParserError) as error:
        print(f"RU 尺码分析失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
