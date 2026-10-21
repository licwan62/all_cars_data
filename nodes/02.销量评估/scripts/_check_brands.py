"""Check PENDING items for specific brands."""
import csv
from collections import defaultdict

with open(r'research_queue/model_year_research_queue.csv', encoding='utf-8-sig') as f:
    queue = list(csv.DictReader(f))

with open(r'cache/sales_model_year_cache.csv', encoding='utf-8-sig') as f:
    cache = list(csv.DictReader(f))

# Build cache key set
cache_keys = set()
for r in cache:
    if r.get("MODEL_YEAR_US_SALES", "").strip():
        cache_keys.add((r['MAKE'], r['MODEL'], r['YEAR']))

# Check specific brands
for brand in ['Alfa Romeo', 'Genesis', 'Polestar']:
    pending = [(r['MODEL'], r['YEAR']) for r in queue 
               if r['MAKE'] == brand and r['CACHE_STATUS'] == 'PENDING'
               and (r['MAKE'], r['MODEL'], r['YEAR']) not in cache_keys]
    if pending:
        models = defaultdict(list)
        for model, year in pending:
            models[model].append(year)
        print(f"\n{brand} PENDING (not in cache):")
        for model in sorted(models):
            print(f"  {model}: {sorted(models[model])}")
    else:
        print(f"\n{brand}: All PENDING items already in cache or none pending")
