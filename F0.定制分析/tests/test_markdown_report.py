import json
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))
from custom_analysis import active_rows, dimension_codes
from report import render_report, table
from run import reference_tasks


def test_prius_document_contains_all_members_and_distinguishes_sampling_groups():
    config = json.loads((PROJECT / 'data' / 'prius_custom_analysis.json').read_text(encoding='utf-8'))
    root = PROJECT.parent
    rows = active_rows(root / 'A0.尺码计算' / 'output' / 'US' / '全量' / '全量表.csv', 'Toyota', 'Prius', 'Hatchback')
    codes = dimension_codes(root / '02.代码映射' / 'output' / '尺寸编码映射.csv')
    reviews = [{'品牌': 'Toyota', '车型': 'Prius', '结构': 'Hatchback', '差评数量': '3', '主要差评原因': '尺寸不合适(2)；太重(1)；不好穿(1)'}]
    document = render_report(config, rows, codes, reviews, [], reference_tasks)
    assert '5 条尺寸记录形成 1 个尺寸候选 SKU' in document
    assert '4646 × 1783 × 1491' in document
    assert 'PRIUS-HB-04-15' in document and 'PRIUS-HB-16-26' in document
    assert all(row['DIMENSION-ID'] in document for row in rows)
    assert 'Toyota Prius Sedan 2001-2003 US' not in document
    assert '## 差评依据' in document and '## 完整成员明细' in document
    assert '## Sketchfab 参考任务' in document and '## 输入来源与追踪' in document
    assert '9fe294ecd0454269809650062a0bd4ae' in document


def test_empty_vehicle_fails_before_publication():
    with pytest.raises(ValueError, match='No valid dimension'):
        render_report({}, [], {}, [], [], reference_tasks)


def test_markdown_members_with_pipe_versions_keep_table_columns():
    assert table(['版本'], [['A | B']])[-1] == '| A \\| B |'
