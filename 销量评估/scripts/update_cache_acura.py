"""Update sales cache with Acura research results."""
import csv
import os

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# Data found from research:
# Sources: Wikipedia (Honda_NSX, Honda_Integra), best-selling-cars.com, hondanews.com
# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, NOTES)
RESEARCH_DATA = [
    # Acura ADX - 2025 full year from best-selling-cars.com
    ("Acura", "ADX", 2025, 20133, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-honda-and-acura-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "2025 full year US sales"),

    # Acura NSX (2nd gen) - from Wikipedia Honda_NSX sales table
    ("Acura", "NSX", 2017, 581, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2018, 170, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2019, 238, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2020, 128, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2021, 124, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2022, 298, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", "includes Type S limited edition"),

    # Acura NSX (1st gen) - from Wikipedia Honda_NSX North American sales table
    ("Acura", "NSX", 1991, 1940, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 1992, 1154, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 1993, 652, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 1994, 533, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 1995, 884, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 1996, 460, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 1997, 415, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 1998, 303, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 1999, 238, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2000, 221, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2001, 182, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2002, 233, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2003, 221, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2004, 178, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "NSX", 2005, 206, "DATABASE", "https://en.wikipedia.org/wiki/Honda_NSX", "HIGH", "US", "FULL_YEAR", "", ""),

    # Acura RSX - from Wikipedia Honda_Integra_(fourth_generation) sales table
    # RSX replaced Integra for 2002 MY; 2001 figure is last Integra year
    ("Acura", "RSX", 2002, 30117, "DATABASE", "https://en.wikipedia.org/wiki/Honda_Integra_(fourth_generation)", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "RSX", 2003, 24292, "DATABASE", "https://en.wikipedia.org/wiki/Honda_Integra_(fourth_generation)", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "RSX", 2004, 21940, "DATABASE", "https://en.wikipedia.org/wiki/Honda_Integra_(fourth_generation)", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "RSX", 2005, 20809, "DATABASE", "https://en.wikipedia.org/wiki/Honda_Integra_(fourth_generation)", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Acura", "RSX", 2006, 16996, "DATABASE", "https://en.wikipedia.org/wiki/Honda_Integra_(fourth_generation)", "HIGH", "US", "FULL_YEAR", "", ""),
]

FIELDNAMES = [
    "MAKE", "MODEL", "YEAR", "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES", "RAW_SALES", "SALES_SCOPE", "SALES_PERIOD",
    "SALES_PERIOD_END", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
    "SECONDARY_SOURCE_URL", "SOURCE_CONFIDENCE", "NOTES",
]


def make_entry(make, model, year, sales, source_type, source, url, confidence, scope, period, notes):
    return {
        "MAKE": make,
        "MODEL": model,
        "YEAR": str(year),
        "SALES_MODEL_NAME": "",
        "SALES_REPORTING_GROUP": "",
        "MODEL_YEAR_US_SALES": str(sales),
        "RAW_SALES": "",
        "SALES_SCOPE": scope,
        "SALES_PERIOD": period,
        "SALES_PERIOD_END": "",
        "SALES_SOURCE_TYPE": source_type,
        "SALES_SOURCE": source,
        "SOURCE_URL": url,
        "SECONDARY_SOURCE_URL": "",
        "SOURCE_CONFIDENCE": confidence,
        "NOTES": notes,
    }


def main():
    # Load existing cache
    rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))

    # Build a key -> row index map
    cache_by_key = {}
    for i, row in enumerate(rows):
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in cache_by_key:
            cache_by_key[key] = i

    added = 0
    skipped = 0
    updated = 0

    for make, model, year, sales, source_type, source, url, confidence, scope, period, notes in RESEARCH_DATA:
        key = (make, model, year)
        entry = make_entry(make, model, year, sales, source_type, source, url, confidence, scope, period, notes)

        if key in cache_by_key:
            existing = rows[cache_by_key[key]]
            if existing.get("MODEL_YEAR_US_SALES", "").strip():
                skipped += 1
            else:
                existing.update(entry)
                updated += 1
                added += 1
        else:
            rows.append(entry)
            cache_by_key[key] = len(rows) - 1
            added += 1

    # Remove duplicates (keep first with sales data)
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

    print(f"Cache updated: {added} new/updated ({updated} updated, {added - updated} new), {skipped} skipped")
    print(f"Total cache entries: {len(unique_rows)}")


if __name__ == "__main__":
    main()
