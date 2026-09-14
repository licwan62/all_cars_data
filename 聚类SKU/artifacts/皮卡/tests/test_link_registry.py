import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from link_registry import assign_persistent_link_ids, save_link_registry


def _cluster(provisional_id, sku, cab, bed, start, end):
    return {
        "CLUSTER_ID": provisional_id,
        "自动尺码": sku,
        "rows": pd.DataFrame({
            "MAKE_NORMALIZED": ["Ford"],
            "MODEL_FAMILY": ["F-150"],
            "版本": [""],
            "CAB": [cab],
            "BED": [bed],
            "YEAR_START": [start],
            "YEAR_END": [end],
        }),
    }


def test_link_ids_are_stable_across_order_and_physical_sku_change(tmp_path):
    registry_path = tmp_path / "link_id_registry.csv"
    first = [
        _cluster("OLD-A", "PK-L", "Crew", "5.5", 2020, 2022),
        _cluster("OLD-B", "PK-L", "Regular", "8.0", 2020, 2022),
    ]
    registry = assign_persistent_link_ids(first, registry_path)
    save_link_registry(registry, registry_path)
    first_ids = {c["rows"]["CAB"].iloc[0]: c["LINK_ID"] for c in first}

    second = [
        _cluster("NEW-B", "PK-L", "Regular", "8.0", 2020, 2022),
        _cluster("NEW-A", "PK-XL", "Crew", "5.5", 2020, 2023),
    ]
    updated = assign_persistent_link_ids(second, registry_path)
    second_ids = {c["rows"]["CAB"].iloc[0]: c["LINK_ID"] for c in second}

    assert second_ids == first_ids
    assert all(c["CLUSTER_ID"].startswith("LINK-") for c in second)
    assert all(not c["CLUSTER_KEY"].startswith(c["自动尺码"]) for c in second)
    assert (updated["STATUS"] == "ACTIVE").sum() == 2
