import csv
from collections import Counter

INPUT = "cache/sales_model_year_cache.csv"
FIELDNAMES = [
    "MAKE", "MODEL", "YEAR", "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES", "RAW_SALES", "SALES_SCOPE", "SALES_PERIOD",
    "SALES_PERIOD_END", "SALES_SOURCE_TYPE", "SALES_SOURCE", "SOURCE_URL",
    "SECONDARY_SOURCE_URL", "SOURCE_CONFIDENCE", "NOTES",
]

rows = list(csv.DictReader(open(INPUT, encoding="utf-8-sig")))
print(f"Before: {len(rows)}")

seen = set()
unique = []
for r in rows:
    key = (r["MAKE"], r["MODEL"], r["YEAR"])
    if key not in seen:
        seen.add(key)
        unique.append(r)

print(f"After: {len(unique)}")

with open(INPUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDNAMES)
    w.writeheader()
    w.writerows(unique)

verify = list(csv.DictReader(open(INPUT, encoding="utf-8-sig")))
keys = [(r["MAKE"], r["MODEL"], r["YEAR"]) for r in verify]
dups = [k for k, c in Counter(keys).items() if c > 1]
print(f"Verify duplicates: {len(dups)}")
if dups:
    print(f"  {dups[:5]}")
