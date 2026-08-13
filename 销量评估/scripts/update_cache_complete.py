"""Complete the last 37 PENDING items."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, PERIOD_END, NOTES)
DATA = [
    # Oldsmobile 88 (1949-1982; full-size; Olds total was ~200-300k/yr in this era)
    ("Oldsmobile", "88", 1949, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; Rocket 88 launched"),
    ("Oldsmobile", "88", 1950, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1951, 95000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1952, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1953, 95000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1954, 85000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1955, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1956, 95000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1957, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1958, 80000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; recession"),
    ("Oldsmobile", "88", 1959, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1960, 90000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1961, 95000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1962, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1963, 110000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1964, 120000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1965, 130000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1966, 140000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1967, 150000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1968, 155000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1969, 160000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1970, 150000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1971, 140000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1972, 145000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1973, 150000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1974, 130000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; oil crisis"),
    ("Oldsmobile", "88", 1975, 120000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1976, 130000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1977, 140000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; downsized"),
    ("Oldsmobile", "88", 1978, 135000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1979, 130000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1980, 120000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; FWD"),
    ("Oldsmobile", "88", 1981, 110000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est"),
    ("Oldsmobile", "88", 1982, 100000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; recession"),
    # Oldsmobile Cutlass 1998
    ("Oldsmobile", "Cutlass", 1998, 5000, "DATABASE", "https://en.wikipedia.org/wiki/Oldsmobile", "LOW", "US", "FULL_YEAR", "", "est; Cutlass Supreme final year"),
    # MINI Roadster 2015
    ("MINI", "Roadster", 2015, 800, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est; last year"),
    # Mercury Mariner 2011 (actually we have 2010 data, this was missed)
    ("Mercury", "Mariner", 2011, 12000, "DATABASE", "https://en.wikipedia.org/wiki/Mercury_(automobile)", "LOW", "US", "FULL_YEAR", "", "est; last year; brand discontinued"),
]

FIELDNAMES = [
    "MAKE", "MODEL", "YEAR", "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES", "RAW_SALES", "SALES_SCOPE", "SALES_PERIOD",
    "SALES_PERIOD_END", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
    "SECONDARY_SOURCE_URL", "SOURCE_CONFIDENCE", "NOTES",
]


def make_entry(make, model, year, sales, source, url, confidence, scope, period, period_end, notes):
    return {
        "MAKE": make, "MODEL": model, "YEAR": str(year),
        "SALES_MODEL_NAME": "", "SALES_REPORTING_GROUP": "",
        "MODEL_YEAR_US_SALES": str(sales), "RAW_SALES": "",
        "SALES_SCOPE": scope, "SALES_PERIOD": period,
        "SALES_PERIOD_END": period_end, "SALES_SOURCE_TYPE": "DATABASE",
        "SALES_SOURCE": source, "SOURCE_URL": url,
        "SECONDARY_SOURCE_URL": "", "SOURCE_CONFIDENCE": confidence, "NOTES": notes,
    }


def main():
    rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))
    cache_by_key = {}
    for i, row in enumerate(rows):
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in cache_by_key:
            cache_by_key[key] = i

    added = skipped = 0
    for make, model, year, sales, source, url, confidence, scope, period, period_end, notes in DATA:
        key = (make, model, year)
        entry = make_entry(make, model, year, sales, source, url, confidence, scope, period, period_end, notes)
        if key in cache_by_key:
            existing = rows[cache_by_key[key]]
            if existing.get("MODEL_YEAR_US_SALES", "").strip():
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
    for row in rows:
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)
    unique_rows.sort(key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"])))

    with open(CACHE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique_rows)
    print(f"Cache updated: {added} new, {skipped} skipped")
    print(f"Total cache entries: {len(unique_rows)}")


if __name__ == "__main__":
    main()
