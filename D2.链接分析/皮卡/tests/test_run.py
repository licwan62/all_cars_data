from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run.py"
SPEC = importlib.util.spec_from_file_location("pickup_link_audit", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_year_parser_handles_discontinuous_ranges() -> None:
    assert MODULE.expand_years("Ford F-150 2001-2002/2004-2005") == {2001, 2002, 2004, 2005}


def test_current_workbook_fields_are_supported_by_source_facts() -> None:
    workbook = MODULE.WORKBOOK
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
    workbook = MODULE.WORKBOOK
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
        "SKU_NAME", "PHYSICAL_SKU", "适配车型", "适配年份", "发货数量", "发货日期",
    ]
    assert report["适配车型"].str.contains(r"\|", regex=True).all()
    model_part = report["适配车型"].str.split("|").str[0]
    assert not model_part.str.contains(r"(?<!\d)(?:19|20)\d{2}", regex=True).any()
    assert report["适配年份"].str.match(r"^(?:19|20)\d{2}").all()
    assert report["发货日期"].eq("2026-08-21").all()


def shipment_fixture():
    facts = pd.DataFrame({"SKU_NAME": ["confirmed"], "PHYSICAL_SKU": ["PK-L"],
                          "发货数量": [3], "发货日期": ["2026-08-21"]})
    listing = pd.DataFrame({"SKU_NAME": ["listing"], "PHYSICAL_SKU": ["PK-L"],
                            "CUSUMER_NAME": ["Ford F-150 1997-2026 | Regular | 8.0' Long Bed"]})
    mapping = pd.DataFrame({"SKU_NAME": ["confirmed"], "workbook_sku": ["listing"]})
    return facts, listing, mapping


@pytest.mark.parametrize("date", ["", None, "2026-02-30", "2026-8-21"])
def test_shipment_rejects_missing_or_invalid_dates(date):
    facts, listing, mapping = shipment_fixture()
    facts["发货日期"] = date
    with pytest.raises(ValueError):
        MODULE.sku_shipment_report(facts, listing, mapping)


def test_shipment_preserves_separate_dates_and_rejects_duplicate_records():
    facts, listing, mapping = shipment_fixture()
    later = facts.copy()
    later["发货日期"] = "2026-09-21"
    report = MODULE.sku_shipment_report(pd.concat([facts, later]), listing, mapping)
    assert report["发货数量"].sum() == 6
    assert set(report["发货日期"]) == {"2026-08-21", "2026-09-21"}
    with pytest.raises(ValueError, match="组合必须唯一"):
        MODULE.sku_shipment_report(pd.concat([facts, facts]), listing, mapping)


def test_listing_rules_preserve_drw_exclusions_and_output_contract():
    rules = json.loads((MODULE.PROJECT_DIR / "data/链接字段规则.json").read_text(encoding="utf-8"))
    listing = pd.read_excel(MODULE.WORKBOOK, sheet_name="上架明细").fillna("")
    result = MODULE.apply_listing_overrides(listing, rules).set_index("SKU_NAME")
    assert rules["listing_title_field"] == "TITLE_NAME"
    assert rules["listing_size_name_prefix"] == "Custom Fit "
    assert rules["shipment_output_fields"] == ["SKU_NAME", "发货数量", "发货日期"]
    assert len(rules["listing_overrides"]) == 2
    for sku in rules["listing_overrides"]:
        assert "Excludes" in result.loc[sku, "CUSUMER_NAME"]
        assert "Excl" in result.loc[sku, "SIZE_NAME"]


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


@pytest.mark.parametrize("source,expected", [
    ("Ford F-150 1998-2026 | Regular, SuperCrew | 5.5'-6.5' Short Bed",
     "Ford F-150(1998-2026) Regular Cab/SuperCrew Cab Short Bed(5.5'-6.5')"),
    ("Ram 1500 1994-2026 | Club/Quad | 6.4' Standard Bed | Excludes DRW",
     "Ram 1500(1994-2026) Club Cab/Quad Cab Standard Bed(6.4') Excludes DRW"),
    ("Ford F-100 1967/1973-1979 | Regular | 8.0' Long Bed",
     "Ford F-100(1967/1973-1979) Regular Cab Long Bed(8.0')"),
    ("Ford F-150 2001-2026 | Crew, SuperCab | 6.5'-8.0' Bed",
     "Ford F-150(2001-2026) Crew Cab/SuperCab Bed(6.5'-8.0')"),
])
def test_listing_title_format(source, expected):
    rules = json.loads((MODULE.PROJECT_DIR / "data/链接字段规则.json").read_text(encoding="utf-8"))
    assert MODULE.listing_title(source, rules) == expected


def test_all_listing_titles_preserve_fitment_and_qualifiers():
    rules = json.loads((MODULE.PROJECT_DIR / "data/链接字段规则.json").read_text(encoding="utf-8"))
    source = pd.read_excel(MODULE.WORKBOOK, sheet_name="上架明细").fillna("")
    source = MODULE.apply_listing_overrides(source, rules)
    for value in source["CUSUMER_NAME"]:
        title = MODULE.listing_title(value, rules)
        assert "|" not in title
        assert MODULE.expand_years(title) == MODULE.expand_years(value)
        assert MODULE.bed_lengths(title) == MODULE.bed_lengths(value)
        assert MODULE.cab_terms(title) == MODULE.cab_terms(value)
        for qualifier in value.split("|")[3:]:
            assert qualifier.strip() in title


def test_title_omission_is_specific_and_preserves_source_facts():
    rules = json.loads((MODULE.PROJECT_DIR / "data/链接字段规则.json").read_text(encoding="utf-8"))
    sku = "CHEV_SILVERADO1500_CREW_B58_Y04-26_EXCL-TRAILBOSS_PK-L"
    source = "Chevrolet Silverado 1500 2004-2026 | Crew | 5.8' Short Bed | Excludes 2021-2026 Trail Boss"
    title = MODULE.listing_title(source, rules, sku)
    assert title == "Chevrolet Silverado 1500(2004-2026) Crew Cab Short Bed(5.8')"
    assert "Excludes" in MODULE.listing_title(source, rules, "other-sku")
    with pytest.raises(ValueError, match="未命中来源限定条件"):
        MODULE.listing_title(source.split(" | Excludes")[0], rules, sku)
    raptor = "Ford F-150 2021-2026 | SuperCrew | 5.5' Short Bed | Excludes 2021-2026 Raptor"
    assert "Excludes 2021-2026 Raptor" in MODULE.listing_title(raptor, rules, "FORD_F-150_SUPERCREW_B55_Y21-26_EXCL-RAPTOR_PK-L")


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


def gray_compatibility_fixture():
    rules = json.loads((MODULE.PROJECT_DIR / "data/链接字段规则.json").read_text(encoding="utf-8"))
    source = pd.read_excel(MODULE.WORKBOOK, sheet_name="上架明细").fillna("")
    source = MODULE.apply_listing_overrides(source, rules)
    source = MODULE.update_physical_sku(source, MODULE.load_physical_sku_mapping())
    source["适配年份"] = source["适配车型"].map(MODULE.year_text)
    source["适配车型"] = source["适配车型"].map(MODULE.model_text)
    dimensions = pd.read_csv(MODULE.US_FULL_TABLE, encoding="utf-8-sig")
    return source, dimensions, rules


def test_gray_compatibility_adds_only_approved_years_and_keeps_sku_facts():
    source, dimensions, rules = gray_compatibility_fixture()
    result = MODULE.apply_gray_compatibility(source, dimensions, rules)
    sku = next(iter(rules["gray_compatibility"]))
    mask = result["SKU_NAME"].eq(sku)
    assert result.loc[mask, "适配年份"].item() == "2001-2026"
    assert "2001-2026" in result.loc[mask, "CUSUMER_NAME"].item()
    assert result.loc[mask, "PHYSICAL_SKU"].item() == "PK-XXL-680"
    pd.testing.assert_frame_equal(result.loc[~mask], source.loc[~mask])
    pd.testing.assert_series_equal(result["SKU_NAME"], source["SKU_NAME"])
    pd.testing.assert_series_equal(result["PHYSICAL_SKU"], source["PHYSICAL_SKU"])


@pytest.mark.parametrize("length", [6300, 6801])
def test_gray_compatibility_rejects_clearance_boundary_and_undersized_cover(length):
    source, dimensions, rules = gray_compatibility_fixture()
    adjustment = next(iter(rules["gray_compatibility"].values()))
    dimensions.loc[dimensions["DIMENSION-ID"].isin(adjustment["dimension_ids"]), "L-MM"] = length
    with pytest.raises(ValueError, match="长度余量"):
        MODULE.apply_gray_compatibility(source, dimensions, rules)


def test_gray_compatibility_rejects_changed_cab_or_missing_years():
    source, dimensions, rules = gray_compatibility_fixture()
    adjustment = next(iter(rules["gray_compatibility"].values()))
    mask = dimensions["DIMENSION-ID"].isin(adjustment["dimension_ids"])
    changed_cab = dimensions.copy()
    changed_cab.loc[mask, "CAB"] = "Regular"
    with pytest.raises(ValueError, match="驾驶室或货斗"):
        MODULE.apply_gray_compatibility(source, changed_cab, rules)
    dimensions.loc[mask, "YEAR"] = "2015-2018"
    with pytest.raises(ValueError, match="不支持新增年份"):
        MODULE.apply_gray_compatibility(source, dimensions, rules)
