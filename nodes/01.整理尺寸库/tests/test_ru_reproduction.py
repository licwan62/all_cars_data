from __future__ import annotations

import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
CODE = PROJECT / "code"
for path in (ROOT / "lib", CODE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from regional_size_common import build_dimension_library, read_csv
from regional_sources import build_ru_base


def test_ru_00_library_is_reproducible_from_three_source_tables():
    base, summary = build_ru_base(PROJECT.parent / "00.自动化尺寸抓取器" / "output" / "RU")
    rebuilt, _ = build_dimension_library(base)
    import pandas as pd
    from merge_dimension_library import transform_region_rows
    official = read_csv(PROJECT / "output" / "尺寸库_RU.csv")

    assert summary["source_rows"] == {"catalog": 4870, "dimensions": 81382, "sales": 13137}
    assert len(base) == 13868
    assert len(rebuilt) == 13850
    rebuilt = pd.DataFrame(transform_region_rows(rebuilt.fillna("").astype(str).to_dict("records"), "ru"))
    assert len(rebuilt) == len(official) == 13617
    assert rebuilt.fillna("").astype(str).equals(official.fillna("").astype(str))
