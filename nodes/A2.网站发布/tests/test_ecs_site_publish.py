from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile

import pytest

from tools import publish_ecs_site, publish_site_copy
from tools.ecs_site_install import MANIFEST, install_release, sha256_file


@pytest.fixture
def deployment(tmp_path):
    source = tmp_path / "public"
    source.mkdir()
    (source / "index.html").write_bytes(b"new site")
    nas = tmp_path / "nas"
    base = tmp_path / "pipeline.yaml"
    base.write_text(json.dumps({
        "paths": {"nas_publish_dir": str(nas)},
        "ecs_publish": {"instance_id": "test-ecs", "region": "test-region", "url": "https://example.com/car/"},
    }), encoding="utf-8")
    config = tmp_path / "pipeline.local.yaml"
    config.write_text("include: pipeline.yaml\n", encoding="utf-8")
    status = tmp_path / "publish.json"
    return source, nas, ["--config", str(config), "--status-file", str(status)], status


def test_nas_publishes_before_ecs_and_retry_uses_nas(deployment, monkeypatch):
    source, nas, args, status = deployment
    calls = []

    def sync(destination, target):
        assert destination == nas
        assert target["instance_id"] == "test-ecs"
        manifest = (nas / publish_ecs_site.NAS_MANIFEST).read_bytes()
        assert json.loads(manifest)["files"] == {"index.html": hashlib.sha256(b"new site").hexdigest()}
        assert (nas / "index.html").read_bytes() == b"new site"
        calls.append(manifest)
        return {"files": 1}

    monkeypatch.setattr(publish_ecs_site, "sync_nas_release", sync)
    assert publish_site_copy.main([*args, "--source", str(source)]) == 0
    assert json.loads(status.read_bytes())["ecs"]["status"] == "published"
    (source / "index.html").write_bytes(b"unpublished change")
    assert publish_site_copy.main([*args, "--ecs-only"]) == 0
    assert calls[0] == calls[1]
    assert json.loads(status.read_bytes())["status"] == "skipped"


def test_ecs_failure_reports_nas_success_and_nas_failure_skips_ecs(deployment, monkeypatch):
    source, nas, args, status = deployment
    calls = []

    def offline(*unused):
        calls.append("ecs")
        raise OSError("ECS unreachable")

    monkeypatch.setattr(publish_ecs_site, "sync_nas_release", offline)
    command = [*args, "--source", str(source), "--best-effort"]
    assert publish_site_copy.main(command) == 1
    record = json.loads(status.read_bytes())
    assert record["status"] == "published"
    assert record["ecs"]["status"] == "failed"
    assert (nas / "index.html").read_bytes() == b"new site"
    (source / "index.html").unlink()
    assert publish_site_copy.main(command) == 0
    record = json.loads(status.read_bytes())
    assert record["status"] == "failed"
    assert record["ecs"]["status"] == "skipped"
    assert calls == ["ecs"]


def test_bundle_checks_nas_bytes_and_excludes_unowned_files(deployment, tmp_path):
    source, nas, _, _ = deployment
    publish_site_copy.publish_owned(source, nas)
    (nas / "other.html").write_bytes(b"other publisher")
    raw = (nas / publish_ecs_site.NAS_MANIFEST).read_bytes()
    release = json.loads(raw)
    archive = tmp_path / "site.zip"
    publish_ecs_site.make_bundle(nas, archive, raw, release)
    with ZipFile(archive) as bundle:
        assert set(bundle.namelist()) == {MANIFEST, "car/index.html"}
        assert bundle.read(MANIFEST) == raw

    (nas / "index.html").write_bytes(b"out-of-band change")
    with pytest.raises(ValueError, match="NAS file SHA-256"):
        publish_ecs_site.make_bundle(nas, tmp_path / "bad.zip", raw, release)
    assert publish_site_copy.publish_owned(source, nas, verify_existing=True)["copied"] == 1


@pytest.mark.skipif(os.name == "nt", reason="ECS activation uses Linux directory symlink replacement")
def test_ecs_activates_only_a_complete_verified_release(tmp_path):
    releases = tmp_path / "releases"
    releases.mkdir()
    live = tmp_path / "car"
    def bundle(name: str, day: int, payload: bytes, expected: bytes) -> Path:
        archive = tmp_path / (name + ".zip")
        manifest = {
            "publisher": publish_site_copy.PUBLISHER,
            "published_at": f"2026-11-{day:02}T00:00:00+08:00",
            "files": {"index.html": hashlib.sha256(expected).hexdigest()},
        }
        with ZipFile(archive, "w") as output:
            output.writestr(MANIFEST, json.dumps(manifest))
            output.writestr("car/index.html", payload)
        return archive

    first = bundle("first", 9, b"first", b"first")
    assert install_release(first, sha256_file(first), live, releases)["action"] == "installed"
    first_site = live.resolve()
    bad = bundle("bad", 10, b"corrupt", b"second")
    with pytest.raises(ValueError, match="ECS file does not match"):
        install_release(bad, sha256_file(bad), live, releases)
    assert live.resolve() == first_site

    second = bundle("second", 10, b"second", b"second")
    assert install_release(second, sha256_file(second), live, releases)["action"] == "installed"
    assert (live / "index.html").read_bytes() == b"second"
    assert (first_site / "index.html").read_bytes() == b"first"
    assert install_release(second, sha256_file(second), live, releases)["action"] == "unchanged"
    with pytest.raises(ValueError, match="newer NAS release"):
        install_release(first, sha256_file(first), live, releases)
