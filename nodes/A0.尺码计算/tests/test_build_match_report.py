import pandas as pd

import build_match_report as report
import build_regional_coverage_full as coverage
import data_layout
import output_layout as layout


def test_shelf_rows_flatten_all_stores():
    rows = report.shelf_rows()
    assert {row[0] for row in rows} >= {"HNT", "TM", "TM_拆分"}
    assert all(len(row) == 3 and all(row) for row in rows)
    assert not any(row[1] == "2L+" or row[2] == "2L+" for row in rows)


def test_region_sources_use_each_regions_own_rules():
    assert report.region_sources("US")["规则"][0] == data_layout.us_rules()
    assert report.region_sources("EU")["规则"][0] == coverage.EU_CONFIG.rules == data_layout.current("EU").rules
    assert report.region_sources("RU")["规则"] == (data_layout.current("RU").rules, "亚马逊尺码")
    for region in layout.REGIONS:
        assert all(path.is_file() for path, _ in report.region_sources(region).values())


def test_output_layout_groups_by_region_then_kind():
    assert layout.full_table("EU") == "EU/全量/全量表.csv"
    assert layout.match_report("RU") == "RU/尺码匹配报告.md"
    assert layout.store_table("TM_拆分") == "US/店铺/店铺全量_TM_拆分.csv"
    assert layout.TRIM_ADAPTER == "US/TRIM/TRIM适配器.csv"


def test_size_order_follows_rules_and_puts_unmatched_last():
    sizes = pd.Series(["无可用尺码", "3L", "2M", "X", "数据不全"])
    assert report.size_order(sizes, ["2M", "3L"]) == ["2M", "3L", "X", "无可用尺码", "数据不全"]


def test_us_rules_use_2l_without_custom_sizes():
    rules = report.read_csv(data_layout.us_rules())
    assert rules["尺码"].eq("2L").sum() == 1
    assert not rules["尺码"].eq("2L+").any()
    assert "模式" not in rules.columns or not rules["模式"].eq("定制").any()


def test_current_config_resolves_each_region_and_rejects_missing_files(tmp_path):
    for region in layout.REGIONS:
        config = data_layout.current(region)
        assert config.rules.is_file() and config.parameters.is_file() and config.size_column
    broken = tmp_path / "当前规则.yaml"
    broken.write_text("US:\n  规则: 不存在.csv\n  尺码字段: 尺码\n  参数: 不存在.csv\n", encoding="utf-8")
    import pytest

    with pytest.raises(FileNotFoundError):
        data_layout.current("US", broken)
    with pytest.raises(ValueError, match="EU"):
        data_layout.current("EU", broken)


def test_report_explains_matching_rules_with_current_parameters():
    text = report.build_report("US", report.OUTPUT)
    section = text.split("## 尺码规则", 1)[1]
    for heading in ("### 计算量", "### 候选池", "### 选码", "### 店铺发货尺码", "### 规则表", "### 参数"):
        assert heading in section
    tolerance = report.parameter_value(report.read_csv(report.region_sources("US")["参数"][0]), "余量长容差")
    assert f"余量长容差 **{tolerance} mm**" in section
    ru = report.build_report("RU", report.OUTPUT).split("## 尺码规则", 1)[1]
    assert "包络体积最小" in ru and "### 选码" not in ru


def _md_table_after(text, heading):
    """按网站旧解析方式读取报告中 heading 之后的第一张表（逐格 strip、反转义竖线）。"""
    import re

    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading))
    table = []
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        if line.startswith("|"):
            table.append(line)
        elif table:
            break
    split = re.compile(r"(?<!\\)\|")
    cells = lambda line: [part.strip().replace("\\|", "|") for part in split.split(line.strip())[1:-1]]  # noqa: E731
    headers = cells(table[0])
    return headers, [dict(zip(headers, cells(line))) for line in table[2:]]


def _normalized(value):
    return str(value).replace("\n", " ").strip()


def test_size_rules_json_matches_report_rule_table_and_tolerance():
    for region in layout.REGIONS:
        payload = report.size_rules_payload(region)
        text = report.build_report(region, report.OUTPUT)
        headers, rows = _md_table_after(text, "### 规则表")
        assert payload["headers"] == headers
        assert [{k: _normalized(v) for k, v in row.items()} for row in payload["rules"]] == rows
        assert payload["rule_id_column"] == "规则ID" and all(row["规则ID"] for row in payload["rules"])
        assert f"余量长容差 {'**' if region != 'RU' else ''}{payload['length_tolerance_mm']:g} mm" in text
        assert payload["rules_file"].startswith("data/") and len(payload["rules_sha256"]) == 64
        assert payload["length_unit"] == "mm"


def test_shelf_json_matches_report_shelf_table():
    payload = report.shelf_payload()
    _, rows = _md_table_after(report.build_report("US", report.OUTPUT), "### 店铺货架")
    flattened = [{"店铺": store, **item} for store, items in payload["stores"].items() for item in items]
    assert flattened == rows
    assert payload["source_file"] == "data/US/店铺/货架.yaml"


def test_size_code_map_is_published_verbatim_with_lf(tmp_path):
    data = report.size_code_map_bytes()
    assert b"\r\n" not in data
    assert data == data_layout.SIZE_CODE_MAP.read_bytes().replace(b"\r\n", b"\n")
    assert data.decode("utf-8-sig").startswith("模式,分类,尺码,新通用尺码,尺码代码")
    broken = tmp_path / "map.csv"
    broken.write_bytes("分类,尺码\n皮卡,X\n".encode())
    import pytest

    with pytest.raises(ValueError, match="新通用尺码"):
        report.size_code_map_bytes(broken)


def test_machine_interfaces_have_stable_layout_names():
    assert layout.size_rules("EU") == "EU/尺码规则.json"
    assert layout.STORE_SHELF == "US/店铺货架.json"
    assert layout.SIZE_CODE_MAP == "US/新旧尺码对应.csv"
