from __future__ import annotations

import csv
import logging
from decimal import Decimal
from pathlib import Path

from .models import VehicleRecord
from .normalizer import clean_name, normalized_key, parse_sales


LOGGER = logging.getLogger(__name__)


def load_vehicle_data(
    path: Path,
    encoding: str,
    make_column: str,
    model_column: str,
    sales_column: str = "",
    dimension_id_column: str = "",
    year_column: str = "",
    region_suffix: str = "",
) -> tuple[list[VehicleRecord], int]:
    records: list[VehicleRecord] = []
    input_rows = 0
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        required = {make_column, model_column}
        if dimension_id_column:
            required.add(dimension_id_column)
        if year_column:
            required.add(year_column)
        # 销量列可选：尺寸库没有销量，缺列时按 0 处理，新增编码按名称升序分配。
        has_sales = bool(sales_column) and sales_column in (reader.fieldnames or [])
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(sorted(missing))}")
        for row_number, row in enumerate(reader, start=2):
            input_rows += 1
            dimension_id = clean_name(row.get(dimension_id_column)) if dimension_id_column else ""
            if region_suffix and not dimension_id.endswith(region_suffix):
                continue
            make = clean_name(row.get(make_column))
            model = clean_name(row.get(model_column))
            if not make or not model:
                LOGGER.warning("Skipping row %s because MAKE or MODEL is empty.", row_number)
                continue
            records.append(
                VehicleRecord(
                    make=make,
                    model=model,
                    make_key=normalized_key(make),
                    model_key=normalized_key(model),
                    sales=parse_sales(row.get(sales_column), row_number) if has_sales else Decimal("0"),
                    dimension_id=dimension_id,
                    year=clean_name(row.get(year_column)) if year_column else "",
                )
            )
    return records, input_rows

