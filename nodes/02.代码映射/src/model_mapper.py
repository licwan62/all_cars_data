from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from decimal import Decimal

from .models import MakeMapping, ModelMapping, ModelTotal, VehicleRecord


def aggregate_models(records: Iterable[VehicleRecord]) -> list[ModelTotal]:
    totals: dict[tuple[str, str], Decimal] = {}
    displays: dict[tuple[str, str], tuple[str, str]] = {}
    for record in records:
        key = (record.make_key, record.model_key)
        totals[key] = totals.get(key, Decimal("0")) + record.sales
        displays.setdefault(key, (record.make, record.model))
    return [ModelTotal(*displays[key], *key, sales) for key, sales in totals.items()]


def update_model_mappings(
    totals: list[ModelTotal],
    existing: list[ModelMapping],
    makes: list[MakeMapping],
    created_at: str,
    width: int,
    max_code: int,
) -> tuple[list[ModelMapping], list[ModelMapping]]:
    active_keys = {(item.make_key, item.model_key) for item in totals}
    result = [
        replace(item, status="ACTIVE" if (item.make_key, item.model_key) in active_keys else "INACTIVE")
        for item in existing
    ]
    existing_keys = {(item.make_key, item.model_key) for item in existing}
    make_by_key = {item.make_key: item for item in makes}
    totals_by_make: dict[str, list[ModelTotal]] = {}
    for item in totals:
        if (item.make_key, item.model_key) not in existing_keys:
            totals_by_make.setdefault(item.make_key, []).append(item)

    added: list[ModelMapping] = []
    for make_key in sorted(totals_by_make, key=lambda key: int(make_by_key[key].make_code)):
        used = [int(item.model_code) for item in existing if item.make_key == make_key]
        next_code = max(used, default=-1) + 1
        new_totals = sorted(totals_by_make[make_key], key=lambda item: (-item.sales, item.model_key))
        if next_code + len(new_totals) - 1 > max_code:
            make_name = make_by_key[make_key].make
            raise ValueError(
                f"MODEL_CODE exhausted for {make_name}. Maximum supported MODEL_CODE is {max_code:0{width}d}."
            )
        make_mapping = make_by_key[make_key]
        for index, item in enumerate(new_totals):
            added.append(
                ModelMapping(
                    make=make_mapping.make,
                    model=item.model,
                    make_key=make_key,
                    model_key=item.model_key,
                    make_code=make_mapping.make_code,
                    model_code=f"{next_code + index:0{width}d}",
                    created_at=created_at,
                    initial_sales=item.sales,
                )
            )
    result.extend(added)
    return result, added

