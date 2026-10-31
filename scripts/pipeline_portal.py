#!/usr/bin/env python3
"""Local, read-only pipeline browser with a separate journal for human notes.

Run from any directory: ``python scripts/pipeline_portal.py``. The HTTP server
always binds to loopback; no pipeline run or publish endpoint is exposed.
"""

from __future__ import annotations

import argparse
import secrets
import hashlib
import tempfile
import json
import os
import sqlite3
import sys
import threading
import time
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from materials import Materials, Conflict, UPLOAD_LIMIT, ClosingConnection
from pipeline_contract import lifecycle_state
from content_store import ContentIndex, raw_sha256
from node_paths import canonical_path, load_record  # noqa: E402
from pipeline_status import is_on_demand  # noqa: E402
from trace_pipeline import trace_node  # noqa: E402

SITE_ID = "website"
TEXT_SUFFIXES = {".txt", ".md", ".json", ".jsonl", ".csv", ".tsv", ".yaml", ".yml", ".py", ".ps1", ".html", ".css", ".js"}
MAX_PREVIEW = 200_000
CHINA_TZ = timezone(timedelta(hours=8))


def read_json(path: Path, root: Path | None = None) -> dict:
    if not path.is_file():
        return {}
    try:
        return load_record(path, root) if root else json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def archive_batches(root: Path, site: bool) -> dict[str, Path]:
    name = "artifact_archive.json" if site else "artifacts_archive.json"
    result = {}
    for group in read_json(root / name).get("archives", []):
        for batch in group.get("batches", []):
            key = batch.get("batch", "")
            if site:
                key = f"artifact/{key}"
            else:
                key = canonical_path(key, root)
            if key and batch.get("archive_path"):
                result[key.replace("\\", "/")] = Path(batch["archive_path"])
    return result


class Portal:
    def __init__(self, data_root: Path = ROOT, web_root: Path | None = None, db_path: Path | None = None, upload_limit: int = UPLOAD_LIMIT):
        self.data_root = data_root.resolve()
        self.web_root = (web_root or data_root.parent / "pipeline_carstable_to_webapp").resolve()
        self.db_path = db_path or self.data_root / "portal" / "data" / "journal.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self._snapshot: tuple[float, dict] | None = None
        self._init_db()
        self.token = secrets.token_urlsafe(32)
        self.materials = Materials(self.data_root, self.db_path, self.lock, upload_limit)

    def _connect(self):
        db = sqlite3.connect(self.db_path, timeout=20, factory=ClosingConnection)
        db.row_factory = sqlite3.Row
        return db

    def _init_db(self):
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS auto_events (
                    event_key TEXT PRIMARY KEY, node_id TEXT NOT NULL, kind TEXT NOT NULL,
                    occurred_at TEXT NOT NULL, status TEXT NOT NULL, title TEXT NOT NULL,
                    file_ref TEXT, detail TEXT NOT NULL, fingerprint TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS auto_node_time ON auto_events(node_id, occurred_at DESC);
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY, node_id TEXT NOT NULL, event_key TEXT,
                    summary TEXT NOT NULL, detail TEXT NOT NULL, file_ref TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS notes_node_time ON notes(node_id, created_at DESC);
            """)

    def _backup_before_write(self):
        stamp = datetime.now(CHINA_TZ).strftime("%Y-%m-%d")
        dest = self.db_path.parent / "backups" / f"journal-{stamp}.sqlite3"
        if dest.exists():
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as source, sqlite3.connect(dest, factory=ClosingConnection) as backup:
            source.backup(backup)

    def _pipeline(self) -> dict:
        payload = read_json(self.data_root / "pipeline.json")
        if not isinstance(payload.get("nodes"), list):
            raise RuntimeError("找不到有效的 pipeline.json")
        return payload

    def _site_batches(self) -> list[tuple[Path, dict]]:
        directory = self.web_root / "artifact"
        if not directory.is_dir():
            return []
        return [(p, read_json(p / "artifact.json")) for p in sorted(directory.iterdir()) if p.is_dir() and (p / "artifact.json").is_file()]

    def _latest_site(self) -> dict:
        batches = self._site_batches()
        if not batches:
            return {"status": "未运行", "public": "未发布", "nas": "未发布", "upstream": [], "steps": []}
        folder, record = batches[-1]
        current_public = next((p.name for p, item in reversed(batches)
                               if ((item.get("publish") or {}).get("public") or {}).get("status") == "promoted"), None)
        current_nas = next((p.name for p, item in reversed(batches)
                            if ((item.get("publish") or {}).get("nas") or {}).get("status") == "published"), None)
        publish = record.get("publish") or {}
        steps = record.get("steps") or {}
        if not isinstance(steps, dict):
            steps = {}
        sources = (record.get("upstream") or {}).get("sources") or {}
        upstream = [{"key": key, "node": source.get("node"), "version": source.get("version"),
                     "artifact": source.get("artifact"), "pinned_at": (record.get("upstream") or {}).get("pinned_at")}
                    for key, source in sources.items()]
        return {"batch": folder.name, "status": record.get("status", "未知"),
                "created_at": record.get("created_at"), "updated_at": record.get("updated_at"),
                "build": (steps.get("build_public_site") or {}).get("status", "未执行"),
                "public": (publish.get("public") or {}).get("status", "未发布"),
                "nas": (publish.get("nas") or {}).get("status", "未发布"),
                "current_public_batch": current_public, "last_nas_published_batch": current_nas,
                "nas_error": (publish.get("nas") or {}).get("error", ""),
                "steps": [{"name": name, **value} for name, value in steps.items() if isinstance(value, dict)],
                "upstream": upstream, "ref": f"web:artifact/{folder.name}/artifact.json"}

    def overview(self) -> dict:
        with self.lock:
            if self._snapshot and time.monotonic() - self._snapshot[0] < 12:
                return self._snapshot[1]
            payload = self._pipeline()
            by_id = {node["id"]: node for node in payload["nodes"]}
            nodes = []
            for node in payload["nodes"]:
                manifest = read_json(self.data_root / node["path"] / "output" / "manifest.json", self.data_root)
                if lifecycle_state(node):
                    state, issues = lifecycle_state(node), node.get("blockers", [])
                elif not manifest:
                    state, issues = "未发布", ["缺少 output/manifest.json"]
                else:
                    errors, stale, deferred = trace_node(node, by_id, is_on_demand(payload, node), self.data_root)
                    if errors:
                        state, issues = "错误", errors
                    elif stale:
                        state, issues = "过期", stale
                    elif deferred:
                        state, issues = "按需待刷新", deferred
                    elif not manifest.get("deliverables") and node.get("pending"):
                        state, issues = "待产出", []
                    else:
                        state, issues = "最新", []
                display_name = (node["path"].split("/")[-1] if node.get("parent") else node["path"].removeprefix("nodes/"))
                display_layer = max(0, min((child.get("layer", 1) for child in payload["nodes"] if child.get("parent") == node["id"]), default=1) - 1) if node.get("kind") == "container" else node.get("layer", 0)
                nodes.append({"id": node["id"], "name": display_name,
                              "kind": node.get("kind", "node"), "parent": node.get("parent"), "lifecycle": node.get("lifecycle", "active"),
                              "naming_basis": node.get("naming_basis", ""),
                              "line": node.get("line", "U"), "layer": display_layer,
                              "trigger": "按需" if is_on_demand(payload, node) else "自动",
                              "upstream": node.get("upstream", []), "state": state, "issues": issues[:5],
                              "version": manifest.get("version"), "deliverables": len(manifest.get("deliverables", [])),
                              "pending": node.get("pending", [])})
            site = self._latest_site()
            edges = [{"from": upstream, "to": node["id"]} for node in payload["nodes"] for upstream in node.get("upstream", [])]
            edges += [{"from": n["parent"], "to": n["id"], "type": "contains"} for n in payload["nodes"] if n.get("parent")]
            edges += [{"from": item["node"], "to": SITE_ID} for item in site["upstream"] if item.get("node") in by_id]
            result = {"nodes": nodes, "edges": edges, "site": site,
                      "files": [self.file_entry("data", name) for name in
                                ("pipeline.json", "release.json", "流水线状态.md", "AGENTS.md", "README.md",
                                 "reports/资料登记草案/资料目录.csv")],
                      "synced_at": datetime.now(CHINA_TZ).isoformat(timespec="seconds")}
            self._snapshot = (time.monotonic(), result)
            return result

    def _archive_path(self, repo: str, relative: str) -> Path | None:
        root = self.data_root if repo == "data" else self.web_root
        batches = archive_batches(root, repo == "web")
        relative = canonical_path(relative, root) if repo == "data" else relative
        for batch in sorted(batches, key=len, reverse=True):
            prefix = batch + "/"
            if relative == batch or relative.startswith(prefix):
                suffix = relative[len(batch):].lstrip("/")
                candidate = batches[batch] / Path(suffix)
                if inside(candidate, batches[batch]):
                    return candidate
        return None

    def resolve_ref(self, ref: str) -> tuple[Path, str]:
        repo, separator, relative = ref.partition(":")
        if not separator or repo not in {"data", "web"} or not relative or "\\" in relative:
            raise ValueError("无效文件引用")
        root = self.data_root if repo == "data" else self.web_root
        candidate = root / relative
        if not inside(candidate, root):
            raise ValueError("文件路径超出仓库")
        if candidate.exists():
            return candidate, "本地"
        archived = self._archive_path(repo, relative)
        if archived is not None:
            return archived, "归档" if archived.exists() else "归档不可用"
        return candidate, "缺失"

    def file_entry(self, repo: str, relative: str, *, sha256: str | None = None, rows=None) -> dict:
        ref = f"{repo}:{relative.replace(chr(92), '/')}"
        path, location = self.resolve_ref(ref)
        return {"name": Path(relative).name, "path": relative, "ref": ref,
                "location": location, "exists": path.is_file() or path.is_dir(),
                "previewable": path.is_file() and path.suffix.lower() in TEXT_SUFFIXES,
                "sha256": sha256, "rows": rows}

    def node(self, node_id: str) -> dict:
        payload = self._pipeline()
        by_id = {node["id"]: node for node in payload["nodes"]}
        if node_id == SITE_ID:
            site = self._latest_site()
            files = [self.file_entry("web", name) for name in
                     ("configs/pipeline.yaml", "docs/pipeline.md", "README.md", "public/index.html")]
            if site.get("batch"):
                files.append(self.file_entry("web", f"artifact/{site['batch']}/artifact.json"))
            return {"id": SITE_ID, "name": "网站构建与发布", "site": site, "files": files,
                    "upstream": site["upstream"], "downstream": [], "history": self._site_history()}
        if node_id not in by_id:
            raise KeyError(node_id)
        node = by_id[node_id]
        base = self.data_root / node["path"]
        manifest = read_json(base / "output" / "manifest.json", self.data_root)
        docs = []
        for folder in ("data", "research_queue", "docs", "plans"):
            source_dir = base / folder
            if source_dir.is_dir():
                docs += [self.file_entry("data", p.relative_to(self.data_root).as_posix())
                         for p in sorted(source_dir.rglob("*")) if p.is_file() and "__pycache__" not in p.parts]
        docs += [self.file_entry("data", p.relative_to(self.data_root).as_posix())
                 for p in sorted(base.glob("*.md")) if p.is_file()]
        outputs = []
        for item in manifest.get("deliverables", []):
            current = self.file_entry("data", f"{node['path']}/output/{item['file']}", sha256=item.get("sha256"), rows=item.get("rows"))
            current["source"] = self.file_entry("data", item["artifact_file"], sha256=item.get("sha256")) if item.get("artifact_file") else None
            outputs.append(current)
        upstream = []
        for item in manifest.get("upstream", []):
            upstream.append({"node": item.get("node"), "version": item.get("version"), "basis": item.get("basis", "未记录"),
                             "files": [{"name": f.get("file"), "sha256": f.get("sha256"),
                                        "source": self.file_entry("data", f["artifact_file"], sha256=f.get("sha256")) if f.get("artifact_file") else None}
                                       for f in item.get("files", [])]})
        rules = [{"file": self.file_entry("data", f"{node['path']}/{item['file']}", sha256=item.get("sha256")), "sha256": item.get("sha256")}
                 for item in manifest.get("rules", []) if item.get("file")]
        code_dir = node.get("code_dir")
        code_dirs = code_dir if isinstance(code_dir, list) else [code_dir] if code_dir else []
        files = [self.file_entry("data", f"{node['path']}/{name}") for name in code_dirs]
        files.append(self.file_entry("data", f"{node['path']}/output/manifest.json"))
        history = []
        art_dir = base / "artifacts"
        if art_dir.is_dir():
            history += [{"name": p.name, "ref": f"data:{p.relative_to(self.data_root).as_posix()}", "location": "本地"}
                        for p in sorted(art_dir.iterdir(), reverse=True) if p.is_dir()]
        prefix = node["path"] + "/artifacts/"
        for batch, path in archive_batches(self.data_root, False).items():
            if batch.startswith(prefix) and not (self.data_root / batch).exists():
                history.append({"name": Path(batch).name, "ref": f"data:{batch}", "location": "归档" if path.exists() else "归档不可用"})
        history.sort(key=lambda item: item["name"], reverse=True)
        return {"id": node_id, "name": node["path"].removeprefix("nodes/"), "line": node.get("line"),
                "naming_basis": node.get("naming_basis", ""), "kind": node.get("kind", "node"), "lifecycle": node.get("lifecycle", "active"), "parent": node.get("parent"),
                "run": node.get("run", []), "state": next(n for n in self.overview()["nodes"] if n["id"] == node_id),
                "docs": docs, "files": files, "outputs": outputs, "rules": rules,
                "upstream": upstream, "declared_upstream": node.get("upstream", []),
                "downstream": [n["id"] for n in payload["nodes"] if node_id in n.get("upstream", [])] +
                              ([SITE_ID] if node_id in {s["node"] for s in self._latest_site()["upstream"]} else []),
                "pending": node.get("pending", []), "manifest": {k: manifest.get(k) for k in ("version", "published_at", "artifact", "notes", "checks")},
                "history": history}

    def _site_history(self) -> list[dict]:
        history = [{"name": p.name, "ref": f"web:artifact/{p.name}", "location": "本地"} for p, _ in self._site_batches()]
        for batch, path in archive_batches(self.web_root, True).items():
            if not (self.web_root / batch).exists():
                history.append({"name": Path(batch).name, "ref": f"web:{batch}", "location": "归档" if path.exists() else "归档不可用"})
        return sorted(history, key=lambda item: item["name"], reverse=True)

    def _events_from_disk(self) -> list[dict]:
        events = []
        nodes = self._pipeline()["nodes"]
        for node in nodes:
            directory = self.data_root / node["path"] / "artifacts"
            if not directory.is_dir():
                continue
            for batch in directory.iterdir():
                if not batch.is_dir():
                    continue
                for filename, kind in (("run.json", "运行"), ("manifest.json", "发布")):
                    path = batch / filename
                    if not path.is_file():
                        continue
                    record = read_json(path, self.data_root)
                    if not record:
                        continue
                    relative = path.relative_to(self.data_root).as_posix()
                    state = record.get("status", "已发布")
                    if isinstance(state, dict):
                        state = state.get("status", "未知")
                    command = record.get("command") or []
                    if isinstance(command, str):
                        command = [command]
                    event_key = (f"data/发布/{node['id']}/{record.get('version') or relative}"
                                 if kind == "发布" else f"data/运行/{relative}")
                    events.append({"event_key": event_key, "node_id": node["id"], "kind": kind,
                                   "occurred_at": record.get("finished_at") or record.get("published_at") or record.get("created_at") or batch.name[:10],
                                   "status": str(state), "title": batch.name, "file_ref": f"data:{relative}",
                                   "detail": "、".join(map(str, command)) if kind == "运行" else f"版本 {record.get('version', '—')}"})
        existing_keys = {event["event_key"] for event in events}
        for node in nodes:
            path = self.data_root / node["path"] / "output" / "manifest.json"
            record = read_json(path, self.data_root)
            if not record:
                continue
            relative = path.relative_to(self.data_root).as_posix()
            event_key = f"data/发布/{node['id']}/{record.get('version') or relative}"
            if event_key not in existing_keys:
                events.append({"event_key": event_key, "node_id": node["id"], "kind": "发布",
                               "occurred_at": record.get("published_at") or record.get("version", ""),
                               "status": "已发布", "title": record.get("artifact", node["path"]).split("/")[-1],
                               "file_ref": f"data:{relative}", "detail": f"版本 {record.get('version', '—')}"})
        for folder, record in self._site_batches():
            publish = record.get("publish") or {}
            public = (publish.get("public") or {}).get("status", "未发布")
            nas = (publish.get("nas") or {}).get("status", "未发布")
            steps = record.get("steps") or {}
            build = (steps.get("build_public_site") or {}).get("status", "未执行") if isinstance(steps, dict) else "未记录"
            events.append({"event_key": f"web/批次/{folder.name}", "node_id": SITE_ID, "kind": "网站批次",
                           "occurred_at": record.get("created_at") or folder.name[:10],
                           "status": record.get("status", "未知"), "title": folder.name,
                           "file_ref": f"web:artifact/{folder.name}/artifact.json",
                           "detail": f"构建 {build}；本地 {public}；NAS {nas}"})
        return events

    def sync_events(self) -> None:
        with self.lock:
            events = self._events_from_disk()
            with self._connect() as db:
                db.executemany("""
                    INSERT INTO auto_events(event_key,node_id,kind,occurred_at,status,title,file_ref,detail,fingerprint)
                    VALUES (:event_key,:node_id,:kind,:occurred_at,:status,:title,:file_ref,:detail,:fingerprint)
                    ON CONFLICT(event_key) DO UPDATE SET occurred_at=excluded.occurred_at,status=excluded.status,
                        title=excluded.title,file_ref=excluded.file_ref,detail=excluded.detail,fingerprint=excluded.fingerprint
                    WHERE auto_events.fingerprint != excluded.fingerprint
                """, [{**event, "fingerprint": json.dumps(event, ensure_ascii=False, sort_keys=True)} for event in events])

    def events(self, node_id: str | None = None, limit: int = 120) -> list[dict]:
        self.sync_events()
        limit = max(1, min(limit, 300))
        with self._connect() as db:
            if node_id:
                auto = [dict(row) for row in db.execute("SELECT * FROM auto_events WHERE node_id=? ORDER BY occurred_at DESC LIMIT ?", (node_id, limit))]
                notes = [dict(row) for row in db.execute("SELECT * FROM notes WHERE node_id=? ORDER BY created_at DESC LIMIT ?", (node_id, limit))]
            else:
                auto = [dict(row) for row in db.execute("SELECT * FROM auto_events ORDER BY occurred_at DESC LIMIT ?", (limit,))]
                notes = [dict(row) for row in db.execute("SELECT * FROM notes ORDER BY created_at DESC LIMIT ?", (limit,))]
        result = [{**event, "type": "auto"} for event in auto]
        result += [{**note, "type": "note", "kind": "人工处理", "occurred_at": note["created_at"],
                    "title": note["summary"], "status": "已记录"} for note in notes]
        return sorted(result, key=lambda item: item["occurred_at"], reverse=True)[:limit]

    def add_note(self, payload: dict) -> dict:
        node_id = str(payload.get("node_id", ""))
        ids = {node["id"] for node in self._pipeline()["nodes"]} | {SITE_ID}
        if node_id not in ids:
            raise ValueError("未知节点")
        summary = str(payload.get("summary", "")).strip()
        detail = str(payload.get("detail", "")).strip()
        if not summary or len(summary) > 200 or len(detail) > 5000:
            raise ValueError("摘要必填且不超过 200 字；详情不超过 5000 字")
        file_ref = str(payload.get("file_ref", "")).strip() or None
        if file_ref:
            self.resolve_ref(file_ref)
        event_key = str(payload.get("event_key", "")).strip() or None
        with self.lock:
            self._backup_before_write()
            with self._connect() as db:
                if event_key and not db.execute("SELECT 1 FROM auto_events WHERE event_key=?", (event_key,)).fetchone():
                    raise ValueError("关联批次不存在")
                now = datetime.now(CHINA_TZ).isoformat(timespec="seconds")
                cursor = db.execute("INSERT INTO notes(node_id,event_key,summary,detail,file_ref,created_at) VALUES (?,?,?,?,?,?)",
                                    (node_id, event_key, summary, detail, file_ref, now))
                return {"id": cursor.lastrowid, "created_at": now}

    def preview(self, ref: str) -> dict:
        path, location = self.resolve_ref(ref)
        if not path.is_file():
            raise FileNotFoundError(f"{location}：{path}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError("此格式请使用默认程序打开")
        with path.open("rb") as handle:
            raw = handle.read(MAX_PREVIEW + 1)
        truncated = len(raw) > MAX_PREVIEW
        raw = raw[:MAX_PREVIEW]
        for encoding in ("utf-8-sig", "gb18030"):
            try:
                content = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            content = raw.decode("utf-8", errors="replace")
        return {"path": str(path), "location": location, "content": content, "truncated": truncated}


def handler_for(portal: Portal):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, data, status=200):
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _error(self, error):
            status = 409 if isinstance(error, Conflict) else 404 if isinstance(error, (KeyError, FileNotFoundError)) else 400 if isinstance(error, ValueError) else 500
            self._json({"error": str(error)}, status)

        def _host_valid(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def do_GET(self):
            if not self._host_valid():
                self._json({"error": "无效本机 Host"}, 403)
                return
            url = urlsplit(self.path)
            query = parse_qs(url.query)
            try:
                if url.path in ("/", "/index.html"):
                    raw = (portal.data_root / "portal" / "index.html").read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'")
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                elif url.path in ("/materials.js", "/materials.css"):
                    raw = (portal.data_root / "portal" / url.path[1:]).read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/javascript; charset=utf-8" if url.path.endswith(".js") else "text/css; charset=utf-8")
                    self.send_header("Content-Length", str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                elif url.path == "/api/session":
                    self._json({"token": portal.token, "upload_limit": portal.materials.upload_limit})
                elif url.path == "/api/materials":
                    self._json(portal.materials.listing(query.get("node", [None])[0], query.get("q", [""])[0], int(query.get("page", [1])[0])))
                elif url.path == "/api/material":
                    self._json(portal.materials.read(query["node"][0], query["path"][0], int(query.get("page", [1])[0]), q=query.get("q", [""])[0]))
                elif url.path == "/api/materials/download":
                    path = portal.materials.path(query["node"][0], query["path"][0])
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Disposition", "attachment; filename=material.bin")
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.send_header("Content-Length", str(path.stat().st_size))
                    self.end_headers()
                    with path.open("rb") as stream:
                        while block := stream.read(1024**2):
                            self.wfile.write(block)
                elif url.path == "/api/materials/history":
                    self._json(portal.materials.history(query.get("node", [None])[0], query.get("path", [None])[0]))
                elif url.path == "/api/content":
                    sha = query.get("sha", [""])[0]
                    if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
                        raise ValueError("请输入完整 SHA-256")
                    index = ContentIndex(portal.data_root, persistent=True)
                    try:
                        index.rebuild()
                        locations = index.entries(sha)
                    finally:
                        index.close()
                    for node_id, _, p in portal.materials.iter_files():
                        if raw_sha256(p) == sha:
                            locations.append({"artifact_file": p.relative_to(portal.data_root).as_posix(), "kind": "维护工作副本", "node": node_id})
                    consumers = []
                    for n in portal._pipeline()["nodes"]:
                        manifest = read_json(portal.data_root / n["path"] / "output/manifest.json", portal.data_root)
                        for item in manifest.get("deliverables", []):
                            if item.get("sha256") == sha:
                                locations.append({"artifact_file": f"{n['path']}/output/{item['file']}", "kind": "当前工作交付", "node": n["id"], "version": manifest.get("version")})
                        for record_path in (portal.data_root / n["path"] / "artifacts").glob("*/run.json"):
                            record = read_json(record_path, portal.data_root)
                            for item in record.get("inputs", []):
                                if (item.get("raw_sha256") or item.get("sha256")) == sha:
                                    consumers.append({"node": n["id"], "record": record_path.relative_to(portal.data_root).as_posix(), "version": record.get("version"), "input": item.get("file"), "status": record.get("status")})
                    self._json({"sha256": sha, "locations": locations, "consumers": consumers})
                elif url.path == "/api/storage":
                    from storage_audit import walk, classify
                    from archive_old_artifacts import plan_moves
                    categories = {}
                    for parts, size in walk(portal.data_root):
                        category = classify(parts)
                        categories[category] = categories.get(category, 0) + size
                    moves = plan_moves(portal.data_root, 5, portal.data_root / ".bak" / "artifacts")
                    self._json({"categories": categories, "archive_candidates": [p.relative_to(portal.data_root).as_posix() for p, _ in moves], "note": "只读预演；保护当前及传递引用、最近5批和未提交文件。"})
                elif url.path == "/api/overview":
                    self._json(portal.overview())
                elif url.path == "/api/node":
                    self._json(portal.node(query.get("id", [""])[0]))
                elif url.path == "/api/events":
                    self._json(portal.events(query.get("node", [None])[0]))
                elif url.path == "/api/preview":
                    self._json(portal.preview(query.get("ref", [""])[0]))
                else:
                    self._json({"error": "未找到"}, 404)
            except Exception as error:
                self._error(error)

        def do_POST(self):
            self._write()

        def do_PUT(self):
            self._write()

        def do_DELETE(self):
            self._write()

        def _write(self):
            origin = self.headers.get("Origin", "")
            if (not self._host_valid() or origin != f"http://127.0.0.1:{self.server.server_port}"
                    or self.headers.get("X-Portal-Request") != "1"
                    or not secrets.compare_digest(self.headers.get("X-Portal-Token", ""), portal.token)):
                self._json({"error": "只接受持有令牌的本机页面请求"}, 403)
                return
            try:
                url = urlsplit(self.path)
                length = int(self.headers.get("Content-Length", "0"))
                if self.headers.get("Transfer-Encoding") or length < 1 or length > portal.materials.upload_limit:
                    raise ValueError("请求大小无效或超过上传上限")
                portal._backup_before_write()
                if url.path == "/api/materials/upload" and self.command == "POST":
                    if self.headers.get("Content-Type") != "application/octet-stream":
                        raise ValueError("上传需要 application/octet-stream")
                    q = parse_qs(url.query, keep_blank_values=True)
                    data = {k: v[0] for k, v in q.items()}
                    data["expected_sha"] = data.get("expected_sha") or None
                    portal.materials.path(data["node"], data["path"])
                    with tempfile.TemporaryFile() as spool:
                        remaining = length
                        while remaining:
                            block = self.rfile.read(min(1024**2, remaining))
                            if not block:
                                raise ValueError("上传内容不完整")
                            spool.write(block)
                            remaining -= len(block)
                        spool.seek(0)
                        result = portal.materials.mutate("update" if data["expected_sha"] else "create", data, spool.read())
                    portal._snapshot = None
                    self._json(result)
                    return
                if self.headers.get("Content-Type", "").split(";")[0] != "application/json" or length > 8 * 1024**2:
                    raise ValueError("JSON 请求大小或类型无效")
                raw = self.rfile.read(length)
                if len(raw) != length:
                    raise ValueError("请求不完整")
                data = json.loads(raw)
                routes = {("POST", "/api/materials"): "create", ("PUT", "/api/material"): "update",
                          ("DELETE", "/api/material"): "delete", ("POST", "/api/materials/rename"): "rename",
                          ("POST", "/api/materials/restore"): "restore"}
                if (self.command, url.path) in routes:
                    result = portal.materials.mutate(routes[(self.command, url.path)], data)
                    portal._snapshot = None
                    self._json(result)
                elif self.command == "POST" and url.path == "/api/materials/preview":
                    with portal.lock:
                        self._json(portal.materials.prepare(data)[2])
                elif self.command == "POST" and url.path == "/api/notes":
                    self._json(portal.add_note(data), 201)
                elif self.command == "POST" and url.path == "/api/open":
                    path, location = portal.resolve_ref(str(data.get("ref", "")))
                    if not path.exists():
                        raise FileNotFoundError(f"{location}：{path}")
                    if path.is_file() and path.suffix.lower() not in {".md", ".txt", ".csv", ".tsv", ".json", ".jsonl", ".yaml", ".yml", ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".xlsx", ".docx"}:
                        raise ValueError("此文件只提供预览或下载，不能通过看板执行")
                    os.startfile(path)
                    self._json({"opened": str(path), "location": location})
                else:
                    self._json({"error": "未找到"}, 404)
            except Exception as error:
                self._error(error)

        def log_message(self, format, *args):
            print(f"[{self.log_date_time_string()}] {format % args}")

    return Handler


class LoopbackServer(ThreadingHTTPServer):
    # On Windows SO_REUSEADDR can attach to another process's listening port.
    allow_reuse_address = False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--web-repo", type=Path, default=ROOT.parent / "pipeline_carstable_to_webapp")
    parser.add_argument("--db", type=Path)
    parser.add_argument("--upload-limit-mib", type=int, default=200)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    portal = Portal(ROOT, args.web_repo, args.db, max(1, args.upload_limit_mib) * 1024**2)
    handler = handler_for(portal)
    try:
        server = LoopbackServer(("127.0.0.1", args.port), handler)
    except OSError:
        if args.port == 0:
            raise
        server = LoopbackServer(("127.0.0.1", 0), handler)
        print(f"端口 {args.port} 已被占用，改用空闲端口。")
    address = f"http://127.0.0.1:{server.server_port}/"
    print(f"流水线管理入口：{address}")
    if not args.no_browser:
        webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
