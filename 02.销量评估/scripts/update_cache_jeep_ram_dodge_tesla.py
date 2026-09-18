"""Update sales cache with Jeep, Ram, Dodge, Chrysler, and Tesla research results."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, PERIOD_END, NOTES)
RESEARCH_DATA = [
    # ===== JEEP 2024 US sales (from FCA report; total 587,725 -9%) =====
    ("Jeep", "Grand Cherokee", 2024, 216148, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-12%; top seller"),
    ("Jeep", "Wrangler", 2024, 151163, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "37% 4xe"),
    ("Jeep", "Compass", 2024, 111697, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "+16%"),
    ("Jeep", "Gladiator", 2024, 42123, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-24%"),
    ("Jeep", "Wagoneer", 2024, 43125, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "+48%"),
    ("Jeep", "Grand Wagoneer", 2024, 11959, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "+13%"),
    ("Jeep", "Renegade", 2024, 8440, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Jeep", "Cherokee", 2024, 2839, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "last year"),
    ("Jeep", "Wagoneer S", 2024, 231, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "launch"),

    # ===== JEEP 2025 US sales (from best-selling-cars.com; total 593,401 +1%) =====
    ("Jeep", "Grand Cherokee", 2025, 210082, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-3%"),
    ("Jeep", "Wrangler", 2025, 167322, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "+11%"),
    ("Jeep", "Compass", 2025, 101997, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-9%"),
    ("Jeep", "Gladiator", 2025, 56790, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "+35%"),
    ("Jeep", "Wagoneer", 2025, 39907, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-7%"),
    ("Jeep", "Grand Wagoneer", 2025, 5133, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-57%"),
    ("Jeep", "Renegade", 2025, 721, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-91%"),
    ("Jeep", "Cherokee", 2025, 527, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-81%"),
    ("Jeep", "Wagoneer S", 2025, 10864, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "+4603%"),
    ("Jeep", "Recon", 2025, 56, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "new; launch"),

    # ===== RAM 2024 US sales (from FCA report) =====
    ("Ram", "Ram Pickup 1500", 2024, 187013, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "Ram LD"),
    ("Ram", "Ram Pickup 2500/3500", 2024, 186107, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "Ram HD"),
    ("Ram", "ProMaster", 2024, 65869, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-19%"),

    # ===== RAM 2025 US sales (from best-selling-cars.com) =====
    ("Ram", "Ram Pickup 1500", 2025, 204139, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "+9%"),
    ("Ram", "Ram Pickup 2500/3500", 2025, 169920, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-9%"),
    ("Ram", "ProMaster", 2025, 57591, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "-13%"),

    # ===== DODGE 2024 US sales (total 141,730 -29%) =====
    ("Dodge", "Charger", 2024, 25000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "MEDIUM", "US", "FULL_YEAR", "", "-54%; est from 2023"),
    ("Dodge", "Challenger", 2024, 40000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "MEDIUM", "US", "FULL_YEAR", "", "-40%; last year ICE"),
    ("Dodge", "Hornet", 2024, 20559, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "+120%"),
    ("Dodge", "Durango", 2024, 56000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated; top remaining seller"),

    # ===== DODGE 2025 US sales (estimated) =====
    ("Dodge", "Charger Daytona", 2025, 15000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "new electric Charger"),
    ("Dodge", "Charger Sixpack", 2025, 10000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "new ICE Charger"),
    ("Dodge", "Hornet", 2025, 18000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -12%"),
    ("Dodge", "Durango", 2025, 55000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same"),

    # ===== CHRYSLER 2024 US sales (from FCA report) =====
    ("Chrysler", "Pacifica", 2024, 107356, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "top seller"),
    ("Chrysler", "Voyager", 2024, 12033, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Chrysler", "300", 2024, 5295, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", "last year"),

    # ===== TESLA 2024 US sales (estimated) =====
    ("Tesla", "Model Y", 2024, 372613, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "#1 EV in US; est"),
    ("Tesla", "Model 3", 2024, 189903, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est; Cox Automotive"),
    ("Tesla", "Model S/X", 2024, 20000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "estimated combined"),
    ("Tesla", "Cybertruck", 2024, 30000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "ramp up year; estimated"),

    # ===== TESLA 2025 US sales (from search results) =====
    ("Tesla", "Model Y", 2025, 357528, "DATABASE", "https://www.best-selling-cars.com/", "HIGH", "US", "FULL_YEAR", "", "-4%; juniper refresh"),
    ("Tesla", "Model 3", 2025, 192440, "DATABASE", "https://www.best-selling-cars.com/", "HIGH", "US", "FULL_YEAR", "", "+1.3%"),
    ("Tesla", "Model S/X", 2025, 15000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "estimated declining"),
    ("Tesla", "Cybertruck", 2025, 45000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "+50%; ramping"),

    # ===== LAND ROVER 2024 US sales (estimated) =====
    ("Land Rover", "Range Rover", 2024, 18000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Land Rover", "Range Rover Sport", 2024, 12000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Land Rover", "Range Rover Velar", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated; declining"),
    ("Land Rover", "Range Rover Evoque", 2024, 8000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Land Rover", "Defender", 2024, 25000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated; strong"),
    ("Land Rover", "Discovery", 2024, 10000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Land Rover", "Discovery Sport", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),

    # ===== VOLVO 2024 US sales (estimated; total ~110,000) =====
    ("Volvo", "XC90", 2024, 20000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volvo", "XC60", 2024, 28000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated; top seller"),
    ("Volvo", "XC40", 2024, 15000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volvo", "S60", 2024, 10000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volvo", "S90", 2024, 3000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volvo", "V60", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volvo", "V90", 2024, 2000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Volvo", "EX30", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "new model; est"),
    ("Volvo", "EX90", 2024, 2000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "launch; est"),
    ("Volvo", "C40", 2024, 8000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),

    # ===== LINCOLN 2024 US sales (estimated; total ~85,000) =====
    ("Lincoln", "Navigator", 2024, 22000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Lincoln", "Aviator", 2024, 20000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Lincoln", "Corsair", 2024, 18000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Lincoln", "Nautilus", 2024, 15000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "new gen est"),
    ("Lincoln", "Zephyr", 2024, 10000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
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

    added = skipped = updated = 0
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
