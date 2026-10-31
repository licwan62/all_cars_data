"""Exercise actual browser CRUD against an isolated repository, never real node data."""
import json
import shutil
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from pipeline_portal import Portal, handler_for


def main():
    from playwright.sync_api import sync_playwright
    source = Path(__file__).resolve().parents[1]
    report = source / "reports/结构优化实施"
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="portal-browser-") as temp:
        root = Path(temp)
        (root / "portal").mkdir()
        for name in ("index.html", "materials.js", "materials.css"):
            shutil.copy2(source / "portal" / name, root / "portal" / name)
        (root / "pipeline.json").write_text(json.dumps({"nodes": [{"id":"sample", "path":"nodes/A0.测试", "line":"A", "layer":0, "upstream":[], "pending":[]}]}), encoding="utf-8")
        folder = root / "nodes/A0.测试/data"
        folder.mkdir(parents=True)
        (folder / "表.csv").write_bytes('\ufeff编码,说明\r\n001,原文\r\n'.encode("utf-8"))
        portal = Portal(root)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(portal))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        errors = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel="msedge", headless=True)
                page = browser.new_page(viewport={"width":1440,"height":950})
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/")
                page.wait_for_selector("#counts .badge")
                page.click("#materials-tab")
                page.locator("[data-material-index]").first.click()
                page.wait_for_selector("#table-body input")
                page.locator("#table-body input").nth(1).fill("已修正")
                page.fill("#material-reason", "浏览器回归测试")
                page.click("#material-preview")
                page.locator("#material-save:enabled").wait_for()
                assert "已修正" in page.locator("#material-diff").inner_text()
                page.screenshot(path=str(report / "浏览器CRUD-差异预览.png"))
                page.click("#material-save")
                page.locator("#material-dialog").wait_for(state="hidden")
                page.locator("#material-next-step").filter(has_text="尚无活跃生产入口").wait_for()
                page.click("#refresh")
                assert "尚无活跃生产入口" in page.locator("#material-next-step").inner_text()
                assert (folder / "表.csv").read_bytes() == '\ufeff编码,说明\r\n001,已修正\r\n'.encode("utf-8")
                # Change the disk externally after opening: save must be rejected.
                page.locator("[data-material-index]").first.click()
                page.wait_for_selector("#table-body input")
                page.locator("#table-body input").nth(1).fill("网页编辑")
                page.fill("#material-reason", "冲突回归")
                page.click("#material-preview")
                page.locator("#material-save:enabled").wait_for()
                external = '\ufeff编码,说明\r\n001,外部编辑\r\n'.encode("utf-8")
                (folder / "表.csv").write_bytes(external)
                page.click("#material-save")
                page.locator("#material-error").filter(has_text="外部修改").wait_for()
                assert (folder / "表.csv").read_bytes() == external
                browser.close()
            assert not errors, errors
            (report / "浏览器CRUD.json").write_text(json.dumps({"table_edit":True,"bom_crlf_and_codes_preserved":True,"external_conflict_rejected":True,"page_errors":errors,"isolated_repo":True}, indent=2), encoding="utf-8")
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)
    print("Isolated browser CRUD passed")


if __name__ == "__main__":
    main()
