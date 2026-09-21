"""
Analyze RU market: find remaining 无可用尺码 vehicles and cluster anchor vehicles.
Uses new rule file: 0921.0-y380&y410.csv
"""
import csv
from collections import defaultdict

RULE_PATH = r'A0.尺码计算\data\ru\尺寸\0921.0-y380&y410.csv'
FULL_PATH = r'A0.尺码计算\output\全量表_RU.csv'

# --- Read rules ---
rules = []
with open(RULE_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['分类'] == '越野车':
            rules.append({
                'code': row['亚马逊尺码'],
                'ozon': row['OZON尺码'],
                'ship': row['发货尺码'],
                'L': float(row['长_mm']),
                'W': float(row['宽_mm']),
                'H': float(row['高_mm']),
            })

print("=== Current SUV Rules ===")
for r in rules:
    print(f"  {r['code']:10s} OZON={r['ozon']:4s} ship={r['ship']:4s}  L={r['L']:5.0f} W={r['W']:5.0f} H={r['H']:5.0f}")

# --- Read full table ---
rows = []
with open(FULL_PATH, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        rows.append(row)

# Column index: 0=MAKE 1=MODEL 4=结构 9=分类 10=L 11=W 12=H 13=销量 20=自动尺码 24=候选 25=原因
# We need to simulate matching with new rules

def match_vehicle(L, W, H, rules):
    """Find the best matching rule for a vehicle."""
    best = None
    for r in rules:
        if L <= r['L'] and W <= r['W'] and H <= r['H']:
            if best is None or (r['L'] < best['L'] or (r['L'] == best['L'] and r['W'] < best['W'])):
                best = r
    return best

def get_issue(L, W, H, r):
    """Determine the most restrictive issue."""
    if L > r['L']: return '超长', L - r['L']
    if W > r['W']: return '超宽', W - r['W']
    if H > r['H']: return '超高', H - r['H']
    issues = []
    vals = []
    margin_L = r['L'] - L
    margin_W = r['W'] - W
    margin_H = r['H'] - H
    if margin_L < 0: issues.append('超长'); vals.append(-margin_L)
    if margin_W < 0: issues.append('超宽'); vals.append(-margin_W)
    if margin_H < 0: issues.append('超高'); vals.append(-margin_H)
    if issues: return issues[0], vals[0]
    # All within limits - check if too small for this tier
    min_L = rules[rules.index(r)-1]['L'] if rules.index(r) > 0 else 0
    min_W = rules[rules.index(r)-1]['W'] if rules.index(r) > 0 else 0
    if L < min_L and L < (min_L + r['L']) / 2:
        return '超余量', min_L - L
    return 'OK', 0

# Group A: 越野车 that are currently "无可用尺码" - simulate with new rules
print('\n=== Simulating matching with new rules ===')

# Categorize all 越野车 by their match status with new rules
matched_new = []
unmatched = []
for row in rows:
    if len(row) < 26: continue
    if row[9] != '越野车': continue
    try:
        L = float(row[10]); W = float(row[11]) if row[11] else 0
        H = float(row[12]) if row[12] else 0; S = float(row[13]) if row[13] else 0
    except: continue
    
    match = match_vehicle(L, W, H, rules)
    if match:
        matched_new.append((L, W, H, S, match['code'], row[28], row[0], row[1]))
    else:
        # Find closest rule
        closest = None
        best_dist = float('inf')
        for r in rules:
            dist = abs(L - r['L']) + abs(W - r['W']) + abs(H - r['H'])
            if dist < best_dist:
                best_dist = dist
                closest = r
        unmatched.append((L, W, H, S, closest, row[28], row[0], row[1], row[24] if len(row)>24 else ''))

print(f'\nMatched with new rules: {len(matched_new)}')
print(f'Still unmatched: {len(unmatched)}')

# --- Cluster analysis on unmatched ---
print('\n=== STILL UNMATCHED (sorted by length) ===')
unmatched_by_L = sorted(unmatched, key=lambda x: x[0])
ts = 0
for L, W, H, S, closest, mid, make, model, old_cand in unmatched_by_L:
    ts += S
    why = ''
    if closest:
        fails = []
        if L > closest['L']: fails.append(f'长超{closest["L"]:.0f}({L-closest["L"]:.0f})')
        if W > closest['W']: fails.append(f'宽超{closest["W"]:.0f}({W-closest["W"]:.0f})')
        if H > closest['H']: fails.append(f'高超{closest["H"]:.0f}({H-closest["H"]:.0f})')
        why = ','.join(fails)
    print(f'{mid:55s} L={L:5.0f} W={W:5.0f} H={H:5.0f} closest={closest["code"] if closest else "?":8s} why={why:30s} old_cand={old_cand:6s} sales={S:5.0f}')
print(f'Count: {len(unmatched)} Total sales: {ts:.0f}')

# --- Now find clusters ---
print('\n=== CLUSTER ANALYSIS ===')

# Cluster by height ranges (height is the main issue)
h_clusters = defaultdict(list)
for L, W, H, S, closest, mid, make, model, old_cand in unmatched:
    h_key = f'H{int(H//100)*100}-{int(H//100)*100+99}'
    h_clusters[h_key].append((L, W, H, S, mid, make, model, closest))

for h_key in sorted(h_clusters.keys()):
    items = h_clusters[h_key]
    items.sort(key=lambda x: x[0])
    ts_c = sum(x[3] for x in items)
    Ls = [x[0] for x in items]
    Ws = [x[1] for x in items]
    Hs = [x[2] for x in items]
    print(f'\n=== Height cluster {h_key} ({len(items)} vehicles, {ts_c:.0f} sales) ===')
    print(f'   L: {min(Ls):.0f}-{max(Ls):.0f}  W: {min(Ws):.0f}-{max(Ws):.0f}  H: {min(Hs):.0f}-{max(Hs):.0f}')
    for L, W, H, S, mid, make, model, closest in items:
        print(f'   {mid:55s} L={L:5.0f} W={W:5.0f} H={H:5.0f} closest={closest["code"] if closest else "?":8s} sales={S:5.0f}')

# --- Anchor vehicle candidates ---
print('\n=== TOP ANCHOR CANDIDATES ===')
print('These vehicles represent the densest clusters around them.')

# For each unmatched vehicle, count how many others could be covered
# if we set a tier at (L+delta, W+delta, H+delta) centered on this vehicle
anchors = []
for L, W, H, S, closest, mid, make, model, old_cand in unmatched:
    # Define a tier that covers this vehicle with some margin
    tier_L = L + 100  # 100mm margin
    tier_W = max(W + 70, 1500)  # 70mm margin
    tier_H = H + 80  # 80mm margin
    
    # Count how many unmatched vehicles this tier would cover
    covered = []
    covered_sales = 0
    for L2, W2, H2, S2, c2, mid2, m2, md2, oc2 in unmatched:
        if L2 <= tier_L and W2 <= tier_W and H2 <= tier_H:
            covered.append(mid2)
            covered_sales += S2
    
    if covered_sales > 0:  # At least itself
        anchors.append((len(covered), covered_sales, tier_L, tier_W, tier_H, mid, L, W, H, covered))

# Sort by coverage count, then by sales
anchors.sort(key=lambda x: (-x[1], -x[0]))

# Show top anchors
seen_vehicles = set()
for n_cov, s_cov, tL, tW, tH, mid, L, W, H, covered in anchors[:20]:
    if mid in seen_vehicles:
        continue
    seen_vehicles.add(mid)
    # Remove already-seen vehicles from the covered list for cleaner display
    disp_covered = [v for v in covered if v not in seen_vehicles or v == mid]
    print(f'\nAnchor: {mid}')
    print(f'  Vehicle size: L={L:.0f} W={W:.0f} H={H:.0f}')
    print(f'  Suggested tier: L<={tL:.0f} W<={tW:.0f} H<={tH:.0f}')
    print(f'  Covers {n_cov} vehicles / {s_cov:.0f} sales')
    if len(disp_covered) <= 5:
        for v in disp_covered:
            print(f'    - {v}')

# --- Unique clusters by dimension range ---
print('\n\n=== BEST CLUSTER PROPOSALS ===')
# Find the best covering clusters by iterating over dimension combinations

# Method: for each unmatched vehicle as lower bound, find how many can fit in a 
# reasonably-sized tier (allowing ~200mm L margin, ~100mm W, ~150mm H)
proposals = []
for L0, W0, H0, S0, c0, mid0, mk0, md0, oc0 in unmatched:
    tier_L = L0 + 200  # generous but not excessive
    tier_W = W0 + 100
    tier_H = H0 + 150
    
    covered = []
    cov_sales = 0
    for L, W, H, S, c, mid, mk, md, oc in unmatched:
        if L <= tier_L and W <= tier_W and H <= tier_H:
            covered.append(mid)
            cov_sales += S
    
    proposals.append((cov_sales, len(covered), tier_L, tier_W, tier_H, L0, W0, H0, mid0, covered))

proposals.sort(key=lambda x: (-x[0], -x[1]))

seen = set()
for s_cov, n_cov, tL, tW, tH, L0, W0, H0, mid0, covered in proposals[:10]:
    key = f'{tL:.0f}_{tW:.0f}_{tH:.0f}'
    if key in seen: continue
    seen.add(key)
    print(f'\nProposal: tier L<={tL:.0f} W<={tW:.0f} H<={tH:.0f}')
    print(f'  Anchored on: {mid0} (L={L0:.0f} W={W0:.0f} H={H0:.0f})')
    print(f'  Covers {n_cov} vehicles / {s_cov:.0f} sales')