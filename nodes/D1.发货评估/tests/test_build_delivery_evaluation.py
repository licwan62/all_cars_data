from pathlib import Path
import importlib.util

import pandas as pd


SPEC = importlib.util.spec_from_file_location(
    "delivery_evaluation", Path(__file__).resolve().parents[1] / "code" / "build_delivery_evaluation.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_classification_is_exclusive_and_w_size_takes_priority():
    frame = pd.DataFrame({"自动尺码": ["4L-0", "PK-M", "YL"], "分类": ["皮卡", "皮卡", "越野车"]})
    config = {"classification": {"w_size_prefix": "4", "pickup_category": "皮卡"}}
    assert MODULE.classify_rows(frame, config).tolist() == ["W型车", "皮卡", "普通车"]


def test_custom_flag_uses_make_model_and_accepts_list_qualifiers():
    evaluations = pd.DataFrame([
        {"MAKE": "Ford", "MODEL": "Bronco"},
        {"MAKE": "Ford", "MODEL": "Bronco Sport"},
        {"MAKE": "Chevrolet", "MODEL": "Corvette"},
        {"MAKE": "MINI", "MODEL": "Countryman"},
        {"MAKE": "Land Rover", "MODEL": "Range Rover"},
        {"MAKE": "Land Rover", "MODEL": "Range Rover Sport"},
    ])
    custom_models = pd.DataFrame({"车型": [
        "Ford Bronco 2dr", "Ford Bronco 4dr", "Chevrolet Corvette C8", "MINI Countryman",
        "Land Rover Range Rover Sport",
    ]})
    result = MODULE.add_custom_flag(evaluations, custom_models)
    assert result["定制标记"].tolist() == ["是", "否", "是", "是", "否", "是"]


def test_review_requires_year_and_size_for_exact_match():
    evaluations = pd.DataFrame([
        {"MAKE": "Ford", "MODEL": "X", "结构": "SUV", "YEAR": "2020-2022",
         "原始自动尺码": "YL", "供货尺码": "YL"},
        {"MAKE": "Ford", "MODEL": "X", "结构": "SUV", "YEAR": "2010-2012",
         "原始自动尺码": "YM", "供货尺码": "YM"},
    ])
    reviews = pd.DataFrame([
        {"品牌": "Ford", "车型": "X", "结构": "SUV", "尺码": "YL", "年份": "2021",
         "差评数量": "3", "主要差评原因": "太小", "严重度评级": "中", "备注": "核对"},
    ])
    result = MODULE.match_reviews(evaluations, reviews)
    assert result["差评匹配方式"].tolist() == ["精确匹配", "模糊匹配"]
    assert result.loc[1, "差评模糊原因"] == "年代未命中；尺码未命中；仅按品牌+车型关联"


def test_missing_review_year_is_fuzzy_even_when_size_matches():
    evaluations = pd.DataFrame([
        {"MAKE": "Ford", "MODEL": "X", "结构": "SUV", "YEAR": "2020-2022",
         "原始自动尺码": "YL", "供货尺码": "YL"},
    ])
    reviews = pd.DataFrame([
        {"品牌": "Ford", "车型": "X", "结构": "SUV", "尺码": "YL", "年份": "",
         "差评数量": "2", "主要差评原因": "偏大", "严重度评级": "低", "备注": ""},
    ])
    result = MODULE.match_reviews(evaluations, reviews)
    assert result.loc[0, "差评标记"] == "是"
    assert result.loc[0, "差评匹配方式"] == "模糊匹配"
    assert "缺少年代" in result.loc[0, "差评模糊原因"]


def test_review_structure_matches_one_of_aggregated_sku_structures():
    assert MODULE._structure_matches("SUV", "Hatchback；SUV")
    assert not MODULE._structure_matches("Sedan", "Hatchback；SUV")


def test_review_inference_uses_model_and_exact_dimensions_without_overwriting_exact_match():
    review_values = {
        "差评标记": "是", "差评数": 3, "差评严重度": "中", "差评原因": "太小",
        "差评备注": "核对", "差评年份": "2021", "差评尺码": "YL", "差评模糊原因": "",
        "差评推理原因": "", "差评推理键": "", "差评推理来源": "",
    }
    evaluations = pd.DataFrame([
        {"SKU": "S1", "差评匹配方式": "精确匹配", **review_values},
        {"SKU": "S2", "差评匹配方式": "模糊匹配", **review_values},
        {"SKU": "S3", "差评匹配方式": "模糊匹配", **review_values},
    ])
    detail = pd.DataFrame([
        {"SKU": "S1", "MODEL": "X", "L-MM": 4500, "W-MM": 1800, "H-MM": 1600,
         "差评匹配方式": "精确匹配", **review_values},
        {"SKU": "S2", "MODEL": "x", "L-MM": 4500, "W-MM": 1800, "H-MM": 1600,
         "差评匹配方式": "模糊匹配", **review_values},
        {"SKU": "S3", "MODEL": "X", "L-MM": 4500, "W-MM": 1801, "H-MM": 1600,
         "差评匹配方式": "模糊匹配", **review_values},
    ])
    policy = {
        "enabled": True,
        "key_fields": ["MODEL", "L-MM", "W-MM", "H-MM"],
        "seed_match_methods": ["精确匹配"],
        "protected_match_methods": ["精确匹配"],
        "target_match_method": "推理匹配",
    }
    inferred_detail, inferred_evaluations, status = MODULE.propagate_review_inference(
        detail, evaluations, policy
    )
    assert inferred_detail["差评匹配方式"].tolist() == ["精确匹配", "推理匹配", "模糊匹配"]
    assert inferred_evaluations["差评匹配方式"].tolist() == ["精确匹配", "推理匹配", "模糊匹配"]
    assert inferred_detail.loc[1, "差评推理键"] == "x|4500|1800|1600"
    assert inferred_detail.loc[1, "差评推理来源"] == "S1"
    assert status == {"detail_rows": 1, "evaluation_rows": 1, "keys": 1}


def test_market_retention_keeps_future_year_at_full_weight():
    policy = {"evaluation_year": 2026, "full_weight_years": 5, "half_life_years": 10}
    assert MODULE.interval_retention("2027", policy) == 1.0
    assert round(MODULE.interval_retention("2011", policy), 3) == 0.5


def test_build_evaluations_uses_sku_grain_and_preserves_every_dimension_id():
    frame = pd.DataFrame([
        {"评估类别": "普通车", "MAKE": "A", "MODEL": "B", "版本": "Base", "结构": "SUV", "CAB": "", "BED": "",
         "供货尺码": "YL", "起始年": 2020, "结束年": 2020, "DIMENSION-ID": "ID1", "代际": "g1", "SHAPE": "SUV",
         "YEAR": "2020", "自动尺码": "YL", "L-MM": 4500, "W-MM": 1800, "H-MM": 1600, "尺寸组销量": 10,
         "年份留存系数": 1.0, "市场潜力值": 10.0, "灰度调整": False, "灰度组ID": ""},
        {"评估类别": "普通车", "MAKE": "A", "MODEL": "B", "版本": "Sport", "结构": "Hatchback", "CAB": "Crew", "BED": "5.5",
         "供货尺码": "YL", "起始年": 2021, "结束年": 2021, "DIMENSION-ID": "ID2", "代际": "g1", "SHAPE": "SUV",
         "YEAR": "2021", "自动尺码": "YL", "L-MM": 4510, "W-MM": 1810, "H-MM": 1605, "尺寸组销量": 20,
         "年份留存系数": 1.0, "市场潜力值": 20.0, "灰度调整": False, "灰度组ID": ""},
    ])
    evaluations, detail = MODULE.build_evaluations(frame)
    assert len(evaluations) == 1
    assert set(detail["DIMENSION-ID"]) == {"ID1", "ID2"}
    assert detail["SKU"].nunique() == 1
    assert evaluations.loc[0, "YEAR"] == "2020-2021"
    assert evaluations.loc[0, "版本"] == "Base；Sport"
    assert evaluations.loc[0, "结构"] == "Hatchback；SUV"
    assert evaluations.loc[0, "市场潜力值"] == 30


def test_business_output_merges_review_trace_and_drops_nonpickup_fields():
    frame = pd.DataFrame([{
        "差评备注": "车型已匹配全量表 MAKE=A MODEL=B；原备注", "差评模糊原因": "年代未命中；仅按品牌+车型关联", "差评推理原因": "同尺寸",
        "差评推理键": "x|1|2|3", "差评推理来源": "SHIP-1", "DIMENSION-ID": "ID1",
        "DIMENSION-ID数量": 1, "CAB": "Crew", "BED": "5.5",
    }])
    policy = {
        "merge_review_fields_into_notes": {
            "差评模糊原因": "模糊原因", "差评推理原因": "推理原因",
            "差评推理键": "推理键", "差评推理来源": "推理来源",
        },
        "drop_from_business_outputs": ["DIMENSION-ID", "DIMENSION-ID数量"],
        "drop_from_nonpickup_category_outputs": ["CAB", "BED"],
    }
    result = MODULE.format_business_output(frame, policy, category="普通车")
    assert result.columns.tolist() == ["差评备注"]
    assert result.loc[0, "差评备注"] == (
        "原备注；匹配：年份不符/仅车型；推理：同车型同尺寸；源：SHIP-1"
    )


def test_business_output_removes_merge_provenance_from_review_note():
    frame = pd.DataFrame([{
        "差评备注": "已从'未识别/X/未知'归并（语义明确可识别品牌/车型）",
        "差评模糊原因": "差评记录缺少年代；尺码未命中", "差评推理原因": "",
        "差评推理键": "", "差评推理来源": "",
    }])
    policy = {
        "merge_review_fields_into_notes": {
            "差评模糊原因": "模糊原因", "差评推理原因": "推理原因",
            "差评推理键": "推理键", "差评推理来源": "推理来源",
        },
        "drop_from_business_outputs": [],
        "drop_from_nonpickup_category_outputs": [],
    }
    result = MODULE.format_business_output(frame, policy)
    assert result.loc[0, "差评备注"] == "匹配：缺年份/尺码不符"


def test_business_column_order_matches_contract():
    expected = [
        "MAKE", "MODEL", "版本", "CAB", "BED", "YEAR", "结构", "评估类别", "定制标记", "代际",
        "供货尺码", "最小长-MM", "最大长-MM", "最小宽-MM", "最大宽-MM", "最小高-MM", "最大高-MM",
        "年份留存系数", "调整后市场潜力值", "市场潜力值", "市场调整增加值", "积加月销量估计", "全局市场潜力排名", "尺寸组销量合计", "类别市场潜力排名",
        "原始自动尺码", "灰度调整记录数", "灰度组ID", "差评标记", "差评数", "差评匹配方式",
        "差评年份", "差评尺码", "差评严重度", "差评原因", "差评备注",
    ]
    assert [column for column in MODULE.EVALUATION_COLUMNS if not column.startswith("差评推理") and column != "差评模糊原因"] == expected


def test_pickup_output_keeps_cab_and_bed_but_drops_dimension_ids():
    frame = pd.DataFrame([{
        "差评备注": "", "差评模糊原因": "", "差评推理原因": "",
        "差评推理键": "", "差评推理来源": "", "DIMENSION-ID": "ID1",
        "DIMENSION-ID数量": 1, "CAB": "Crew", "BED": "5.5",
    }])
    policy = {
        "merge_review_fields_into_notes": {
            "差评模糊原因": "模糊原因", "差评推理原因": "推理原因",
            "差评推理键": "推理键", "差评推理来源": "推理来源",
        },
        "drop_from_business_outputs": ["DIMENSION-ID", "DIMENSION-ID数量"],
        "drop_from_nonpickup_category_outputs": ["CAB", "BED"],
    }
    result = MODULE.format_business_output(frame, policy, category="皮卡")
    assert result.columns.tolist() == ["差评备注", "CAB", "BED"]


def test_identity_mapping_preserves_every_dimension_id():
    detail = pd.DataFrame([
        {"DIMENSION-ID": "ID2", "SKU": "S2", "评估类别": "普通车", "灰度组ID": "", "灰度调整": False},
        {"DIMENSION-ID": "ID1", "SKU": "S1", "评估类别": "皮卡", "灰度组ID": "G1", "灰度调整": True},
    ])
    evaluations = pd.DataFrame([
        {"SKU": "S1", "MAKE": "A", "MODEL": "B", "YEAR": "2020", "供货尺码": "PK-M"},
        {"SKU": "S2", "MAKE": "C", "MODEL": "D", "YEAR": "2021", "供货尺码": "YL"},
    ])
    result = MODULE.build_identity_mapping(detail, evaluations)
    assert result["DIMENSION-ID"].tolist() == ["ID1", "ID2"]
    assert result.columns.tolist() == MODULE.IDENTITY_COLUMNS


def test_review_flag_uses_dimension_priority_then_quality_then_none():
    frame = pd.DataFrame([
        {"差评数": 2, "差评原因": "质量差(1)；尺寸偏小(1)"},
        {"差评数": 1, "差评原因": "拉链断裂(1)"},
        {"差评数": 0, "差评原因": ""},
        {"差评数": 1, "差评原因": "/(1)"},
    ])
    policy = {
        "dimension_label": "尺寸", "quality_label": "质量", "none_label": "无",
        "dimension_keywords": ["尺寸", "偏小"], "empty_reason_tokens": ["/"],
    }
    result = MODULE.classify_review_flags(frame, policy)
    assert result["差评标记"].tolist() == ["尺寸", "质量", "无", "无"]


def test_sales_adjustment_conserves_sales_and_boosts_only_gap():
    evaluations = pd.DataFrame([
        {"MAKE": "Toyota", "MODEL": "Camry", "市场潜力值": 1.0},
        {"MAKE": "Toyota", "MODEL": "Camry", "市场潜力值": 3.0},
        {"MAKE": "Ford", "MODEL": "Focus", "市场潜力值": 100.0},
    ])
    sales = pd.DataFrame([
        {"车型": "Toyota Camry", "ASIN": "A", "7天销量": 7, "15天销量": 15, "30天销量": 30},
        {"车型": "未匹配/通用款", "ASIN": "B", "7天销量": 7, "15天销量": 15, "30天销量": 30},
    ])
    policy = {"monthly_weights": [0.2, 0.3, 0.5], "confidence_units": 10, "score_per_monthly_unit": 1}
    result, audit = MODULE.adjust_market(evaluations, sales, policy)
    assert abs(result["积加月销量估计"].sum() - 30) < 1e-9
    assert abs(result["市场调整增加值"].sum() - 18.5) < 1e-9
    assert result.loc[2, "调整后市场潜力值"] == 100
    assert audit.loc[1, "匹配状态"] == "待审核"
    sales.loc[1, "ASIN"] = "A"
    import pytest
    with pytest.raises(ValueError, match="ASIN"):
        MODULE.adjust_market(evaluations, sales, policy)
