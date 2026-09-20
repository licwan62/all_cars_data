"""Tests for CAB mapping."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from normalize import normalize_cab


def test_cab_mapping(tmp_path):
    """Test CAB normalization with a temporary config."""
    import tempfile, os

    config_dir = tempfile.mkdtemp()
    cab_csv = Path(config_dir) / "cab_mapping.csv"
    cab_csv.write_text("""cab_raw,cab_group
Regular,REGULAR
Crew,CREW
Extended,EXTENDED
SuperCab,EXTENDED
SuperCrew,CREW
Mega,MEGA
Double,CREW
Quad,CREW
Access,EXTENDED
King,EXTENDED
XtraCab,EXTENDED
Club,EXTENDED
""")

    df = pd.DataFrame({"CAB": ["Regular", "Crew", "SuperCrew", "Mega", "Double", "Unknown"]})
    df = normalize_cab(df, config_dir)

    assert df.loc[0, "CAB_GROUP"] == "REGULAR"
    assert df.loc[1, "CAB_GROUP"] == "CREW"
    assert df.loc[2, "CAB_GROUP"] == "CREW"
    assert df.loc[3, "CAB_GROUP"] == "MEGA"
    assert df.loc[4, "CAB_GROUP"] == "CREW"
    assert df.loc[5, "CAB_GROUP"] == "UNKNOWN"