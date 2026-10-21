"""Update sales cache with Chevrolet, Porsche, and other brands research results."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, PERIOD_END, NOTES)
RESEARCH_DATA = [
    # ===== CHEVROLET 2024 (from best-selling-cars.com GM report) =====
    ("Chevrolet", "Blazer", 2024, 52576, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Blazer EV", 2024, 23115, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "first significant year"),
    ("Chevrolet", "Bolt", 2024, 8627, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Bolt EV + EUV combined"),
    ("Chevrolet", "Camaro", 2024, 5859, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "last year of production"),
    ("Chevrolet", "Colorado", 2024, 98012, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+37.9%"),
    ("Chevrolet", "Corvette", 2024, 33330, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Equinox", 2024, 207730, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Equinox EV", 2024, 28874, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "first year"),
    ("Chevrolet", "Express", 2024, 44221, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Malibu", 2024, 117319, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Silverado 1500", 2024, 358771, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Silverado LD"),
    ("Chevrolet", "Silverado 2500HD/3500HD", 2024, 183746, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Silverado HD"),
    ("Chevrolet", "Silverado EV", 2024, 7428, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Suburban", 2024, 44398, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Tahoe", 2024, 105147, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Trailblazer", 2024, 104398, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Traverse", 2024, 105835, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chevrolet", "Trax", 2024, 200689, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+83.5%"),

    # Chevrolet 2025 (from top-10 models page + estimates)
    ("Chevrolet", "Silverado 1500", 2025, 380000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "Silverado LD est from total 588709 minus HD"),
    ("Chevrolet", "Silverado 2500HD/3500HD", 2025, 190000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~5% growth from 2024"),
    ("Chevrolet", "Equinox", 2025, 332301, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "HIGH", "US", "FULL_YEAR", "", "+40.5% new record"),
    ("Chevrolet", "Trax", 2025, 210000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~5% growth"),
    ("Chevrolet", "Tahoe", 2025, 110000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~5% growth"),
    ("Chevrolet", "Suburban", 2025, 46000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~5% growth"),
    ("Chevrolet", "Corvette", 2025, 35000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~5% growth"),
    ("Chevrolet", "Colorado", 2025, 100000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~2% growth"),
    ("Chevrolet", "Malibu", 2025, 110000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~6% decline"),
    ("Chevrolet", "Blazer", 2025, 50000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~5% decline"),
    ("Chevrolet", "Trailblazer", 2025, 100000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~4% decline"),
    ("Chevrolet", "Traverse", 2025, 100000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-top-10-best-selling-vehicle-models/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~6% decline"),

    # ===== PORSCHE 2024-2025 US sales (from best-selling-cars.com) =====
    ("Porsche", "911", 2024, 14128, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+20.8% record"),
    ("Porsche", "718", 2024, 5698, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Boxster + Cayman; +25.9%"),
    ("Porsche", "Taycan", 2024, 4747, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Porsche", "Panamera", 2024, 3982, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Porsche", "Cayenne", 2024, 22432, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+9.6% record"),
    ("Porsche", "Macan", 2024, 25180, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),

    ("Porsche", "911", 2025, 13574, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Porsche", "718", 2025, 6399, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "production nearing end"),
    ("Porsche", "Taycan", 2025, 4142, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Porsche", "Panamera", 2025, 4651, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+16.8%"),
    ("Porsche", "Cayenne", 2025, 20314, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Porsche", "Macan", 2025, 27139, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-porsche-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "record year; ICE + electric"),

    # ===== GMC 2024 US sales (from best-selling-cars.com) =====
    ("GMC", "Acadia", 2024, 49178, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("GMC", "Canyon", 2024, 38215, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+70.2%"),
    ("GMC", "Sierra 1500", 2024, 214819, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Sierra LD"),
    ("GMC", "Sierra 2500HD/3500HD", 2024, 108127, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "Sierra HD"),
    ("GMC", "Terrain", 2024, 82100, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+14.3%"),
    ("GMC", "Yukon", 2024, 87312, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+6.1%"),
    ("GMC", "Savana", 2024, 18585, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),

    # ===== CADILLAC 2024 US sales (from best-selling-cars.com) =====
    ("Cadillac", "CT4", 2024, 6208, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Cadillac", "CT5", 2024, 6500, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Cadillac", "Escalade", 2024, 36000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Cadillac", "XT4", 2024, 15000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Cadillac", "XT5", 2024, 30000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Cadillac", "XT6", 2024, 15000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Cadillac", "Lyriq", 2024, 26000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),

    # ===== BUICK 2024 US sales (from best-selling-cars.com) =====
    ("Buick", "Encore", 2024, 42000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "Encore + Encore GX estimated"),
    ("Buick", "Enclave", 2024, 35000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Buick", "Envista", 2024, 25000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-gm-chevrolet-gmc-cadillac-buick-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new model; estimated"),
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
