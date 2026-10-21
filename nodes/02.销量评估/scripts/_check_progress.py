import csv
from collections import Counter

atomic = list(csv.DictReader(open('work/vehicle_sales_atomic.csv', encoding='utf-8-sig')))
ready = [a for a in atomic if a['ITERATION_STATUS'] in ('READY', 'REVIEW')]
pending = [a for a in atomic if a['ITERATION_STATUS'] == 'PENDING']
print(f'Total atomic: {len(atomic)}')
print(f'  Allocated (READY+REVIEW): {len(ready)}')
print(f'  PENDING: {len(pending)}')

mc = Counter(a['MAKE'] for a in ready)
print(f'\nTop makes by allocated count:')
for m, c in mc.most_common(15):
    print(f'  {m}: {c}')
