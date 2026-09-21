"""
两厢车高度恢复原始值（2S=1575, 2M=1448, 2L=1499），其余保持 0921.1 改动
"""
import csv
from collections import defaultdict

params = {'长容差':0, '宽容差':270, '高容差':280, '余量长容差':635}
tL, tW, tH, tRem = 0, 270, 280, 635

# 读取 0921.1 规则
rules_by_cat = {}
with open('A0.尺码计算/data/ru/尺寸/0921.1-微调&高mpv.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat = row['分类']
        if cat not in rules_by_cat: rules_by_cat[cat] = []
        rules_by_cat[cat].append(dict(row))

# 两厢车高度恢复原始：用 0921.0 的高度值覆盖
original_heights = {'2S': '1575', '2M': '1448', '2L': '1499', '2XL': '1600', '2XXL-510': '1600', '2XXL-525': '1778'}
for r in rules_by_cat['两厢车']:
    code = r['亚马逊尺码']
    if code in original_heights:
        old_h = str(r['高_mm'])
        r['高_mm'] = original_heights[code]
        print(f"  两厢车 {code}: 高 {old_h} -> {r['高_mm']} (恢复原始)")

print("\n=== 当前两厢车规则 ===")
for r in sorted(rules_by_cat['两厢车'], key=lambda x: int(x['高_mm'])):
    effH = int(r['高_mm']) + 280
    print(f"  {r['亚马逊尺码']:10s} L<={r['长_mm']:>5s} W<={r['宽_mm']:>5s}(eff{int(r['宽_mm'])+270:>4d}) H<={r['高_mm']:>5s}(eff{effH:>4d})")

# 读取全量数据
rows = []
with open('A0.尺码计算/output/全量表_RU.csv', 'r', encoding='utf-8') as f:
    next(f)
    for row in csv.reader(f): rows.append(row)

def match(L, W, H, rules):
    rules_typed = []
    for r in rules:
        rules_typed.append({'code': r['亚马逊尺码'], 'L': float(r['长_mm']), 'W': float(r['宽_mm']), 'H': float(r['高_mm'])})
    
    for r in sorted(rules_typed, key=lambda x: (x['L'], x['W'], x['H'])):
        if (r['L']+tL>=L) and (r['W']+tW>=W) and (r['H']+tH>=H) and (r['L']-L<=tRem):
            return r['code'], None
    closest = min(rules_typed, key=lambda r: max(0,L-(r['L']+tL), W-(r['W']+tW), H-(r['H']+tH), r['L']-L-tRem))
    dL = max(0, L-(closest['L']+tL))
    dW = max(0, W-(closest['W']+tW))
    dH = max(0, H-(closest['H']+tH))
    dRem = max(0, closest['L']-L-tRem)
    reasons = []
    if dRem > 0: reasons.append(f'超余量{dRem:.0f}')
    if dL > 0: reasons.append(f'超长{dL:.0f}')
    if dW > 0: reasons.append(f'超宽{dW:.0f}')
    if dH > 0: reasons.append(f'超高{dH:.0f}')
    return None, '|'.join(reasons) if reasons else '?'

# 统计
by_cat_unmatched = defaultdict(list)
by_cat_matched = defaultdict(int)

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
print("恢复高度后各分类匹配情况：")
total_u = 0; total_us = 0
for cat in ['两厢车', '跑车', '三厢车', '越野车', '皮卡']:
    m = by_cat_matched.get(cat, 0)
    u_list = by_cat_unmatched.get(cat, [])
    u = len(u_list); us = sum(x[3] for x in u_list)
    t = m + u; total_u += u; total_us += us
    print(f"  {cat}: {t}总 -> {m}匹配 / {u}未匹配 ({us:.0f}销量)")

print(f"\n总计: {total_u}辆未匹配, {total_us:.0f}销量")

# 两厢车详细分析
print(f"\n{'='*60}")
print("两厢车未匹配详情（按原因分组）：")
items = by_cat_unmatched.get('两厢车', [])
items.sort(key=lambda x: -x[3])

# 分组
def get_main_reason(reason):
    if '超长' in reason: return '超长'
    if '超高' in reason: return '超高'
    if '超宽' in reason: return '超宽'
    if '超余量' in reason: return '超余量'
    return reason

groups = defaultdict(list)
for L, W, H, S, mid, reason in items:
    groups[get_main_reason(reason)].append((L, W, H, S, mid, reason))

# 超高组重点分析
print(f"\n--- [超高] 车辆分析 ---")
height_items = groups.get('超高', [])
height_items.sort(key=lambda x: -x[3])
hs = sum(x[3] for x in height_items)
print(f"  共{len(height_items)}辆, {hs:.0f}销量")

# 按高度区间分组
h_range = defaultdict(list)
for L, W, H, S, mid, reason in height_items:
    h_key = f"H{int(H)//10*10}-{int(H)//10*10+9}"
    h_range[h_key].append((L, W, H, S, mid, reason))

for key in sorted(h_range.keys()):
    g = h_range[key]; gs = sum(x[3] for x in g)
    print(f"\n  {key}: {len(g)}辆, {gs:.0f}销量")
    for L, W, H, S, mid, reason in sorted(g, key=lambda x: -x[3])[:10]:
        print(f"    L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid:50s} [{reason}]")

# 超长组
print(f"\n--- [超长] 车辆分析 ---")
long_items = groups.get('超长', [])
long_items.sort(key=lambda x: -x[3])
ls = sum(x[3] for x in long_items)
print(f"  共{len(long_items)}辆, {ls:.0f}销量")
for L, W, H, S, mid, reason in long_items[:15]:
    print(f"    L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid:50s} [{reason}]")
if len(long_items) > 15:
    print(f"    ... 还有{len(long_items)-15}辆")

# 超余量组
print(f"\n--- [超余量] 车辆分析 ---")
rem_items = groups.get('超余量', [])
rem_items.sort(key=lambda x: -x[3])
rs = sum(x[3] for x in rem_items)
print(f"  共{len(rem_items)}辆, {rs:.0f}销量")
for L, W, H, S, mid, reason in rem_items[:15]:
    print(f"    L={L:5.0f} W={W:4.0f} H={H:4.0f} S={S:5.0f}  {mid:50s} [{reason}")

# Partner/Berlingo 集群验证
print(f"\n{'='*60}")
print("Partner/Berlingo 集群验证（高度恢复后）：")
check = [
    ("Peugeot Partner Van 2008-2012", 4379, 1811, 1875, 83),
    ("Peugeot Partner Van 2002-2012", 4145, 1720, 1811, 90),
    ("Citroen Berlingo MPV 2002-2012", 4138, 1725, 1811, 74),
    ("Peugeot Partner MPV 2002-2012", 4145, 1720, 1811, 71),
    ("Citroen Berlingo Van 2002-2012", 4138, 1725, 1811, 63),
    ("Renault Kangoo Van 2003-2009", 3995, 1671, 1811, 57),
    ("Renault Kangoo MPV 2003-2009", 3995, 1664, 1826, 55),
    ("Renault Kangoo Van 1997-2003", 3995, 1664, 1826, 25),
    ("Fiat Doblo MPV 2005-2015", 4252, 1722, 1819, 140),
]
for name, L, W, H, S in check:
    code, reason = match(L, W, H, rules_by_cat['两厢车'])
    status = f"✅ {code}" if code else f"❌ [{reason}]"
    print(f"  {status:15s}  {name:40s} L={L} W={W} H={H} S={S:.0f}")

# Berlingo/Kangoo 类分析 - 这些需要什么高度？
print(f"\n{'='*60}")
print("Partner/Berlingo/Kangoo 集群所需的合理高度：")
berlingo_types = [
    (4145, 1720, 1811),  # Partner
    (4138, 1725, 1811),  # Berlingo
    (3995, 1664, 1826),  # Kangoo
    (4252, 1722, 1819),  # Doblo
]
print(f"  这些车高度在 1811-1826 之间")
print(f"  2M 当前有效高: 1448+280 = 1728mm -> 最大可容纳 1728")
print(f"  需要有效高至少 1826+0=1826mm 或更高")
print(f"  需要高_mm 至少 1826-280 = 1546mm")
print(f"\n  建议: 2M 高从 1448 -> 1550 (有效高 1830)")
print(f"        或 2M 高从 1448 -> 1575 (有效高 1855, 同 2S 原始高度)")

# 所有高度合适的方案对比
print(f"\n{'='*60}")
print("不同 2M/2L 高度方案覆盖对比：")
for test_h_mm in [1448, 1500, 1525, 1550, 1575, 1600]:
    effH = test_h_mm + 280
    # 临时修改2M和2L高度
    for r in rules_by_cat['两厢车']:
        if r['亚马逊尺码'] in ('2M', '2L'):
            r_original_h = r['高_mm']
            r['高_mm'] = str(test_h_mm)
    
    # 重新匹配 Berlingo 集群
    covered = 0; covered_sales = 0
    for name, L, W, H, S in check:
        code, reason = match(L, W, H, rules_by_cat['两厢车'])
        if code:
            covered += 1; covered_sales += S
    
    # 恢复
    for r in rules_by_cat['两厢车']:
        if r['亚马逊尺码'] in ('2M', '2L'):
            r['高_mm'] = r_original_h if 'r_original_h' in dir() else r['高_mm']
    
    print(f"  2M/2L H={test_h_mm:4d}(effH={effH:4d}) -> 覆盖{covered:2d}/{len(check)}辆 / 覆盖{covered_sales:4.0f}销量")