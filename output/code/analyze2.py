import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

with (ROOT / '车型尺寸库.csv').open(encoding='utf-8-sig') as f:
    reader = list(csv.reader(f))
header = reader[0]
data = reader[1:]
IDX = {h: i for i, h in enumerate(header)}

# 1. 查看非标准结构的具体记录
non_standard = ['CUV', 'Minivan', 'Coupe SUV', 'Sportback', 'Roadster', 
                'Coupe/Convertible', 'Targa', 'Fastback', 'Coupe/Convertible/Targa',
                'Hardtop', 'Convertible/Targa']

for ns in non_standard:
    records = [r for r in data if r[IDX['结构']] == ns]
    if records:
        print(f'\n=== {ns} ({len(records)}条) ===')
        for r in records[:10]:
            print(f"  {r[IDX['MAKE']]} {r[IDX['MODEL']]} {r[IDX['版本']]} {r[IDX['YEAR']]} 分类={r[IDX['分类']]}")

# 2. 查看分类与结构不匹配的情况
print('\n\n=== 分类与结构不匹配 ===')
expected_map = {
    'Sedan': '三厢车', 'Coupe': '跑车', 'SUV': '越野车', 'Crossover': '跨界车',
    'Wagon': '旅行车', 'Hatchback': '两厢车', 'Convertible': '跑车',
    'Pickup': '皮卡', 'MPV': 'MPV', 'Liftback': '两厢车',
    'Roadster': '跑车', 'Targa': '跑车', 'Fastback': '三厢车',
    'CUV': '跨界车', 'Minivan': 'MPV', 'Coupe SUV': '越野车',
    'Sportback': '两厢车', 'Hardtop': '跑车',
}
for row in data:
    struct = row[IDX['结构']]
    cat = row[IDX['分类']]
    expected = expected_map.get(struct, '')
    if expected and cat != expected:
        print(f"  {row[IDX['MAKE']]} {row[IDX['MODEL']]} {row[IDX['版本']]} {row[IDX['YEAR']]} 结构={struct} 分类={cat} (期望={expected})")
