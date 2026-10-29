"""US 市场潜力：尺寸库与本节点原子销量生成，销售证据只补不减。"""
from __future__ import annotations

import csv
from functools import lru_cache
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch, sha256
from node_paths import load_record

COLUMN = "市场潜力"
ADJUSTMENT = "销量潜力调整"
OUTPUT = "市场潜力.csv"
SALES_DIR = "商业潜力调整"


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def read_jijia_export(path: Path) -> tuple[pd.DataFrame, list[int]]:
    """一次性导入助手：以唯一 ASIN 定位，恢复车型中未转义的逗号。"""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        header, *rows = list(csv.reader(stream))
    if len(header) != 8 or header[2] != "ASIN":
        raise ValueError("积加导出列结构不符")
    recovered, repaired = [], []
    for number, row in enumerate(rows, 2):
        positions = [i for i, value in enumerate(row) if re.fullmatch(r"[A-Z0-9]{10}", value)
                     and len(row) - i == len(header) - 2]
        if len(positions) != 1 or positions[0] < 2:
            raise ValueError(f"积加第 {number} 行无法定位唯一 ASIN")
        position = positions[0]
        restored = [row[0], ",".join(row[1:position]), *row[position:]]
        if len(restored) != len(header):
            raise ValueError(f"积加第 {number} 行无法恢复字段")
        recovered.append(restored)
        if len(row) != len(header):
            repaired.append(number)
    return pd.DataFrame(recovered, columns=header), repaired


def load_config(project: Path) -> dict:
    policy = json.loads((project / "data" / SALES_DIR / "参数.json").read_text(encoding="utf-8"))
    numbers = [policy[key] for key in ("evaluation_year", "full_weight_years", "half_life_years",
                                      "divisor", "confidence_units", "score_per_monthly_unit")]
    if not np.isfinite(numbers).all() or any(value < 0 for value in numbers):
        raise ValueError("市场潜力参数必须为有限非负数")
    if any(policy[key] <= 0 for key in ("half_life_years", "divisor", "confidence_units")):
        raise ValueError("半衰期、除数、可信度参数必须为正")
    weights = policy["monthly_weights"]
    if len(weights) != 3 or not np.isfinite(weights).all() or min(weights) < 0 or not np.isclose(sum(weights), 1):
        raise ValueError("月销量权重必须为三个非负数且合计为1")
    return policy


def interval_retention(value: str, policy: dict) -> float:
    match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", str(value).strip())
    if not match:
        raise ValueError(f"无法解析年份: {value!r}")
    start, end = int(match[1]), int(match[2] or match[1])
    if end < start:
        raise ValueError(f"年份倒序: {value!r}")
    ages = np.maximum(0, policy["evaluation_year"] - np.arange(start, end + 1))
    return float(np.power(2.0, -np.maximum(0, ages - policy["full_weight_years"]) /
                          policy["half_life_years"]).mean())


def nonnegative(values: pd.DataFrame) -> pd.DataFrame:
    result = values.apply(pd.to_numeric, errors="raise")
    if not np.isfinite(result.to_numpy()).all() or (result < 0).any(axis=None):
        raise ValueError("销量必须为有限非负数")
    return result


def load_sales(project: Path, policy: dict) -> pd.DataFrame:
    directory = project / "data" / SALES_DIR
    own, competitor = read(directory / "积加销量.csv"), read(directory / "竞品车罩销量统计表.csv")
    windows = ["7天销量", "15天销量", "30天销量"]
    values = nonnegative(own[windows])
    if ((values[windows[0]] > values[windows[1]]) | (values[windows[1]] > values[windows[2]])).any():
        raise ValueError("积加累计窗口销量倒序")
    own["月销量估计"] = values.mul([30 / 7, 2, 1]).mul(policy["monthly_weights"]).sum(axis=1)
    own["30天销量依据"] = values["30天销量"]
    own["来源"] = "积加"
    competitor["月销量估计"] = nonnegative(competitor[["销量"]])["销量"]
    competitor["30天销量依据"] = competitor["月销量估计"]
    competitor["来源"] = "竞品"
    sales = pd.concat([own, competitor], ignore_index=True).fillna("")
    sales["ASIN"] = sales["ASIN"].str.strip().str.upper()
    if not sales["ASIN"].str.fullmatch(r"[A-Z0-9]{10}").all() or sales["ASIN"].duplicated().any():
        raise ValueError("ASIN 非法或重复（含跨来源），需核对后计算")
    sales["可信度"] = sales["30天销量依据"] / (sales["30天销量依据"] + policy["confidence_units"])
    sales["销量目标分"] = sales["月销量估计"] * sales["可信度"] * policy["score_per_monthly_unit"]
    if not np.isfinite(sales[["月销量估计", "销量目标分"]].to_numpy(dtype=float)).all():
        raise ValueError("销量目标分溢出")
    return sales


@lru_cache(maxsize=16384)
def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def match_model(name: str, models: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], str]:
    if re.search(r"[,，/;；]|\band\b|未匹配|通用", name, flags=re.I):
        return [], "通用或多车型，待审核"
    # 只移除独立年份区间，S2000 等车型名称不作为年份删除。
    cleaned = re.sub(r"(?<![a-zA-Z0-9])(?:19|20)\d{2}\s*[-–]\s*\d{2,4}(?!\d)", "", name)
    text = normalize(cleaned)
    candidates = []
    for make, model in models:
        token = normalize(model)
        if not token or token not in text:
            continue
        if len(token) <= 3:
            boundary = r"(?<![a-z0-9])" + r"[\s-]*".join(map(re.escape, token)) + r"(?![a-z0-9])"
            if not re.search(boundary, cleaned.casefold()):
                continue
        candidates.append((make, model))
    if not candidates:
        return [], "未匹配，待审核"
    longest = max(len(normalize(model)) for _, model in candidates)
    candidates = [(make, model) for make, model in candidates if len(normalize(model)) == longest]
    branded = [(make, model) for make, model in candidates if normalize(make) in text]
    candidates = branded or candidates
    return candidates, "车型匹配，按潜力分摊" if len(candidates) == 1 else "车型歧义，待审核"


def calculate(frame: pd.DataFrame, sales: pd.DataFrame, policy: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = ["DIMENSION-ID", "MAKE", "MODEL", "YEAR", "尺寸组销量", "车型销量"]
    if missing := set(required) - set(frame):
        raise ValueError(f"全量表缺字段: {sorted(missing)}")
    if frame["DIMENSION-ID"].str.strip().eq("").any() or frame["DIMENSION-ID"].duplicated().any():
        raise ValueError("全量表 DIMENSION-ID 必须非空且唯一")
    detail = frame[required].copy()
    detail["年份留存系数"] = frame["YEAR"].map(lambda value: interval_retention(value, policy))
    detail["基础潜力"] = nonnegative(frame[["尺寸组销量"]])["尺寸组销量"] * detail["年份留存系数"] / policy["divisor"]
    for source in ("积加", "竞品"):
        detail[f"{source}月销量分摊"] = 0.0
        detail[f"{source}目标分分摊"] = 0.0
    models = list(frame[["MAKE", "MODEL"]].drop_duplicates().itertuples(index=False, name=None))
    allocations = {}
    for model, group in detail.groupby(["MAKE", "MODEL"], sort=False):
        base = group["基础潜力"]
        allocations[model] = base / base.sum() if base.sum() else pd.Series(1 / len(group), index=group.index)
    audit = []
    for sale in sales.to_dict("records"):
        candidates, status = match_model(str(sale["车型"]), models)
        if sale["来源"] == "竞品" and sale["类别"] not in policy["competitor_categories"]:
            status = "非纳入车罩类别，待审核"
        matched = status == "车型匹配，按潜力分摊"
        if matched:
            weights = allocations[candidates[0]]
            for suffix, value in [("月销量分摊", sale["月销量估计"]), ("目标分分摊", sale["销量目标分"])]:
                detail.loc[weights.index, sale["来源"] + suffix] += value * weights
        audit.append({**sale, "匹配状态": status, "匹配车型": json.dumps(candidates, ensure_ascii=False),
                      "已分摊目标分": sale["销量目标分"] if matched else 0.0})
    detail["销售目标分合计"] = detail["积加目标分分摊"] + detail["竞品目标分分摊"]
    detail[COLUMN] = detail[["基础潜力", "销售目标分合计"]].max(axis=1)
    detail["补差值"] = detail[COLUMN] - detail["基础潜力"]
    if not np.isfinite(detail[["基础潜力", COLUMN]].to_numpy()).all():
        raise ValueError("市场潜力出现非有限值")
    audit = pd.DataFrame(audit)
    if not np.isclose(detail["销售目标分合计"].sum(), audit["已分摊目标分"].sum(), rtol=1e-12, atol=1e-8):
        raise ValueError("分摊目标分不守恒")
    return detail, audit



def build_base(dimensions: pd.DataFrame, atoms: pd.DataFrame) -> pd.DataFrame:
    required = ["DIMENSION-ID", "MAKE", "MODEL", "YEAR"]
    if set(required) - set(dimensions) or set(["atom_record_id", "预估销量"]) - set(atoms):
        raise ValueError("尺寸库或原子销量缺字段")
    if atoms["atom_record_id"].duplicated().any() or not atoms["atom_record_id"].str.fullmatch(r".+ US\|ATOM_YEAR=\d{4}").all():
        raise ValueError("原子身份非法或重复")
    ids = atoms["atom_record_id"].str.split("|ATOM_YEAR=", regex=False).str[0]
    if set(ids) - set(dimensions["DIMENSION-ID"]):
        raise ValueError("原子销量身份不在 US 尺寸库中，须先核对上游")
    known = atoms["预估销量"].ne("")
    nonnegative(atoms.loc[known, ["预估销量"]])
    values = pd.to_numeric(atoms["预估销量"].replace("", np.nan))
    totals = values.groupby(ids, sort=False).sum(min_count=1)
    base = dimensions[required].copy()
    base["尺寸组销量"] = base["DIMENSION-ID"].map(totals).fillna(0)
    # 该列仅用于计算明细；目标分的分组粒度仍为 MAKE + MODEL。
    base["车型销量"] = base.groupby(["MAKE", "MODEL"], sort=False)["尺寸组销量"].transform("sum")
    return base


def run(project: Path = PROJECT, dimensions_path: Path | None = None) -> dict:
    dimensions_path = dimensions_path or project.parent / "01.整理尺寸库/output/尺寸库_US.csv"
    atoms_path = project / "output/原子销量.csv"
    with RunBatch.create(project / "artifacts", "us-market-potential", data_dir=project / "data") as batch:
        policy = load_config(project)
        batch.input(dimensions_path)
        batch.input(atoms_path)
        dimensions, atoms = read(dimensions_path), read(atoms_path)
        base = build_base(dimensions, atoms)
        detail, audit = calculate(base, load_sales(project, policy), policy)
        detail[ADJUSTMENT] = detail["补差值"]
        result = detail[["DIMENSION-ID", COLUMN, ADJUSTMENT]].copy()
        for column in (COLUMN, ADJUSTMENT):
            result[column] = result[column].map(lambda value: f"{np.ceil(value * 1e6) / 1e6:.6f}")
        result.to_csv(batch.output(OUTPUT), index=False, encoding="utf-8-sig", lineterminator="\n")
        detail.to_csv(batch.extra("市场潜力计算明细.csv"), index=False, encoding="utf-8-sig", lineterminator="\n")
        audit.to_csv(batch.extra("销售匹配依据.csv"), index=False, encoding="utf-8-sig", lineterminator="\n")
        summary = {"rows": len(result), "boosted_rows": int(detail[ADJUSTMENT].gt(0).sum()),
                   "base_total": float(detail["基础潜力"].sum()), "potential_total": float(detail[COLUMN].sum()),
                   "missing_atom_sales": int(atoms["预估销量"].eq("").sum()),
                   "match_counts": {" / ".join(k): int(v) for k,v in audit.groupby(["来源", "匹配状态"]).size().items()}}
        batch.extra("REPORT.md", compress=False).write_text(
            "# US 市场潜力\n\n计算由 A0 迁入02；公式与参数保持不变，新增销量潜力调整＝最终潜力－基础潜力。"
            "来源 CSV、参数与维护说明见本节点 data/商业潜力调整/。数值为潜力分，不是车辆或订单销量。\n\n"
            + json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        batch.finish(summary, publish_to=project / "output")
        return {"batch": str(batch.directory), **summary}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
