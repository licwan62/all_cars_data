import importlib.util
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_ru_proxy_sales", PROJECT / "scripts" / "build_ru_proxy_sales.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_proxy_sales_sum_by_match_key_onto_final_ids():
    sales = [
        {"match_key": "a", "sale_detail": "3"}, {"match_key": "a", "sale_detail": "2"},
        {"match_key": "b", "sale_detail": "4"}, {"match_key": "", "sale_detail": "9"},
        {"match_key": "zz", "sale_detail": "1"},
    ]
    sources = [{"来源ID": "RU|a", "DIMENSION-ID": "X RU"}, {"来源ID": "RU|b", "DIMENSION-ID": "X RU"}]
    result, audit = module.build(sales, sources, [{"DIMENSION-ID": "X RU"}, {"DIMENSION-ID": "Y RU"}])
    assert result == [{"DIMENSION-ID": "X RU", "销量合计": 9}, {"DIMENSION-ID": "Y RU", "销量合计": 0}]
    assert (audit["sales_source_total"], audit["matched_sales_total"], audit["unmatched_sales_total"]) == (19, 9, 10)


def test_published_proxy_sales_match_current_sources():
    result, audit = module.build(
        module.read_rows(module.SALES_PATH), module.read_rows(module.SOURCE_MAP_PATH), module.read_rows(module.DIMENSIONS_PATH)
    )
    assert len(result) == 13617
    assert audit["sales_source_total"] == 301065
    assert audit["matched_sales_total"] == 297009
    assert audit["sales_rows_without_match_key"] == 304
    assert audit["sales_source_positive_rows"] == 4272
    assert audit["dimension_rows_with_positive_proxy_sales"] == 4050
