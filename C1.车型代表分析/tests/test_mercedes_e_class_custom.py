from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze_mercedes_e_class_custom import active_rows, cluster_minimum_envelopes, dimension_codes, sku_code


def row(identifier: str, length: int, width: int, height: int) -> dict[str, str]:
    return {"DIMENSION-ID": identifier, "L-MM": str(length), "W-MM": str(width), "H-MM": str(height)}


def test_clusters_only_use_lwh_envelope_and_length_boundary() -> None:
    limits = {"L-MM": 150, "W-MM": 100, "H-MM": 80}
    groups = cluster_minimum_envelopes([
        row("a", 4800, 1800, 1450), row("b", 4950, 1900, 1500), row("c", 4951, 1900, 1500),
    ], limits)
    assert len(groups) == 2
    assert sorted(len(group.rows) for group in groups) == [1, 2]


def test_active_rows_can_limit_to_sedan(tmp_path: Path) -> None:
    source = tmp_path / "source.csv"
    source.write_text("MAKE,MODEL,结构,L-MM,W-MM,H-MM,DIMENSION-ID\nMercedes-Benz,E-Class,Sedan,4800,1800,1450,a\nMercedes-Benz,E-Class,Wagon,4800,1800,1450,b\n", encoding="utf-8")
    assert [row["DIMENSION-ID"] for row in active_rows(source, "Mercedes-Benz", "E-Class", "Sedan")] == ["a"]


def test_dimension_codes_uses_code_mapping_output(tmp_path: Path) -> None:
    source = tmp_path / "codes.csv"
    source.write_text("DIMENSION-ID,DIMENSION-CODE\na,23019495\n", encoding="utf-8")
    assert dimension_codes(source) == {"a": "23019495"}


def test_sku_code_uses_one_sku_year_range() -> None:
    rows = (row("a", 4800, 1800, 1450) | {"YEAR": "1994-1995"}, row("b", 4801, 1800, 1450) | {"YEAR": "2003-2009"})
    assert sku_code(rows, {"a": "23019495", "b": "23010309"}) == "23019409"
