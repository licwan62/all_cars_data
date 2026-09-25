from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import build_consolidated_full_table as consolidated  # noqa: E402


def write_region(output_dir: Path, region: str, extra: dict[str, str] | None = None) -> None:
    row = {"MAKE": "Ford", "自动尺码": "3L", **(extra or {})}
    row.update({"DIMENSION-CODE": f"{region}0001", "DIMENSION-ID": f"Ford Focus {region}"})
    pd.DataFrame([row]).to_csv(output_dir / f"全量表_{region}.csv", index=False, encoding="utf-8-sig")


def write_stores(output_dir: Path, sizes: dict[str, str]) -> None:
    """店铺货架 + 店铺全量_<店铺>（与 US 表同行，自动尺码换成店铺发货尺码）。"""
    shelf = [{"店铺": store, "匹配尺码": "3L", "发货尺码": size} for store, size in sizes.items()]
    pd.DataFrame(shelf, columns=["店铺", "匹配尺码", "发货尺码"]).to_csv(output_dir / "店铺货架.csv", index=False, encoding="utf-8-sig")
    us = pd.read_csv(output_dir / "全量表_US.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    for store, size in sizes.items():
        us.assign(自动尺码=size).to_csv(output_dir / f"店铺全量_{store}.csv", index=False, encoding="utf-8-sig")


def test_consolidates_three_regions_with_union_columns(tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    write_region(output, "US")
    write_region(output, "EU")
    write_region(output, "RU", {"OZON尺码": "L"})
    write_stores(output, {"HNT": "3L-0", "TM": "3L"})
    mapping = tmp_path / "尺寸TRIM映射.csv"
    pd.DataFrame([{"DIMENSION-ID": "Ford Focus", "Trims": "SE|SEL"}]).to_csv(mapping, index=False, encoding="utf-8-sig")

    result = consolidated.run(output, tmp_path / "final", tmp_path / "artifacts", trim_mapping=mapping)

    frame = pd.read_csv(tmp_path / "final" / "全量表_汇总.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    assert result["rows"] == 3
    assert list(frame.columns)[-2:] == ["DIMENSION-CODE", "DIMENSION-ID"]
    assert frame.loc[frame["DIMENSION-ID"].str.endswith("US"), "OZON尺码"].item() == ""
    assert frame.loc[frame["DIMENSION-ID"].eq("Ford Focus US"), "Trims"].item() == "SE|SEL"
    assert frame.loc[frame["DIMENSION-ID"].eq("Ford Focus EU"), "Trims"].item() == ""
    assert result["trim_lookup"]["matched_us_rows"] == 1
    assert list((tmp_path / "artifacts").glob("*_01_consolidated-full-table/status.json"))

    for region in consolidated.REGIONS:
        part = pd.read_csv(tmp_path / "final" / f"全量生成_{region}.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
        assert part["DIMENSION-ID"].tolist() == [f"Ford Focus {region}"]
        assert list(part.columns)[-3:] == ["Trims", "DIMENSION-CODE", "DIMENSION-ID"]
        assert ("OZON尺码" in part.columns) == (region == "RU")
    us = pd.read_csv(tmp_path / "final" / "全量生成_US.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    assert us["Trims"].item() == "SE|SEL"
    assert result["stores"] == ["HNT", "TM"]
    hnt = pd.read_csv(tmp_path / "final" / "全量生成_HNT.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    assert list(hnt.columns) == list(us.columns)
    assert (hnt["自动尺码"].item(), hnt["Trims"].item()) == ("3L-0", "SE|SEL")


def test_store_rows_must_match_us_table(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    for region in consolidated.REGIONS:
        write_region(source, region)
    write_stores(source, {"HNT": "3L-0"})
    write_region(source, "US")  # 保持 US 表
    pd.DataFrame([{"MAKE": "Ford", "自动尺码": "3L-0", "DIMENSION-CODE": "X", "DIMENSION-ID": "Other US"}]).to_csv(
        source / "店铺全量_HNT.csv", index=False, encoding="utf-8-sig"
    )
    mapping = tmp_path / "mapping.csv"
    pd.DataFrame([{"DIMENSION-ID": "Ford Focus", "Trims": "A"}]).to_csv(mapping, index=False)
    with pytest.raises(consolidated.ConsolidationError, match="行不一致"):
        consolidated.run(source, tmp_path / "final", tmp_path / "artifacts", trim_mapping=mapping)
    assert not (tmp_path / "final").exists()


def test_missing_region_or_code_column_fails_without_touching_output(tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    write_region(output, "US")
    with pytest.raises(consolidated.ConsolidationError, match="缺少 EU 全量表"):
        consolidated.run(output, tmp_path / "final", tmp_path / "artifacts")

    pd.DataFrame([{"MAKE": "A", "DIMENSION-ID": "A EU"}]).to_csv(
        output / "全量表_EU.csv", index=False, encoding="utf-8-sig"
    )
    write_region(output, "RU")
    with pytest.raises(consolidated.ConsolidationError, match="DIMENSION-CODE"):
        consolidated.run(output, tmp_path / "final", tmp_path / "artifacts")
    assert not (tmp_path / "final" / "全量表_汇总.csv").exists()
    assert not (tmp_path / "artifacts").exists()


def test_duplicate_trim_mapping_fails_without_publishing(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    for region in consolidated.REGIONS:
        write_region(source, region)
    write_stores(source, {"HNT": "3L-0"})
    mapping = tmp_path / "mapping.csv"
    pd.DataFrame([{"DIMENSION-ID": "Ford Focus", "Trims": "A"},
                  {"DIMENSION-ID": "Ford Focus", "Trims": "B"}]).to_csv(mapping, index=False)
    with pytest.raises(consolidated.ConsolidationError, match="重复"):
        consolidated.run(source, tmp_path / "final", tmp_path / "artifacts", trim_mapping=mapping)
    assert not (tmp_path / "final").exists()
