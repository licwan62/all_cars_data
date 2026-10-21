import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'scripts/audit_year_names.py'
spec = importlib.util.spec_from_file_location('audit_year_names', path)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class YearNamesTest(unittest.TestCase):
    def test_preserve_gaps_and_roundtrip(self):
        value = '1964-1974/1978-1983'
        self.assertEqual(audit.compact(audit.years(value)), value)
        self.assertNotIn(1975, audit.years(value))

    def test_detect_shared_gap_and_boundary(self):
        def row(sku, y):
            return {'SKU_NAME': sku, '聚类ID': sku, '适配车型': 'Oldsmobile Cutlass', '尺码': '4M', '年份': y}
        self.assertEqual(len(audit.overlaps([row('a','1978/1980/1982'),row('b','1979-1981')], '年份')), 1)
        self.assertEqual(audit.overlaps([row('a','1978/1982'),row('b','1979/1981')], '年份'), [])
        self.assertEqual(len(audit.overlaps([row('a','1978-1980'),row('b','1980-1981')], '年份')), 1)

    def test_invalid_years_fail(self):
        for value in ['1980-1970','unknown','']:
            with self.assertRaises(ValueError):
                audit.years(value)


if __name__ == '__main__':
    unittest.main()
