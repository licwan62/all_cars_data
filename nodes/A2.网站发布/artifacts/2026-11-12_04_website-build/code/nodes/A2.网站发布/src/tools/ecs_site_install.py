"""Install a NAS site bundle on the ECS host; invoked through Workbench."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


PUBLISHER = "pipeline_carstable_to_webapp"
MANIFEST = "release-manifest.json"
REMOTE_BUNDLE = re.compile(r"codex-car-publish-[0-9a-f]{32}\.zip")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_release(raw: bytes) -> dict:
    release = json.loads(raw)
    if release.get("publisher") != PUBLISHER:
        raise ValueError("Unexpected site publisher")
    files = release.get("files")
    if not isinstance(files, dict) or "index.html" not in files:
        raise ValueError("NAS release has no site entry point")
    if datetime.fromisoformat(release["published_at"]).utcoffset() is None:
        raise ValueError("NAS release timestamp needs a time zone")
    for name, digest in files.items():
        path = PurePosixPath(name)
        if (not path.parts or path.is_absolute() or ".." in path.parts
                or "\\" in name or ":" in name or str(path) != name or path.parts[0] == "_publishers"
                or not isinstance(digest, str) or re.fullmatch(r"[a-f0-9]{64}", digest) is None):
            raise ValueError(f"Invalid NAS release entry: {name!r}")
    return release


def same_files(site: Path, files: dict[str, str]) -> bool:
    observed = set()
    for path in site.rglob("*"):
        if path.is_symlink():
            return False
        if path.is_file():
            relative = path.relative_to(site).as_posix()
            if relative not in files or sha256_file(path) != files[relative]:
                return False
            observed.add(relative)
    return observed == set(files)


def atomic_manifest(path: Path, raw: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(raw)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def install_release(archive: Path, archive_sha: str, live: Path, releases: Path) -> dict:
    if sha256_file(archive) != archive_sha:
        raise ValueError("ECS bundle SHA-256 does not match")
    with ZipFile(archive) as bundle:
        raw = bundle.read(MANIFEST)
        release = read_release(raw)
        files = release["files"]
        members = bundle.namelist()
        if len(members) != len(files) + 1 or set(members) != {MANIFEST, *("car/" + name for name in files)}:
            raise ValueError("ECS bundle does not match its NAS release manifest")

        manifest_sha = hashlib.sha256(raw).hexdigest()
        result = {"files": len(files), "manifest_sha256": manifest_sha, "published_at": release["published_at"]}
        if live.is_symlink():
            current = live.resolve(strict=True)
            if current.parent.parent != releases.resolve() or current.name != "car":
                raise ValueError("ECS site link points outside managed releases")
            current_manifest = current.parent / MANIFEST
            old_raw = current_manifest.read_bytes()
            old = read_release(old_raw)
            if datetime.fromisoformat(old["published_at"]) > datetime.fromisoformat(release["published_at"]):
                raise ValueError("ECS is already serving a newer NAS release")
            if old["files"] == files and same_files(current, files):
                if old_raw != raw:
                    atomic_manifest(current_manifest, raw)
                return dict(result, action="unchanged" if old_raw == raw else "reused", release=current.parent.name)
        elif live.exists():
            raise ValueError("ECS site path exists and is not a managed link")

        name = f"{manifest_sha[:16]}-{uuid.uuid4().hex[:12]}"
        ready = releases / name
        with tempfile.TemporaryDirectory(prefix=".car-stage-", dir=releases) as directory:
            stage = Path(directory) / "release"
            for relative, expected in files.items():
                payload = bundle.read("car/" + relative)
                if hashlib.sha256(payload).hexdigest() != expected:
                    raise ValueError(f"ECS file does not match the NAS release: {relative}")
                path = stage / "car" / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            (stage / MANIFEST).write_bytes(raw)
            stage.rename(ready)

        temporary = live.with_name(f".{live.name}-{uuid.uuid4().hex}")
        try:
            temporary.symlink_to(ready / "car", target_is_directory=True)
            os.replace(temporary, live)
        finally:
            temporary.unlink(missing_ok=True)
        return dict(result, action="installed", release=name)


def main() -> None:
    import fcntl

    archive, archive_sha = Path(sys.argv[1]), sys.argv[2]
    if archive.parent != Path("/tmp") or not REMOTE_BUNDLE.fullmatch(archive.name) or archive.is_symlink():
        raise ValueError("Unexpected ECS upload path")
    os.umask(0o022)
    releases = Path("/srv/car-publish/releases")
    live = Path("/srv/www/car")
    try:
        with (releases.parent / ".publish.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            print(json.dumps(install_release(archive, archive_sha, live, releases)))
    finally:
        archive.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
