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

# Collect all 两厢车 with height issues
tall_items = []
for row in rows:
    if len(row) < 26: continue
    if row[9] != '两厢车': continue
    try: L = float(row[10]); W = float(row[11]) or 0; H = float(row[12]) or 0; S = float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    code, reason = match(L, W, H, rules_by_cat['两厢车'])
    if not code and H > 1700:
        tall_items.append((L, W, H, S, mid, reason or '?'))

print("两厢车超高未匹配: %d辆 / %.0f销\n" % (len(tall_items), sum(x[3] for x in tall_items)))

# === CLUSTER A: Compact tall MPVs ===
# These should fit in 2L length range (L<=4521) but need more height
print("=" * 65)
print("一、紧凑高顶 MPV（Cluster A）")
print("=" * 65)

cluster_a = [(L, W, H, S, mid, r) for L, W, H, S, mid, r in tall_items 
             if 3700 <= L <= 4550 and 1800 <= H <= 1920]
cluster_a.sort(key=lambda x: -x[3])

print(f"\n共{len(cluster_a)}辆 / {sum(x[3] for x in cluster_a):.0f}销")
print(f"\n--- 按销量前10 ---")
for L, W, H, S, mid, r in cluster_a[:15]:
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid:50s} [{r}]")

# Dimension extremes in cluster A
Ls = [x[0] for x in cluster_a]
Ws = [x[1] for x in cluster_a]
Hs = [x[2] for x in cluster_a]
print(f"\n--- 维度极值 ---")
print(f"  L: {min(Ls):.0f}-{max(Ls):.0f}")
print(f"  W: {min(Ws):.0f}-{max(Ws):.0f}")  
print(f"  H: {min(Hs):.0f}-{max(Hs):.0f}")

# Suggested L/W/H for 2L-H
print(f"\n--- 建议尺码 ---")
suggest_L = max(Ls) + 20  # add small margin
suggest_W = max(Ws) + 20
suggest_H = (max(Hs) + 20) - 280  # need effH >= max(Hs)+margin
print(f"  最小覆盖方案: L={suggest_L:.0f} W={suggest_W:.0f} H={suggest_H:.0f} (effH={suggest_H+280:.0f})")

# Test this tier
test_rule = {'cat':'两厢车','code':'2L-H','L':float(suggest_L),'W':float(suggest_W),'H':float(suggest_H)}
covered = 0; covered_s = 0
for L, W, H, S, mid, r in cluster_a:
    code, _ = match(L, W, H, rules_by_cat['两厢车'] + [test_rule])
    if code == '2L-H': covered += 1; covered_s += S
print(f"  覆盖: {covered}/{len(cluster_a)}辆 / {covered_s:.0f}销")

# === CLUSTER C: Mid-size tall vans ===
print("\n" + "=" * 65)
print("二、中尺寸高顶 Van（Cluster C）")
print("=" * 65)

cluster_c = [(L, W, H, S, mid, r) for L, W, H, S, mid, r in tall_items 
             if 3800 <= L <= 4850 and H >= 1900]
cluster_c.sort(key=lambda x: -x[3])

print(f"\n共{len(cluster_c)}辆 / {sum(x[3] for x in cluster_c):.0f}销")
print(f"\n--- 按销量前15 ---")
for L, W, H, S, mid, r in cluster_c[:15]:
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid:50s} [{r}]")

Ls2 = [x[0] for x in cluster_c]; Ws2 = [x[1] for x in cluster_c]; Hs2 = [x[2] for x in cluster_c]
print(f"\n--- 维度极值 ---")
print(f"  L: {min(Ls2):.0f}-{max(Ls2):.0f}")
print(f"  W: {min(Ws2):.0f}-{max(Ws2):.0f}")
print(f"  H: {min(Hs2):.0f}-{max(Hs2):.0f}")

# Check what the max W includes
wide_ones = [(L, W, H, S, mid, r) for L, W, H, S, mid, r in cluster_c if W >= 1830]
print(f"\n  宽≥1830的: {len(wide_ones)}辆")
for L, W, H, S, mid, r in wide_ones:
    print(f"    L={L:.0f} W={W:.0f} H={H:.0f} S={S:.0f}  {mid}")

# Check Kei van cluster
print("\n" + "=" * 65)
print("三、Kei Van 集群（2S 高度不足）")
print("=" * 65)

kei_vans = [(L, W, H, S, mid, r) for L, W, H, S, mid, r in tall_items
            if 3300 <= L <= 3800 and H >= 1860]
kei_vans.sort(key=lambda x: -x[3])
print(f"\n共{len(kei_vans)}辆 / {sum(x[3] for x in kei_vans):.0f}销")
for L, W, H, S, mid, r in kei_vans[:15]:
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid:50s} [{r}]")

# Can Kei vans go through 2S with a new 2S-H tier?
print(f"\n  2S 当前高=1575 (eff 1855)")
print(f"  Kei van H={max([x[2] for x in kei_vans]) if kei_vans else 0:.0f}")
print(f"  需要 2S-H H=1630 (eff 1910) 覆盖全部 Kei Van")

# Now compute optimal L/W/H for each proposed tier
print("\n" + "=" * 65)
print("四、各新尺码最优 L/W/H 计算")
print("=" * 65)

# For 紧凑高顶: determine optimal using cumulative coverage
print("\n【紧凑高顶 MPV 尺码 - 2L-H】")
print(f"\n锚点车型分析:")
# Sales-weighted extremes
total_s = sum(x[3] for x in cluster_a)
print(f"  销量加权后: 最长 {max(Ls):.0f}mm / 最宽 {max(Ws):.0f}mm / 最高 {max(Hs):.0f}mm")

# Test coverage for different H values at L=4521, W=1829
print(f"\nL=4521 W=1829 不同高度覆盖:")
for test_H in range(1520, 1720, 20):
    test_rule = {'cat':'两厢车','code':'2L-H','L':4521,'W':1829,'H':float(test_H)}
    c = 0; cs = 0
    for L, W, H, S, mid, r in cluster_a:
        code, _ = match(L, W, H, rules_by_cat['两厢车'] + [test_rule])
        if code == '2L-H': c += 1; cs += S
    print(f"  H={test_H}(eff{test_H+280}) -> 覆盖{c:2d}/{len(cluster_a):2d}辆 / {cs:5.0f}销")
    # Also check Kei vans
    kc = 0; kcs = 0
    for L, W, H, S, mid, r in kei_vans:
        code, _ = match(L, W, H, rules_by_cat['两厢车'] + [test_rule])
        if code == '2L-H': kc += 1; kcs += S
    if kc > 0:
        print(f"    其中Kei Van: {kc}辆 / {kcs:.0f}销")

print(f"\n推荐: 2L-H = 4521×1829×(min 1580, 推荐 1600)")

# For 中尺寸高顶
print(f"\n\n【中尺寸高顶 Van 尺码 - 2XL-H】")
print(f"\n锚点车型分析:")
# Careful with the wide ones - only a few wide outliers
non_wide = [(L, W, H, S, mid, r) for L, W, H, S, mid, r in cluster_c if W <= 1830]
wide_count = len(cluster_c) - len(non_wide)
print(f"  排除宽体(W>1830): 排除{wide_count}辆 / 保留{len(non_wide)}辆")

Ls3 = [x[0] for x in non_wide]; Ws3 = [x[1] for x in non_wide]; Hs3 = [x[2] for x in non_wide]
print(f"  维度极值(窄体): L={min(Ls3):.0f}-{max(Ls3):.0f}  W={min(Ws3):.0f}-{max(Ws3):.0f}  H={min(Hs3):.0f}-{max(Hs3):.0f}")

# Test at L=4826
print(f"\nL=4826 W=1829 不同高度覆盖(含窄体+紧凑MPV总计):")
compact_n_mid = cluster_a + non_wide  # merge A + narrow C
compact_n_mid.sort(key=lambda x: -x[3])
print(f"  A+C(窄)车辆: {len(compact_n_mid)}辆 / {sum(x[3] for x in compact_n_mid):.0f}销")

for test_H in range(1600, 1800, 20):
    test_rule = {'cat':'两厢车','code':'2XL-H','L':4826,'W':1829,'H':float(test_H)}
    ca = 0; cas = 0; cc = 0; ccs = 0
    for L, W, H, S, mid, r in compact_n_mid:
        code, _ = match(L, W, H, rules_by_cat['两厢车'] + [test_rule])
        if code == '2XL-H':
            if (L, W, H, S, mid, r) in cluster_a:
                ca += 1; cas += S
            else:
                cc += 1; ccs += S
    total_c = ca + cc; total_s = cas + ccs
    print(f"  H={test_H}(eff{test_H+280}) -> A:{ca:2d}/{len(cluster_a):2d} C窄:{cc:2d}/{len(non_wide):2d} 合计:{total_c:2d}辆 / {total_s:5.0f}销")

print(f"\n推荐: 2XL-H = 4826×1829×1720 (eff 2000)")
print(f"       或 4826×1829×1750 (eff 2030, 更宽松)")