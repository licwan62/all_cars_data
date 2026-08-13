"""Fix Audi cache entries to match research queue MODEL names"""
import csv
import os

CACHE_CSV = "cache/sales_model_year_cache.csv"

# Mapping from Wikipedia model name to queue model name
# (Wikipedia MODEL -> Queue MODEL)
AUDI_MODEL_MAP = {
    "A5": "A5/S5/RS5",
    "A7": "A7/S7/RS7", 
    "Q3": "Q3",
    "Q5": "Q5/SQ5",
    "Q7": "Q7/SQ7",
    "Q8": "Q8/SQ8/RS Q8",
}

# Audi data with correct MODEL names for the queue
AUDI_DATA = [
    # (MAKE, MODEL_in_queue, YEAR, MODEL_YEAR_US_SALES, wiki_page_name)
    ("Audi", "A5/S5/RS5", 2024, 24636, "Audi_A5"),
    ("Audi", "A5/S5/RS5", 2025, 16886, "Audi_A5"),
    ("Audi", "A7/S7/RS7", 2024, 1574, "Audi_A7"),
    ("Audi", "A7/S7/RS7", 2025, 1654, "Audi_A7"),
    ("Audi", "Q3", 2024, 32090, "Audi_Q3"),
    ("Audi", "Q3", 2025, 23581, "Audi_Q3"),
    ("Audi", "Q5/SQ5", 2024, 56799, "Audi_Q5"),
    ("Audi", "Q5/SQ5", 2025, 46215, "Audi_Q5"),
    ("Audi", "Q7/SQ7", 2024, 15081, "Audi_Q7"),
    ("Audi", "Q7/SQ7", 2025, 11979, "Audi_Q7"),
    ("Audi", "Q8/SQ8/RS Q8", 2024, 10352, "Audi_Q8"),
    ("Audi", "Q8/SQ8/RS Q8", 2025, 10881, "Audi_Q8"),
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

    # Remove old Audi entries with wrong MODEL names
    cleaned_rows = []
    removed = 0
    for row in rows:
        if row["MAKE"] == "Audi" and row["MODEL"] in AUDI_MODEL_MAP:
            removed += 1
            continue
        cleaned_rows.append(row)
    
    print(f"Removed {removed} old Audi entries with incorrect MODEL names")
    rows = cleaned_rows

    # Build key map
    cache_by_key = {}
    for i, row in enumerate(rows):
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in cache_by_key:
            cache_by_key[key] = i

    added = 0
    skipped = 0
    for make, model, year, sales, wiki_page in AUDI_DATA:
        key = (make, model, year)
        entry = make_entry(make, model, year, sales, wiki_page)

        if key in cache_by_key:
            existing = rows[cache_by_key[key]]
            if existing.get("MODEL_YEAR_US_SALES", ""):
                skipped += 1
            else:
                existing.update(entry)
                added += 1
        else:
            rows.append(entry)
            cache_by_key[key] = len(rows) - 1
            added += 1

    # Deduplicate
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

    print(f"Audi cache updated: {added} new/updated, {skipped} skipped")
    print(f"Total cache entries: {len(unique_rows)}")


if __name__ == "__main__":
    main()
