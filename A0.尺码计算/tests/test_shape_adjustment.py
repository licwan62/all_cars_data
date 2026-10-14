import pandas as pd
import pytest

import pandas_analysis as analysis
from shape_adjustment import adjust, load_config
from rule_identity import rule_ids


def fixture(*, structure="Hatchback", status="PROBABLE", height=1500, shape="SPORT_LIFTBACK", insert=0, length=4500, whitelist=""):
    rules = pd.DataFrame([
        {"尺码": "2XL", "分类": "两厢车", "尺码池": "H", "长上限": 4600, "插片指数上限": 999, "插片指数下限": "", "车型白名单": whitelist},
        {"尺码": "3M", "分类": "三厢车", "尺码池": "S", "长上限": 4560, "插片指数上限": 120, "插片指数下限": "", "车型白名单": ""},
    ])
    config = {**load_config(), "enabled": True, "target_sizes": ["3M"]}
    parameters = pd.DataFrame([{"参数": "余量长容差", "值": 500}])
    vehicle = pd.DataFrame([{"DIMENSION-ID": "A B Hatchback 2020 US", "MAKE": "A", "MODEL": "B", "YEAR": "2020", "结构": structure,
        "分类": "两厢车", "CAB": "", "版本": "", "L-MM": length, "H-MM": height, "插片指数": insert, "车形": "H0"}])
    shapes = pd.DataFrame([{"DIMENSION-ID": vehicle.iloc[0]["DIMENSION-ID"], "COUNTRY": "US", "SHAPE": shape, "SHAPE_STATUS": status}])
    base = analysis.SizeMatcher(parameters, rules).apply(vehicle)
    return base, parameters, rules, config, shapes


def run(**kwargs):
    base, parameters, rules, config, shapes = fixture(**kwargs)
    result, audit = adjust(base, parameters, rules, config=config, shapes=shapes)
    return base, result, audit, rules


@pytest.mark.parametrize("structure,shape", [("Hatchback", "SPORT_LIFTBACK"), ("Fastback", "LOW_FASTBACK"), ("Liftback", "SPORT_LIFTBACK")])
def test_low_sloped_body_changes_size_and_preserves_base_fields(structure, shape):
    base, result, audit, rules = run(structure=structure, shape=shape)
    assert result.iloc[0]["自动尺码"] == "3M"
    assert result.iloc[0]["规则ID"] == rule_ids(rules).iloc[1]
    assert result.iloc[0]["自动长度余量"] == 60
    assert result[["分类", "结构", "车形", "插片指数"]].equals(base[["分类", "结构", "车形", "插片指数"]])
    assert audit[0]["基础尺码"] == "2XL" and audit[0]["处理"] == "已调整"


@pytest.mark.parametrize("kwargs", [{"height": 1501}, {"height": None}, {"height": 0}, {"structure": "Wagon"}, {"structure": "Coupe"}, {"shape": "COMPACT_HATCH"}, {"status": "INFERRED"}, {"insert": 121}, {"length": 4600}, {"whitelist": "仅 A B 2020 Hatchback"}])
def test_nonqualifying_or_unsafe_target_preserves_original_result(kwargs):
    base, result, _, _ = run(**kwargs)
    assert result.equals(base)


def test_store_shelf_cannot_be_bypassed():
    base, parameters, rules, config, shapes = fixture()
    result, audit = adjust(base, parameters, rules, allowed_sizes=["2XL"], config=config, shapes=shapes)
    assert result.equals(base)
    assert "货架" in audit[0]["处理"]


def test_disabled_adjustment_keeps_base_without_reading_shape(monkeypatch):
    base, parameters, rules, config, shapes = fixture()
    config["enabled"] = False
    monkeypatch.setattr(analysis, "_read_csv", lambda _: pytest.fail("停用时不应读取SHAPE来源"))
    result, audit = adjust(base, parameters, rules, config=config)
    assert result.equals(base) and audit == []


def test_disabled_report_is_explicit(monkeypatch):
    import shape_adjustment
    import build_match_report as report
    base, parameters, rules, config, shapes = fixture()
    config["enabled"] = False
    monkeypatch.setattr(shape_adjustment, "load_config", lambda: config)
    text = "\n".join(report.shape_adjustment_text(base, rules, parameters))
    assert "当前已停用" in text and "调整记录数为0" in text


def test_missing_or_duplicate_exact_shape_fails():
    base, parameters, rules, config, shapes = fixture()
    for source in [shapes.iloc[:0], pd.concat([shapes, shapes])]:
        with pytest.raises(ValueError):
            adjust(base, parameters, rules, config=config, shapes=source)


def test_report_reminds_and_reconciles(monkeypatch):
    import shape_adjustment
    import build_match_report as report
    base, parameters, rules, config, shapes = fixture()
    monkeypatch.setattr(shape_adjustment, "load_config", lambda: config)
    original_read = analysis._read_csv
    monkeypatch.setattr(analysis, "_read_csv", lambda path: shapes if path == shape_adjustment.SOURCE else original_read(path))
    changed, _ = adjust(base, parameters, rules, config=config, shapes=shapes)
    text = "\n".join(report.shape_adjustment_text(changed, rules, parameters))
    assert "实际调整明细（1 条）" in text and "2XL | 3M" in text
    with pytest.raises(ValueError, match="不一致"):
        report.shape_adjustment_text(base, rules, parameters)
