import json
from pathlib import Path
import pytest
import artifact_batch as ab
from content_store import ContentIndex, resolve_source
from artifact_refs import record_references


def test_cross_node_and_cross_name_reuse_keeps_current_provenance(tmp_path, monkeypatch):
    monkeypatch.setattr(ab,"REPO_ROOT",tmp_path)
    first=ab.RunBatch.create(tmp_path/"nodes/A0.a/artifacts","one")
    first.output("first.csv").write_bytes(b"id\n001\n")
    r1=first.finish()
    second=ab.RunBatch.create(tmp_path/"nodes/A1.b/artifacts","two")
    source=tmp_path/"new-input.txt";source.write_bytes(b"new provenance")
    second.input(source)
    second.output("different.csv").write_bytes(b"id\n001\n")
    r2=second.finish(publish_to=tmp_path/"nodes/A1.b/output")
    assert r2["outputs"][0]["artifact_file"]==r1["outputs"][0]["artifact_file"]
    assert not list((second.directory/"output").glob("*.csv"))
    assert r2["inputs"][0]["sha256"]==ab.sha256(source)
    assert (tmp_path/"nodes/A1.b/output/different.csv").read_bytes()==b"id\n001\n"
    assert r1["batch"] in record_references(r2)


def test_corrupt_and_failed_sources_are_not_reused(tmp_path,monkeypatch):
    monkeypatch.setattr(ab,"REPO_ROOT",tmp_path)
    batch=ab.RunBatch.create(tmp_path/"nodes/A0.a/artifacts","one")
    out=batch.output("x.txt");out.write_bytes(b"good");r=batch.finish()
    out.write_bytes(b"evil")
    second=ab.RunBatch.create(tmp_path/"nodes/A1.b/artifacts","two")
    second.output("y.txt").write_bytes(b"good");r2=second.finish()
    assert r2["outputs"][0]["artifact_file"]!=r["outputs"][0]["artifact_file"]


def test_group_publication_rolls_back_on_failure(tmp_path,monkeypatch):
    monkeypatch.setattr(ab,"REPO_ROOT",tmp_path)
    dest=tmp_path/"output";dest.mkdir()
    (dest/"a.txt").write_bytes(b"old-a");(dest/"b.txt").write_bytes(b"old-b")
    batch=ab.RunBatch.create(tmp_path/"artifacts","one")
    batch.output("a.txt").write_bytes(b"new-a");batch.output("b.txt").write_bytes(b"new-b")
    real=ab.os.replace
    def fail_second(source,target):
        if Path(target)==dest/"b.txt" and "new" in Path(source).parts:
            raise OSError("injected failure")
        return real(source,target)
    monkeypatch.setattr(ab.os,"replace",fail_second)
    with pytest.raises(OSError):batch.finish(publish_to=dest)
    assert (dest/"a.txt").read_bytes()==b"old-a" and (dest/"b.txt").read_bytes()==b"old-b"
    assert not (batch.directory/"run.json").exists()


def test_concurrent_batches_serialize_content_finalization(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    monkeypatch.setattr(ab, "REPO_ROOT", tmp_path)
    ready = threading.Barrier(2)
    def run(name):
        batch = ab.RunBatch.create(tmp_path / "nodes" / name / "artifacts", "parallel")
        batch.output(name + ".txt").write_bytes(b"identical concurrent content")
        ready.wait(timeout=10)
        return batch.finish()["outputs"][0]["artifact_file"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        a, b = list(pool.map(run, ("A0.a", "A1.b")))
    assert a == b


def test_batch_reference_cycles_are_reported(tmp_path):
    from artifact_refs import reference_cycles
    a = "nodes/A0.a/artifacts/a"
    b = "nodes/A1.b/artifacts/b"
    for batch, target in ((a, b), (b, a)):
        path = tmp_path / batch / "run.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"inputs":[{"artifact_file":target+"/input/ref.csv"}]}))
    manifest = tmp_path / "nodes/A0.a/output/manifest.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"artifact":a}))
    errors = reference_cycles(tmp_path, [{"path":"nodes/A0.a"}])
    assert len(errors) == 1 and "引用循环" in errors[0]
