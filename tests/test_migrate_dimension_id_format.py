from __future__ import annotations

import unittest

from migrate_dimension_id_format import migrate_text


class DimensionIdMigrationTests(unittest.TestCase):
    def test_migrates_regular_and_atom_ids(self) -> None:
        old = "MAKE" + "=Acura|MODEL=ADX|VERSION=|STRUCTURE=SUV|YEAR=2025-2026"
        text = old + "," + old + "|ATOM_YEAR=2025"
        migrated, count = migrate_text(text)
        compact = "Acura ADX SUV 2025-2026"
        self.assertEqual(migrated, compact + "," + compact + "|ATOM_YEAR=2025")
        self.assertEqual(count, 2)

    def test_migrates_pickup_suffix(self) -> None:
        old = (
            "MAKE"
            + "=Cadillac|MODEL=Escalade EXT|VERSION=|STRUCTURE=Pickup|"
            "YEAR=2002-2006|CAB=Crew|BED=5.3"
        )
        migrated, count = migrate_text(old)
        self.assertEqual(
            migrated, "Cadillac Escalade EXT Pickup 2002-2006 Crew 5.3"
        )
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
