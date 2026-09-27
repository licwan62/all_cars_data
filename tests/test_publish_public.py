from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import publish_public as pp  # noqa: E402


def test_store_full_tables_go_to_us_full_dir():
    assert pp.target_for("US/店铺/店铺全量_HNT.csv", "size-calculation") == Path("data/us_data/全量/店铺全量_HNT.csv")
    assert pp.target_for("US/全量/全量表.csv", "size-calculation") == Path("data/us_data/全量/全量表.csv")


def test_us_compression_lines_go_to_compression_dir():
    lines = pp.compression_lines()
    assert {line for line, region in lines.items() if region == "US"} == {"US", "HNT", "TM", "TM_拆分"}
    assert pp.target_for("US/压缩尺码表.csv", "size-compression", lines) == Path("data/us_data/压缩/US/压缩尺码表.csv")
    assert pp.target_for("TM_拆分/压缩尺码表_皮卡.csv", "size-compression", lines) == Path("data/us_data/压缩/TM_拆分/压缩尺码表_皮卡.csv")
    assert pp.target_for("EU/压缩尺码表.csv", "size-compression", lines) == Path("data/eu_data/压缩尺码表.csv")
