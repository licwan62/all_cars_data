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
              'max_total_per_sku': 2, 'custom_size_blank': True}
    result = module.plan(rows, config)
    assert sum(r['第一批发货量'] for r in result) == 4
    assert sum(r['第二批发货量'] for r in result) == 4
    assert sum(r['第一批发货量'] == 0 for r in result) == 2
    assert max(r['总发货量'] for r in result) <= 2
    assert result[0]['供货尺码'] == ''
    assert all(r['差评标记'] == '尺寸' for r in result)
    assert len({r['SKU'] for r in result}) == 6
