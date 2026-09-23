import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "apply_model_semantic_repairs.py"
SPEC = importlib.util.spec_from_file_location("apply_model_semantic_repairs", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_repair_mapping_has_unique_existing_keys():
    rules = json.loads(MODULE.RULES.read_text(encoding="utf-8"))["记录"]
    _, rows = MODULE.read_csv(MODULE.RAW)
    keys = {row["差评汇总主键"] for row in rows}
    assert rules
    assert set(rules) <= keys


def test_repair_mapping_contains_required_evidence():
    rules = json.loads(MODULE.RULES.read_text(encoding="utf-8"))["记录"]
    for repair in rules.values():
        assert repair["车型"].strip()
        assert repair["依据"].strip()


def test_size_foreign_keys_resolve_to_raw_rows():
    _, raw_rows = MODULE.read_csv(MODULE.RAW)
    _, size_rows = MODULE.read_csv(MODULE.SIZE)
    raw_keys = {row["差评汇总主键"] for row in raw_rows}
    assert all(row["差评汇总外键"] in raw_keys for row in size_rows)
