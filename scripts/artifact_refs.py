"""artifact 引用：交付物字节只存一次，其他地方按 (节点, 版本, 文件, sha256) 引用。

- 发布时内容未变的交付物不再复制，``artifact_file`` 指向最早保存这份字节的批次文件
  （发布批次 ``output/名称-<版本>.ext``，或节点运行批次 ``run.json`` 登记的 ``output/名称-<版本>.ext``）；
  因此 ``versioned_file`` 的版本后缀可以早于 manifest 的 ``version``。
- ``check_deliverable_source`` 供追踪与结构校验共用；``referenced_batches`` 供归档按引用计数保护批次。
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

VERSION = re.compile(r"^\d{8}_\d{2}$")
RUN_RECORD = "run.json"
MANIFEST = "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def versioned_name(file_name: str, version: str) -> str:
    path = Path(file_name)
    return path.with_name(f"{path.stem}-{version}{path.suffix}").as_posix()


def version_of(file_name: str, versioned_file: str) -> str | None:
    """``versioned_file`` 是 ``file_name`` 加 ``-YYYYMMDD_NN`` 后缀时返回该版本，否则 None。"""
    path = Path(file_name)
    prefix = path.with_name(f"{path.stem}-").as_posix()
    if not (versioned_file.startswith(prefix) and versioned_file.endswith(path.suffix)):
        return None
    version = versioned_file[len(prefix): len(versioned_file) - len(path.suffix) if path.suffix else None]
    return version if VERSION.match(version) else None


def check_deliverable_source(root: Path, manifest: dict, item: dict) -> str | None:
    """校验交付物来源记录，返回错误说明；只检查命名与存在性，内容一致性由调用方按需比对。"""
    name = item["file"]
    versioned = item.get("versioned_file") or ""
    source = item.get("artifact_file") or ""
    stored = version_of(name, versioned)
    if stored is None:
        return f"{name} 的 versioned_file {versioned!r} 不是 {versioned_name(name, '<YYYYMMDD_NN>')}"
    if stored > manifest.get("version", ""):
        return f"{name} 的存储版本 {stored} 晚于 manifest 版本 {manifest.get('version')}"
    if not source.endswith(f"/output/{versioned}"):
        return f"{name} 的 artifact_file {source!r} 应以 /output/{versioned} 结尾"
    if not (root / source).is_file():
        return f"来源 {source} 不存在"
    return None


def batch_of(artifact_file: str) -> str | None:
    """``<节点>/artifacts/<批次>/...`` → ``<节点>/artifacts/<批次>``。"""
    parts = artifact_file.split("/")
    return "/".join(parts[:3]) if len(parts) >= 3 and parts[1] == "artifacts" else None


def record_references(record: dict) -> set[str]:
    """manifest.json / run.json 引用到的批次（含自身所在批次）。"""
    refs: set[str] = set()
    if record.get("artifact"):
        refs.add(record["artifact"])
    for item in record.get("deliverables", []) + record.get("outputs", []):
        refs.add(batch_of(item.get("artifact_file") or ""))
    for upstream in record.get("upstream", []) + record.get("inputs", []):
        if upstream.get("artifact"):
            refs.add(upstream["artifact"])
        for item in upstream.get("files", [upstream]):
            refs.add(batch_of(item.get("artifact_file") or ""))
    refs.discard(None)
    return refs


def _load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def referenced_batches(root: Path, nodes: list[dict], keep_batches: set[str] = frozenset()) -> set[str]:
    """当前各节点 output/manifest.json 与 keep_batches 直接或间接引用的全部批次（相对仓库的 posix 路径）。"""
    pending: list[str] = list(keep_batches)
    for node in nodes:
        manifest = _load(root / node["path"] / "output" / MANIFEST)
        if manifest:
            pending.extend(record_references(manifest))
    seen: set[str] = set()
    while pending:
        batch = pending.pop()
        if batch in seen:
            continue
        seen.add(batch)
        for name in (MANIFEST, RUN_RECORD):
            record = _load(root / batch / name)
            if record:
                pending.extend(record_references(record) - seen)
    return seen
