"""多尺码歧义来源诊断（只读：不改 output/、artifacts/，不参与正式运行）。

压缩原子检查的 MULTI 表示同一对外原子（压缩类型、品牌、车型、年份、版本、结构、CAB、BED）命中了不同尺码的压缩记录。
本模块把 MULTI 分成两类：

- **原有歧义**：A0 全量表按压缩引擎同一规则展开后，同一原子键本身就对应多个尺码（多条 DIMENSION-ID 在对外
  字段上无法区分，如 Jaguar XJ Sedan 1979-1992 gen1 与 1988-1994 gen2 的重叠年份）。压缩无法消除，需要上游
  补区分字段或业务决定如何表达；
- **压缩新增歧义**：原子键在源头只对应一个尺码，是压缩合并/扩张让它命中了不同尺码记录。

对原有歧义，按参与的 DIMENSION-ID 组合归并年份，列出能区分这些身份的 A0 字段（代际、车形、长宽高等）和涉及销量。

    python src/ambiguity.py                          # 全部产线，写到仓库 reports/尺码歧义诊断/
    python src/ambiguity.py --lines US,EU,RU --out <目录>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run as compression  # noqa: E402

PROJECT_DIR = compression.PROJECT_DIR
REPO_ROOT = PROJECT_DIR.parent
DEFAULT_OUT = REPO_ROOT / "reports" / "尺码歧义诊断"
ATOM_FIELDS = compression.ATOM_KEY[:-1]  # 不含 BACKSIZE 的对外原子键
SIZE = compression.ATOM_KEY[-1]
# 可能区分同键身份的 A0 字段：对外原子键之外、能说明“为什么是两条身份”的信息
DISTINGUISHING_COLUMNS = ["代际", "车形", "SHAPE", "分类", "L-MM", "W-MM", "H-MM"]
SOURCE = "原有歧义"
INTRODUCED = "压缩新增歧义"


def year_ranges(years: list[int]) -> str:
    """[1988, 1989, 1990, 1995] -> '1988-1990/1995'。"""
    parts: list[str] = []
    for year in sorted(set(years)):
        if parts and year == int(parts[-1].split("-")[-1]) + 1:
            parts[-1] = f"{parts[-1].split('-')[0]}-{year}"
        else:
            parts.append(str(year))
    return "/".join(parts)


def source_atom_rows(frame: pd.DataFrame, field_profile: dict) -> pd.DataFrame:
    """全量表展开出的原子（与压缩引擎同一规则），附来源行的 DIMENSION-ID 与按原子均摊的尺寸组销量。"""
    atoms = compression.source_atoms(frame, field_profile)
    sales = pd.to_numeric(frame[compression.SALES_SOURCE_COLUMN].replace("", "0"), errors="coerce").fillna(0.0)
    atoms["DIMENSION-ID"] = frame.loc[atoms["行号"], "DIMENSION-ID"].to_numpy()
    atoms["原子销量"] = [float(sales[index]) / count for index, count in zip(atoms["行号"], atoms["份数"])]
    return atoms


def ambiguous_keys(atoms: pd.DataFrame) -> pd.DataFrame:
    """源头同一原子键对应多个尺码的原子明细（每个参与的 原子键 × 尺码 × 来源行 一行）。"""
    sizes = atoms.groupby(ATOM_FIELDS, sort=False)[SIZE].nunique()
    keys = sizes[sizes > 1].index
    if not len(keys):
        return atoms.iloc[0:0]
    return atoms.set_index(ATOM_FIELDS).loc[keys].reset_index()


def summarize_source_ambiguity(frame: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    """按参与的 DIMENSION-ID 组合归并年份：每组一行，列出各身份尺码、区分字段与涉及销量。"""
    columns = ["压缩类型", "MAKE", "MODEL", "VERSION", "CONST", "CAB", "BED_FT", "重叠年份", "原子数", "尺码",
               "DIMENSION-ID", "区分字段", "区分取值", "涉及销量"]
    if detail.empty:
        return pd.DataFrame(columns=columns)
    by_id = frame.drop_duplicates("DIMENSION-ID").set_index("DIMENSION-ID")
    size_of = detail.groupby("DIMENSION-ID")[SIZE].agg(lambda values: "/".join(sorted(set(values))))
    rows = []
    key_without_year = [field for field in ATOM_FIELDS if field != "YEAR"]
    per_atom = detail.groupby(ATOM_FIELDS, sort=False).agg(
        ids=("DIMENSION-ID", lambda values: tuple(sorted(set(values)))), sales=("原子销量", "sum"),
    ).reset_index()
    for (*key, ids), group in per_atom.groupby([*key_without_year, "ids"], sort=False):
        identities = by_id.loc[list(ids)]
        sizes = [size_of[identity] for identity in ids]
        differing = [column for column in DISTINGUISHING_COLUMNS
                     if column in identities.columns and identities[column].astype(str).nunique() > 1]
        values = "；".join(
            f"{column}: " + " / ".join(identities[column].astype(str)) for column in differing
        )
        rows.append({
            **dict(zip(key_without_year, key)),
            "重叠年份": year_ranges([int(year) for year in group["YEAR"]]),
            "原子数": len(group),
            "尺码": " | ".join(sizes),
            "DIMENSION-ID": " | ".join(ids),
            "区分字段": "、".join(differing) or "（A0 字段无差异，需回查 01 来源）",
            "区分取值": values,
            "涉及销量": round(float(group["sales"].sum()), 2),
        })
    return pd.DataFrame(rows, columns=columns)


def classify_multi(issues: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    """给原子检查问题（MULTI）标注歧义来源。"""
    result = issues.copy()
    if result.empty:
        result["歧义来源"] = []
        return result
    source = {tuple(key) for key in detail[ATOM_FIELDS].astype(str).itertuples(index=False)} if not detail.empty else set()
    keys = result[ATOM_FIELDS].fillna("").astype(str).map(compression.engine.normalize_text)
    result["歧义来源"] = [SOURCE if tuple(key) in source else INTRODUCED for key in keys.itertuples(index=False)]
    return result


def current_run_batch(output_dir: Path = PROJECT_DIR / "output") -> Path:
    """产生当前 output/ 交付字节的运行批次（manifest 中压缩来源 的 artifact_file 所在批次）。"""
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    files = [item["artifact_file"] for item in manifest["deliverables"] if item["file"].endswith("压缩来源.csv")]
    if not files:
        raise ValueError("output/manifest.json 未登记 压缩来源.csv")
    batch = REPO_ROOT / files[0]
    while batch.parent.name != "artifacts":
        batch = batch.parent
    return batch


def read_issues(batch: Path, line: str) -> pd.DataFrame:
    frames = []
    for kind in ("非皮卡", "皮卡"):
        path = batch / "extra" / f"原子检查问题_{line}_{kind}.csv.gz"
        if path.is_file():
            frames.append(pd.read_csv(path, dtype=str, encoding="utf-8-sig", keep_default_na=False))
    issues = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=[*ATOM_FIELDS, SIZE, "检查结果"])
    return issues[issues["检查结果"] == "MULTI"].reset_index(drop=True)


def diagnose_line(line: str, region: str, batch: Path, data_dir: Path = compression.DATA_DIR,
                  source_dir: Path = compression.UPSTREAM_OUTPUT) -> dict:
    frame = compression.read_frame(source_dir / compression.upstream_file(line, region))
    field_profile = compression.load_field_profile((data_dir / compression.FIELD_PROFILE).resolve())
    detail = ambiguous_keys(source_atom_rows(frame, field_profile))
    summary = summarize_source_ambiguity(frame, detail)
    multi = classify_multi(read_issues(batch, line), detail)
    counts = multi["歧义来源"].value_counts().to_dict() if not multi.empty else {}
    return {
        "summary": summary, "multi": multi,
        "stats": {
            "MULTI": len(multi), SOURCE: int(counts.get(SOURCE, 0)), INTRODUCED: int(counts.get(INTRODUCED, 0)),
            "源头多尺码原子键": int(detail[ATOM_FIELDS].drop_duplicates().shape[0]) if not detail.empty else 0,
            "身份组": len(summary),
            "涉及销量": round(float(summary["涉及销量"].sum()), 2) if not summary.empty else 0.0,
        },
    }


def render_markdown(batch: Path, results: dict[str, dict]) -> str:
    lines = [
        "# 多尺码歧义来源诊断", "",
        f"- 依据：A0 当前 output 全量表；原子检查取自产生当前 A1 交付的运行批次 `{batch.relative_to(REPO_ROOT).as_posix()}`。",
        "- 只读诊断，不改变任何交付。“原有歧义”需上游补区分字段或业务决定表达方式；“压缩新增歧义”需 A1 合并规则处理。",
        "- 涉及销量：参与歧义的原子按来源行尺寸组销量均摊后的合计（同一原子在多身份间已拆分，不重复计）。", "",
        "| 产线 | MULTI 原子 | 原有歧义 | 压缩新增歧义 | 源头多尺码原子键 | 身份组 | 涉及销量 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for line, result in results.items():
        stats = result["stats"]
        lines.append(f"| {line} | {stats['MULTI']} | {stats[SOURCE]} | {stats[INTRODUCED]} | {stats['源头多尺码原子键']} "
                     f"| {stats['身份组']} | {stats['涉及销量']:,.0f} |")
    for line, result in results.items():
        summary = result["summary"]
        if summary.empty:
            continue
        fields = summary["区分字段"].str.split("、").explode().value_counts()
        lines += ["", f"## {line}", "", "区分字段分布（一组可含多个字段）：" + "，".join(f"{name} {count}" for name, count in fields.items()) + "。", "",
                  "涉及销量最高的 10 组（销量相同按原子数）：", "", "| 车型 | 重叠年份 | 原子数 | 尺码 | 区分字段 | 涉及销量 |",
                  "| --- | --- | ---: | --- | --- | ---: |"]
        for _, row in summary.sort_values(["涉及销量", "原子数"], ascending=False).head(10).iterrows():
            name = " ".join(part for part in (row["MAKE"], row["MODEL"], row["VERSION"], row["CONST"], row["CAB"], row["BED_FT"]) if part)
            sizes = row["尺码"].replace(" | ", " / ")
            lines.append(f"| {name} | {row['重叠年份']} | {row['原子数']} | {sizes} | {row['区分字段']} | {row['涉及销量']:,.0f} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lines", help="产线（逗号分隔），默认 data/产线.yaml 全部")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    lines = compression.load_lines()
    selected = args.lines.split(",") if args.lines else list(lines)
    unknown = sorted(set(selected) - set(lines))
    if unknown:
        parser.error(f"未知产线：{', '.join(unknown)}")
    batch = current_run_batch()
    results = {line: diagnose_line(line, lines[line], batch) for line in selected}
    args.out.mkdir(parents=True, exist_ok=True)
    for line, result in results.items():
        result["summary"].to_csv(args.out / f"{line}_原有歧义身份组.csv", index=False, encoding="utf-8-sig")
        result["multi"].to_csv(args.out / f"{line}_MULTI分类.csv", index=False, encoding="utf-8-sig")
    (args.out / "摘要.md").write_text(render_markdown(batch, results), encoding="utf-8")
    for line, result in results.items():
        print(line, json.dumps(result["stats"], ensure_ascii=False))
    print(f"已写入 {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
