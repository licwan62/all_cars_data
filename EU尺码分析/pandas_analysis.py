from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
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
    write_dimension_library,
    write_analysis_outputs,
    write_outputs,
)


def read_repaired_csv(path: Path) -> tuple[pd.DataFrame, int]:
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


def year_range(start_value: object, end_value: object, as_of_year: int) -> str:
    start_match = re.search(r"(\d{4})", str(start_value))
    end_match = re.search(r"(\d{4})", str(end_value))
    if start_match is None:
        return ""
    start = int(start_match.group(1))
    end = int(end_match.group(1)) if end_match else as_of_year
    return f"{start}-{end}"


def source_variant(row: pd.Series) -> str:
    identifier = str(row.get("id", "")).strip()
    ktype = str(row.get("Ktype", "")).strip()
    suffix = identifier[len(ktype):].strip(" _-") if identifier.startswith(ktype) else ""
    return re.sub(r"[_-]+", " ", suffix).strip()


def build_base(source_dir: Path, as_of_year: int) -> tuple[pd.DataFrame, dict[str, object]]:
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
        year_range(start, end, as_of_year)
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
            "_source_variant": merged.apply(source_variant, axis=1),
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成与 US 全量表同结构的 EU 尺码分析发布表")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=ROOT / "data" / "eu" / "0916" / "source",
    )
    parser.add_argument("--output", type=Path, default=PROJECT_DIR / "output" / "pandas_output.csv")
    parser.add_argument("--publish-output", type=Path)
    parser.add_argument("--analysis-output", type=Path, default=PROJECT_DIR / "output" / "尺寸分析表.csv")
    parser.add_argument("--publish-analysis-output", type=Path)
    parser.add_argument("--dimension-output", type=Path, default=PROJECT_DIR / "output" / "尺寸库.csv")
    parser.add_argument("--publish-dimension-output", type=Path)
    parser.add_argument("--status", type=Path, default=PROJECT_DIR / "output" / "status.json")
    parser.add_argument("--shape-map", type=Path, default=PROJECT_DIR / "rules" / "车形映射.csv")
    parser.add_argument("--as-of-year", type=int, default=date.today().year)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source_base, extra = build_base(args.source_dir.resolve(), args.as_of_year)
        library, metadata = build_dimension_library(source_base)
        base = dimension_library_to_base(library, metadata)
        result, analysis = calculate_us_standard(
            base,
            args.shape_map.resolve(),
            country_code="EU",
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
        print(f"EU 尺码分析失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
