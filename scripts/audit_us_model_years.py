"""Read-only local US model-year audit with explicit combined-model membership."""
import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from model_members import ModelCoverage, load_members, model_key as key, year_set as years


def ranges(values):
    groups = []
    for year in sorted(set(values)):
        if groups and groups[-1][-1] + 1 == year:
            groups[-1].append(year)
        else:
            groups.append([year])
    return ";".join(str(g[0]) if len(g) == 1 else f"{g[0]}-{g[-1]}" for g in groups)


def read(path):
    if path.suffix == '.json':
        from json_interface import load_table
        table = load_table(path)
        return [dict(zip(table['columns'], row)) for row in table['rows']]
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def audit(root, destination, previous=None):
    if previous:
        previous = previous.resolve()
    node = root / "nodes/01.整理尺寸库"
    paths = {"dimensions": root / "json/dimension-library/尺寸库_US.json", "year_reference": root / "nodes/M0.车型年覆盖/data/data_source/trimslate-vehicles.csv",
             "market_reference": root / "nodes/M0.车型年覆盖/data/data_source/vehicles.csv", "config": node / "data/build_config.json",
             "members": node / "data/us/model_members.json"}
    resolution_path = node / "data/us/year_gap_resolutions.json"
    resolutions = {}
    if resolution_path.exists():
        paths["year_resolutions"] = resolution_path
        data = json.loads(resolution_path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            raise ValueError("不支持的年份处理规则版本")
        for item in data["resolutions"]:
            cell = key(item["make"]), key(item["model"]), int(item["year"])
            if cell in resolutions:
                raise ValueError("重复的年份处理规则")
            if item["status"] not in {"verified_add", "excluded_reference_year", "pending"}:
                raise ValueError("无效的年份处理状态")
            if item["status"] != "pending" and not item.get("sources"):
                raise ValueError("已处理年份缺少来源")
            for source in item.get("sources", []):
                if source.get("file"):
                    path = (node / source["file"]).resolve()
                    try:
                        path.relative_to((node / "data").resolve())
                    except ValueError as exc:
                        raise ValueError("证据文件必须位于节点data目录") from exc
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    if digest != source.get("sha256"):
                        raise ValueError("证据文件SHA不匹配")
                    paths[f"evidence_{digest}"] = path
            resolutions[cell] = item
    as_of = json.loads(paths["config"].read_text(encoding="utf-8"))["as_of_year"]
    dims, reference, market = (read(paths[name]) for name in ("dimensions", "year_reference", "market_reference"))
    matcher = ModelCoverage(dims, load_members(paths["members"]))
    invalid = []
    for line, row in enumerate(dims, 2):
        try:
            valid = all(math.isfinite(float(row[c])) and float(row[c]) > 0 for c in ("L-IN", "W-IN", "H-IN"))
        except ValueError:
            valid = False
        if not valid:
            invalid.append({"line": line, "id": row["DIMENSION-ID"]})
    pairs, source_lines = defaultdict(set), defaultdict(list)
    for line, row in enumerate(reference, 2):
        item = row["make"], row["model"], int(row["year"])
        pairs[item[:2]].add(item[2])
        source_lines[item].append(line)
    detail, summary = [], []
    for (make, model), expected in sorted(pairs.items()):
        matched = matcher.classify(make, model)
        missing, states = set(), Counter()
        for year in sorted(expected):
            match = matcher.classify(make, model, year)
            state = match["state"]
            resolution = resolutions.get((key(make), key(model), year))
            # A staged research result must never override actual independent or
            # combined coverage, nor silently become a published dimension row.
            if resolution and state == "确认年份缺口（本地参考差集）":
                state = {"verified_add": "尺寸候选待发布", "excluded_reference_year": "参考年份排除",
                         "pending": "候选待核"}[resolution["status"]]
            states[state] += 1
            if state not in {"独立记录覆盖", "参考年份排除"}:
                missing.add(year)
            detail.append({"MAKE": make, "SOURCE_MODEL": model, "YEAR": year, "结果": state,
                "项目范围": "评估年内" if year <= as_of else "超出评估年", "库内车型或候选": match["candidates"],
                "组合来源ID": match["group_ids"], "来源行号": "|".join(map(str, source_lines[(make, model, year)]))})
        summary.append({"MAKE": make, "SOURCE_MODEL": model, "匹配类型": "|".join(sorted(states)),
            "库内车型或候选": matched["candidates"], "参考年份": ranges(expected), "独立库内年份": ranges(matched["years"]),
            "评估年内未独立覆盖或待核年份": ranges(y for y in missing if y <= as_of),
            "评估年内数量": sum(y <= as_of for y in missing), "超出评估年年份": ranges(y for y in missing if y > as_of)})
    market_detail = []
    for row in market:
        if "us" not in row["countries"].split("|"):
            continue
        match = matcher.classify(row["make_name"], row["model_name"])
        market_detail.append({"MAKE": row["make_name"], "MODEL": row["model_name"], "结果": match["state"],
            "库内车型或候选": match["candidates"], "原库别名": row["aliases"], "车身": row["body_types"]})
    inventory = []
    for row in dims:
        if "/" not in row["MODEL"]:
            continue
        rule = matcher.groups.get((key(row["MAKE"]), key(row["MODEL"])))
        inventory.append({"DIMENSION-ID": row["DIMENSION-ID"], "MAKE": row["MAKE"], "MODEL": row["MODEL"],
            "YEAR": row["YEAR"], "登记状态": rule["status"] if rule else "未登记待核",
            "成员": "|".join(m["model"] for m in rule["members"]) if rule else ""})
    corrections = []
    if previous:
        previous_map = {(r["MAKE"], r["SOURCE_MODEL"], int(r["YEAR"])): r for r in read(previous / "车型年份核对.csv")}
        for row in detail:
            prior = previous_map.get((row["MAKE"], row["SOURCE_MODEL"], row["YEAR"]))
            if prior and prior["结果"] != row["结果"]:
                reason = {"组合记录覆盖、成员年份待核": "显式组合成员识别；不推定成员独立年份",
                          "尺寸候选待发布": "已登记尺寸候选，正式库尚未承接",
                          "候选待核": "已登记待核证据，尚无可发布结论",
                          "参考年份排除": "有来源的参考车型年排除结论"}.get(row["结果"], "状态口径统一或组合边界核对")
                corrections.append({"MAKE": row["MAKE"], "MODEL": row["SOURCE_MODEL"], "YEAR": row["YEAR"],
                    "原结果": prior["结果"], "新结果": row["结果"], "原因": reason})
        paths["previous_detail"] = previous / "车型年份核对.csv"
    gaps = [r for r in detail if r["YEAR"] <= as_of and r["结果"] in {
        "确认年份缺口（本地参考差集）", "尺寸候选待发布", "候选待核"}]
    report = {"schema_version": 2, "as_of_year": as_of, "dimension_rows": len(dims),
        "dimension_make_model_pairs": len({(key(r['MAKE']), key(r['MODEL'])) for r in dims}),
        "invalid_dimension_rows": invalid, "reference_trim_rows": len(reference), "reference_make_model_pairs": len(pairs),
        "reference_model_year_pairs": len(detail), "combined_rows": len(inventory),
        "combined_labels": len({(r['MAKE'], r['MODEL']) for r in inventory}),
        "in_scope_counts": dict(Counter(r["结果"] for r in detail if r["YEAR"] <= as_of)),
        "recent_2020_to_as_of_counts": dict(Counter(r["结果"] for r in detail if 2020 <= r["YEAR"] <= as_of)),
        "future_counts": dict(Counter(r["结果"] for r in detail if r["YEAR"] > as_of)),
        "gap_model_count": len({(r['MAKE'], r['SOURCE_MODEL']) for r in gaps}),
        "previous_gap_reclassified_as_group": sum(r["原结果"] == "同名车型年份缺口" and r["新结果"] == "组合记录覆盖、成员年份待核" and r["YEAR"] <= as_of for r in corrections),
        "exact_name_year_gaps_by_make": dict(Counter(r['MAKE'] for r in gaps).most_common()),
        "us_market_model_counts": dict(Counter(r["结果"] for r in market_detail)),
        "sources": {name: {"file": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for name, path in paths.items()},
        "limits": ["确认年份缺口仅指本地参考差集，不代表已核实美国销售年份。",
            "尺寸候选待发布仅指研究登记，不代表正式尺寸库已覆盖或下游已承接。",
            "参考年份排除是对候选年份的有来源处置，不删除历史参考数据。",
            "组合记录仅表示组内覆盖可能，成员车型年与尺寸仍待核，不作为独立确认。",
            "trimslate没有市场字段，原来源未独立核实；不据缺行推断未销售。",
            "不按斜杠自动拆词；仅按显式规则认成员，不自动去除AWD/Hybrid等版本词。",
            "独立覆盖指至少一条尺寸记录覆盖该年，不保证车身、配置、动力版本齐全。",
            "超过评估年的年份单列；vehicles只取countries包含us，没有年份。"]}
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "车型年份核对.csv", list(detail[0]), detail)
    write(destination / "确认年份缺口.csv", list(detail[0]), gaps)
    write(destination / "车型汇总.csv", list(summary[0]), summary)
    write(destination / "美国市场车型核对.csv", list(market_detail[0]), market_detail)
    write(destination / "组合车型盘点.csv", ["DIMENSION-ID", "MAKE", "MODEL", "YEAR", "登记状态", "成员"], inventory)
    write(destination / "前次结果纠正.csv", ["MAKE", "MODEL", "YEAR", "原结果", "新结果", "原因"], corrections)
    resolution_rows = [{"MAKE": r["make"], "MODEL": r["model"], "YEAR": r["year"],
                        "登记状态": r["status"], "依据": r.get("reason", ""),
                        "来源URL": "|".join(s["url"] for s in r.get("sources", [])),
                        "证据SHA256": "|".join(s["sha256"] for s in r.get("sources", []) if s.get("sha256")),
                        "证据文件": "|".join(s["file"] for s in r.get("sources", []) if s.get("file")),
                        "来源页码": "|".join(json.dumps(s["pdf_pages"], ensure_ascii=False, sort_keys=True)
                                               for s in r.get("sources", []) if s.get("pdf_pages"))}
                       for r in resolutions.values()]
    write(destination / "候选处置.csv", ["MAKE", "MODEL", "YEAR", "登记状态", "依据", "来源URL",
                                       "证据SHA256", "证据文件", "来源页码"], resolution_rows)
    (destination / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--previous-report", type=Path)
    args = parser.parse_args()
    audit(ROOT, args.report_dir, args.previous_report)
