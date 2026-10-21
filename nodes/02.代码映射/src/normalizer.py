from __future__ import annotations

import logging
import unicodedata
from decimal import Decimal, InvalidOperation


LOGGER = logging.getLogger(__name__)


def clean_name(value: object) -> str:
    if value is None:
        return ""
    return unicodedata.normalize("NFKC", str(value)).strip()


def normalized_key(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def parse_sales(value: object, row_number: int) -> Decimal:
    text = "" if value is None else str(value).strip()
    if not text:
        return Decimal("0")
    text = text.replace(",", "")
    try:
        result = Decimal(text)
        if not result.is_finite():
            raise InvalidOperation
        return result
    except InvalidOperation:
        LOGGER.warning("Row %s has invalid sales %r; using 0.", row_number, value)
        return Decimal("0")


def decimal_text(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(value.quantize(Decimal("1")))
    return format(value.normalize(), "f")

