"""Analyze PENDING items for next batch of brands."""
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

# Get PENDING items not in cache
pending = [r for r in queue if r['CACHE_STATUS'] == 'PENDING']
truly_new = []
for r in pending:
    key = (r['MAKE'], r['MODEL'], r['YEAR'])
    if key not in cache_keys:
        truly_new.append(r)

# Group by MAKE
make_models = defaultdict(lambda: defaultdict(list))
for r in truly_new:
    make_models[r['MAKE']][r['MODEL']].append(r['YEAR'])

# Show next batch of brands to research
brands = ['Chevrolet', 'Audi', 'Toyota', 'Ford', 'Hyundai', 'Dodge', 'Honda', 'Porsche', 'Subaru', 'Mazda', 'Nissan', 'Volkswagen', 'Lexus', 'Buick', 'Cadillac', 'Jeep', 'Ram', 'Volvo', 'Land Rover', 'BMW']

for brand in brands:
    if brand in make_models:
        models = make_models[brand]
        total_years = sum(len(y) for y in models.values())
        print(f"\n{brand} ({total_years} model-years, {len(models)} models):")
        for model in sorted(models):
            years = sorted(models[model])
            print(f"  {model}: {years[0]}-{years[-1]} ({len(years)} years)")
