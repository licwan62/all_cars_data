from decimal import Decimal

import pytest

from src.make_mapper import aggregate_makes, update_make_mappings
from src.models import MakeMapping, VehicleRecord


def record(make: str, model: str, sales: str) -> VehicleRecord:
    return VehicleRecord(make, model, make.casefold(), model.casefold(), Decimal(sales))


def test_initial_make_codes_follow_sales_then_name():
    totals = aggregate_makes([
        record("Toyota", "A", "1000"), record("Ford", "A", "800"), record("Honda", "A", "500")
    ])
    mappings, added = update_make_mappings(totals, [], "2026-09-17", 2, 99)
    assert [(x.make, x.make_code) for x in mappings] == [
        ("Toyota", "00"), ("Ford", "01"), ("Honda", "02")
    ]
    assert added == mappings


def test_existing_make_codes_do_not_change_when_sales_change():
    existing = [
        MakeMapping("Toyota", "toyota", "00", "2026-01-01", Decimal("1000")),
        MakeMapping("Ford", "ford", "01", "2026-01-01", Decimal("800")),
    ]
    totals = aggregate_makes([record("Ford", "A", "5000"), record("Toyota", "A", "1")])
    mappings, added = update_make_mappings(totals, existing, "2026-09-17", 2, 99)
    assert [(x.make, x.make_code) for x in mappings] == [("Toyota", "00"), ("Ford", "01")]
    assert added == []


def test_new_makes_append_in_current_sales_order():
    existing = [MakeMapping("Toyota", "toyota", "00", "2026-01-01", Decimal("1000"))]
    totals = aggregate_makes([
        record("Toyota", "A", "1"), record("Acura", "A", "5"), record("Honda", "A", "10")
    ])
    mappings, _ = update_make_mappings(totals, existing, "2026-09-17", 2, 99)
    assert [(x.make, x.make_code) for x in mappings] == [
        ("Toyota", "00"), ("Honda", "01"), ("Acura", "02")
    ]


def test_make_capacity_exhaustion():
    existing = [
        MakeMapping(f"M{i}", f"m{i}", f"{i:02d}", "2026-01-01", Decimal("1"))
        for i in range(100)
    ]
    with pytest.raises(ValueError, match="MAKE_CODE exhausted"):
        update_make_mappings(
            aggregate_makes([record("New", "A", "1")]), existing, "2026-09-17", 2, 99
        )

