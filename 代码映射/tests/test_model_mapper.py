from decimal import Decimal

import pytest

from src.make_mapper import aggregate_makes, update_make_mappings
from src.model_mapper import aggregate_models, update_model_mappings
from src.models import MakeMapping, ModelMapping, VehicleRecord


def record(make: str, model: str, sales: str) -> VehicleRecord:
    return VehicleRecord(make, model, make.casefold(), model.casefold(), Decimal(sales))


def test_model_codes_restart_for_each_make_and_aggregate_duplicates():
    records = [
        record("Toyota", "Corolla", "600"), record("Toyota", "Corolla", "400"),
        record("Toyota", "Camry", "800"), record("Honda", "Civic", "900"),
        record("Honda", "Accord", "700"),
    ]
    makes, _ = update_make_mappings(aggregate_makes(records), [], "2026-09-17", 2, 99)
    models, _ = update_model_mappings(aggregate_models(records), [], makes, "2026-09-17", 2, 99)
    found = {(x.make, x.model): x.model_code for x in models}
    assert found == {
        ("Toyota", "Corolla"): "00", ("Toyota", "Camry"): "01",
        ("Honda", "Civic"): "00", ("Honda", "Accord"): "01",
    }


def test_new_model_appends_and_missing_model_is_retained():
    makes = [MakeMapping("Toyota", "toyota", "00", "2026-01-01", Decimal("1"))]
    existing = [
        ModelMapping("Toyota", "Corolla", "toyota", "corolla", "00", "00", "2026-01-01", Decimal("1")),
        ModelMapping("Toyota", "Avalon", "toyota", "avalon", "00", "01", "2026-01-01", Decimal("1")),
    ]
    totals = aggregate_models([record("Toyota", "Corolla", "1"), record("Toyota", "RAV4", "5")])
    mappings, added = update_model_mappings(totals, existing, makes, "2026-09-17", 2, 99)
    assert [(x.model, x.model_code, x.status) for x in mappings] == [
        ("Corolla", "00", "ACTIVE"), ("Avalon", "01", "INACTIVE"), ("RAV4", "02", "ACTIVE")
    ]
    assert [(x.model, x.model_code) for x in added] == [("RAV4", "02")]


def test_model_capacity_exhaustion_is_scoped_to_make():
    makes = [MakeMapping("Toyota", "toyota", "00", "2026-01-01", Decimal("1"))]
    existing = [
        ModelMapping("Toyota", f"M{i}", "toyota", f"m{i}", "00", f"{i:02d}", "2026-01-01", Decimal("1"))
        for i in range(100)
    ]
    with pytest.raises(ValueError, match="MODEL_CODE exhausted for Toyota"):
        update_model_mappings(
            aggregate_models([record("Toyota", "New", "1")]), existing, makes, "2026-09-17", 2, 99
        )

