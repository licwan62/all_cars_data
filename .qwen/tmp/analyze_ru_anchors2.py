"""
Find the best anchor vehicles in the RU market:
- Which single vehicle, if we customize a tier to its dimensions + margin,
  would cover the most OTHER vehicles or sales volume?
- Also check: width bottlenecks at YL(1880) and YXL(1981)
"""
import csv

RULE_PATH = r'A0.尺码计算\data\ru\尺寸\0921.0-y380&y410.csv'
FULL_PATH = r'A0.尺码计算\output\全量表_RU.csv'

# --- Read rules ---
rules = []
with open(RULE_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['分类'] == '越野车':
            rules.append({
                'code': row['亚马逊尺码'], 'L': float(row['长_mm']),
                'W': float(row['宽_mm']), 'H': float(row['高_mm']),
            })

# --- Read full table ---
rows = []
with open(FULL_PATH, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        rows.append(row)

def match(L, W, H, rules):
    """Find best fitting rule."""
    best = None
    for r in sorted(rules, key=lambda x: (x['L'], x['W'], x['H'])):
        if L <= r['L'] and W <= r['W'] and H <= r['H']:
            if best is None or (r['L'] < best['L']):
                best = r
    return best

# Gather all 越野车
all_suv = []
for row in rows:
    if len(row) < 26 or row[9] != '越野车': continue
    try:
        L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    all_suv.append((L, W, H, S, row[28], row[0], row[1]))

# Find unmatched
unmatched = [(L, W, H, S, mid, mk, md) for L, W, H, S, mid, mk, md in all_suv 
             if not match(L, W, H, rules)]
matched = [(L, W, H, S, mid, mk, md) for L, W, H, S, mid, mk, md in all_suv 
           if match(L, W, H, rules)]

print(f"Total SUV: {len(all_suv)}")
print(f"Matched: {len(matched)}")
print(f"Unmatched: {len(unmatched)}")
print(f"Unmatched sales: {sum(x[3] for x in unmatched):.0f}")

# --- TOP ANCHORS BY SALES COVERAGE ---
# For each unmatched vehicle, propose a tier at +margin and count coverage
print("\n=== TOP 15 ANCHORS (by sales covered, margin L+200/W+100/H+150) ===")
anchors = []
for L, W, H, S, mid, mk, md in unmatched:
    tL, tW, tH = L + 200, W + 100, H + 150
    cov = [(L2, W2, H2, S2, mid2) for L2, W2, H2, S2, mid2, _, _ in unmatched
           if L2 <= tL and W2 <= tW and H2 <= tH]
    cov_sales = sum(x[3] for x in cov)
    cov_count = len(cov)
    anchors.append((cov_sales, cov_count, tL, tW, tH, L, W, H, S, mid))

anchors.sort(key=lambda x: (-x[0], -x[1]))

seen = set()
rank = 0
for s, n, tL, tW, tH, L, W, H, S, mid in anchors:
    key = f"{tL:.0f}_{tW:.0f}_{tH:.0f}"
    if key in seen: continue
    seen.add(key)
    rank += 1
    print(f"\n#{rank} Anchor: {mid}")
    print(f"   Vehicle: L={L:.0f} W={W:.0f} H={H:.0f} sales={S:.0f}")
    print(f"   Tier:    L<={tL:.0f} W<={tW:.0f} H<={tH:.0f}")
    print(f"   Covers {n} vehicles / {s:.0f} sales")
    if rank >= 15: break

# --- WIDTH BOTTLENECK ANALYSIS ---
print("\n\n=== WIDTH BOTTLENECK ANALYSIS ===")
print("Vehicles failing ONLY on width (other dims fit a tier):")

# Group by closest rule
by_closest = {}
for L, W, H, S, mid, mk, md in unmatched:
    closest = None
    best_dist = float('inf')
    for r in rules:
        if L > r['L']: continue  # length exceeds, skip this rule
        if H > r['H']: continue  # height exceeds
        w_gap = W - r['W']
        if w_gap < 0: continue  # width fits
        r_gap = min(r['L'] - L, r['H'] - H)
        if w_gap < best_dist:
            best_dist = w_gap
            closest = (r['code'], w_gap, r['W'], r['L'], r['H'])
    if closest:
        key = closest[0]
        if key not in by_closest: by_closest[key] = []
        by_closest[key].append((L, W, H, S, mid, closest[1]))

for key in ['YM', 'YL', 'YXL']:
    items = by_closest.get(key, [])
    items.sort(key=lambda x: -x[3])
    total_s = sum(x[3] for x in items)
    print(f"\n--- Only-width-fail at {key} (W={rules[[r['code'] for r in rules].index(key)]['W']:.0f}) ---")
    print(f"  {len(items)} vehicles / {total_s:.0f} sales")
    for L, W, H, S, mid, w_gap in items[:10]:
        print(f"   {mid:55s} W={W:.0f}(+{w_gap:.0f}) H={H:.0f} sales={S:.0f}")
    if len(items) > 10:
        print(f"   ... and {len(items)-10} more")

# --- What if we raise YXL width from 1981 to 2020? ---
print("\n\n=== WHAT-IF: YXL W=1981 -> 2020 ===")
yxl = [r for r in rules if r['code'] == 'YXL'][0]
count_fits = 0
sales_fits = 0
for L, W, H, S, mid, mk, md in unmatched:
    if L <= yxl['L'] and W <= 2020 and H <= yxl['H']:
        count_fits += 1; sales_fits += S
print(f"Would cover {count_fits} more vehicles / {sales_fits:.0f} more sales at YXL W=2020")

# What if we raise YL width from 1880 to 2020 and height to 2000?
print("\n=== WHAT-IF: YL W=1880->2020, H=1778->2050 ===")
yl = [r for r in rules if r['code'] == 'YL'][0]
count_fits2 = 0; sales_fits2 = 0
for L, W, H, S, mid, mk, md in unmatched:
    if L <= yl['L'] and W <= 2020 and H <= 2050:
        count_fits2 += 1; sales_fits2 += S
print(f"Would cover {count_fits2} more vehicles / {sales_fits2:.0f} more sales at YL W=2020 H=2050")


# --- Specific anchor analysis by market segment ---
print("\n\n=== SPECIFIC SEGMENT ANCHORS ===")

# Segment 1: Classic tall SUVs (already covered by YS-410)
seg1 = [(L, W, H, S, mid) for L, W, H, S, mid, _, _ in unmatched 
        if 3800 <= L <= 4500 and H >= 1900]
print(f"\nSegment 1 - Classic tall SUVs L3800-4500 H>=1900: {len(seg1)} vehicles")
for L, W, H, S, mid in sorted(seg1, key=lambda x: x[3], reverse=True)[:5]:
    print(f"   {mid:55s} L={L:.0f} W={W:.0f} H={H:.0f} sales={S:.0f}")

# Segment 2: Modern wide SUVs (width bottleneck at YXL 1981)
seg2 = [(L, W, H, S, mid) for L, W, H, S, mid, _, _ in unmatched 
        if 4900 <= L <= 5100 and W >= 1980 and W <= 2020 and H <= 1800]
print(f"\nSegment 2 - Modern wide SUVs L4900-5100 W1980-2020: {len(seg2)} vehicles, sales={sum(x[3] for x in seg2):.0f}")
for L, W, H, S, mid in sorted(seg2, key=lambda x: x[3], reverse=True)[:10]:
    print(f"   {mid:55s} L={L:.0f} W={W:.0f} H={H:.0f} sales={S:.0f}")

# Segment 3: Full-size SUVs with height issues
seg3 = [(L, W, H, S, mid) for L, W, H, S, mid, _, _ in unmatched 
        if 5000 <= L <= 5400 and H >= 1850]
print(f"\nSegment 3 - Full-size SUVs L5000-5400 H>1850: {len(seg3)} vehicles, sales={sum(x[3] for x in seg3):.0f}")
for L, W, H, S, mid in sorted(seg3, key=lambda x: x[3], reverse=True)[:10]:
    print(f"   {mid:55s} L={L:.0f} W={W:.0f} H={H:.0f} sales={S:.0f}")

# Segment 4: Large premium SUVs (Escalade, Navigator, etc.)
seg4 = [(L, W, H, S, mid) for L, W, H, S, mid, _, _ in unmatched 
        if 5300 <= L <= 5900 and W >= 2000 and H >= 1900]
print(f"\nSegment 4 - Large premium SUVs L5300-5900 W>=2000 H>=1900: {len(seg4)} vehicles, sales={sum(x[3] for x in seg4):.0f}")
for L, W, H, S, mid in sorted(seg4, key=lambda x: x[3], reverse=True)[:10]:
    print(f"   {mid:55s} L={L:.0f} W={W:.0f} H={H:.0f} sales={S:.0f}")