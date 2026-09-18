"""批量更新缓存 - 第3批：Nissan/Kia"""
import csv
import os

CACHE_CSV = "cache/sales_model_year_cache.csv"

ALL_DATA = [
    # Nissan
    ("Nissan", "Altima", 2024, 113898, "Nissan_Altima"),
    ("Nissan", "Altima", 2025, 93268, "Nissan_Altima"),
    ("Nissan", "Maxima", 2024, 942, "Nissan_Maxima"),
    ("Nissan", "Rogue", 2024, 245724, "Nissan_Rogue"),
    ("Nissan", "Rogue", 2025, 217896, "Nissan_Rogue"),
    ("Nissan", "Pathfinder", 2024, 80915, "Nissan_Pathfinder"),
    ("Nissan", "Pathfinder", 2025, 101598, "Nissan_Pathfinder"),
    ("Nissan", "Murano", 2024, 19316, "Nissan_Murano"),
    ("Nissan", "Murano", 2025, 42747, "Nissan_Murano"),
    ("Nissan", "Kicks", 2024, 77356, "Nissan_Kicks"),
    ("Nissan", "Kicks", 2025, 103575, "Nissan_Kicks"),
    ("Nissan", "Titan", 2024, 14662, "Nissan_Titan"),
    ("Nissan", "Titan", 2025, 2043, "Nissan_Titan"),
    ("Nissan", "Leaf", 2024, 11226, "Nissan_Leaf"),
    ("Nissan", "Ariya", 2024, 19798, "Nissan_Ariya"),
    ("Nissan", "Ariya", 2025, 14906, "Nissan_Ariya"),
    # Kia
    ("Kia", "Forte", 2024, 139778, "Kia_Forte"),
    ("Kia", "Forte", 2025, 11986, "Kia_Forte"),
    ("Kia", "K5", 2024, 46311, "Kia_K5"),
    ("Kia", "K5", 2025, 72751, "Kia_K5"),
    ("Kia", "Stinger", 2024, 1, "Kia_Stinger"),
    ("Kia", "Sportage", 2024, 161917, "Kia_Sportage"),
    ("Kia", "Sportage", 2025, 182823, "Kia_Sportage"),
    ("Kia", "Sorento", 2024, 95154, "Kia_Sorento"),
    ("Kia", "Sorento", 2025, 94772, "Kia_Sorento"),
    ("Kia", "Telluride", 2024, 115504, "Kia_Telluride"),
    ("Kia", "Telluride", 2025, 123281, "Kia_Telluride"),
    ("Kia", "Seltos", 2024, 60053, "Kia_Seltos"),
    ("Kia", "Soul", 2024, 52397, "Kia_Soul"),
    ("Kia", "Soul", 2025, 50133, "Kia_Soul"),
    ("Kia", "EV6", 2024, 21715, "Kia_EV6"),
    ("Kia", "EV6", 2025, 12933, "Kia_EV6"),
    ("Kia", "Niro", 2024, 30094, "Kia_Niro"),
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

    new_count = added - updated
    print(f"Batch 3: {added} 条 ({new_count} 新增, {updated} 更新), {skipped} 跳过")
    print(f"Total cache: {len(unique_rows)}")


if __name__ == "__main__":
    main()
