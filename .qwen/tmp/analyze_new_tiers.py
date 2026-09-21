import csv
from collections import defaultdict

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
            return r['code'], None
    closest = min(rules, key=lambda r: max(0,L-(r['L']+tL), W-(r['W']+tW), H-(r['H']+tH), r['L']-L-tRem))
    dL = max(0, L-(closest['L']+tL)); dW = max(0, W-(closest['W']+tW))
    dH = max(0, H-(closest['H']+tH)); dRem = max(0, closest['L']-L-tRem)
    reasons = []
    if dRem > 0: reasons.append(f'\u8d85\u4f59\u91cf{dRem:.0f}')
    if dL > 0: reasons.append(f'\u8d85\u957f{dL:.0f}')
    if dW > 0: reasons.append(f'\u8d85\u5bbd{dW:.0f}')
    if dH > 0: reasons.append(f'\u8d85\u9ad8{dH:.0f}')
    return None, '|'.join(reasons) if reasons else '?'

# Current status
by_cat_matched = defaultdict(int)
by_cat_unmatched = defaultdict(list)
for row in rows:
    if len(row) < 26: continue
    cat = row[9]
    try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    if cat not in rules_by_cat: continue
    code, reason = match(L, W, H, rules_by_cat[cat])
    if code: by_cat_matched[cat] += 1
    else: by_cat_unmatched[cat].append((L, W, H, S, mid, reason))

print("=== \u5f53\u524d\u89c4\u5219\u4e0b\u5404\u5206\u7c7b\u72b6\u6001 ===")
for cat in ['\u4e24\u53a2\u8f66', '\u8dd1\u8f66', '\u4e09\u53a2\u8f66', '\u8d8a\u91ce\u8f66', '\u76ae\u5361']:
    m = by_cat_matched.get(cat, 0)
    u_list = by_cat_unmatched.get(cat, [])
    u, us = len(u_list), sum(x[3] for x in u_list)
    print(f"  {cat}: {m+u}\u603b -> {m}\u5339\u914d / {u}\u672a\u5339\u914d ({us:.0f}\u9500\u91cf)")

items = by_cat_unmatched.get('\u4e24\u53a2\u8f66', [])
print(f"\n\u4e24\u53a2\u8f66\u672a\u5339\u914d: {len(items)}\u8f86 / {sum(x[3] for x in items):.0f}\u9500\u91cf")

# Classify by height bucket and failure mode
print(f"\n{'='*70}")
print("\u9ad8MPV\u96c6\u7fa4\u5206\u6790\uff08\u6309\u9ad8\u5ea6\u533a\u95f4\uff09")
print(f"{'='*70}")

h_clusters = defaultdict(list)
for L, W, H, S, mid, reason in items:
    if '\u8d85\u9ad8' in reason or '\u8d85\u957f' in reason or '\u8d85\u5bbd' in reason:
        # Determine height bucket
        if H <= 1900: key = f'A_H{int(H//50)*50}-{int(H//50)*50+49}'
        else: key = f'B_H{int(H//50)*50}-{int(H//50)*50+49}'
    else:
        key = 'C_\u5176\u4ed6'
    h_clusters[key].append((L, W, H, S, mid, reason))

for key in sorted(h_clusters.keys()):
    g = h_clusters[key]; g.sort(key=lambda x: -x[3])
    gs = sum(x[3] for x in g)
    Ls = [x[0] for x in g]; Ws = [x[1] for x in g]; Hs = [x[2] for x in g]
    print(f"\n{key}: {len(g)}\u8f86, {gs:.0f}\u9500\u91cf")
    print(f"  L={min(Ls):.0f}-{max(Ls):.0f}  W={min(Ws):.0f}-{max(Ws):.0f}  H={min(Hs):.0f}-{max(Hs):.0f}")
    for L, W, H, S, mid, reason in g[:8]:
        print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid:50s} [{reason}]")
    if len(g) > 8: print(f"  ... \u8fd8\u6709{len(g)-8}\u8f86")

# Now propose new tiers
print(f"\n{'='*70}")
print("\u65b0\u589e\u5c3a\u7801\u65b9\u6848\u63a8\u8350")
print(f"{'='*70}")

# Test different new-tiers and their coverage
def simulate_new_rules(new_rules):
    """Add new rules temporarily and count unmatched"""
    rules_test = defaultdict(list, {k: list(v) for k, v in rules_by_cat.items()})
    for r in new_rules:
        rules_test[r['cat']].append(r)
    
    total = 0; total_s = 0
    for row in rows:
        if len(row) < 26: continue
        cat = row[9]
        try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
        except: continue
        if cat not in rules_test: continue
        code, reason = match(L, W, H, rules_test[cat])
        if not code: total += 1; total_s += S
    return total, total_s

# Proposals for tall MPV tiers
proposals = [
    # (name, new tiers list)
    ("\u65b0 2L-H: L=4521 W=1829 H=1580 (effH=1860, \u8986\u76d6 Berlingo+\u90e8\u5206 Kei Van)",
     [{'cat':'\u4e24\u53a2\u8f66','code':'2L-H','L':4521,'W':1829,'H':1580}]),
    ("\u65b0 2L-H: L=4521 W=1829 H=1620 (effH=1900, \u8986\u76d6 Berlingo+\u5168\u90e8Kei Van)",
     [{'cat':'\u4e24\u53a2\u8f66','code':'2L-H','L':4521,'W':1829,'H':1620}]),
    ("\u65b0 2XL-H: L=4826 W=1829 H=1700 (effH=1980, \u8986\u76d6\u65e5\u7cfb\u9ad8\u9876 Van)",
     [{'cat':'\u4e24\u53a2\u8f66','code':'2XL-H','L':4826,'W':1829,'H':1700}]),
    ("\u65b0 2XL-H: L=4826 W=1829 H=1750 (effH=2030, \u8986\u76d6\u65e5\u7cfb+Transporter)",
     [{'cat':'\u4e24\u53a2\u8f66','code':'2XL-H','L':4826,'W':1829,'H':1750}]),
    ("2L-H(1620) + 2XL-H(1700) \u53cc\u5c3a\u7801",
     [{'cat':'\u4e24\u53a2\u8f66','code':'2L-H','L':4521,'W':1829,'H':1620},
      {'cat':'\u4e24\u53a2\u8f66','code':'2XL-H','L':4826,'W':1829,'H':1700}]),
    ("2L-H(1620) + 2XL-H(1750) \u53cc\u5c3a\u7801",
     [{'cat':'\u4e24\u53a2\u8f66','code':'2L-H','L':4521,'W':1829,'H':1620},
      {'cat':'\u4e24\u53a2\u8f66','code':'2XL-H','L':4826,'W':1829,'H':1750}]),
]

baseline_u, baseline_us = simulate_new_rules([])
print(f"\n\u5f53\u524d\u672a\u5339\u914d: {baseline_u}\u8f86 / {baseline_us:.0f}\u9500\u91cf")

for name, new_tiers in proposals:
    u, us = simulate_new_rules(new_tiers)
    covered = baseline_u - u
    covered_s = baseline_us - us
    print(f"\n{name}")
    print(f"  \u51cf\u5c11\u672a\u5339\u914d: {covered}\u8f86 / {covered_s:.0f}\u9500\u91cf")
    print(f"  \u5269\u4f59\u672a\u5339\u914d: {u}\u8f86 / {us:.0f}\u9500\u91cf")

# Deep dive: what's the optimal single new tier for tall MPVs?
print(f"\n{'='*70}")
print("\u5355\u4e00\u65b0\u5c3a\u7801\u6700\u4f18\u89e3\u641c\u7d22")
print(f"{'='*70}")

# Best single-tier proposals scanning L and H
best = []
for test_L in [4521, 4826, 5000]:
    for test_H in range(1550, 1800, 10):
        effH = test_H + 280
        test_rule = {'cat':'两厢车','code':f'NEW-{test_L:.0f}','L':float(test_L),'W':1990,'H':float(test_H)}
        u, us = simulate_new_rules([test_rule])
        covered = baseline_u - u
        covered_s = baseline_us - us
        best.append((covered_s, covered, test_L, test_H, effH))
        # Find the vehicle that's tallest in the cluster being covered

best.sort(key=lambda x: -x[0])
print("\nL\u548cH\u624b\u52a8\u626b\u63cf\u7ed3\u679c\uff08\u6309\u8986\u76d6\u9500\u91cf\u6392\u5e8f\uff09:")
for s, n, L, H, effH in best[:20]:
    print(f"  L={L:5.0f} W=1990 H={H:4.0f}(eff{effH:4.0f}) -> \u8986\u76d6{n:3d}\u8f86 / {s:5.0f}\u9500\u91cf")