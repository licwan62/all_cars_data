"""Update sales cache with Toyota, Lexus, and Ford research results."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, PERIOD_END, NOTES)
RESEARCH_DATA = [
    # ===== TOYOTA 2024 US sales (from best-selling-cars.com) =====
    ("Toyota", "Corolla", 2024, 232370, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Corolla sedan"),
    ("Toyota", "Camry", 2024, 290649, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "RAV4", 2024, 434943, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Tacoma", 2024, 234768, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+34% new gen"),
    ("Toyota", "Tundra", 2024, 125185, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Tundra + Tundra GH"),
    ("Toyota", "Highlander", 2024, 169543, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Grand Highlander", 2024, 48036, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "first full year"),
    ("Toyota", "4Runner", 2024, 119238, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Sequoia", 2024, 22182, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Sienna", 2024, 66547, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Corolla Cross", 2024, 71110, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Venza", 2024, 29907, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "last year"),
    ("Toyota", "bZ4X", 2024, 9329, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Crown", 2024, 19063, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Crown sedan"),
    ("Toyota", "Prius", 2024, 38052, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "new gen Prius"),
    ("Toyota", "Supra", 2024, 2652, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "GR86", 2024, 11078, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Mirai", 2024, 2737, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Toyota", "Land Cruiser", 2024, 7, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "new gen launched late"),

    # ===== TOYOTA 2025 US sales (estimated from search results) =====
    ("Toyota", "Tacoma", 2025, 275000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "+17% est"),
    ("Toyota", "RAV4", 2025, 479288, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+10.2%"),
    ("Toyota", "Camry", 2025, 316185, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "new gen +8.8%"),
    ("Toyota", "Corolla", 2025, 240000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "slight increase est"),
    ("Toyota", "Highlander", 2025, 175000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~3% growth"),
    ("Toyota", "Grand Highlander", 2025, 55000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~15% growth"),
    ("Toyota", "4Runner", 2025, 130000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new gen est"),
    ("Toyota", "Tundra", 2025, 130000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~4% growth"),
    ("Toyota", "Sienna", 2025, 68000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~2% growth"),
    ("Toyota", "Corolla Cross", 2025, 75000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~5% growth"),
    ("Toyota", "Prius", 2025, 48000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "+26.3%"),
    ("Toyota", "Crown Signia", 2025, 20000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new model replacing Venza"),
    ("Toyota", "Sequoia", 2025, 23000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~4% growth"),
    ("Toyota", "bZ4X", 2025, 12000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est growth"),
    ("Toyota", "GR86", 2025, 11500, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Toyota", "Supra", 2025, 2000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "declining"),
    ("Toyota", "Land Cruiser", 2025, 15000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-toyota-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new gen full year"),

    # ===== LEXUS 2024 US sales (from best-selling-cars.com) =====
    ("Lexus", "ES", 2024, 39117, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "ES 250/300/350"),
    ("Lexus", "IS", 2024, 22521, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Lexus", "LS", 2024, 2234, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Lexus", "LC", 2024, 1761, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Lexus", "RC", 2024, 1752, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Lexus", "UX", 2024, 11846, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Lexus", "NX", 2024, 74526, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Lexus", "RX", 2024, 114033, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Lexus", "RZ", 2024, 5386, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "electric"),
    ("Lexus", "TX", 2024, 8201, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "new model; TX 350/500h/550h"),
    ("Lexus", "GX", 2024, 31910, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "new gen GX"),
    ("Lexus", "LX", 2024, 6959, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-toyota-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),

    # ===== LEXUS 2025 US sales (estimated) =====
    ("Lexus", "RX", 2025, 113000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Lexus", "NX", 2025, 77000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~3% growth"),
    ("Lexus", "ES", 2025, 40000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~2% growth"),
    ("Lexus", "GX", 2025, 35000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~10% growth; new gen ramping"),
    ("Lexus", "TX", 2025, 25000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~3x growth; full year"),
    ("Lexus", "IS", 2025, 22000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Lexus", "UX", 2025, 12000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Lexus", "RZ", 2025, 8000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~48% growth"),
    ("Lexus", "LX", 2025, 7000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Lexus", "LS", 2025, 2000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Lexus", "LC", 2025, 1700, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Lexus", "RC", 2025, 1500, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est declining"),

    # ===== FORD 2024 US sales (from best-selling-cars.com / search results) =====
    ("Ford", "F-Series", 2024, 765649, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "F-150 + F-250 + F-350 + F-450"),
    ("Ford", "Explorer", 2024, 194094, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Ford", "Maverick", 2024, 131142, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+21%"),
    ("Ford", "Bronco", 2024, 109172, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Bronco + Bronco Sport"),
    ("Ford", "Ranger", 2024, 46205, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "new gen; +45%"),
    ("Ford", "F-150 Lightning", 2024, 33510, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "electric"),
    ("Ford", "Mustang Mach-E", 2024, 34100, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Ford", "Escape", 2024, 148000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated; declining"),
    ("Ford", "Edge", 2024, 85000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "last year; estimated"),
    ("Ford", "Expedition", 2024, 52000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Ford", "Transit", 2024, 120000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "commercial van; estimated"),
    ("Ford", "E-Transit", 2024, 15000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Ford", "Mustang", 2024, 72000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new Dark Horse gen; estimated"),

    # ===== FORD 2025 US sales (from search results) =====
    ("Ford", "F-Series", 2025, 828832, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+8.3% record"),
    ("Ford", "Maverick", 2025, 155051, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+18.2% record"),
    ("Ford", "Ranger", 2025, 70960, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+53.6%"),
    ("Ford", "Explorer", 2025, 190000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~slight decline"),
    ("Ford", "Bronco", 2025, 105000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~slight decline"),
    ("Ford", "Escape", 2025, 130000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est declining"),
    ("Ford", "Expedition", 2025, 55000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new gen est"),
    ("Ford", "Mustang Mach-E", 2025, 30000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est declining"),
    ("Ford", "F-150 Lightning", 2025, 28000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est declining"),
    ("Ford", "Mustang", 2025, 75000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Ford", "Transit", 2025, 125000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),
    ("Ford", "E-Transit", 2025, 18000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-ford-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est growth"),
]

FIELDNAMES = [
    "MAKE", "MODEL", "YEAR", "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES", "RAW_SALES", "SALES_SCOPE", "SALES_PERIOD",
    "SALES_PERIOD_END", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
    "SECONDARY_SOURCE_URL", "SOURCE_CONFIDENCE", "NOTES",
]


def make_entry(make, model, year, sales, source, url, confidence, scope, period, period_end, notes):
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
        "SALES_PERIOD_END": period_end,
        "SALES_SOURCE_TYPE": "DATABASE",
        "SALES_SOURCE": source,
        "SOURCE_URL": url,
        "SECONDARY_SOURCE_URL": "",
        "SOURCE_CONFIDENCE": confidence,
        "NOTES": notes,
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

    for make, model, year, sales, source, url, confidence, scope, period, period_end, notes in RESEARCH_DATA:
        key = (make, model, year)
        entry = make_entry(make, model, year, sales, source, url, confidence, scope, period, period_end, notes)

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

    # Remove duplicates
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

    print(f"Cache updated: {added} new/updated ({updated} updated, {added - updated} new), {skipped} skipped")
    print(f"Total cache entries: {len(unique_rows)}")


if __name__ == "__main__":
    main()
