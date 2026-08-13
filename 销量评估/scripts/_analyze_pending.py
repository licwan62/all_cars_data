"""Analyze PENDING items and group them for batch research."""
import csv
from collections import defaultdict

queue_path = r'research_queue/model_year_research_queue.csv'
cache_path = r'cache/sales_model_year_cache.csv'

with open(queue_path, encoding='utf-8-sig') as f:
    queue = list(csv.DictReader(f))

with open(cache_path, encoding='utf-8-sig') as f:
    cache = list(csv.DictReader(f))

# Build cache key set
cache_keys = set()
for r in cache:
    cache_keys.add((r['MAKE'], r['MODEL'], r['YEAR']))

# Get PENDING items not in cache
pending = [r for r in queue if r['CACHE_STATUS'] == 'PENDING']
truly_new = []
for r in pending:
    key = (r['MAKE'], r['MODEL'], r['YEAR'])
    if key not in cache_keys:
        truly_new.append(r)

print(f"PENDING in queue: {len(pending)}")
print(f"Already in cache (but marked PENDING): {len(pending) - len(truly_new)}")
print(f"Truly new (need research): {len(truly_new)}")

# Group by MAKE+MODEL
make_model_years = defaultdict(list)
for r in truly_new:
    make_model_years[(r['MAKE'], r['MODEL'])].append(r['YEAR'])

print(f"\nUnique MAKE+MODEL combos needing research: {len(make_model_years)}")

# Group by MAKE
make_models = defaultdict(list)
for (make, model), years in sorted(make_model_years.items()):
    make_models[make].append((model, years))

print(f"\nMAKE summary (models needing research):")
for make in sorted(make_models):
    models = make_models[make]
    total_years = sum(len(y) for _, y in models)
    print(f"  {make}: {len(models)} models, {total_years} model-years")

# Show first batch
print(f"\n--- First batch: Acura ---")
for model, years in make_models.get('Acura', []):
    print(f"  {model}: {sorted(years)}")
