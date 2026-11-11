"""Mirror one verified NAS site release to ECS through Workbench."""
from __future__ import annotations

import base64
import hashlib
import json
import shlex
import subprocess
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import ProxyHandler, Request, build_opener
from zipfile import ZIP_DEFLATED, ZipFile

from tools.ecs_site_install import MANIFEST, PUBLISHER, read_release, sha256_file


NAS_MANIFEST = Path("_publishers") / f"{PUBLISHER}.json"


def make_bundle(nas: Path, archive: Path, raw: bytes, release: dict) -> None:
    """Use only this publisher's files, checking the actual NAS bytes as they are read."""
    def checked_file(entry: tuple[str, str]) -> tuple[str, bytes]:
        relative, expected = entry
        payload = (nas / relative).read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError(f"NAS file SHA-256 does not match its release: {relative}")
        return relative, payload

    files = sorted(release["files"].items())
    with ZipFile(archive, "x", compression=ZIP_DEFLATED, compresslevel=3) as bundle:
        bundle.writestr(MANIFEST, raw)
        with ThreadPoolExecutor(max_workers=16) as workers:
            for offset in range(0, len(files), 64):
                for relative, payload in workers.map(checked_file, files[offset:offset + 64]):
                    bundle.writestr("car/" + relative, payload)
    if archive.stat().st_size > 1_000_000_000:
        raise ValueError("The NAS bundle exceeds the Workbench upload limit (1 GB)")


def workbench(action: list[str], target: dict, *, timeout: int) -> str:
    command = ["workbench", *action, "--instance-id", target["instance_id"], "--region", target["region"]]
    if target.get("profile"):
        command += ["--profile", target["profile"]]
    process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if process.returncode:
        try:
            record = json.loads(process.stdout)
            detail = record.get("stderr") or record.get("message") or record.get("stdout") or ""
        except (ValueError, AttributeError):
            detail = process.stderr or process.stdout
        raise RuntimeError(f"Workbench {action[0]} failed ({process.returncode}): {detail.strip()[-1200:]}")
    return process.stdout


def remote_exec(command: str, target: dict, *, timeout: int = 20) -> str:
    output = workbench(["exec", "--timeout", str(timeout), "--output", "json", "--command", command],
                       target, timeout=timeout + 20)
    result = json.loads(output)
    if result.get("exit_code", 0):
        raise RuntimeError(f"ECS command failed: {result.get('stderr', '').strip()}")
    return result.get("stdout") or result.get("output") or ""


def check_public(url: str, files: dict[str, str]) -> int:
    opener = build_opener(ProxyHandler({}))
    candidates = ("index.html", "size-match.html", "size-ref.html", "model-dashboard.html",
                  "assets/app/viewer.css", "data/generated/size-match.json", "data/generated/size-ref.json")
    verified = 0
    for relative in candidates:
        if relative not in files:
            continue
        endpoint = url if relative == "index.html" else urljoin(url, quote(relative))
        request = Request(endpoint, headers={"Cache-Control": "no-cache", "User-Agent": "car-site-publisher"})
        for delay in (1, 2, None):
            try:
                with opener.open(request, timeout=12) as response:
                    if response.status != 200 or response.geturl() != endpoint:
                        raise ValueError(f"Unexpected HTTPS response for {endpoint}")
                    if hashlib.sha256(response.read()).hexdigest() != files[relative]:
                        raise ValueError(f"Public ECS response differs from the NAS release: {relative}")
                break
            except (OSError, ValueError):
                if delay is None:
                    raise
                time.sleep(delay)
        verified += 1
    return verified


def sync_nas_release(nas: Path, target: dict) -> dict:
    url = target["url"]
    parsed_url = urlsplit(url)
    if parsed_url.scheme != "https" or not parsed_url.hostname or parsed_url.path != "/car/" or parsed_url.query or parsed_url.fragment:
        raise ValueError("ECS publishing URL must be an HTTPS /car/ endpoint")
    manifest = nas / NAS_MANIFEST
    raw = manifest.read_bytes()
    release = read_release(raw)
    registry = json.loads((manifest.parent / "registry.json").read_bytes())
    if registry.get("publishers", {}).get(PUBLISHER, {}).get("published_at") != release["published_at"]:
        raise ValueError("NAS manifest and registry disagree; finish NAS publication before syncing ECS")

    with tempfile.TemporaryDirectory(prefix="car-ecs-publish-") as directory:
        filename = f"codex-car-publish-{uuid.uuid4().hex}.zip"
        archive = Path(directory) / filename
        remote = f"/tmp/{filename}"
        make_bundle(nas, archive, raw, release)
        remote_exec(f"test ! -e {remote} && test ! -L {remote}", target)
        workbench(["upload", str(archive), remote], target, timeout=300)
        if manifest.read_bytes() != raw:
            remote_exec(f"unlink {remote}", target)
            raise RuntimeError("NAS release changed while ECS was uploading; rerun the mirror")
        installer = base64.b64encode(Path(__file__).with_name("ecs_site_install.py").read_bytes()).decode("ascii")
        command = f"printf %s {shlex.quote(installer)} | base64 -d | /usr/bin/python3.11 - {remote} {sha256_file(archive)}"
        result = json.loads(remote_exec(command, target, timeout=120))
    if result.get("manifest_sha256") != hashlib.sha256(raw).hexdigest() or result.get("files") != len(release["files"]):
        raise ValueError("ECS did not report the expected NAS release")
    result["https_checks"] = check_public(url, release["files"])
    if manifest.read_bytes() != raw:
        raise RuntimeError("NAS release changed during ECS verification; rerun the mirror")
    return result
