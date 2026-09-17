from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import shape_project as project


ROOT = Path(__file__).resolve().parents[2]
SHAPE_PROJECT = ROOT / "车形分类核定"
CACHE = SHAPE_PROJECT / "cache" / "model_shape_cache.csv"
QUEUE = SHAPE_PROJECT / "research_queue" / "regional_queue.csv"
BATCH = SHAPE_PROJECT / "artifacts" / "2026-09-16_01_regional-data-cache-inheritance"

REGIONS = ("us", "eu", "ru")
URL_RE = re.compile(r"https?://[^;\s|]+")

AUDIT_FIELDS = [
    "地区", "源文件", "DIMENSION-ID", "MAKE", "MODEL", "版本", "结构", "代际", "YEAR",
    "当前车形", "核定车形", "处理状态", "继承依据", "缓存来源", "定义版本",
]
MAPPING_FIELDS = ["地区", "DIMENSION-ID", "车形", "处理状态", "缓存来源"]
QUEUE_FIELDS = [
    "queue_key", "地区", "MAKE", "MODEL", "记录数", "年份范围", "代际", "结构",
    "当前车形", "source_urls", "状态", "worker", "updated_at",
]


# 本轮只写入轮廓单一、证据足以覆盖整个模型键的规则。复杂多车身模型继续留在队列。
RESEARCHED_RULES = [
    {
        "MAKE": "Porsche", "MODEL": "911", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD0",
        "source_url": "https://files.porsche.com/filestore/download/usa/en-us/modelseries-911-carrera-models/default/ab44b2a7-4f30-11ea-80c8-005056bbdc38/911-Carrera-Models.pdf",
        "note": "定义表 SD0 参考车型直接锚定 911；Porsche 官方资料确认跨代延续低矮、下宽上窄、前风挡陡斜且车顶向后下落的运动轮廓。Coupé、Cabriolet、Targa 的开顶差异不改变罩体基本轮廓。",
    },
    {
        "MAKE": "Mercedes-benz", "MODEL": "190", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-26.xhtml?oid=5475",
        "note": "Mercedes-Benz 官方档案的 W201 图片用于核对。虽为直线化三厢车，但车头、前翼子板与座舱仍有常规收窄，不满足 SD2 所要求的极端宽头、俯视长边近乎平行和前端极少收窄，按严格反例规则归 SD1。",
    },
    {
        "MAKE": "Audi", "MODEL": "A8 d4", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://press.audi.co.uk/assets/documents/original/19790-AudiUK00016077AudiA8andS8Pricingand.pdf",
        "note": "源目录 Audi 官方资料对应 D4。该车是现代圆角大型三厢车，车头与座舱存在正常收窄；没有 SD2 所需的极端宽头及俯视近矩形证据，也不是 SD0 的低矮运动轮廓，归 SD1。",
    },
    {
        "MAKE": "VW", "MODEL": "Golf vii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "H0",
        "source_url": "https://www.volkswagen-newsroom.com/en/golf-7-20122019-20035",
        "note": "Volkswagen 官方 Golf VII 档案确认标准短尾紧凑两厢轮廓，车身低于 H1 高方两厢，后车顶与尾门较早下落；不含另列的 Variant 旅行车模型键，归 H0。",
    },
    {
        "MAKE": "Volvo", "MODEL": "S80 ii", "match_pattern": "", "generation": "",
        "year_start": "", "year_end": "", "shape": "SD1",
        "source_url": "https://www.volvocars.com/us/media/press-releases/488AF72B93EB31A4/",
        "note": "Volvo 官方外观说明明确第二代 S80 采用圆润前部、拱形风挡—车顶—后窗与流线化三厢比例。其轮廓不满足 SD2 的正向极端方正证据，也不属于 SD0 低矮运动型，归 SD1。",
    },
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def latest_region_source(region: str) -> Path:
    batches = sorted(path for path in (ROOT / "data" / region).iterdir() if path.is_dir())
    if not batches:
        raise FileNotFoundError(f"data/{region} 下没有批次目录")
    candidates = sorted(batches[-1].glob("00_*.csv"))
    if len(candidates) != 1:
        raise ValueError(f"{batches[-1]} 应且仅应包含一份 00_*.csv，实际为 {len(candidates)}")
    return candidates[0]


def current_shape_index(region: str, batch_dir: Path) -> dict[str, str]:
    candidates = sorted(batch_dir.glob("01_*.csv"))
    if len(candidates) != 1:
        return {}
    result: dict[str, str] = {}
    suffix = f" {region.upper()}"
    for row in project.read_csv(candidates[0]):
        dimension_id = row.get("DIMENSION-ID", "")
        if dimension_id.endswith(suffix):
            dimension_id = dimension_id[: -len(suffix)]
        result[dimension_id] = row.get("车形", "")
    return result


def normalized_stage_ids(region: str, path: Path) -> list[str]:
    suffix = f" {region.upper()}"
    result = []
    for row in project.read_csv(path):
        dimension_id = row.get("DIMENSION-ID", "")
        if dimension_id.endswith(suffix):
            dimension_id = dimension_id[: -len(suffix)]
        result.append(dimension_id)
    return result


def structural_candidates(row: dict[str, str], cache_index: dict[tuple[str, str], list[dict[str, str]]]) -> list[dict[str, str]]:
    """Retry obsolete display-ID regex rules using their semantic generation/year bounds.

    This fallback is accepted only when every applicable rule resolves to one shape.
    It does not reuse a cache rule for a new generation.
    """

    candidates: list[dict[str, str]] = []
    lo, hi = project.years(row.get("YEAR", ""))
    key = (project.norm(row.get("MAKE", "")), project.norm(row.get("MODEL", "")))
    for item in cache_index.get(key, []):
        if item.get("generation") and project.norm(item["generation"]) != project.norm(row.get("代际", "")):
            continue
        start = int(item["year_start"]) if item.get("year_start") else None
        end = int(item["year_end"]) if item.get("year_end") else None
        if start is not None and hi is not None and hi < start:
            continue
        if end is not None and lo is not None and lo > end:
            continue
        candidates.append(item)
    return candidates


def cache_source(item: dict[str, str]) -> str:
    return item.get("source_url", "") or "车形分类核定/cache/model_shape_cache.csv"


def queue_key(make: str, model: str) -> str:
    identity = f"{project.norm(make)}\x1f{project.norm(model)}"
    return hashlib.sha256(identity.encode()).hexdigest()[:20]


def extract_urls(row: dict[str, str]) -> set[str]:
    return set(URL_RE.findall(" ".join(str(value or "") for value in row.values())))


def ru_source_urls() -> dict[tuple[str, str], set[str]]:
    result: dict[tuple[str, str], set[str]] = defaultdict(set)
    source = ROOT / "data" / "ru" / "0916" / "source" / "auto_ru_dimensions_with_match_key.csv"
    for row in project.read_csv(source):
        key = (project.norm(row.get("brand", "")), project.norm(row.get("model", "")))
        for field in ("model_url", "specifications_url"):
            if row.get(field):
                result[key].add(row[field])
    return result


def upsert_researched_rules(researched_rules: list[dict[str, str]]) -> list[dict[str, str]]:
    cache = project.read_csv(CACHE)
    stamp = now()
    changed: list[dict[str, str]] = []
    for rule in researched_rules:
        identity = tuple(rule[field] for field in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end"))
        existing = next(
            (
                row for row in cache
                if tuple(row.get(field, "") for field in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end")) == identity
            ),
            None,
        )
        new = {**rule, "updated_at": existing.get("updated_at", stamp) if existing else stamp}
        rule_fields = [field for field in project.CACHE_FIELDS if field != "updated_at"]
        if existing is None or any(existing.get(field, "") != new.get(field, "") for field in rule_fields):
            new["updated_at"] = stamp
            cache = [
                row for row in cache
                if tuple(row.get(field, "") for field in ("MAKE", "MODEL", "match_pattern", "generation", "year_start", "year_end")) != identity
            ]
            cache.append(new)
        changed.append(new)
    write_csv(CACHE, project.CACHE_FIELDS, cache)
    return changed


def run(
    batch: Path = BATCH,
    researched_rules: list[dict[str, str]] = RESEARCHED_RULES,
) -> dict[str, object]:
    changed_rules = upsert_researched_rules(researched_rules)
    cache = project.read_csv(CACHE)
    cache_index = project.index_cache(cache)
    researched_pairs = {(project.norm(row["MAKE"]), project.norm(row["MODEL"])) for row in researched_rules}
    ru_urls = ru_source_urls()

    audit: list[dict[str, str]] = []
    mapping: list[dict[str, str]] = []
    unresolved_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    summary: dict[str, dict[str, int]] = {}
    stage_consistency: dict[str, dict[str, object]] = {}

    for region in REGIONS:
        source = latest_region_source(region)
        rows = project.read_csv(source)
        current_shapes = current_shape_index(region, source.parent)
        analysis_path = next(iter(sorted(source.parent.glob("01_*.csv"))), None)
        full_path = next(iter(sorted(source.parent.glob("02_*.csv"))), None)
        library_ids = [row["DIMENSION-ID"] for row in rows]
        analysis_ids = normalized_stage_ids(region, analysis_path) if analysis_path else []
        full_ids = normalized_stage_ids(region, full_path) if full_path else []
        library_set, analysis_set, full_set = set(library_ids), set(analysis_ids), set(full_ids)
        stage_consistency[region.upper()] = {
            "library_rows": len(library_ids), "analysis_rows": len(analysis_ids), "full_rows": len(full_ids),
            "library_only_vs_analysis": len(library_set - analysis_set),
            "analysis_only_vs_library": len(analysis_set - library_set),
            "analysis_only_vs_full": len(analysis_set - full_set),
            "full_only_vs_analysis": len(full_set - analysis_set),
            "library_only_examples": sorted(library_set - analysis_set)[:10],
            "analysis_only_examples": sorted(analysis_set - library_set)[:10],
        }
        counts = defaultdict(int)
        seen_ids: set[str] = set()
        for row in rows:
            dimension_id = row["DIMENSION-ID"]
            if dimension_id in seen_ids:
                raise ValueError(f"{region.upper()} DIMENSION-ID 重复: {dimension_id}")
            seen_ids.add(dimension_id)

            selected = project.select_indexed_cache(row, cache_index)
            basis = ""
            status = "待研究"
            if selected is not None:
                pair = (project.norm(row["MAKE"]), project.norm(row["MODEL"]))
                status = "本轮增量研究" if pair in researched_pairs else "缓存精确继承"
                basis = "MAKE+MODEL 与缓存限定条件完整命中"
            else:
                candidates = structural_candidates(row, cache_index)
                shapes = {item["shape"] for item in candidates}
                if len(shapes) == 1:
                    selected = candidates[0]
                    status = "缓存结构继承"
                    basis = "代际与年份命中；旧 DIMENSION-ID 正则失效，但适用规则仅有一个车形结论"
                elif len(shapes) > 1:
                    status = "缓存冲突待研究"
                    basis = "同等适用的缓存规则出现多个车形结论"

            resolved_shape = selected["shape"] if selected else ""
            source_url = cache_source(selected) if selected else ""
            audit_row = {
                "地区": region.upper(), "源文件": str(source.relative_to(ROOT)).replace("\\", "/"),
                "DIMENSION-ID": dimension_id, "MAKE": row.get("MAKE", ""), "MODEL": row.get("MODEL", ""),
                "版本": row.get("版本", ""), "结构": row.get("结构", ""), "代际": row.get("代际", ""),
                "YEAR": row.get("YEAR", ""), "当前车形": current_shapes.get(dimension_id, ""),
                "核定车形": resolved_shape, "处理状态": status, "继承依据": basis,
                "缓存来源": source_url, "定义版本": "public/参考尺寸计算.csv@2026-09-16",
            }
            audit.append(audit_row)
            counts[status] += 1
            if selected:
                mapping.append({
                    "地区": region.upper(), "DIMENSION-ID": dimension_id, "车形": resolved_shape,
                    "处理状态": status, "缓存来源": source_url,
                })
            else:
                enriched = {**row, "地区": region.upper()}
                enriched["当前车形"] = current_shapes.get(dimension_id, "")
                enriched["source_urls"] = sorted(extract_urls(row))
                unresolved_groups[(project.norm(row["MAKE"]), project.norm(row["MODEL"]))].append(enriched)
        summary[region.upper()] = {"records": len(rows), **dict(counts)}

    old_queue = {row["queue_key"]: row for row in project.read_csv(QUEUE)}
    queue_rows: list[dict[str, str]] = []
    for items in unresolved_groups.values():
        first = items[0]
        key = queue_key(first["MAKE"], first["MODEL"])
        urls: set[str] = set()
        for item in items:
            urls.update(item.get("source_urls", []))
        if any(item["地区"] == "RU" for item in items):
            urls.update(ru_urls.get((project.norm(first["MAKE"]), project.norm(first["MODEL"])), set()))
        prior = old_queue.get(key, {})
        queue_rows.append({
            "queue_key": key, "地区": ";".join(sorted({item["地区"] for item in items})),
            "MAKE": first["MAKE"], "MODEL": first["MODEL"], "记录数": str(len(items)),
            "年份范围": "; ".join(sorted({item.get("YEAR", "") for item in items if item.get("YEAR")})),
            "代际": "; ".join(sorted({item.get("代际", "") for item in items if item.get("代际")})),
            "结构": "; ".join(sorted({item.get("结构", "") for item in items if item.get("结构")})),
            "当前车形": "; ".join(sorted({item.get("当前车形", "") for item in items if item.get("当前车形")})),
            "source_urls": ";".join(sorted(urls)[:8]),
            "状态": prior.get("状态", "pending") if prior.get("状态") != "done" else "pending",
            "worker": prior.get("worker", ""), "updated_at": prior.get("updated_at", now()),
        })

    queue_rows.sort(key=lambda row: (-int(row["记录数"]), project.norm(row["MAKE"]), project.norm(row["MODEL"])))
    audit.sort(key=lambda row: (REGIONS.index(row["地区"].lower()), row["DIMENSION-ID"]))
    mapping.sort(key=lambda row: (REGIONS.index(row["地区"].lower()), row["DIMENSION-ID"]))

    comparison: dict[str, dict[str, object]] = {}
    for region in (item.upper() for item in REGIONS):
        resolved = [row for row in audit if row["地区"] == region and row["核定车形"]]
        differences = [
            row for row in resolved
            if row["当前车形"] and row["当前车形"] != row["核定车形"]
        ]
        transitions = Counter((row["当前车形"], row["核定车形"]) for row in differences)
        comparison[region] = {
            "resolved_rows": len(resolved),
            "missing_current_shape": sum(not row["当前车形"] for row in resolved),
            "different_from_current": len(differences),
            "top_transitions": [
                {"from": before, "to": after, "rows": count}
                for (before, after), count in transitions.most_common(10)
            ],
        }

    write_csv(QUEUE, QUEUE_FIELDS, queue_rows)
    write_csv(batch / "regional_dimension_audit.csv", AUDIT_FIELDS, audit)
    write_csv(batch / "inherited_mapping.csv", MAPPING_FIELDS, mapping)
    write_csv(batch / "cache_changes.csv", project.CACHE_FIELDS, changed_rules)

    allowed = project.ALLOWED_SHAPES
    stages_match = all(
        item["library_only_vs_analysis"] == 0
        and item["analysis_only_vs_library"] == 0
        and item["analysis_only_vs_full"] == 0
        and item["full_only_vs_analysis"] == 0
        for item in stage_consistency.values()
    )
    validation = {
        "status": "PASS" if stages_match else "WARN",
        "data_batches": {region.upper(): str(latest_region_source(region).parent.relative_to(ROOT)).replace("\\", "/") for region in REGIONS},
        "summary": summary,
        "audit_rows": len(audit),
        "resolved_rows": len(mapping),
        "queued_models": len(queue_rows),
        "cache_rules_added_or_updated": len(changed_rules),
        "stage_consistency": stage_consistency,
        "current_mapping_comparison": comparison,
        "queue_models_without_source_url": [
            {"MAKE": row["MAKE"], "MODEL": row["MODEL"], "地区": row["地区"]}
            for row in queue_rows if not row["source_urls"]
        ],
        "checks": {
            "audit_row_count": len(audit) == sum(item["records"] for item in summary.values()),
            "mapping_matches_resolved": len(mapping) == sum(1 for row in audit if row["核定车形"]),
            "allowed_shapes_only": all(row["车形"] in allowed for row in mapping),
            "unresolved_not_published": all(row["核定车形"] for row in audit if row["处理状态"] != "待研究"),
            "queue_has_sources": sum(bool(row["source_urls"]) for row in queue_rows),
            "regional_stage_id_consistency": stages_match,
        },
    }
    (batch / "validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 新 data 结构车形缓存继承与研究队列",
        "",
        "本批次读取 `data/{us,eu,ru}/0916/00_*尺寸库.csv`，使用 `public/参考尺寸计算.csv` 的当前车形定义。",
        "缓存仅在完整命中，或代际与年份命中且所有适用规则得到唯一车形结论时继承；未命中记录不沿用区域脚本的默认车形。",
        "",
        "## 结果",
        "",
    ]
    for region, counts in summary.items():
        resolved = sum(value for key, value in counts.items() if key != "records" and key != "待研究")
        lines.append(f"- {region}: {counts['records']} 条，安全继承/研究完成 {resolved} 条，待研究 {counts.get('待研究', 0)} 条。")
    lines += [
        f"- 合并后的待研究模型键：{len(queue_rows)} 个。",
        f"- 本轮新增或更新缓存规则：{len(changed_rules)} 条。",
        "",
        "## 新 data 结构检查",
        "",
    ]
    for region, item in stage_consistency.items():
        lines.append(
            f"- {region}: 00/01/02 行数 {item['library_rows']}/{item['analysis_rows']}/{item['full_rows']}；"
            f"00 独有 {item['library_only_vs_analysis']}，01 独有 {item['analysis_only_vs_library']}，"
            f"01/02 双向差异 {item['analysis_only_vs_full']}/{item['full_only_vs_analysis']}。"
        )
    lines += [
        "",
        "## 当前车形映射差异",
        "",
    ]
    for region, item in comparison.items():
        transitions = "；".join(
            f"{change['from']}→{change['to']} {change['rows']} 条"
            for change in item["top_transitions"][:5]
        ) or "无"
        lines.append(
            f"- {region}: 已核定 {item['resolved_rows']} 条，其中与当前车形不同 {item['different_from_current']} 条；主要变化：{transitions}。"
        )
    lines += [
        "",
        "## 本轮增量研究",
        "",
    ]
    for rule in researched_rules:
        lines.append(f"- `{rule['MAKE']} {rule['MODEL']}` → `{rule['shape']}`：{rule['note']} 来源：{rule['source_url']}")
    lines += [
        "",
        "## 发布边界",
        "",
        "本批次只生成候选映射和研究队列。由于 EU/RU 仍有未研究模型，不生成或覆盖正式 `record_shape.csv`，也不回写三国 `01/02` 表。",
    ]
    (batch / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return validation


def main() -> None:
    run()


if __name__ == "__main__":
    main()
