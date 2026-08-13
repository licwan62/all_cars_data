from __future__ import annotations

import hashlib
from collections.abc import Mapping


def _escape(value: str) -> str:
    return (value or "").strip().replace("%", "%25").replace("|", "%7C")


def dimension_id(row: Mapping[str, str]) -> str:
    fields = [
        ("MAKE", "MAKE"),
        ("MODEL", "MODEL"),
        ("VERSION", "版本"),
        ("STRUCTURE", "结构"),
        ("YEAR", "YEAR"),
    ]
    if (row.get("分类", "") or "").strip() == "皮卡":
        fields.extend((("CAB", "CAB"), ("BED", "BED")))
    return "|".join(
        f"{label}={_escape(row.get(source, ''))}" for label, source in fields
    )


def atom_record_id(record_id: str, year: str) -> str:
    return f"{record_id}|ATOM_YEAR={_escape(year)}"


def research_queue_key(record_id: str, issue_type: str, detail: str) -> str:
    raw = f"{record_id}\x1f{issue_type}\x1f{detail}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]
