#!/usr/bin/env python3
"""通过 SSH 发布 A2/output/US 到远端 size_compressed。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_DIR / "data" / "ssh发布.yaml"


class PublishError(ValueError):
    pass


@dataclass(frozen=True)
class PublishPlan:
    host: str
    destination: PurePosixPath
    version: str
    files: tuple[tuple[Path, str, str], ...]  # local path, remote name, sha256


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_plan(config_path: Path = DEFAULT_CONFIG) -> PublishPlan:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    host = str(config.get("host", "")).strip()
    destination = str(config.get("destination", "")).strip()
    source = PROJECT_DIR / str(config.get("source", ""))
    names = tuple(str(name) for name in config.get("files", []))
    if not host or not destination or not names:
        raise PublishError(f"SSH 发布配置不完整：{config_path}")
    destination_path = PurePosixPath(destination)
    if ".." in destination_path.parts:
        raise PublishError("destination 不得包含上级目录")
    allowed_destination = PurePosixPath("/share/Public/PQData/pub_all_cars_data/size_compressed")
    if destination_path.is_absolute() and destination_path != allowed_destination:
        raise PublishError(f"绝对发布路径仅允许 {allowed_destination}")

    manifest_path = PROJECT_DIR / "output" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    deliverables = {item["file"]: item for item in manifest.get("deliverables", [])}
    files = []
    for name in names:
        local = source / name
        manifest_name = f"US/{name}"
        item = deliverables.get(manifest_name)
        if not local.is_file() or item is None:
            raise PublishError(f"缺少已发布交付物：{manifest_name}")
        digest = sha256(local)
        if digest != item.get("sha256"):
            raise PublishError(f"{manifest_name} 与 output/manifest.json 的 SHA-256 不一致")
        files.append((local, name, digest))
    return PublishPlan(host, destination_path, str(manifest["version"]), tuple(files))


def run_command(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, encoding="utf-8", capture_output=True)
    return completed.stdout


def publish(plan: PublishPlan) -> None:
    destination = plan.destination.as_posix()
    run_command(["ssh", "-o", "BatchMode=yes", plan.host, f"mkdir -p -- {shlex.quote(destination)}"])

    temporary_names: list[tuple[str, str]] = []
    for local, name, _ in plan.files:
        temporary = f".{name}.{plan.version}.tmp"
        remote = f"{plan.host}:{destination}/{temporary}"
        # QNAP 上未启用 SFTP 子系统；-O 强制使用兼容的传统 SCP 协议。
        run_command(["scp", "-O", "-p", "--", str(local), remote])
        temporary_names.append((temporary, name))

    moves = " && ".join(
        f"mv -f -- {shlex.quote(temporary)} {shlex.quote(name)}" for temporary, name in temporary_names
    )
    run_command(["ssh", "-o", "BatchMode=yes", plan.host, f"cd {shlex.quote(destination)} && {moves}"])

    remote_hashes = run_command([
        "ssh", "-o", "BatchMode=yes", plan.host,
        f"cd {shlex.quote(destination)} && sha256sum -- "
        + " ".join(shlex.quote(name) for _, name, _ in plan.files),
    ]).splitlines()
    actual = [line.split(maxsplit=1)[0] for line in remote_hashes if line.strip()]
    expected = [digest for _, _, digest in plan.files]
    if actual != expected:
        raise PublishError(f"远端 SHA-256 校验失败：expected={expected}, actual={actual}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true", help="只校验并打印发布计划")
    args = parser.parse_args(argv)
    try:
        plan = load_plan(args.config.resolve())
        if not args.dry_run:
            publish(plan)
    except (PublishError, OSError, subprocess.CalledProcessError) as error:
        print(f"SSH 发布失败：{error}")
        return 2
    action = "将发布" if args.dry_run else "已发布"
    print(f"{action} {len(plan.files)} 个文件到 {plan.host}:{plan.destination.as_posix()}（A2 {plan.version}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
