from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from src.fitment_coverage import model_parts
from src.trimlist import (
    ONLINE_EVIDENCE_HEADER,
    clean,
    normalized,
    read_csv,
    write_csv,
)


ROOT = Path(__file__).resolve().parent
LOCAL_INPUT = ROOT / "input"
SAFE_VEHICLE_TYPES = {
    "SUV": "Multipurpose Passenger Vehicle (MPV)",
    "Crossover": "Multipurpose Passenger Vehicle (MPV)",
    "MPV": "Multipurpose Passenger Vehicle (MPV)",
    "Pickup": "Truck",
}
RESEARCH_HEADER = [
    "DIMENSION-ID",
    "Year",
    "源MAKE",
    "源MODEL",
    "版本",
    "结构",
    "候选Make",
    "候选Model",
    "NHTSA车辆类型",
    "查询结果",
    "SourceURL",
    "说明",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="用 NHTSA vPIC 审核无版本的同名 SUV/Crossover/MPV/Pickup 候选"
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=ROOT / "output" / "TrimList_online_review.csv",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=LOCAL_INPUT / "online_evidence.csv",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "output" / "NHTSAResearchReport.csv",
    )
    parser.add_argument(
        "--apply-safe-evidence",
        action="store_true",
        help="将通过严格安全条件的结果写入 online_evidence.csv",
    )
    parser.add_argument("--workers", type=int, default=12)
    return parser.parse_args()


def query_url(year: int, make: str, vehicle_type: str) -> str:
    return (
        "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/"
        f"make/{quote(make, safe='')}/modelyear/{year}/"
        f"vehicletype/{quote(vehicle_type, safe='')}?format=json"
    )


def fetch_models(url: str) -> tuple[set[tuple[str, str]], str]:
    last_error = ""
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "TrimSizeMatcher/3.0"})
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            values = {
                (clean(row.get("Make_Name")), clean(row.get("Model_Name")))
                for row in payload.get("Results", [])
            }
            return values, ""
        except Exception as exc:  # network errors must remain visible in report
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    return set(), last_error


def supported_semantic_relation(row: dict[str, str]) -> str:
    if normalized(row["源MAKE"]) != normalized(row["候选Make"]):
        return ""
    source_model = normalized(row["源MODEL"])
    candidate_model = normalized(row["候选Model"])
    version = normalized(row["版本"])
    if candidate_model == source_model and not version:
        return "MODEL_EXACT_EMPTY_VERSION"
    if version and candidate_model == version:
        return "VERSION_EXACT"
    if version and candidate_model in {
        source_model + version,
        version + source_model,
    }:
        return "MODEL_VERSION_EXACT"
    if candidate_model in model_parts(row["源MODEL"]):
        return "MODEL_COMPONENT_EXACT"
    return ""


def eligible(row: dict[str, str]) -> bool:
    try:
        year = int(row["Year"])
    except ValueError:
        return False
    return (
        year >= 1996
        and row["结构"] in SAFE_VEHICLE_TYPES
        and bool(supported_semantic_relation(row))
    )


def main() -> None:
    args = parse_args()
    review_rows = [row for row in read_csv(args.review.resolve()) if eligible(row)]
    queries = {
        (
            int(row["Year"]),
            row["候选Make"],
            SAFE_VEHICLE_TYPES[row["结构"]],
        )
        for row in review_rows
    }
    results: dict[tuple[int, str, str], tuple[set[tuple[str, str]], str, str]] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {
            executor.submit(fetch_models, query_url(*query)): query
            for query in sorted(queries)
        }
        for future in as_completed(future_map):
            query = future_map[future]
            models, error = future.result()
            results[query] = (models, error, query_url(*query))

    research_rows: list[dict[str, object]] = []
    approved_evidence: list[dict[str, object]] = []
    for row in review_rows:
        year = int(row["Year"])
        vehicle_type = SAFE_VEHICLE_TYPES[row["结构"]]
        relation = supported_semantic_relation(row)
        models, error, url = results[(year, row["候选Make"], vehicle_type)]
        matched = any(
            normalized(make) == normalized(row["候选Make"])
            and normalized(model) == normalized(row["候选Model"])
            for make, model in models
        )
        status = "MATCHED" if matched else "NOT_FOUND"
        note = (
            f"NHTSA同年Make+Model+VehicleType命中；语义关系={relation}"
            if matched
            else error or "NHTSA同年车辆类型结果未找到候选Model"
        )
        research_rows.append(
            {
                "DIMENSION-ID": row["DIMENSION-ID"],
                "Year": year,
                "源MAKE": row["源MAKE"],
                "源MODEL": row["源MODEL"],
                "版本": row["版本"],
                "结构": row["结构"],
                "候选Make": row["候选Make"],
                "候选Model": row["候选Model"],
                "NHTSA车辆类型": vehicle_type,
                "查询结果": status,
                "SourceURL": url,
                "说明": note,
            }
        )
        if matched:
            approved_evidence.append(
                {
                    "DIMENSION-ID": row["DIMENSION-ID"],
                    "Year": year,
                    "Make": row["候选Make"],
                    "Model": row["候选Model"],
                    "版本": row["版本"],
                    "结构": row["结构"],
                    "Decision": "APPROVE",
                    "SourceURL": url,
                    "SourceTitle": "NHTSA vPIC GetModelsForMakeYear",
                    "EvidenceNote": note,
                    "ReviewedAt": date.today().isoformat(),
                }
            )

    write_csv(args.report.resolve(), RESEARCH_HEADER, research_rows)
    if args.apply_safe_evidence:
        existing = read_csv(args.evidence.resolve()) if args.evidence.exists() else []
        evidence_index = {
            (row["DIMENSION-ID"], row["Year"], row["Make"], row["Model"]): row
            for row in existing
        }
        for row in approved_evidence:
            key = (
                str(row["DIMENSION-ID"]),
                str(row["Year"]),
                str(row["Make"]),
                str(row["Model"]),
            )
            evidence_index[key] = row
        merged = sorted(
            evidence_index.values(),
            key=lambda row: (
                str(row["DIMENSION-ID"]),
                int(row["Year"]),
                str(row["Make"]).casefold(),
                str(row["Model"]).casefold(),
            ),
        )
        write_csv(args.evidence.resolve(), ONLINE_EVIDENCE_HEADER, merged)

    summary = {
        "eligible_review_rows": len(review_rows),
        "unique_nhtsa_queries": len(queries),
        "matched_rows": len(approved_evidence),
        "not_found_or_error_rows": len(review_rows) - len(approved_evidence),
        "evidence_applied": bool(args.apply_safe_evidence),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
