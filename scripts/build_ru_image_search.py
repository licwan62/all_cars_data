"""Build an auditable, generation-based RU image-search handoff report."""
from __future__ import annotations

import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch
from node_paths import node_output


def url_key(value):
    return urlsplit(value).path.rstrip("/").casefold()


def year_range(record):
    match = re.fullmatch(r"(\d{4})-(\d{4})", record["YEAR"])
    if not match or int(match[1]) > int(match[2]):
        raise ValueError(f"Invalid year range: {record['DIMENSION-ID']}")
    return int(match[1]), int(match[2])


def minimum_year_groups(records):
    """Greedy interval stabbing gives the minimum years for a fixed identity group."""
    remaining = sorted(records, key=lambda r: (year_range(r)[1], r["DIMENSION-ID"]))
    while remaining:
        endpoint = year_range(remaining[0])[1]
        covered = [r for r in remaining if year_range(r)[0] <= endpoint]
        remaining = [r for r in remaining if year_range(r)[0] > endpoint]
        start = max(year_range(r)[0] for r in covered)
        end = min(year_range(r)[1] for r in covered)
        yield (start + end) // 2, covered


def main():
    pipeline = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in pipeline["nodes"]}
    batch = RunBatch.create(ROOT / "reports/ru-image-search/artifacts", "ru-image-search")
    sources = []

    def read_table(node_id, name):
        path = node_output(ROOT, nodes[node_id]) / name
        table = json.loads(batch.input(path).read_text(encoding="utf-8-sig"))
        sources.append({"node": node_id, "file": path.relative_to(ROOT).as_posix(),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "rows": len(table["rows"])})
        return [dict(zip(table["columns"], row)) for row in table["rows"]]

    records = read_table("dimension-library", "尺寸库_RU.json")
    raw = read_table("dimension-crawler", "RU/auto_ru_dimensions_with_match_key.json")
    catalog = read_table("dimension-crawler", "RU/auto_ru_catalog_rank.json")
    urls_by_model = collections.defaultdict(set)
    for row in raw:
        urls_by_model[row["brand"], row["model"]].add(row["model_url"])
    catalog_by_url = collections.defaultdict(list)
    for row_number, row in enumerate(catalog, 1):
        catalog_by_url[url_key(row["link_url"])].append((row_number, row))
    groups = collections.defaultdict(list)
    for row in records:
        generation = row["代际"] or "unknown:" + row["YEAR"]
        groups[row["MAKE"], row["MODEL"], generation].append(row)

    tasks = []
    matched_catalog = set()
    for (make, model, generation), rows in sorted(groups.items()):
        for representative_year, members in minimum_year_groups(rows):
            urls = sorted(urls_by_model[make, model])
            catalog_entries = [entry for url in urls for entry in catalog_by_url[url_key(url)]]
            matched_catalog.update(number for number, _ in catalog_entries)
            query = f"{make} {model} {representative_year} {members[0]['代际']} car exterior".strip()
            identity = [make, model, generation, representative_year]
            task_id = "RU-" + hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode()).hexdigest()[:16]
            requirements = [{key: r[key] for key in ("DIMENSION-ID", "YEAR", "结构", "版本", "CAB", "BED", "L-IN", "W-IN", "H-IN")}
                            for r in members]
            tasks.append({"id": task_id, "priority": 0, "state": "pending_search", "kind": "generation_search",
                          "make": make, "model": model, "generation": members[0]["代际"],
                          "generation_status": "source_label_unverified" if members[0]["代际"] else "unknown_keep_year_range",
                          "representative_year": representative_year, "query": query,
                          "search_url": "https://www.google.com/search?tbm=isch&q=" + quote(query),
                          "source_model_urls": urls, "catalog_rows": sorted({n for n, _ in catalog_entries}),
                          "catalog_rank": min((int(r[" Rank"]) for _, r in catalog_entries), default=999999),
                          "requirements": requirements, "covered_records": len(members),
                          "multi_configuration": len(members) > 1,
                          "image_coverage_verified": False})
    unmatched = collections.defaultdict(list)
    for number, row in enumerate(catalog, 1):
        if number not in matched_catalog:
            unmatched[url_key(row["link_url"])].append((number, row))
    for key, entries in sorted(unmatched.items()):
        row = entries[0][1]
        query = row["Model"] + " generations car exterior"
        tasks.append({"id": "RU-CAT-" + hashlib.sha256(key.encode()).hexdigest()[:16],
                      "priority": 0, "state": "pending_identity_research", "kind": "catalog_only_research",
                      "make": "", "model": row["Model"], "generation": "", "representative_year": None,
                      "generation_status": "catalog_only_unknown", "query": query,
                      "search_url": "https://www.google.com/search?tbm=isch&q=" + quote(query),
                      "source_model_urls": [row["link_url"]], "catalog_rows": [n for n, _ in entries],
                      "catalog_rank": min(int(r[" Rank"]) for _, r in entries),
                      "requirements": [], "covered_records": 0, "multi_configuration": False,
                      "image_coverage_verified": False})
    tasks.sort(key=lambda t: (t["priority"], t["catalog_rank"], t["kind"], t["id"]))
    covered_ids = [r["DIMENSION-ID"] for t in tasks for r in t["requirements"]]
    assert collections.Counter(covered_ids) == collections.Counter(r["DIMENSION-ID"] for r in records)
    assert len({t["id"] for t in tasks}) == len(tasks)
    assert {n for t in tasks for n in t["catalog_rows"]} == set(range(1, len(catalog) + 1))
    for task in tasks:
        for row in task["requirements"]:
            assert year_range(row)[0] <= task["representative_year"] <= year_range(row)[1]
    summary = {"dimension_records": len(records), "catalog_records": len(catalog),
               "unique_dimension_models": len({(r["MAKE"], r["MODEL"]) for r in records}),
               "generation_searches": sum(t["kind"] == "generation_search" for t in tasks),
               "catalog_only_searches": len(unmatched), "total_initial_searches": len(tasks),
               "missing_generation_records": sum(not r["代际"] for r in records),
               "multi_configuration_tasks": sum(t["multi_configuration"] for t in tasks),
               "verified_images": 0}
    queue = {"schema": "vehicle-image-search-queue/v1", "source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "sources": sources, "summary": summary,
        "scheduling": {"order": ["ru_image_search", "classic_car"], "ru_priority": 0, "classic_priority": 100,
                       "within_ru": "catalog_rank then kind then id", "policy": "RU pending work precedes new classic-car work; finish already submitted requests safely."},
        "method": {"group": "MAKE + MODEL + exact generation/facelift/market label; unknown generation uses exact YEAR range",
                   "representative_year": "minimum interval stabbing; midpoint of each group's common year intersection",
                   "configuration": "All body/cab/bed/version requirements retained. A shared search does not confirm one image covers all configurations.",
                   "limits": "Conditional minimum initial queries under these groups, not a guaranteed number of web calls or verified photos. Unknown generations and catalog-only models may require splitting. Existing historical data has not been independently reverified."},
        "tasks": tasks}
    queue_path = batch.output("找图队列.json")
    queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compact = [{"id": t["id"], "车型": (t["make"] + " " + t["model"]).strip(), "代际": t["generation"],
                "代表年": t["representative_year"] or "待核", "记录数": t["covered_records"],
                "配置": " / ".join(sorted({" ".join(filter(None, (r["结构"], r["版本"], r["CAB"], r["BED"]))) for r in t["requirements"]})),
                "状态": t["state"], "搜索词": t["query"], "链接": t["search_url"]} for t in tasks]
    page = HTML.replace("__SUMMARY__", json.dumps(summary, ensure_ascii=False)).replace(
        "__DATA__", json.dumps(compact, ensure_ascii=False).replace("<", "\\u003c"))
    batch.output("俄罗斯车型找图.html").write_text(page, encoding="utf-8")
    batch.finish({"status": "passed", "summary": summary, "validation": "all dimension IDs exactly once; all catalog rows covered; representative years within every member range"})
    print(json.dumps({"summary": summary, "batch": str(batch.directory)}, ensure_ascii=False))


HTML = '''<!doctype html><html lang="zh"><meta charset="utf-8"><title>俄罗斯车型找图列表</title>
<style>body{font:15px system-ui;margin:28px;color:#172b39;background:#f5f7fa}input,button{padding:9px;margin:4px}table{border-collapse:collapse;background:white;width:100%}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left;white-space:nowrap}.scroll{overflow:auto}h1{font-size:24px}</style>
<h1>俄罗斯车型找图列表</h1><p id="summary"></p><p>按车型、代际、改款和市场标记合并初次搜索，代表年取共同年份区间中点。缺少代际时保留原年份范围。各车身、驾驶室和版本仍须逐项找图核对。来源为现有历史资料，代际与图片覆盖尚待核实。</p>
<p>调度顺序为俄罗斯车型找图优先，老车后续。这里记录的是初始搜索任务数，补查和配置分图可能增加实际搜索次数。</p>
<input id="filter" placeholder="筛选车型、代际或配置"><button id="export">导出筛选结果 CSV</button><button id="prev">上一页</button><button id="next">下一页</button><span id="count"></span>
<div class="scroll"><table><thead><tr><th>任务</th><th>车型</th><th>代际</th><th>代表年</th><th>记录数</th><th>配置</th><th>状态</th><th>搜索</th></tr></thead><tbody></tbody></table></div>
<script>const rows=__DATA__,summary=__SUMMARY__;let page=0,selected=rows;document.querySelector('#summary').textContent=`尺寸记录 ${summary.dimension_records} 条，车型目录 ${summary.catalog_records} 条。代际搜索 ${summary.generation_searches} 项，目录补查 ${summary.catalog_only_searches} 项，共 ${summary.total_initial_searches} 项。已验证图片 0 张。`;
function render(){const body=document.querySelector('tbody');body.replaceChildren();for(const r of selected.slice(page*80,(page+1)*80)){const tr=document.createElement('tr');for(const key of ['id','车型','代际','代表年','记录数','配置','状态']){const td=document.createElement('td');td.textContent=r[key];tr.append(td)}const td=document.createElement('td'),a=document.createElement('a');a.href=r['链接'];a.target='_blank';a.rel='noopener';a.textContent='找图';td.append(a);tr.append(td);body.append(tr)}document.querySelector('#count').textContent=`${selected.length} 项 · ${page+1} / ${Math.max(1,Math.ceil(selected.length/80))} 页`;}
document.querySelector('#filter').oninput=e=>{selected=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(e.target.value.toLowerCase()));page=0;render()};document.querySelector('#prev').onclick=()=>{page=Math.max(0,page-1);render()};document.querySelector('#next').onclick=()=>{page=Math.min(Math.max(0,Math.ceil(selected.length/80)-1),page+1);render()};
document.querySelector('#export').onclick=()=>{const keys=Object.keys(rows[0]);const cell=v=>'"'+String(v).replaceAll('"','""')+'"';const csv=[keys,...selected.map(r=>keys.map(k=>r[k]))].map(r=>r.map(cell).join(',')).join('\\r\\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\\ufeff'+csv],{type:'text/csv;charset=utf-8'}));a.download='俄罗斯车型找图.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};render();</script></html>'''

if __name__ == "__main__":
    main()
