from __future__ import annotations

import hashlib
from collections.abc import Mapping


COUNTRY_CODES = frozenset({"US", "EU", "RU"})


def _clean(value: str) -> str:
    return (value or "").strip()


def dimension_id(row: Mapping[str, str]) -> str:
    """Return the compact, human-readable vehicle dimension identity.

    Values keep the established business order. Empty optional values are
    omitted, so a blank version does not leave doubled spaces in the ID.
    Pickup identities append CAB and BED after the year as before.
    """
    fields = ["MAKE", "MODEL", "版本", "结构", "YEAR"]
    if (row.get("分类", "") or "").strip() == "皮卡":
        fields.extend(("CAB", "BED"))
    return " ".join(value for field in fields if (value := _clean(row.get(field, ""))))


def append_country_code(record_id: str, country_code: str) -> str:
    """Append a supported country code to a DIMENSION-ID exactly once."""
    value = _clean(record_id)
    code = _clean(country_code).upper()
    if not value:
        raise ValueError("DIMENSION-ID 不能为空")
    if code not in COUNTRY_CODES:
        raise ValueError(f"不支持的国家代号：{country_code}")
    last_token = value.rsplit(" ", 1)[-1].upper()
    if last_token in COUNTRY_CODES:
        if last_token != code:
            raise ValueError(f"DIMENSION-ID 已带其他国家代号：{record_id}")
        return value
    return f"{value} {code}"


def base_dimension_id(record_id: str) -> str:
    """Return the shared base ID by removing a supported regional suffix."""
    value = _clean(record_id)
    if not value:
        return value
    head, separator, tail = value.rpartition(" ")
    return head if separator and tail.upper() in COUNTRY_CODES else value


def atom_record_id(record_id: str, year: str) -> str:
    return f"{record_id}|ATOM_YEAR={_clean(year)}"


def research_queue_key(record_id: str, issue_type: str, detail: str) -> str:
    raw = f"{record_id}\x1f{issue_type}\x1f{detail}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]
