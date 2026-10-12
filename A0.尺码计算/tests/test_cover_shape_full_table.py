from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas_analysis as analysis

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
from cover_shape_contract import SHAPE_FIELDS, FULL_TABLE_SHAPE_FIELDS, attach_cover_shape


def shapes():
    return pd.DataFrame([{"DIMENSION-ID": "same US", "COUNTRY": "US", "SHAPE": "LOW_FASTBACK", "SHAPE_STATUS": "INFERRED", "SHAPE_YEAR": "1974",
                          "SHAPE_METHOD": "fixture", "SHAPE_ALTERNATES": "[]", "SHAPE_SOURCE": '["fixture:a"]'},
                         {"DIMENSION-ID": "same EU", "COUNTRY": "EU", "SHAPE": "STANDARD_SEDAN", "SHAPE_STATUS": "INFERRED", "SHAPE_YEAR": "2025",
                          "SHAPE_METHOD": "fixture", "SHAPE_ALTERNATES": "[]", "SHAPE_SOURCE": '["fixture:b"]'}])


def test_shape_enrichment_preserves_old_data_order_and_trim():
    frame = pd.DataFrame([{"DIMENSION-ID": "same US", "车形": "SD0", "自动尺码": "S", "TRIM": "A"}])
    result = attach_cover_shape(frame, shapes(), "US")
    assert result[frame.columns].equals(frame)
    assert result.loc[0, "SHAPE"] == "LOW_FASTBACK"
    assert result.columns[0] == "DIMENSION-ID" and result.columns[-1] == "TRIM"
    assert list(result.columns[2:3]) == FULL_TABLE_SHAPE_FIELDS
    assert not (set(SHAPE_FIELDS) - {"SHAPE"}) & set(result.columns)
    assert attach_cover_shape(result, shapes(), "US").equals(result)


def test_previous_metadata_columns_are_removed_from_full_table_only():
    frame = pd.DataFrame([{"DIMENSION-ID": "same US", "车形": "SD0", "SHAPE": "STANDARD_SEDAN",
                           "SHAPE_STATUS": "INFERRED", "SHAPE_YEAR": "1974", "SHAPE_METHOD": "old",
                           "SHAPE_ALTERNATES": "[]", "SHAPE_SOURCE": "old", "TRIM": "A"}])
    source = shapes()
    before = source.copy(deep=True)
    result = attach_cover_shape(frame, source, "US")
    assert list(result.columns) == ["DIMENSION-ID", "车形", "SHAPE", "TRIM"]
    assert result.loc[0, "SHAPE"] == "LOW_FASTBACK" and source.equals(before)


def test_regional_base_id_does_not_cross_market():
    frame = pd.DataFrame([{"DIMENSION-ID": "same", "车形": "SD1", "相差数值": ""}])
    result = attach_cover_shape(frame, shapes(), "EU")
    assert result.loc[0, "SHAPE"] == "STANDARD_SEDAN"
    assert result.loc[0, "DIMENSION-ID"] == "same" and result.columns[-1] == "相差数值"


def test_unmatched_duplicate_or_blank_shape_rejected():
    frame = pd.DataFrame([{"DIMENSION-ID": "same US", "车形": "SD0"}])
    with pytest.raises(ValueError): attach_cover_shape(pd.DataFrame([{"DIMENSION-ID": "missing US"}]), shapes(), "US")
    with pytest.raises(ValueError): attach_cover_shape(frame, pd.concat([shapes(), shapes()]), "US")
    bad = shapes(); bad.loc[0, "SHAPE"] = ""
    with pytest.raises(ValueError): attach_cover_shape(frame, bad, "US")


def test_explicit_sales_id_extension_preserves_sales_and_market():
    source = pd.DataFrame([{"DIMENSION-ID": "old US", "尺寸组销量": 123}, {"DIMENSION-ID": "old EU", "尺寸组销量": 45}])
    migration = pd.DataFrame([{"COUNTRY": "US", "旧DIMENSION-ID": "old US", "新DIMENSION-ID": "new US", "理由": "fixture extension"}])
    result = analysis.apply_sales_id_migrations(source, ["new US", "old EU"], migration)
    assert result["DIMENSION-ID"].tolist() == ["new US", "old EU"] and result["尺寸组销量"].sum() == 168
    assert source["DIMENSION-ID"].tolist() == ["old US", "old EU"]
    duplicate = pd.concat([source, pd.DataFrame([{"DIMENSION-ID": "new US", "尺寸组销量": 7}])])
    with pytest.raises(analysis.DataContractError): analysis.apply_sales_id_migrations(duplicate, ["new US"], migration)
