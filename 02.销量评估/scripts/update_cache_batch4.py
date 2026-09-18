"""批量更新缓存 - 第4批：Jeep/GMC"""
import csv
import os

CACHE_CSV = "cache/sales_model_year_cache.csv"

ALL_DATA = [
    # Jeep
    ("Jeep", "Grand Cherokee", 2024, 216148, "Jeep_Grand_Cherokee"),
    ("Jeep", "Grand Cherokee", 2025, 210082, "Jeep_Grand_Cherokee"),
    ("Jeep", "Compass", 2024, 111697, "Jeep_Compass"),
    ("Jeep", "Compass", 2025, 101997, "Jeep_Compass"),
    ("Jeep", "Wrangler", 2024, 151163, "Jeep_Wrangler"),
    ("Jeep", "Wrangler", 2025, 167322, "Jeep_Wrangler"),
    ("Jeep", "Cherokee", 2024, 2839, "Jeep_Cherokee_(KL)"),
    ("Jeep", "Renegade", 2024, 8440, "Jeep_Renegade"),
    ("Jeep", "Renegade", 2025, 721, "Jeep_Renegade"),
    ("Jeep", "Gladiator", 2024, 42123, "Jeep_Gladiator_(JT)"),
    ("Jeep", "Gladiator", 2025, 56790, "Jeep_Gladiator_(JT)"),
    # GMC
    ("GMC", "Canyon", 2024, 38215, "GMC_Canyon"),
    ("GMC", "Canyon", 2025, 36477, "GMC_Canyon"),
    ("GMC", "Terrain", 2024, 82100, "GMC_Terrain"),
    ("GMC", "Terrain", 2025, 74975, "GMC_Terrain"),
    ("GMC", "Acadia", 2024, 49178, "GMC_Acadia"),
    ("GMC", "Acadia", 2025, 55221, "GMC_Acadia"),
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
    updated = 0

    for make, model, year, sales, wiki_page in ALL_DATA:
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

    seen = set()
    unique_rows = [r for r in rows if (key := (r["MAKE"], r["MODEL"], r["YEAR"])) not in seen and not seen.add(key)]
    unique_rows.sort(key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"])))

    with open(CACHE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique_rows)

    new_count = added - updated
    print(f"Batch 4: {added} 条 ({new_count} 新增, {updated} 更新), {skipped} 跳过")
    print(f"Total cache: {len(unique_rows)}")


if __name__ == "__main__":
    main()
