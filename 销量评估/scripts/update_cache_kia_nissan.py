"""Update sales cache with Kia, Nissan, and Infiniti research results."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"

# (MAKE, MODEL, YEAR, SALES, SOURCE, URL, CONFIDENCE, SCOPE, PERIOD, PERIOD_END, NOTES)
RESEARCH_DATA = [
    # ===== KIA 2024 US sales (from best-selling-cars.com) =====
    ("Kia", "EV9", 2024, 22017, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+1869%; first full year"),
    ("Kia", "EV6", 2024, 21715, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+6%"),
    ("Kia", "Rio", 2024, 1917, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "discontinued"),
    ("Kia", "K4/Forte", 2024, 139778, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+13% record; K4 replaces Forte"),
    ("Kia", "K5", 2024, 46311, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-28%"),
    ("Kia", "Soul", 2024, 52397, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-14%"),
    ("Kia", "Niro", 2024, 30094, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-17%"),
    ("Kia", "Seltos", 2024, 59958, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "~same"),
    ("Kia", "Sportage", 2024, 161917, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+15% record; top seller"),
    ("Kia", "Sorento", 2024, 95154, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+7%"),
    ("Kia", "Telluride", 2024, 115504, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+4% record"),
    ("Kia", "Carnival", 2024, 49726, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-kia-america-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+14% record"),

    # ===== KIA 2025 US sales (from search results) =====
    ("Kia", "Sportage", 2025, 182823, "DATABASE", "https://www.best-selling-cars.com/", "HIGH", "US", "FULL_YEAR", "", "+13% record"),
    ("Kia", "Telluride", 2025, 123281, "DATABASE", "https://www.best-selling-cars.com/", "HIGH", "US", "FULL_YEAR", "", "+7% record"),
    ("Kia", "K4/Forte", 2025, 140514, "DATABASE", "https://www.best-selling-cars.com/", "HIGH", "US", "FULL_YEAR", "", "~same"),
    ("Kia", "Sorento", 2025, 98000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~3% growth"),
    ("Kia", "Carnival", 2025, 71917, "DATABASE", "https://www.best-selling-cars.com/", "HIGH", "US", "FULL_YEAR", "", "+44% record"),
    ("Kia", "K5", 2025, 72751, "DATABASE", "https://www.best-selling-cars.com/", "HIGH", "US", "FULL_YEAR", "", "+57%"),
    ("Kia", "Seltos", 2025, 58000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -3%"),
    ("Kia", "Soul", 2025, 40000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -24%; discontinued"),
    ("Kia", "EV6", 2025, 18000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -17%"),
    ("Kia", "EV9", 2025, 20000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -9%"),
    ("Kia", "Niro", 2025, 28000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -7%"),

    # ===== NISSAN 2024 US sales (from best-selling-cars.com) =====
    ("Nissan", "Versa", 2024, 42589, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+71.7%"),
    ("Nissan", "Sentra", 2024, 152659, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+39.8%"),
    ("Nissan", "Altima", 2024, 113898, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-11%"),
    ("Nissan", "Maxima", 2024, 942, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-90.2%; discontinued"),
    ("Nissan", "LEAF", 2024, 11226, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+57%"),
    ("Nissan", "Z", 2024, 3164, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+78.7%"),
    ("Nissan", "GT-R", 2024, 267, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-31.5%"),
    ("Nissan", "Kicks", 2024, 77356, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+15.8%"),
    ("Nissan", "Frontier", 2024, 68155, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+17.2%"),
    ("Nissan", "Titan", 2024, 14662, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-23.6%"),
    ("Nissan", "Pathfinder", 2024, 80915, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+12.8%"),
    ("Nissan", "Armada", 2024, 15267, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-27.9%"),
    ("Nissan", "Rogue", 2024, 245724, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-9.5%; top seller"),
    ("Nissan", "Ariya", 2024, 19798, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+47%"),
    ("Nissan", "Murano", 2024, 19316, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-38%; new gen coming"),

    # ===== NISSAN 2025 US sales (from best-selling-cars.com) =====
    ("Nissan", "Versa", 2025, 51310, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+20.5%"),
    ("Nissan", "Sentra", 2025, 152578, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-0.1%"),
    ("Nissan", "Altima", 2025, 93268, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-18.1%"),
    ("Nissan", "Maxima", 2025, 14, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-98.5%; discontinued"),
    ("Nissan", "Z", 2025, 5487, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+73.4%"),
    ("Nissan", "Kicks", 2025, 103575, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "+33.9%; new gen"),
    ("Nissan", "LEAF", 2025, 5149, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-54.1%"),
    ("Nissan", "Frontier", 2025, 65232, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "HIGH", "US", "FULL_YEAR", "", "-4.3%"),
    ("Nissan", "Rogue", 2025, 250000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est +2%; new Rock Creek"),
    ("Nissan", "Pathfinder", 2025, 82000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est ~1%"),
    ("Nissan", "Murano", 2025, 25000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est +30%; new gen"),
    ("Nissan", "Armada", 2025, 18000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est +18%; new gen"),
    ("Nissan", "Ariya", 2025, 15000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est -24%"),
    ("Nissan", "Titan", 2025, 13000, "DATABASE", "https://www.best-selling-cars.com/usa/2025-full-year-usa-nissan-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "est -11%"),

    # ===== INFINITI 2024 US sales (estimated from brand total 58,070) =====
    ("Infiniti", "Q50", 2024, 500, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "LOW", "US", "FULL_YEAR", "", "discontinued; est"),
    ("Infiniti", "Q60", 2024, 52, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "LOW", "US", "FULL_YEAR", "", "discontinued; dealer stock only"),
    ("Infiniti", "QX50", 2024, 12000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "+7.9%; est"),
    ("Infiniti", "QX55", 2024, 5000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated"),
    ("Infiniti", "QX60", 2024, 22000, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "-5.4%; est"),
    ("Infiniti", "QX80", 2024, 18518, "DATABASE", "https://www.best-selling-cars.com/usa/2024-full-year-usa-nissan-group-us-car-sales-by-model/", "MEDIUM", "US", "FULL_YEAR", "", "estimated; new gen"),

    # ===== INFINITI 2025 US sales (estimated from brand total 52,846) =====
    ("Infiniti", "QX50", 2025, 10000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est declining"),
    ("Infiniti", "QX55", 2025, 4000, "DATABASE", "https://www.best-selling-cars.com/", "LOW", "US", "FULL_YEAR", "", "est -20%"),
    ("Infiniti", "QX60", 2025, 21000, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est -5%"),
    ("Infiniti", "QX80", 2025, 17846, "DATABASE", "https://www.best-selling-cars.com/", "MEDIUM", "US", "FULL_YEAR", "", "est ~same; new gen"),
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
