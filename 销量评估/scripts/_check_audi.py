import csv

rows = list(csv.DictReader(open('cache/sales_model_year_cache.csv', encoding='utf-8-sig')))
audi = [r for r in rows if r['MAKE']=='Audi']
print(f'Audi entries in current cache: {len(audi)}')
audi_sales = [r for r in audi if r.get('MODEL_YEAR_US_SALES','')]
print(f'  With sales data: {len(audi_sales)}')
for r in audi_sales:
    print(f'    {r["MODEL"]} {r["YEAR"]}: {r["MODEL_YEAR_US_SALES"]} ({r.get("SALES_SOURCE","")})')
