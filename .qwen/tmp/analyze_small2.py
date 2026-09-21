import csv
from collections import defaultdict

params = {'长容差':0, '宽容差':270, '高容差':280, '余量长容差':635}
tL, tW, tH, tRem = 0, 270, 280, 635

rules_by_cat = {}
with open('A0.尺码计算/data/ru/尺寸/0921.0-y380&y410.csv', 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        cat = row['分类']
        if cat not in rules_by_cat: rules_by_cat[cat] = []
        rules_by_cat[cat].append({
            'code': row['亚马逊尺码'], 'L': float(row['长_mm']),
            'W': float(row['宽_mm']), 'H': float(row['高_mm']),
        })

rows = []
with open('A0.尺码计算/output/全量表_RU.csv', 'r', encoding='utf-8') as f:
    next(f)
    for row in csv.reader(f): rows.append(row)

# Collect unmatched small vehicles (L < 3800)
small_unmatched = []
for row in rows:
    if len(row) < 26: continue
    cat = row[9]
    try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    if cat not in rules_by_cat: continue
    
    rules = rules_by_cat[cat]
    # Check if matched
    matched = False
    for r in sorted(rules, key=lambda x: (x['L'], x['W'], x['H'])):
        if (r['L'] + tL >= L) and (r['W'] + tW >= W) and (r['H'] + tH >= H) and (r['L'] - L <= tRem):
            matched = True
            break
    if not matched and L < 3800:
        # Find closest rule
        closest = min(rules, key=lambda r: max(0, L-(r['L']+tL), 0, W-(r['W']+tW), 0, H-(r['H']+tH), r['L']-L-tRem))
        dL = max(0, L - (closest['L'] + tL))
        dW = max(0, W - (closest['W'] + tW))
        dH = max(0, H - (closest['H'] + tH))
        dRem = max(0, closest['L'] - L - tRem)
        reasons = []
        if dRem > 0: reasons.append(f'\u8d85\u4f59\u91cf{dRem:.0f}')
        if dL > 0: reasons.append(f'\u8d85\u957f{dL:.0f}')
        if dW > 0: reasons.append(f'\u8d85\u5bbd{dW:.0f}')
        if dH > 0: reasons.append(f'\u8d85\u9ad8{dH:.0f}')
        small_unmatched.append((cat, L, W, H, S, mid, closest['code'], '|'.join(reasons) if reasons else '?'))

# Print results
print(f'\u5171{len(small_unmatched)}\u8f86\u5c0f\u578b\u8f66\uff08L<3800mm\uff09\u672a\u5339\u914d')
print(f'\u603b\u9500\u91cf: {sum(x[4] for x in small_unmatched):.0f}')

# By category
by_cat = defaultdict(list)
for item in small_unmatched: by_cat[item[0]].append(item)
for cat in ['两厢车', '跑车', '三厢车', '越野车', '皮卡']:
    items = by_cat.get(cat, [])
    if not items: continue
    total = sum(x[4] for x in items)
    print(f'\n--- {cat}: {len(items)}\u8f86, \u9500\u91cf{total:.0f} ---')
    # Sort by sales descending
    for cat, L, W, H, S, mid, closest, reason in sorted(items, key=lambda x: -x[4]):
        print(f'  L={L:5.0f} W={W:4.0f} H={H:4.0f}  S={S:5.0f}  [{reason:10s}]  {mid:55s}  closest={closest}')

# --- What if we add a smaller tier? ---
print('\n\n=== What-if: add new small tier ===')
# Group by length ranges
groups = defaultdict(list)
for cat, L, W, H, S, mid, closest, reason in small_unmatched:
    key = f'{cat}_{L//200*200}'
    groups[key].append((cat, L, W, H, S, mid, closest, reason))

for key in sorted(groups.keys()):
    items = groups[key]
    total = sum(x[4] for x in items)
    print(f'  {key}: {len(items)}\u8f86, {total:.0f}\u9500\u91cf')

# Top vehicles by sales
print('\n\n=== Top small unmatched by sales ===')
for cat, L, W, H, S, mid, closest, reason in sorted(small_unmatched, key=lambda x: -x[4])[:30]:
    print(f'  [{cat}] L={L:5.0f} W={W:4.0f} H={H:4.0f}  S={S:5.0f}  {mid:55s}  [{reason:10s}  ->{closest}]')