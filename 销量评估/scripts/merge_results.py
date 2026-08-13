from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal

from common import (
    CACHE_FIELDS,
    SALES_FIELDS,
    decimal_text,
    load_config,
    model_year_key,
    parse_nonnegative_integer,
    read_csv,
    require_fields,
    write_csv,
)


def allocate_integer(total: int, weights: list[Decimal]) -> list[int]:
    exact = [Decimal(total) * weight for weight in weights]
    floors = [int(value) for value in exact]
    remainder = total - sum(floors)
    order = sorted(range(len(exact)), key=lambda index: (exact[index] - floors[index], -index), reverse=True)
    for index in order[:remainder]:
        floors[index] += 1
    return floors


def _derive_estimate_type(cache: dict[str, str], distinct_atoms: int) -> str:
    if cache.get("SALES_SOURCE_TYPE", "").upper() == "ESTIMATED":
        return "ESTIMATED"
    if cache.get("SALES_PERIOD", "").upper() == "YTD":
        return "ANNUALIZED"
    return "ACTUAL" if distinct_atoms == 1 else "ALLOCATED_ACTUAL"


def _join_notes(*values: str) -> str:
    return " | ".join(value.strip() for value in values if value and value.strip())


def run(config_path: str = "config.json") -> dict[str, int]:
    config = load_config(config_path)
    atom_fields, atoms = read_csv(config["atoms_csv"])
    require_fields(atom_fields, ["DIMENSION-ID", "MAKE", "MODEL", "YEAR", "SALES_ATOM_KEY", "ATOM_ROW_ID"], config["atoms_csv"])

    cache_fields, cache_rows = read_csv(config["model_year_cache_csv"])
    require_fields(cache_fields, CACHE_FIELDS, config["model_year_cache_csv"])
    cache_by_key: dict[tuple[str, str, str], dict[str, str]] = {}
    for cache in cache_rows:
        key = model_year_key(cache)
        if key in cache_by_key:
            raise ValueError(f"duplicate model-year cache row: {'|'.join(key)}")
        cache_by_key[key] = cache

    _, override_rows = read_csv(config["allocation_overrides_csv"])
    overrides: dict[str, dict[str, str]] = {}
    for override in override_rows:
        key = override.get("SALES_ATOM_KEY", "")
        if not key:
            continue
        if key in overrides:
            raise ValueError(f"duplicate allocation override: {key}")
        overrides[key] = override

    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for atom in atoms:
        groups[model_year_key(atom)].append(atom)

    allowed_scopes = {scope.upper() for scope in config.get("allowed_us_scopes", ["", "US", "USA"])}
    output: list[dict[str, str]] = []
    ready_groups = 0
    pending_groups = 0
    for group_key in sorted(groups):
        group = groups[group_key]
        cache = cache_by_key.get(group_key)
        if not cache or not cache.get("MODEL_YEAR_US_SALES", ""):
            pending_groups += 1
            for atom in group:
                result = dict(atom)
                result.update({field: "" for field in SALES_FIELDS if field not in atom})
                result["ITERATION_STATUS"] = "PENDING"
                result["NOTES"] = "MODEL-YEAR sales cache is missing"
                output.append(result)
            continue

        scope = cache.get("SALES_SCOPE", "").upper()
        if scope not in allowed_scopes:
            pending_groups += 1
            for atom in group:
                result = dict(atom)
                result.update({field: "" for field in SALES_FIELDS if field not in atom})
                for field in CACHE_FIELDS:
                    if field in result or field in SALES_FIELDS:
                        result[field] = cache.get(field, "")
                result["ITERATION_STATUS"] = "PENDING"
                result["MODEL_YEAR_US_SALES"] = ""
                result["NOTES"] = _join_notes(cache.get("NOTES", ""), f"non-US scope cannot be used as US sales: {scope}")
                output.append(result)
            continue

        total = parse_nonnegative_integer(cache["MODEL_YEAR_US_SALES"], "MODEL_YEAR_US_SALES")
        rows_by_atom: dict[str, list[int]] = defaultdict(list)
        for index, atom in enumerate(group):
            rows_by_atom[atom["SALES_ATOM_KEY"]].append(index)
        distinct_keys = sorted(rows_by_atom)
        selected_overrides = {key: overrides[key] for key in distinct_keys if key in overrides}

        if selected_overrides and len(selected_overrides) != len(distinct_keys):
            missing = sorted(set(distinct_keys) - set(selected_overrides))
            raise ValueError(f"partial allocation overrides for {'|'.join(group_key)}; missing: {missing}")

        atom_weights: dict[str, Decimal]
        if selected_overrides:
            atom_weights = {key: Decimal(selected_overrides[key]["ALLOCATION_WEIGHT"]) for key in distinct_keys}
            if any(weight < 0 for weight in atom_weights.values()):
                raise ValueError(f"negative allocation weight for {'|'.join(group_key)}")
            if abs(sum(atom_weights.values()) - Decimal(1)) > Decimal("0.000001"):
                raise ValueError(f"allocation weights do not sum to 1 for {'|'.join(group_key)}")
        else:
            equal = Decimal(1) / Decimal(len(distinct_keys))
            atom_weights = {key: equal for key in distinct_keys}

        row_weights: list[Decimal] = [Decimal(0)] * len(group)
        for atom_key, indices in rows_by_atom.items():
            shared = atom_weights[atom_key] / Decimal(len(indices))
            for index in indices:
                row_weights[index] = shared
        estimates = allocate_integer(total, row_weights)
        duplicate_counts = Counter(atom["SALES_ATOM_KEY"] for atom in group)
        ready_groups += 1

        for index, atom in enumerate(group):
            result = dict(atom)
            result.update(
                {
                    "SALES_MODEL_NAME": cache.get("SALES_MODEL_NAME", "") or atom["MODEL"],
                    "SALES_REPORTING_GROUP": cache.get("SALES_REPORTING_GROUP", ""),
                    "MODEL_YEAR_US_SALES": str(total),
                    "ALLOCATION_WEIGHT": decimal_text(row_weights[index]),
                    "US_SALES_ESTIMATE": str(estimates[index]),
                    "SALES_ESTIMATE_TYPE": _derive_estimate_type(cache, len(distinct_keys)),
                    "SALES_SOURCE_TYPE": cache.get("SALES_SOURCE_TYPE", ""),
                    "SALES_SOURCE": cache.get("SALES_SOURCE", ""),
                    "SOURCE_URL": cache.get("SOURCE_URL", ""),
                    "SECONDARY_SOURCE_URL": cache.get("SECONDARY_SOURCE_URL", ""),
                    "SALES_SCOPE": cache.get("SALES_SCOPE", "") or "US",
                    "SALES_PERIOD": cache.get("SALES_PERIOD", ""),
                    "SALES_PERIOD_END": cache.get("SALES_PERIOD_END", ""),
                }
            )
            if selected_overrides:
                override = selected_overrides[atom["SALES_ATOM_KEY"]]
                result["ALLOCATION_METHOD"] = override.get("ALLOCATION_METHOD", "") or "ESTIMATED_SHARE"
                result["SALES_CONFIDENCE"] = override.get("SALES_CONFIDENCE", "") or cache.get("SOURCE_CONFIDENCE", "") or "MEDIUM"
                result["NOTES"] = _join_notes(cache.get("NOTES", ""), override.get("NOTES", ""))
                result["ITERATION_STATUS"] = "REVIEW" if duplicate_counts[atom["SALES_ATOM_KEY"]] > 1 else "READY"
            elif len(distinct_keys) == 1 and len(group) == 1:
                result["ALLOCATION_METHOD"] = "DIRECT"
                result["SALES_CONFIDENCE"] = cache.get("SOURCE_CONFIDENCE", "") or "HIGH"
                result["NOTES"] = cache.get("NOTES", "")
                result["ITERATION_STATUS"] = "READY"
            else:
                result["ALLOCATION_METHOD"] = "EQUAL_SPLIT"
                result["SALES_CONFIDENCE"] = "LOW"
                duplicate_note = "duplicate source rows share one semantic atom weight" if duplicate_counts[atom["SALES_ATOM_KEY"]] > 1 else ""
                result["NOTES"] = _join_notes(cache.get("NOTES", ""), duplicate_note, "equal split requires review")
                result["ITERATION_STATUS"] = "REVIEW"
            output.append(result)

    extra_fields = [field for field in atom_fields if field not in SALES_FIELDS]
    write_csv(config["atomic_output_csv"], SALES_FIELDS + extra_fields, output)
    return {"output_rows": len(output), "ready_groups": ready_groups, "pending_groups": pending_groups}


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge sourced model-year sales and allocate them to atomic vehicle rows.")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    stats = run(args.config)
    print(
        f"wrote {stats['output_rows']} rows; {stats['ready_groups']} model-years allocated, "
        f"{stats['pending_groups']} model-years pending research"
    )


if __name__ == "__main__":
    main()
