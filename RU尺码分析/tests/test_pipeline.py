from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "RU尺码分析" / "pandas_analysis.py"
SOURCE = ROOT / "data" / "ru" / "0916" / "source"
spec = importlib.util.spec_from_file_location("ru_size_analysis", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RuPipelineTest(unittest.TestCase):
    def test_base_contract(self) -> None:
        base, summary = module.build_base(SOURCE)
        self.assertEqual(len(base), 13868)
        self.assertEqual(base["DIMENSION-ID"].nunique(), len(base))
        self.assertEqual(summary["dimension_groups_with_multiple_tuples"], 10)
        self.assertEqual(summary["sales_rows_without_match_key"], 304)

    def test_dimension_library_contract(self) -> None:
        from regional_size_common import DIMENSION_COLUMNS, build_dimension_library
        from id_scheme import dimension_id

        base, _ = module.build_base(SOURCE)
        library, _ = build_dimension_library(base)
        self.assertEqual(len(library), 13850)
        self.assertEqual(list(library.columns), DIMENSION_COLUMNS)
        self.assertTrue(library["DIMENSION-ID"].is_unique)
        self.assertEqual(
            library["DIMENSION-ID"].tolist(),
            [dimension_id(row) for row in library.to_dict("records")],
        )


if __name__ == "__main__":
    unittest.main()
