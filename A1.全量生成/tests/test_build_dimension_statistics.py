from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import build_dimension_statistics as subject  # noqa: E402


def write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    widths = [100, 101, 102, 103, 300]
    tables = {
        # 只有 US 带 TRIM；RU 独有 OZON尺码
        "US": pd.DataFrame([
            {"MAKE": "M", "MODEL": f"V{i}", "TRIM": "T", "自动尺码": "S", "W-MM": width, "H-MM": 150 + i, "DIMENSION-ID": f"ID{i} US"}
            for i, width in enumerate(widths)
        ]),
        "EU": pd.DataFrame([{"MAKE": "M", "MODEL": "EU", "自动尺码": "S", "W-MM": 500, "H-MM": 600, "DIMENSION-ID": "EU1 EU"}]),
        "RU": pd.DataFrame([{"MAKE": "M", "MODEL": "skip", "自动尺码": "无可用尺码", "OZON尺码": "", "W-MM": 999, "H-MM": 999, "DIMENSION-ID": "SKIP RU"}]),
    }
    source = tmp_path / "a0_output"
    for region, frame in tables.items():
        path = source / subject.region_table(region)
        path.parent.mkdir(parents=True)
        frame.to_csv(path, index=False, encoding="utf-8-sig")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"excluded_sizes": ["无可用尺码", "数据不全"], "iqr_multiplier": 1.5, "zscore_threshold": 3.0, "variance_ddof": 0}, ensure_ascii=False), encoding="utf-8")
    return source, config


def test_builds_statistics_extremes_and_outliers(tmp_path):
    source, config = write_inputs(tmp_path)
    result = subject.run(source, config, tmp_path / "output", tmp_path / "artifacts")

    stats = pd.read_csv(tmp_path / "output" / subject.STATS_NAME)
    assert result["source_rows"] == 6
    assert result["sizes"] == 1
    assert result["region_size_groups"] == 2
    us_stats = stats.loc[(stats["区域"] == "US") & (stats["自动尺码"] == "S")].iloc[0]
    assert us_stats["宽最大-MM"] == 300
    assert us_stats["宽中位数-MM"] == 102
    assert us_stats["宽方差-MM2"] == pd.Series([100, 101, 102, 103, 300]).var(ddof=0)

    extremes = pd.read_csv(tmp_path / "output" / subject.EXTREMES_NAME)
    assert set(extremes["指标"]) == {"最宽", "最高"}
    assert set(extremes["DIMENSION-ID"]) == {"ID4 US", "EU1 EU"}
    assert extremes.set_index("DIMENSION-ID")["TRIM"].fillna("").to_dict() == {"ID4 US": "T", "EU1 EU": ""}
    assert "DIMENSION-CODE" not in extremes.columns

    outliers = pd.read_csv(tmp_path / "output" / subject.OUTLIERS_NAME)
    assert outliers["DIMENSION-ID"].tolist() == ["ID4 US"]
    assert "宽超出1.5×IQR" in outliers.loc[0, "异常原因"]
    artifact = Path(result["artifact"])
    assert (artifact / "status.json").is_file()
    assert len(list((artifact / "output").glob("*-*.csv"))) == 3
    assert (artifact / "input" / subject.region_table("RU")).is_file()


def test_missing_region_fails(tmp_path):
    source, config = write_inputs(tmp_path)
    (source / subject.region_table("EU")).unlink()
    try:
        subject.run(source, config, tmp_path / "output", tmp_path / "artifacts")
    except subject.DimensionStatisticsError as error:
        assert "缺少 EU 全量表" in str(error)
    else:
        raise AssertionError("expected missing region to fail")


def test_invalid_dimensions_fail_before_output(tmp_path):
    source, config = write_inputs(tmp_path)
    us = source / subject.region_table("US")
    frame = pd.read_csv(us)
    frame.loc[0, "W-MM"] = 0
    frame.to_csv(us, index=False, encoding="utf-8-sig")
    try:
        subject.run(source, config, tmp_path / "output", tmp_path / "artifacts")
    except subject.DimensionStatisticsError as error:
        assert "非正或空宽高" in str(error)
    else:
        raise AssertionError("expected invalid dimensions to fail")
    assert not (tmp_path / "output").exists()
