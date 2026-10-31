"""节点目录位置：所有节点位于仓库 ``nodes/`` 下（2026-10-21 迁移）。

迁移前写入的 manifest.json / run.json / release.json 记录的是旧的仓库相对路径（如
``A0.尺码计算/artifacts/<批次>/...``）。历史记录不回写，读取时用 ``canonical_path`` /
``load_record`` 统一规范为 ``nodes/A0.尺码计算/...``；迁移后新写入的记录本来就是新路径。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NODES_DIR = "nodes"
NODE_PATH_ALIASES = {
    "D1.聚类SKU": "D1.发货评估",
    "D2.链接分析/皮卡": "D2.链接分析/nodes/皮卡",
    "D2.链接分析/普通": "D2.链接分析/nodes/普通",
    "D2.链接分析/W型车": "D2.链接分析/nodes/W型车",
}


def node_dir_name(path: str) -> str:
    """``nodes/D2.链接分析/皮卡`` → ``D2.链接分析/皮卡``：节点在 nodes/ 下的目录名（用于前缀校验与展示）。"""
    prefix = f"{NODES_DIR}/"
    return path[len(prefix):] if path.startswith(prefix) else path


def canonical_path(value: str, root: Path = REPO_ROOT) -> str:
    """把迁移前记录的旧仓库相对路径规范为 ``nodes/...``；其他字符串原样返回。"""
    for old, new in NODE_PATH_ALIASES.items():
        for prefix in (old, f"{NODES_DIR}/{old}"):
            if value == prefix or value.startswith(prefix + "/"):
                suffix = value[len(prefix):]
                return f"{NODES_DIR}/{new}{suffix}"
    # Only node-relative POSIX paths are candidates. Never stat arbitrary text,
    # drive paths or UNC archive locations while recursively reading records.
    if "\\" in value or value.startswith("/") or ":" in value:
        return value
    head = value.split("/", 1)[0]
    if not re.match(r"^(?:[0-9]{2}|[A-Z][0-9]+)\.", head):
        return value
    if head and head != NODES_DIR and (root / NODES_DIR / head).is_dir() and not (root / head).exists():
        return f"{NODES_DIR}/{value}"
    return value


def canonical_record(record, root: Path = REPO_ROOT):
    """递归规范 manifest / run.json 中的路径字符串（节点内相对路径如 ``US/全量表.csv``、``data/...`` 不受影响）。"""
    if isinstance(record, dict):
        return {key: canonical_record(value, root) for key, value in record.items()}
    if isinstance(record, list):
        return [canonical_record(value, root) for value in record]
    if isinstance(record, str):
        return canonical_path(record, root)
    return record


def load_record(path: Path, root: Path = REPO_ROOT) -> dict:
    """读取 manifest.json / run.json / release.json，并把旧路径规范为 nodes/ 下的路径。"""
    return canonical_record(json.loads(path.read_text(encoding="utf-8-sig")), root)
