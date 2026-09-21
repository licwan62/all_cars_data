import csv
from collections import defaultdict

params = {'长容差':0, '宽容差':270, '高容差':280, '余量长容差':635}

# 新规则 0921.1-微调&高mpv.csv
rules_by_cat = {}
with open('A0.尺码计算/data/ru/尺寸/0921.1-微调&高mpv.csv', 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        cat = row['分类']
        if cat not in rules_by_cat: rules_by_cat[cat] = []
        rules_by_cat[cat].append({
            'code': row['亚马逊尺码'], 'L': float(row['长_mm']),
            'W': float(row['宽_mm']), 'H': float(row['高_mm']),
            'ozon': row['OZON尺码'], 'ship': row['发货尺码'],
        })

print("=== 新规则 两厢车 ===")
for r in rules_by_cat['两厢车']:
    effH = r['H'] + 280
    print(f"  {r['code']:10s} L<={r['L']:5.0f} W<={r['W']:5.0f}(eff{r['W']+270:.0f}) H<={r['H']:5.0f}(eff{effH:.0f})")

rows = []
with open('A0.尺码计算/output/全量表_RU.csv', 'r', encoding='utf-8') as f:
    next(f)
    for row in csv.reader(f): rows.append(row)

tL, tW, tH, tRem = 0, 270, 280, 635

def match(L, W, H, rules):
    for r in sorted(rules, key=lambda x: (x['L'], x['W'], x['H'])):
        if (r['L']+tL>=L) and (r['W']+tW>=W) and (r['H']+tH>=H) and (r['L']-L<=tRem):
            return r['code'], None
    closest = min(rules, key=lambda r: max(0,L-(r['L']+tL), W-(r['W']+tW), H-(r['H']+tH), r['L']-L-tRem))
    dL = max(0, L-(closest['L']+tL))
    dW = max(0, W-(closest['W']+tW))
    dH = max(0, H-(closest['H']+tH))
    dRem = max(0, closest['L']-L-tRem)
    reasons = []
    if dRem > 0: reasons.append(f'\u8d85\u4f59\u91cf{dRem:.0f}')
    if dL > 0: reasons.append(f'\u8d85\u957f{dL:.0f}')
    if dW > 0: reasons.append(f'\u8d85\u5bbd{dW:.0f}')
    if dH > 0: reasons.append(f'\u8d85\u9ad8{dH:.0f}')
    return None, '|'.join(reasons) if reasons else '?'

# 统计所有分类
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
    if code:
        by_cat_matched[cat] += 1
    else:
        by_cat_unmatched[cat].append((L, W, H, S, mid, reason))

print(f"\n{'='*60}")
print(f"\u65b0\u89c4\u5219\u4e0b\u5404\u5206\u7c7b\u5339\u914d\u60c5\u51b5\uff1a")
total_u = 0
total_us = 0
for cat in ['两厢车', '跑车', '三厢车', '越野车', '皮卡']:
    m = by_cat_matched.get(cat, 0)
    u_list = by_cat_unmatched.get(cat, [])
    u = len(u_list)
    us = sum(x[3] for x in u_list)
    t = m + u
    total_u += u
    total_us += us
    print(f"  {cat}: {t} \u603b\u2192 {m}\u5339\u914d / {u}\u672a\u5339\u914d ({us:.0f}\u9500\u91cf)")

print(f"\n\u5171\u8ba1: {total_u}\u8f86\u672a\u5339\u914d, {total_us:.0f}\u9500\u91cf")

# 重点分析两厢车未匹配
print(f"\n{'='*60}")
print(f"\u4e24\u53a2\u8f66\u672a\u5339\u914d\u8be6\u60c5\uff1a")
items_2 = by_cat_unmatched.get('两厢车', [])
items_2.sort(key=lambda x: -x[3])
total_s = sum(x[3] for x in items_2)
print(f"\u5171{len(items_2)}\u8f86, {total_s:.0f}\u9500\u91cf")

# 按原因分组
reason_groups = defaultdict(list)
for L, W, H, S, mid, reason in items_2:
    # 提取主要失败原因
    if '\u8d85\u957f' in reason: main_r = '\u8d85\u957f'
    elif '\u8d85\u9ad8' in reason: main_r = '\u8d85\u9ad8'
    elif '\u8d85\u5bbd' in reason: main_r = '\u8d85\u5bbd'
    elif '\u8d85\u4f59\u91cf' in reason: main_r = '\u8d85\u4f59\u91cf'
    else: main_r = reason
    reason_groups[main_r].append((L, W, H, S, mid, reason))

for reason in ['\u8d85\u957f', '\u8d85\u9ad8', '\u8d85\u5bbd', '\u8d85\u4f59\u91cf']:
    g = reason_groups.get(reason, [])
    if not g: continue
    g.sort(key=lambda x: -x[3])
    gs = sum(x[3] for x in g)
    print(f"\n  [{reason}] {len(g)}\u8f86, {gs:.0f}\u9500\u91cf")
    for L, W, H, S, mid, full_reason in g[:15]:
        print(f"    L={L:5.0f} W={W:4.0f} H={H:4.0f}  S={S:5.0f}  {mid:55s}  [{full_reason}]")
    if len(g) > 15:
        print(f"    ... \u8fd8\u6709{len(g)-15}\u8f86")

# 核心问题：Berlingo 集群是否已被2M覆盖？
print(f"\n{'='*60}")
print("验证 Berlingo/Partner 集群是否已被新 2M (H=1600, effH=1880) 覆盖：")
check_vehicles = [
    ("Peugeot Partner Van 2002-2012", 4145, 1720, 1811, 90),
    ("Citroen Berlingo MPV 2002-2012", 4138, 1725, 1811, 74),
    ("Peugeot Partner MPV 2002-2012", 4145, 1720, 1811, 71),
    ("Citroen Berlingo Van 2002-2012", 4138, 1725, 1811, 63),
    ("Peugeot Partner Van 2008-2012", 4138, 1725, 1811, 58),
    ("Renault Kangoo Van 2003-2009", 3995, 1671, 1811, 57),
    ("Renault Kangoo MPV 2003-2009", 3995, 1664, 1826, 55),
    ("Renault Kangoo Van 1997-2003", 3995, 1664, 1826, 25),
]
for name, L, W, H, S in check_vehicles:
    code, reason = match(L, W, H, rules_by_cat['两厢车'])
    status = f"匹配到 {code}" if code else f"未匹配 [{reason}]"
    print(f"  {name:45s} L={L} W={W} H={H} S={S:3.0f}  \u2192 {status}")

# 其他"短高两厢车"缺口
print(f"\n{'='*60}")
print("检查 4000-4600 范围内是否有其他仍有高度问题的两厢车：")
tall_mpv = [(L, W, H, S, mid, reason) for L, W, H, S, mid, reason in items_2 
            if 3800 <= L <= 4600 and ('\u8d85\u9ad8' in reason or '\u8d85\u957f' in reason)]
tall_mpv.sort(key=lambda x: -x[3])
for L, W, H, S, mid, reason in tall_mpv[:20]:
    print(f"  L={L:5.0f} W={W:4.0f} H={H:4.0f}  S={S:5.0f}  {mid:55s}  [{reason}]")
if not tall_mpv:
    print("  (无)")