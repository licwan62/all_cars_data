import csv

queue = list(csv.DictReader(open('research_queue/model_year_research_queue.csv', encoding='utf-8-sig')))
cache = list(csv.DictReader(open('cache/sales_model_year_cache.csv', encoding='utf-8-sig')))

# Audi 2025 in queue
audi_q = [r for r in queue if r['MAKE']=='Audi' and r['YEAR']=='2025']
print(f'Audi 2025 in queue: {len(audi_q)}')
audi_q_filled = [r for r in audi_q if r['CACHE_STATUS']=='FILLED']
print(f'  FILLED: {len(audi_q_filled)}')

# Check cache
audi_c = [r for r in cache if r['MAKE']=='Audi' and r['YEAR']=='2025' and r.get('MODEL_YEAR_US_SALES','')]
print(f'\nAudi 2025 in cache with sales: {len(audi_c)}')
for r in audi_c:
    print(f'  {r["MODEL"]}: {r["MODEL_YEAR_US_SALES"]}')

# Matching
print('\nQueue -> Cache matching:')
for r in audi_q:
    matching = [c for c in cache if c['MAKE']=='Audi' and c['MODEL']==r['MODEL'] and c['YEAR']=='2025' and c.get('MODEL_YEAR_US_SALES','')]
    if matching:
        print(f'  {r["MODEL"]} -> {matching[0]["MODEL_YEAR_US_SALES"]}')
    else:
        print(f'  {r["MODEL"]} -> NO MATCH')
