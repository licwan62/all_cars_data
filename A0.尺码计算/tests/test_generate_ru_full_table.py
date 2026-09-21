from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))
SPEC = importlib.util.spec_from_file_location("generate_ru_full_table", PROJECT / "generate_ru_full_table.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_ru_sales_are_aggregated_by_match_key_and_cover_published_dimensions():
    sales, audit = module.build_ru_sales_by_dimension()

    assert len(sales) == 13848
    assert sales["DIMENSION-ID"].is_unique
    assert sales["销量合计"].sum() == 296972
    assert audit["sales_source_total"] == 301065
    assert audit["unmatched_sales_total"] == 4093
    assert audit["sales_rows_without_match_key"] == 304
    assert audit["sales_source_positive_rows"] == 4272
    assert audit["dimension_rows_with_positive_proxy_sales"] == 4175


def test_ru_full_base_uses_only_ru_dimensions_and_sales():
    dimensions = module.analysis._read_csv(module.RU_DIMENSIONS_PATH)
    sales, _ = module.build_ru_sales_by_dimension()

    result = module.build_ru_full_base(dimensions, sales)

    assert len(result) == 13848
    assert result["DIMENSION-ID"].str.endswith(" RU").all()
    assert result["销量合计"].sum() == 296972
