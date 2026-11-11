"""Build the final website from registered JSON interfaces, without sibling repos."""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
SRC = PROJECT / "src"
sys.path[:0] = [str(SRC), str(SRC / "tools"), str(ROOT / "lib")]
from artifact_batch import RunBatch, sha256
from json_interface import legacy_name, materialize
from node_paths import node_output
from tools.build_publish_site import build_staged_site, site_file_list
from tools.import_compressed_tables import import_lines
from tools.site_promote import promote_site
from tools.validate_publish_site import validate_publish_site

NODE_ID = "website-publish"
RESULT = "网站构建清单.json"


def configuration():
    nodes = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))["nodes"]
    by_id = {n["id"]: n for n in nodes}
    return by_id[NODE_ID], by_id


def source_hashes():
    return {p.relative_to(PROJECT).as_posix(): sha256(p)
            for folder in (SRC, PROJECT / "data", PROJECT / "tests")
            for p in sorted(folder.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def pin_inputs(batch, node, by_id, destination):
    """Verify JSON first; materialize private CSV and translate proven legacy hashes.

    Historical format migrations retain the original CSV SHA. That SHA must match
    A1's recorded input before a private CSV digest can replace it in the adapter.
    Official manifests and history are never rewritten.
    """
    manifests, digests, translated = {}, {}, {}
    for entry in node["inputs"]:
        owner, name = entry["node"], entry["file"]
        upstream = by_id[owner]
        output = node_output(ROOT, upstream)
        if owner not in manifests:
            manifest_path = output / "manifest.json"
            digests[manifest_path] = sha256(manifest_path)
            manifests[owner] = json.loads(manifest_path.read_text(encoding="utf-8"))
        published = next((d for d in manifests[owner]["deliverables"] if d["file"] == name), None)
        source = output / name
        if not published or sha256(source) != published["sha256"]:
            raise ValueError(f"Unpublished or changed JSON input: {owner}/{name}")
        batch.input(source)
        if batch.inputs[-1]["sha256"] != published["sha256"]:
            raise ValueError(f"Input changed while pinning: {source}")
        digests[source] = published["sha256"]
        old = legacy_name(upstream, name)
        target = destination / owner / old
        materialize(source, target)
        translated[owner, name] = (old, sha256(target), published)

    # A1 must be based on these very A0 values, including pre-JSON provenance.
    a1 = manifests["size-compression"]
    a0_basis = next((u for u in a1.get("upstream", []) if u["node"] == "size-calculation"), {})
    basis_files = {f["file"]: f["sha256"] for f in a0_basis.get("files", [])}
    for (owner, name), (old, digest, item) in translated.items():
        if owner != "size-calculation" or "全量" not in name:
            continue
        current = basis_files.get(name) == item["sha256"]
        legacy = (item.get("legacy_file") == old and item.get("legacy_sha256")
                  and basis_files.get(old) == item["legacy_sha256"])
        if not (current or legacy):
            raise ValueError(f"A1 does not reference current A0: {name}; rebuild A1 first")

    for owner, manifest in manifests.items():
        view = copy.deepcopy(manifest)
        view["deliverables"] = [dict(item, file=old, sha256=digest)
                                for (up, name), (old, digest, item) in translated.items() if up == owner]
        for upstream in view.get("upstream", []):
            for entry in upstream.get("files", []):
                for (up, name), (old, digest, item) in translated.items():
                    if upstream["node"] != up or entry["file"] not in {old, name}:
                        continue
                    expected = item["sha256"] if entry["file"] == name else item.get("legacy_sha256")
                    if entry["sha256"] != expected:
                        raise ValueError(f"{owner} uses stale {up}/{name}")
                    entry.update(file=old, sha256=digest)
        if owner == "size-compression":
            for upstream in view.get("upstream", []):
                if upstream["node"] == "size-calculation":
                    upstream["files"] = [{"file": old, "sha256": digest}
                                         for (up, name), (old, digest, _) in translated.items()
                                         if up == "size-calculation"]
        (destination / owner / "manifest.json").write_text(json.dumps(view, ensure_ascii=False), encoding="utf-8")
    verify_inputs(digests)
    return digests


def verify_inputs(digests):
    for path, digest in digests.items():
        if not path.is_file() or sha256(path) != digest:
            raise ValueError(f"Input changed during build: {path}")


def command(script, *args):
    subprocess.run([sys.executable, str(SRC / "tools" / script), *map(str, args)], cwd=PROJECT, check=True)


def build():
    node, by_id = configuration()
    data = PROJECT / "data"
    work_root = ROOT / "work" / "website"
    work_root.mkdir(parents=True, exist_ok=True)
    original_sources = source_hashes()
    with RunBatch.create(PROJECT / "artifacts", "website-build", data) as batch:
        with tempfile.TemporaryDirectory(prefix="build-", dir=work_root) as temporary:
            work = Path(temporary)
            digests = pin_inputs(batch, node, by_id, work / "upstream")
            a0 = work / "upstream" / "size-calculation"
            a1 = work / "upstream" / "size-compression"
            sales = work / "upstream" / "sales-estimation"
            runtime = work / "pipeline.json"
            import_lines(a0, a1, data / "pipeline.yaml", work / "tables", runtime, work / "compressed")
            command("build_user_size_json.py", "--compress-root", work / "compressed", "--config", runtime,
                    "--rules", data / "user-size-rules.json", "--size-code-map", a0 / "US/新旧尺码对应.csv",
                    "--type-abbreviations", data / "type-structure-abbreviations.json",
                    "--type-confirm", data / "type-manual-confirm.csv", "--ai-config", data / "ai-user-size.yaml",
                    "--type-pending-output", work / "type-pending.csv", "--output", work / "user-size.json")
            command("export_user_size_json_tables.py", "--input", work / "user-size.json", "--output-root", work / "csv")
            command("generate_all_html.py", "--export-root", work / "csv", "--output-root", work / "html",
                    "--config-path", data / "html-style.yaml", "--html-script", SRC / "chart_generator/tsv_to_size_chart_html.py")
            staged = build_staged_site(SRC / "skeleton", work / "html", runtime, data / "html-style.yaml",
                                       work / "site", a0, a1, sales)
            verify_inputs(digests)
            if source_hashes() != original_sources:
                raise ValueError("Website source/rules changed during build")
            files = site_file_list(staged)
            archive = batch.extra("website.zip", compress=False)
            with ZipFile(archive, "x", compression=ZIP_DEFLATED, compresslevel=6) as bundle:
                for item in files:
                    info = ZipInfo(item["path"], date_time=(2020, 1, 1, 0, 0, 0))
                    info.compress_type = ZIP_DEFLATED
                    bundle.writestr(info, (staged / item["path"]).read_bytes())
            shutil.copy2(work / "type-pending.csv", batch.extra("type-pending.csv", compress=False))
            result = {"schema": "vehicle-pipeline/website-v1", "status": "validated",
                      "version": batch.version, "publisher": "pipeline_carstable_to_webapp",
                      "archive": {"file": archive.relative_to(ROOT).as_posix(), "sha256": sha256(archive)},
                      "files": files, "inputs": {p.relative_to(ROOT).as_posix(): d for p, d in digests.items()},
                      "sources": original_sources, "deployment": "not-published"}
            batch.output(RESULT).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            batch.finish({"status": "passed", "transport": "json", "site_files": len(files)},
                         publish_to=node_output(ROOT, node))
            promote_site(staged, work_root / "public", validate_publish_site)
    print(f"Validated website: {work_root / 'public'} ({len(files)} files); no remote publication")


def verified_candidate(destination):
    node, _ = configuration()
    result_file = node_output(ROOT, node) / RESULT
    release = json.loads((node_output(ROOT, node) / "manifest.json").read_text(encoding="utf-8"))
    expected = next(d["sha256"] for d in release["deliverables"] if d["file"] == RESULT)
    if sha256(result_file) != expected:
        raise ValueError("Candidate is not locally released; use scripts/website.py build")
    result = json.loads(result_file.read_text(encoding="utf-8"))
    verify_inputs({ROOT / p: digest for p, digest in result["inputs"].items()})
    if source_hashes() != result["sources"]:
        raise ValueError("Source or rules changed since validation; rebuild before publishing")
    archive = (ROOT / result["archive"]["file"]).resolve()
    archive.relative_to((PROJECT / "artifacts").resolve())
    if sha256(archive) != result["archive"]["sha256"]:
        raise ValueError("Candidate archive SHA mismatch")
    with ZipFile(archive) as bundle:
        expected_files = {f["path"] for f in result["files"]}
        if len(bundle.namelist()) != len(expected_files) or set(bundle.namelist()) != expected_files:
            raise ValueError("Candidate archive inventory mismatch")
        for name in bundle.namelist():
            (destination / name).resolve().relative_to(destination.resolve())
        bundle.extractall(destination)
    if site_file_list(destination) != result["files"]:
        raise ValueError("Candidate site SHA mismatch")
    validate_publish_site(destination)
    return result


def publish(ecs_only=False):
    from tools.publish_site_copy import main as publish_main
    report = ROOT / "reports" / "website"
    report.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    status = report / (datetime.now().strftime("%Y%m%d-%H%M%S-%f") + "-publish.json")
    args = ["--config", str(PROJECT / "data/pipeline.yaml"), "--status-file", str(status)]
    if ecs_only:
        code = publish_main([*args, "--ecs-only"])
    else:
        with tempfile.TemporaryDirectory(prefix="website-release-") as temp:
            verified_candidate(Path(temp))
            code = publish_main([*args, "--source", temp])
    if code:
        raise RuntimeError(f"Publication failed; see {status}")
    result = json.loads(status.read_text(encoding="utf-8"))
    if result.get("ecs", {}).get("status") != "published" or (not ecs_only and result.get("status") != "published"):
        raise RuntimeError(f"Dual publication incomplete; see {status}")
    print(f"Dual publication verified: {status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=["build", "publish", "ecs-only"], default="build")
    args = parser.parse_args()
    if args.action == "build":
        build()
    else:
        publish(ecs_only=args.action == "ecs-only")
