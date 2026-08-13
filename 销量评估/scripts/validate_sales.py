from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation

from common import load_config, model_year_key, read_csv, require_fields, write_csv, write_json


REPORT_FIELDS = [
    "MAKE",
    "MODEL",
    "YEAR",
    "ROW_COUNT",
    "DISTINCT_ATOM_COUNT",
    "MODEL_YEAR_US_SALES",
    "ALLOCATED_SALES_SUM",
    "ALLOCATION_WEIGHT_SUM",
    "VALIDATION_STATUS",
    "DETAILS",
]


def run(config_path: str = "config.json", fail_on_error: bool = True) -> dict[str, int]:
    config = load_config(config_path)
    fields, rows = read_csv(config["atomic_output_csv"])
    require_fields(
        fields,
        ["MAKE", "MODEL", "YEAR", "SALES_ATOM_KEY", "MODEL_YEAR_US_SALES", "ALLOCATION_WEIGHT", "US_SALES_ESTIMATE", "ITERATION_STATUS"],
        config["atomic_output_csv"],
    )
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[model_year_key(row)].append(row)

    tolerance = Decimal(str(config.get("conservation_tolerance", 1)))
    report = []
    counts: Counter[str] = Counter()
    for key in sorted(groups):
        group = groups[key]
        sales_values = {row["MODEL_YEAR_US_SALES"] for row in group if row["MODEL_YEAR_US_SALES"]}
        if not sales_values:
            status = "PENDING"
            expected_text = allocated_text = weight_text = ""
            details = "MODEL-YEAR sales cache is missing or not US scope"
        else:
            details_list: list[str] = []
            status = "PASS"
            if len(sales_values) != 1:
                status = "FAIL"
                details_list.append("inconsistent MODEL_YEAR_US_SALES values")
                expected = Decimal(0)
            else:
                expected = Decimal(next(iter(sales_values)))
            try:
                allocated = sum(Decimal(row["US_SALES_ESTIMATE"]) for row in group)
                weight = sum(Decimal(row["ALLOCATION_WEIGHT"]) for row in group)
            except InvalidOperation:
                status = "FAIL"
                allocated = weight = Decimal(0)
                details_list.append("non-numeric allocation value")
            if abs(allocated - expected) > tolerance:
                status = "FAIL"
                details_list.append(f"sales conservation error {allocated - expected}")
            if abs(weight - Decimal(1)) > Decimal("0.000001"):
                status = "FAIL"
                details_list.append(f"allocation weights sum to {weight}")
            duplicate_count = len(group) - len({row["SALES_ATOM_KEY"] for row in group})
            if duplicate_count:
                details_list.append(f"{duplicate_count} duplicate semantic atom row(s); see duplicate report")
            expected_text = str(expected)
            allocated_text = str(allocated)
            weight_text = str(weight)
            details = "; ".join(details_list)
        counts[status] += 1
        report.append(
            {
                "MAKE": key[0],
                "MODEL": key[1],
                "YEAR": key[2],
                "ROW_COUNT": len(group),
                "DISTINCT_ATOM_COUNT": len({row["SALES_ATOM_KEY"] for row in group}),
                "MODEL_YEAR_US_SALES": expected_text,
                "ALLOCATED_SALES_SUM": allocated_text,
                "ALLOCATION_WEIGHT_SUM": weight_text,
                "VALIDATION_STATUS": status,
                "DETAILS": details,
            }
        )

    write_csv(config["validation_report_csv"], REPORT_FIELDS, report)
    summary = {
        "model_year_groups": len(groups),
        "pass": counts["PASS"],
        "pending": counts["PENDING"],
        "fail": counts["FAIL"],
    }
    write_json(config["validation_summary_json"], summary)
    if fail_on_error and counts["FAIL"]:
        raise ValueError(f"validation failed for {counts['FAIL']} model-year group(s)")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate model-year allocation conservation.")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    summary = run(args.config)
    print(
        f"validated {summary['model_year_groups']} model-years: "
        f"{summary['pass']} pass, {summary['pending']} pending, {summary['fail']} fail"
    )


if __name__ == "__main__":
    main()
