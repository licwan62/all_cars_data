#!/usr/bin/env python3
"""Export audited scraper TSVs into the regional size-data pipeline.

The exporter is intentionally one-way: it writes a new candidate directory and
never changes the scraper artifacts or an existing published data directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
ROOT = PROJECT_DIR.parent
SOURCE_COLUMNS = [
    "Make",
    "Model",
    "VariantName",
    "BodyStyle",
    "DriveType",
    "Energy",
    "EngineOutputKW",
    "EngineOutputHP",
    "Product Start Month-Year",
    "Product End Month-Year",
    "Ktype",
]
MAPPING_COLUMNS = [
    "id",
    "Ktype",
    "NormalizedBodyStyle",
    "Generation",
    "BodyCode",
    "Doors",
    "DIMENSION_GROUP_ID",
    "MatchConfidence",
    "Notes",
    "IterationStatus",
]
DIMENSION_COLUMNS = [
    "DIMENSION_GROUP_ID",
    "LengthMM",
    "WidthMM",
    "HeightMM",
    "DimensionSource",
    "SourceURL",
]
PIPELINE_DIMENSION_COLUMNS = [
    "DIMENSION_GROUP_ID",
    "Type",
    "分类",
    "LengthMM",
    "WidthMM",
    "HeightMM",
    "DimensionSource",
    "SourceURL",
]


class ExportError(ValueError):
    """The scraper output cannot be safely handed to the data pipeline."""


def read_tsv(path: Path, expected_columns: list[str], table_name: str) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"{table_name} 不存在：{path}")
    frame = pd.read_csv(
        path,
        sep="\t",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )
    if list(frame.columns) != expected_columns:
        raise ExportError(
            f"{table_name} 字段不符合契约：预期 {expected_columns}，实际 {list(frame.columns)}"
        )
    return frame


def _strip_cells(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()
    for column in cleaned.columns:
        cleaned[column] = cleaned[column].astype("string").str.strip().fillna("")
    return cleaned


def _deduplicate_mappings(mapping: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    duplicate_rows = int(mapping.duplicated().sum())
    mapping = mapping.drop_duplicates().copy()
    conflicting = [
        str(key)
        for key, group in mapping.groupby("id", sort=False)
        if len(group) > 1
    ]
    if conflicting:
        preview = ", ".join(conflicting[:10])
        suffix = "" if len(conflicting) <= 10 else f"，另有 {len(conflicting) - 10} 个"
        raise ExportError(f"Ktype 映射 id 存在冲突：{preview}{suffix}")
    return mapping, duplicate_rows


def _merge_text(values: pd.Series) -> str:
    unique: list[str] = []
    for value in values:
        for item in str(value).split(";"):
            item = item.strip()
            if item and item not in unique:
                unique.append(item)
    return ";".join(unique)


def _deduplicate_dimensions(dimensions: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    duplicate_rows = int(dimensions.duplicated().sum())
    dimensions = dimensions.drop_duplicates().copy()
    rows: list[pd.Series] = []
    conflicts: list[str] = []
    for group_id, group in dimensions.groupby("DIMENSION_GROUP_ID", sort=False):
        signatures = group[["LengthMM", "WidthMM", "HeightMM"]].drop_duplicates()
        if len(signatures) > 1:
            conflicts.append(str(group_id))
            continue
        row = group.iloc[0].copy()
        row["DimensionSource"] = _merge_text(group["DimensionSource"])
        row["SourceURL"] = _merge_text(group["SourceURL"])
        rows.append(row)
    if conflicts:
        preview = ", ".join(conflicts[:10])
        suffix = "" if len(conflicts) <= 10 else f"，另有 {len(conflicts) - 10} 个"
        raise ExportError(f"尺寸组 ID 对应多个三维值：{preview}{suffix}")
    return pd.DataFrame(rows, columns=DIMENSION_COLUMNS), duplicate_rows


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


def _pipeline_group_id(group_id: str, body_style: str, occupied: set[str]) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", body_style.upper()).strip("-") or "BODY"
    base = f"{group_id}-PIPE-{slug}"
    candidate = base
    sequence = 2
    while candidate in occupied:
        candidate = f"{base}-{sequence:02d}"
        sequence += 1
    occupied.add(candidate)
    return candidate


def _split_pipeline_dimension_groups(
    mapping: pd.DataFrame,
    dimensions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Give each mapping body style its own compatibility dimension row.

    The scraper may intentionally reuse one physical dimension group for, for
    example, MPV and Van Ktypes. The legacy regional CSV stores body type on
    the dimension row, so a pipeline-only ID is needed to preserve both
    branches without changing the research cache identity.
    """
    mapping = mapping.copy()
    occupied = set(dimensions["DIMENSION_GROUP_ID"])
    output_rows: list[pd.Series] = []
    split_groups = 0
    dimensions_by_id = dimensions.set_index("DIMENSION_GROUP_ID", drop=False)
    for group_id, group in mapping.groupby("DIMENSION_GROUP_ID", sort=False):
        styles = sorted({str(value).strip() for value in group["NormalizedBodyStyle"] if str(value).strip()})
        if not styles:
            raise ExportError(f"尺寸组 {group_id} 的映射缺少 NormalizedBodyStyle")
        source_row = dimensions_by_id.loc[group_id]
        if len(styles) == 1:
            row = source_row.copy()
            row["Type"] = styles[0]
            row["分类"] = category_for_body(styles[0])
            output_rows.append(row)
            continue

        split_groups += 1
        for style in styles:
            pipeline_id = _pipeline_group_id(group_id, style, occupied)
            row = source_row.copy()
            row["DIMENSION_GROUP_ID"] = pipeline_id
            row["Type"] = style
            row["分类"] = category_for_body(style)
            output_rows.append(row)
            mask = (
                mapping["DIMENSION_GROUP_ID"].eq(group_id)
                & mapping["NormalizedBodyStyle"].eq(style)
            )
            mapping.loc[mask, "DIMENSION_GROUP_ID"] = pipeline_id

    pipeline_dimensions = pd.DataFrame(output_rows)
    pipeline_dimensions = pipeline_dimensions[PIPELINE_DIMENSION_COLUMNS].reset_index(drop=True)
    return mapping.reset_index(drop=True), pipeline_dimensions, split_groups


def _validate_ready_tables(
    source: pd.DataFrame,
    mapping: pd.DataFrame,
    dimensions: pd.DataFrame,
) -> None:
    for name, frame, key in [
        ("原始 Ktype", source, "Ktype"),
        ("Ktype 映射", mapping, "id"),
        ("尺寸组", dimensions, "DIMENSION_GROUP_ID"),
    ]:
        blank = frame[key].eq("")
        if blank.any():
            raise ExportError(f"{name} 有 {int(blank.sum())} 行空主键")
        if frame[key].duplicated().any():
            raise ExportError(f"{name} 主键不唯一：{key}")

    unknown_confidence = sorted(set(mapping["MatchConfidence"]) - {"HIGH", "MEDIUM", "LOW"})
    if unknown_confidence:
        raise ExportError(f"MatchConfidence 非法：{', '.join(unknown_confidence)}")
    if not mapping["IterationStatus"].eq("READY").all():
        raise ExportError("进入流水线的 Ktype 映射必须全部为 READY")
    if mapping["DIMENSION_GROUP_ID"].eq("").any():
        raise ExportError("READY Ktype 映射存在空 DIMENSION_GROUP_ID")

    source_ktypes = set(source["Ktype"])
    missing_ktypes = sorted(set(mapping["Ktype"]) - source_ktypes)
    if missing_ktypes:
        raise ExportError(f"映射引用了原始表不存在的 Ktype：{', '.join(missing_ktypes[:10])}")

    dimension_ids = set(dimensions["DIMENSION_GROUP_ID"])
    missing_groups = sorted(set(mapping["DIMENSION_GROUP_ID"]) - dimension_ids)
    if missing_groups:
        raise ExportError(f"映射引用了不存在的尺寸组：{', '.join(missing_groups[:10])}")

    for column in ("LengthMM", "WidthMM", "HeightMM"):
        values = pd.to_numeric(dimensions[column], errors="coerce")
        invalid = values.isna() | values.le(0) | values.mod(1).ne(0)
        if invalid.any():
            raise ExportError(f"{column} 有 {int(invalid.sum())} 个非正整数")
    for column in ("DimensionSource", "SourceURL"):
        blank = dimensions[column].eq("")
        if blank.any():
            raise ExportError(f"尺寸组有 {int(blank.sum())} 行缺少 {column}")
    invalid_urls = ~dimensions["SourceURL"].str.split(";").map(
        lambda items: all(re.match(r"^https?://", item.strip(), flags=re.I) for item in items if item.strip())
    )
    if invalid_urls.any():
        raise ExportError(f"尺寸组有 {int(invalid_urls.sum())} 行包含非 HTTP(S) 来源链接")


def build_pipeline_inputs(
    source: pd.DataFrame,
    mapping: pd.DataFrame,
    dimensions: pd.DataFrame,
    *,
    include_unmatched: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    source = _strip_cells(source)
    mapping = _strip_cells(mapping)
    dimensions = _strip_cells(dimensions)
    mapping, duplicate_mapping_rows = _deduplicate_mappings(mapping)
    dimensions, duplicate_dimension_rows = _deduplicate_dimensions(dimensions)

    pending_mask = ~mapping["IterationStatus"].eq("READY")
    pending_rows = int(pending_mask.sum())
    mapping = mapping.loc[~pending_mask].copy()
    if mapping.empty:
        raise ExportError("没有可进入流水线的 READY Ktype 映射")

    referenced_groups = set(mapping["DIMENSION_GROUP_ID"])
    dimensions = dimensions.loc[
        dimensions["DIMENSION_GROUP_ID"].isin(referenced_groups)
    ].copy()
    _validate_ready_tables(source, mapping, dimensions)

    if not include_unmatched:
        referenced_ktypes = set(mapping["Ktype"])
        source = source.loc[source["Ktype"].isin(referenced_ktypes)].copy()

    dimensions["Type"] = ""
    dimensions["分类"] = ""
    mapping, pipeline_dimensions, split_groups = _split_pipeline_dimension_groups(
        mapping,
        dimensions,
    )

    source = source[SOURCE_COLUMNS].reset_index(drop=True)
    mapping = mapping[MAPPING_COLUMNS].reset_index(drop=True)
    pipeline_dimensions = pipeline_dimensions.reset_index(drop=True)
    summary = {
        "source_rows": int(len(source)),
        "ready_mapping_rows": int(len(mapping)),
        "ready_ktypes": int(mapping["Ktype"].nunique()),
        "dimension_groups": int(len(pipeline_dimensions)),
        "shared_dimension_groups_split_for_pipeline": split_groups,
        "pending_mapping_rows_skipped": pending_rows,
        "exact_duplicate_mapping_rows_removed": duplicate_mapping_rows,
        "exact_duplicate_dimension_rows_removed": duplicate_dimension_rows,
        "include_unmatched": include_unmatched,
    }
    return source, mapping, pipeline_dimensions, summary


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
        na_rep="",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_new_targets(paths: list[Path]) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError("拒绝覆盖已有候选文件：" + ", ".join(existing))


def export_source_candidate(
    source: pd.DataFrame,
    mapping: pd.DataFrame,
    dimensions: pd.DataFrame,
    output_dir: Path,
    summary: dict[str, Any],
) -> dict[str, Any]:
    source_dir = output_dir / "source"
    paths = {
        "Ktype": source_dir / "Ktype.csv",
        "KtypeMatched": source_dir / "KtypeMatched.csv",
        "DimensionGroup": source_dir / "DimensionGroup尺寸.csv",
    }
    status_path = output_dir / "ingest_status.json"
    _require_new_targets([*paths.values(), status_path])
    _write_csv(source, paths["Ktype"])
    _write_csv(mapping, paths["KtypeMatched"])
    _write_csv(dimensions, paths["DimensionGroup"])
    manifest = {
        **summary,
        "files": {
            name: {
                "path": str(path.resolve()),
                "sha256": _sha256(path),
            }
            for name, path in paths.items()
        },
    }
    status_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def _load_eu_module():
    path = ROOT / "EU尺码分析" / "pandas_analysis.py"
    spec = importlib.util.spec_from_file_location("eu_size_analysis_for_scraper", path)
    if spec is None or spec.loader is None:
        raise ExportError(f"无法加载 EU 尺码分析模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_eu_pipeline(source_dir: Path, output_dir: Path, as_of_year: int) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT))
    from regional_size_common import (  # noqa: PLC0415
        build_dimension_library,
        calculate_us_standard,
        dimension_library_to_base,
        output_summary,
        write_analysis_outputs,
        write_dimension_library,
        write_outputs,
    )

    targets = [
        output_dir / "00_EU尺寸库.csv",
        output_dir / "01_EU尺寸分析表.csv",
        output_dir / "02_EU全量.csv",
        output_dir / "status.json",
    ]
    _require_new_targets(targets)
    eu = _load_eu_module()
    source_base, extra = eu.build_base(source_dir, as_of_year)
    library, metadata = build_dimension_library(source_base)
    base = dimension_library_to_base(library, metadata)
    result, analysis = calculate_us_standard(
        base,
        ROOT / "EU尺码分析" / "rules" / "车形映射.csv",
        country_code="EU",
        include_analysis=True,
    )
    summary = output_summary(
        result,
        {
            **extra,
            "dimension_library_rows": int(len(library)),
            "dimension_analysis_rows": int(len(analysis)),
            "input_port": "自动化尺寸抓取器",
        },
    )
    write_dimension_library(library, targets[0])
    write_analysis_outputs(analysis, targets[1])
    write_outputs(result, targets[2], targets[3], summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-tsv", type=Path, default=PROJECT_DIR / "all-eu.tsv")
    parser.add_argument("--mapping-tsv", type=Path, default=PROJECT_DIR / "artifacts" / "KTYPES.tsv")
    parser.add_argument(
        "--dimension-tsv",
        type=Path,
        default=PROJECT_DIR / "artifacts" / "DIMENSION_GROUP.tsv",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--include-unmatched",
        action="store_true",
        help="保留原始表中尚无 READY 映射的 Ktype；默认只导出可入库记录",
    )
    parser.add_argument(
        "--run-pipeline",
        action="store_true",
        help="继续生成 00 尺寸库、01 尺寸分析表和 02 全量表候选",
    )
    parser.add_argument("--as-of-year", type=int, default=date.today().year)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source = read_tsv(args.input_tsv.resolve(), SOURCE_COLUMNS, "原始 Ktype TSV")
        mapping = read_tsv(args.mapping_tsv.resolve(), MAPPING_COLUMNS, "Ktype 映射 TSV")
        dimensions = read_tsv(args.dimension_tsv.resolve(), DIMENSION_COLUMNS, "尺寸组 TSV")
        source, mapping, dimensions, summary = build_pipeline_inputs(
            source,
            mapping,
            dimensions,
            include_unmatched=args.include_unmatched,
        )
        output_dir = args.output_dir.resolve()
        manifest = export_source_candidate(source, mapping, dimensions, output_dir, summary)
        if args.run_pipeline:
            manifest["pipeline"] = run_eu_pipeline(
                output_dir / "source",
                output_dir / "pipeline",
                args.as_of_year,
            )
            (output_dir / "ingest_status.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    except (ExportError, FileNotFoundError, pd.errors.ParserError, OSError, ValueError) as error:
        print(f"尺寸抓取结果接入失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
