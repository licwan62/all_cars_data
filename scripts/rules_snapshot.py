"""节点 data/ 规则快照：发布时写入 manifest 的 ``rules``，追踪时与当前 data/ 比对。

按目录约定，``data/`` 只放本节点人工维护的规则、配置、映射和参考资料，因此整个目录都是规则输入；
不在 pipeline.json 逐个登记文件，避免登记清单与实际使用的规则版本脱节。

sha256 按 CRLF→LF 归一后的内容计算：仓库 ``core.autocrlf=true``，检出会改写换行，
只改换行不应让节点被判为规则已变化。
"""

from __future__ import annotations

import hashlib
from pathlib import Path

IGNORED_DIRS = {"__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".tmp"}


def _ignored(relative: Path) -> bool:
    if any(part in IGNORED_DIRS or part.startswith(".") for part in relative.parts):
        return True
    return relative.name.startswith("~$") or relative.suffix.lower() in IGNORED_SUFFIXES


def content_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def rules_snapshot(project: Path) -> list[dict]:
    """返回 ``[{"file": "data/...", "sha256": ...}]``，按路径排序；没有 data/ 时为空。"""
    data_dir = project / "data"
    if not data_dir.is_dir():
        return []
    records = []
    for path in sorted(data_dir.rglob("*")):
        relative = path.relative_to(project)
        if path.is_file() and not _ignored(relative.relative_to("data")):
            records.append({"file": relative.as_posix(), "sha256": content_sha256(path)})
    return records


def rules_changes(recorded: list[dict], current: list[dict]) -> dict[str, list[str]]:
    """比较两次快照，返回 修改/新增/删除 的文件清单（均已排序）。"""
    before = {item["file"]: item["sha256"] for item in recorded}
    after = {item["file"]: item["sha256"] for item in current}
    return {
        "修改": sorted(name for name in before.keys() & after.keys() if before[name] != after[name]),
        "新增": sorted(after.keys() - before.keys()),
        "删除": sorted(before.keys() - after.keys()),
    }


def describe_changes(changes: dict[str, list[str]]) -> str:
    return "；".join(f"{kind} {', '.join(files)}" for kind, files in changes.items() if files)
