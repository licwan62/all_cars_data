from __future__ import annotations

import hashlib
from collections.abc import Mapping


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


def atom_record_id(record_id: str, year: str) -> str:
    return f"{record_id}|ATOM_YEAR={_clean(year)}"


def research_queue_key(record_id: str, issue_type: str, detail: str) -> str:
    raw = f"{record_id}\x1f{issue_type}\x1f{detail}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]
