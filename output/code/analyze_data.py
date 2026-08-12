import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 读取数据
with (ROOT / '车型尺寸库.csv').open(encoding='utf-8-sig') as f:
    reader = list(csv.reader(f))
header = reader[0]
data = reader[1:]

# 字段索引
IDX = {h: i for i, h in enumerate(header)}

print(f'总记录数: {len(data)}')

# 分析各结构对应的分类分布
struct_cat = defaultdict(Counter)
for row in data:
    struct = row[IDX['结构']]
    cat = row[IDX['分类']]
    struct_cat[struct][cat] += 1

print('\n=== 结构 -> 分类 映射 ===')
for struct in sorted(struct_cat.keys()):
    print(f'{struct}:')
    for cat, cnt in struct_cat[struct].most_common():
        print(f'  {cat}: {cnt}')

# 分析版本字段
print('\n=== 各结构的版本示例 ===')
for struct in ['Sedan', 'Coupe', 'SUV', 'Wagon', 'Hatchback', 'Convertible', 'Pickup', 'CUV', 'Minivan', 'Sportback', 'Roadster', 'Coupe SUV', 'Targa', 'Fastback', 'Liftback']:
    versions = set()
    for row in data:
        if row[IDX['结构']] == struct and row[IDX['版本']].strip():
            versions.add(row[IDX['版本']])
    if versions:
        print(f'{struct}: {sorted(versions)[:20]}')
