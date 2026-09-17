from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from id_scheme import append_country_code, dimension_id
from full_table_schema import build_dimension_analysis


ROOT = Path(__file__).resolve().parent
SIZE_PROJECT = ROOT / "尺码计算"
PUBLIC_DIR = ROOT / "public"
US_COLUMNS = [
    "MAKE", "MODEL", "TRIM", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类",
    "L-MM", "W-MM", "H-MM", "销量合计", "车形", "前宽-MM", "后宽-MM", "参考侧高",
    "插片指数", "等效长", "自动尺码", "自动长度余量", "候选", "原因", "相差数值",
    "DIMENSION-ID",
]
BASE_COLUMNS = [
    "MAKE", "MODEL", "TRIM", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类",
    "L-MM", "W-MM", "H-MM", "销量合计", "DIMENSION-ID",
]
DIMENSION_COLUMNS = [
    "DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际", "YEAR", "分类",
    "L-IN", "W-IN", "H-IN", "参考车型", "备注", "迭代状态",
]


class RegionalDataError(ValueError):
    pass


def load_size_module():
    path = SIZE_PROJECT / "pandas_analysis.py"
    name = "shared_size_calculation"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RegionalDataError(f"无法加载尺码计算模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def require_columns(frame: pd.DataFrame, columns: list[str], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise RegionalDataError(f"{name} 缺少字段：{', '.join(missing)}")


def _clean_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _append_version(current: object, detail: object) -> str:
    current_text = _clean_text(current)
    detail_text = _clean_text(detail)
    if not detail_text or detail_text == "-":
        return current_text
    if current_text and detail_text.casefold() in current_text.casefold():
        return current_text
    return " ".join(value for value in [current_text, detail_text] if value)


def _dimension_detail(row: pd.Series) -> str:
    values = []
    for label, column in [("L", "L-MM"), ("W", "W-MM"), ("H", "H-MM")]:
        value = pd.to_numeric(pd.Series([row[column]]), errors="coerce").iloc[0]
        if pd.notna(value):
            values.append(f"{label}{int(value) if float(value).is_integer() else value:g}")
    return " ".join(values)


def build_dimension_library(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Normalize a regional base into the public size-library contract.

    Exact duplicate bodies are collapsed before IDs are assigned. When the
    public ID fields alone would collide for genuinely different dimensions,
    generation, a source body variant, and finally an explicit L/W/H variant
    are used in that order to keep the ID human-readable and unique.
    """
    require_columns(base, BASE_COLUMNS, "区域车型基表")
    work = base.copy()
    for column in ["MAKE", "MODEL", "TRIM", "版本", "结构", "CAB", "BED", "代际", "YEAR", "分类"]:
        work[column] = work[column].map(_clean_text)
    for column in ["L-MM", "W-MM", "H-MM", "销量合计"]:
        work[column] = pd.to_numeric(work[column], errors="coerce")
    work["销量合计"] = work["销量合计"].fillna(0)
    for column in ["_source_variant", "_reference", "_notes", "_iteration"]:
        if column not in work.columns:
            work[column] = ""
        work[column] = work[column].map(_clean_text)

    physical_key = [
        "MAKE", "MODEL", "版本", "结构", "CAB", "BED", "YEAR", "分类",
        "L-MM", "W-MM", "H-MM",
    ]
    sales = work.groupby(physical_key, dropna=False, sort=False)["销量合计"].transform("sum")
    work = work.loc[~work.duplicated(physical_key, keep="first")].copy()
    work["销量合计"] = sales.loc[work.index].values

    def refresh_ids() -> None:
        work["DIMENSION-ID"] = [dimension_id(row) for row in work.to_dict("records")]

    refresh_ids()
    collisions = work["DIMENSION-ID"].duplicated(keep=False)
    if collisions.any():
        work.loc[collisions, "版本"] = [
            _append_version(version, generation)
            for version, generation in zip(
                work.loc[collisions, "版本"], work.loc[collisions, "代际"], strict=True
            )
        ]
        refresh_ids()

    collisions = work["DIMENSION-ID"].duplicated(keep=False)
    if collisions.any():
        work.loc[collisions, "版本"] = [
            _append_version(version, variant)
            for version, variant in zip(
                work.loc[collisions, "版本"], work.loc[collisions, "_source_variant"], strict=True
            )
        ]
        refresh_ids()

    collisions = work["DIMENSION-ID"].duplicated(keep=False)
    if collisions.any():
        work.loc[collisions, "版本"] = [
            _append_version(row["版本"], _dimension_detail(row))
            for _, row in work.loc[collisions].iterrows()
        ]
        refresh_ids()

    if work["DIMENSION-ID"].eq("").any() or work["DIMENSION-ID"].duplicated().any():
        raise RegionalDataError("按公共格式生成的 DIMENSION-ID 存在空值或重复值")

    default_reference = work.apply(
        lambda row: " ".join(
            value for value in [row["YEAR"], row["MAKE"], row["MODEL"], row["版本"], row["结构"]]
            if value
        ),
        axis=1,
    )
    references = work["_reference"].where(work["_reference"].ne(""), default_reference)
    complete = work[["L-MM", "W-MM", "H-MM"]].notna().all(axis=1)
    iterations = work["_iteration"].where(
        work["_iteration"].ne(""), complete.map({True: "可入库", False: "待补尺寸"})
    )
    library = pd.DataFrame(
        {
            "DIMENSION-ID": work["DIMENSION-ID"],
            "MAKE": work["MAKE"],
            "MODEL": work["MODEL"],
            "版本": work["版本"],
            "CAB": work["CAB"],
            "BED": work["BED"],
            "结构": work["结构"],
            "代际": work["代际"],
            "YEAR": work["YEAR"],
            "分类": work["分类"],
            "L-IN": (work["L-MM"] / 25.4).round(1),
            "W-IN": (work["W-MM"] / 25.4).round(1),
            "H-IN": (work["H-MM"] / 25.4).round(1),
            "参考车型": references,
            "备注": work["_notes"],
            "迭代状态": iterations,
        }
    )
    library = library[DIMENSION_COLUMNS].sort_values("DIMENSION-ID", kind="stable").reset_index(drop=True)
    metadata = work[["DIMENSION-ID", "TRIM", "销量合计"]].copy()
    return library, metadata


def dimension_library_to_base(library: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    require_columns(library, DIMENSION_COLUMNS, "区域尺寸库")
    require_columns(metadata, ["DIMENSION-ID", "TRIM", "销量合计"], "区域尺寸库元数据")
    if library["DIMENSION-ID"].eq("").any() or library["DIMENSION-ID"].duplicated().any():
        raise RegionalDataError("区域尺寸库的 DIMENSION-ID 必须非空且唯一")
    merged = library.merge(metadata, on="DIMENSION-ID", how="left", validate="one_to_one")
    base = pd.DataFrame(
        {
            "MAKE": merged["MAKE"],
            "MODEL": merged["MODEL"],
            "TRIM": merged["TRIM"].fillna(merged["MODEL"]),
            "版本": merged["版本"],
            "结构": merged["结构"],
            "CAB": merged["CAB"],
            "BED": merged["BED"],
            "代际": merged["代际"],
            "YEAR": merged["YEAR"],
            "分类": merged["分类"],
            "L-MM": (pd.to_numeric(merged["L-IN"], errors="coerce") * 25.4).round(),
            "W-MM": (pd.to_numeric(merged["W-IN"], errors="coerce") * 25.4).round(),
            "H-MM": (pd.to_numeric(merged["H-IN"], errors="coerce") * 25.4).round(),
            "销量合计": pd.to_numeric(merged["销量合计"], errors="coerce").fillna(0),
            "DIMENSION-ID": merged["DIMENSION-ID"],
        }
    )
    return base[BASE_COLUMNS]


def assign_shapes(base: pd.DataFrame, mapping_path: Path) -> pd.Series:
    mapping = read_csv(mapping_path)
    require_columns(mapping, ["优先级", "分类", "结构正则", "车形"], "车形映射")
    mapping["优先级"] = pd.to_numeric(mapping["优先级"], errors="raise")
    mapping = mapping.sort_values("优先级", kind="stable")
    rules = [
        (str(row["分类"]).strip(), re.compile(str(row["结构正则"]), re.I), str(row["车形"]).strip())
        for _, row in mapping.iterrows()
    ]
    shapes: list[str] = []
    for _, row in base.iterrows():
        category = str(row["分类"]).strip()
        descriptor = " ".join(
            str(row[column]).strip() for column in ["结构", "版本", "CAB"] if str(row[column]).strip()
        )
        shape = next(
            (candidate for rule_category, pattern, candidate in rules
             if rule_category == category and pattern.search(descriptor)),
            "",
        )
        shapes.append(shape)
    return pd.Series(shapes, index=base.index, dtype="string")


def calculate_us_standard(
    base: pd.DataFrame,
    mapping_path: Path,
    country_code: str | None = None,
    include_analysis: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
    require_columns(base, BASE_COLUMNS, "区域车型基表")
    base = base[BASE_COLUMNS].copy()
    if base["DIMENSION-ID"].eq("").any() or base["DIMENSION-ID"].duplicated().any():
        raise RegionalDataError("区域车型基表的 DIMENSION-ID 必须非空且唯一")

    for column in ["L-MM", "W-MM", "H-MM", "销量合计"]:
        base[column] = pd.to_numeric(base[column], errors="coerce")
    for column in ["L-MM", "W-MM", "H-MM"]:
        nonblank = base[column].dropna()
        if nonblank.eq(nonblank.round()).all():
            base[column] = base[column].round().astype("Int64")
    base["销量合计"] = base["销量合计"].fillna(0)
    if (base["销量合计"] % 1 == 0).all():
        base["销量合计"] = base["销量合计"].astype("Int64")

    base["车形"] = assign_shapes(base, mapping_path)
    core = load_size_module()
    references = read_csv(PUBLIC_DIR / "参考尺寸计算.csv")
    bodies = base[["DIMENSION-ID", "车形"]].copy()
    vehicles = base.drop(columns=["车形"])
    result = core.add_body_dimensions(vehicles, bodies, references)
    result = core.add_equivalent_length(result, references)
    if country_code is not None:
        result["DIMENSION-ID"] = result["DIMENSION-ID"].map(
            lambda value: append_country_code(value, country_code)
        )
    analysis = build_dimension_analysis(result)
    analysis = analysis.sort_values("DIMENSION-ID", kind="stable").reset_index(drop=True)
    matcher = core.SizeMatcher(
        read_csv(SIZE_PROJECT / "rules" / "尺码匹配参数.csv"),
        read_csv(SIZE_PROJECT / "rules" / "尺码匹配规则.csv"),
    )
    result = matcher.apply(result)
    result = result[US_COLUMNS].sort_values("DIMENSION-ID", kind="stable").reset_index(drop=True)
    result["自动长度余量"] = core._compact_number_column(result["自动长度余量"])
    result["相差数值"] = core._compact_number_column(result["相差数值"])
    validate_output(result)
    return (result, analysis) if include_analysis else result


def validate_output(result: pd.DataFrame) -> None:
    if list(result.columns) != US_COLUMNS:
        raise RegionalDataError("发布表字段与 US 全量表标准不一致")
    if result["DIMENSION-ID"].duplicated().any():
        raise RegionalDataError("发布表 DIMENSION-ID 不唯一")
    blank_status = result["自动尺码"].astype("string").str.strip().eq("")
    if blank_status.any():
        raise RegionalDataError(f"发布表有 {int(blank_status.sum())} 行缺少尺码状态")


def output_summary(result: pd.DataFrame, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    shapes = result["车形"].astype("string")
    summary: dict[str, Any] = {
        "rows": int(len(result)),
        "columns": list(result.columns),
        "unique_dimension_ids": int(result["DIMENSION-ID"].nunique()),
        "sales_total": int(pd.to_numeric(result["销量合计"], errors="coerce").sum()),
        "matched_sizes": int((~result["自动尺码"].isin(["数据不全", "无可用尺码"])).sum()),
        "unavailable_sizes": int(result["自动尺码"].eq("无可用尺码").sum()),
        "incomplete_rows": int(result["自动尺码"].eq("数据不全").sum()),
        "missing_shapes": int((shapes.isna() | shapes.str.strip().eq("")).sum()),
    }
    if extra:
        summary.update(extra)
    return summary


def write_outputs(
    result: pd.DataFrame,
    output_path: Path,
    status_path: Path,
    summary: dict[str, Any],
    publish_path: Path | None = None,
) -> None:
    targets = [output_path]
    if publish_path is not None and publish_path.resolve() != output_path.resolve():
        targets.append(publish_path)
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(
            target,
            index=False,
            encoding="utf-8-sig",
            lineterminator="\n",
            quoting=csv.QUOTE_MINIMAL,
            na_rep="",
        )
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_analysis_outputs(
    analysis: pd.DataFrame,
    output_path: Path,
    publish_path: Path | None = None,
) -> None:
    expected = [column for column in US_COLUMNS if column not in {
        "自动尺码", "自动长度余量", "候选", "原因", "相差数值"
    }]
    if list(analysis.columns) != expected:
        raise RegionalDataError("尺寸分析表字段不符合标准")
    targets = [output_path]
    if publish_path is not None and publish_path.resolve() != output_path.resolve():
        targets.append(publish_path)
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        analysis.to_csv(
            target,
            index=False,
            encoding="utf-8-sig",
            lineterminator="\n",
            quoting=csv.QUOTE_MINIMAL,
            na_rep="",
        )


def write_dimension_library(
    library: pd.DataFrame,
    output_path: Path,
    publish_path: Path | None = None,
) -> None:
    if list(library.columns) != DIMENSION_COLUMNS:
        raise RegionalDataError("尺寸库字段与 public/尺寸库.csv 标准不一致")
    targets = [output_path]
    if publish_path is not None and publish_path.resolve() != output_path.resolve():
        targets.append(publish_path)
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        library.to_csv(
            target,
            index=False,
            encoding="utf-8-sig",
            lineterminator="\n",
            quoting=csv.QUOTE_MINIMAL,
            na_rep="",
        )
