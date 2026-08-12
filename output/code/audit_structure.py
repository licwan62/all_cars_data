import csv
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / 'output' / 'artifacts'

# 读取数据
with (ROOT / '车型尺寸库.csv').open(encoding='utf-8-sig') as f:
    reader = list(csv.reader(f))
header = reader[0]
data = reader[1:]

IDX = {h: i for i, h in enumerate(header)}

# 审核结果
table1_corrections = []
table2_corrected = []
table3_uncertain = []
table4_split = []
table5_other = []

stats = {
    'total': len(data),
    'correct': 0,
    'modified': 0,
    'uncertain': 0,
    'empty': 0,
    'split': 0,
    'other_issues': 0,
}

def check_record(row):
    """检查单条记录"""
    record_id = row[IDX['record_id']]
    make = row[IDX['MAKE']]
    model = row[IDX['MODEL']]
    version = row[IDX['版本']]
    cab = row[IDX['CAB']]
    bed = row[IDX['BED']]
    structure = row[IDX['结构']]
    generation = row[IDX['代际']]
    year = row[IDX['YEAR']]
    category = row[IDX['分类']]
    l_in = row[IDX['L-IN']]
    w_in = row[IDX['W-IN']]
    h_in = row[IDX['H-IN']]
    ref_car = row[IDX['参考车型']]
    note = row[IDX['备注']]
    iter_status = row[IDX['迭代状态']]
    
    original_structure = structure
    original_category = category
    needs_correction = False
    suggested_structure = structure
    suggested_category = category
    confidence = ''
    reason = ''
    basis = ''
    needs_split = False
    
    # 1. 检查空结构
    if not structure.strip():
        stats['empty'] += 1
        table3_uncertain.append({
            'record_id': record_id,
            'MAKE': make,
            'MODEL': model,
            '版本': version,
            'YEAR': year,
            '当前结构': structure,
            '疑似结构': '无法判断',
            '问题': '结构字段为空',
            '需要补充的信息': '车型官方资料',
            '建议处理方式': '人工复核',
        })
        table2_corrected.append(row)
        return
    
    # 2. 标准化非标准结构名称
    standard_map = {
        'CUV': ('Crossover', '高', 'CUV应使用标准名称Crossover', '数据库命名规范'),
        'Minivan': ('MPV', '高', 'Minivan应使用标准名称MPV', '数据库命名规范'),
        'Coupe SUV': ('SUV', '高', 'Coupe SUV应归类为SUV', '车型实际结构'),
        'Sportback': ('Liftback', '中', 'Sportback应使用标准名称Liftback', '数据库命名规范'),
        'Roadster': ('Convertible', '中', 'Roadster属于敞篷车，归类为Convertible', '车型实际结构'),
    }
    
    if structure in standard_map:
        suggested_structure, confidence, reason, basis = standard_map[structure]
        needs_correction = True
        
        # 分类是固定五类车衣版型，不随 Body Style 标准化创建新类别。
    
    # 3. 特殊车型结构修正
    # Chevrolet Suburban 跨越多个历史代际，禁止自动修改，必须按 YEAR 人工复核。
    if make == 'Chevrolet' and model == 'Suburban' and structure == 'Pickup':
        table3_uncertain.append({
            'record_id': record_id, 'MAKE': make, 'MODEL': model, '版本': version,
            'YEAR': year, '当前结构': structure, '疑似结构': 'Wagon/SUV',
            '问题': '历史 Suburban 需按 YEAR 区分封闭 Carryall/Wagon/SUV，不得因卡车底盘直接判 Pickup',
            '需要补充的信息': '对应年份官方规格、车身照片及是否存在独立开放货斗',
            '建议处理方式': '仅提交用户人工复核，禁止自动应用',
        })
    
    # Lincoln MKT 应该是 Crossover 而不是 Wagon
    if make == 'Lincoln' and model == 'MKT' and structure == 'Wagon':
        suggested_structure = 'Crossover'
        needs_correction = True
        confidence = '高'
        reason = 'MKT是Crossover，不是Wagon'
        basis = '车型官方资料'
        if category == '两厢车':
            suggested_category = '越野车'
    
    # 4. 检查分类与结构是否匹配（仅当结构正确时）
    if not needs_correction:
        struct_cat_map = {
            'Sedan': '三厢车',
            'Coupe': '跑车',
            'SUV': '越野车',
            'Crossover': '跨界车',
            'Wagon': '两厢车',
            'Hatchback': '两厢车',
            'Convertible': '跑车',
            'Pickup': '皮卡',
            # MPV/Van 需在五类车衣版型中人工选择；Liftback 必须按长斜背/短高尾门判断。
        }
        
        expected_cat = struct_cat_map.get(structure, '')
        if expected_cat and category != expected_cat:
            # 分类不匹配，记录到其他问题
            stats['other_issues'] += 1
            table5_other.append({
                'record_id': record_id,
                '字段': '分类',
                '当前值': f'结构={structure}, 分类={category}',
                '疑似问题': f'结构 {structure} 通常对应分类 {expected_cat}',
                '建议检查': '确认分类规则',
            })
    
    # 5. 检查年份跨度
    if '-' in year:
        try:
            parts = year.split('-')
            if len(parts) == 2:
                start_y = int(parts[0])
                end_y = int(parts[1])
                span = end_y - start_y
                
                if span > 20:
                    stats['other_issues'] += 1
                    table5_other.append({
                        'record_id': record_id,
                        '字段': 'YEAR',
                        '当前值': year,
                        '疑似问题': f'年份跨度 {span} 年，可能包含不同代际',
                        '建议检查': '确认该时间段内结构是否一致',
                    })
        except:
            pass
    
    # 构建输出
    if needs_correction:
        stats['modified'] += 1
        table1_corrections.append({
            'record_id': record_id,
            'MAKE': make,
            'MODEL': model,
            '版本': version,
            'YEAR': year,
            '原结构': original_structure,
            '建议结构': suggested_structure,
            '原分类': original_category,
            '建议分类': suggested_category,
            '置信度': confidence,
            '修改原因': reason,
            '主要依据': basis,
            '是否需要拆分记录': '否',
        })
        
        # 修正记录
        corrected_row = row.copy()
        corrected_row[IDX['结构']] = suggested_structure
        if suggested_category != original_category:
            corrected_row[IDX['分类']] = suggested_category
        corrected_row[IDX['迭代状态']] = '可入库'
        table2_corrected.append(corrected_row)
    else:
        stats['correct'] += 1
        table2_corrected.append(row)

# 处理所有记录
print('开始审核...')
for i, row in enumerate(data):
    if i % 500 == 0:
        print(f'已处理 {i}/{len(data)} 条记录...')
    check_record(row)

print(f'\n=== 审核完成 ===')
print(f'总记录数: {stats["total"]}')
print(f'结构正确: {stats["correct"]}')
print(f'建议修改: {stats["modified"]}')
print(f'疑似待复核: {stats["uncertain"]}')
print(f'结构缺失: {stats["empty"]}')
print(f'建议拆分: {stats["split"]}')
print(f'其他数据问题: {stats["other_issues"]}')

# 输出表1
if table1_corrections:
    with (ARTIFACTS / 'audit_table1_corrections.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=table1_corrections[0].keys())
        writer.writeheader()
        writer.writerows(table1_corrections)
    print(f'\n表1已保存: audit_table1_corrections.csv ({len(table1_corrections)} 条)')

# 输出表2
with (ARTIFACTS / 'audit_table2_corrected.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(table2_corrected)
print(f'表2已保存: audit_table2_corrected.csv ({len(table2_corrected)} 条)')

# 输出表3
if table3_uncertain:
    with (ARTIFACTS / 'audit_table3_uncertain.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=table3_uncertain[0].keys())
        writer.writeheader()
        writer.writerows(table3_uncertain)
    print(f'表3已保存: audit_table3_uncertain.csv ({len(table3_uncertain)} 条)')

# 输出表4
if table4_split:
    with (ARTIFACTS / 'audit_table4_split.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=table4_split[0].keys())
        writer.writeheader()
        writer.writerows(table4_split)
    print(f'表4已保存: audit_table4_split.csv ({len(table4_split)} 条)')

# 输出表5
if table5_other:
    with (ARTIFACTS / 'audit_table5_other.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=table5_other[0].keys())
        writer.writeheader()
        writer.writerows(table5_other)
    print(f'表5已保存: audit_table5_other.csv ({len(table5_other)} 条)')

print('\n所有审核表已生成！')
