import csv

params = {'长容差':0, '宽容差':270, '高容差':280, '余量长容差':635}
tL, tW, tH, tRem = 0, 270, 280, 635

# 新规则
rules_by_cat = {}
with open('A0.尺码计算/data/ru/尺寸/0921.1-微调&高mpv.csv', 'r', encoding='utf-8-sig') as f:
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

def match(L, W, H, rules):
    for r in sorted(rules, key=lambda x: (x['L'], x['W'], x['H'])):
        if (r['L']+tL>=L) and (r['W']+tW>=W) and (r['H']+tH>=H) and (r['L']-L<=tRem):
            return r['code'], None
    closest = min(rules, key=lambda r: max(0,L-(r['L']+tL), W-(r['W']+tW), H-(r['H']+tH), r['L']-L-tRem))
    dL = max(0, L-(closest['L']+tL))
    dW = max(0, W-(closest['W']+tW))
    dH = max(0, H-(closest['H']+tH))
    dRem = max(0, closest['L']-L-tRem)
    reasons = []
    if dRem > 0: reasons.append(f'超余量{dRem:.0f}')
    if dL > 0: reasons.append(f'超长{dL:.0f}')
    if dW > 0: reasons.append(f'超宽{dW:.0f}')
    if dH > 0: reasons.append(f'超高{dH:.0f}')
    return None, '|'.join(reasons) if reasons else '?'

# 1. 验证 Peugeot Partner Van 2008-2012 RU
print("=== 1. Peugeot Partner Van 2008-2012 RU 匹配验证 ===")
target = None
for row in rows:
    mid = row[28] if len(row)>28 else ''
    if 'Peugeot' in row[0] and 'Partner' in row[1] and '2008' in row[8] and row[9]=='两厢车':
        target = row
        break

if target:
    L = float(target[10]); W = float(target[11]) or 0; H = float(target[12]) or 0
    S = float(target[13]) if target[13] else 0
    print(f"  车型: {target[28]}")
    print(f"  尺寸: L={L:.0f} W={W:.0f} H={H:.0f} 销量={S:.0f}")
    code, reason = match(L, W, H, rules_by_cat['两厢车'])
    if code:
        # 显示匹配的规则
        for r in rules_by_cat['两厢车']:
            if r['code'] == code:
                effH = r['H'] + 280
                print(f"  匹配: {code} (L≤{r['L']:.0f} W≤{r['W']:.0f} effW≤{r['W']+270:.0f} H≤{r['H']:.0f} effH≤{effH:.0f})")
                print(f"  ✅ 已覆盖")
    else:
        print(f"  未匹配: [{reason}]")

# 2. 该附近所有两厢车（L 3800-4300, H>1700）的匹配状态
print(f"\n=== 2. Partner 附近(L3800-4300, H>1700)所有两厢车匹配状态 ===")
nearby = []
for row in rows:
    if len(row)<26: continue
    if row[9] != '两厢车': continue
    try:
        L = float(row[10]); W = float(row[11]) or 0; H = float(row[12]) or 0; S = float(row[13]) or 0
    except: continue
    if 3800 <= L <= 4300 and H > 1700:
        mid = row[28] if len(row)>28 else f"{row[0]} {row[1]}"
        code, reason = match(L, W, H, rules_by_cat['两厢车'])
        nearby.append((L, W, H, S, mid, code if code else f'❌ [{reason}]'))

nearby.sort(key=lambda x: -x[3])
print(f"  共{len(nearby)}辆")
for L, W, H, S, mid, status in nearby:
    print(f"  {'✅' if status.startswith('2') else '❌'} {status:15s} L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid}")

# 3. 统计附近超高未匹配的情况
print(f"\n=== 3. Partner 附近未匹配车辆原因分析 ===")
unmatched_nearby = [(L, W, H, S, mid, status) for L, W, H, S, mid, status in nearby if status.startswith('❌')]
print(f"  未匹配: {len(unmatched_nearby)}辆 销量{sum(x[3] for x in unmatched_nearby):.0f}")
by_reason = {}
for L, W, H, S, mid, status in unmatched_nearby:
    # Extract reason
    reason = status.split('[')[1].rstrip(']')
    if '超高' in reason: key = '超高'
    elif '超长' in reason: key = '超长'
    elif '超宽' in reason: key = '超宽'
    elif '超余量' in reason: key = '超余量'
    else: key = reason
    by_reason.setdefault(key, []).append((L, W, H, S, mid, status))

for reason, items in sorted(by_reason.items(), key=lambda x: -sum(v[3] for v in x[1])):
    print(f"  [{reason}] {len(items)}辆, 销量{sum(x[3] for x in items):.0f}")
    for L, W, H, S, mid, status in items[:10]:
        print(f"    L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid}  {status}")