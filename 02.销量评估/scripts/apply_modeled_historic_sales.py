from __future__ import annotations

import argparse

from common import CACHE_FIELDS, load_config, read_csv, write_csv


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["MAKE"].casefold(), row["MODEL"].casefold(), row["YEAR"]


def run(config_path: str = "config.json") -> int:
    config = load_config(config_path)
    _, atomic = read_csv(config["atomic_output_csv"])
    _, cache = read_csv(config["model_year_cache_csv"])
    _, rules = read_csv("data/modeled_historic_us_sales.csv")
    by_key = {key(row): row for row in cache}
    rule_by_model = {(row["MAKE"].casefold(), row["MODEL"].casefold()): row for row in rules}
    added = 0
    for atom in atomic:
        if atom.get("ITERATION_STATUS") != "PENDING":
            continue
        atom_key = key(atom)
        if atom_key in by_key:
            continue
        rule = rule_by_model.get(atom_key[:2])
        if not rule:
            raise ValueError(f"no modeled-sales rule for {'|'.join(atom_key)}")
        row = {field: "" for field in CACHE_FIELDS}
        row.update({
            "MAKE": atom["MAKE"], "MODEL": atom["MODEL"], "YEAR": atom["YEAR"],
            "MODEL_YEAR_US_SALES": rule["ANNUAL_US_SALES"], "RAW_SALES": rule["ANNUAL_US_SALES"],
            "SALES_SCOPE": "US", "SALES_PERIOD": "FULL_YEAR", "SALES_SOURCE_TYPE": "MODELED_ESTIMATE",
            "SALES_SOURCE": "Historical production/export proxy", "SOURCE_URL": rule["SOURCE_URL"],
            "SOURCE_CONFIDENCE": "LOW", "NOTES": rule["NOTES"] + " | modeled historical US annual sales",
        })
        cache.append(row)
        by_key[atom_key] = row
        added += 1
    cache.sort(key=lambda row: (row["MAKE"].casefold(), row["MODEL"].casefold(), int(row["YEAR"])))
    write_csv(config["model_year_cache_csv"], CACHE_FIELDS, cache)
    return added


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    print({"added": run(args.config)})
