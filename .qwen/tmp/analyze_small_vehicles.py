"""
Analyze small vehicle coverage gaps across ALL categories.
With tolerance params: 宽=270, 高=280, 余量长=635
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
    for row in csv.DictReader(f):
        params[row['参数']] = float(row['值'])
tL, tW, tH, tRem = params['长容差'], params['宽容差'], params['高容差'], params['余量长容差']

# --- Read rules ---
rules_by_cat = {}
with open(RULE_PATH, 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        cat = row['分类']
        if cat not in rules_by_cat:
            rules_by_cat[cat] = []
        rules_by_cat[cat].append({
            'code': row['亚马逊尺码'], 'ozon': row['OZON尺码'], 'ship': row['发货尺码'],
            'L': float(row['长_mm']), 'W': float(row['宽_mm']), 'H': float(row['高_mm']),
        })

def match_result(L, W, H, rules):
    """Return (matched_code|None, reason, max_diff, closest_rule)"""
    # Try exact match with tolerances
    for r in sorted(rules, key=lambda x: (x['L'], x['W'], x['H'])):
        if (r['L'] + tL >= L) and (r['W'] + tW >= W) and (r['H'] + tH >= H) and (r['L'] - L <= tRem):
            return r['code'], None, None, None
    # No match - find closest
    closest = None; min_diff = float('inf'); reason = None
    for r in rules:
        dL = max(0, L - (r['L'] + tL))
        dW = max(0, W - (r['W'] + tW))
        dH = max(0, H - (r['H'] + tH))
        dRem = max(0, r['L'] - L - tRem)
        max_d = max(dL, dW, dH, dRem)
        if max_d < min_diff:
            min_diff = max_d; closest = r
            if dRem == max_d and dRem > 0: reason = '超余量'
            elif dL == max_d and dL > 0: reason = '超长'
            elif dW == max_d and dW > 0: reason = '超宽'
            elif dH == max_d and dH > 0: reason = '超高'
            else: reason = '其他'
    return None, reason, min_diff, closest

# --- Read full table ---
rows = []
with open(FULL_PATH, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader: rows.append(row)

# Gather unmatched by category and reason
by_cat = defaultdict(list)
all_small = []

for row in rows:
    if len(row) < 26: continue
    cat = row[9]
    try:
        L = float(row[10]); W = float(row[11]) or 0; H = float(row[12]) or 0
        S = float(row[13]) if row[13] else 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    
    if cat not in rules_by_cat:
        continue
    
    code, reason, diff, closest = match_result(L, W, H, rules_by_cat[cat])
    if code is None:
        by_cat[cat].append((L, W, H, S, mid, reason, diff, closest))
        if reason == '超余量' or (closest and L < closest['L'] * 0.85):
            all_small.append((cat, L, W, H, S, mid, reason, diff, closest))

# --- ANALYSIS ---
print("=" * 70)
print("小尺寸车型覆盖分析（含容差 长=0 宽=270 高=280 余量长=635）")
print("=" * 70)

# Show smallest tier in each category
print("\n各分类最小尺码：")
for cat, rs in sorted(rules_by_cat.items()):
    smallest = min(rs, key=lambda r: r['L'])
    largest = max(rs, key=lambda r: r['L'])
    print(f"  {cat}: 最小={smallest['code']}(L≤{smallest['L']:.0f}) → 最大={largest['code']}(L≤{largest['L']:.0f})")

# Focus on 小尺寸 (超余量 failure)
print("\n" + "=" * 70)
print('一、因超余量（车型太小/太长余量）未匹配的车辆')
print("=" * 70)

small_by_cat = defaultdict(list)
for cat, L, W, H, S, mid, reason, diff, closest in all_small:
    if reason == '超余量':
        small_by_cat[cat].append((L, W, H, S, mid, diff, closest))

for cat in ['两厢车', '跑车', '三厢车', '越野车', '皮卡']:
    items = small_by_cat.get(cat, [])
    if not items: continue
    items.sort(key=lambda x: x[0])  # sort by length asc
    total_s = sum(x[3] for x in items)
    print(f"\n📋 {cat} — {len(items)}辆 超余量, 总销量{total_s:.0f}")
    print(f"   {'尺寸(L×W×H)':>20s}  {'超余量':>8s}  {'销量':>5s}  {'车型名'}")
    print(f"   {'-'*60}")
    for L, W, H, S, mid, diff, closest in items:
        code = closest['code'] if closest else '?'
        print(f"   L{L:5.0f}×W{W:4.0f}×H{H:4.0f}  {diff:6.0f}mm  {S:5.0f}  {mid}  ←最小档{code}")

# Focus on small vehicles that fail for OTHER reasons (too tall for their small tier)
print("\n" + "=" * 70)
print('二、小尺寸但因其他原因（超高/超宽）未匹配')
print("=" * 70)

other_small_by_cat = defaultdict(list)
for cat, L, W, H, S, mid, reason, diff, closest in all_small:
    if reason != '超余量' and L < 4000:  # physically small vehicles
        other_small_by_cat[cat].append((L, W, H, S, mid, reason, diff, closest))

for cat in ['两厢车', '跑车', '三厢车', '越野车', '皮卡']:
    items = other_small_by_cat.get(cat, [])
    if not items: continue
    items.sort(key=lambda x: -x[3])
    total_s = sum(x[3] for x in items)
    print(f"\n📋 {cat} — {len(items)}辆 小型车因他因未匹配, 总销量{total_s:.0f}")
    for L, W, H, S, mid, reason, diff, closest in items[:15]:
        code = closest['code'] if closest else '?'
        print(f"   L{L:5.0f}×W{W:4.0f}×H{H:4.0f}  {reason}{diff:.0f}  {S:5.0f}  {mid}  →{code}")
    if len(items) > 15:
        print(f"   ... 还有{len(items)-15}辆")

# --- Anchor analysis for small vehicle cluster ---
print("\n" + "=" * 70)
print('三、小型车锚点分析：以哪个车为基准能覆盖最多小车型？')
print("=" * 70)

# Collect all small vehicles (L < 3800)
all_small_vehicles = []
for cat, L, W, H, S, mid, reason, diff, closest in all_small:
    if L < 3800:
        all_small_vehicles.append((cat, L, W, H, S, mid, reason, diff, closest))

print(f"\n共{len(all_small_vehicles)}辆小型车（L<3800mm） 总销量{sum(x[4] for x in all_small_vehicles):.0f}")

# By sales, what are the top small vehicles?
print("\n按销量排序的小型未匹配车：")
for cat, L, W, H, S, mid, reason, diff, closest in sorted(all_small_vehicles, key=lambda x: -x[4])[:20]:
    code = closest['code'] if closest else '?'
    print(f"   [{cat}] L{L:5.0f}×W{W:4.0f}×H{H:4.0f}  {reason}{diff:.0f}  {S:5.0f}  {mid}  →{code}")

# What dimensions would cover the most small vehicles?
print("\n\n最优小型车覆盖方案（新档位分析）：")
# Try different S-size proposals
proposals = []
for test_L in range(2500, 4200, 100):
    for test_W in range(1300, 1900, 50):
        for test_H in range(1400, 2200, 100):
            cov = [(cat, L, W, H, S, mid) for cat, L, W, H, S, mid, reason, diff, closest in all_small_vehicles
                   if L <= test_L and W <= test_W and H <= test_H]
            if len(cov) >= 5:
                cov_s = sum(x[4] for x in cov)
                proposals.append((len(cov), cov_s, test_L, test_W, test_H, cov))

# Sort and show distinct proposals
seen = set()
for n, s, L, W, H, cov in sorted(proposals, key=lambda x: -x[1])[:15]:
    key = f"{L}_{W}_{H}"
    if key in seen: continue
    seen.add(key)
    # Show top 5 vehicles in this cluster
    top5 = sorted(cov, key=lambda x: -x[4])[:5]
    print(f"\n  新小尺寸 L≤{L} W≤{W} H≤{H} → 覆盖{n}辆 / {s:.0f}销量")
    for cat, vL, vW, vH, vS, vmid in top5:
        print(f"     [{cat}] {vmid:55s} L={vL:5.0f} W={vW:4.0f} H={vH:4.0f} sales={vS:5.0f}")