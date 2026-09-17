from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
ROOT = PROJECT_DIR.parent
SOURCE_COLUMNS = [
    "DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际", "YEAR", "分类",
    "L-IN", "W-IN", "H-IN", "参考车型", "备注", "迭代状态",
]
COVERAGE_COLUMNS = ["页面车型", "页面年份", "处理结论", "对应DIMENSION-ID", "依据", "来源URL"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def compact(value: object) -> str:
    return " ".join(str(value or "").split())


def dimension_id(row: dict[str, str]) -> str:
    fields = ["MAKE", "MODEL", "版本", "结构", "YEAR"]
    if compact(row.get("分类", "")) == "皮卡":
        fields.extend(["CAB", "BED"])
    return " ".join(compact(row.get(field, "")) for field in fields if compact(row.get(field, "")))


def build_candidate(source: pd.DataFrame, config: dict[str, object]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    if list(source.columns) != SOURCE_COLUMNS:
        raise ValueError("源尺寸库字段与标准 16 列不一致")
    replacements = list(config["replacements"])
    removal_ids = {value for item in replacements for value in item["source_ids"]}
    missing = sorted(removal_ids - set(source["DIMENSION-ID"]))
    if missing:
        raise ValueError(f"迭代规则引用了不存在的 DIMENSION-ID：{missing}")
    if source["DIMENSION-ID"].duplicated().any():
        raise ValueError("源尺寸库 DIMENSION-ID 不唯一")

    added_rows: list[dict[str, str]] = []
    sources_by_new_id: dict[str, str] = {}
    for item in replacements:
        row = {column: compact(item["row"].get(column, "")) for column in SOURCE_COLUMNS if column != "DIMENSION-ID"}
        row["DIMENSION-ID"] = dimension_id(row)
        added_rows.append(row)
        sources_by_new_id[row["DIMENSION-ID"]] = str(item["source_url"])

    kept = source.loc[~source["DIMENSION-ID"].isin(removal_ids)].copy()
    added = pd.DataFrame(added_rows, columns=SOURCE_COLUMNS)
    candidate = pd.concat([kept, added], ignore_index=True)[SOURCE_COLUMNS]
    candidate = candidate.sort_values("DIMENSION-ID", kind="stable").reset_index(drop=True)
    recomputed = candidate.apply(lambda row: dimension_id(row.to_dict()), axis=1)
    if not recomputed.eq(candidate["DIMENSION-ID"]).all():
        raise ValueError("候选尺寸库存在不符合统一格式的 DIMENSION-ID")
    if candidate["DIMENSION-ID"].eq("").any() or candidate["DIMENSION-ID"].duplicated().any():
        raise ValueError("候选尺寸库 DIMENSION-ID 存在空值或重复")
    if candidate[["L-IN", "W-IN", "H-IN"]].eq("").any(axis=1).sum() != source[["L-IN", "W-IN", "H-IN"]].eq("").any(axis=1).sum():
        raise ValueError("本轮 Wrangler 迭代不应改变全库缺尺寸记录数")

    removed = source.loc[source["DIMENSION-ID"].isin(removal_ids)].copy()
    removed.insert(0, "变更类型", "删除旧分段")
    removed.insert(1, "来源URL", "")
    added_changes = added.copy()
    added_changes.insert(0, "变更类型", "新增候选")
    added_changes.insert(1, "来源URL", added_changes["DIMENSION-ID"].map(sources_by_new_id))
    changes = pd.concat([removed, added_changes], ignore_index=True)

    untouched_source = source.loc[~source["DIMENSION-ID"].isin(removal_ids)].sort_values("DIMENSION-ID").reset_index(drop=True)
    untouched_candidate = candidate.loc[~candidate["DIMENSION-ID"].isin(set(added["DIMENSION-ID"]))].sort_values("DIMENSION-ID").reset_index(drop=True)
    untouched_equal = untouched_source.equals(untouched_candidate)
    validation = {
        "iteration_id": config["iteration_id"],
        "source_rows": int(len(source)),
        "candidate_rows": int(len(candidate)),
        "removed_rows": int(len(removed)),
        "added_rows": int(len(added)),
        "untouched_rows_equal": bool(untouched_equal),
        "columns_match": list(candidate.columns) == SOURCE_COLUMNS,
        "dimension_id_unique": bool(candidate["DIMENSION-ID"].is_unique),
        "dimension_id_format_valid": bool(recomputed.eq(candidate["DIMENSION-ID"]).all()),
        "missing_dimension_rows": int(candidate[["L-IN", "W-IN", "H-IN"]].eq("").any(axis=1).sum()),
    }
    if not all(validation[key] for key in ["untouched_rows_equal", "columns_match", "dimension_id_unique", "dimension_id_format_valid"]):
        raise ValueError(f"候选尺寸库校验失败：{validation}")
    return candidate, changes, validation


def build_coverage(candidate: pd.DataFrame, config: dict[str, object]) -> tuple[pd.DataFrame, dict[str, object]]:
    coverage = pd.DataFrame(config.get("coverage", []), columns=COVERAGE_COLUMNS)
    candidate_ids = set(candidate["DIMENSION-ID"])
    missing_ids: list[str] = []
    for _, row in coverage.iterrows():
        if str(row["处理结论"]).startswith("已覆盖"):
            for dimension_id_value in filter(None, str(row["对应DIMENSION-ID"]).split(";")):
                if dimension_id_value not in candidate_ids:
                    missing_ids.append(dimension_id_value)
    resolved = bool(len(coverage)) and not missing_ids and coverage["处理结论"].ne("").all()
    summary = {
        "coverage_rows": int(len(coverage)),
        "coverage_missing_ids": sorted(set(missing_ids)),
        "coverage_resolved": bool(resolved),
        "coverage_conclusion_counts": coverage["处理结论"].value_counts().sort_index().to_dict(),
    }
    if not resolved:
        raise ValueError(f"完整性验证失败：{summary}")
    return coverage, summary


def write_report(path: Path, config: dict[str, object], validation: dict[str, object]) -> None:
    lines = [
        "# Jeep Wrangler 侧视图尺寸迭代报告",
        "",
        "## 结论",
        "",
        "本轮将 Jeep Database 的 Wrangler / Gladiator 代际页作为基础车身三维与车型覆盖来源，合并普通版年度分段，并为 Rubicon、392、Xtreme 等既有特殊外廓记录补全门数和平台码。Renegade 新增为待终核候选。",
        "",
        f"- 源尺寸库：{validation['source_rows']} 行",
        f"- 候选尺寸库：{validation['candidate_rows']} 行",
        f"- 删除旧分段：{validation['removed_rows']} 行",
        f"- 新增候选分段：{validation['added_rows']} 行",
        "- 未触及记录逐字段一致：是",
        "- DIMENSION-ID 唯一且符合统一格式：是",
        "- `correct.csv` 与 `尺寸库候选.csv` 内容一致，可作为人工发布输入。",
        f"- 页面车型完整性清单：{validation['coverage_rows']} 项，全部已有入库记录或明确排除结论。",
        "- `完整性验证.csv` 给出 Wrangler / Gladiator 每种页面车型的对应记录和排除依据。",
        "",
        "## 采用口径",
        "",
        f"- {config['height_policy']}",
        "- YJ 总览页的 1987-1996 与车型明细/美国 model year 存在口径差异，本轮采用 1987-1995。",
        "- LJ 页面标题写 2003-2006，但同页车型关联出现 2004-2006，本轮采用美国 model year 2004-2006。",
        "- JL/JLU 页面明确规格覆盖到 2024；2025-2026 从原记录拆出并保留原值，标记待终核。",
        "",
        "## 来源",
        "",
        f"- Wrangler 侧视图总览：{config['scope_source']}",
    ]
    for item in config["replacements"]:
        url = item["source_url"]
        if f"- {url}" not in lines:
            lines.append(f"- {url}")
    lines += [
        "",
        "## 发布说明",
        "",
        "本批次只生成候选文件，不覆盖 `data/us/source/US尺寸库.csv`。人工审阅 `变更.csv` 和本报告后，可使用 `correct.csv` 作为发布输入。",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成尺寸库迭代候选与审计产物")
    parser.add_argument("--source", type=Path, default=ROOT / "data" / "us" / "source" / "US尺寸库.csv")
    parser.add_argument("--config", type=Path, default=PROJECT_DIR / "config" / "2026-09-16_jeep_wrangler_side_views.json")
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    output_dir = args.output_dir or PROJECT_DIR / "artifacts" / str(config["iteration_id"])
    source_hash_before = sha256(args.source)
    source = read_csv(args.source)
    candidate, changes, validation = build_candidate(source, config)
    coverage, coverage_validation = build_coverage(candidate, config)
    validation.update(coverage_validation)
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate.to_csv(output_dir / "尺寸库候选.csv", index=False, encoding="utf-8-sig", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    candidate.to_csv(output_dir / "correct.csv", index=False, encoding="utf-8-sig", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    changes.to_csv(output_dir / "变更.csv", index=False, encoding="utf-8-sig", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    coverage.to_csv(output_dir / "完整性验证.csv", index=False, encoding="utf-8-sig", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    validation["source_sha256"] = source_hash_before
    validation["candidate_sha256"] = sha256(output_dir / "尺寸库候选.csv")
    validation["correct_sha256"] = sha256(output_dir / "correct.csv")
    validation["correct_matches_candidate"] = validation["correct_sha256"] == validation["candidate_sha256"]
    validation["source_unchanged"] = sha256(args.source) == source_hash_before
    (output_dir / "验证.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(output_dir / "报告.md", config, validation)
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
