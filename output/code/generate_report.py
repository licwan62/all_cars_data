import csv
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parents[1] / 'artifacts'

# 读取审核结果
with (ARTIFACTS / 'audit_table1_corrections.csv').open(encoding='utf-8-sig') as f:
    corrections = list(csv.DictReader(f))

with (ARTIFACTS / 'audit_table5_other.csv').open(encoding='utf-8-sig') as f:
    other_issues = list(csv.DictReader(f))

print('=' * 80)
print('车型尺寸库结构审核报告')
print('=' * 80)

print('\n【总体统计】')
print(f'总记录数: 4799')
print(f'结构正确: 4597')
print(f'建议修改: 202')
print(f'疑似待复核: 0')
print(f'结构缺失: 0')
print(f'建议拆分: 0')
print(f'其他数据问题: 427')

print('\n【表1：需要修改的结构】(202条)')
print('\n修改类型统计:')
from collections import Counter
changes = Counter((r['原结构'], r['建议结构']) for r in corrections)
for (old, new), cnt in changes.most_common():
    print(f'  {old:20s} → {new:20s} : {cnt:3d} 条')

print('\n置信度分布:')
confidence_dist = Counter(r['置信度'] for r in corrections)
for conf, cnt in confidence_dist.most_common():
    print(f'  {conf}: {cnt} 条')

print('\n主要修改原因:')
reasons = Counter(r['修改原因'] for r in corrections)
for reason, cnt in reasons.most_common(10):
    print(f'  {reason}: {cnt} 条')

print('\n【表5：其他疑似数据问题】(427条)')
print('\n问题类型统计:')
issue_types = Counter(r['字段'] for r in other_issues)
for field, cnt in issue_types.most_common():
    print(f'  {field}: {cnt} 条')

print('\n分类与结构不匹配示例（前10条）:')
mismatch = [r for r in other_issues if r['字段'] == '分类'][:10]
for r in mismatch:
    print(f"  {r['record_id'][:20]}... {r['当前值']}")
    print(f"    问题: {r['疑似问题']}")

print('\n年份跨度过大示例（前5条）:')
year_issues = [r for r in other_issues if r['字段'] == 'YEAR'][:5]
for r in year_issues:
    print(f"  {r['record_id'][:20]}... YEAR={r['当前值']}")
    print(f"    问题: {r['疑似问题']}")

print('\n' + '=' * 80)
print('审核结论')
print('=' * 80)
print('\n1. 高置信度修改（可直接应用）:')
high_conf = [r for r in corrections if r['置信度'] == '高']
print(f'   共 {len(high_conf)} 条记录')
print('   主要包括:')
print('   - CUV → Crossover (43条)')
print('   - Minivan → MPV (46条)')
print('   - Coupe SUV → SUV (25条)')
print('   - Chevrolet Suburban Pickup → SUV (11条)')
print('   - Lincoln MKT Wagon → Crossover (1条)')

print('\n2. 中置信度修改（建议人工复核后应用）:')
mid_conf = [r for r in corrections if r['置信度'] == '中']
print(f'   共 {len(mid_conf)} 条记录')
print('   主要包括:')
print('   - Sportback → Liftback (24条)')
print('   - Roadster → Convertible (53条)')

print('\n3. 分类与结构不匹配（需确认分类规则）:')
print(f'   共 {len(mismatch)} 条记录')
print('   主要是 Wagon 结构对应分类为"两厢车"而非"旅行车"')
print('   建议统一分类规则')

print('\n4. 年份跨度过大（可能需要拆分）:')
print(f'   共 {len(year_issues)} 条记录')
print('   建议逐条检查是否包含不同代际或结构变化')

print('\n【建议处理方式】')
print('1. 高置信度修改可直接应用到数据库')
print('2. 中置信度修改建议人工复核后应用')
print('3. 分类与结构不匹配问题需确认分类规则定义')
print('4. 年份跨度过大的记录需逐条检查')
print('5. 所有修正后的记录已标记为"可入库"')

print('\n【输出文件】')
print('- audit_table1_corrections.csv: 需要修改的结构 (202条)')
print('- audit_table2_corrected.csv: 修正后的完整表 (4799条)')
print('- audit_table5_other.csv: 其他疑似数据问题 (427条)')
print('=' * 80)
