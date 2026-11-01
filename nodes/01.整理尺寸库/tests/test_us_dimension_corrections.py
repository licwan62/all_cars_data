import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from us_dimension_corrections import apply_corrections


def test_correction_preserves_identity_and_rejects_changed_upstream():
    rows = [{"DIMENSION-ID": "id", "YEAR": "2009", "结构": "Convertible", "H-IN": "50.9"}]
    rules = {"corrections": [{"DIMENSION-ID": "id", "expected": {"YEAR": "2009", "结构": "Convertible", "H-IN": "50.9"},
                              "changes": {"H-IN": "50.1"}, "reason": "reviewed",
                              "sources": [{"url": "https://example.com/spec"}]}]}
    corrected = apply_corrections(rows, rules)
    assert corrected == [{**rows[0], "H-IN": "50.1"}]
    assert rows[0]["H-IN"] == "50.9"
    rows[0]["H-IN"] = "51.0"
    with pytest.raises(ValueError, match="前置条件"):
        apply_corrections(rows, rules)
