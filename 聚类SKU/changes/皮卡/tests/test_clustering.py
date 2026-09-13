"""Tests for clustering engine."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import tempfile
import yaml

from clustering import load_config, filter_valid_rows, build_initial_clusters, check_cluster_safety


def test_filter_valid_rows():
    df = pd.DataFrame({
        "自动尺码": ["P1", "P1", "无可用尺码", "P2"],
        "L-MM": [5000, 5100, 5200, None],
        "W-MM": [1800, 1850, 1900, 1950],
        "H-MM": [1500, 1550, 1600, 1650],
        "自动长度余量": [100, 50, 60, 40],
        "YEAR_START": [2015, 2016, 2017, 2018],
        "YEAR_END": [2020, 2021, 2022, 2023],
        "CAB": ["Crew", "Regular", "Crew", "Crew"],
        "BED": ["5.5", "6.5", "8.0", "5.5"],
        "预估销量 的总和": [100, 200, 300, 400],
        "MAKE_NORMALIZED": ["Ford", "Chevy", "Ram", "GMC"],
        "MODEL_FAMILY": ["F-150", "Silverado 1500", "1500", "Sierra 1500"],
    })

    valid, exc = filter_valid_rows(df)

    assert len(valid) == 2  # first two rows are valid
    assert len(exc) == 2    # row 2: invalid size, row 3: missing L-MM


def test_build_initial_clusters():
    df = pd.DataFrame({
        "自动尺码": ["P1", "P1", "P2", "P2"],
        "AXLE_TYPE": ["SRW", "SRW", "SRW", "SRW"],
        "TRUCK_TYPE": ["FULLSIZE", "FULLSIZE", "MIDSIZE", "MIDSIZE"],
        "CAB_GROUP": ["CREW", "CREW", "CREW", "CREW"],
        "BED_GROUP": ["SHORT", "SHORT", "SHORT", "SHORT"],
        "L-MM": [5000, 5100, 5200, 5300],
        "W-MM": [1800, 1850, 1900, 1950],
        "H-MM": [1500, 1550, 1600, 1650],
        "自动长度余量": [100, 50, 80, 40],
        "YEAR_START": [2015, 2016, 2017, 2018],
        "YEAR_END": [2020, 2021, 2022, 2023],
        "CAB": ["Crew", "Crew", "Crew", "Crew"],
        "BED": ["5.5", "5.5", "5.5", "5.5"],
        "预估销量 的总和": [100, 200, 300, 400],
        "MAKE_NORMALIZED": ["Ford", "Chevy", "Toyota", "Nissan"],
        "MODEL_FAMILY": ["F-150", "Silverado 1500", "Tacoma", "Frontier"],
    })

    config = {
        "pickup": {
            "max_length_spread_mm": 450,
            "max_width_spread_mm": 180,
            "max_height_spread_mm": 200,
            "min_length_margin_mm": 50,
            "allow_cross_make": True,
            "allow_cross_model": True,
            "allow_cross_cab": True,
            "allow_cross_bed_group": True,
            "allow_drw_srw_merge": True,
        }
    }

    clusters = build_initial_clusters(df, config)

    assert len(clusters) == 2  # 2 unique auto sizes
    assert clusters[0]["自动尺码"] == "P1"
    assert clusters[1]["自动尺码"] == "P2"
    assert clusters[0]["fitment_count"] == 2
    assert clusters[1]["fitment_count"] == 2


def test_check_cluster_safety_pass():
    cluster = {
        "l_spread": 200,
        "w_spread": 100,
        "h_spread": 80,
        "length_margin_min": 60,
    }
    config = {
        "pickup": {
            "max_length_spread_mm": 450,
            "max_width_spread_mm": 180,
            "max_height_spread_mm": 200,
            "min_length_margin_mm": 50,
        }
    }
    assert check_cluster_safety(cluster, config) is True


def test_check_cluster_safety_fail_length():
    cluster = {
        "l_spread": 500,
        "w_spread": 100,
        "h_spread": 80,
        "length_margin_min": 60,
    }
    config = {
        "pickup": {
            "max_length_spread_mm": 450,
            "max_width_spread_mm": 180,
            "max_height_spread_mm": 200,
            "min_length_margin_mm": 50,
        }
    }
    assert check_cluster_safety(cluster, config) is False


def test_check_cluster_safety_fail_margin():
    cluster = {
        "l_spread": 200,
        "w_spread": 100,
        "h_spread": 80,
        "length_margin_min": 30,
    }
    config = {
        "pickup": {
            "max_length_spread_mm": 450,
            "max_width_spread_mm": 180,
            "max_height_spread_mm": 200,
            "min_length_margin_mm": 50,
        }
    }
    assert check_cluster_safety(cluster, config) is False