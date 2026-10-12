from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


MODULE_PATH = Path(__file__).resolve().parents[1] / "run.py"
SPEC = importlib.util.spec_from_file_location("pickup_link_audit", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_year_parser_handles_discontinuous_ranges() -> None:
    assert MODULE.expand_years("Ford F-150 2001-2002/2004-2005") == {2001, 2002, 2004, 2005}


def test_current_workbook_fields_are_supported_by_source_facts() -> None:
    workbook = Path(__file__).resolve().parents[2] / "data" / "发货单明细.xlsx"
    final = pd.read_excel(workbook, sheet_name="上架明细").fillna("")
    detail = pd.read_excel(workbook, sheet_name="ref_cluster_detail").fillna("")
    audit = pd.DataFrame([MODULE.audit_row(row, detail) for _, row in final.iterrows()])
    assert len(audit) == 108
    assert (audit["校验结论"] == "通过").all()
    assert not audit["适配车型"].str.contains(r"(?<!\d)(?:19|20)\d{2}", regex=True).any()
    assert audit["适配年份"].str.match(r"^(?:19|20)\d{2}").all()
    assert final["SKU_NAME"].is_unique


def test_split_fitment_separates_vehicle_and_years() -> None:
    assert MODULE.split_fitment("Ford F-150 2001-2002/2004-2020") == (
        "Ford F-150", "2001-2002/2004-2020",
    )


def test_sku_shipment_report_uses_confirmed_sku_facts_without_cluster() -> None:
    workbook = Path(__file__).resolve().parents[2] / "data" / "发货单明细.xlsx"
    project = Path(__file__).resolve().parents[1]
    listing = pd.read_excel(workbook, sheet_name="上架明细").fillna("")
    facts = pd.read_csv(project / "data" / "发货事实.csv", encoding="utf-8-sig")
    mapping = pd.read_csv(project / "data" / "SKU上架映射.csv", encoding="utf-8-sig")
    report = MODULE.sku_shipment_report(facts, listing, mapping)
    assert len(report) == 108
    assert report["SKU_NAME"].is_unique
    assert report["发货数量"].sum() == 801
    assert (report["发货数量"] > 0).all()
    assert list(report.columns) == [
        "SKU_NAME", "PHYSICAL_SKU", "适配车型", "适配年份", "发货数量",
    ]
    assert report["适配车型"].str.contains(r"\|", regex=True).all()
    model_part = report["适配车型"].str.split("|").str[0]
    assert not model_part.str.contains(r"(?<!\d)(?:19|20)\d{2}", regex=True).any()
    assert report["适配年份"].str.match(r"^(?:19|20)\d{2}").all()


def test_physical_sku_mapping_uses_latest_pickup_names_without_changing_facts() -> None:
    mapping = MODULE.load_physical_sku_mapping()
    assert mapping == {
        "PK-M": "PK-S",
        "PK-M+": "PK-M",
        "PK-L": "PK-L",
        "PK-XL": "PK-XL",
        "PK-XXL": "PK-XXL-645",
        "PK-XXXL": "PK-XXL-680",
    }
    source = pd.DataFrame({
        "PHYSICAL_SKU": list(mapping),
        "CLUSTER_ID": list(range(6)),
        "发货数量": [1, 2, 3, 4, 5, 6],
    })
    updated = MODULE.update_physical_sku(source, mapping)
    assert updated["PHYSICAL_SKU"].tolist() == list(mapping.values())
    pd.testing.assert_frame_equal(
        updated.drop(columns="PHYSICAL_SKU"),
        source.drop(columns="PHYSICAL_SKU"),
    )


def test_us_size_extremes_are_derived_from_current_automatic_sku() -> None:
    us_full_table = pd.read_csv(MODULE.US_FULL_TABLE, encoding="utf-8-sig")
    skus = ["PK-S", "PK-M", "PK-L", "PK-XL", "PK-XXL-645", "PK-XXL-680"]
    audit = pd.DataFrame({"PHYSICAL_SKU": skus})
    result = MODULE.add_us_size_extremes(audit, us_full_table)
    assert result[["最长-MM", "最宽-MM", "最高-MM"]].values.tolist() == [
        [5291, 2032, 1918],
        [5624, 2395, 2078],
        [5895, 2438, 2075],
        [6200, 2395, 2080],
        [6414, 2395, 2073],
        [6777, 2459, 2075],
    ]
