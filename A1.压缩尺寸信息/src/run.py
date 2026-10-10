#!/usr/bin/env python3
"""把 A0.尺码计算/output 的产线全量表（国别线 <国别>/全量/全量表.csv，店铺线 US/店铺/店铺全量_<店铺>.csv）按产线（data/产线.yaml：US、HNT、TM、TM_拆分、EU、RU）分别压缩为尺码表。

压缩引擎为内置的 src/sizechart（与网站流水线原压缩步骤同一算法，见 src/sizechart/VENDORED.md）：
按原子事实（品牌、车型、结构/CAB/BED、版本、年份）校验，非皮卡与皮卡分表输出。
默认交付所有已配置产线的高度压缩（有损）结果：
  <产线>/压缩尺码表.csv       非皮卡高度压缩（车型组合/版本/结构两两合并，逐次原子校验）
  <产线>/压缩尺码表_皮卡.csv  皮卡高度压缩
  <产线>/压缩来源.csv         两张压缩表每条记录（压缩类型 + 记录序号）覆盖的全量表行、覆盖年份与长宽高
其中 HNT、TM、TM_拆分均读取 US 店铺全量表；无损表不作为 output 流水线接口。
代号区域（data/产线.yaml，当前 US）的产线在首列加 CODE：02.代码映射/output/车型编码映射.csv 的
MAKE_CODE + MODEL_CODE + YEARCODE（与 DIMENSION-CODE 同一规则）。
两张交付表末列为 尺码销量总和 与来源尺寸（记录命中的同尺码原子的长宽高最大/最小值 mm 及取到该值的年份）。
全部产线压缩成功后才创建不可覆盖的 artifacts/<批次>/（lib/artifact_batch.py）：run.json 记录上游输入引用、
data/ 规则快照（sha256 + git commit）与输出 sha256；extra/ 保存压缩 log、原子事实表、原子检查问题（gzip），
随后原子更新 output/。
"""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd
import yaml

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "src" / "sizechart"))
if str(PROJECT_DIR.parent / "lib") not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR.parent / "lib"))

from artifact_batch import RunBatch  # noqa: E402

import process_tsv as engine  # noqa: E402
from check_atom import build_atom_check  # noqa: E402
from field_profile import load_field_profile  # noqa: E402
from non_pickup_validation import MergeRules  # noqa: E402

UPSTREAM_OUTPUT = PROJECT_DIR.parent / "A0.尺码计算" / "output"
CODE_MAPPING = PROJECT_DIR.parent / "02.代码映射" / "output" / "车型编码映射.csv"
REGIONS = ("US", "EU", "RU")
DATA_DIR = PROJECT_DIR / "data"
FIELD_PROFILE = "字段映射.yaml"
MODEL_COMBO = "车型组合.tsv"
LINES_CONFIG = "产线.yaml"
MERGE_RULES = "合并规则.yaml"
# A0 全量表逐行销量（按 DIMENSION-ID）与压缩表新增的记录销量列
SALES_SOURCE_COLUMN = "尺寸组销量"
SALES_COLUMN = "尺码销量总和"
# 记录来源尺寸：维度名 -> A0 全量表列；压缩表在 尺码销量总和 之后输出各维度最大/最小值（mm）及取到该值的年份
DIMENSION_SOURCES = {"长": "L-MM", "宽": "W-MM", "高": "H-MM"}
DIMENSION_EXTREMES = (("最大", "max"), ("最小", "min"))
DIMENSION_COLUMNS = [f"{extreme}{name}{suffix}" for name in DIMENSION_SOURCES for extreme, _ in DIMENSION_EXTREMES for suffix in ("-MM", "年份")]
# 来源明细（<产线>/压缩来源.csv）：压缩记录覆盖的全量表行，供网站展开查看各年份长宽高
SOURCE_ROW_COLUMNS = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "结构", "CAB", "BED"]
SOURCE_COLUMNS = ["压缩类型", "记录序号", *SOURCE_ROW_COLUMNS, "YEAR", *DIMENSION_SOURCES.values()]
CODE_COLUMN = "CODE"
ATOM_KEY = ["压缩类型", "MAKE", "MODEL", "YEAR", "VERSION", "CONST", "CAB", "BED_FT", "BACKSIZE"]


class CompressionError(ValueError):
    pass


def upstream_file(line: str, region: str | None = None) -> str:
    """A0 output 中产线全量表的相对路径：国别线读区域全量表，店铺线读该区域的店铺全量表。"""
    region = region or line
    if line == region:
        return f"{region}/全量/全量表.csv"
    return f"{region}/店铺/店铺全量_{line}.csv"


def output_names(line: str) -> dict[str, str]:
    """默认交付物：按产线目录存放，文件名不再标注“有损”。"""
    return {
        "non_pickup_high": f"{line}/压缩尺码表.csv",
        "pickup_high": f"{line}/压缩尺码表_皮卡.csv",
        "sources": f"{line}/压缩来源.csv",
    }


def load_lines(data_dir: Path = DATA_DIR) -> dict[str, str]:
    """产线 -> 区域（保持配置顺序）。"""
    config = yaml.safe_load((data_dir / LINES_CONFIG).read_text(encoding="utf-8")) or {}
    lines = {str(name): str((body or {}).get("区域", "")) for name, body in (config.get("产线") or {}).items()}
    bad = {name: region for name, region in lines.items() if region not in REGIONS}
    if not lines or bad:
        raise CompressionError(f"{LINES_CONFIG} 产线为空或区域无效：{bad}")
    return lines


def load_size_formats(data_dir: Path = DATA_DIR) -> dict[str, dict]:
    """产线 -> 尺码输出格式 {"尺码列名": 输出中 BACKSIZE 的列名, "附加尺码列": [按尺码从全量表回填的列]}。"""
    config = yaml.safe_load((data_dir / LINES_CONFIG).read_text(encoding="utf-8")) or {}
    formats = {}
    for name, body in (config.get("产线") or {}).items():
        body = body or {}
        extra = [str(column) for column in body.get("附加尺码列") or []]
        formats[str(name)] = {"尺码列名": str(body.get("尺码列名") or "BACKSIZE"), "附加尺码列": extra}
    return formats


def apply_size_format(tables: dict[str, pd.DataFrame], frame: pd.DataFrame, field_profile: dict, size_format: dict | None) -> None:
    """按产线格式在 BACKSIZE 后回填附加尺码列（如 RU 的 OZON尺码、发货尺码），再把 BACKSIZE 改名。

    附加列取自全量表：同一匹配尺码必须对应唯一的附加尺码组合，否则运行失败。
    """
    if not size_format:
        return
    extra, size_name = size_format["附加尺码列"], size_format["尺码列名"]
    if extra:
        missing = [column for column in extra if column not in frame.columns]
        if missing:
            raise CompressionError(f"全量表缺少附加尺码列：{missing}")
        sizes = engine.normalize_input_schema(frame, field_profile=field_profile)[engine.BACKSIZE_SOURCE_COLUMN].map(engine.normalize_text)
        pairs = pd.concat([sizes.rename("BACKSIZE"), frame[extra].apply(lambda column: column.map(engine.normalize_text))], axis=1)
        pairs = pairs[pairs["BACKSIZE"] != ""].drop_duplicates()
        conflicts = sorted(pairs.loc[pairs["BACKSIZE"].duplicated(), "BACKSIZE"].unique())
        if conflicts:
            raise CompressionError(f"尺码对应多个附加尺码组合：{conflicts}")
        mapping = pairs.set_index("BACKSIZE")
    for key in ("non_pickup_high", "pickup_high"):
        table = tables[key]
        position = table.columns.get_loc("BACKSIZE") + 1
        for offset, column in enumerate(extra):
            table.insert(position + offset, column, table["BACKSIZE"].map(engine.normalize_text).map(mapping[column]).fillna(""))
        tables[key] = table.rename(columns={"BACKSIZE": size_name})


def load_code_regions(data_dir: Path = DATA_DIR) -> set[str]:
    """在压缩表加 CODE 列的区域（data/产线.yaml 代号区域）。"""
    config = yaml.safe_load((data_dir / LINES_CONFIG).read_text(encoding="utf-8")) or {}
    regions = {str(region) for region in config.get("代号区域") or []}
    if regions - set(REGIONS):
        raise CompressionError(f"{LINES_CONFIG} 代号区域无效：{sorted(regions - set(REGIONS))}")
    return regions


def name_key(text: str) -> str:
    """与 02.代码映射 相同的名称匹配键：NFKC、去首尾空格、忽略大小写。"""
    return unicodedata.normalize("NFKC", str(text)).strip().casefold()


def load_code_mapping(path: Path = CODE_MAPPING) -> dict[tuple[str, str, str], str]:
    """(REGION, MAKE 键, MODEL 键) -> MAKE_CODE + MODEL_CODE。"""
    frame = read_frame(path)
    missing = {"REGION", "MAKE", "MODEL", "MAKE_CODE", "MODEL_CODE"} - set(frame.columns)
    if missing:
        raise CompressionError(f"{path.name} 缺少列：{sorted(missing)}")
    mapping: dict[tuple[str, str, str], str] = {}
    for item in frame.itertuples(index=False):
        key = (item.REGION.strip(), name_key(item.MAKE), name_key(item.MODEL))
        if key in mapping:
            raise CompressionError(f"{path.name} 车型重复：{item.REGION} {item.MAKE} {item.MODEL}")
        mapping[key] = item.MAKE_CODE + item.MODEL_CODE
    return mapping


def year_code(year: str) -> str:
    """YEARCODE：年份区间两端后两位（1956-2012 -> 5612，单年 1994 -> 9494），同 02.代码映射。"""
    match = re.fullmatch(r"(\d{4})(?:\s*-\s*(\d{4}))?", str(year).strip())
    if not match:
        raise CompressionError(f"YEAR 无法生成 YEARCODE：{year!r}")
    return match.group(1)[2:] + (match.group(2) or match.group(1))[2:]


def apply_codes(tables: dict[str, pd.DataFrame], mapping: dict[tuple[str, str, str], str], region: str, line: str) -> None:
    """在两张交付表首列插入 CODE = MAKE_CODE + MODEL_CODE + YEARCODE；车型不在映射中则运行失败。"""
    for key in ("non_pickup_high", "pickup_high"):
        table = tables[key]
        prefixes = [mapping.get((region, name_key(make), name_key(model))) for make, model in zip(table["MAKE"], table["MODEL"])]
        missing = sorted({f"{make} {model}" for make, model, prefix in zip(table["MAKE"], table["MODEL"], prefixes) if prefix is None})
        if missing:
            raise CompressionError(f"{line} 车型不在 02.代码映射 {region} 车型编码映射中：{missing[:20]}")
        table.insert(0, CODE_COLUMN, [prefix + year_code(year) for prefix, year in zip(prefixes, table["YEAR"])])


def load_merge_rules(data_dir: Path = DATA_DIR) -> MergeRules:
    """高度压缩两两合并的扩张约束（data/合并规则.yaml）。"""
    config = yaml.safe_load((data_dir / MERGE_RULES).read_text(encoding="utf-8")) or {}
    gap = config.get("最大空档年数")
    if gap is not None and (not isinstance(gap, int) or gap < 0):
        raise CompressionError(f"{MERGE_RULES} 最大空档年数须为非负整数或留空：{gap!r}")
    return MergeRules(max_gap_years=gap, gap_exempt_sizes=frozenset(str(size) for size in config.get("空档豁免尺码") or []))


def default_lines(lines: dict[str, str]) -> dict[str, str]:
    """默认交付所有配置产线；网站可再按用途排除 EU/RU。"""
    return dict(lines)


def region_of(dimension_id: str) -> str:
    token = dimension_id.rsplit(" ", 1)[-1] if dimension_id else ""
    return token if token in REGIONS else ""


def read_frame(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise CompressionError(f"找不到输入文件：{path}")
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig", keep_default_na=False)


def write_csv_atomic(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    compression = "gzip" if path.suffix == ".gz" else None  # 临时文件名不带 .gz，压缩方式须显式指定
    frame.to_csv(temporary, index=False, encoding="utf-8-sig", lineterminator="\n", compression=compression)
    os.replace(temporary, path)


def export_or_empty(frame: pd.DataFrame, exporter, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns) if frame.empty else exporter(frame)


def source_atoms(frame: pd.DataFrame, field_profile: dict) -> pd.DataFrame:
    """全量表每行展开出的原子事实（与压缩引擎相同的展开规则）：ATOM_KEY + 行号（frame 索引）+ 份数（该行展开的原子数）。

    非皮卡按 车型（前台车型拆分）× 年份 × 结构 展开，皮卡按 年份 × CAB 展开。
    """
    work = engine.normalize_input_schema(frame, field_profile=field_profile)
    text = lambda column: work[column].map(engine.normalize_text) if column in work.columns else pd.Series("", index=work.index)  # noqa: E731
    category, cab, bed, size = text("分类"), text("驾驶室类型"), text("货斗长度_ft"), text(engine.BACKSIZE_SOURCE_COLUMN)
    if category.str.contains("皮卡", na=False).any():
        pickup = category.str.contains("皮卡", na=False)
    else:
        pickup = (cab != "") | (bed != "")
    brand, model, version, structure, years = text("品牌"), text("前台车型"), text("版本"), text("结构"), text("年份区间")

    atoms: list[tuple] = []
    for index in work.index[size != ""]:
        year_list = engine.parse_year_list(years[index])
        if pickup[index]:
            keys = {
                ("皮卡", brand[index], model[index], str(year), version[index], "", cab_atom, bed[index], size[index])
                for year in year_list
                for cab_atom in engine.split_joined_atoms(cab[index])
            }
        else:
            keys = {
                ("非皮卡", brand[index], engine.normalize_text(model_atom), str(year), version[index], engine.normalize_text(const), "", "", size[index])
                for model_atom in engine.split_front_model_atoms(model[index])
                for year in year_list
                for const in engine.split_const_atoms(structure[index])
            }
        atoms.extend((*key, index, len(keys)) for key in keys)
    return pd.DataFrame(atoms, columns=[*ATOM_KEY, "行号", "份数"])


def source_atom_sales(frame: pd.DataFrame, atoms: pd.DataFrame) -> pd.DataFrame:
    """把全量表每行的尺寸组销量均摊到它展开出的原子事实；返回按原子键（ATOM_KEY）汇总的 销量 列。"""
    if SALES_SOURCE_COLUMN not in frame.columns:
        raise CompressionError(f"全量表缺少 {SALES_SOURCE_COLUMN} 列")
    sales = pd.to_numeric(frame[SALES_SOURCE_COLUMN].replace("", "0"), errors="coerce")
    if sales.isna().any():
        raise CompressionError(f"全量表 {SALES_SOURCE_COLUMN} 存在非数值")
    result = atoms[ATOM_KEY].copy()
    result["销量"] = [float(sales[index]) / count for index, count in zip(atoms["行号"], atoms["份数"])]
    return result.groupby(ATOM_KEY, as_index=False, sort=False)["销量"].sum()


def source_dimensions(frame: pd.DataFrame) -> pd.DataFrame:
    """全量表各行的长宽高（mm，缺值为 NaN），列名为维度名（长、宽、高）。"""
    missing = [column for column in DIMENSION_SOURCES.values() if column not in frame.columns]
    if missing:
        raise CompressionError(f"全量表缺少尺寸列：{missing}")
    result = pd.DataFrame(index=frame.index)
    for name, column in DIMENSION_SOURCES.items():
        text = frame[column].map(engine.normalize_text)
        result[name] = pd.to_numeric(text, errors="coerce")
        if (result[name].isna() & (text != "")).any():
            raise CompressionError(f"全量表 {column} 存在非数值")
    return result


def same_size_hits(table: pd.DataFrame, check: pd.DataFrame):
    """原子检查命中关系中与原子尺码相同的压缩记录：逐原子产出 (原子索引, [记录索引])，未命中同尺码记录时列表为空。"""
    line_sizes = {index + 2: engine.normalize_text(value) for index, value in table["BACKSIZE"].items()}
    for atom_row, lines, atom_size in zip(check["原子行号"], check["压缩行号"], check["BACKSIZE"]):
        targets = [int(line) for line in str(lines).split("/") if line and line_sizes.get(int(line)) == atom_size]
        yield int(atom_row) - 2, [line - 2 for line in targets]


def atom_export_keys(atom_export: pd.DataFrame) -> pd.DataFrame:
    return atom_export[ATOM_KEY].astype(str).map(engine.normalize_text) if not atom_export.empty else atom_export[ATOM_KEY]


def allocate_record_sales(atom_export: pd.DataFrame, atom_sales: pd.DataFrame, table: pd.DataFrame, check: pd.DataFrame) -> tuple[pd.Series, dict]:
    """按原子检查的命中关系把原子销量汇总到压缩记录；原子命中多条同尺码记录时均分。"""
    keys = atom_export_keys(atom_export)
    sales_by_key = atom_sales.set_index(ATOM_KEY)["销量"]
    atom_values = pd.Series(
        [float(sales_by_key.get(tuple(key), 0.0)) for key in keys.itertuples(index=False)], index=atom_export.index
    )
    totals = pd.Series(0.0, index=table.index)
    unallocated = 0.0
    for atom, targets in same_size_hits(table, check):
        value = atom_values[atom]
        if not targets:
            unallocated += value
            continue
        for target in targets:
            totals[target] += value / len(targets)
    audit = {"原子销量": round(float(atom_values.sum())), "已分配": round(float(totals.sum())), "未命中同尺码记录": round(unallocated)}
    return totals.round().astype("Int64"), audit


def year_ranges(years) -> str:
    """年份集合 -> 连续区间以 / 分隔（2019-2021/2024），与压缩引擎 parse_year_list 可互逆。"""
    ordered = sorted(set(int(year) for year in years))
    parts, start = [], None
    for position, year in enumerate(ordered):
        start = year if start is None else start
        if position + 1 == len(ordered) or ordered[position + 1] != year + 1:
            parts.append(str(year) if start == year else f"{start}-{year}")
            start = None
    return "/".join(parts)


def millimetres(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def record_source_hits(atom_export: pd.DataFrame, atoms: pd.DataFrame, table: pd.DataFrame, check: pd.DataFrame) -> pd.DataFrame:
    """压缩记录命中的同尺码原子（原子检查）回溯到展开出它的全量表行：去重的 (记录, 行号, 年份)。

    合理扩张出的无原子年份不在其中；同一原子来自多行时各行都计入。
    """
    pairs = [(target, atom) for atom, targets in same_size_hits(table, check) for target in targets]
    if not pairs:
        return pd.DataFrame(columns=["记录", "行号", "年份"])
    keys = atom_export_keys(atom_export).assign(原子=atom_export.index)
    hits = pd.DataFrame(pairs, columns=["记录", "原子"]).merge(keys, on="原子").merge(atoms[[*ATOM_KEY, "行号"]], on=ATOM_KEY)
    hits["年份"] = hits["YEAR"].astype(int)
    return hits[["记录", "行号", "年份"]].drop_duplicates(ignore_index=True)


def record_dimensions(hits: pd.DataFrame, dimensions: pd.DataFrame, table: pd.DataFrame) -> pd.DataFrame:
    """压缩记录的来源尺寸：所覆盖来源行 × 年份中各维度的最大/最小值，及取到该值的年份。"""
    result = pd.DataFrame("", index=table.index, columns=DIMENSION_COLUMNS)
    hits = hits.join(dimensions, on="行号")
    for name in DIMENSION_SOURCES:
        valid = hits.dropna(subset=[name])
        if valid.empty:
            continue
        for extreme, how in DIMENSION_EXTREMES:
            grouped = valid[valid[name] == valid.groupby("记录")[name].transform(how)].groupby("记录")
            values = grouped[name].first()
            result.loc[values.index, f"{extreme}{name}-MM"] = values.map(millimetres)
            result.loc[values.index, f"{extreme}{name}年份"] = grouped["年份"].agg(year_ranges)
    return result


def record_sources(hits: pd.DataFrame, frame: pd.DataFrame, kind: str) -> pd.DataFrame:
    """来源明细：每条压缩记录（记录序号 = 压缩表数据行序号，从 1 起）覆盖的全量表行及其被覆盖的年份与长宽高。"""
    if hits.empty:
        return pd.DataFrame(columns=SOURCE_COLUMNS)
    grouped = hits.groupby(["记录", "行号"], sort=False)["年份"]
    rows = grouped.agg(year_ranges).rename("YEAR").reset_index().assign(首年=grouped.min().to_numpy())
    rows = rows.sort_values(["记录", "首年", "行号"], kind="stable", ignore_index=True)
    result = pd.DataFrame({"压缩类型": kind, "记录序号": rows["记录"] + 1})
    for column in SOURCE_ROW_COLUMNS:
        values = frame[column].map(engine.normalize_text) if column in frame.columns else pd.Series("", index=frame.index)
        result[column] = values.loc[rows["行号"]].to_numpy()
    result["YEAR"] = rows["YEAR"]
    for column in DIMENSION_SOURCES.values():
        result[column] = frame[column].map(engine.normalize_text).loc[rows["行号"]].to_numpy()
    return result[SOURCE_COLUMNS]


def compress_line(
    line: str,
    frame: pd.DataFrame,
    field_profile: dict,
    region: str | None = None,
    progress: bool = False,
    merge_rules: MergeRules | None = None,
    size_format: dict | None = None,
) -> dict:
    """返回 {"tables": {键: DataFrame}, "log": DataFrame, "atoms": DataFrame, "checks": {类型: DataFrame}, "sales": {类型: 审计}}。"""
    region = region or line
    if "DIMENSION-ID" in frame.columns:
        wrong_region = set(frame["DIMENSION-ID"].map(region_of)) - {region}
        if wrong_region:
            raise CompressionError(f"{upstream_file(line, region)} 含非 {region} 的 DIMENSION-ID：{sorted(wrong_region)}")
    reporter = engine.ProgressReporter(interval_seconds=10.0, enabled=progress)
    non_lossless, _, non_high, pick_lossless, pick_high, log_df, atom_df = engine.transform_all_outputs(
        frame, progress=reporter, field_profile=field_profile, merge_rules=merge_rules or load_merge_rules()
    )
    names = output_names(line)
    tables = {
        "non_pickup_lossless": export_or_empty(non_lossless, engine.export_non_pickup_table, engine.NON_PICKUP_EXPORT_COLUMNS),
        "non_pickup_high": export_or_empty(non_high, engine.export_non_pickup_table, engine.NON_PICKUP_EXPORT_COLUMNS),
        "pickup_lossless": export_or_empty(pick_lossless, engine.export_pickup_table, engine.PICKUP_EXPORT_COLUMNS),
        "pickup_high": export_or_empty(pick_high, engine.export_pickup_table, engine.PICKUP_EXPORT_COLUMNS),
    }
    if all(table.empty for table in tables.values()):
        raise CompressionError(f"{line} 没有可压缩的行（检查 最终尺码/年份区间 等字段映射）")

    atom_export = engine.export_table(atom_df)
    checks: dict[str, pd.DataFrame] = {}
    kinds = atom_export["压缩类型"].map(engine.normalize_text) if not atom_export.empty else pd.Series(dtype=str)
    if not tables["non_pickup_high"].empty:
        checks["非皮卡"] = build_atom_check(atom_export[kinds == "非皮卡"].copy(), tables["non_pickup_high"], progress=reporter, progress_phase="非皮卡原子检查")
    if not tables["pickup_high"].empty:
        checks["皮卡"] = build_atom_check(atom_export[kinds == "皮卡"].copy(), tables["pickup_high"], progress=reporter, progress_phase="皮卡原子检查")

    # 尺码销量总和：压缩记录所覆盖原子事实的尺寸组销量之和（行销量按原子均摊）；来源尺寸：所覆盖原子的长宽高最大/最小值及年份
    atoms = source_atoms(frame, field_profile)
    atom_sales = source_atom_sales(frame, atoms)
    dimensions = source_dimensions(frame)
    export_keys = set(atom_export[ATOM_KEY].astype(str).map(engine.normalize_text).itertuples(index=False, name=None))
    sales_keys = set(atom_sales[ATOM_KEY].itertuples(index=False, name=None))
    if export_keys != sales_keys:
        raise CompressionError(
            f"{line} 销量原子与压缩原子不一致：仅销量 {len(sales_keys - export_keys)}，仅压缩 {len(export_keys - sales_keys)}"
        )
    sales_audit: dict[str, dict] = {}
    sources: list[pd.DataFrame] = []
    for kind, key in (("非皮卡", "non_pickup_high"), ("皮卡", "pickup_high")):
        table = tables[key]
        if kind in checks:
            table[SALES_COLUMN], sales_audit[kind] = allocate_record_sales(atom_export[kinds == kind], atom_sales, table, checks[kind])
            hits = record_source_hits(atom_export[kinds == kind], atoms, table, checks[kind])
        else:
            table[SALES_COLUMN] = pd.Series(dtype="Int64")
            hits = pd.DataFrame(columns=["记录", "行号", "年份"])
        record_dims = record_dimensions(hits, dimensions, table)
        for column in DIMENSION_COLUMNS:
            table[column] = record_dims[column]
        sources.append(record_sources(hits, frame, kind))
    tables["sources"] = pd.concat(sources, ignore_index=True)
    apply_size_format(tables, frame, field_profile, size_format)
    return {"names": names, "tables": tables, "log": engine.export_table(log_df), "atoms": atom_export, "checks": checks, "sales": sales_audit}


FALLBACK_REASONS = ("原子事实对应多条候选记录", "无原子空档", "原子事实未被候选记录覆盖", "命中尺码", "原子事实命中不同尺码候选记录", "候选合并范围内没有可验证原子事实", "候选年份区间内存在同BED不同尺码事实")


def fallback_category(reason: str) -> str:
    return next((name for name in FALLBACK_REASONS if name in reason), reason)


def summarize(result: dict) -> dict:
    log = result["log"]
    fallback = log[log["结果"] == "fallback"] if "结果" in log.columns else log.iloc[0:0]
    return {
        "行数": {name: int(len(result["tables"][key])) for key, name in result["names"].items()},
        "原子事实数": int(len(result["atoms"])),
        "两两合并": dict(Counter(log["结果"])) if "结果" in log.columns else {},
        "fallback原因": dict(Counter(fallback["原因"].map(fallback_category))) if "原因" in fallback.columns else {},
        "原子检查": {kind: dict(Counter(check["检查结果"])) for kind, check in result["checks"].items()},
        SALES_COLUMN: result["sales"],
    }


def compress_file(line: str, path: Path, region: str, data_dir: Path, progress: bool = False) -> dict:
    """子进程入口：读取一条产线的全量表并压缩。"""
    field_profile = load_field_profile((data_dir / FIELD_PROFILE).resolve())
    return compress_line(
        line, read_frame(path), field_profile, region, progress, load_merge_rules(data_dir), load_size_formats(data_dir).get(line)
    )


def run(
    source_dir: Path = UPSTREAM_OUTPUT,
    data_dir: Path = DATA_DIR,
    output_dir: Path = PROJECT_DIR / "output",
    artifacts_dir: Path = PROJECT_DIR / "artifacts",
    progress: bool = False,
    workers: int = 0,
    code_mapping: Path = CODE_MAPPING,
) -> dict:
    """workers：并行进程数，0 = 每条产线一个进程（上限 CPU 数），1 = 当前进程串行。"""
    lines = default_lines(load_lines(data_dir))
    code_regions = load_code_regions(data_dir)
    codes = load_code_mapping(code_mapping) if code_regions & set(lines.values()) else {}
    inputs = {line: source_dir / upstream_file(line, lines[line]) for line in lines}
    for path in inputs.values():
        if not path.is_file():
            raise CompressionError(f"找不到输入文件：{path}")
    jobs = [(line, path, lines[line], data_dir, progress) for line, path in inputs.items()]
    workers = workers or min(len(jobs), os.cpu_count() or 1)
    if workers == 1:
        results = {job[0]: compress_file(*job) for job in jobs}
    else:
        # 每条产线独立进程：互不累积缓存状态，总耗时取决于最慢的产线
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {job[0]: executor.submit(compress_file, *job) for job in jobs}
            results = {line: future.result() for line, future in futures.items()}
    for line, result in results.items():
        if lines[line] in code_regions:
            apply_codes(result["tables"], codes, lines[line], line)

    rules_in_data = data_dir.name == "data"
    with RunBatch.create(artifacts_dir, "compress-by-line", data_dir=data_dir if rules_in_data else None) as batch:
        # 上游已发布的全量表与代码映射只记引用；字段映射/产线/合并规则/车型组合 均在 data/，由规则快照记录
        for path in inputs.values():
            batch.input(path, name=path.relative_to(source_dir).as_posix())
        if not rules_in_data:
            for name in (FIELD_PROFILE, LINES_CONFIG, MERGE_RULES):
                batch.input(data_dir / name)
        if Path(engine.DEFAULT_MODEL_COMBO_PATH).resolve().parent != data_dir.resolve():
            batch.input(Path(engine.DEFAULT_MODEL_COMBO_PATH), name=MODEL_COMBO)
        if codes:
            batch.input(code_mapping, name=code_mapping.name)

        status_lines = {}
        for line, result in results.items():
            for key, name in result["names"].items():
                write_csv_atomic(batch.output(name), result["tables"][key])
            log = result["log"]
            # 只留成功合并记录；fallback（数量大）按原因计数写入 run.json，完整 log 可重跑得到
            write_csv_atomic(batch.extra(f"压缩log_{line}.csv"), log[log["结果"] == "success"] if "结果" in log.columns else log)
            write_csv_atomic(batch.extra(f"原子事实表_{line}.csv"), result["atoms"])
            for kind, check in result["checks"].items():
                issues = check[check["检查结果"] != "OK"]
                if not issues.empty:
                    write_csv_atomic(batch.extra(f"原子检查问题_{line}_{kind}.csv"), issues)
            status_lines[line] = {"区域": lines[line], "上游输入": upstream_file(line, lines[line]), **summarize(result)}
        record = batch.finish({"lines": status_lines}, publish_to=output_dir)
    return {**record["status"], "outputs": [item["file"] for item in record["outputs"]], "artifact": str(batch.directory)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按产线把 A0 全量表压缩为尺码表（非皮卡/皮卡 × 无损/有损）")
    parser.add_argument("--source-dir", type=Path, default=UPSTREAM_OUTPUT)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--artifacts-dir", type=Path, default=PROJECT_DIR / "artifacts")
    parser.add_argument("--code-mapping", type=Path, default=CODE_MAPPING, help="02.代码映射 车型编码映射.csv")
    parser.add_argument("--no-progress", action="store_true", help="不输出周期进度")
    parser.add_argument("--workers", type=int, default=0, help="并行进程数；0 = 每条产线一个（上限 CPU 数），1 = 串行")
    args = parser.parse_args(argv)
    try:
        result = run(
            args.source_dir.resolve(), args.data_dir.resolve(),
            args.output_dir.resolve(), args.artifacts_dir.resolve(),
            progress=not args.no_progress,
            workers=args.workers,
            code_mapping=args.code_mapping.resolve(),
        )
    except CompressionError as error:
        print(f"运行失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
