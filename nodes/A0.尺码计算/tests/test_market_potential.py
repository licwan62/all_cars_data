from pathlib import Path
import json
import pandas as pd
import pytest
import add_market_potential as market


def setup(project):
    detail = pd.DataFrame({"DIMENSION-ID": ["a US", "b US"], "市场潜力": ["10.000000", "20.000000"], "销量潜力调整": ["1.000000", "0.000000"]})
    source = project / "source"; source.mkdir()
    path = source / "市场潜力.csv"; detail.to_csv(path,index=False,encoding="utf-8-sig")
    (source / "manifest.json").write_text(json.dumps({"version":"test", "deliverables":[{"file":path.name,"sha256":market.sha256(path)}]}),encoding="utf-8")
    for i,name in enumerate(market.TABLES):
        path=project/"output"/name; path.parent.mkdir(parents=True,exist_ok=True)
        pd.DataFrame({"DIMENSION-ID":["a US","b US"],"车型销量":["100","200"],"自动尺码":[f"store{i}"]*2,"TRIM":["LE","XLE"]}).to_csv(path,index=False,encoding="utf-8-sig")
    return source


def test_run_preserves_original_columns_and_is_idempotent(tmp_path):
    source=setup(tmp_path)
    before={name:market.read(tmp_path/"output"/name) for name in market.TABLES}
    market.run(tmp_path,source)
    hashes={name:market.sha256(tmp_path/"output"/name) for name in market.TABLES}
    for name in market.TABLES:
        frame=market.read(tmp_path/"output"/name)
        assert frame[before[name].columns].equals(before[name])
        assert frame.columns.tolist()[1:4] == ["车型销量","市场潜力","销量潜力调整"]
        assert frame["市场潜力"].tolist()==["10.000000","20.000000"]
    market.run(tmp_path,source)
    assert hashes=={name:market.sha256(tmp_path/"output"/name) for name in market.TABLES}


def test_invalid_source_or_table_never_publishes(tmp_path):
    source=setup(tmp_path)
    broken=tmp_path/"output"/market.TABLES[-1]
    market.read(broken).iloc[:1].to_csv(broken,index=False)
    hashes={name:market.sha256(tmp_path/"output"/name) for name in market.TABLES}
    with pytest.raises(ValueError,match="DIMENSION-ID"):
        market.run(tmp_path,source)
    assert hashes=={name:market.sha256(tmp_path/"output"/name) for name in market.TABLES}
    with (source/"市场潜力.csv").open("a",encoding="utf-8") as f: f.write("bad")
    with pytest.raises(ValueError,match="sha256"):
        market.run(tmp_path,source)
