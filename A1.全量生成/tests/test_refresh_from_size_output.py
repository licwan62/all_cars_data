import csv
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(PROJECT))

import refresh_from_size_output as refresh  # noqa: E402


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_refreshed_trim_mapping_matches_current_us_and_preserves_maintained_values():
    source = read_rows(ROOT / "A0.尺码计算" / "output" / "全量表_US.csv")
    current_ids = {row["DIMENSION-ID"].removesuffix(" US") for row in source}
    mapping = read_rows(PROJECT / "output" / "尺寸TRIM映射.csv")
    maintained = {row["DIMENSION-ID"]: row["Trims"]
                  for row in read_rows(PROJECT / "data" / "trim_values.csv")}
    migration = refresh.load_id_migration(current_ids)
    for old_id, trims in list(maintained.items()):
        for new_id in refresh.migrated_ids(migration, old_id, None) or []:
            maintained.setdefault(new_id, trims)
    assert len(mapping) == len(current_ids)
    assert {row["DIMENSION-ID"] for row in mapping} == current_ids
    assert all(row["Trims"] == maintained.get(row["DIMENSION-ID"], "")
               for row in mapping)
    assert any(row["Trims"] for row in mapping)
