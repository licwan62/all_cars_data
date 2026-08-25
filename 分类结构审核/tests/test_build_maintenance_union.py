from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "code" / "build_maintenance_union.py"
SPEC = importlib.util.spec_from_file_location("build_maintenance_union", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def row(structure: str, year: str, segment: str) -> dict[str, str]:
    value = {field: "" for field in MODULE.FIELDS}
    value.update(
        {
            "MAKE": "Example",
            "MODEL": "Model",
            "结构": structure,
            "代际": "gen1",
            "YEAR": year,
            "__segment": segment,
            "__source_file": f"{segment}.csv",
            "__source_row": "2",
        }
    )
    value["DIMENSION-ID"] = MODULE.expected_dimension_id(value)
    return value


class MaintenanceUnionTests(unittest.TestCase):
    def test_valid_disjoint_inputs_pass(self) -> None:
        rows = [row("Sedan", "1980-1999", "normal"), row("Sedan", "1950-1979", "classic")]
        report, errors = MODULE.validate(MODULE.FIELDS, MODULE.FIELDS, rows)
        self.assertTrue(report["passed"])
        self.assertEqual([], errors)

    def test_mixed_structure_is_rejected(self) -> None:
        report, errors = MODULE.validate(MODULE.FIELDS, MODULE.FIELDS, [row("Coupe/Convertible", "1960", "classic")])
        self.assertFalse(report["passed"])
        self.assertTrue(any("复合结构" in error for error in errors))

    def test_cross_segment_year_overlap_is_rejected(self) -> None:
        rows = [row("Sedan", "1975-1985", "normal"), row("Sedan", "1980", "classic")]
        report, errors = MODULE.validate(MODULE.FIELDS, MODULE.FIELDS, rows)
        self.assertFalse(report["passed"])
        self.assertTrue(any("年份重叠" in error for error in errors))

    def test_dimension_id_must_match_identity_fields(self) -> None:
        bad = row("Coupe", "1970", "classic")
        bad["DIMENSION-ID"] = "stale-id"
        report, errors = MODULE.validate(MODULE.FIELDS, MODULE.FIELDS, [bad])
        self.assertFalse(report["passed"])
        self.assertTrue(any("身份字段" in error for error in errors))

    def test_source_output_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.assert_safe_output(MODULE.SOURCE_DIR / "do-not-write.csv")


if __name__ == "__main__":
    unittest.main()
