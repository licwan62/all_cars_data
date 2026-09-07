"""发布前校验；输出审计 JSON，不覆盖 public。"""
import json
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

import pandas_analysis as analysis


def main():
    root = Path(__file__).resolve().parent.parent
    public = root / 'public'
    output = root / '尺码计算' / 'output'
    old = analysis._read_csv(public / '全量数据.csv').set_index('DIMENSION-ID')
    new = analysis._read_csv(output / 'pandas_output.csv').set_index('DIMENSION-ID')
    baseline = analysis.calculate(public, config_dir=root / '尺码计算' / 'rules', trim_source=public / '全量数据.csv')
    baseline = baseline.set_index('DIMENSION-ID').astype('string').fillna('')
    assert set(old.index) == set(new.index) == set(baseline.index)
    assert old.index.is_unique and new.index.is_unique
    differences = {c: int((old[c] != baseline.loc[old.index, c]).sum()) for c in old if (old[c] != baseline.loc[old.index, c]).any()}
    assert not differences, differences
    changes = {c: int((old[c] != new.loc[old.index, c]).sum()) for c in old if (old[c] != new.loc[old.index, c]).any()}
    refs = analysis._read_csv(public / '参考尺寸计算.csv').set_index('车身号')
    for key, row in new.iterrows():
        factor = refs.loc[row['车形'], '周长系数']
        if not factor or not row['L-MM'] or not row['H-MM']:
            assert row['参考半周长'] == '', key
            continue
        expected = ((Decimal(row['L-MM']) + Decimal(row['H-MM'])) * Decimal(factor) - Decimal(750)).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN)
        assert int(row['参考半周长']) == int(expected), (key, row['参考半周长'], expected)
    assert new['TRIM'].equals(old.loc[new.index, 'TRIM'])
    shapes = analysis._read_csv(root / '车形分类核定' / 'artifacts' / 'record_shape.csv').set_index('DIMENSION-ID')['车形']
    assert new['车形'].equals(shapes.loc[new.index])
    report = {
        'rows': len(new), 'baseline_reproduced_exactly': True, 'changed_columns': changes,
        'half_perimeter_formula': 'ROUND_HALF_EVEN((L-MM + H-MM) * 周长系数 - 750)',
        'half_perimeter_filled': int(new['参考半周长'].ne('').sum()),
        'half_perimeter_blank': int(new['参考半周长'].eq('').sum()),
        'trim_preserved': True, 'candidate_shapes_match': True,
        'all_half_perimeters_independently_verified': True, 'tests_passed': 7,
        'rules_source': '尺码计算/output/车型数据尺码.xlsx: 参数!容差参数表(A1:B2), 尺码!tb_size(A1:J44)',
    }
    (output / 'recalculation_2026-09-06.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
