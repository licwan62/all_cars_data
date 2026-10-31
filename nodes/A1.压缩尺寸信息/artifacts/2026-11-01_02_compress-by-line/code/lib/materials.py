"""Local data-file editing with byte revisions, content-addressed recovery and WAL audit."""
from __future__ import annotations
import csv
import difflib
import hashlib
import io
import json
import os
import re
import sqlite3
import tempfile
import threading
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

TEXT_LIMIT = 2 * 1024**2
TABLE_LIMIT = 50 * 1024**2
UPLOAD_LIMIT = 200 * 1024**2
TEXT_TYPES = {".json", ".jsonl", ".yaml", ".yml", ".md", ".txt"}
FORBIDDEN = re.compile(r'[<>:"\\|?*\x00-\x1f]')
RESERVED = re.compile(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", re.I)


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


class Conflict(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def timestamp():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def decode(raw):
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    try:
        return raw.decode(encoding), encoding
    except UnicodeDecodeError:
        return raw.decode("gb18030"), "gb18030"


def validate(raw, suffix):
    if suffix not in TEXT_TYPES | {".csv", ".tsv"}:
        return
    text, _ = decode(raw)
    if suffix == ".json":
        json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        import yaml
        yaml.safe_load(text)
    elif suffix == ".jsonl":
        for line in text.splitlines():
            if line.strip():
                json.loads(line)
    elif suffix in {".csv", ".tsv"}:
        rows = csv.reader(io.StringIO(text, newline=""), delimiter="\t" if suffix == ".tsv" else ",", strict=True)
        header = next(rows, [])
        if not header or any(not c for c in header) or len(set(header)) != len(header):
            raise ValueError("表头不能为空或重复")
        for number, row in enumerate(rows, 2):
            if len(row) != len(header):
                raise ValueError(f"第 {number} 条记录列数不符")


class Materials:
    def __init__(self, root, db_path, lock=None, upload_limit=UPLOAD_LIMIT):
        self.root = Path(root).resolve()
        self.db_path = Path(db_path)
        self.objects = self.db_path.parent / "objects"
        self.objects.mkdir(parents=True, exist_ok=True)
        self.lock = lock or threading.RLock()
        self.upload_limit = upload_limit
        with self.connect() as db:
            db.executescript("""
              PRAGMA journal_mode=WAL;
              CREATE TABLE IF NOT EXISTS materials(
                id TEXT PRIMARY KEY, node TEXT NOT NULL, path TEXT NOT NULL,
                purpose TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT '',
                owner TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT '待确认',
                deleted INTEGER NOT NULL DEFAULT 0, UNIQUE(node,path));
              CREATE TABLE IF NOT EXISTS material_audit(
                id INTEGER PRIMARY KEY, material_id TEXT NOT NULL, node TEXT NOT NULL,
                operation TEXT NOT NULL, old_path TEXT, new_path TEXT, before_sha TEXT,
                after_sha TEXT, occurred_at TEXT NOT NULL, reason TEXT NOT NULL,
                state TEXT NOT NULL, error TEXT NOT NULL DEFAULT '');
            """)
        self.recover()

    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=20, factory=ClosingConnection)
        db.row_factory = sqlite3.Row
        return db

    def nodes(self):
        return {n["id"]: n for n in json.loads((self.root / "pipeline.json").read_text(encoding="utf-8-sig"))["nodes"]}

    def path(self, node, relative):
        if not isinstance(relative, str) or not relative or relative.startswith("/"):
            raise ValueError("必须使用 data 内相对路径")
        parts = relative.split("/")
        if any(p in {"", ".", ".."} or p.endswith((" ", ".")) or p.startswith(".") or FORBIDDEN.search(p) or RESERVED.match(p) for p in parts):
            raise ValueError("非法文件路径")
        n = self.nodes()[node]
        base = self.root / n["path"] / "data"
        base.resolve().relative_to(self.root)
        candidate = base.joinpath(*parts)
        for p in [base, *candidate.parents, candidate]:
            if p.exists() and (p.is_symlink() or p.is_junction()):
                raise ValueError("不允许通过链接或 junction 编辑")
            if p == base:
                continue
        candidate.resolve().relative_to(base.resolve())
        return candidate

    def _metadata(self, node, relative):
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO materials(id,node,path) VALUES(?,?,?)", ("M-" + uuid.uuid4().hex, node, relative))
            return dict(db.execute("SELECT * FROM materials WHERE node=? AND path=?", (node, relative)).fetchone())

    def listing(self, node=None, q="", page=1, page_size=100):
        result = []
        nodes = self.nodes()
        for nid, n in nodes.items():
            if node and nid != node:
                continue
            base = self.root / n["path"] / "data"
            for path in sorted(base.rglob("*")):
                if not path.is_file() or any(p.startswith(".") or p == "__pycache__" for p in path.relative_to(base).parts):
                    continue
                rel = path.relative_to(base).as_posix()
                try:
                    self.path(nid, rel)
                except ValueError:
                    continue
                meta = self._metadata(nid, rel)
                if q.lower() not in (nid + rel + meta["purpose"] + meta["owner"]).lower():
                    continue
                result.append({**meta, "bytes": path.stat().st_size, "suffix": path.suffix.lower()})
        size = min(max(int(page_size), 1), 500)
        page = max(int(page), 1)
        return {"items": result[(page - 1)*size:page*size], "total": len(result), "page": page, "page_size": size}

    def impact(self, node, relative):
        nodes = self.nodes()
        affected, todo = set(), [node]
        while todo:
            current = todo.pop()
            for nid, n in nodes.items():
                if current in n.get("upstream", []) and nid not in affected and nid != node:
                    affected.add(nid)
                    todo.append(nid)
        references = []
        n = nodes[node]
        folders = n.get("code_dir") or []
        if isinstance(folders, str):
            folders = [folders]
        for folder in folders:
            for p in (self.root / n["path"] / folder).rglob("*.py"):
                if Path(relative).name in p.read_text(encoding="utf-8-sig", errors="replace"):
                    references.append(p.relative_to(self.root).as_posix())
        return {"node": node, "downstream": sorted(affected), "code_references": references,
                "limitation": "静态文件名匹配可能遗漏动态目录读取；未发现引用不等于未使用。",
                "commands": [f"python scripts/verify_pipeline.py --rebuild {node} --fresh", f"python scripts/publish_release.py --nodes {node}"]}

    def read(self, node, relative, page=1, page_size=100, q="", download=False):
        with self.lock:
            path = self.path(node, relative)
            size = path.stat().st_size
            meta = self._metadata(node, relative)
            h = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024**2), b""):
                    h.update(block)
            result = {**meta, "sha256": h.hexdigest(), "bytes": size, "impact": self.impact(node, relative), "mode": "binary"}
            if size <= TABLE_LIMIT and path.suffix.lower() in {".csv", ".tsv"}:
                raw = path.read_bytes()
                text, encoding = decode(raw)
                reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
                header = next(reader, [])
                rows = [{"index": i, "values": row} for i, row in enumerate(reader) if q.lower() in "\t".join(row).lower()]
                size_page = min(max(int(page_size), 1), 500)
                start = (max(int(page), 1) - 1)*size_page
                result.update(mode="table", header=header, rows=rows[start:start+size_page], total=len(rows), page=max(int(page), 1), page_size=size_page, encoding=encoding)
            elif size <= TEXT_LIMIT and path.suffix.lower() in TEXT_TYPES:
                text, encoding = decode(path.read_bytes())
                result.update(mode="text", content=text, encoding=encoding)
            return result

    def _put_object(self, raw):
        sha = digest(raw)
        path = self.objects / sha[:2] / sha
        if path.exists():
            if digest(path.read_bytes()) != sha:
                raise ValueError("恢复对象损坏")
        else:
            self._atomic(path, raw)
        return sha

    def _object(self, sha):
        raw = (self.objects / sha[:2] / sha).read_bytes()
        if digest(raw) != sha:
            raise ValueError("恢复对象 SHA 不匹配")
        return raw

    @staticmethod
    def _atomic(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".material-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
        finally:
            Path(name).unlink(missing_ok=True)

    def _revision(self, path, expected):
        raw = path.read_bytes() if path.is_file() else None
        actual = digest(raw) if raw is not None else None
        if expected != actual:
            raise Conflict("文件已被外部修改，请重新读取后合并；未覆盖当前文件")
        return raw

    def prepare(self, data):
        node, relative = data["node"], data["path"]
        path = self.path(node, relative)
        before = self._revision(path, data.get("expected_sha"))
        if "content" in data:
            if path.suffix.lower() not in TEXT_TYPES | {".csv", ".tsv"}:
                raise ValueError("此文件只支持上传替换")
            encoding = decode(before)[1] if before is not None else "utf-8"
            content = data["content"]
            if before is not None:
                old_text = decode(before)[0]
                newline = "\r\n" if "\r\n" in old_text else "\r" if "\r" in old_text and "\n" not in old_text else "\n"
                content = content.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline)
            after = content.encode(encoding)
            if len(after) > TEXT_LIMIT:
                raise ValueError("文本编辑上限 2 MiB；请使用上传替换")
        elif "changes" in data:
            if before is None or len(before) > TABLE_LIMIT or path.suffix.lower() not in {".csv", ".tsv"}:
                raise ValueError("表格编辑上限 50 MiB")
            text, encoding = decode(before)
            delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
            rows = list(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter))
            header, rows = rows[0], rows[1:]
            edits, additions = {}, []
            for change in data["changes"]:
                op = change["op"]
                if op == "insert":
                    additions.append(change["values"])
                else:
                    i = int(change["index"])
                    if i < 0 or i >= len(rows) or i in edits or op not in {"update", "delete"}:
                        raise ValueError("非法或重复行编辑")
                    edits[i] = change
            for i, change in sorted(edits.items(), reverse=True):
                if change["op"] == "delete":
                    del rows[i]
                else:
                    rows[i] = change["values"]
            rows += additions
            if any(len(row) != len(header) or any(not isinstance(v, str) for v in row) for row in rows):
                raise ValueError("表格值必须为字符串且列数一致")
            stream = io.StringIO(newline="")
            newline = "\r\n" if "\r\n" in text else "\n"
            writer = csv.writer(stream, delimiter=delimiter, lineterminator=newline)
            writer.writerows([header, *rows])
            rendered = stream.getvalue()
            if text and not text.endswith(("\r", "\n")):
                rendered = rendered[:-len(newline)]
            after = rendered.encode(encoding)
        elif "metadata" in data and before is not None:
            after = before
        else:
            raise ValueError("缺少文本或行编辑内容")
        validate(after, path.suffix.lower())
        try:
            old_text = decode(before or b"")[0].splitlines(True)
            new_text = decode(after)[0].splitlines(True)
            diff = "".join(difflib.unified_diff(old_text, new_text, fromfile=relative, tofile=relative))[:100000]
        except UnicodeError:
            diff = "二进制替换"
        return before, after, {"before_sha": digest(before) if before is not None else None, "after_sha": digest(after), "diff": diff, "impact": self.impact(node, relative)}

    def mutate(self, operation, data, raw=None):
        with self.lock:
            node, relative = data["node"], data["path"]
            path = self.path(node, relative)
            before = self._revision(path, data.get("expected_sha"))
            new_relative = data.get("new_path", relative)
            target = self.path(node, new_relative)
            if operation == "create" and before is not None:
                raise Conflict("文件已存在")
            if operation in {"update", "rename", "delete"} and before is None:
                raise FileNotFoundError(relative)
            if operation == "rename" and target.exists():
                raise Conflict("目标文件已存在")
            if operation == "delete":
                after = None
            elif operation == "rename":
                after = before
            elif operation == "restore":
                with self.connect() as db:
                    event = db.execute("SELECT * FROM material_audit WHERE id=? AND node=? AND state='committed'", (int(data["event_id"]), node)).fetchone()
                if not event or relative not in {event["old_path"], event["new_path"]}:
                    raise ValueError("恢复记录与文件不匹配")
                if event["material_id"] != self._metadata(node, relative)["id"]:
                    raise ValueError("恢复记录属于另一份资料")
                if event["operation"] == "rename":
                    new_relative = event["old_path"]
                    target = self.path(node, new_relative)
                    if target.exists():
                        raise Conflict("恢复原名称的目标已存在")
                after = self._object(event["before_sha"]) if event["before_sha"] else None
            elif raw is not None:
                after = raw
            else:
                _, after, _ = self.prepare(data)
            if after is not None:
                if len(after) > self.upload_limit:
                    raise ValueError("上传超过上限")
                validate(after, target.suffix.lower())
            reason = str(data.get("reason", "")).strip()
            if not reason or len(reason) > 2000:
                raise ValueError("必须填写修改原因（最多 2000 字）")
            meta = self._metadata(node, relative)
            before_sha = self._put_object(before) if before is not None else None
            after_sha = self._put_object(after) if after is not None else None
            with self.connect() as db:
                event_id = db.execute("INSERT INTO material_audit(material_id,node,operation,old_path,new_path,before_sha,after_sha,occurred_at,reason,state) VALUES(?,?,?,?,?,?,?,?,?,'prepared')", (meta["id"], node, operation, relative, new_relative, before_sha, after_sha, timestamp(), reason)).lastrowid
            # Check again after snapshotting; external editors are not covered by our lock.
            try:
                self._revision(path, data.get("expected_sha"))
            except Conflict as error:
                with self.connect() as db:
                    db.execute("UPDATE material_audit SET state='aborted',error=? WHERE id=?", (str(error), event_id))
                raise
            try:
                if after is None:
                    path.unlink(missing_ok=True)
                else:
                    self._atomic(target, after)
                    if target != path:
                        path.unlink()
                with self.connect() as db:
                    db.execute("UPDATE materials SET path=?, deleted=? WHERE id=?", (new_relative, int(after is None), meta["id"]))
                    for key in ("purpose", "source", "owner", "status"):
                        if key in data.get("metadata", {}):
                            db.execute(f"UPDATE materials SET {key}=? WHERE id=?", (str(data["metadata"][key])[:2000], meta["id"]))
                    db.execute("UPDATE material_audit SET state='committed' WHERE id=?", (event_id,))
            except BaseException:
                self.recover()
                raise
            return {"id": meta["id"], "event_id": event_id, "sha256": after_sha, "path": new_relative, "state": "维护资料已变更、产物待验证", "impact": self.impact(node, new_relative)}

    def history(self, node=None, relative=None):
        with self.connect() as db:
            query = "SELECT * FROM material_audit WHERE 1=1"
            args = []
            if node:
                query += " AND node=?"
                args.append(node)
            if relative:
                meta = db.execute("SELECT id FROM materials WHERE node=? AND path=?", (node, relative)).fetchone()
                query += " AND material_id=?"
                args.append(meta[0] if meta else "")
            return [dict(r) for r in db.execute(query + " ORDER BY id DESC LIMIT 500", args)]

    def recover(self):
        with self.lock, self.connect() as db:
            events = db.execute("SELECT * FROM material_audit WHERE state='prepared'").fetchall()
            for e in events:
                try:
                    path = self.path(e["node"], e["old_path"])
                    target = self.path(e["node"], e["new_path"])
                    current = digest(path.read_bytes()) if path.is_file() else None
                    if current not in {e["before_sha"], e["after_sha"], None}:
                        raise Conflict("恢复时发现外部修改，保留现场")
                    if target != path and target.exists():
                        if digest(target.read_bytes()) != e["after_sha"]:
                            raise Conflict("重命名目标存在外部修改，保留现场")
                        target.unlink()
                    if e["before_sha"]:
                        self._atomic(path, self._object(e["before_sha"]))
                    else:
                        path.unlink(missing_ok=True)
                    db.execute("UPDATE material_audit SET state='rolled_back' WHERE id=?", (e["id"],))
                except Exception as error:
                    db.execute("UPDATE material_audit SET state='needs_attention',error=? WHERE id=?", (str(error), e["id"]))
