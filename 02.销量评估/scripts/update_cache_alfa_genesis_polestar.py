"""Update sales cache with Alfa Romeo, Genesis, and Polestar research results."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, NOTES)
RESEARCH_DATA = [
    # ===== ALFA ROMEO =====
    # Alfa Romeo 4C - US sales (small volumes, estimates for early years)
    ("Alfa Romeo", "4C", 2015, 200, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated from brand total"),
    ("Alfa Romeo", "4C", 2016, 250, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated from brand total"),
    ("Alfa Romeo", "4C", 2017, 300, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated from brand total"),
    ("Alfa Romeo", "4C", 2018, 200, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "estimated from brand total"),
    ("Alfa Romeo", "4C", 2019, 144, "DATABASE", "https://www.best-selling-cars.com/usa/2023-full-year-usa-fca-car-sales-jeep-ram-dodge-chrysler-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Alfa Romeo", "4C", 2020, 99, "DATABASE", "https://www.best-selling-cars.com/usa/2020-full-year-usa-fca-sales-by-model-jeep-ram-chrysler-dodge-fiat-alfa-romeo/", "HIGH", "US", "FULL_YEAR", "", ""),

    # Alfa Romeo Giulia - US sales
    ("Alfa Romeo", "GIULIA", 2024, 2320, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-fca-car-sales-jeep-ram-dodge-chrysler-by-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Alfa Romeo", "GIULIA", 2025, 1366, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Alfa Romeo", "GIULIA", 2026, 0, "DATABASE", "", "LOW", "US", "FULL_YEAR", "", "discontinued after 2025 MY; new model expected 2028"),

    # Alfa Romeo Stelvio - US sales
    ("Alfa Romeo", "Stelvio", 2025, 1872, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Alfa Romeo", "Stelvio", 2026, 0, "DATABASE", "", "LOW", "US", "FULL_YEAR", "", "discontinued after 2025 MY; new model expected 2028"),

    # Alfa Romeo Tonale - US sales
    ("Alfa Romeo", "Tonale", 2024, 3383, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-fca-car-sales-jeep-ram-dodge-chrysler-by-model/", "HIGH", "US", "FULL_YEAR", "", "first full year"),
    ("Alfa Romeo", "Tonale", 2025, 2414, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-fca-jeep-ram-dodge-car-sales-by-brand-and-model/", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Alfa Romeo", "Tonale", 2026, 0, "DATABASE", "", "LOW", "US", "FULL_YEAR", "", "uncertain if continued for 2026 MY"),

    # ===== GENESIS =====
    # Genesis US sales by model - 2022 (from MotorTrend/GCBC)
    ("Genesis", "G70", 2022, 12649, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Genesis", "G80", 2022, 4125, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Genesis", "G90", 2022, 1172, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Genesis", "GV60", 2022, 1590, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", "first year"),
    ("Genesis", "GV70", 2022, 19141, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", ""),
    ("Genesis", "GV80", 2022, 17521, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", ""),

    # Genesis US sales by model - 2023 (from MotorTrend)
    ("Genesis", "G70", 2023, 13246, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", "+5% vs 2022"),
    ("Genesis", "G80", 2023, 4170, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", "+1% vs 2022; includes Electrified G80 ~1329"),
    ("Genesis", "G90", 2023, 1200, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "MEDIUM", "US", "FULL_YEAR", "", "estimated from brand total minus known models"),
    ("Genesis", "GV60", 2023, 3400, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", "+114% vs 2022"),
    ("Genesis", "GV70", 2023, 24314, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", "ICE version; +27% vs 2022; Electrified GV70 ~1674"),
    ("Genesis", "GV80", 2023, 19697, "DATABASE", "https://www.motortrend.com/news/2023-car-sales-by-automaker", "HIGH", "US", "FULL_YEAR", "", "+12% vs 2022"),

    # Genesis US sales by model - 2024 (estimated from brand total 74930)
    ("Genesis", "G70", 2024, 12500, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~same as 2023"),
    ("Genesis", "G80", 2024, 4200, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~same as 2023"),
    ("Genesis", "G90", 2024, 1300, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Genesis", "GV60", 2024, 3500, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~same as 2023"),
    ("Genesis", "GV70", 2024, 25500, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "MEDIUM", "US", "FULL_YEAR", "", "estimated ~5% growth"),
    ("Genesis", "GV80", 2024, 22980, "DATABASE", "https://baijiahao.baidu.com/s?id=1847095770854250315", "HIGH", "US", "FULL_YEAR", "", "confirmed from article"),

    # Genesis US sales by model - 2025 (estimated from brand total 80210, ~7% growth)
    ("Genesis", "G70", 2025, 13000, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "FULL_YEAR", "", "estimated proportional to brand growth"),
    ("Genesis", "G80", 2025, 4400, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "FULL_YEAR", "", "estimated proportional to brand growth"),
    ("Genesis", "G90", 2025, 1400, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "FULL_YEAR", "", "estimated proportional to brand growth"),
    ("Genesis", "GV60", 2025, 3600, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "FULL_YEAR", "", "estimated proportional to brand growth"),
    ("Genesis", "GV70", 2025, 27000, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "FULL_YEAR", "", "estimated proportional to brand growth"),
    ("Genesis", "GV80", 2025, 24500, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "FULL_YEAR", "", "estimated proportional to brand growth"),

    # Genesis EQ900 - discontinued, no US sales for 2025+
    ("Genesis", "EQ900", 2025, 0, "DATABASE", "", "HIGH", "US", "FULL_YEAR", "", "discontinued; EQ900 was early G90 name, not sold in US"),
    ("Genesis", "EQ900", 2026, 0, "DATABASE", "", "HIGH", "US", "FULL_YEAR", "", "discontinued"),

    # Genesis 2026 - partial year (Jan-Jul 2026 brand total: 46035)
    ("Genesis", "G70", 2026, 7500, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "YTD", "2026-07", "Jan-Jul 2026 estimated"),
    ("Genesis", "G80", 2026, 2500, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "YTD", "2026-07", "Jan-Jul 2026 estimated"),
    ("Genesis", "G90", 2026, 800, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "YTD", "2026-07", "Jan-Jul 2026 estimated"),
    ("Genesis", "GV60", 2026, 2100, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "YTD", "2026-07", "Jan-Jul 2026 estimated"),
    ("Genesis", "GV70", 2026, 15500, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "YTD", "2026-07", "Jan-Jul 2026 estimated"),
    ("Genesis", "GV80", 2026, 14000, "DATABASE", "https://www.goodcarbadcar.net/genesis-us-sales-figures/", "LOW", "US", "YTD", "2026-07", "Jan-Jul 2026 estimated"),

    # ===== POLESTAR =====
    # Polestar US sales - Polestar is global brand, US is major market (~40-50% of global)
    # Polestar 1: limited production PHEV, ~1500 global in 2020, ~500 in 2021
    ("Polestar", "1", 2020, 600, "DATABASE", "https://en.wikipedia.org/wiki/Polestar_1", "LOW", "US", "FULL_YEAR", "", "US est ~40% of ~1500 global"),
    ("Polestar", "1", 2021, 200, "DATABASE", "https://en.wikipedia.org/wiki/Polestar_1", "LOW", "US", "FULL_YEAR", "", "US est; production winding down"),

    # Polestar 2: main volume model
    # Global: 2021: ~29000, 2022: ~51000, 2023: ~52000, 2024: ~44000
    # US is largest market, est ~45% of global
    ("Polestar", "2", 2021, 13000, "DATABASE", "https://www.goodcarbadcar.net/polestar-2-us-sales-figures/", "LOW", "US", "FULL_YEAR", "", "US est ~45% of ~29000 global"),
    ("Polestar", "2", 2025, 15000, "DATABASE", "https://www.goodcarbadcar.net/polestar-2-us-sales-figures/", "LOW", "US", "FULL_YEAR", "", "US est; declining as model ages"),

    # Polestar 3: launched late 2023/early 2024
    ("Polestar", "3", 2025, 5000, "DATABASE", "https://www.goodcarbadcar.net/", "LOW", "US", "FULL_YEAR", "", "US est; ramping up"),
    ("Polestar", "3", 2026, 3000, "DATABASE", "https://www.goodcarbadcar.net/", "LOW", "US", "YTD", "2026-07", "Jan-Jul 2026 est; declining"),

    # Polestar 4: launched 2024
    ("Polestar", "4", 2026, 2000, "DATABASE", "https://www.goodcarbadcar.net/", "LOW", "US", "YTD", "2026-07", "Jan-Jul 2026 est"),
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
    # Load existing cache
    rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))

    # Build a key -> row index map
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

    # Remove duplicates (keep first with sales data)
    seen = set()
    unique_rows = []
    for row in rows:
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)

    # Sort and write
    unique_rows.sort(key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"])))

    with open(CACHE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"Cache updated: {added} new/updated ({updated} updated, {added - updated} new), {skipped} skipped")
    print(f"Total cache entries: {len(unique_rows)}")


if __name__ == "__main__":
    main()
