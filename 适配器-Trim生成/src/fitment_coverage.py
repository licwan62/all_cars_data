from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from src.trimlist import clean, expanded_years, normalized, read_csv, sha256_file, write_csv


COVERAGE_HEADER = [
    "Year",
    "Make",
    "Model",
    "4A源行数",
    "尝试状态",
    "DIMENSION-ID数量",
    "DIMENSION-ID列表",
    "匹配层级",
    "最高语义分数",
    "版本列表",
    "结构列表",
    "建议搜索词",
    "说明",
]

CANDIDATE_HEADER = [
    "DIMENSION-ID",
    "Year",
    "源MAKE",
    "源MODEL",
    "主车型",
    "版本",
    "结构",
    "CAB",
    "BED",
    "候选Make",
    "候选Model",
    "原匹配方式",
    "审核状态",
    "原因",
    "建议搜索词",
    "证据要求",
    "语义分数",
]


@dataclass(frozen=True)
class SemanticCandidate:
    dimension_id: str
    level: str
    score: float
    row: dict[str, str]


@dataclass
class CoverageResult:
    coverage_rows: list[dict[str, object]]
    candidate_rows: list[dict[str, object]]
    report: dict[str, object]


def model_parts(value: str) -> set[str]:
    values = {normalized(value)}
    for part in re.split(r"[/,&+]|\band\b", value, flags=re.IGNORECASE):
        token = normalized(part)
        if token:
            values.add(token)
    return {value for value in values if value}


def semantic_score(fitment_model: str, dimension: dict[str, str]) -> tuple[str, float]:
    fit = normalized(fitment_model)
    model = normalized(dimension["MODEL"])
    version = normalized(dimension.get("版本", ""))
    if not fit or not model:
        return "", 0.0
    if fit == model:
        return "MODEL_EXACT", 1.0
    if version and fit == version:
        return "VERSION_EXACT", 0.99
    if version and fit in {model + version, version + model}:
        return "MODEL_VERSION_EXACT", 0.98
    if fit in model_parts(dimension["MODEL"]):
        return "MODEL_COMPONENT_EXACT", 0.97
    if min(len(fit), len(model)) >= 4 and (fit in model or model in fit):
        return "MODEL_CONTAINS", 0.90
    ratio = SequenceMatcher(None, fit, model).ratio()
    if ratio >= 0.86:
        return "MODEL_SIMILAR", round(ratio, 4)
    return "", 0.0


def joined(values: set[str]) -> str:
    return "; ".join(sorted(value for value in values if value))


def build_fitment_coverage(
    fitment_rows: list[dict[str, str]],
    dimension_rows: list[dict[str, str]],
    trim_rows: list[dict[str, str]],
    review_rows: list[dict[str, str]],
) -> CoverageResult:
    fitment_atom_counts = Counter(
        (int(row["year"]), row["make"], row["model"])
        for row in fitment_rows
        if row.get("year") and row.get("make") and row.get("model")
    )
    fitment_atoms = sorted(
        fitment_atom_counts,
        key=lambda item: (item[0], item[1].casefold(), item[2].casefold()),
    )

    dimensions_by_year_make: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    dimension_map = {row["DIMENSION-ID"]: row for row in dimension_rows}
    for row in dimension_rows:
        for year in expanded_years(row["YEAR"]):
            dimensions_by_year_make[(year, normalized(row["MAKE"]))].append(row)

    matched_index: dict[tuple[int, str, str], set[str]] = defaultdict(set)
    for row in trim_rows:
        matched_index[(int(row["Year"]), row["Make"], row["Model"])].add(
            row["DIMENSION-ID"]
        )

    review_index: dict[tuple[int, str, str], set[str]] = defaultdict(set)
    for row in review_rows:
        review_index[
            (int(row["Year"]), row["候选Make"], row["候选Model"])
        ].add(row["DIMENSION-ID"])

    coverage_rows: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    status_counts: Counter[str] = Counter()
    level_counts: Counter[str] = Counter()

    for year, make, model in fitment_atoms:
        atom = (year, make, model)
        matched_ids = matched_index.get(atom, set())
        reviewed_ids = review_index.get(atom, set())
        semantic_candidates: list[SemanticCandidate] = []

        if not matched_ids and not reviewed_ids:
            for dimension in dimensions_by_year_make.get(
                (year, normalized(make)), []
            ):
                level, score = semantic_score(model, dimension)
                if level:
                    semantic_candidates.append(
                        SemanticCandidate(
                            dimension["DIMENSION-ID"], level, score, dimension
                        )
                    )
            semantic_candidates.sort(
                key=lambda item: (-item.score, item.dimension_id)
            )
            semantic_candidates = semantic_candidates[:5]

        if matched_ids:
            status = "MATCHED"
            ids = matched_ids
            level = "PUBLISHED_MAPPING"
            score = 1.0
            note = "已存在正式 DIMENSION-ID 映射"
        elif reviewed_ids:
            status = "ONLINE_REVIEW_ATTEMPTED"
            ids = reviewed_ids
            level = "EXISTING_REVIEW_CANDIDATE"
            score = 1.0
            note = "已有候选并已进入联网审核队列"
        elif semantic_candidates:
            status = "SEMANTIC_CANDIDATE_ATTEMPTED"
            ids = {item.dimension_id for item in semantic_candidates}
            level = joined({item.level for item in semantic_candidates})
            score = max(item.score for item in semantic_candidates)
            note = "已按同年、同品牌和车型/版本语义生成候选；发布前须核实版本与结构"
            for item in semantic_candidates:
                dimension = item.row
                query_parts = [
                    str(year),
                    f'"{make} {model}"',
                    f'"{dimension["MAKE"]} {dimension["MODEL"]}"',
                ]
                if dimension["版本"]:
                    query_parts.append(f'"{dimension["版本"]}"')
                if dimension["结构"]:
                    query_parts.append(f'"{dimension["结构"]}"')
                candidate_rows.append(
                    {
                        "DIMENSION-ID": item.dimension_id,
                        "Year": year,
                        "源MAKE": dimension["MAKE"],
                        "源MODEL": dimension["MODEL"],
                        "主车型": f"{dimension['MAKE']} {dimension['MODEL']}".strip(),
                        "版本": dimension["版本"],
                        "结构": dimension["结构"],
                        "CAB": dimension.get("CAB", ""),
                        "BED": dimension.get("BED", ""),
                        "候选Make": make,
                        "候选Model": model,
                        "原匹配方式": f"4A全覆盖-{item.level}",
                        "审核状态": "待联网审核",
                        "原因": "4A原子尚无正式映射；语义候选需验证版本、结构和年份",
                        "建议搜索词": " ".join(query_parts),
                        "证据要求": "年份、Make、Model、版本、结构均与DIMENSION-ID语义一致",
                        "语义分数": f"{item.score:.4f}",
                    }
                )
                level_counts[item.level] += 1
        else:
            status = "ATTEMPTED_NO_DIMENSION_CANDIDATE"
            ids = set()
            level = "NO_SAME_YEAR_MAKE_MODEL_SEMANTIC_CANDIDATE"
            score = 0.0
            note = "已尝试；尺寸库中没有同年同品牌且车型/版本语义达到阈值的DIMENSION-ID"

        dimension_values = [dimension_map[value] for value in ids if value in dimension_map]
        structures = {row["结构"] for row in dimension_values if row["结构"]}
        versions = {row["版本"] for row in dimension_values if row["版本"]}
        search_query = f'{year} "{make} {model}" vehicle body style trim'
        coverage_rows.append(
            {
                "Year": year,
                "Make": make,
                "Model": model,
                "4A源行数": fitment_atom_counts[atom],
                "尝试状态": status,
                "DIMENSION-ID数量": len(ids),
                "DIMENSION-ID列表": joined(set(ids)),
                "匹配层级": level,
                "最高语义分数": f"{score:.4f}",
                "版本列表": joined(versions),
                "结构列表": joined(structures),
                "建议搜索词": search_query,
                "说明": note,
            }
        )
        status_counts[status] += 1

    candidate_rows.sort(
        key=lambda row: (
            int(row["Year"]),
            str(row["候选Make"]).casefold(),
            str(row["候选Model"]).casefold(),
            -float(row["语义分数"]),
            str(row["DIMENSION-ID"]),
        )
    )
    attempted_atoms = sum(status_counts.values())
    report: dict[str, object] = {
        "schema_version": "1.0",
        "counts": {
            "fitment_input_rows": len(fitment_rows),
            "unique_4a_atoms": len(fitment_atoms),
            "attempted_4a_atoms": attempted_atoms,
            "unattempted_4a_atoms": len(fitment_atoms) - attempted_atoms,
            "coverage_candidate_rows": len(candidate_rows),
        },
        "attempt_status_counts": dict(status_counts.most_common()),
        "semantic_level_candidate_counts": dict(level_counts.most_common()),
        "checks": {
            "every_unique_4a_atom_has_one_coverage_row": len(coverage_rows)
            == len(fitment_atoms),
            "no_unattempted_4a_atoms": attempted_atoms == len(fitment_atoms),
            "all_4a_input_rows_accounted_for": sum(
                int(row["4A源行数"]) for row in coverage_rows
            )
            == len(fitment_rows),
            "all_candidates_respect_year_and_make": all(
                int(row["Year"])
                in expanded_years(dimension_map[str(row["DIMENSION-ID"])]["YEAR"])
                and normalized(row["候选Make"])
                == normalized(dimension_map[str(row["DIMENSION-ID"])]["MAKE"])
                for row in candidate_rows
            ),
        },
        "hard_errors": [],
    }
    if not all(report["checks"].values()):
        report["hard_errors"].append("4A全覆盖校验失败")
    return CoverageResult(coverage_rows, candidate_rows, report)


def build_fitment_coverage_files(
    fitment_path: Path,
    dimensions_path: Path,
    trim_path: Path,
    review_path: Path,
    output_dir: Path,
) -> CoverageResult:
    result = build_fitment_coverage(
        read_csv(fitment_path),
        read_csv(dimensions_path),
        read_csv(trim_path),
        read_csv(review_path),
    )
    result.report["sources"] = {
        "fitment": {"path": str(fitment_path), "sha256": sha256_file(fitment_path)},
        "dimensions": {
            "path": str(dimensions_path),
            "sha256": sha256_file(dimensions_path),
        },
        "trim": {"path": str(trim_path), "sha256": sha256_file(trim_path)},
        "online_review": {
            "path": str(review_path),
            "sha256": sha256_file(review_path),
        },
    }
    if result.report["hard_errors"]:
        raise ValueError("\n".join(result.report["hard_errors"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "FitmentCoverage.csv", COVERAGE_HEADER, result.coverage_rows)
    write_csv(
        output_dir / "FitmentCoverageCandidates.csv",
        CANDIDATE_HEADER,
        result.candidate_rows,
    )
    with (output_dir / "FitmentCoverageSummary.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(result.report, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return result
