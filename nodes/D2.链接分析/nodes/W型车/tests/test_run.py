import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from run import CHECK_DIR, MASTER_DIR, dimension_concentration, drop_derived_columns, read_table, slim_release, write_csv


def rows(dimensions):
    return [
        {"L-MM": str(length), "W-MM": str(width), "H-MM": str(height)}
        for length, width, height in dimensions
    ]


def test_identical_dimensions_have_full_concentration():
    assert dimension_concentration(rows([(4800, 1800, 1400), (4800, 1800, 1400)])) == 100.0


def test_length_variation_has_more_weight_than_equal_relative_width_variation():
    length_score = dimension_concentration(rows([(4500, 1800, 1400), (5100, 1800, 1400)]))
    width_score = dimension_concentration(rows([(4800, 1680, 1400), (4800, 1920, 1400)]))
    assert length_score < width_score


def test_derived_column_is_dropped_only_when_every_row_matches(tmp_path):
    path = tmp_path / "table.csv"
    write_csv(path, ["链接名称", "尺码名称"], [{"链接名称": "A", "尺码名称": "A"}, {"链接名称": "B", "尺码名称": "B"}])
    drop_derived_columns(path, {"尺码名称": lambda row: row["链接名称"]})
    assert read_table(path)[0] == ["链接名称"]

    write_csv(path, ["链接名称", "尺码名称"], [{"链接名称": "A", "尺码名称": "X"}])
    with pytest.raises(ValueError, match="尺码名称"):
        drop_derived_columns(path, {"尺码名称": lambda row: row["链接名称"]})


def write_minimal_release(root):
    master_dir, check_dir = root / MASTER_DIR, root / CHECK_DIR
    master_dir.mkdir()
    check_dir.mkdir()
    write_csv(master_dir / "聚类主表.csv", [
        "聚类ID", "链接名称", "尺码名称", "品牌", "车型", "适配车型", "年份汇总", "最早年份", "最晚年份", "聚类状态", "原始年份", "命名年份",
    ], [
        {"聚类ID": cluster, "链接名称": f"Ford {model} {years}", "尺码名称": f"Ford {model} {years}", "品牌": "Ford", "车型": model,
         "适配车型": f"Ford {model} {years}", "年份汇总": years, "最早年份": years[:4], "最晚年份": years[-4:], "聚类状态": "通过",
         "原始年份": years, "命名年份": years}
        for cluster, model, years in (("C1", "Falcon", "1960-1965"), ("C2", "Falcon", "1966-1970"))
    ])
    write_csv(check_dir / "聚类合并校验.csv", ["原聚类ID", "原逻辑尺码", "品牌", "车型", "建议最终尺码", "尺码簇分析明细", "冲突明细"], [
        {"原聚类ID": cluster, "原逻辑尺码": "4S", "品牌": "Ford", "车型": "Falcon", "建议最终尺码": "4S", "尺码簇分析明细": "", "冲突明细": ""}
        for cluster in ("C1", "C2")
    ])
    write_csv(master_dir / "聚类ID映射.csv", ["原聚类ID", "原逻辑尺码", "品牌", "车型", "建议最终尺码", "新聚类ID", "是否变更"], [
        {"原聚类ID": cluster, "原逻辑尺码": "4S", "品牌": "Ford", "车型": "Falcon", "建议最终尺码": "4S", "新聚类ID": cluster, "是否变更": "否"}
        for cluster in ("C1", "C2")
    ])
    write_csv(master_dir / "聚类原子明细.csv", ["CLUSTER_ID", "YEAR", "相差数值", "原聚类ID", "原逻辑尺码"], [
        {"CLUSTER_ID": cluster, "YEAR": "1960", "相差数值": "", "原聚类ID": cluster, "原逻辑尺码": "4S"} for cluster in ("C1", "C2")
    ])
    write_csv(check_dir / "年份合并校验.csv", ["聚类ID", "合并结论", "新增年份数", "尺码簇分析明细", "冲突明细"], [
        {"聚类ID": "C1", "合并结论": "无需合并", "新增年份数": "0", "尺码簇分析明细": "", "冲突明细": ""},
        {"聚类ID": "C2", "合并结论": "安全合并：无跨尺码事实", "新增年份数": "2", "尺码簇分析明细": "", "冲突明细": ""},
    ])
    write_csv(master_dir / "关联链接明细.csv", ["CLUSTER_ID", "兄弟CLUSTER_ID"], [
        {"CLUSTER_ID": "C1", "兄弟CLUSTER_ID": "C2"}, {"CLUSTER_ID": "C2", "兄弟CLUSTER_ID": "C1"},
    ])


def test_slim_release_merges_id_map_and_removes_repeated_rows(tmp_path):
    write_minimal_release(tmp_path)
    slim_release(tmp_path)

    assert not (tmp_path / MASTER_DIR / "聚类ID映射.csv").exists()
    assert read_table(tmp_path / MASTER_DIR / "聚类主表.csv")[0] == ["聚类ID", "链接名称", "品牌", "车型", "原始年份", "命名年份"]
    check_columns, checks = read_table(tmp_path / CHECK_DIR / "聚类合并校验.csv")
    assert check_columns[-3:] == ["冲突明细", "新聚类ID", "是否变更"] and "尺码簇分析明细" not in check_columns
    assert [row["新聚类ID"] for row in checks] == ["C1", "C2"]
    assert read_table(tmp_path / MASTER_DIR / "聚类原子明细.csv")[0] == ["CLUSTER_ID", "YEAR", "原聚类ID"]
    assert [row["聚类ID"] for row in read_table(tmp_path / CHECK_DIR / "年份合并校验.csv")[1]] == ["C2"]
    assert read_table(tmp_path / MASTER_DIR / "关联链接明细.csv")[1] == [{"CLUSTER_ID": "C1", "兄弟CLUSTER_ID": "C2"}]
