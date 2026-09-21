import csv
from collections import defaultdict

rows = []
with open('A0.尺码计算/output/全量表_RU.csv', 'r', encoding='utf-8') as f:
    next(f)
    for row in csv.reader(f): rows.append(row)

tiers = [
    {'code':'2L-192', 'name':'紧凑高顶', 'H':1920, 'below_H':1780},
    {'code':'2XL-200', 'name':'中高顶',   'H':2000, 'below_H':1880},
    {'code':'2XXL-545','name':'旗舰长MPV','H':2380, 'below_H':2060},
]

for t in tiers:
    # Collect vehicles needing this tier (too tall for below tier, fits W/H limits)
    cand = []
    for row in rows:
        if len(row) < 26 or row[9] != '两厢车': continue
        try:
            L = float(row[10]); W = float(row[11]) or 0
            H = float(row[12]) or 0; S = float(row[13]) or 0
        except: continue
        if H <= t['below_H']: continue
        if W > 2260 or H > t['H']: continue
        mid = row[28] if len(row) > 28 else f'{row[0]} {row[1]}'
        cand.append((S, L, W, H, mid))

    total_v = len(cand)
    total_s = sum(x[0] for x in cand)
    if total_v == 0:
        print(f'\n=== {t["code"]} ({t["name"]}) — 无数据 ===')
        continue

    # Length buckets
    buckets = defaultdict(int)
    sales_b = defaultdict(int)
    for S, L, W, H, mid in cand:
        b = int(round(L / 50) * 50)
        buckets[b] += 1
        sales_b[b] += int(S)

    print(f'\n{"="*70}')
    print(f'{t["code"]} ({t["name"]}, H上限={t["H"]})')
    print(f'下层H上限={t["below_H"]}，需此高度的车共{total_v}辆 / {total_s:.0f}销')
    print(f'{"="*70}')

    # Length distribution
    print(f'\n--- 长度分布（50mm粒度，销量≥30的区间） ---')
    for b in sorted(buckets.keys()):
        s = sales_b[b]
        if s >= 30:
            bar_len = max(1, s // 30)
            bar = '█' * bar_len
            print(f'  L={b:5d}mm:  {buckets[b]:3d}辆  {s:5d}销  {bar}')

    # Cumulative coverage
    by_L = sorted(cand, key=lambda x: x[1])
    print(f'\n--- 累计覆盖率（长上限逐步向右移） ---')
    cum_s = 0
    checkpoints = list(range(3800, 5600, 100))
    idx = 0
    for S, L, W, H, mid in by_L:
        cum_s += S
        while idx < len(checkpoints) and L <= checkpoints[idx]:
            idx += 1
        if idx < len(checkpoints) and (checkpoints[idx] == L or any(abs(L - cp) < 5 for cp in checkpoints)):
            pass
    # Simpler approach: just print every 100mm
    for cl in checkpoints:
        covered = [x for x in by_L if x[1] <= cl]
        cv = len(covered)
        cs = sum(x[0] for x in covered)
        pct = cs / total_s * 100 if total_s > 0 else 0
        bar_len = max(1, int(pct // 5))
        bar = '█' * bar_len
        print(f'  L<={cl:5d}: {cv:4d}/{total_v:4d}辆  {cs:6.0f}/{total_s:.0f}销 ({pct:5.1f}%)  {bar}')

    # Sales concentration points
    print(f'\n--- 销量集中点 ---')
    top5 = sorted(sales_b.items(), key=lambda x: -x[1])[:5]
    for b, s in top5:
        print(f'  L≈{b:5d}mm: {buckets[b]:3d}辆 / {s:5d}销')

    # 80% and 90% points
    cum_s = 0
    p80 = None; p90 = None; p95 = None
    for S, L, W, H, mid in by_L:
        cum_s += S
        pct = cum_s / total_s * 100
        if p80 is None and pct >= 80: p80 = L
        if p90 is None and pct >= 90: p90 = L
        if p95 is None and pct >= 95: p95 = L

    max_L = max(x[1] for x in by_L)
    print(f'\n--- 覆盖节点 ---')
    print(f'  80%车辆长度 ≤ {p80:.0f}mm')
    print(f'  90%车辆长度 ≤ {p90:.0f}mm')
    print(f'  95%车辆长度 ≤ {p95:.0f}mm')
    print(f'  100%车辆长度 ≤ {max_L:.0f}mm')

    # Show boundary vehicles (within 15cm of 80%/90%/95% points)
    print(f'\n--- 不同长上限对应的边界车形 ---')
    for test_L, label in [(p80, f'80%点({p80:.0f})'), (p90, f'90%点({p90:.0f})'), (p95, f'95%点({p95:.0f})'), (max_L, '100%点')]:
        if test_L is None: continue
        bs = [x for x in by_L if abs(x[1] - test_L) <= 80]
        bs.sort(key=lambda x: -x[0])
        print(f'\n  L≤{int(test_L):5d} ({label}) — 边界附近{len(bs)}辆:')
        for S, L, W, H, mid in bs[:6]:
            print(f'    S={S:5.0f}  L={L:5.0f}(余{int(test_L)-int(L):4d}) W={W:4.0f} H={H:4.0f}  {mid}')