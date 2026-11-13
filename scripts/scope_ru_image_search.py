"""Restrict the RU search handoff to the user's external vehicle CSV."""
import argparse
import collections
import copy
import csv
import hashlib
import json
import sys
from pathlib import Path

from build_ru_image_search import HTML, ROOT
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("queue", type=Path)
    args = parser.parse_args()
    batch = RunBatch.create(ROOT / "reports/ru-image-search/artifacts", "ru-csv-priority")
    source = batch.input(args.source.resolve(), name="俄罗斯原始列表.csv")
    full_path = args.queue.resolve()
    batch.inputs.append({"file": full_path.relative_to(ROOT).as_posix(),
                         "artifact_file": full_path.relative_to(ROOT).as_posix(),
                         "sha256": hashlib.sha256(full_path.read_bytes()).hexdigest(),
                         "basis": "immutable parent report batch"})
    rows = list(csv.DictReader(source.open(encoding="utf-8-sig", newline="")))
    full = json.loads(full_path.read_text(encoding="utf-8"))
    index = collections.defaultdict(list)
    for number, row in enumerate(rows, 1):
        for model in row["车型"].split("/"):
            index[row["汽车品牌"].strip().casefold(), model.strip().casefold()].append((number, row))
    tasks = []
    matched_rows = set()
    for original in full["tasks"]:
        entries = index[original["make"].casefold(), original["model"].casefold()]
        requirements = []
        source_rows = set()
        for requirement in original["requirements"]:
            matches = [number for number, row in entries
                       if not row["车身"].strip() or requirement["结构"].casefold() in
                       {body.strip().casefold() for body in row["车身"].split("/")}]
            if matches:
                requirement = dict(requirement, scope_rows=matches)
                requirements.append(requirement)
                source_rows.update(matches)
        if not requirements:
            continue
        task = copy.deepcopy(original)
        task.update(requirements=requirements, covered_records=len(requirements),
                    scope_rows=sorted(source_rows), priority=0,
                    multi_configuration=len(requirements) > 1)
        tasks.append(task)
        matched_rows.update(source_rows)
    unresolved = collections.defaultdict(list)
    for number, row in enumerate(rows, 1):
        if number not in matched_rows:
            unresolved[row["汽车品牌"], row["车型"], row["车身"]].append(number)
    for (make, model, body), source_rows in unresolved.items():
        query = f"{make} {model} {body} generations car exterior"
        from urllib.parse import quote
        tasks.append({"id": "RU-SCOPE-" + hashlib.sha256(query.encode()).hexdigest()[:16],
                      "make": make, "model": model, "generation": "", "representative_year": None,
                      "query": query, "search_url": "https://www.google.com/search?tbm=isch&q=" + quote(query),
                      "priority": 0, "state": "pending_identity_research", "kind": "scope_unmatched_research",
                      "scope_rows": source_rows, "requirements": [], "covered_records": 0,
                      "multi_configuration": False, "image_coverage_verified": False,
                      "requested_body": body, "catalog_rank": 999999})
    tasks.sort(key=lambda t: (min(int(rows[n-1]["链接"]) for n in t["scope_rows"]), t["id"]))
    assert {n for t in tasks for n in t["scope_rows"]} == set(range(1, len(rows)+1))
    assert len({t["id"] for t in tasks}) == len(tasks)
    summary = {"csv_rows": len(rows), "csv_models": len({(r["汽车品牌"], r["车型"]) for r in rows}),
               "unique_csv_rows": len({tuple(r.values()) for r in rows}),
               "dimension_records": sum(t["covered_records"] for t in tasks),
               "catalog_records": len(rows), "generation_searches": len(tasks)-len(unresolved),
               "catalog_only_searches": len(unresolved), "total_initial_searches": len(tasks),
               "unmatched_csv_rows": len(rows)-len(matched_rows), "verified_images": 0}
    result = {"schema": "vehicle-image-search-queue/v1", "summary": summary,
              "scope_source": {"original_path": str(args.source.resolve()),
                               "snapshot": batch.inputs[0]["artifact_file"],
                               "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                               "rows": rows},
              "parent_queue": {"path": args.queue.as_posix(),
                               "sha256": hashlib.sha256(full_path.read_bytes()).hexdigest()},
              "scheduling": {"order": ["ru_csv_scope", "ru_outside_scope", "classic_car"],
                             "priorities": [0, 50, 100], "within_scope": "CSV 链接 number then task ID"},
              "method": "CSV has no years or generations. Retain every known generation matching the requested model and body. Split slash model names explicitly (Audi A3/S3 etc), and slash body alternatives. Blank body accepts all bodies. Exact duplicate CSV rows share tasks with row mapping retained. Unmatched rows receive identity-research tasks. Counts are initial search tasks, not verified minimum photos or guaranteed web calls.",
              "tasks": tasks}
    batch.output("俄罗斯优先找图队列.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf8", newline="\n")
    compact = [{"id": t["id"], "车型": t["make"]+" "+t["model"], "代际": t["generation"],
                "代表年": t["representative_year"] or "待核", "记录数": t["covered_records"],
                "配置": " / ".join(sorted({" ".join(filter(None,(r["结构"],r["版本"],r["CAB"]))) for r in t["requirements"]})) or t.get("requested_body", ""),
                "状态": t["state"], "搜索词": t["query"], "链接": t["search_url"]} for t in tasks]
    page = HTML.replace("俄罗斯车型找图列表", "俄罗斯 CSV 优先找图列表")
    page = page.replace("<p id=\"summary\"></p>", f'<p>用户列表 {len(rows)} 行、{summary["csv_models"]} 个车型名称组合。原表没有年份及代际，当前保留指定车型与车身的全部已知代际。</p><p id="summary"></p>')
    page = page.replace("老车后续", "俄罗斯范围外列表其次，老车后续")
    page = page.replace("__SUMMARY__", json.dumps(summary, ensure_ascii=False)).replace("__DATA__", json.dumps(compact, ensure_ascii=False).replace("<", "\\u003c"))
    batch.output("俄罗斯优先找图.html").write_text(page, encoding="utf8", newline="\n")
    batch.finish({"status": "passed", "summary": summary, "validation": "every CSV row maps to one or more tasks; every retained dimension requirement matches a source model/body"})
    print(json.dumps({"summary": summary, "batch": str(batch.directory)},ensure_ascii=False))


if __name__ == "__main__":
    main()
