import publish_rule_reference as prr


def test_shelf_rows_flatten_all_stores():
    rows = prr.shelf_rows()
    assert {row[0] for row in rows} >= {"HNT", "TM", "TM_拆分"}
    assert all(len(row) == 3 and all(row) for row in rows)


def test_payloads_cover_three_regions_and_shelf():
    payloads = prr.build_payloads()
    assert set(payloads) == {"尺码匹配规则.csv", "尺码匹配规则_EU.csv", "尺码匹配规则_RU.csv", "店铺货架.csv"}
