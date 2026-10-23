import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('shipment', Path(__file__).resolve().parents[1] / 'code/build_two_batch_shipment.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_cap_redistributes_without_losing_units():
    assert module.allocate([1000, 2, 1], 10, [3, 4, 10]) == [3, 4, 3]


def test_coverage_batches_preserve_identity_and_flags():
    rows = [{'MAKE': 'A', 'MODEL': str(i), 'YEAR': '2020', '供货尺码': 'M',
             '评估类别': '普通车', '调整后市场潜力值': str(100 - i),
             '定制标记': '是' if i == 0 else '否', '差评标记': '尺寸'} for i in range(6)]
    config = {'category': '普通车', 'weight': '调整后市场潜力值', 'batch_units': [4, 4],
              'max_total_per_sku': 2, 'custom_size_blank': True,
              'max_skus_per_batch': 4, 'batch2_new_sku_target': 2}
    result = module.plan(rows, config)
    assert sum(r['第一批发货量'] for r in result) == 4
    assert sum(r['第二批发货量'] for r in result) == 4
    assert sum(r['第一批发货量'] == 0 for r in result) == 2
    assert max(r['总发货量'] for r in result) <= 2
    assert sum(r['第一批发货量'] > 0 for r in result) <= 4
    assert sum(r['第二批发货量'] > 0 for r in result) <= 4
    assert result[0]['供货尺码'] == ''
    assert all(r['差评标记'] == '尺寸' for r in result)
    assert all('SKU' not in r for r in result)
    exported = module.business_rows(result, '总发货量')
    assert list(exported[0]) == ['MAKE', 'MODEL', '版本', '结构', 'YEAR', '尺码', '定制标记', '差评标记', '发货量']
    assert all(r['YEAR'] == '2020' for r in exported)
    assert sum(r['发货量'] for r in exported) == 8
    assert exported[0]['尺码'] == ''


def test_batch_capacity_failure_does_not_relax_limits():
    import pytest
    rows = [{'MAKE': 'A', 'MODEL': str(i), 'YEAR': '2020', '供货尺码': 'M',
             '评估类别': '普通车', '调整后市场潜力值': '1',
             '定制标记': '否', '差评标记': '无'} for i in range(5)]
    config = {'category': '普通车', 'weight': '调整后市场潜力值', 'batch_units': [5, 5],
              'max_total_per_sku': 2, 'custom_size_blank': True,
              'max_skus_per_batch': 2, 'batch2_new_sku_target': 1}
    with pytest.raises(ValueError, match='容量不足'):
        module.plan(rows, config)


def test_unavailable_model_is_excluded_only_from_first_batch():
    rows = [{'MAKE': 'Ford', 'MODEL': str(i), 'YEAR': '2020', '供货尺码': 'M',
             '评估类别': '普通车', '调整后市场潜力值': str(100-i),
             '定制标记': '否', '差评标记': '无'} for i in range(6)]
    config = {'category': '普通车', 'weight': '调整后市场潜力值', 'batch_units': [4, 4],
              'max_total_per_sku': 2, 'custom_size_blank': True,
              'max_skus_per_batch': 4, 'batch2_new_sku_target': 2}
    blocked, _ = module.unavailable_models(rows, [{'车型': 'Ford 0 4dr', '可用': '0'}])
    result = module.plan(rows, config, blocked)
    r = next(r for r in result if r['MODEL'] == '0')
    assert r['第一批发货量'] == 0 and r['第二批发货量'] > 0


def test_version_evidence_requires_comparable_generation_and_year():
    atoms = [dict(zip(['DIMENSION-ID','MAKE','MODEL','版本','代际','结构','YEAR','L-MM','W-MM','H-MM','自动尺码'], r))
             for r in [('a','Jeep','Test','','gen1','SUV','2020-2022',4900,1900,1800,'M'),
                       ('b','Jeep','Test','L','gen1','SUV','2021-2022',5200,1900,1800,'L'),
                       ('c','Jeep','Test','Turbo','gen2','SUV','2021-2022',5600,1900,1800,'XL'),
                       ('d','Jeep','Test','Sport','gen1','SUV','2025-2026',5500,1900,1800,'XL')]]
    evaluations = [{'MAKE':'Jeep','MODEL':'Test','YEAR':r['YEAR'],'供货尺码':r['自动尺码']} for r in atoms]
    identity = [{**e,'DIMENSION-ID':a['DIMENSION-ID']} for e,a in zip(evaluations,atoms)]
    labels, evidence = module.version_labels(evaluations, atoms, identity,
                      {'min_dimension_delta_mm':50,'include_size_changes':True})
    assert len(evidence) == 1
    assert labels[('Jeep','Test','2021-2022','L')] == 'L'
    assert labels[('Jeep','Test','2021-2022','XL')] == ''
    assert labels[('Jeep','Test','2025-2026','XL')] == ''
