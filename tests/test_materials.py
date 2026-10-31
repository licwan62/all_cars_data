import json
import threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest
from materials import Materials, Conflict, digest, validate
from pipeline_portal import Portal, handler_for


@pytest.fixture
def service(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "pipeline.json").write_text(json.dumps({"nodes": [{"id": "a", "path": "nodes/A0.a", "upstream": [], "line": "A"}, {"id": "b", "path": "nodes/A1.b", "upstream": ["a"], "line": "A"}]}), encoding="utf-8")
    folder = root / "nodes/A0.a/data"
    folder.mkdir(parents=True)
    return Materials(root, root / "portal/data/journal.sqlite3"), folder


def create(s, path, content):
    return s.mutate("create", {"node": "a", "path": path, "expected_sha": None, "content": content, "reason": "新增依据"})


def test_crud_revisions_and_independent_material_identity(service):
    s, folder = service
    first = create(s, "规则/中文.json", '{"value":1}')
    second = create(s, "其他.json", '{"value":1}')
    assert first["id"] != second["id"]
    assert len(list(s.objects.rglob(first["sha256"]))) == 1
    with pytest.raises(Conflict):
        s.mutate("update", {"node": "a", "path": "规则/中文.json", "expected_sha": "0"*64, "content": "{}", "reason": "修改"})
    renamed = s.mutate("rename", {"node": "a", "path": "规则/中文.json", "new_path": "规则/改名.json", "expected_sha": first["sha256"], "reason": "改名"})
    assert renamed["id"] == first["id"]
    deleted = s.mutate("delete", {"node": "a", "path": renamed["path"], "expected_sha": renamed["sha256"], "reason": "停用"})
    assert not (folder / renamed["path"]).exists()
    s.mutate("restore", {"node": "a", "path": renamed["path"], "expected_sha": None, "event_id": deleted["event_id"], "reason": "恢复"})
    assert s.read("a", renamed["path"])["sha256"] == first["sha256"]
    assert first["impact"]["downstream"] == ["b"]


def test_table_preserves_bom_crlf_codes_and_multiline(service):
    s, folder = service
    raw = '\ufeff编码,说明\r\n001,"第一行\r\n第二行"\r\n002,NA\r\n'.encode("utf-8")
    result = s.mutate("create", {"node":"a", "path":"表.csv", "expected_sha":None, "reason":"导入"}, raw)
    page = s.read("a", "表.csv", page_size=1)
    assert page["rows"][0]["values"] == ["001", "第一行\r\n第二行"]
    updated = s.mutate("update", {"node":"a", "path":"表.csv", "expected_sha":result["sha256"], "reason":"修正", "changes":[{"op":"update", "index":1,"values":["002","更新"]},{"op":"insert","values":["003","NA"]}]})
    data = (folder / "表.csv").read_bytes()
    assert data.startswith(b"\xef\xbb\xbf") and b"003,NA\r\n" in data and b"001," in data
    assert s.read("a", "表.csv", q="003")["rows"][0]["index"] == 2
    assert updated["sha256"] != result["sha256"]


@pytest.mark.parametrize("path", ["../output/x.csv", "/tmp/a", "a\\b", "a:b", "CON.txt", "x/.. /a", "x.", ".hidden", "x//y", "x/../y"])
def test_windows_path_rejection(service, path):
    s, _ = service
    with pytest.raises(ValueError):
        s.path("a", path)


def test_validation_and_external_conflict_leave_files_unchanged(service):
    s, folder = service
    result = create(s, "规则.json", "{}")
    with pytest.raises(ValueError):
        s.mutate("update", {"node":"a","path":"规则.json","expected_sha":result["sha256"],"content":"{","reason":"非法"})
    assert (folder / "规则.json").read_text() == "{}"
    (folder / "规则.json").write_text('{"external":true}')
    with pytest.raises(Conflict):
        s.mutate("delete", {"node":"a","path":"规则.json","expected_sha":result["sha256"],"reason":"删除"})
    for raw in (b"a,a\n1,2\n", b"a,b\n1\n"):
        with pytest.raises(ValueError):
            validate(raw, ".csv")


def test_text_line_endings_and_rename_restore(service):
    s, folder = service
    first = s.mutate("create", {"node":"a", "path":"说明.txt", "expected_sha":None, "reason":"导入"}, b"a\r\nb\r\n")
    changed = s.mutate("update", {"node":"a", "path":"说明.txt", "expected_sha":first["sha256"], "content":"a\nc\n", "reason":"修正"})
    assert (folder/"说明.txt").read_bytes() == b"a\r\nc\r\n"
    renamed = s.mutate("rename", {"node":"a", "path":"说明.txt", "expected_sha":changed["sha256"], "new_path":"新名称.txt", "reason":"改名"})
    restored = s.mutate("restore", {"node":"a", "path":"新名称.txt", "expected_sha":renamed["sha256"], "event_id":renamed["event_id"], "reason":"恢复名称"})
    assert restored["id"] == first["id"] and restored["path"] == "说明.txt"
    assert not (folder/"新名称.txt").exists()


def test_interrupted_write_recovers_and_preserves_external_change(service):
    s, folder = service
    original = create(s, "规则.txt", "before")
    after = s._put_object(b"after")
    with s.connect() as db:
        event = db.execute("INSERT INTO material_audit(material_id,node,operation,old_path,new_path,before_sha,after_sha,occurred_at,reason,state) VALUES(?,?,?,?,?,?,?,?,?,'prepared')", (original["id"],"a","update","规则.txt","规则.txt",original["sha256"],after,"now","test")).lastrowid
    (folder / "规则.txt").write_bytes(b"after")
    s.recover()
    assert (folder / "规则.txt").read_bytes() == b"before"
    with s.connect() as db:
        db.execute("UPDATE material_audit SET state='prepared' WHERE id=?", (event,))
    (folder / "规则.txt").write_bytes(b"external")
    s.recover()
    assert (folder / "规则.txt").read_bytes() == b"external"
    assert s.history()[0]["state"] == "needs_attention"


def test_http_token_host_conflict_and_stream_upload(service):
    s, _ = service
    portal = Portal(s.root, db_path=s.db_path, upload_limit=1024)
    server = ThreadingHTTPServer(("127.0.0.1",0), handler_for(portal))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    def send(path, body, token=portal.token, content_type="application/json", method="POST"):
        data = json.dumps(body).encode() if isinstance(body,dict) else body
        return urlopen(Request(base+path,data=data,method=method,headers={"Origin":base,"Content-Type":content_type,"X-Portal-Request":"1","X-Portal-Token":token}))
    try:
        with pytest.raises(HTTPError) as error:
            send("/api/materials",{},token="wrong")
        assert error.value.code==403
        with send("/api/materials",{"node":"a","path":"x.txt","expected_sha":None,"content":"x","reason":"test"}) as response:
            result=json.load(response)
        with pytest.raises(HTTPError) as error:
            send("/api/material",{"node":"a","path":"x.txt","expected_sha":"wrong","content":"y","reason":"test"},method="PUT")
        assert error.value.code==409
        with send("/api/materials/upload?node=a&path=ref.bin&reason=test", b"\x00\r\n\xff",content_type="application/octet-stream") as response:
            assert json.load(response)["sha256"]==digest(b"\x00\r\n\xff")
        with pytest.raises(HTTPError) as error:
            send("/api/materials/upload?node=a&path=large.bin&reason=test",b"x"*1025,content_type="application/octet-stream")
        assert error.value.code==400
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_maintenance_next_steps_require_real_generation_and_active_entry(service):
    s, _ = service
    config = s.root / "pipeline.json"
    pipeline = json.loads(config.read_text(encoding="utf-8"))
    node = pipeline["nodes"][0]
    node["run"] = ["python src/main.py"]
    config.write_text(json.dumps(pipeline), encoding="utf-8")
    impact = s.impact("a", "rules.json")
    assert impact["commands"] == ["python scripts/run_nodes.py --nodes a",
                                  "python scripts/verify_pipeline.py --rebuild a --fresh"]
    assert impact["downstream"] == ["b"]
    for change in ({"lifecycle": "planned"}, {"lifecycle": "legacy"},
                   {"lifecycle": "active", "kind": "container"}):
        node.update(change)
        config.write_text(json.dumps(pipeline), encoding="utf-8")
        assert s.impact("a", "rules.json")["commands"] == []
