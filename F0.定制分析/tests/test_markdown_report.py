import json
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))
from custom_analysis import active_rows, dimension_codes
from report import render_report, table
from run import reference_tasks


def test_prius_family_document_contains_all_members_and_distinguishes_sampling_groups():
    config = json.loads((PROJECT / 'data' / 'prius_custom_analysis.json').read_text(encoding='utf-8'))
    root = PROJECT.parent
    rows = active_rows(root / 'A0.尺码计算' / 'output' / 'US' / '全量' / '全量表.csv', 'Toyota', models=config['models'], structures=config['structures'])
    codes = dimension_codes(root / '02.代码映射' / 'output' / '尺寸编码映射.csv')
    reviews = [{'品牌': 'Toyota', '车型': 'Prius', '结构': 'Hatchback', '差评数量': '3', '主要差评原因': '尺寸不合适(2)；太重(1)；不好穿(1)'}]
    document = render_report(config, rows, codes, reviews, [], reference_tasks)
    assert '13 条尺寸记录形成 2 个尺寸候选 SKU' in document
    assert 'TOYOTA-PRIUS-' in document
    assert 'PRIUS-C-12-19' in document and 'PRIUS-V-12-17' in document
    assert all(row['DIMENSION-ID'] in document for row in rows)
    assert 'Toyota Prius Sedan 2001-2003 US' not in document
    assert 'Toyota Prius C Hatchback 2012-2017 US' in document
    assert 'Toyota Prius V Wagon 2012-2014 US' in document
    assert 'Toyota Prius Prime Hatchback 2017-2022 US' in document
    assert '## 差评依据' in document and '## 完整成员明细' in document
    assert '## Sketchfab 参考任务' in document and '## 输入来源与追踪' in document
    assert '9fe294ecd0454269809650062a0bd4ae' in document


def test_empty_vehicle_fails_before_publication():
    with pytest.raises(ValueError, match='No valid dimension'):
        render_report({}, [], {}, [], [], reference_tasks)


def test_forester_document_covers_wilderness_and_all_generations():
    config = json.loads((PROJECT / 'data' / 'subaru_forester_custom_analysis.json').read_text(encoding='utf-8'))
    root = PROJECT.parent
    rows = active_rows(root / 'A0.尺码计算' / 'output' / 'US' / '全量' / '全量表.csv',
                       config['make'], config['model'], config['structure'])
    codes = dimension_codes(root / '02.代码映射' / 'output' / '尺寸编码映射.csv')
    reviews = [{'品牌': 'Subaru', '车型': 'Forester', '结构': 'SUV', '差评数量': '2',
                '主要差评原因': '尺寸不合适(1)；少件(1)'}]
    document = render_report(config, rows, codes, reviews, [], reference_tasks)
    assert '8 条尺寸记录形成 2 个尺寸候选 SKU' in document
    assert 'Subaru Forester Wilderness SUV 2026 US' in document
    assert '尺寸不合适(1)；少件(1)' in document
    assert '## 通用尺码适配风险' in document
    assert 'YM 覆盖 1998–2021' in document
    assert '\n## 打样 SKU 方案\n' not in document


def test_gladiator_document_keeps_pickup_fitment_risks_visible():
    config = json.loads((PROJECT / 'data' / 'jeep_gladiator_custom_analysis.json').read_text(encoding='utf-8'))
    root = PROJECT.parent
    rows = active_rows(root / 'A0.尺码计算' / 'output' / 'US' / '全量' / '全量表.csv',
                       config['make'], config['model'], config['structure'])
    codes = dimension_codes(root / '02.代码映射' / 'output' / '尺寸编码映射.csv')
    reviews = [{'品牌': 'Jeep', '车型': 'Gladiator', '结构': 'Pickup', '差评数量': '7',
                '主要差评原因': '质量差(2)；尺寸小(1)；防风带不够长(1)'}]
    document = render_report(config, rows, codes, reviews, [], reference_tasks)
    assert '6 条尺寸记录形成 1 个尺寸候选 SKU' in document
    assert 'PK-M 覆盖全部 6 条记录' in document
    assert '后备箱-PK-L' in document
    assert '驾驶室—货斗分界' in document


def test_kia_soul_document_covers_all_generations_and_review_structure_alias():
    config = json.loads((PROJECT / 'data' / 'kia_soul_custom_analysis.json').read_text(encoding='utf-8'))
    root = PROJECT.parent
    rows = active_rows(root / 'A0.尺码计算' / 'output' / 'US' / '全量' / '全量表.csv',
                       config['make'], config['model'], structures=config['structures'])
    codes = dimension_codes(root / '02.代码映射' / 'output' / '尺寸编码映射.csv')
    reviews = [{'品牌': 'Kia', '车型': 'Soul', '结构': 'Hatchback 5dr', '尺码': '2M；2L+；2XL+',
                '差评数量': '3', '主要差评原因': '尺寸不合适(3)；小(1)；偏小(1)', '严重度评级': '中'}]
    document = render_report(config, rows, codes, reviews, [], reference_tasks)
    assert '4 条尺寸记录形成 1 个尺寸候选 SKU' in document
    assert all(row['DIMENSION-ID'] in document for row in rows)
    assert all(generation in document for generation in ('AM 2010–2013', 'PS 2014–2019', 'SK3 2020–2025'))
    assert '尺寸不合适(3)；小(1)；偏小(1)' in document
    assert '2L 覆盖 2010–2019' in document and '自动长度余量为 324 mm' in document
    assert 'SQUIR3D' not in document
    assert document.count('（可下载）') == 2


def test_markdown_members_with_pipe_versions_keep_table_columns():
    assert table(['版本'], [['A | B']])[-1] == '| A \\| B |'


def test_ford_mustang_document_excludes_mach_e_and_covers_all_generations():
    config = json.loads((PROJECT / 'data' / 'ford_mustang_custom_analysis.json').read_text(encoding='utf-8'))
    root = PROJECT.parent
    rows = active_rows(root / 'A0.尺码计算' / 'output' / 'US' / '全量' / '全量表.csv',
                       config['make'], models=config['models'], structures=config['structures'])
    codes = dimension_codes(root / '02.代码映射' / 'output' / '尺寸编码映射.csv')
    reviews = [
        {'品牌': 'Ford', '车型': 'Mustang', '结构': 'Convertible', '差评数量': '4',
         '主要差评原因': '尺寸不合适(2)；绑带断裂(1)；质量差(1)', '严重度评级': '中'},
        {'品牌': 'Ford', '车型': 'Mustang', '结构': 'Coupe', '差评数量': '13',
         '主要差评原因': '质量差(2)；不防水(2)；尺寸不合适(2)', '严重度评级': '高'},
    ]
    document = render_report(config, rows, codes, reviews, [], reference_tasks)
    assert len(rows) == 57
    assert {row['MODEL'] for row in rows} == {'Mustang', 'Mustang Mach-E'}
    assert 'Ford Mustang Mach-E Rally Crossover 2024-2026 US' in document
    assert {row['代际'] for row in rows} == {f'gen{i}' for i in range(1, 8)}
    assert '13' in document and '绑带断裂(1)' in document
    assert '## 完整成员明细' not in document
    assert '完整成员已用于计算与完整性校验' in document
    assert sorted(item['sku'] for item in config['sketchfab_sku_searches']) == ['SKU-01', 'SKU-02', 'SKU-03', 'SKU-04']
    assert all(item['representative_url'] and len(item['models']) >= 4 for item in config['sketchfab_sku_searches'])
    assert '待补参考模型' not in document
    assert '1993 Ford Mustang GT Foxbody' in document
    assert '2005 Ford Mustang GT' in document
    assert '2024 Ford Mustang Dark Horse' in document
    assert '1969 Ford Mustang Boss 302' in document
    assert '## 候选 SKU 分组原因' in document
    assert '高度中心/mm' in document and '长度中心/mm' in document
    assert '| SKU-02 | Mustang Mach-E | 4 |' in document
    assert '高度中心较高：大于 SKU-01/SKU-03/SKU-04（+322.5/+242.5/+340.5 mm）' in document
    assert '长度中心较长：大于 SKU-01/SKU-03（+287.5/+127.5 mm）' in document
    assert '长度中心较短：小于 SKU-02/SKU-03/SKU-04' in document
    assert '| SKU-01 + SKU-04 | 长度 478>250 |' in document
    assert '| SKU-02 + SKU-03 | 高度 302>100 |' in document
    assert '19 条｜1965–2004' in document
