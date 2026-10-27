from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import add_market_potential as market


@pytest.fixture
def policy():
    return market.load_config(market.PROJECT)


@pytest.fixture
def project(tmp_path, policy):
    directory = tmp_path / "data" / market.SALES_DIR
    directory.mkdir(parents=True)
    (directory / "参数.json").write_text(json.dumps(policy), encoding="utf-8")
    pd.DataFrame([{"车型": "Toyota Camry", "ASIN": "B000000001", "MSKU": "OWN",
                   "7天销量": "7", "15天销量": "15", "30天销量": "30"}]).to_csv(
        directory / "积加销量.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([{"站点": "Seller:US", "车型": "Toyota Camry", "ASIN": "B000000002",
                   "SKU": "COMP", "类别": "车型款", "销量": "10"}]).to_csv(
        directory / "竞品车罩销量统计表.csv", index=False, encoding="utf-8-sig")
    return tmp_path


@pytest.fixture
def full():
    return pd.DataFrame([
        {"DIMENSION-ID": "camry-a US", "MAKE": "Toyota", "MODEL": "Camry", "YEAR": "2021-2026",
         "尺寸组销量": "1000", "车型销量": "4000", "自动尺码": "M", "TRIM": "LE,SE"},
        {"DIMENSION-ID": "camry-b US", "MAKE": "Toyota", "MODEL": "Camry", "YEAR": "2026",
         "尺寸组销量": "3000", "车型销量": "4000", "自动尺码": "L", "TRIM": "XLE"},
        {"DIMENSION-ID": "focus US", "MAKE": "Ford", "MODEL": "Focus", "YEAR": "2021",
         "尺寸组销量": "1000000", "车型销量": "1000000", "自动尺码": "S", "TRIM": ""},
    ])


def test_retention_matches_d1_thresholds_and_interval(policy):
    spec = importlib.util.spec_from_file_location(
        "d1_market_reference", market.ROOT / "nodes/D1.发货评估/code/build_delivery_evaluation.py")
    d1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d1)
    assert market.interval_retention("2021", policy) == 1
    assert market.interval_retention("2011", policy) == .5
    assert market.interval_retention("2030", policy) == 1
    assert market.interval_retention("2011-2021", policy) == pytest.approx(
        np.mean([2 ** (-age / 10) for age in range(11)]))
    for year in ["1950-1960", "2011", "2020-2023", "2026", "2030"]:
        assert market.interval_retention(year, policy) == pytest.approx(d1.interval_retention(year, policy))


@pytest.mark.parametrize("year", ["", "2026-2020", "unknown", "2020/2025"])
def test_invalid_year_fails(year, policy):
    with pytest.raises(ValueError, match="年份"):
        market.interval_retention(year, policy)


def test_two_sources_sum_targets_and_conserve_allocations(project, policy, full):
    sales = market.load_sales(project, policy)
    assert sales["月销量估计"].tolist() == pytest.approx([30, 10])
    assert sales["销量目标分"].tolist() == pytest.approx([450, 100])
    detail, audit = market.calculate(full, sales, policy)
    assert detail["销售目标分合计"].tolist() == pytest.approx([137.5, 412.5, 0])
    assert detail[market.COLUMN].tolist() == pytest.approx([137.5, 412.5, 1000])
    assert detail["销售目标分合计"].sum() == pytest.approx(audit["已分摊目标分"].sum())
    assert detail["积加月销量分摊"].sum() == pytest.approx(30)
    assert detail["竞品月销量分摊"].sum() == pytest.approx(10)


def test_confidence_is_per_asin_not_per_model(project, policy):
    path = project / "data" / market.SALES_DIR / "竞品车罩销量统计表.csv"
    first = market.read(path)
    second = first.assign(ASIN="B000000003")
    pd.concat([first, second]).to_csv(path, index=False)
    sales = market.load_sales(project, policy)
    assert sales.loc[sales["来源"].eq("竞品"), "销量目标分"].sum() == pytest.approx(200)


def test_zero_base_equal_split_and_no_sales_keeps_base(project, policy, full):
    full.loc[:1, "尺寸组销量"] = "0"
    detail, _ = market.calculate(full, market.load_sales(project, policy), policy)
    assert detail[market.COLUMN].tolist() == pytest.approx([275, 275, 1000])
    sales = market.load_sales(project, policy)
    sales[["月销量估计", "销量目标分"]] = 0.0
    detail, _ = market.calculate(full, sales, policy)
    assert detail[market.COLUMN].tolist() == pytest.approx([0, 0, 1000])


def test_match_longest_short_names_ambiguity_and_generic():
    models = [("Ford", "Bronco"), ("Ford", "Bronco Sport"), ("Ford", "F-150"),
              ("Audi", "A3"), ("Honda", "S2000"), ("Other", "Bronco")]
    assert market.match_model("Ford Bronco Sport (2021-26)", models)[0] == [("Ford", "Bronco Sport")]
    assert market.match_model("Ford F150", models)[0] == [("Ford", "F-150")]
    assert market.match_model("Audi A30", models)[0] == []
    assert market.match_model("Honda S2000", models)[0] == [("Honda", "S2000")]
    for name in ["Toyota Camry / Honda Accord", "未匹配", "皮卡通用", "Missing"]:
        assert "待审核" in market.match_model(name, models)[1]
    assert "歧义" in market.match_model("Bronco", models)[1]


def test_competitor_non_cover_is_audited_without_allocating(project, policy, full):
    sales = market.load_sales(project, policy)
    sales.loc[sales["来源"].eq("竞品"), "类别"] = "轮胎罩"
    detail, audit = market.calculate(full, sales, policy)
    assert detail["销售目标分合计"].sum() == pytest.approx(450)
    assert audit.loc[1, "已分摊目标分"] == 0
    assert "类别" in audit.loc[1, "匹配状态"]


@pytest.mark.parametrize("change", ["duplicate_own", "duplicate_comp", "cross_source", "negative", "infinite", "window"])
def test_bad_sales_rejected(project, policy, change):
    directory = project / "data" / market.SALES_DIR
    own = market.read(directory / "积加销量.csv")
    comp = market.read(directory / "竞品车罩销量统计表.csv")
    if change == "duplicate_own":
        own = pd.concat([own, own])
    elif change == "duplicate_comp":
        comp = pd.concat([comp, comp])
    elif change == "cross_source":
        comp["ASIN"] = own.iloc[0]["ASIN"]
    elif change == "negative":
        comp["销量"] = "-1"
    elif change == "infinite":
        own["30天销量"] = "inf"
    else:
        own["7天销量"] = "40"
    own.to_csv(directory / "积加销量.csv", index=False)
    comp.to_csv(directory / "竞品车罩销量统计表.csv", index=False)
    with pytest.raises(ValueError):
        market.load_sales(project, policy)


def test_csv_recovery_preserves_commas_and_accepts_ten_char_msku(tmp_path):
    path = tmp_path / "source.csv"
    path.write_text("序号,车型,ASIN,MSKU,订单销量,7天销量,15天销量,30天销量\n"
                    "1,Ford F150, F250,B000000001,COBL01C3XL,0,1,2,3\n", encoding="utf-8")
    frame, repaired = market.read_jijia_export(path)
    assert repaired == [2] and len(frame) == 1
    assert frame.iloc[0]["车型"] == "Ford F150, F250"
    assert frame.iloc[0]["ASIN"] == "B000000001"


def seed_tables(project, full):
    for i, name in enumerate(market.TABLES):
        path = project / "output" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        table = full.copy() if not i else full.iloc[::-1].assign(自动尺码=f"STORE-{i}")
        table.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")


def test_run_preserves_original_fields_and_is_idempotent(project, full):
    seed_tables(project, full)
    before = {name: market.read(project / "output" / name) for name in market.TABLES}
    first = market.run(project)
    after = {name: market.read(project / "output" / name) for name in market.TABLES}
    baseline = after[market.BASE_TABLE].set_index("DIMENSION-ID")[market.COLUMN]
    for name, frame in after.items():
        assert frame[before[name].columns].equals(before[name])
        assert frame.columns.get_loc(market.COLUMN) == frame.columns.get_loc("车型销量") + 1
        assert frame.columns[-1] == "TRIM"
        assert frame[market.COLUMN].str.fullmatch(r"\d+\.\d{6}").all()
        pd.testing.assert_series_equal(frame.set_index("DIMENSION-ID")[market.COLUMN].sort_index(), baseline.sort_index())
    hashes = {name: market.sha256(project / "output" / name) for name in market.TABLES}
    second = market.run(project)
    assert first["batch"] != second["batch"]
    assert hashes == {name: market.sha256(project / "output" / name) for name in market.TABLES}
    record = json.loads((Path(second["batch"]) / "run.json").read_text(encoding="utf-8"))
    assert record["status"]["status"] == "passed"
    assert len(record["outputs"]) == 4
    assert (Path(second["batch"]) / "extra/销售匹配依据.csv.gz").is_file()


def test_failed_run_does_not_publish_any_table(project, full):
    seed_tables(project, full)
    broken = project / "output" / market.TABLES[-1]
    full.iloc[:1].to_csv(broken, index=False)
    hashes = {name: market.sha256(project / "output" / name) for name in market.TABLES}
    with pytest.raises(ValueError, match="DIMENSION-ID"):
        market.run(project)
    assert hashes == {name: market.sha256(project / "output" / name) for name in market.TABLES}
    records = list((project / "artifacts").glob("*/run.json"))
    assert json.loads(records[0].read_text(encoding="utf-8"))["status"]["status"] == "failed"
