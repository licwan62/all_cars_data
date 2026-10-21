"""
Merge batch research results into the sales_model_year_cache.csv.

Reads all batch*_results.csv files from cache/research/,
deduplicates, and writes to cache/sales_model_year_cache.csv.
Also updates the CACHE_STATUS in model_year_research_queue.csv.
"""

import csv
import os
import glob
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH_DIR = os.path.join(BASE_DIR, "cache", "research")
CACHE_FILE = os.path.join(BASE_DIR, "output", "sales_model_year_cache.csv")
QUEUE_FILE = os.path.join(BASE_DIR, "output", "model_year_research_queue.csv")

CACHE_COLUMNS = [
    "MAKE", "MODEL", "YEAR",
    "SALES_MODEL_NAME", "SALES_REPORTING_GROUP",
    "MODEL_YEAR_US_SALES", "RAW_SALES",
    "SALES_SCOPE", "SALES_PERIOD", "SALES_PERIOD_END",
    "SALES_SOURCE_TYPE", "SALES_SOURCE",
    "SOURCE_URL", "SECONDARY_SOURCE_URL",
    "SOURCE_CONFIDENCE", "NOTES",
]


def load_batch_results():
    """Load all batch result CSVs and return combined rows."""
    rows = []
    patterns = [
        os.path.join(RESEARCH_DIR, "batch*_results.csv"),
        os.path.join(RESEARCH_DIR, "supplement_*.csv"),
        os.path.join(RESEARCH_DIR, "round*_*.csv"),
    ]
    files = []
    for pat in patterns:
        files.extend(sorted(glob.glob(pat)))
    files = sorted(set(files))
    print(f"Found {len(files)} batch result files:")
    for f in files:
        with open(f, "r", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            count = 0
            for row in reader:
                rows.append(row)
                count += 1
        print(f"  {os.path.basename(f)}: {count} rows")
    return rows


def deduplicate(rows):
    """Deduplicate by MAKE+MODEL+YEAR, keeping highest confidence."""
    confidence_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    best = {}
    for row in rows:
        key = (row["MAKE"], row["MODEL"], str(row["YEAR"]))
        conf = confidence_rank.get(row.get("SOURCE_CONFIDENCE", ""), 0)
        if key not in best or conf > confidence_rank.get(best[key].get("SOURCE_CONFIDENCE", ""), 0):
            best[key] = row
    return list(best.values())


def write_cache(rows):
    """Write deduplicated rows to the cache file."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CACHE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r["MAKE"], r["MODEL"], int(r["YEAR"]))):
            out = {col: row.get(col, "") for col in CACHE_COLUMNS}
            # Ensure SALES_MODEL_NAME and SALES_REPORTING_GROUP default to empty
            if not out.get("SALES_MODEL_NAME"):
                out["SALES_MODEL_NAME"] = ""
            if not out.get("SALES_REPORTING_GROUP"):
                out["SALES_REPORTING_GROUP"] = ""
            if not out.get("RAW_SALES"):
                out["RAW_SALES"] = ""
            if not out.get("SALES_PERIOD_END"):
                out["SALES_PERIOD_END"] = ""
            if not out.get("SECONDARY_SOURCE_URL"):
                out["SECONDARY_SOURCE_URL"] = ""
            if not out.get("NOTES"):
                out["NOTES"] = ""
            writer.writerow(out)
    print(f"Wrote {len(rows)} entries to {CACHE_FILE}")


def update_queue_status(rows):
    """Update CACHE_STATUS in research queue for matched entries."""
    filled_keys = set()
    for row in rows:
        key = (row["MAKE"], row["MODEL"], str(row["YEAR"]))
        filled_keys.add(key)

    # Read queue
    queue_rows = []
    with open(QUEUE_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            key = (row["MAKE"], row["MODEL"], str(row["YEAR"]))
            if key in filled_keys:
                row["CACHE_STATUS"] = "FILLED"
            queue_rows.append(row)

    # Write back
    with open(QUEUE_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(queue_rows)

    print(f"Updated queue: {len(filled_keys)} entries marked as FILLED")
    return len(filled_keys)


def main():
    print("=== Merging research batch results ===\n")

    # Load all batch results
    rows = load_batch_results()
    print(f"\nTotal raw rows: {len(rows)}")

    if not rows:
        print("No batch results found. Nothing to merge.")
        return

    # Deduplicate
    deduped = deduplicate(rows)
    print(f"After deduplication: {len(deduped)}")

    # Write cache
    write_cache(deduped)

    # Update queue status
    filled = update_queue_status(deduped)

    # Summary
    print(f"\n=== Summary ===")
    print(f"Cache entries written: {len(deduped)}")
    print(f"Queue entries updated: {filled}")


if __name__ == "__main__":
    main()
