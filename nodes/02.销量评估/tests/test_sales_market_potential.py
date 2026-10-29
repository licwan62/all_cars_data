from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_market_potential as market


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
    assert market.interval_retention("2021", policy) == 1
    assert market.interval_retention("2011", policy) == .5
    assert market.interval_retention("2030", policy) == 1
    assert market.interval_retention("2011-2021", policy) == pytest.approx(
        np.mean([2 ** (-age / 10) for age in range(11)]))



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



def seed_inputs(project, full):
    dimensions = full[["DIMENSION-ID", "MAKE", "MODEL", "YEAR"]].copy()
    dimensions["DIMENSION-ID"] = ["Toyota Camry Sedan 2021-2026 US", "Toyota Camry Sedan 2026 US", "Ford Focus Sedan 2021 US"]
    dim_path = project / "dimensions.csv"
    dimensions.to_csv(dim_path, index=False)
    path = project / "output/原子销量.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"atom_record_id": dimensions["DIMENSION-ID"] + "|ATOM_YEAR=2026", "预估销量": full["尺寸组销量"]}).to_csv(path,index=False)
    return dim_path


def test_run_is_idempotent_and_preserves_missing(project, full):
    dimensions = seed_inputs(project, full)
    first = market.run(project, dimensions)
    path = project / "output" / market.OUTPUT
    before = path.read_bytes()
    result = market.read(path)
    assert result.columns.tolist() == ["DIMENSION-ID", market.COLUMN, market.ADJUSTMENT]
    assert result[market.ADJUSTMENT].astype(float).ge(0).all()
    second = market.run(project, dimensions)
    assert first["batch"] != second["batch"] and path.read_bytes() == before
    atoms = market.read(project / "output/原子销量.csv")
    atoms.loc[0,"预估销量"] = ""
    atoms.to_csv(project / "output/原子销量.csv", index=False)
    assert market.run(project, dimensions)["missing_atom_sales"] == 1


def test_failed_run_preserves_output(project, full):
    dimensions = seed_inputs(project, full)
    market.run(project, dimensions)
    before = (project / "output" / market.OUTPUT).read_bytes()
    path = project / "data" / market.SALES_DIR / "积加销量.csv"
    frame = market.read(path); frame.loc[0,"ASIN"] = "invalid"; frame.to_csv(path,index=False)
    with pytest.raises(ValueError, match="ASIN"):
        market.run(project, dimensions)
    assert (project / "output" / market.OUTPUT).read_bytes() == before
    records = [json.loads(p.read_text(encoding="utf-8")) for p in (project/"artifacts").glob("*/run.json")]
    assert any(rec["status"]["status"] == "failed" for rec in records)


def test_base_rejects_orphan_duplicate_negative(full):
    dims = full[["DIMENSION-ID","MAKE","MODEL","YEAR"]]
    for rows in [
        [("unknown US|ATOM_YEAR=2026", "1")],
        [("camry-a US|ATOM_YEAR=2026", "-1")],
        [("camry-a US|ATOM_YEAR=2026", "1")]*2,
    ]:
        with pytest.raises(ValueError):
            market.build_base(dims, pd.DataFrame(rows,columns=["atom_record_id","预估销量"]))
