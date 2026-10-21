from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import expand_year  # noqa: E402
from common import CACHE_FIELDS, read_csv, write_csv  # noqa: E402
from common import dimension_id  # noqa: E402
import build_atoms  # noqa: E402
import expand_years  # noqa: E402
import merge_results  # noqa: E402
from merge_results import allocate_integer  # noqa: E402
import validate_sales  # noqa: E402
import allocation_weight_review_project as awr  # noqa: E402


class YearExpansionTests(unittest.TestCase):
    def test_range_is_inclusive(self) -> None:
        self.assertEqual(expand_year("2023-2025"), [2023, 2024, 2025])

    def test_single_year(self) -> None:
        self.assertEqual(expand_year("2025"), [2025])

    def test_reversed_range_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            expand_year("2025-2023")

    def test_us_regional_suffix_is_accepted_for_us_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.csv"
            expanded = root / "expanded.csv"
            row = {field: "" for field in expand_years.REQUIRED_FIELDS}
            row.update({"MAKE": "Test", "MODEL": "One", "YEAR": "2025"})
            row["DIMENSION-ID"] = dimension_id(row) + " US"
            write_csv(source, expand_years.REQUIRED_FIELDS, [row])
            config = {"input_csv": str(source), "expanded_csv": str(expanded)}
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            result = expand_years.run(str(config_path))

            self.assertEqual(result, {"source_rows": 1, "expanded_rows": 1})


class AllocationTests(unittest.TestCase):
    def test_largest_remainder_preserves_total(self) -> None:
        from decimal import Decimal

        values = allocate_integer(10, [Decimal("0.333333333333"), Decimal("0.333333333333"), Decimal("0.333333333334")])
        self.assertEqual(sum(values), 10)
        self.assertEqual(sorted(values), [3, 3, 4])

    def test_sales_cache_key_is_case_insensitive(self) -> None:
        self.assertEqual(
            merge_results.cache_key({"MAKE": "MINI", "MODEL": "CLUBMAN", "YEAR": "2024"}),
            merge_results.cache_key({"MAKE": "Mini", "MODEL": "Clubman", "YEAR": "2024"}),
        )


class PipelineIntegrationTests(unittest.TestCase):
    def test_two_atoms_are_allocated_and_conserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {
                "input_csv": root / "input.csv",
                "expanded_csv": root / "expanded.csv",
                "atoms_csv": root / "atoms.csv",
                "research_queue_csv": root / "queue.csv",
                "model_year_cache_csv": root / "cache.csv",
                "allocation_overrides_csv": root / "overrides.csv",
                "atomic_output_csv": root / "atomic.csv",
                "duplicate_report_csv": root / "duplicates.csv",
                "validation_report_csv": root / "validation.csv",
                "validation_summary_json": root / "summary.json",
                "research_log": root / "research.log",
            }
            input_fields = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际", "YEAR"]
            input_rows = [
                {"MAKE": "Test", "MODEL": "One", "版本": "Base", "结构": "SUV", "YEAR": "2025", "分类": "越野车"},
                {"MAKE": "Test", "MODEL": "One", "版本": "Sport", "结构": "SUV", "YEAR": "2025", "分类": "越野车"},
            ]
            for row in input_rows:
                row["DIMENSION-ID"] = dimension_id(row)
            write_csv(
                paths["input_csv"],
                input_fields,
                input_rows,
            )
            config = {key: str(value) for key, value in paths.items()}
            config.update({"conservation_tolerance": 1, "allowed_us_scopes": ["US"]})
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

            expand_years.run(str(config_path))
            build_atoms.run(str(config_path))
            write_csv(
                paths["model_year_cache_csv"],
                CACHE_FIELDS,
                [
                    {
                        "MAKE": "Test",
                        "MODEL": "One",
                        "YEAR": "2025",
                        "MODEL_YEAR_US_SALES": "101",
                        "SALES_SCOPE": "US",
                        "SALES_PERIOD": "FULL_YEAR",
                        "SALES_SOURCE_TYPE": "OFFICIAL",
                        "SALES_SOURCE": "Test source",
                        "SOURCE_URL": "https://example.test/source",
                        "SOURCE_CONFIDENCE": "HIGH",
                    }
                ],
            )
            merge_results.run(str(config_path))
            summary = validate_sales.run(str(config_path))
            _, rows = read_csv(paths["atomic_output_csv"])

            self.assertEqual(summary["fail"], 0)
            self.assertEqual(summary["pass"], 1)
            self.assertEqual(sum(int(row["US_SALES_ESTIMATE"]) for row in rows), 101)
            self.assertTrue(all(row["ALLOCATION_METHOD"] == "EQUAL_SPLIT" for row in rows))
            self.assertTrue(all(row["ITERATION_STATUS"] == "REVIEW" for row in rows))


class AllocationWeightQueueTests(unittest.TestCase):
    def test_diff_type_distinguishes_trim_from_body(self) -> None:
        trim_group = [{"版本": "", "结构": "SUV"}, {"版本": "Quadrifoglio", "结构": "SUV"}]
        body_group = [{"版本": "", "结构": "Sedan"}, {"版本": "", "结构": "Hatchback"}]
        both_group = [{"版本": "", "结构": "Sedan"}, {"版本": "Sport", "结构": "Hatchback"}]
        self.assertEqual(awr.diff_type(trim_group), "TRIM")
        self.assertEqual(awr.diff_type(body_group), "BODY")
        self.assertEqual(awr.diff_type(both_group), "BOTH")

    def test_priority_tier_ranks_high_volume_trim_first(self) -> None:
        self.assertEqual(awr.priority_tier("TRIM", "909330"), "TIER1")
        self.assertEqual(awr.priority_tier("TRIM", "120"), "TIER2")
        self.assertEqual(awr.priority_tier("BOTH", "50000"), "TIER1")
        self.assertEqual(awr.priority_tier("BODY", "999999"), "TIER3")
        self.assertEqual(awr.priority_tier("TRIM", ""), "TIER2")

    def test_queue_key_is_stable_and_case_insensitive(self) -> None:
        first = awr.queue_key("Ford", "F-150", "2018")
        second = awr.queue_key(" ford ", "F-150", "2018")
        different = awr.queue_key("Ford", "F-150", "2019")
        self.assertEqual(first, second)
        self.assertNotEqual(first, different)

    def test_validate_allocations_requires_full_coverage_and_sum_to_one(self) -> None:
        atom_keys = ["A", "B"]
        weights = awr._validate_allocations(
            atom_keys,
            [{"SALES_ATOM_KEY": "A", "ALLOCATION_WEIGHT": "0.7"}, {"SALES_ATOM_KEY": "B", "ALLOCATION_WEIGHT": "0.3"}],
        )
        self.assertEqual(weights["A"] + weights["B"], 1)

        with self.assertRaises(SystemExit):
            awr._validate_allocations(atom_keys, [{"SALES_ATOM_KEY": "A", "ALLOCATION_WEIGHT": "1"}])

        with self.assertRaises(SystemExit):
            awr._validate_allocations(
                atom_keys,
                [{"SALES_ATOM_KEY": "A", "ALLOCATION_WEIGHT": "0.9"}, {"SALES_ATOM_KEY": "B", "ALLOCATION_WEIGHT": "0.3"}],
            )

        with self.assertRaises(SystemExit):
            awr._validate_allocations(
                atom_keys,
                [{"SALES_ATOM_KEY": "A", "ALLOCATION_WEIGHT": "-0.1"}, {"SALES_ATOM_KEY": "B", "ALLOCATION_WEIGHT": "1.1"}],
            )


if __name__ == "__main__":
    unittest.main()
