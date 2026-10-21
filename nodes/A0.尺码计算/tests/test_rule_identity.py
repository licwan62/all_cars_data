from __future__ import annotations

import pandas as pd

import generate_ru_full_table as ru
import generate_store_outputs as store_outputs
import pandas_analysis as analysis
from rule_identity import RULE_ID_COLUMN, rule_id, rule_ids

PARAMETERS = pd.DataFrame([{"参数": "余量长容差", "值": "500"}])


def test_rule_id_is_content_based_and_ignores_notes_and_number_format():
    columns = ["尺码", "分类", "长上限", "备注"]
    base = {"尺码": "2L", "分类": "两厢车", "长上限": "4140", "备注": "旧说明"}
    same = {"尺码": " 2L ", "分类": "两厢车", "长上限": 4140.0, "备注": "新说明"}
    other = {"尺码": "2L", "分类": "两厢车", "长上限": "4141", "备注": "旧说明"}
    assert rule_id(base, columns) == rule_id(same, columns)
    assert rule_id(base, columns) != rule_id(other, columns)
    assert rule_id(base, columns).startswith("R") and len(rule_id(base, columns)) == 11


def test_rule_ids_do_not_depend_on_row_order():
    rules = pd.DataFrame([
        {"尺码": "2M", "分类": "两厢车", "长上限": 3610},
        {"尺码": "2L", "分类": "两厢车", "长上限": 4140},
    ])
    forward = dict(zip(rules["尺码"], rule_ids(rules)))
    reversed_rules = rules.iloc[::-1].reset_index(drop=True)
    assert dict(zip(reversed_rules["尺码"], rule_ids(reversed_rules))) == forward


def test_matcher_reports_the_rule_that_produced_the_size():
    rules = pd.DataFrame([
        {"尺码": "SMALL", "分类": "两厢车|三厢车", "尺码池": "", "长上限": 4600, "插片指数上限": 999, "车型白名单": ""},
        {"尺码": "LARGE", "分类": "两厢车", "尺码池": "", "长上限": 5000, "插片指数上限": 999, "车型白名单": ""},
    ])
    ids = dict(zip(rules["尺码"], rule_ids(rules)))
    vehicles = pd.DataFrame([
        {"MAKE": "A", "MODEL": "B", "YEAR": "2020", "结构": "Hatchback", "分类": "两厢车", "CAB": "", "版本": "", "L-MM": 4500, "插片指数": 0},
        {"MAKE": "A", "MODEL": "C", "YEAR": "2020", "结构": "Sedan", "分类": "三厢车", "CAB": "", "版本": "", "L-MM": 4300, "插片指数": 0},
        {"MAKE": "A", "MODEL": "D", "YEAR": "2020", "结构": "Hatchback", "分类": "两厢车", "CAB": "", "版本": "", "L-MM": 4800, "插片指数": 0},
        {"MAKE": "A", "MODEL": "E", "YEAR": "2020", "结构": "Hatchback", "分类": "两厢车", "CAB": "", "版本": "", "L-MM": 5600, "插片指数": 0},
    ])
    result = analysis.SizeMatcher(PARAMETERS, rules).apply(vehicles)
    assert result["自动尺码"].tolist() == ["SMALL", "SMALL", "LARGE", "无可用尺码"]
    # 按分类展开的同一规则行（两厢车|三厢车）得到同一个规则ID；未匹配为空
    assert result[RULE_ID_COLUMN].tolist() == [ids["SMALL"], ids["SMALL"], ids["LARGE"], ""]


def test_store_table_keeps_match_size_before_shipping_mapping():
    source = pd.DataFrame([
        {"自动尺码": "3XXL-550", "候选": "", "相差数值": "", RULE_ID_COLUMN: "Rabc", "TRIM": ""},
        {"自动尺码": "无可用尺码", "候选": "4XL", "相差数值": "12", RULE_ID_COLUMN: "", "TRIM": ""},
    ])
    result = store_outputs.apply_shipping_sizes(source, [("3XXL-550", "4XL-0"), ("4XL", "4XL-0")])
    assert result["自动尺码"].tolist() == ["4XL-0", "无可用尺码"]
    assert result[store_outputs.MATCH_SIZE_COLUMN].tolist() == ["3XXL-550", "无可用尺码"]
    assert list(result.columns) == ["自动尺码", "候选", "相差数值", "匹配尺码", RULE_ID_COLUMN, "TRIM"]


def test_ru_matching_reports_rule_id(tmp_path):
    path = tmp_path / "rules.csv"
    pd.DataFrame([
        {"亚马逊尺码": "S", "OZON尺码": "S", "发货尺码": "S", "分类": "两厢车", "长_mm": 4000, "宽_mm": 1800, "高_mm": 1600, "余量长上限_mm": 600},
        {"亚马逊尺码": "L", "OZON尺码": "L", "发货尺码": "L", "分类": "两厢车", "长_mm": 4600, "宽_mm": 1900, "高_mm": 1700, "余量长上限_mm": 600},
    ]).to_csv(path, index=False, encoding="utf-8-sig")
    rules = ru.read_rules(path)
    expected = dict(zip(rules["亚马逊尺码"], rules[RULE_ID_COLUMN]))
    assert expected == dict(zip(["S", "L"], rule_ids(analysis._read_csv(path))))
    vehicles = pd.DataFrame([
        {"分类": "两厢车", "L-MM": 3900, "W-MM": 1700, "H-MM": 1500},
        {"分类": "两厢车", "L-MM": 4500, "W-MM": 1850, "H-MM": 1650},
        {"分类": "两厢车", "L-MM": 4900, "W-MM": 1850, "H-MM": 1650},
    ])
    matched = ru.match_ru_sizes(vehicles, rules, {"余量长容差": 600})
    assert matched[RULE_ID_COLUMN].tolist() == [expected["S"], expected["L"], ""]
