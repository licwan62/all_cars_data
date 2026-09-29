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


def test_common_deliverables_are_grouped_by_responsibility():
    assert pp.target_for("尺寸库.csv", "dimension-library") == Path("data/基础数据/尺寸库.csv")
    assert pp.target_for("车型编码映射.csv", "code-mapping") == Path("data/编码映射/车型编码映射.csv")
    assert pp.target_for("车形分类.csv", "shape-classification") == Path("data/车型分类/车形分类.csv")
    assert pp.target_for("尺码尺寸异常.csv", "full-generation") == Path("data/质量分析/尺码尺寸异常.csv")
    assert pp.target_for("耳位分析表.csv", "negative-review-analysis") == Path("data/差评分析/耳位分析表.csv")
    assert pp.target_for("代表车型.csv", "representative-model") == Path("data/代表车型/代表车型.csv")


def test_regional_and_customizing_paths_keep_priority_over_common_grouping():
    assert pp.target_for("尺寸库_EU.csv", "dimension-library") == Path("data/eu_data/尺寸库_EU.csv")
    assert pp.target_for("定制需求度评分.csv", "compression-scoring") == Path("customizing/定制需求度评分.csv")
