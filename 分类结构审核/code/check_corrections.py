import csv
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parents[1] / 'artifacts'

with (ARTIFACTS / 'audit_table1_corrections.csv').open(encoding='utf-8-sig') as f:
    data = list(csv.DictReader(f))

print('=== Coupe -> Sedan 例子 ===')
for r in data:
    if r['原结构']=='Coupe' and r['建议结构']=='Sedan':
        print(f"  {r['MAKE']} {r['MODEL']} {r['版本']} {r['YEAR']}")

print()
print('=== Convertible -> Coupe 例子 ===')
count = 0
for r in data:
    if r['原结构']=='Convertible' and r['建议结构']=='Coupe':
        print(f"  {r['MAKE']} {r['MODEL']} {r['版本']} {r['YEAR']}")
        count += 1
        if count >= 15: break

print()
print('=== Wagon -> Sedan 例子 ===')
for r in data:
    if r['原结构']=='Wagon' and r['建议结构']=='Sedan':
        print(f"  {r['MAKE']} {r['MODEL']} {r['版本']} {r['YEAR']}")

print()
print('=== Pickup -> SUV 例子 ===')
for r in data:
    if r['原结构']=='Pickup' and r['建议结构']=='SUV':
        print(f"  {r['MAKE']} {r['MODEL']} {r['版本']} {r['YEAR']}")

print()
print('=== Hatchback -> Sedan 例子 ===')
for r in data:
    if r['原结构']=='Hatchback' and r['建议结构']=='Sedan':
        print(f"  {r['MAKE']} {r['MODEL']} {r['版本']} {r['YEAR']}")
