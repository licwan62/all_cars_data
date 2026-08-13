"""Update research queue status for researched items."""
import csv

QUEUE_CSV = r"research_queue/model_year_research_queue.csv"
CACHE_CSV = r"cache/sales_model_year_cache.csv"

# Load cache keys that have sales data
with open(CACHE_CSV, encoding="utf-8-sig") as f:
    cache = list(csv.DictReader(f))

cache_with_sales = set()
for row in cache:
    if row.get("MODEL_YEAR_US_SALES", "").strip():
        cache_with_sales.add((row["MAKE"], row["MODEL"], row["YEAR"]))

# Update queue
with open(QUEUE_CSV, encoding="utf-8-sig") as f:
    queue = list(csv.DictReader(f))

updated = 0
for row in queue:
    key = (row["MAKE"], row["MODEL"], row["YEAR"])
    if key in cache_with_sales and row["CACHE_STATUS"] == "PENDING":
        row["CACHE_STATUS"] = "READY"
        updated += 1

# Write back
fieldnames = ["MAKE", "MODEL", "YEAR", "CACHE_STATUS", "SEARCH_QUERY"]
with open(QUEUE_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(queue)

# Count remaining
pending = sum(1 for r in queue if r["CACHE_STATUS"] == "PENDING")
ready = sum(1 for r in queue if r["CACHE_STATUS"] == "READY")
print(f"Updated {updated} items from PENDING to READY")
print(f"Queue: {ready} READY, {pending} PENDING, {len(queue)} total")
