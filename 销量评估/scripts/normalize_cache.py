from __future__ import annotations

import argparse

from common import CACHE_FIELDS, load_config, read_csv, write_csv


def run(config_path: str = "config.json") -> dict[str, int]:
    config = load_config(config_path)
    _, source_rows = read_csv(config["input_csv"])
    _, cache_rows = read_csv(config["model_year_cache_csv"])

    source_names = {
        (row["MAKE"].casefold(), row["MODEL"].casefold()): (row["MAKE"], row["MODEL"])
        for row in source_rows
    }
    repaired = 0
    for row in cache_rows:
        if row.get("SALES_SCOPE") != "FULL_YEAR":
            continue
        if row.get("SOURCE_CONFIDENCE") == "US":
            malformed_url = row.get("SALES_SOURCE", "")
            confidence = row.get("SOURCE_URL", "")
            row["SALES_SCOPE"] = "US"
            row["SALES_PERIOD"] = "FULL_YEAR"
            row["SALES_SOURCE"] = "DATABASE"
            row["SOURCE_URL"] = malformed_url
            row["SOURCE_CONFIDENCE"] = confidence if confidence in {"HIGH", "MEDIUM", "LOW"} else "MEDIUM"
        else:
            row["SALES_SCOPE"] = "US"
        repaired += 1

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in cache_rows:
        folded = (row["MAKE"].casefold(), row["MODEL"].casefold(), row["YEAR"])
        grouped.setdefault(folded, []).append(row)

    output = []
    removed = 0
    for folded, candidates in grouped.items():
        canonical = source_names.get(folded[:2])
        exact = [row for row in candidates if canonical and (row["MAKE"], row["MODEL"]) == canonical]
        selected = exact[0] if exact else candidates[0]
        if canonical:
            selected["MAKE"], selected["MODEL"] = canonical
        output.append(selected)
        removed += len(candidates) - 1

    output.sort(key=lambda row: (row["MAKE"].casefold(), row["MODEL"].casefold(), int(row["YEAR"])))
    write_csv(config["model_year_cache_csv"], CACHE_FIELDS, output)
    return {"rows": len(output), "repaired": repaired, "removed_case_duplicates": removed}


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair and canonicalize the model-year sales cache.")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    print(run(args.config))


if __name__ == "__main__":
    main()
