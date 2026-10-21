from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from decimal import Decimal

from .models import MakeMapping, MakeTotal, VehicleRecord


def aggregate_makes(records: Iterable[VehicleRecord]) -> list[MakeTotal]:
    totals: dict[str, Decimal] = {}
    displays: dict[str, str] = {}
    for record in records:
        totals[record.make_key] = totals.get(record.make_key, Decimal("0")) + record.sales
        displays.setdefault(record.make_key, record.make)
    return [MakeTotal(displays[key], key, sales) for key, sales in totals.items()]


def update_make_mappings(
    totals: list[MakeTotal],
    existing: list[MakeMapping],
    created_at: str,
    width: int,
    max_code: int,
) -> tuple[list[MakeMapping], list[MakeMapping]]:
    active_keys = {item.make_key for item in totals}
    result = [replace(item, status="ACTIVE" if item.make_key in active_keys else "INACTIVE") for item in existing]
    existing_keys = {item.make_key for item in existing}
    next_code = max((int(item.make_code) for item in existing), default=-1) + 1
    new_totals = sorted(
        (item for item in totals if item.make_key not in existing_keys),
        key=lambda item: (-item.sales, item.make_key),
    )
    if new_totals and next_code + len(new_totals) - 1 > max_code:
        raise ValueError(f"MAKE_CODE exhausted. Maximum supported MAKE_CODE is {max_code:0{width}d}.")
    added = [
        MakeMapping(item.make, item.make_key, f"{next_code + index:0{width}d}", created_at, item.sales)
        for index, item in enumerate(new_totals)
    ]
    result.extend(added)
    return result, added

