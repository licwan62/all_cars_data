"""按三国通用车衣分类标准审核 01.整理尺寸库 的分类，生成 output/车型结构*.csv。

输入：01.整理尺寸库/output/尺寸库_{US,EU,RU}.csv（只改 分类，不改 DIMENSION-ID 与其他字段）。
规则：data/分类标准.json（结构→分类）+ data/分类联网判定.csv（需联网判定结构的车型级结论）。
运行先写新的 artifacts/<批次>/，校验通过后才原子更新 output/。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
UPSTREAM = ROOT / "01.整理尺寸库" / "output"
DATA = PROJECT / "data"
STANDARD_PATH = DATA / "分类标准.json"
DECISIONS_PATH = DATA / "分类联网判定.csv"
REGIONS = ("US", "EU", "RU")
FIELDS = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际", "YEAR", "分类",
          "L-IN", "W-IN", "H-IN", "参考车型", "备注", "迭代状态"]
DECISION_FIELDS = ["区域", "MAKE", "MODEL", "结构", "YEAR", "分类", "依据", "来源URL", "核实日期"]
CHANGE_FIELDS = ["区域", "DIMENSION-ID", "MAKE", "MODEL", "结构", "YEAR", "原分类", "新分类", "规则", "依据", "来源URL"]
QUEUE_FIELDS = ["区域", "MAKE", "MODEL", "结构", "YEAR范围", "行数", "当前分类", "允许分类"]


class ReviewError(ValueError):
    pass


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def load_standard(path: Path = STANDARD_PATH) -> dict:
    standard = json.loads(path.read_text(encoding="utf-8"))
    allowed = set(standard["allowed"])
    for structure, category in standard["fixed"].items():
        if category not in allowed:
            raise ReviewError(f"分类标准 fixed 含非法分类：{structure}={category}")
    for structure, categories in standard["research_required"].items():
        if not set(categories) <= allowed:
            raise ReviewError(f"分类标准 research_required 含非法分类：{structure}={categories}")
    overlap = set(standard["fixed"]) & (set(standard["research_required"]) | set(standard["excluded"]))
    if overlap or set(standard["research_required"]) & set(standard["excluded"]):
        raise ReviewError(f"分类标准中同一结构出现在多个分组：{sorted(overlap)}")
    return standard


def load_decisions(path: Path = DECISIONS_PATH) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    rows = read_csv(path)
    if rows and list(rows[0].keys()) != DECISION_FIELDS:
        raise ReviewError(f"{path.name} 字段必须为 {DECISION_FIELDS}")
    for row in rows:
        if not row["来源URL"].startswith("http") or not row["依据"].strip():
            raise ReviewError(f"联网判定缺少来源URL或依据：{row}")
    return rows


def structure_family(structure: str, standard: dict) -> str:
    return re.sub(standard["door_suffix_pattern"], "", (structure or "").strip()).strip()


def _years(value: str) -> tuple[int, int] | None:
    found = [int(item) for item in re.findall(r"\d{4}", value or "")]
    return (min(found), max(found)) if found else None


def _decision_matches(decision: dict[str, str], region: str, row: dict[str, str], family: str) -> bool:
    if decision["区域"] not in ("*", region):
        return False
    if (decision["MAKE"], decision["MODEL"], decision["结构"]) != (row["MAKE"], row["MODEL"], family):
        return False
    if not decision["YEAR"].strip():
        return True
    wanted, actual = _years(decision["YEAR"]), _years(row["YEAR"])
    return bool(wanted and actual and wanted[0] <= actual[1] and actual[0] <= wanted[1])


def classify(
    region: str, row: dict[str, str], standard: dict, decisions: list[dict[str, str]]
) -> tuple[str, str, dict[str, str] | None]:
    """返回 (分类, 规则说明, 命中的联网判定)。"""
    family = structure_family(row["结构"], standard)
    if family in standard["fixed"]:
        return standard["fixed"][family], f"通用标准：{family}", None
    if family in standard["excluded"]:
        return "", f"排除：{standard['excluded'][family]}", None
    if family in standard["research_required"]:
        hits = [d for d in decisions if _decision_matches(d, region, row, family)]
        categories = {d["分类"] for d in hits}
        if len(categories) > 1:
            raise ReviewError(f"联网判定冲突：{region} {row['DIMENSION-ID']} -> {sorted(categories)}")
        if hits:
            if hits[0]["分类"] not in standard["research_required"][family]:
                raise ReviewError(f"联网判定分类不在 {family} 允许范围：{hits[0]}")
            return hits[0]["分类"], f"联网判定：{family}", hits[0]
        return row["分类"], f"待联网：{family}", None
    raise ReviewError(f"结构未被分类标准覆盖：{region} {row['DIMENSION-ID']} 结构={row['结构']!r}")


def review(region_rows: dict[str, list[dict[str, str]]], standard: dict, decisions: list[dict[str, str]]) -> dict:
    outputs: dict[str, list[dict[str, str]]] = {}
    changes: list[dict[str, str]] = []
    pending: dict[tuple, dict] = {}
    rules = Counter()
    for region, rows in region_rows.items():
        reviewed = []
        for source in rows:
            category, rule, decision = classify(region, source, standard, decisions)
            rules[rule.split("：")[0]] += 1
            row = dict(source)
            row["分类"] = category
            reviewed.append(row)
            if category != source["分类"]:
                changes.append({
                    "区域": region, "DIMENSION-ID": source["DIMENSION-ID"], "MAKE": source["MAKE"],
                    "MODEL": source["MODEL"], "结构": source["结构"], "YEAR": source["YEAR"],
                    "原分类": source["分类"], "新分类": category, "规则": rule,
                    "依据": decision["依据"] if decision else "", "来源URL": decision["来源URL"] if decision else "",
                })
            if rule.startswith("待联网"):
                family = structure_family(source["结构"], standard)
                key = (region, source["MAKE"], source["MODEL"], family)
                item = pending.setdefault(key, {"years": [], "rows": 0, "categories": Counter()})
                item["years"].append(_years(source["YEAR"]))
                item["rows"] += 1
                item["categories"][source["分类"]] += 1
        outputs[region] = reviewed
    queue = []
    for (region, make, model, family), item in sorted(pending.items()):
        years = [y for y in item["years"] if y]
        queue.append({
            "区域": region, "MAKE": make, "MODEL": model, "结构": family,
            "YEAR范围": f"{min(y[0] for y in years)}-{max(y[1] for y in years)}" if years else "",
            "行数": item["rows"], "当前分类": "; ".join(f"{k or '空'}×{v}" for k, v in item["categories"].items()),
            "允许分类": "/".join(standard["research_required"][family]),
        })
    return {"outputs": outputs, "changes": changes, "queue": queue, "rule_counts": dict(rules)}


def validate(result: dict, region_rows: dict[str, list[dict[str, str]]], standard: dict) -> dict:
    allowed = set(standard["allowed"])
    errors = []
    for region, rows in result["outputs"].items():
        source = region_rows[region]
        if [r["DIMENSION-ID"] for r in rows] != [r["DIMENSION-ID"] for r in source]:
            errors.append(f"{region} DIMENSION-ID 顺序或集合变化")
        for before, after in zip(source, rows, strict=True):
            if any(before[f] != after[f] for f in FIELDS if f != "分类"):
                errors.append(f"{region} {after['DIMENSION-ID']} 非分类字段被修改")
                break
        for row in rows:
            family = structure_family(row["结构"], standard)
            if family in standard["excluded"]:
                if row["分类"]:
                    errors.append(f"{row['DIMENSION-ID']} 排除结构不应有分类")
            elif family in standard["fixed"] and row["分类"] != standard["fixed"][family]:
                errors.append(f"{row['DIMENSION-ID']} 未按通用标准分类")
            elif family in standard["research_required"] and row["分类"] not in allowed:
                errors.append(f"{row['DIMENSION-ID']} 分类非法：{row['分类']}")
    by_family: dict[str, set[str]] = {}
    for rows in result["outputs"].values():
        for row in rows:
            family = structure_family(row["结构"], standard)
            if family in standard["fixed"]:
                by_family.setdefault(family, set()).add(row["分类"])
    inconsistent = {k: sorted(v) for k, v in by_family.items() if len(v) > 1}
    if inconsistent:
        errors.append(f"同一结构跨区域分类不一致：{inconsistent}")
    return {"passed": not errors, "errors": errors[:50]}


def next_artifact_dir(artifacts: Path, description: str) -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = [
        int(m.group(1)) for p in artifacts.glob(f"{prefix}*")
        if p.is_dir() and (m := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", p.name))
    ]
    return artifacts / f"{prefix}{max(used, default=0) + 1:02d}_{description}"


def run(upstream: Path = UPSTREAM, output_dir: Path = PROJECT / "output", artifacts: Path = PROJECT / "artifacts") -> dict:
    standard = load_standard()
    decisions = load_decisions()
    region_rows = {}
    for region in REGIONS:
        rows = read_csv(upstream / f"尺寸库_{region}.csv")
        if rows and list(rows[0].keys()) != FIELDS:
            raise ReviewError(f"尺寸库_{region}.csv 字段与约定不一致")
        region_rows[region] = rows
    result = review(region_rows, standard, decisions)
    validation = validate(result, region_rows, standard)
    if not validation["passed"]:
        raise ReviewError(f"校验失败：{validation['errors']}")

    artifact = next_artifact_dir(artifacts, "category-standard")
    artifact.mkdir(parents=True)
    rules_dir = artifact / "rules"
    rules_dir.mkdir()
    for path in (STANDARD_PATH, DECISIONS_PATH, Path(__file__)):
        if path.is_file():
            shutil.copy2(path, rules_dir / path.name)
    upstream_manifest = upstream / "manifest.json"
    if upstream_manifest.is_file():
        shutil.copy2(upstream_manifest, artifact / "upstream_manifest.json")
    combined = [row for region in REGIONS for row in result["outputs"][region]]
    files = {f"车型结构_{region}.csv": result["outputs"][region] for region in REGIONS}
    files["车型结构.csv"] = combined
    for name, rows in files.items():
        write_csv(artifact / "output" / name, FIELDS, rows)
    write_csv(artifact / "changes.csv", CHANGE_FIELDS, result["changes"])
    write_csv(artifact / "待联网.csv", QUEUE_FIELDS, result["queue"])
    change_summary = Counter((c["区域"], structure_family(c["结构"], standard), c["原分类"], c["新分类"]) for c in result["changes"])
    status = {
        "status": "passed",
        "rows": {region: len(result["outputs"][region]) for region in REGIONS},
        "rule_counts": result["rule_counts"],
        "changed_rows": len(result["changes"]),
        "change_summary": [
            {"区域": r, "结构": f, "原分类": o, "新分类": n, "行数": c}
            for (r, f, o, n), c in sorted(change_summary.items(), key=lambda item: -item[1])
        ],
        "pending_research_models": len(result["queue"]),
        "pending_research_rows": sum(item["行数"] for item in result["queue"]),
        "decisions": len(decisions),
    }
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_dir.mkdir(parents=True, exist_ok=True)
    for name in files:
        staged = output_dir / f".{name}.tmp"
        shutil.copy2(artifact / "output" / name, staged)
        os.replace(staged, output_dir / name)
    return {**status, "artifact": str(artifact)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按三国通用车衣分类标准生成 车型结构*.csv")
    parser.parse_args(argv)
    try:
        summary = run()
    except (ReviewError, FileNotFoundError) as error:
        print(f"分类结构审核失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
