from __future__ import annotations

import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
CODE = PROJECT / "code"
for path in (ROOT, CODE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from regional_size_common import build_dimension_library, read_csv
from regional_sources import build_ru_base


def test_ru_00_library_is_reproducible_from_three_source_tables():
    base, summary = build_ru_base(PROJECT / "data" / "ru" / "0916")
    rebuilt, _ = build_dimension_library(base)
    official = read_csv(PROJECT / "data" / "ru" / "0916" / "00_RU尺寸库.csv")

    assert summary["source_rows"] == {"catalog": 4870, "dimensions": 81382, "sales": 13137}
    assert len(base) == 13868
    assert len(rebuilt) == len(official) == 13850
    assert rebuilt.fillna("").astype(str).equals(official.fillna("").astype(str))
