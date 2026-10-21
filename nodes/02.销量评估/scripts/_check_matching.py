import csv

queue = list(csv.DictReader(open('research_queue/model_year_research_queue.csv', encoding='utf-8-sig')))
cache = list(csv.DictReader(open('cache/sales_model_year_cache.csv', encoding='utf-8-sig')))

# Check Ford entries in cache
ford_cache = {r['MODEL']: int(r['MODEL_YEAR_US_SALES']) for r in cache if r['MAKE']=='Ford' and r.get('MODEL_YEAR_US_SALES','')}
print('Ford cache entries:')
for m, s in sorted(ford_cache.items()):
    print(f'  {m}: {s}')

# Check Ford entries in queue  
ford_queue = set()
for r in queue:
    if r['MAKE']=='Ford' and r['CACHE_STATUS']=='PENDING':
        ford_queue.add(r['MODEL'])
print(f'\nFord pending in queue: {sorted(ford_queue)}')

# Check matching
for model, sales in ford_cache.items():
    matching = [r for r in queue if r['MAKE']=='Ford' and r['MODEL']==model and r['YEAR']=='2025' and r['CACHE_STATUS']=='PENDING']
    print(f'\nFord {model} 2025: {len(matching)} pending in queue')
