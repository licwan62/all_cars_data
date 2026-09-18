"""Update sales_model_year_cache.csv with agent-found sales data from Wikipedia."""
import csv
import os

CACHE_CSV = "cache/sales_model_year_cache.csv"

# Data found by agents from Wikipedia:
# (MAKE, MODEL, YEAR, MODEL_YEAR_US_SALES, wiki_page_name)
AGENT_DATA = [
    # Chevrolet
    ("Chevrolet", "Equinox", 2025, 274356, "Chevrolet_Equinox"),
    ("Chevrolet", "Equinox", 2024, 207730, "Chevrolet_Equinox"),
    ("Chevrolet", "Traverse", 2025, 148278, "Chevrolet_Traverse"),
    ("Chevrolet", "Traverse", 2024, 105835, "Chevrolet_Traverse"),
    ("Chevrolet", "Trax", 2025, 206339, "Chevrolet_Trax"),
    ("Chevrolet", "Trax", 2024, 200689, "Chevrolet_Trax"),
    ("Chevrolet", "Colorado", 2025, 107867, "Chevrolet_Colorado"),
    ("Chevrolet", "Colorado", 2024, 98012, "Chevrolet_Colorado"),
    ("Chevrolet", "Camaro", 2024, 5859, "Chevrolet_Camaro"),
    ("Chevrolet", "Bolt EV/EUV", 2024, 8414, "Chevrolet_Bolt_EV"),
    # Ford
    ("Ford", "F-Series", 2025, 828832, "Ford_F-Series"),
    ("Ford", "Mustang", 2025, 45333, "Ford_Mustang"),
    ("Ford", "Bronco", 2025, 146007, "Ford_Bronco"),
    ("Ford", "Bronco Sport", 2025, 134493, "Ford_Bronco_Sport"),
    ("Ford", "Maverick", 2025, 155051, "Ford_Maverick_(2022)"),
    ("Ford", "Edge", 2024, 66436, "Ford_Edge"),
]

FIELDNAMES = [
    "MAKE", "MODEL", "YEAR", "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES", "RAW_SALES", "SALES_SCOPE", "SALES_PERIOD",
    "SALES_PERIOD_END", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
    "SECONDARY_SOURCE_URL", "SOURCE_CONFIDENCE", "NOTES",
]


def make_entry(make, model, year, sales, wiki_page):
    return {
        "MAKE": make,
        "MODEL": model,
        "YEAR": str(year),
        "SALES_MODEL_NAME": "",
        "SALES_REPORTING_GROUP": "",
        "MODEL_YEAR_US_SALES": str(sales),
        "RAW_SALES": "",
        "SALES_SCOPE": "US",
        "SALES_PERIOD": "FULL_YEAR",
        "SALES_PERIOD_END": "",
        "SALES_SOURCE_TYPE": "DATABASE",
        "SALES_SOURCE": "Wikipedia",
        "SOURCE_URL": f"https://en.wikipedia.org/wiki/{wiki_page}",
        "SECONDARY_SOURCE_URL": "",
        "SOURCE_CONFIDENCE": "HIGH",
        "NOTES": f"Agent research: {wiki_page}",
    }


def main():
    # Load existing cache
    if os.path.exists(CACHE_CSV):
        rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))
    else:
        rows = []

    # Build a key -> row index map, keep first occurrence
    cache_by_key = {}
    for i, row in enumerate(rows):
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in cache_by_key:
            cache_by_key[key] = i

    added = 0
    skipped = 0
    updated = 0

    for make, model, year, sales, wiki_page in AGENT_DATA:
        key = (make, model, year)
        entry = make_entry(make, model, year, sales, wiki_page)

        if key in cache_by_key:
            existing = rows[cache_by_key[key]]
            if existing.get("MODEL_YEAR_US_SALES", ""):
                skipped += 1
            else:
                existing.update(entry)
                updated += 1
                added += 1
        else:
            rows.append(entry)
            cache_by_key[key] = len(rows) - 1
            added += 1

    # Remove any duplicate rows (keep first with sales data, or first overall)
    seen = set()
    unique_rows = []
    for row in rows:
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)

    # Sort and write
    unique_rows.sort(key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"])))

    with open(CACHE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"Cache updated: {added} new/updated ({updated} updated, {added - updated} new), {skipped} skipped (already filled)")
    print(f"Total cache entries: {len(unique_rows)}")


if __name__ == "__main__":
    main()
