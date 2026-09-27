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
