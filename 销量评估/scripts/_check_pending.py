import csv
from collections import Counter

cache = list(csv.DictReader(open('cache/sales_model_year_cache.csv', encoding='utf-8-sig')))
queue = list(csv.DictReader(open('research_queue/model_year_research_queue.csv', encoding='utf-8-sig')))

# Check what cache data exists for older years
cached_models_by_year = {}
for r in cache:
    if r.get('MODEL_YEAR_US_SALES','').strip():
        yr = r['YEAR']
        if yr not in cached_models_by_year:
            cached_models_by_year[yr] = set()
        cached_models_by_year[yr].add((r['MAKE'], r['MODEL']))

for yr in ['2020','2019','2015','2010','2005','2000']:
    if yr in cached_models_by_year:
        print(f'{yr}: {len(cached_models_by_year[yr])} models with data')

# Check remaining PENDING
pending = [r for r in queue if r['CACHE_STATUS'] == 'PENDING']
recent = [r for r in pending if int(r['YEAR']) >= 2025]
print(f'\n2025-2027 PENDING ({len(recent)}):')
for r in recent[:20]:
    print(f'  {r["MAKE"]} {r["MODEL"]} {r["YEAR"]}')

mid = [r for r in pending if 2020 <= int(r['YEAR']) <= 2024]
print(f'\n2020-2024 PENDING ({len(mid)}):')
models_mid = Counter((r['MAKE'], r['MODEL']) for r in mid)
for (m, m2), c in models_mid.most_common(15):
    print(f'  {m} {m2}: {c} years')

# Check how many PENDING can be filled from 2020 data going backwards
data_2020 = {}
for r in cache:
    if r['YEAR'] == '2020' and r.get('MODEL_YEAR_US_SALES','').strip():
        try:
            data_2020[(r['MAKE'], r['MODEL'])] = int(r['MODEL_YEAR_US_SALES'])
        except: pass

# For 2015-2019 pending, how many match 2020 data?
older = [r for r in pending if 2015 <= int(r['YEAR']) <= 2019]
matchable = sum(1 for r in older if (r['MAKE'], r['MODEL']) in data_2020)
print(f'\n2015-2019 PENDING: {len(older)}, can fill from 2020 data: {matchable}')

# Also check 2010-2014
older2 = [r for r in pending if 2010 <= int(r['YEAR']) <= 2014]
data_2015 = {}
for r in cache:
    if r['YEAR'] == '2015' and r.get('MODEL_YEAR_US_SALES','').strip():
        try:
            data_2015[(r['MAKE'], r['MODEL'])] = int(r['MODEL_YEAR_US_SALES'])
        except: pass
matchable2 = sum(1 for r in older2 if (r['MAKE'], r['MODEL']) in data_2015)
print(f'2010-2014 PENDING: {len(older2)}, can fill from 2015 data: {matchable2}')
