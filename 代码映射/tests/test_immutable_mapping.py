from decimal import Decimal

import pytest

from src.models import MakeMapping, ModelMapping
from src.validator import validate_immutable


def test_changed_make_code_is_rejected():
    old = [MakeMapping("Toyota", "toyota", "00", "2026-01-01", Decimal("1"))]
    new = [MakeMapping("Toyota", "toyota", "01", "2026-01-01", Decimal("1"))]
    with pytest.raises(ValueError, match="Immutable mapping violation"):
        validate_immutable(old, new, [], [])


def test_changed_model_code_is_rejected():
    make = MakeMapping("Toyota", "toyota", "00", "2026-01-01", Decimal("1"))
    old = [ModelMapping("Toyota", "Corolla", "toyota", "corolla", "00", "00", "2026-01-01", Decimal("1"))]
    new = [ModelMapping("Toyota", "Corolla", "toyota", "corolla", "00", "01", "2026-01-01", Decimal("1"))]
    with pytest.raises(ValueError, match="Immutable mapping violation"):
        validate_immutable([make], [make], old, new)

