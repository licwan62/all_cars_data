"""Rebuildable content index; immutable records remain authoritative.

No hard links: published outputs and editable rules are independent working copies.
Only successful, readable historical content is eligible for reuse.
"""
from __future__ import annotations
import hashlib
import json
import sqlite3
from pathlib import Path
from node_paths import canonical_path, load_record


def raw_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def resolve_source(root, reference):
    root = Path(root).resolve()
    ref = canonical_path(str(reference), root)
    p = Path(ref)
    candidate = p if p.is_absolute() else root / p
    try:
        candidate.resolve().relative_to(root)
    except ValueError:
        raise ValueError("历史内容引用超出仓库")
    if candidate.is_file():
        return candidate
    index = root / "artifacts_archive.json"
    if index.is_file():
        for group in load_record(index, root).get("archives", []):
            for batch in group.get("batches", []):
                prefix = canonical_path(batch.get("batch", ""), root).rstrip("/")
                if prefix and ref.startswith(prefix + "/") and batch.get("archive_path"):
                    base = Path(batch["archive_path"]).resolve()
                    target = (base / ref[len(prefix) + 1:]).resolve()
                    target.relative_to(base)
                    if target.is_file():
                        return target
    return candidate


class ContentIndex:
    def __init__(self, root, persistent=False):
        self.root = Path(root).resolve()
        db = ":memory:"
        if persistent:
            folder = self.root / "cache"
            folder.mkdir(exist_ok=True)
            db = str(folder / "content_index.sqlite3")
        self.db = sqlite3.connect(db)
        self.db.execute("CREATE TABLE IF NOT EXISTS content(sha TEXT, bytes INTEGER, ref TEXT, record TEXT, PRIMARY KEY(sha, ref))")

    def close(self):
        self.db.close()

    def rebuild(self):
        self.db.execute("DELETE FROM content")
        base = self.root / "nodes" if (self.root / "nodes").is_dir() else self.root
        for path in sorted(base.rglob("*.json")):
            if path.name not in {"run.json", "manifest.json"} or "artifacts" not in path.parts:
                continue
            try:
                record = load_record(path, self.root)
                if path.name == "run.json" and record.get("status", {}).get("status") != "passed":
                    continue
                items = record.get("outputs", []) + record.get("deliverables", []) + record.get("inputs", []) + record.get("rules", {}).get("files", []) if isinstance(record.get("rules", {}), dict) else record.get("deliverables", [])
                items += record.get("code", {}).get("files", []) + record.get("extra_records", [])
                for item in items:
                    ref = item.get("artifact_file")
                    if not ref:
                        continue
                    source = self.root / canonical_path(ref, self.root)
                    if not source.is_file():
                        continue
                    digest = item.get("raw_sha256") or item.get("sha256")
                    # Legacy rules use a normalized digest, never treat it as byte identity.
                    if item.get("file", "").startswith("data/") and not item.get("raw_sha256"):
                        digest = raw_sha256(source)
                    if digest:
                        self.add(digest, source.stat().st_size, ref, path.relative_to(self.root).as_posix())
            except (OSError, ValueError, TypeError):
                continue
        self.db.commit()

    def add(self, sha, size, ref, record=""):
        self.db.execute("INSERT OR IGNORE INTO content VALUES(?,?,?,?)", (sha, size, ref, record))

    def find(self, digest, size):
        for (ref,) in self.db.execute("SELECT ref FROM content WHERE sha=? AND bytes=? ORDER BY ref", (digest, size)):
            source = resolve_source(self.root, ref)
            if source.is_file() and source.stat().st_size == size and raw_sha256(source) == digest:
                return ref
        return None

    def entries(self, digest):
        return [dict(zip(("sha256", "bytes", "artifact_file", "record"), row)) for row in self.db.execute("SELECT * FROM content WHERE sha=?", (digest,))]
