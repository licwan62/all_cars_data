"""JSON transport for node handoffs; computation adapters stay inside scratch space.

Tables use ordered columns + string rows, preserving blank cells, leading zeroes,
duplicate headers and decimal spelling without type inference.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path

SCHEMA = "vehicle-pipeline/table-v1"
TEXT_SCHEMA = "vehicle-pipeline/text-v1"
WORKBOOK_SCHEMA = "vehicle-pipeline/workbook-v1"


def json_name(name):
    return str(Path(name).with_suffix(".json")).replace("\\", "/")


def dumps(payload):
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n"


def convert(path):
    path = Path(path)
    raw = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".json":
        json.loads(raw)  # Validate, but preserve existing JSON bytes and schema.
        return raw
    origin = {"source_format": suffix[1:], "source_sha256": hashlib.sha256(raw).hexdigest()}
    if suffix in {".csv", ".tsv"}:
        reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), delimiter="\t" if suffix == ".tsv" else ",")
        payload = {"schema": SCHEMA, "columns": next(reader, []), "rows": list(reader), **origin}
    elif suffix == ".xlsx":
        import openpyxl
        book = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=False)
        sheets = []
        try:
            for sheet in book:
                rows = [["" if c is None else str(c) for c in row] for row in sheet.iter_rows(values_only=True)]
                sheets.append({"name": sheet.title, "columns": rows[0] if rows else [], "rows": rows[1:]})
        finally:
            book.close()
        payload = {"schema": WORKBOOK_SCHEMA, "sheets": sheets, **origin,
                   "limitation": "历史工作簿的单元格值/公式文本；不承诺保留 Excel 排版或重算公式。原工作簿保存在原 artifact。"}
    else:
        payload = {"schema": TEXT_SCHEMA, "text": raw.decode("utf-8-sig"), **origin}
    return dumps(payload).encode("utf-8")


def load_table(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError(f"不是统一 JSON 表格：{path}")
    columns, rows = payload["columns"], payload["rows"]
    if not isinstance(columns, list) or not isinstance(rows, list) or any(not isinstance(r, list) for r in rows):
        raise ValueError(f"JSON 表格结构无效：{path}")
    return payload


def csv_bytes(payload, delimiter=","):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter=delimiter, lineterminator="\n")
    writer.writerow(payload["columns"])
    writer.writerows(payload["rows"])
    return stream.getvalue().encode("utf-8-sig")


def materialize(source, destination):
    """Translate a JSON handoff into a private computation input, never a node output."""
    source, destination = Path(source), Path(destination)
    raw = source.read_bytes()
    payload = json.loads(raw)
    if source.suffix == destination.suffix:
        value = raw
    elif isinstance(payload, dict) and payload.get("schema") == SCHEMA:
        value = csv_bytes(payload, "\t" if destination.suffix == ".tsv" else ",")
    elif isinstance(payload, dict) and payload.get("schema") == TEXT_SCHEMA:
        value = payload["text"].encode("utf-8")
    else:
        raise ValueError(f"不能物化计算输入：{source} → {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(value)


def legacy_name(node, name):
    return next((old for old, new in node.get("interface_files", {}).items() if new == name), name)


def manifest_hashes(manifest):
    """Compare old upstream evidence without claiming it used the new JSON version."""
    result = {}
    for item in (manifest or {}).get("deliverables", []):
        result[item["file"]] = item["sha256"]
        if item.get("legacy_file") and item.get("legacy_sha256"):
            result[item["legacy_file"]] = item["legacy_sha256"]
    return result


def legacy_metadata(path, node, name):
    old = legacy_name(node, name)
    if old == name:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return {"legacy_file": old, "legacy_sha256": payload["source_sha256"]}


def table_row_count(path):
    if Path(path).suffix == ".json":
        value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        if isinstance(value, dict) and value.get("schema") == SCHEMA:
            return len(value["rows"])
    return None
