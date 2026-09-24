import publish_rule_reference as prr
import csv
import io


def test_shelf_rows_flatten_all_stores():
    rows = prr.shelf_rows()
    assert {row[0] for row in rows} >= {"HNT", "TM", "TM_拆分"}
    assert all(len(row) == 3 and all(row) for row in rows)


def test_payloads_cover_three_regions_and_shelf():
    payloads = prr.build_payloads()
    assert set(payloads) == {"尺码匹配规则.csv", "尺码匹配规则_EU.csv", "尺码匹配规则_RU.csv", "店铺货架.csv"}


def test_us_rules_use_2l_without_custom_sizes():
    payloads = prr.build_payloads()
    rules = list(csv.DictReader(io.StringIO(payloads["尺码匹配规则.csv"].decode("utf-8-sig"))))
    assert sum(row["尺码"] == "2L" for row in rules) == 1
    assert not any(row["尺码"] == "2L+" or row.get("模式") == "定制" for row in rules)
    shelf = list(csv.DictReader(io.StringIO(payloads["店铺货架.csv"].decode("utf-8-sig"))))
    assert not any(row["匹配尺码"] == "2L+" or row["发货尺码"] == "2L+" for row in shelf)


def test_eu_calculation_uses_the_published_eu_rules():
    import build_regional_coverage_full as coverage

    eu_rules, _ = prr.RULE_SOURCES["尺码匹配规则_EU.csv"]
    assert coverage.EU_CONFIG_DIR / "尺码匹配规则.csv" == eu_rules
    assert (coverage.EU_CONFIG_DIR / "尺码匹配参数.csv").is_file()
