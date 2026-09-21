import csv

rows = []
with open('A0.尺码计算/output/全量表_RU.csv', 'r', encoding='utf-8') as f:
    next(f)
    for row in csv.reader(f): rows.append(row)

# 0921.2 真实上限：各现有尺码高度上限
existing_H = {
    '2S': 1780, '2M': 1780, '2L': 1780,
    '2XL': 1880, '2XXL-510': 1880, '2XXL-525': 2060,
}

# 新尺码定义 (0921.2-真实上限.csv)
new_tiers = [
    {
        'name': '2L-192 (\u7d27\u51d1\u9ad8\u9876)',
        'code': '2L-192',
        'L': 4520, 'W': 2100, 'H': 1920,
        'below_code': '2L',  # 下面一档
        'margin': 150,
    },
    {
        'name': '2XL-200 (\u4e2d\u9ad8\u9876)',
        'code': '2XL-200',
        'L': 4830, 'W': 2100, 'H': 2000,
        'below_code': '2XL',
        'margin': 150,
    },
    {
        'name': '2XXL-545 (\u65d7\u8230\u957fMPV)',
        'code': '2XXL-545',
        'L': 5450, 'W': 2260, 'H': 2380,
        'below_code': '2XXL-525',
        'margin': 150,
    },
]

for t in new_tiers:
    min_L = t['L'] - t['margin']
    below_H = existing_H.get(t['below_code'], 0)
    
    items = []
    for row in rows:
        if len(row) < 26 or row[9] != '\u4e24\u53a2\u8f66': continue
        try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
        except: continue
        # 在新尺码长度边界内
        if L < min_L or L > t['L']: continue
        # 不超新尺码的宽高
        if W > t['W'] or H > t['H']: continue
        # 关键：必须是下面的普通尺码**装不下**的
        if H <= below_H: continue  # 下面尺码够高，不需要新尺码
        
        mid = row[28] if len(row) > 28 else f'{row[0]} {row[1]}'
        items.append((S, L, W, H, mid))
    
    items.sort(key=lambda x: -x[0])
    total_s = sum(x[0] for x in items)
    print(f"\n{'='*65}")
    print(f"{t['name']} (L<={t['L']}, \u8fb9\u754c L\u2265{min_L}, H>{below_H})")
    print(f"{'='*65}")
    num = len(items)
    info = f"\u5171{num}\u8f66\u8f86 / {total_s:.0f}\u9500\u91cf (\u53ea\u6709\u4e0b\u5c42\u5c3a\u7801\u88c5\u4e0d\u4e0b\u7684\u8f66)"
    print(info)
    
    for S, L, W, H, mid in items[:25]:
        remaining = t['L'] - L
        why_tall = f"H\u8d85{below_H:.0f}(+{H-below_H:.0f})" if H > below_H else ''
        print(f"  S={S:5.0f}  L={L:5.0f}(\u4f59{remaining:3.0f}) W={W:4.0f} H={H:4.0f}  [{why_tall:20s}]  {mid}")
    if len(items) > 25:
        print(f"  ... \u8fd8\u6709{len(items)-25}\u8f86")