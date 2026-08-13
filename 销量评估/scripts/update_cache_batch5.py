"""批量更新缓存 - 第5批：Subaru（最后一批）"""
import csv

CACHE_CSV = "cache/sales_model_year_cache.csv"

ALL_DATA = [
    # Subaru
    ("Subaru", "Legacy", 2024, 19591, "Subaru_Legacy"),
    ("Subaru", "Legacy", 2025, 22212, "Subaru_Legacy"),
    ("Subaru", "Outback", 2024, 168771, "Subaru_Outback"),
    ("Subaru", "Crosstrek", 2024, 181811, "Subaru_Crosstrek"),
    ("Subaru", "Crosstrek", 2025, 191724, "Subaru_Crosstrek"),
    ("Subaru", "Forester", 2024, 175521, "Subaru_Forester"),
    ("Subaru", "Forester", 2025, 175070, "Subaru_Forester"),
    ("Subaru", "Ascent", 2024, 56286, "Subaru_Ascent"),
    ("Subaru", "Ascent", 2025, 44400, "Subaru_Ascent"),
    ("Subaru", "WRX", 2024, 18587, "Subaru_WRX"),
    ("Subaru", "WRX", 2025, 10930, "Subaru_WRX"),
    ("Subaru", "Solterra", 2024, 12447, "Subaru_Solterra"),
    ("Subaru", "Solterra", 2025, 10715, "Subaru_Solterra"),
    ("Subaru", "BRZ", 2024, 3345, "Subaru_BRZ"),
    ("Subaru", "BRZ", 2025, 2882, "Subaru_BRZ"),
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

    new_count = added - updated
    print(f"Batch 5 (Subaru): {added} 条 ({new_count} 新增, {updated} 更新), {skipped} 跳过")
    print(f"Total cache: {len(unique_rows)}")
    
    # 汇总所有品牌
    print(f"\n=== 全部代理数据汇总 ===")
    brands = {
        'Chevrolet': 10, 'Ford': 6, 'Honda': 14, 'BMW': 16,
        'Hyundai': 8, 'Dodge': 4, 'Audi': 12, 'Mercedes-Benz': 14,
        'Volkswagen': 14, 'Porsche': 2, 'Nissan': 16, 'Kia': 17,
        'Jeep': 11, 'GMC': 6, 'Subaru': 15,
    }
    total = sum(brands.values())
    print(f"品牌数: {len(brands)}")
    print(f"总数据条数: {total}")


if __name__ == "__main__":
    main()
