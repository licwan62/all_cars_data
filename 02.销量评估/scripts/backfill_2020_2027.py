"""Backfill 2020-2027 estimates using existing 2024/2025 cache data with name mapping."""
import csv

CACHE_CSV = r"cache/sales_model_year_cache.csv"
QUEUE_CSV = r"research_queue/model_year_research_queue.csv"

# Name mapping: queue model name -> cache model name
NAME_MAP = {
    # Audi combined names
    ("Audi", "A3/S3/RS3"): ("Audi", "A3"),
    ("Audi", "A4/S4"): ("Audi", "A4"),
    ("Audi", "A4 allroad quattro"): ("Audi", "A4"),
    ("Audi", "A5/S5"): ("Audi", "A5"),
    ("Audi", "A6/S6"): ("Audi", "A6"),
    ("Audi", "A6 allroad quattro"): ("Audi", "A6"),
    ("Audi", "A6 e-tron/S6 e-tron"): ("Audi", "A6 e-tron"),
    ("Audi", "A8/S8"): ("Audi", "A8"),
    ("Audi", "Q6/SQ6 e-tron"): ("Audi", "Q6 e-tron"),
    ("Audi", "Q8 e-tron/SQ8 e-tron"): ("Audi", "Q8 e-tron"),
    ("Audi", "e-tron GT/RS e-tron GT"): ("Audi", "e-tron GT"),
    ("Audi", "e-tron GT/S e-tron GT/RS e-tron GT"): ("Audi", "e-tron GT"),
    ("Audi", "e-tron/S e-tron"): ("Audi", "Q8 e-tron"),
    ("Audi", "RS6"): ("Audi", "A6"),
    ("Audi", "RS7"): ("Audi", "A7"),
    ("Audi", "R8/R8 GT"): ("Audi", "R8"),
    ("Audi", "TT/TTS/TT RS"): ("Audi", "TT"),
    # BMW
    ("BMW", "8 Series"): ("BMW", "8 Series"),
    ("BMW", "X7"): ("BMW", "X7"),
    ("BMW", "XM"): ("BMW", "XM"),
    ("BMW", "i3"): ("BMW", "i3"),
    ("BMW", "i5"): ("BMW", "i5"),
    ("BMW", "i8"): ("BMW", "i8"),
    # Ram
    ("Ram", "1500"): ("Ram", "Ram Pickup 1500"),
    ("Ram", "1500 Classic"): ("Ram", "Ram Pickup 1500"),
    ("Ram", "2500/3500"): ("Ram", "Ram Pickup 2500/3500"),
    # Tesla
    ("Tesla", "Model S"): ("Tesla", "Model S/X"),
    ("Tesla", "Model X"): ("Tesla", "Model S/X"),
    ("Tesla", "Model Y L"): ("Tesla", "Model Y"),
    # MINI
    ("MINI", "Hardtop"): ("MINI", "Cooper"),
    ("MINI", "Hatchback"): ("MINI", "Cooper"),
    ("MINI", "Convertible"): ("MINI", "Cooper"),
    ("MINI", "Clubman"): ("MINI", "Countryman"),
    ("MINI", "Cooper SE"): ("MINI", "Cooper"),
    # Maserati
    ("Maserati", "Ghibli"): ("Maserati", "Ghibli"),
    ("Maserati", "Grecale"): ("Maserati", "Grecale"),
    ("Maserati", "Levante"): ("Maserati", "Levante"),
    ("Maserati", "Quattroporte"): ("Maserati", "Quattroporte"),
    ("Maserati", "GranTurismo"): ("Maserati", "GranTurismo"),
    ("Maserati", "MC20"): ("Maserati", "MC20"),
    # Jaguar
    ("Jaguar", "F-Pace"): ("Jaguar", "F-Pace"),
    ("Jaguar", "E-Pace"): ("Jaguar", "E-Pace"),
    ("Jaguar", "I-Pace"): ("Jaguar", "I-Pace"),
    ("Jaguar", "XE"): ("Jaguar", "XE"),
    ("Jaguar", "XF"): ("Jaguar", "XF"),
    ("Jaguar", "F-Type"): ("Jaguar", "F-Type"),
    # Mazda
    ("Mazda", "3"): ("Mazda", "Mazda3"),
    ("Mazda", "MX-5"): ("Mazda", "MX-5 Miata"),
    ("Mazda", "Miata"): ("Mazda", "MX-5 Miata"),
    ("Mazda", "MX-30"): ("Mazda", "MX-30"),
    # Land Rover
    ("Land Rover", "Evoque"): ("Land Rover", "Range Rover Evoque"),
    # Mercedes-Benz
    ("Mercedes-Benz", "CLS-Class"): ("Mercedes-Benz", "CLS-Class"),
    ("Mercedes-Benz", "EQB"): ("Mercedes-Benz", "EQB"),
    ("Mercedes-Benz", "SL-Class"): ("Mercedes-Benz", "SL-Class"),
    ("Mercedes-Benz", "SLC-Class"): ("Mercedes-Benz", "SLC-Class"),
    # Porsche
    ("Porsche", "Boxster"): ("Porsche", "Boxster"),
    ("Porsche", "Cayman"): ("Porsche", "Cayman"),
    # Others
    ("Chevrolet", "Impala"): ("Chevrolet", "Impala"),
    ("Chevrolet", "Sonic"): ("Chevrolet", "Sonic"),
    ("Chrysler", "300 series"): ("Chrysler", "300"),
    ("Dodge", "Caravan"): ("Dodge", "Grand Caravan"),
    ("GMC", "Sierra EV"): ("GMC", "Sierra EV"),
    ("GMC", "Yukon XL"): ("GMC", "Yukon XL"),
    ("Honda", "Clarity"): ("Honda", "Clarity"),
    ("Honda", "Clarity Plug In"): ("Honda", "Clarity"),
    ("Honda", "Insight"): ("Honda", "Insight"),
    ("Hyundai", "Accent"): ("Hyundai", "Accent"),
    ("Hyundai", "Elantra GT"): ("Hyundai", "Elantra"),
    ("Hyundai", "Ioniq"): ("Hyundai", "Ioniq"),
    ("Hyundai", "Ioniq 9"): ("Hyundai", "Ioniq 9"),
    ("Lucid Motors", "Air"): ("Lucid Motors", "Air"),
    ("Lucid Motors", "Gravity"): ("Lucid Motors", "Gravity"),
    ("Toyota", "86"): ("Toyota", "GR86"),
    ("Toyota", "Corolla GR"): ("Toyota", "Corolla"),
    ("Toyota", "Prius Prime"): ("Toyota", "Prius"),
    ("Volkswagen", "Arteon"): ("Volkswagen", "Arteon"),
    ("Volvo", "EX40"): ("Volvo", "XC40"),
    ("Nissan", "Rogue Sport"): ("Nissan", "Rogue Sport"),
    ("Karma Automotive", "GS-6"): ("Karma Automotive", "GS-6"),
    ("Karma Automotive", "Revero"): ("Karma Automotive", "Revero"),
    ("Cadillac", "Optiq"): ("Cadillac", "Optiq"),
    ("Cadillac", "Vistiq"): ("Cadillac", "Vistiq"),
    ("Ineos Automotive", "Grenadier"): ("Ineos Automotive", "Grenadier"),
    ("Lincoln", "Continental"): ("Lincoln", "Continental"),
    ("FIAT", "500L"): ("Fiat", "500L"),
    ("Fiat", "124 Spider"): ("Fiat", "124 Spider"),
    ("Fiat", "500X"): ("Fiat", "500X"),
    ("Ford", "GT"): ("Ford", "GT"),
    ("Buick", "Regal"): ("Buick", "Regal"),
    ("VinFast", "VF8"): ("VinFast", "VF 8"),
}

# Brand annual growth/decline rates for backfill
BRAND_RATES = {
    "Audi": -0.05, "BMW": 0.02, "Mercedes-Benz": -0.03, "Toyota": 0.02,
    "Honda": -0.02, "Ford": -0.03, "Chevrolet": -0.04, "Nissan": -0.08,
    "Hyundai": 0.04, "Kia": 0.05, "Mazda": 0.03, "Subaru": 0.02,
    "Volkswagen": -0.05, "Tesla": 0.10, "Jeep": -0.02, "Ram": 0.01,
    "Dodge": -0.10, "Chrysler": -0.08, "GMC": -0.02, "Cadillac": -0.05,
    "Lexus": 0.03, "Porsche": 0.05, "Land Rover": -0.06, "Jaguar": -0.15,
    "Volvo": -0.03, "Lincoln": -0.08, "Maserati": -0.15, "MINI": -0.05,
    "Mitsubishi": -0.05, "Infiniti": -0.10, "Genesis": 0.20,
    "Lucid Motors": 0.30, "Rivian": 0.40, "Polestar": 0.30,
    "Fiat": -0.20, "Alfa Romeo": -0.05, "Buick": -0.10,
    "Karma Automotive": -0.10, "Ineos Automotive": 0.50,
    "VinFast": 0.50,
}


def main():
    cache_rows = list(csv.DictReader(open(CACHE_CSV, encoding="utf-8-sig")))
    queue_rows = list(csv.DictReader(open(QUEUE_CSV, encoding="utf-8-sig")))

    # Build lookup: (MAKE, MODEL, YEAR) -> sales from cache
    cache_data = {}
    for r in cache_rows:
        if r.get("MODEL_YEAR_US_SALES", "").strip():
            try:
                sales = int(r["MODEL_YEAR_US_SALES"])
                cache_data[(r["MAKE"], r["MODEL"], r["YEAR"])] = {
                    "sales": sales,
                    "scope": r.get("SALES_SCOPE", "US"),
                    "source_url": r.get("SOURCE_URL", ""),
                }
            except ValueError:
                pass

    # Build best-year lookup (prefer 2024, fallback to 2025, then 2023)
    best_data = {}
    for year in ["2024", "2025", "2023"]:
        for (make, model, yr), info in cache_data.items():
            if yr == year and (make, model) not in best_data:
                best_data[(make, model)] = info

    # Get PENDING items for 2020-2027
    pending_items = []
    for r in queue_rows:
        if r["CACHE_STATUS"] == "PENDING" and 2020 <= int(r["YEAR"]) <= 2027:
            pending_items.append(r)

    # Check what's already in cache
    existing_keys = set(cache_data.keys())

    fieldnames = [
        "MAKE", "MODEL", "YEAR", "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
        "MODEL_YEAR_US_SALES", "RAW_SALES", "SALES_SCOPE", "SALES_PERIOD",
        "SALES_PERIOD_END", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
        "SECONDARY_SOURCE_URL", "SOURCE_CONFIDENCE", "NOTES",
    ]

    new_entries = []
    filled = 0
    no_data = 0

    for item in pending_items:
        q_make = item["MAKE"]
        q_model = item["MODEL"]
        year = int(item["YEAR"])

        cache_key = (q_make, q_model, str(year))
        if cache_key in existing_keys:
            continue  # Already in cache

        # Try name mapping
        lookup_key = (q_make, q_model)
        if (q_make, q_model) not in best_data:
            mapped = NAME_MAP.get((q_make, q_model))
            if mapped and mapped in best_data:
                lookup_key = mapped
            else:
                no_data += 1
                continue

        base_info = best_data[lookup_key]
        base_sales = base_info["sales"]

        if base_sales == 0:
            continue

        # Calculate year offset from base year (2024)
        offset = year - 2024
        rate = BRAND_RATES.get(q_make, -0.02)

        # Apply compound rate
        est_sales = max(1, int(base_sales * ((1 + rate) ** offset)))

        entry = {
            "MAKE": q_make,
            "MODEL": q_model,
            "YEAR": str(year),
            "SALES_MODEL_NAME": "",
            "SALES_REPORTING_GROUP": "",
            "MODEL_YEAR_US_SALES": str(est_sales),
            "RAW_SALES": "",
            "SALES_SCOPE": base_info["scope"],
            "SALES_PERIOD": "FULL_YEAR",
            "SALES_PERIOD_END": "",
            "SALES_SOURCE_TYPE": "DATABASE",
            "SALES_SOURCE": "ESTIMATE",
            "SOURCE_URL": base_info["source_url"] or "https://www.best-selling-cars.com/",
            "SECONDARY_SOURCE_URL": "",
            "SOURCE_CONFIDENCE": "LOW",
            "NOTES": f"Backfill est from {lookup_key[0]} {lookup_key[1]} 2024 ({base_sales}); rate={rate:+.0%}/yr",
        }
        new_entries.append(entry)
        filled += 1

    # Add new entries
    all_rows = cache_rows + new_entries

    # Deduplicate
    seen = set()
    unique = []
    for row in all_rows:
        key = (row["MAKE"], row["MODEL"], row["YEAR"])
        if key not in seen:
            seen.add(key)
            unique.append(row)

    unique.sort(key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"])))

    with open(CACHE_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique)

    print(f"Backfilled {filled} entries for 2020-2027")
    print(f"Could not fill: {no_data} items (no base data)")
    print(f"Total cache entries: {len(unique)}")


if __name__ == "__main__":
    main()
