from __future__ import annotations

import csv
import logging
from pathlib import Path

from .models import VehicleRecord
from .normalizer import clean_name, normalized_key, parse_sales


LOGGER = logging.getLogger(__name__)


def load_vehicle_data(
    path: Path,
    encoding: str,
    make_column: str,
    model_column: str,
    sales_column: str,
) -> tuple[list[VehicleRecord], int]:
    records: list[VehicleRecord] = []
    input_rows = 0
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        required = {make_column, model_column, sales_column}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(sorted(missing))}")
        for row_number, row in enumerate(reader, start=2):
            input_rows += 1
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
                    sales=parse_sales(row.get(sales_column), row_number),
                )
            )
    return records, input_rows

