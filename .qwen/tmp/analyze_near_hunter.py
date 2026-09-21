import csv

rows = []
with open('A0.尺码计算\\output\\全量表_RU.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        rows.append(row)

# 0:MAKE 1:MODEL 9:分类 10:L-MM 11:W-MM 12:H-MM 13:销量合计
# 20:自动尺码 24:候选 25:原因

# Group A: 越野车, 无可用尺码, L 3800-4400, H > 1700
print('=== Group A: SUV no-size L3800-4400 H>1700 ===')
group_a = []
for row in rows:
    if len(row) < 26: continue
    cat = row[9]
    auto_size = row[20]
    if cat != '越野车' or auto_size != '无可用尺码': continue
    try:
        L = float(row[10]); W = float(row[11]) if row[11] else 0
        H = float(row[12]) if row[12] else 0; S = float(row[13]) if row[13] else 0
    except: continue
    if 3800 <= L <= 4400 and H > 1700:
        candidate = row[24] if len(row) > 24 else ''
        reason = row[25] if len(row) > 25 else ''
        group_a.append((L, W, H, S, row[28], row[0], row[1], candidate, reason))
group_a.sort(key=lambda x: x[0])
ts = 0
for L,W,H,S,mid,b,m,cand,reason in group_a:
    ts += S
    print(f'{mid:55s} L={L:5.0f} W={W:5.0f} H={H:5.0f} cand={cand:6s} reason={reason:6s} sales={S:5.0f}')
print(f'Count: {len(group_a)}  Total sales: {ts:.0f}')

# Group B: 越野车 matched to YM (候选=YM) with height issues
print('\n=== Group B: SUV candidate=YM with height/reason issues ===')
group_b = []
for row in rows:
    if len(row) < 26: continue
    cat = row[9]; candidate = row[24] if len(row) > 24 else ''; reason = row[25] if len(row) > 25 else ''
    if cat != '越野车' or candidate != 'YM': continue
    try:
        L = float(row[10]); W = float(row[11]) if row[11] else 0
        H = float(row[12]) if row[12] else 0; S = float(row[13]) if row[13] else 0
    except: continue
    if '超高' in reason or '超余量' in reason or '超长' in reason or '超宽' in reason:
        group_b.append((L, W, H, S, row[28], row[0], row[1], candidate, reason))
group_b.sort(key=lambda x: x[0])
ts = 0
for L,W,H,S,mid,b,m,cand,reason in group_b:
    ts += S
    print(f'{mid:55s} L={L:5.0f} W={W:5.0f} H={H:5.0f} reason={reason:6s} sales={S:5.0f}')
print(f'Count: {len(group_b)} Total sales: {ts:.0f}')

# Group C: 越野车 matched to YS with height issues
print('\n=== Group C: SUV candidate=YS with height issues ===')
group_c = []
for row in rows:
    if len(row) < 26: continue
    cat = row[9]; candidate = row[24] if len(row) > 24 else ''; reason = row[25] if len(row) > 25 else ''
    if cat != '越野车' or candidate != 'YS': continue
    try:
        L = float(row[10]); W = float(row[11]) if row[11] else 0
        H = float(row[12]) if row[12] else 0; S = float(row[13]) if row[13] else 0
    except: continue
    if '超高' in reason or '超余量' in reason:
        group_c.append((L, W, H, S, row[28], row[0], row[1], candidate, reason))
group_c.sort(key=lambda x: x[0])
ts = 0
for L,W,H,S,mid,b,m,cand,reason in group_c:
    ts += S
    print(f'{mid:55s} L={L:5.0f} W={W:5.0f} H={H:5.0f} reason={reason:6s} sales={S:5.0f}')
print(f'Count: {len(group_c)} Total sales: {ts:.0f}')

# Group D: All 越野车 where candidate=YM or YS, sorted by H desc
print('\n=== Group D: SUV candidate=YM (all, sorted by H desc) ===')
group_d = []
for row in rows:
    if len(row) < 26: continue
    cat = row[9]; candidate = row[24] if len(row) > 24 else ''
    if cat != '越野车' or candidate != 'YM': continue
    try:
        L = float(row[10]); W = float(row[11]) if row[11] else 0
        H = float(row[12]) if row[12] else 0; S = float(row[13]) if row[13] else 0
        reason = row[25] if len(row) > 25 else ''
    except: continue
    group_d.append((H, L, W, S, row[28], row[0], row[1], reason))
group_d.sort(key=lambda x: -x[0])
ts = 0
for H,L,W,S,mid,b,m,reason in group_d:
    ts += S
    print(f'{mid:55s} L={L:5.0f} W={W:5.0f} H={H:5.0f} reason={reason:6s} sales={S:5.0f}')
print(f'Count: {len(group_d)} Total sales: {ts:.0f}')

# Group E: All 无可用尺码 越野车 sorted by L (to see the cluster)
print('\n=== Group E: SUV no-size (all, sorted by L) ===')
group_e = []
for row in rows:
    if len(row) < 26: continue
    cat = row[9]; auto_size = row[20]
    if cat != '越野车' or auto_size != '无可用尺码': continue
    try:
        L = float(row[10]); W = float(row[11]) if row[11] else 0
        H = float(row[12]) if row[12] else 0; S = float(row[13]) if row[13] else 0
    except: continue
    candidate = row[24] if len(row) > 24 else ''
    reason = row[25] if len(row) > 25 else ''
    group_e.append((L, W, H, S, row[28], row[0], row[1], candidate, reason))
group_e.sort(key=lambda x: x[0])
ts = 0
for L,W,H,S,mid,b,m,cand,reason in group_e:
    ts += S
    print(f'{mid:55s} L={L:5.0f} W={W:5.0f} H={H:5.0f} cand={cand:6s} reason={reason:6s} sales={S:5.0f}')
print(f'Count: {len(group_e)} Total sales: {ts:.0f}')