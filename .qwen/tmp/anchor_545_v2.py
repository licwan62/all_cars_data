"""
Find vehicles that NEED 2XXL-545 but don't fit in 2XXL-525.
2XXL-545: 5450×2260×2380  vs  2XXL-525: 5250×2170×2060
"""
import csv

rows = []
with open('A0.尺码计算/output/全量表_RU.csv', 'r', encoding='utf-8') as f:
    next(f)
    for row in csv.reader(f): rows.append(row)

# 2XXL-525 limits
XL525 = {'L':5250, 'W':2170, 'H':2060}
# 2XXL-545 limits
XL545 = {'L':5450, 'W':2260, 'H':2380}

print("=== 超出 2XXL-525 但可落入 2XXL-545 的两厢车 ===")
print()

candidates = []
for row in rows:
    if len(row) < 26: continue
    if row[9] != '两厢车': continue
    try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    
    in_525 = L <= XL525['L'] and W <= XL525['W'] and H <= XL525['H']
    in_545 = L <= XL545['L'] and W <= XL545['W'] and H <= XL545['H']
    
    if not in_525 and in_545:
        candidates.append((L, W, H, S, mid))

candidates.sort(key=lambda x: -x[3])
total_s = sum(x[3] for x in candidates)
print(f"共{len(candidates)}辆 / {total_s:.0f}销\n")

for L, W, H, S, mid in candidates:
    # Show which dimension(s) exceed 525
    reasons = []
    if L > XL525['L']: reasons.append(f"L超{XL525['L']:.0f}(+{L-XL525['L']:.0f})")
    if W > XL525['W']: reasons.append(f"W超{XL525['W']:.0f}(+{W-XL525['W']:.0f})")
    if H > XL525['H']: reasons.append(f"H超{XL525['H']:.0f}(+{H-XL525['H']:.0f})")
    reason_str = ' / '.join(reasons)
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  [{reason_str:40s}]  {mid}")

# Also: vehicles that are NEAR 2XXL-525's limits and would benefit
print()
print("=== 边缘车辆: 离 2XXL-525 任一维度≤30mm 的标志性长MPV ===")
borderline = []
for row in rows:
    if len(row) < 26: continue
    if row[9] != '两厢车': continue
    try: L, W, H, S = float(row[10]), float(row[11]) or 0, float(row[12]) or 0, float(row[13]) or 0
    except: continue
    mid = row[28] if len(row) > 28 else f"{row[0]} {row[1]}"
    
    in_525 = L <= XL525['L'] and W <= XL525['W'] and H <= XL525['H']
    in_545 = L <= XL545['L'] and W <= XL545['W'] and H <= XL545['H']
    
    if in_525 and in_545 and L >= 5000 and S > 10:
        borderline.append((L, W, H, S, mid))

borderline.sort(key=lambda x: -x[3])
for L, W, H, S, mid in borderline[:15]:
    remaining_L = XL545['L'] - L
    remaining_W = XL545['W'] - W
    remaining_H = XL545['H'] - H
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  余量:(L{remaining_L:.0f} W{remaining_W:.0f} H{remaining_H:.0f})  {mid}")