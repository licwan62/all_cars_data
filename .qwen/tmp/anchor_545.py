"""
Analyze 2XXL-545 (5450×2260×2380) anchor vehicles.
Rules: 0921.2-真实上限.csv - dimensions ARE the real upper limits (tolerances baked in).
"""
import csv
from collections import defaultdict

# With real upper limits (no tolerances, values ARE matching limits)
tL, tW, tH, tRem = 0, 0, 0, 0

rules_by_cat = {}
with open('A0.尺码计算/data/ru/尺寸/0921.2-真实上限.csv', 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        cat = row['分类']
        if cat not in rules_by_cat: rules_by_cat[cat] = []
        rules_by_cat[cat].append({
            'code': row['亚马逊尺码'], 'L': float(row['长_mm']),
            'W': float(row['宽_mm']), 'H': float(row['高_mm']),
        })

# 2XXL-545 details
tw = [r for r in rules_by_cat['两厢车'] if r['code'] == '2XXL-545'][0]
print(f"2XXL-545: L≤{tw['L']:.0f} W≤{tw['W']:.0f} H≤{tw['H']:.0f}")
print()

rows = []
with open('A0.尺码计算/output/全量表_RU.csv', 'r', encoding='utf-8') as f:
    next(f)
    for row in csv.reader(f): rows.append(row)

def match(L, W, H, rules):
    for r in sorted(rules, key=lambda x: (x['L'], x['W'], x['H'])):
        if L <= r['L'] and W <= r['W'] and H <= r['H']:
            return r['code']
    return None

# First: what currently unmatched 两厢车 does 2XXL-545 cover?
print("=== 当前在 0921.2 规则下，2XXL-545 能覆盖的未匹配两厢车 ===")
print()

candidates = []
for row in rows:
    if len(row) < 26: continue
    if row[9] != '两厢车': continue
    try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    
    # Check if matched in current 0921.2 rules
    code = match(L, W, H, rules_by_cat['两厢车'])
    
    # Does 2XXL-545 fit?
    fits_545 = (L <= tw['L'] and W <= tw['W'] and H <= tw['H'])
    
    if not code and fits_545:
        candidates.append((L, W, H, S, mid))
    elif fits_545 and code and code != '2XXL-545':
        # Already matched by another tier - include for reference
        pass

candidates.sort(key=lambda x: -x[3])
print(f"2XXL-545 新覆盖: {len(candidates)}辆 / {sum(x[3] for x in candidates):.0f}销")
print()
for L, W, H, S, mid in candidates[:10]:
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid}")
if len(candidates) > 10:
    print(f"  ... 还有{len(candidates)-10}辆")

# Also: vehicles that currently match to 2XXL-525 or smaller tiers but are close to 2XXL-545 limits
# This helps identify if 2XXL-545 is capturing vehicles that used to be well-served
print()
print("=== 现匹配到 2XXL-525 但 L/W/H 离 2XXL-545 边界很近的车辆 ===")
borderline = []
for row in rows:
    if len(row) < 26: continue
    if row[9] != '两厢车': continue
    try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    code = match(L, W, H, rules_by_cat['两厢车'])
    if code == '2XXL-540' or code == '2XXL-525':
        fits_545 = (L <= tw['L'] and W <= tw['W'] and H <= tw['H'])
        if fits_545:
            borderline.append((L, W, H, S, mid, code))

borderline.sort(key=lambda x: -x[3])
print(f"本可落入 2XXL-545 但现匹配到 2XXL-525/540 的车辆: {len(borderline)}辆 / {sum(x[3] for x in borderline):.0f}销")
for L, W, H, S, mid, code in borderline[:10]:
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid:50s} now={code}")
if len(borderline) > 10:
    print(f"  ... 还有{len(borderline)-10}辆")

# Determine the best anchor candidates
print()
print("=== 2XXL-545 最佳锚点车型分析 ===")

# Group candidates by vehicle type cluster
clusters = defaultdict(list)
for L, W, H, S, mid in candidates:
    # Determine cluster based on name keywords
    if any(k in mid for k in ['Mercedes-Benz V', 'Mercedes V', 'Vito', 'V-Класс']):
        clusters['Mercedes V-Class/Vito'].append((L, W, H, S, mid))
    elif any(k in mid for k in ['Wey', 'Gaoshan', 'High Mountain']):
        clusters['Wey Gaoshan'].append((L, W, H, S, mid))
    elif any(k in mid for k in ['Ford Transit', 'Tourneo', 'Transit']):
        clusters['Ford Transit/Tourneo'].append((L, W, H, S, mid))
    elif any(k in mid for k in ['Volkswagen', 'Caravelle', 'Transporter', 'Multivan']):
        clusters['VW Caravelle/Transporter'].append((L, W, H, S, mid))
    elif any(k in mid for k in ['Renault Trafic', 'Trafic']):
        clusters['Renault Trafic'].append((L, W, H, S, mid))
    elif any(k in mid for k in ['Citroen', 'Peugeot', 'Opel', 'SpaceTourer', 'Zafira', 'Scudo', 'Jumpy', 'Travelle']):
        clusters['PSA MPV (Citroen/Peugeot/Opel)'].append((L, W, H, S, mid))
    elif any(k in mid for k in ['Chevrolet Express', 'GMC', 'Savana']):
        clusters['GM Van (Express/Savana)'].append((L, W, H, S, mid))
    elif any(k in mid for k in ['Toyota HiAce', 'HiAce']):
        clusters['Toyota HiAce'].append((L, W, H, S, mid))
    elif any(k in mid for k in ['Iveco', 'Daily']):
        clusters['Iveco Daily'].append((L, W, H, S, mid))
    else:
        clusters['其他'].append((L, W, H, S, mid))

for cluster, items in sorted(clusters.items(), key=lambda x: -sum(v[3] for v in x[1])):
    items.sort(key=lambda x: -x[3])
    total = sum(x[3] for x in items)
    print(f"\n{cluster}: {len(items)}辆 / {total:.0f}销")
    for L, W, H, S, mid in items[:5]:
        print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid}")
    if len(items) > 5:
        print(f"  ... 还有{len(items)-5}辆")

# Find the dimension extremes for anchor recommendation
Ls = [x[0] for x in candidates]
Ws = [x[1] for x in candidates]
Hs = [x[2] for x in candidates]
print(f"\n维度范围: L={min(Ls):.0f}-{max(Ls):.0f}  W={min(Ws):.0f}-{max(Ws):.0f}  H={min(Hs):.0f}-{max(Hs):.0f}")

# Sales-weighted midpoint (以销量为中点的"典型车")
# Find the vehicle closest to the weighted average dimensions
avg_L = sum(x[0]*x[3] for x in candidates) / sum(x[3] for x in candidates)
avg_W = sum(x[1]*x[3] for x in candidates) / sum(x[3] for x in candidates)
avg_H = sum(x[2]*x[3] for x in candidates) / sum(x[3] for x in candidates)
print(f"\n销量加权平均: L={avg_L:.0f} W={avg_W:.0f} H={avg_H:.0f}")

# Find top anchors by sales within dimensions that represent the tier
print()
print("=== 推荐的 4 个锚点车型 ===")
print("(按销量排序，覆盖尺寸范围的代表性车辆)")

# Best anchor candidates ranked by sales, covering diverse vehicle types
top_anchors = []
seen_types = set()
for L, W, H, S, mid in candidates:
    # Skip Smart and other micro cars (not the target)
    vtype = 'car'
    if any(k in mid for k in ['V-Class', 'Vito', 'V-Класс', 'Viano', 'EQV']):
        vtype = 'benz_mpv'
    elif any(k in mid for k in ['Wey', 'Gaoshan']):
        vtype = 'wey'
    elif any(k in mid for k in ['Ford Transit', 'Tourneo', 'Transit']):
        vtype = 'ford'
    elif any(k in mid for k in ['Caravelle', 'Multivan', 'Transporter']):
        vtype = 'vw'
    elif any(k in mid for k in ['Trafic', 'Vivaro']):
        vtype = 'renault'
    elif any(k in mid for k in ['Express', 'Savana']):
        vtype = 'gm'
    elif any(k in mid for k in ['Scudo', 'Jumpy', 'SpaceTourer', 'Zafira']):
        vtype = 'psa'
    elif any(k in mid for k in ['HiAce']):
        vtype = 'toyota'
    
    if vtype not in seen_types:
        seen_types.add(vtype)
        top_anchors.append((S, L, W, H, mid, vtype))

top_anchors.sort(key=lambda x: -x[0])
rank = 0
for S, L, W, H, mid, vtype in top_anchors[:6]:
    rank += 1
    dim_status = ""
    if L > 5300: dim_status += "超长 "
    if W > 2100: dim_status += "超宽 "
    if H > 2200: dim_status += "超高 "
    print(f"\n#{rank} [{vtype}] {mid}")
    print(f"     L={L:.0f} W={W:.0f} H={H:.0f} S={S:.0f}  {dim_status}")
    if rank >= 4: break

# Final recommendation with rationale
print()
print("=== 2XXL-545 锚点适用性评估 ===")
print(f"2XXL-545 上限: L=5450 W=2260 H=2380")
print(f"目标区间: 长Mpv L=5000-5450 W=1800-2200 H=1800-2300")
print(f"当前可新覆盖: {len(candidates)}辆 / {sum(x[3] for x in candidates):.0f}销")