import csv

params = {'长容差':0, '宽容差':270, '高容差':280, '余量长容差':635}
tL, tW, tH, tRem = 0, 270, 280, 635

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
            return r['code']
    return None

# Define proposed new tiers
new_tiers = [
    {'code':'2L-H',  'L':4521, 'W':1829, 'H':1640},   # eff 1920
    {'code':'2XL-H', 'L':4826, 'W':1829, 'H':1720},   # eff 2000
]

# Count coverage: how many currently unmatched 两厢车 get covered
total_unmatched = 0; new_covered = 0; new_sales = 0
covered_by_tier = {}

for row in rows:
    if len(row) < 26: continue
    if row[9] != '两厢车': continue
    try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    
    code_old = match(L, W, H, rules_by_cat['两厢车'])
    if code_old: continue
    
    total_unmatched += 1
    # Try new tiers
    all_rules = rules_by_cat['两厢车'] + new_tiers
    code_new = match(L, W, H, all_rules)
    if code_new and code_new in ('2L-H', '2XL-H'):
        new_covered += 1
        new_sales += S
        covered_by_tier.setdefault(code_new, []).append((L, W, H, S, mid))
    elif not code_new:
        pass  # still unmatched

print("=== 新增两尺码覆盖验证 ===\n")
print(f"当前两厢车未匹配: {total_unmatched}辆")
print(f"新增覆盖:          {new_covered}辆 / {new_sales:.0f}销\n")

for code in ['2L-H', '2XL-H']:
    items = covered_by_tier.get(code, [])
    s = sum(x[3] for x in items)
    print(f"--- {code} 覆盖 {len(items)}辆 / {s:.0f}销 ---")
    items.sort(key=lambda x: -x[3])
    for L, W, H, S, mid in items[:12]:
        print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid}")
    if len(items) > 12:
        print(f"  ... 还有{len(items)-12}辆")

# Still unmatched
print("\n=== 仍未被覆盖的两厢车 ===")
still_unmatched = []
for row in rows:
    if len(row) < 26: continue
    if row[9] != '两厢车': continue
    try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    code = match(L, W, H, rules_by_cat['两厢车'] + new_tiers)
    if not code:
        still_unmatched.append((L, W, H, S, mid))

print(f"共{len(still_unmatched)}辆 / {sum(x[3] for x in still_unmatched):.0f}销")
still_unmatched.sort(key=lambda x: -x[3])
for L, W, H, S, mid in still_unmatched[:20]:
    # Find closest existing tier
    closest = min(rules_by_cat['两厢车'] + new_tiers, 
                  key=lambda r: max(0,L-(r['L']+tL), W-(r['W']+tW), H-(r['H']+tH), r['L']-L-tRem))
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid}  ->closest={closest['code']}")