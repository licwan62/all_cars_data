"""Private native-format view for legacy computation regression tests.

Current JSON output supplies current fixture values. Explicit historical research
fixtures listed in pipeline.json remain historical, and no CSV fixture is written
into the real repository's node outputs.
"""
from __future__ import annotations
import copy
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from node_paths import node_output, node_page
from json_interface import materialize, legacy_name
from artifact_batch import sha256


def prepare(root, destination):
    payload = json.loads((root / "pipeline.json").read_text(encoding="utf-8"))
    native = copy.deepcopy(payload)
    by_id = {n["id"]: n for n in payload["nodes"]}
    for folder in ("lib", "scripts"):
        shutil.copytree(root / folder, destination / folder, ignore=shutil.ignore_patterns("__pycache__"))
    for node in native["nodes"]:
        original = by_id[node["id"]]
        source = root / node["path"]
        target = destination / node["path"]
        target.mkdir(parents=True, exist_ok=True)
        folders = []
        for value in (node.get("code_dir"), node.get("tests"), "data", "src", "code", "scripts"):
            folders.extend([value] if isinstance(value, str) else value or [])
        for folder in dict.fromkeys(folders):
            if (source / folder).is_dir():
                shutil.copytree(source / folder, target / folder, dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        for file in source.iterdir():
            if file.is_file():
                shutil.copy2(file, target / file.name)
        for file in (source / "research").rglob("*.py"):
            relative = file.relative_to(source)
            (target / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target / relative)
        (target / "output").mkdir(exist_ok=True)
        # Preserve auxiliary, unregistered native results used by older research
        # tests. The registered interface values below always come from JSON.
        if node_output(root, original).is_dir():
            shutil.copytree(node_output(root, original), target / "output", dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("*.html", "html_manifest.json"))
        legacy = root / "work/legacy-output" / node["id"]
        if legacy.is_dir():
            shutil.copytree(legacy, target / "output", dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("*.html", "html_manifest.json"))
        for name in original.get("outputs", []):
            old = legacy_name(original, name)
            if old.endswith(".xlsx"):
                continue  # Legacy workbook node has no computation tests.
            materialize(node_output(root, original) / name, target / "output" / old)
        manifest_path = target / "output/manifest.json"
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for item in manifest.get("deliverables", []):
                item["file"] = legacy_name(original, item["file"])
                path = target / "output" / item["file"]
                if path.is_file():
                    item["sha256"] = sha256(path)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        node["outputs"] = [legacy_name(original, name) for name in original.get("outputs", [])]
        node["run"] = node.get("engine_run", [])
        node.pop("output_dir", None)
        node.pop("html_at_root", None)
        for item in node.get("inputs", []):
            item["file"] = legacy_name(by_id[item["node"]], item["file"])
    (destination / "pipeline.json").write_text(json.dumps(native, ensure_ascii=False), encoding="utf-8")
    for relative in payload.get("verification_contract", {}).get("historical_test_fixtures", []):
        source = (root / relative).resolve()
        source.relative_to(root.resolve())
        target = destination / relative
        target.resolve().relative_to(destination.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
