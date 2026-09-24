from __future__ import annotations

import validate_pipeline_structure as validator


def node(node_id, path, layer, upstream=()):
    return {"id": node_id, "path": path, "layer": layer, "upstream": list(upstream)}


def test_layers_must_match_longest_upstream_chain_and_prefix():
    nodes = [node("a", "00.a", 0), node("b", "01.b", 1, ["a"]), node("c", "02.c", 2, ["a", "b"])]
    assert validator.check_layers(nodes) == []

    wrong = [node("a", "00.a", 0), node("c", "01.c", 1, ["a"]), node("d", "01.d", 2, ["c"])]
    errors = validator.check_layers(wrong)
    assert any("d" in error and "02." in error for error in errors)


def test_cycle_is_reported():
    nodes = [node("a", "00.a", 0, ["b"]), node("b", "01.b", 1, ["a"])]
    assert "依赖存在环" in validator.check_layers(nodes)[0]


def test_repository_pipeline_is_valid():
    assert validator.main() == 0


def test_pipeline_manifest_is_owned_by_last_node():
    payload = __import__("json").loads(validator.MANIFEST.read_text(encoding="utf-8"))
    assert payload["governance"]["manifest_owner"] == "link-analysis"
    assert payload["governance"]["manifest_owner_path"] == "D2.链接分析"


def test_code_layout_rejects_loose_scripts_and_missing_entries(tmp_path, monkeypatch):
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    project = tmp_path / "A1.demo"
    (project / "src").mkdir(parents=True)
    (project / "tests").mkdir()
    (project / "src" / "run.py").write_text("", encoding="utf-8")
    good = {"id": "demo", "path": "A1.demo", "code_dir": "src", "run": ["python src/run.py"], "tests": "tests"}
    assert validator.check_code_layout([good]) == []

    (project / "run.py").write_text("", encoding="utf-8")
    missing = {**good, "run": ["python src/missing.py"], "tests": "tests_py"}
    errors = validator.check_code_layout([missing])
    assert any("run.py" in error and "根目录" in error for error in errors)
    assert any("src/missing.py" in error for error in errors)
    assert any("tests_py" in error for error in errors)
    assert any("缺少 code_dir" in error for error in validator.check_code_layout([{"id": "x", "path": "A1.demo"}]))
