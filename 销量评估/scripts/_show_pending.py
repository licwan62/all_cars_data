import csv
from collections import Counter

rows = list(csv.DictReader(open('research_queue/model_year_research_queue.csv', encoding='utf-8-sig')))
pending = [r for r in rows if r['CACHE_STATUS'] == 'PENDING']
print(f'Total PENDING: {len(pending)}')
mk = Counter(r['MAKE'] for r in pending)
print('\nBy make:')
for m, c in mk.most_common():
    print(f'  {m}: {c}')

print('\nAll remaining PENDING items:')
for r in pending:
    print(f'  {r["MAKE"]} | {r["MODEL"]} | {r["YEAR"]}')
