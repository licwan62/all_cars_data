import csv

queue_path = r'research_queue/model_year_research_queue.csv'
cache_path = r'cache/sales_model_year_cache.csv'

with open(queue_path, encoding='utf-8-sig') as f:
    queue = list(csv.DictReader(f))

with open(cache_path, encoding='utf-8-sig') as f:
    cache = list(csv.DictReader(f))

pending = [r for r in queue if r['CACHE_STATUS'] == 'PENDING']
ready = [r for r in queue if r['CACHE_STATUS'] == 'READY']

print(f"Queue total: {len(queue)}")
print(f"READY: {len(ready)}")
print(f"PENDING: {len(pending)}")
print(f"Cache entries: {len(cache)}")

# Group pending by MAKE
from collections import Counter
make_counts = Counter(r['MAKE'] for r in pending)
print(f"\nPending by MAKE (top 30):")
for make, cnt in make_counts.most_common(30):
    print(f"  {make}: {cnt}")

# Show first 20 pending
print(f"\nFirst 20 PENDING items:")
for r in pending[:20]:
    print(f"  {r['MAKE']} {r['MODEL']} {r['YEAR']}")
