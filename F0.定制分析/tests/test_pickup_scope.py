import csv
import json
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))
from custom_analysis import active_rows, dimension_codes
from report import render_report
from run import reference_tasks


def test_pickup_filters_clip_years_without_changing_identity(tmp_path):
    source = tmp_path / 'rows.csv'
    fields = ['MAKE', 'MODEL', '结构', 'CAB', 'BED', '版本', 'YEAR', 'DIMENSION-ID', 'L-MM', 'W-MM', 'H-MM']
    base = dict(zip(fields, ['Ford', 'F-150', 'Pickup', 'SuperCrew', '5.5', '', '2004-2008', 'original', '5800', '2000', '1900']))
    rows = [base, base | {'DIMENSION-ID': 'long', 'BED': '6.5'}, base | {'DIMENSION-ID': 'cab', 'CAB': 'SuperCab'}, base | {'DIMENSION-ID': 'ev', '版本': 'Lightning'}, base | {'DIMENSION-ID': 'old', 'YEAR': '2001-2002'}]
    with source.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    selected = active_rows(source, 'Ford', 'F-150', 'Pickup', cabs=['SuperCrew'], beds=['5.5'], year_range=[2008, 2026], excluded_versions=['Lightning'])
    assert [(r['DIMENSION-ID'], r['YEAR'], r['SOURCE_YEAR']) for r in selected] == [('original', '2008', '2004-2008')]
    assert base['YEAR'] == '2004-2008'
    with pytest.raises(ValueError):
        active_rows(source, 'Ford', year_range=[2026, 2008])


@pytest.mark.parametrize('case,expected', [
    ('ford_f150_supercrew_short_bed', 10),
    ('ford_f350_crew_short_bed', 5),
    ('ford_f250_crew_short_bed', 5),
    ('ram1500_crew_short_bed', 6),
    ('silverado2500_crew_short_bed', 1),
])
def test_pickup_configs_match_scope_and_render_complete_reports(case, expected):
    root = PROJECT.parent
    config = json.loads((PROJECT / 'data' / f'{case}_custom_analysis.json').read_text(encoding='utf-8'))
    rows = active_rows(root / 'A0.尺码计算/output/US/全量/全量表.csv', config['make'], config['model'], config['structure'], models=config.get('models'), cabs=config['cabs'], beds=config['beds'], year_range=config['year_range'], excluded_versions=config['excluded_versions'])
    assert len(rows) == expected
    assert all(r['CAB'] in config['cabs'] and r['BED'] in config['beds'] for r in rows)
    codes = dimension_codes(root / '02.代码映射/output/尺寸编码映射.csv')
    document = render_report(config, rows, codes, [], [], reference_tasks)
    assert all(r['DIMENSION-ID'] in document for r in rows)
    assert '来源年款' in document and '## 通用尺码适配风险' in document
    if case.startswith('ram'):
        assert '2009、2010、2013' in document
        assert any(r['MODEL'] == '1500 Classic' for r in rows)
    if 'f250' in case:
        assert next(r for r in rows if r['SOURCE_YEAR'] == '1999-2007')['YEAR'] == '2001-2007'
