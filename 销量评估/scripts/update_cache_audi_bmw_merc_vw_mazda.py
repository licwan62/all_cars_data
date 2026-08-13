"""Update sales cache with Audi, BMW, Mercedes-Benz, VW, Mazda research results."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, PERIOD_END, NOTES)
RESEARCH_DATA = [
    # ===== AUDI 2024 US sales (from search results; total 196,576 -14%) =====
    ("Audi", "Q5", 2024, 56799, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-23%; top seller"),
    ("Audi", "Q3", 2024, 32090, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+45%"),
    ("Audi", "Q4 e-tron", 2024, 8546, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+5%"),
    ("Audi", "Q4 Sportback e-tron", 2024, 2810, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+8%"),
    ("Audi", "Q6 e-tron", 2024, 17207, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "new; +1681%"),
    ("Audi", "A6 e-tron", 2024, 3931, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "new model"),
    ("Audi", "A4", 2024, 18000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "-48% est"),
    ("Audi", "A5", 2024, 22000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "+4% est"),
    ("Audi", "A6", 2024, 10000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "+2% est"),
    ("Audi", "A7", 2024, 5500, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "+5% est"),
    ("Audi", "A3", 2024, 8000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "-30% est"),
    ("Audi", "A8", 2024, 3500, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "-28% est"),
    ("Audi", "Q7", 2024, 18381, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-12%"),
    ("Audi", "Q8", 2024, 5500, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "-24% est"),
    ("Audi", "Q8 e-tron", 2024, 5264, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "-38%; Q4 e-tron renamed"),
    ("Audi", "e-tron GT", 2024, 3500, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-audi-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "-10% est"),

    # ===== AUDI 2025 US sales (estimated; total 164,942 -16%) =====
    ("Audi", "Q5", 2025, 55000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -3%"),
    ("Audi", "Q3", 2025, 30000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -7%"),
    ("Audi", "Q6 e-tron", 2025, 22000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est +28%; full year"),
    ("Audi", "Q7", 2025, 16000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -13%"),
    ("Audi", "A5", 2025, 20000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -9%; new gen A5 replaces A4"),
    ("Audi", "A6", 2025, 9000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -10%"),

    # ===== BMW 2025 US sales (from search results; total 388,897 +4.7%) =====
    ("BMW", "X3", 2025, 76546, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+11.3%; #1 BMW"),
    ("BMW", "X5", 2025, 76246, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+5.4%"),
    ("BMW", "3 Series", 2025, 33031, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+5.4%"),
    ("BMW", "2 Series", 2025, 20975, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+36.3%"),
    ("BMW", "X6", 2025, 12000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+26.6%"),
    ("BMW", "X1", 2025, 35000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est; X1+X2 combined ~90k"),
    ("BMW", "4 Series", 2025, 18000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("BMW", "5 Series", 2025, 15000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est; new gen"),
    ("BMW", "X4", 2025, 8000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est; last year"),
    ("BMW", "7 Series", 2025, 10000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("BMW", "Z4", 2025, 5000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("BMW", "iX", 2025, 8000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("BMW", "i4", 2025, 10000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("BMW", "i7", 2025, 4000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-bmw-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est"),

    # ===== BMW 2024 US sales (estimated; total ~371,487) =====
    ("BMW", "X3", 2024, 68776, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est from 2025 -11.3%"),
    ("BMW", "X5", 2024, 72340, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est from 2025 -5.4%"),
    ("BMW", "3 Series", 2024, 31338, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est from 2025 -5.4%"),
    ("BMW", "X1", 2024, 38000, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est; X1+X2"),
    ("BMW", "2 Series", 2024, 15389, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est from 2025 -36.3%"),
    ("BMW", "4 Series", 2024, 19000, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("BMW", "5 Series", 2024, 12000, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est; old gen declining"),
    ("BMW", "X6", 2024, 9479, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est from 2025 -26.6%"),
    ("BMW", "7 Series", 2024, 11000, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est"),
    ("BMW", "X4", 2024, 10000, "DATABASE", "https://www.bmwblog.com/2025/03/14/bmw-2024-sales-each-model-series/", "MEDIUM", "US", "FULL_YEAR", "", "est"),

    # ===== MERCEDES-BENZ 2024 US sales (estimated; total ~363,000) =====
    ("Mercedes-Benz", "C-Class", 2024, 55000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "E-Class", 2024, 30000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new gen est"),
    ("Mercedes-Benz", "S-Class", 2024, 12000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "GLC", 2024, 75000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "top seller est"),
    ("Mercedes-Benz", "GLE", 2024, 55000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "GLS", 2024, 30000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "GLA", 2024, 20000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "GLB", 2024, 18000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "A-Class", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "last year; est"),
    ("Mercedes-Benz", "CLA", 2024, 12000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "EQE", 2024, 8000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "EQS", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "G-Class", 2024, 10000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mercedes-Benz", "AMG GT", 2024, 3000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mercedes-benz-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),

    # ===== VOLKSWAGEN 2024 US sales (estimated; total ~290,000) =====
    ("Volkswagen", "ID.4", 2024, 20000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volkswagen", "Atlas", 2024, 55000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated; top seller"),
    ("Volkswagen", "Atlas Cross Sport", 2024, 25000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volkswagen", "Tiguan", 2024, 50000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volkswagen", "Jetta", 2024, 55000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volkswagen", "Jetta GLI", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volkswagen", "Taos", 2024, 35000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volkswagen", "Golf GTI", 2024, 8000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volkswagen", "Golf R", 2024, 3000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-volkswagen-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),

    # ===== MAZDA 2024 US sales (estimated; total ~380,000) =====
    ("Mazda", "CX-5", 2024, 95000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mazda-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "top seller est"),
    ("Mazda", "CX-30", 2024, 65000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mazda-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mazda", "CX-50", 2024, 50000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mazda-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mazda", "CX-90", 2024, 35000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mazda-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new model est"),
    ("Mazda", "Mazda3", 2024, 70000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mazda-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Mazda", "CX-70", 2024, 10000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mazda-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "new model; partial year"),
    ("Mazda", "CX-9", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mazda-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "last year; replaced by CX-90"),
    ("Mazda", "MX-5 Miata", 2024, 12000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mazda-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),

    # ===== MAZDA 2025 US sales (estimated) =====
    ("Mazda", "CX-5", 2025, 90000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -5%"),
    ("Mazda", "CX-30", 2025, 60000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -8%"),
    ("Mazda", "CX-50", 2025, 55000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est +10%"),
    ("Mazda", "CX-90", 2025, 40000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est +14%; full year"),
    ("Mazda", "Mazda3", 2025, 65000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -7%"),
    ("Mazda", "CX-70", 2025, 25000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est +150%; full year"),
    ("Mazda", "MX-5 Miata", 2025, 11000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -8%"),

    # ===== MITSUBISHI 2024 US sales (from best-selling-cars.com) =====
    ("Mitsubishi", "Mirage", 2024, 29766, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mitsubishi-motors-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+125%"),
    ("Mitsubishi", "Outlander Sport", 2024, 15125, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mitsubishi-motors-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+0.7%"),
    ("Mitsubishi", "Outlander", 2024, 45253, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mitsubishi-motors-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+6.5% record"),
    ("Mitsubishi", "Outlander PHEV", 2024, 6975, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mitsubishi-motors-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+4.4%"),
    ("Mitsubishi", "Eclipse Cross", 2024, 12724, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-mitsubishi-motors-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+28.2%"),
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
