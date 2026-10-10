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


def test_markdown_members_with_pipe_versions_keep_table_columns():
    assert table(['版本'], [['A | B']])[-1] == '| A \\| B |'
