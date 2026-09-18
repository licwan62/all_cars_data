"""批量更新缓存 - 第6批：Chrysler"""
import csv

CACHE_CSV = "cache/sales_model_year_cache.csv"

ALL_DATA = [
    ("Chrysler", "300", 2024, 5295, "Chrysler_300"),
]

FIELDNAMES = [
    "MAKE", "MODEL", "YEAR", "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES", "RAW_SALES", "SALES_SCOPE", "SALES_PERIOD",
    "SALES_PERIOD_END", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
    "SECONDARY_SOURCE_URL", "SOURCE_CONFIDENCE", "NOTES",
]


def make_entry(make, model, year, sales, wiki_page):
    return {
        "MAKE": make, "MODEL": model, "YEAR": str(year),
        "SALES_MODEL_NAME": "", "SALES_REPORTING_GROUP": "",
        "MODEL_YEAR_US_SALES": str(sales), "RAW_SALES": "",
        "SALES_SCOPE": "US", "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "",
        "SALES_SOURCE_TYPE": "DATABASE", "SALES_SOURCE": "Wikipedia",
        "SOURCE_URL": f"https://en.wikipedia.org/wiki/{wiki_page}",
        "SECONDARY_SOURCE_URL": "", "SOURCE_CONFIDENCE": "HIGH",
        "NOTES": f"Agent research: {wiki_page}",
    }


def main():
    rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))
    cache_by_key = {}
    for i, row in enumerate(rows):
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in cache_by_key:
            cache_by_key[key] = i

    added = 0
    skipped = 0
    for make, model, year, sales, wiki_page in ALL_DATA:
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

    seen = set()
    unique_rows = []
    for r in rows:
        key = (r["MAKE"], r["MODEL"], r["YEAR"])
        if key not in seen:
            seen.add(key)
            unique_rows.append(r)
    unique_rows.sort(key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"])))

    with open(CACHE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"Batch 6 (Chrysler): {added} 条, {skipped} 跳过, Total: {len(unique_rows)}")


if __name__ == "__main__":
    main()
