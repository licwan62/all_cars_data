import sys
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
import data_layout
from gray_matching import apply_gray_matching
from pandas_analysis import _read_csv


def test_raptor_gray_zone_keeps_configuration_and_store_boundaries():
    anchor = {
        "DIMENSION-ID": "Ford F-150 Raptor Pickup 2017-2020 SuperCrew 5.5 US",
        "MAKE": "Ford", "MODEL": "F-150", "版本": "Raptor", "结构": "Pickup",
        "分类": "皮卡", "CAB": "SuperCrew", "BED": "5.5", "YEAR": "2017-2020",
        "L-MM": 5890, "W-MM": 2192, "H-MM": 1994, "插片指数": 0,
        "自动尺码": "PK-L", "自动长度余量": 10, "规则ID": "base", "原因": "",
    }
    current = {
        **anchor, "DIMENSION-ID": "Ford F-150 Raptor Pickup 2021-2026 SuperCrew 5.5 US",
        "YEAR": "2021-2026", "L-MM": 5908, "W-MM": 2200, "H-MM": 2027,
        "自动尺码": "PK-XL", "自动长度余量": 292,
    }
    raptor_r = {**current, "DIMENSION-ID": "Raptor R US", "版本": "Raptor R"}
    frame = pd.DataFrame([anchor, current, raptor_r])
    layout = data_layout.current("US")
    parameters, rules = _read_csv(layout.parameters), _read_csv(layout.rules)
    matched, audit = apply_gray_matching(frame, parameters, rules)
    assert matched["自动尺码"].tolist() == ["PK-L", "PK-L", "PK-XL"]
    assert matched.loc[1, "自动长度余量"] == -8
    assert len(audit) == 1 and audit[0][-1] == "8"
    restricted, _ = apply_gray_matching(frame, parameters, rules, ["PK-XL"])
    assert restricted.loc[1, "自动尺码"] == "PK-XL"
    frame.loc[1, "L-MM"] = 5926
    outside, _ = apply_gray_matching(frame, parameters, rules)
    assert outside.loc[1, "自动尺码"] == "PK-XL"
