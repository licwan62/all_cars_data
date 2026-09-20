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
