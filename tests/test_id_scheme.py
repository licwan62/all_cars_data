from __future__ import annotations

import unittest

from id_scheme import atom_record_id, dimension_id


class DimensionIdTests(unittest.TestCase):
    def test_omits_labels_and_blank_version(self) -> None:
        row = {
            "MAKE": "Acura",
            "MODEL": "ADX",
            "版本": "",
            "结构": "SUV",
            "YEAR": "2025-2026",
            "分类": "越野车",
        }
        self.assertEqual(dimension_id(row), "Acura ADX SUV 2025-2026")

    def test_keeps_nonempty_version(self) -> None:
        row = {
            "MAKE": "Acura",
            "MODEL": "MDX",
            "版本": "Type S",
            "结构": "SUV",
            "YEAR": "2025-2026",
            "分类": "越野车",
        }
        self.assertEqual(dimension_id(row), "Acura MDX Type S SUV 2025-2026")

    def test_pickup_appends_cab_and_bed(self) -> None:
        row = {
            "MAKE": "Cadillac",
            "MODEL": "Escalade EXT",
            "版本": "",
            "结构": "Pickup",
            "YEAR": "2002-2006",
            "分类": "皮卡",
            "CAB": "Crew",
            "BED": "5.3",
        }
        value = "Cadillac Escalade EXT Pickup 2002-2006 Crew 5.3"
        self.assertEqual(dimension_id(row), value)
        self.assertEqual(atom_record_id(value, "2002"), value + "|ATOM_YEAR=2002")


if __name__ == "__main__":
    unittest.main()
