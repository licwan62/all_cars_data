"""节点目录位置：所有节点位于仓库 ``nodes/`` 下（2026-10-21 迁移）。

迁移前写入的 manifest.json / run.json / release.json 记录的是旧的仓库相对路径（如
``A0.尺码计算/artifacts/<批次>/...``）。历史记录不回写，读取时用 ``canonical_path`` /
``load_record`` 统一规范为 ``nodes/A0.尺码计算/...``；迁移后新写入的记录本来就是新路径。
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NODES_DIR = "nodes"


def node_dir_name(path: str) -> str:
    """``nodes/D2.链接分析/皮卡`` → ``D2.链接分析/皮卡``：节点在 nodes/ 下的目录名（用于前缀校验与展示）。"""
    prefix = f"{NODES_DIR}/"
    return path[len(prefix):] if path.startswith(prefix) else path


def canonical_path(value: str, root: Path = REPO_ROOT) -> str:
    """把迁移前记录的旧仓库相对路径规范为 ``nodes/...``；其他字符串原样返回。"""
    head = value.split("/", 1)[0]
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
