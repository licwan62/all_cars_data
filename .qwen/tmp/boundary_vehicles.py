import csv

rows = []
with open('A0.尺码计算/output/全量表_RU.csv', 'r', encoding='utf-8') as f:
    next(f)
    for row in csv.reader(f): rows.append(row)

tiers = {
    '2L-192 (\u7d27\u51d1\u9ad8\u9876)':  {'L':4520, 'W':2100, 'H':1920, 'margin':150},
    '2XL-200 (\u4e2d\u9ad8\u9876)':   {'L':4830, 'W':2100, 'H':2000, 'margin':150},
    '2XXL-545 (\u65d7\u8230\u957fMPV)':{'L':5450, 'W':2260, 'H':2380, 'margin':150},
}

for name, t in tiers.items():
    min_L = t['L'] - t['margin']
    items = []
    for row in rows:
        if len(row) < 26 or row[9] != '\u4e24\u53a2\u8f66': continue
        try:
            L = float(row[10]); W = float(row[11]) or 0
            H = float(row[12]) or 0; S = float(row[13]) or 0
        except: continue
        if L < min_L or L > t['L']: continue
        if W > t['W'] or H > t['H']: continue
        mid = row[28] if len(row) > 28 else f'{row[0]} {row[1]}'
        items.append((S, L, W, H, mid))

    items.sort(key=lambda x: -x[0])
    total_s = sum(x[0] for x in items)
    print(f'\n=== {name} (L<={t["L"]}, \u8fb9\u754c L\u2265{min_L}) ===')
    print(f'\u5171{len(items)}\u8f86 / {total_s:.0f}\u9500\u91cf\n')
    for S, L, W, H, mid in items[:25]:
        remaining = t['L'] - L
        print(f'  L={L:5.0f}(\u4f59{remaining:3.0f}) W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid}')
    if len(items) > 25:
        print(f'  ... \u8fd8\u6709{len(items)-25}\u8f86')