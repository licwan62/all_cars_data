from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class VehicleRecord:
    make: str
    model: str
    make_key: str
    model_key: str
    sales: Decimal


@dataclass(frozen=True)
class MakeTotal:
    make: str
    make_key: str
    sales: Decimal


@dataclass(frozen=True)
class ModelTotal:
    make: str
    model: str
    make_key: str
    model_key: str
    sales: Decimal


@dataclass(frozen=True)
class MakeMapping:
    make: str
    make_key: str
    make_code: str
    created_at: str
    initial_sales: Decimal
    status: str = "ACTIVE"


@dataclass(frozen=True)
class ModelMapping:
    make: str
    model: str
    make_key: str
    model_key: str
    make_code: str
    model_code: str
    created_at: str
    initial_sales: Decimal
    status: str = "ACTIVE"

