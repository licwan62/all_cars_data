"""批量更新缓存 - 整合所有代理找到的销量数据"""
import csv
import os

CACHE_CSV = "cache/sales_model_year_cache.csv"

# 所有代理找到的数据
# (MAKE, MODEL, YEAR, MODEL_YEAR_US_SALES, wiki_page_name)
ALL_DATA = [
    # Chevrolet (之前的)
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
    # Ford (之前的)
    ("Ford", "F-Series", 2025, 828832, "Ford_F-Series"),
    ("Ford", "Mustang", 2025, 45333, "Ford_Mustang"),
    ("Ford", "Bronco", 2025, 146007, "Ford_Bronco"),
    ("Ford", "Bronco Sport", 2025, 134493, "Ford_Bronco_Sport"),
    ("Ford", "Maverick", 2025, 155051, "Ford_Maverick_(2022)"),
    ("Ford", "Edge", 2024, 66436, "Ford_Edge"),
    # Honda (新)
    ("Honda", "Civic", 2024, 242005, "Honda_Civic"),
    ("Honda", "Civic", 2025, 238661, "Honda_Civic"),
    ("Honda", "CR-V", 2024, 402791, "Honda_CR-V"),
    ("Honda", "CR-V", 2025, 403768, "Honda_CR-V"),
    ("Honda", "HR-V", 2024, 151468, "Honda_HR-V"),
    ("Honda", "HR-V", 2025, 148771, "Honda_HR-V"),
    ("Honda", "Pilot", 2024, 141245, "Honda_Pilot"),
    ("Honda", "Pilot", 2025, 124209, "Honda_Pilot"),
    ("Honda", "Passport", 2024, 32527, "Honda_Passport"),
    ("Honda", "Passport", 2025, 55231, "Honda_Passport"),
    ("Honda", "Odyssey", 2024, 80293, "Honda_Odyssey_(North_America)"),
    ("Honda", "Odyssey", 2025, 88462, "Honda_Odyssey_(North_America)"),
    ("Honda", "Ridgeline", 2024, 45421, "Honda_Ridgeline"),
    ("Honda", "Ridgeline", 2025, 48448, "Honda_Ridgeline"),
    # BMW (新)
    ("BMW", "2 Series", 2024, 15384, "BMW_2_Series"),
    ("BMW", "2 Series", 2025, 20975, "BMW_2_Series"),
    ("BMW", "3 Series", 2024, 146362, "BMW_3_Series"),
    ("BMW", "3 Series", 2025, 157596, "BMW_3_Series"),
    ("BMW", "5 Series", 2024, 25316, "BMW_5_Series"),
    ("BMW", "5 Series", 2025, 27109, "BMW_5_Series"),
    ("BMW", "7 Series", 2024, 10723, "BMW_7_Series"),
    ("BMW", "7 Series", 2025, 9528, "BMW_7_Series"),
    ("BMW", "X1", 2024, 13142, "BMW_X1"),
    ("BMW", "X1", 2025, 12346, "BMW_X1"),
    ("BMW", "X3", 2024, 68798, "BMW_X3"),
    ("BMW", "X3", 2025, 76546, "BMW_X3"),
    ("BMW", "X5", 2024, 72348, "BMW_X5"),
    ("BMW", "X5", 2025, 76246, "BMW_X5"),
    ("BMW", "X6", 2024, 3500, "BMW_X6"),
    ("BMW", "X6", 2025, 2041, "BMW_X6"),
    # Hyundai (新)
    ("Hyundai", "Tucson", 2024, 206126, "Hyundai_Tucson"),
    ("Hyundai", "Tucson", 2025, 41840, "Hyundai_Tucson"),
    ("Hyundai", "Palisade", 2024, 110055, "Hyundai_Palisade"),
    ("Hyundai", "Palisade", 2025, 123929, "Hyundai_Palisade"),
    ("Hyundai", "Kona", 2024, 82172, "Hyundai_Kona"),
    ("Hyundai", "Venue", 2024, 24607, "Hyundai_Venue"),
    ("Hyundai", "Ioniq 5", 2024, 44400, "Hyundai_Ioniq_5"),
    ("Hyundai", "Ioniq 5", 2025, 47039, "Hyundai_Ioniq_5"),
    # Dodge (新)
    ("Dodge", "Durango", 2024, 59357, "Dodge_Durango"),
    ("Dodge", "Durango", 2025, 81168, "Dodge_Durango"),
    ("Dodge", "Hornet", 2024, 20559, "Dodge_Hornet"),
    ("Dodge", "Hornet", 2025, 9365, "Dodge_Hornet"),
    # Audi (新)
    ("Audi", "A5", 2024, 24636, "Audi_A5"),
    ("Audi", "A5", 2025, 16886, "Audi_A5"),
    ("Audi", "A7", 2024, 1574, "Audi_A7"),
    ("Audi", "A7", 2025, 1654, "Audi_A7"),
    ("Audi", "Q3", 2024, 32090, "Audi_Q3"),
    ("Audi", "Q3", 2025, 23581, "Audi_Q3"),
    ("Audi", "Q5", 2024, 56799, "Audi_Q5"),
    ("Audi", "Q5", 2025, 46215, "Audi_Q5"),
    ("Audi", "Q7", 2024, 15081, "Audi_Q7"),
    ("Audi", "Q7", 2025, 11979, "Audi_Q7"),
    ("Audi", "Q8", 2024, 10352, "Audi_Q8"),
    ("Audi", "Q8", 2025, 10881, "Audi_Q8"),
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
    # 加载现有缓存
    if os.path.exists(CACHE_CSV):
        rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))
    else:
        rows = []

    # 建立 key -> row index 映射
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

    # 去重（保留第一次出现的）
    seen = set()
    unique_rows = []
    for row in rows:
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)

    # 排序并写入
    unique_rows.sort(key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"])))

    with open(CACHE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique_rows)

    new_count = added - updated
    print(f"缓存更新: {added} 条新/更新 ({new_count} 新增, {updated} 更新), {skipped} 跳过(已有数据)")
    print(f"总缓存条目: {len(unique_rows)}")


if __name__ == "__main__":
    main()
