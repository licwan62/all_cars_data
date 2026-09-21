"""
Proper analysis with tolerance parameters.
Rules: 0921.0-y380&y410.csv
Params: 0921.0-加容宽.csv
Data:  全量表_RU.csv
"""
import csv
from collections import defaultdict

BASE = r'A0.尺码计算'
RULE_PATH = f'{BASE}\\data\\ru\\尺寸\\0921.0-y380&y410.csv'
PARAM_PATH = f'{BASE}\\data\\ru\\参数\\0921.0-加容宽.csv'
FULL_PATH = f'{BASE}\\output\\全量表_RU.csv'

# --- Read parameters ---
params = {}
with open(PARAM_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        params[row['参数']] = float(row['值'])
tL = params['长容差']
tW = params['宽容差']  # 270mm
tH = params['高容差']  # 280mm
tRem = params['余量长容差']
print(f"Params: 长容差={tL}, 宽容差={tW}, 高容差={tH}, 余量长容差={tRem}")

# --- Read rules ---
rules_by_cat = {}
with open(RULE_PATH, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat = row['分类']
        if cat not in rules_by_cat:
            rules_by_cat[cat] = []
        rules_by_cat[cat].append({
            'code': row['亚马逊尺码'],
            'ozon': row['OZON尺码'],
            'ship': row['发货尺码'],
            'L': float(row['长_mm']),
            'W': float(row['宽_mm']),
            'H': float(row['高_mm']),
        })

print("\n=== Rules by category ===")
for cat, rs in rules_by_cat.items():
    print(f"\n{cat} ({len(rs)} tiers):")
    for r in rs:
        effL = r['L'] + tL
        effW = r['W'] + tW
        effH = r['H'] + tH
        print(f"  {r['code']:10s} L<={r['L']:5.0f}(eff{effL:5.0f}) W<={r['W']:5.0f}(eff{effW:5.0f}) H<={r['H']:5.0f}(eff{effH:5.0f})")

def match_vehicle(L, W, H, rules):
    """Match with tolerance, as in generate_ru_full_table.py"""
    pool = rules
    # Filter by effective limits
    fits = [r for r in pool 
            if (r['L'] + tL >= L)       # length with tolerance
            and (r['W'] + tW >= W)       # width with tolerance
            and (r['H'] + tH >= H)       # height with tolerance
            and (r['L'] - L <= tRem)]    # not too small for tier
    if fits:
        # Return the smallest fitting tier (first by L asc)
        return fits[0], True
    
    # No fit — find closest
    diffs = []
    for r in pool:
        diff_L = max(0, L - (r['L'] + tL))
        diff_W = max(0, W - (r['W'] + tW))
        diff_H = max(0, H - (r['H'] + tH))
        diff_Rem = max(0, r['L'] - L - tRem)
        max_diff = max(diff_L, diff_W, diff_H, diff_Rem)
        reasons = []
        if diff_L > 0: reasons.append(f'超长{diff_L:.0f}')
        if diff_W > 0: reasons.append(f'超宽{diff_W:.0f}')
        if diff_H > 0: reasons.append(f'超高{diff_H:.0f}')
        if diff_Rem > 0: reasons.append(f'超余量{diff_Rem:.0f}')
        diffs.append((max_diff, r, reasons))
    diffs.sort(key=lambda x: (x[0], rules.index(x[1])))
    return diffs[0][1], False, diffs[0][2]

# --- Read full table ---
rows = []
with open(FULL_PATH, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        rows.append(row)

# Analyze ALL categories
by_cat_unmatched = defaultdict(list)
by_cat_matched = defaultdict(list)

for row in rows:
    if len(row) < 26: continue
    cat = row[9]
    try:
        L, W, H = float(row[10]), float(row[11]) or 0, float(row[12]) or 0
        S = float(row[13]) if row[13] else 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    
    if cat not in rules_by_cat:
        by_cat_unmatched[cat].append((L, W, H, S, mid, '无规则'))
        continue
    
    result = match_vehicle(L, W, H, rules_by_cat[cat])
    if result[1]:  # matched
        by_cat_matched[cat].append((L, W, H, S, mid, result[0]['code']))
    else:
        by_cat_unmatched[cat].append((L, W, H, S, mid, '|'.join(result[2])))

print("\n\n=== MATCHING RESULTS (WITH TOLERANCES) ===")
all_cats = sorted(set(list(by_cat_matched.keys()) + list(by_cat_unmatched.keys())))
for cat in all_cats:
    m = len(by_cat_matched.get(cat, []))
    u = len(by_cat_unmatched.get(cat, []))
    u_sales = sum(x[3] for x in by_cat_unmatched.get(cat, []))
    total = m + u
    pct = u / total * 100 if total > 0 else 0
    print(f"\n{cat}: {total} total → {m} matched / {u} unmatched ({pct:.1f}%)")
    if u > 0:
        print(f"   Unmatched sales: {u_sales:.0f}")

# --- DEEP DIVE: Unmatched by category ---
print("\n\n" + "="*80)
print("DETAILED UNMATCHED ANALYSIS")
print("="*80)

for cat in all_cats:
    items = by_cat_unmatched.get(cat, [])
    if not items: continue
    items.sort(key=lambda x: -x[3])
    total_s = sum(x[3] for x in items)
    
    print(f"\n{'='*60}")
    print(f"📋 {cat} — {len(items)} unmatched, {total_s:.0f} sales")
    print(f"{'='*60}")
    
    # Group by failure reason
    reason_groups = defaultdict(list)
    for L, W, H, S, mid, reason in items:
        reason_groups[reason].append((L, W, H, S, mid))
    
    for reason, group in sorted(reason_groups.items(), key=lambda x: -sum(v[3] for v in x[1])):
        g_sales = sum(x[3] for x in group)
        g_Ls = [x[0] for x in group]
        g_Ws = [x[1] for x in group]
        g_Hs = [x[2] for x in group]
        print(f"\n  🔸 [{reason}] {len(group)} vehicles / {g_sales:.0f} sales")
        print(f"     Dims range: L={min(g_Ls):.0f}-{max(g_Ls):.0f} W={min(g_Ws):.0f}-{max(g_Ws):.0f} H={min(g_Hs):.0f}-{max(g_Hs):.0f}")
        # Show top vehicles by sales
        for L, W, H, S, mid in group[:8]:
            print(f"     {mid:55s} L={L:5.0f} W={W:5.0f} H={H:5.0f} sales={S:5.0f}")
        if len(group) > 8:
            print(f"     ... and {len(group)-8} more")

# --- ANCHOR ANALYSIS: find the best vehicle to customize for ---
print("\n\n" + "="*80)
print("ANCHOR VEHICLE ANALYSIS (all categories)")
print("="*80)

# Collect all unmatched
all_unmatched = []
for cat in all_cats:
    for item in by_cat_unmatched.get(cat, []):
        all_unmatched.append((cat, *item))

print(f"\nTotal unmatched: {len(all_unmatched)}")
print(f"Total unmatched sales: {sum(x[4] for x in all_unmatched):.0f}")

# For each unmatched vehicle, simulate a new rule at +margin
# and see how many others it covers (same category)
anchors = []
for cat, L, W, H, S, mid, reason in all_unmatched:
    # Propose tier: +100mm L, +70mm W, +80mm H (reasonable margins)
    tL_prop, tW_prop, tH_prop = L + 100, W + 70, H + 80
    
    # Count vehicles that would fit (same category only)
    cov_count = 0
    cov_sales = 0
    cov_vehicles = []
    for cat2, L2, W2, H2, S2, mid2, reason2 in all_unmatched:
        if cat2 != cat: continue
        if L2 <= tL_prop and W2 <= tW_prop and H2 <= tH_prop:
            cov_count += 1
            cov_sales += S2
            cov_vehicles.append(mid2)
    
    anchors.append((cov_sales, cov_count, cat, tL_prop, tW_prop, tH_prop, L, W, H, S, mid, cov_vehicles))

anchors.sort(key=lambda x: (-x[0], -x[1]))

# Show top anchors
seen = set()
rank = 0
for s_cov, n_cov, cat, tL_prop, tW_prop, tH_prop, L, W, H, S, mid, cov_vehicles in anchors[:25]:
    key = f"{cat}_{tL_prop:.0f}_{tW_prop:.0f}_{tH_prop:.0f}"
    if key in seen: continue
    seen.add(key)
    rank += 1
    print(f"\n#{rank} [{cat}] {mid}")
    print(f"   Vehicle: L={L:.0f} W={W:.0f} H={H:.0f} sales={S:.0f}")
    print(f"   New tier: L<={tL_prop:.0f} W<={tW_prop:.0f} H<={tH_prop:.0f}")
    print(f"   Covers {n_cov} vehicles / {s_cov:.0f} sales")
    if rank >= 15: break