"""Analyze PENDING items by brand."""
import csv
from collections import defaultdict

with open(r'research_queue/model_year_research_queue.csv', encoding='utf-8-sig') as f:
    queue = list(csv.DictReader(f))

pending = [r for r in queue if r['CACHE_STATUS'] == 'PENDING']

# Group by MAKE
make_counts = defaultdict(lambda: {'models': set(), 'years': 0})
for r in pending:
    make = r['MAKE']
    make_counts[make]['models'].add(r['MODEL'])
    make_counts[make]['years'] += 1

print('Top 30 brands by PENDING model-years:')
for make, info in sorted(make_counts.items(), key=lambda x: -x[1]['years'])[:30]:
    print(f"  {make}: {len(info['models'])} models, {info['years']} model-years")

print(f"\nTotal PENDING: {len(pending)}")
