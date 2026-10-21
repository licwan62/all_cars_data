"""批量更新缓存 - 第2批：Mercedes-Benz/VW/Porsche"""
import csv
import os

CACHE_CSV = "cache/sales_model_year_cache.csv"

ALL_DATA = [
    # Mercedes-Benz (注意：queue 中 MODEL 名称需要匹配)
    ("Mercedes-Benz", "C-Class", 2024, 5297, "Mercedes-Benz_C-Class"),
    ("Mercedes-Benz", "C-Class", 2025, 3340, "Mercedes-Benz_C-Class"),
    ("Mercedes-Benz", "E-Class", 2024, 17638, "Mercedes-Benz_E-Class"),
    # E-Class 2025 empty, skip
    ("Mercedes-Benz", "S-Class", 2024, 16145, "Mercedes-Benz_S-Class"),
    ("Mercedes-Benz", "S-Class", 2025, 10427, "Mercedes-Benz_S-Class"),
    ("Mercedes-Benz", "GLA-Class", 2024, 8901, "Mercedes-Benz_GLA-Class"),
    ("Mercedes-Benz", "GLA-Class", 2025, 4690, "Mercedes-Benz_GLA-Class"),
    ("Mercedes-Benz", "GLB-Class", 2024, 14859, "Mercedes-Benz_GLB-Class"),
    # GLB 2025 empty, skip
    ("Mercedes-Benz", "GLC-Class", 2024, 153359, "Mercedes-Benz_GLC-Class"),
    ("Mercedes-Benz", "GLC-Class", 2025, 133248, "Mercedes-Benz_GLC-Class"),
    ("Mercedes-Benz", "GLE-Class", 2024, 47539, "Mercedes-Benz_GLE-Class"),
    ("Mercedes-Benz", "GLE-Class", 2025, 35734, "Mercedes-Benz_GLE-Class"),
    ("Mercedes-Benz", "GLS-Class", 2024, 16934, "Mercedes-Benz_GLS-Class"),
    ("Mercedes-Benz", "GLS-Class", 2025, 10790, "Mercedes-Benz_GLS-Class"),
    # Volkswagen
    ("Volkswagen", "Jetta", 2024, 71829, "Volkswagen_Jetta"),
    ("Volkswagen", "Jetta", 2025, 54291, "Volkswagen_Jetta"),
    ("Volkswagen", "Passat", 2024, 6772, "Volkswagen_Passat"),
    ("Volkswagen", "Passat", 2025, 4393, "Volkswagen_Passat"),
    ("Volkswagen", "Golf", 2024, 42807, "Volkswagen_Golf"),
    ("Volkswagen", "Golf", 2025, 29917, "Volkswagen_Golf"),
    ("Volkswagen", "Tiguan", 2024, 94372, "Volkswagen_Tiguan"),
    ("Volkswagen", "Tiguan", 2025, 78621, "Volkswagen_Tiguan"),
    ("Volkswagen", "Atlas", 2024, 75516, "Volkswagen_Atlas"),
    ("Volkswagen", "Atlas", 2025, 71044, "Volkswagen_Atlas"),
    ("Volkswagen", "Taos", 2024, 63882, "Volkswagen_Taos"),
    ("Volkswagen", "Taos", 2025, 55198, "Volkswagen_Taos"),
    ("Volkswagen", "ID.4", 2024, 34301, "Volkswagen_ID.4"),
    ("Volkswagen", "ID.4", 2025, 16367, "Volkswagen_ID.4"),
    # Porsche
    ("Porsche", "Macan", 2024, 157, "Porsche_Macan"),
    ("Porsche", "Macan", 2025, 1313, "Porsche_Macan"),
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
    if os.path.exists(CACHE_CSV):
        rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))
    else:
        rows = []

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

    # Deduplicate
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
    print(f"缓存更新: {added} 条 ({new_count} 新增, {updated} 更新), {skipped} 跳过")
    print(f"总缓存条目: {len(unique_rows)}")


if __name__ == "__main__":
    main()
