"""Keep the approved SUV name relationship separate from the pickup record."""
import json
import sys
from pathlib import Path

N = Path(__file__).resolve().parents[1]
R = N.parents[1]
sys.path.insert(0, str(N / 'src'))
from mmy_coverage import analyze, read_csv


def test_hummer_suv_mapping_cannot_claim_pickup_identity_or_market_confirmation():
    raw_models = ['Hummer EV SUV', 'Hummer EV SUV MT Tires 3X', 'Hummer EV']
    sources = [dict(id='test', file='test.csv', sha256='test', kind='model_year',
                    notes='test scope', rows=[dict(make='GMC', model=model, year='2025')
                                               for model in raw_models])]
    entries = {'US': dict(file='test.json', sha256='test', rows=[
        dict(MAKE='GMC', MODEL='Hummer SUV', YEAR='2024-2026', **{'DIMENSION-ID': 'suv'}),
        dict(MAKE='GMC', MODEL='Hummer EV', YEAR='2025', **{'DIMENSION-ID': 'pickup'})])}
    membership = json.loads((R / 'json/dimension-library/车型名称规则.json').read_text())
    result = analyze(sources, entries, entries, membership,
                     read_csv(N / 'data/名称映射.csv'), [],
                     [dict(market='US', as_of_year='2026')],
                     make_mappings=read_csv(N / 'data/品牌映射.csv'))
    rows = {r['MODEL']: r for r in result['覆盖明细.json']}
    assert rows['Hummer EV SUV']['01_DIMENSION-ID'] == 'suv'
    assert rows['Hummer EV SUV']['状态'] == '独立记录覆盖'
    assert rows['Hummer EV SUV MT Tires 3X']['01_DIMENSION-ID'] == 'suv'
    assert rows['Hummer EV SUV MT Tires 3X']['状态'] == '车系级记录覆盖（配置未核）'
    assert rows['Hummer EV']['01_DIMENSION-ID'] == 'pickup'
    assert all(r['市场依据'] == '车型年市场未核' for r in rows.values())
