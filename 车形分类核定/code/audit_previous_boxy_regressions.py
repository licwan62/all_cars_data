from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

import shape_project as project
from review_generation_shape_cache import REVIEWED_PREVIOUS_BOXY_EXCLUSIONS


def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_git(revision: str) -> list[dict[str, str]]:
    relative = (project.PROJECT / "artifacts" / "record_shape.csv").relative_to(project.ROOT).as_posix()
    content = subprocess.check_output(
        ["git", "show", f"{revision}:{relative}"], cwd=project.ROOT
    ).decode("utf-8-sig")
    return list(csv.DictReader(content.splitlines()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit every legacy 32 that regressed during generation-cache rebuild.")
    parser.add_argument("--legacy-revision", required=True)
    parser.add_argument("--regressed-snapshot", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    legacy = {row["DIMENSION-ID"]: row["车形"] for row in read_git(args.legacy_revision)}
    regressed = {row["DIMENSION-ID"]: row["车形"] for row in read(args.regressed_snapshot)}
    current = {row["DIMENSION-ID"]: row["车形"] for row in read(project.RESULT)}
    source = {row["DIMENSION-ID"]: row for row in read(project.SOURCE)}

    candidates = sorted(
        dimension_id for dimension_id, old_shape in legacy.items()
        if old_shape == "32" and dimension_id in regressed and regressed[dimension_id] != "32"
        and dimension_id in current and dimension_id in source
    )
    restored: list[str] = []
    wagon_21: list[str] = []
    reviewed_exclusions: list[str] = []
    unexpected: list[dict[str, str]] = []
    for dimension_id in candidates:
        row = source[dimension_id]
        shape = current[dimension_id]
        key = (row["MAKE"], row["MODEL"], row["代际"])
        if shape == "32":
            restored.append(dimension_id)
        elif row["结构"] == "Wagon" and shape == "21":
            wagon_21.append(dimension_id)
        elif key in REVIEWED_PREVIOUS_BOXY_EXCLUSIONS and shape == REVIEWED_PREVIOUS_BOXY_EXCLUSIONS[key][0]:
            reviewed_exclusions.append(dimension_id)
        else:
            unexpected.append({"dimension_id": dimension_id, "current_shape": shape, "key": " | ".join(key)})

    report = {
        "passed": not unexpected,
        "legacy_revision": args.legacy_revision,
        "regressed_snapshot": str(args.regressed_snapshot.resolve()),
        "regression_candidates": len(candidates),
        "restored_to_32": len(restored),
        "fixed_category_wagon_21": len(wagon_21),
        "explicitly_reviewed_non_boxy_30": len(reviewed_exclusions),
        "unexplained_regressions": unexpected,
        "restored_ids": restored,
        "wagon_ids": wagon_21,
        "reviewed_exclusion_ids": reviewed_exclusions,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if not key.endswith("_ids")}, ensure_ascii=False))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
