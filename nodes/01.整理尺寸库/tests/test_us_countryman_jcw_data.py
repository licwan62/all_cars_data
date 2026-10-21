from pathlib import Path
import csv


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "data" / "us" / "0916" / "00_US尺寸库.csv"


def test_2018_countryman_jcw_is_a_single_year_us_record_with_official_dimensions() -> None:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    matched = [row for row in rows if row["DIMENSION-ID"] == "MINI Countryman JCW SUV 2018"]
    assert matched == [
        {
            "DIMENSION-ID": "MINI Countryman JCW SUV 2018", "MAKE": "MINI", "MODEL": "Countryman", "版本": "JCW",
            "CAB": "", "BED": "", "结构": "SUV", "代际": "gen2", "YEAR": "2018", "分类": "越野车",
            "L-IN": "169.8", "W-IN": "71.7", "H-IN": "61.3", "参考车型": "2018 MINI John Cooper Works Countryman ALL4",
            "备注": "US 官方 1/2017 资料：2018 MY；2017-04 到店；169.8×71.7×61.3 in；不外推后续年款 | https://www.press.bmwgroup.com/usa/article/attachment/T0267351EN_US/376516", "迭代状态": "可入库",
        }
    ]
