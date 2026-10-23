import importlib.util
from pathlib import Path
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location('regular_links', Path(__file__).parents[1] / 'scripts/run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_gray_size_and_custom_quantity():
    shipment = pd.DataFrame([{'MAKE': 'A', 'MODEL': 'B', 'YEAR': '2020-2022', '尺码': size,
                              '版本': '', '结构': 'SUV', '发货量': 7} for size in ['YL', '']])
    identity = pd.DataFrame([{'DIMENSION-ID': 'a', 'MAKE': 'A', 'MODEL': 'B', 'YEAR': '2020-2022',
                              '供货尺码': 'YL', '评估类别': '普通车'}])
    full = pd.DataFrame([{'DIMENSION-ID': 'a', 'MAKE': 'A', 'MODEL': 'B', 'YEAR': '2020-2021',
                          '版本': '', '结构': 'SUV', '自动尺码': 'YM', 'L-MM': 4500, 'W-MM': 1800, 'H-MM': 1600}])
    result, evidence = module.analyze(shipment, identity, full)
    assert result['发货量'].sum() == 14
    assert result['审核状态'].tolist() == ['待确认年份缺口', '待确认定制尺码']
    assert result.iloc[0]['尺码'] == 'YL'
    assert result.iloc[0]['年份缺口'] == '2022'
    assert len(evidence) == 2
    shipment.loc[0, '发货量'] = -1
    with pytest.raises(ValueError, match='非负整数'):
        module.analyze(shipment, identity, full)
