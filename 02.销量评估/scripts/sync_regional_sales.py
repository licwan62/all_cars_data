from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "销量评估"
CACHE = PROJECT / "cache" / "regional_model_year_sales.csv"
QUEUE = PROJECT / "research_queue" / "regional_sales_queue.csv"
BATCH = PROJECT / "artifacts" / "2026-09-16_01_regional-scope-audit"
REGIONS = ("US", "EU", "RU")

CACHE_FIELDS = [
    "REGION", "COUNTRY_SCOPE", "MAKE", "MODEL", "YEAR", "SALES_VALUE",
    "SALES_METRIC", "SALES_PERIOD", "SALES_PERIOD_END", "SOURCE_TYPE",
    "SOURCE_URL", "SOURCE_SCOPE", "SOURCE_CONFIDENCE", "STATUS", "NOTES", "UPDATED_AT",
]
QUEUE_FIELDS = [
    "queue_key", "REGION", "COUNTRY_SCOPE", "MAKE", "MODEL", "DIMENSION_ROWS",
    "MODEL_YEAR_TASKS", "YEAR_RANGE", "CURRENT_METRIC", "CURRENT_VALUE_SUM",
    "SOURCE_URLS", "SEARCH_QUERY", "STATUS", "worker", "updated_at",
]
AUDIT_FIELDS = [
    "REGION", "COUNTRY_SCOPE", "SOURCE_FILE", "DIMENSION-ID", "MAKE", "MODEL", "YEAR",
    "RAW_销量合计", "AUDITED_VALUE", "SALES_METRIC", "SALES_PERIOD", "SOURCE_SCOPE",
    "VALUE_STATUS", "SOURCE_URL", "NOTES",
]
SUMMARY_FIELDS = [
    "REGION", "COUNTRY_SCOPE", "DIMENSION_ROWS", "MODEL_KEYS", "RAW_POSITIVE_ROWS",
    "RAW_ZERO_ROWS", "RAW_VALUE_SUM", "ACCEPTED_ROWS", "ACCEPTED_VALUE_SUM",
    "PROXY_ROWS", "PROXY_VALUE_SUM", "PENDING_ROWS", "QUEUE_MODEL_KEYS", "INTERPRETATION",
]

RESEARCHED_FACTS = [
    {
        "REGION": "US", "COUNTRY_SCOPE": "US", "MAKE": "Nissan", "MODEL": "Sentra",
        "YEAR": "2025", "SALES_VALUE": "152578", "SALES_METRIC": "NEW_VEHICLE_SALES",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2025-12-31",
        "SOURCE_TYPE": "OEM_SALES_REPORT",
        "SOURCE_URL": "https://www.nissan-global.com/JP/IR/PERFORMANCE/ASSETS/2025/PDF/Nissan_Sales_202512.pdf",
        "SOURCE_SCOPE": "US", "SOURCE_CONFIDENCE": "HIGH",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": "Nissan 官方美国分车型 CYTD 2025；仅限 US，不向 EU/RU 继承。",
    },
    {
        "REGION": "EU", "COUNTRY_SCOPE": "EU", "MAKE": "VW", "MODEL": "Id.7",
        "YEAR": "2025", "SALES_VALUE": "76600", "SALES_METRIC": "VEHICLE_DELIVERIES",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2025-12-31",
        "SOURCE_TYPE": "OEM_PRESS_RELEASE",
        "SOURCE_URL": "https://www.volkswagen-newsroom.com/en/press-releases/volkswagen-delivers-473-million-vehicles-worldwide-and-further-consolidates-its-market-leadership-in-europe-20063",
        "SOURCE_SCOPE": "EUROPE", "SOURCE_CONFIDENCE": "HIGH",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": "Volkswagen 官方欧洲交付量；口径是 EUROPE deliveries，不改称单一国家注册量，也不向 US/RU 继承。",
    },
    {
        "REGION": "RU", "COUNTRY_SCOPE": "RU", "MAKE": "Lada (ВАЗ)", "MODEL": "Granta",
        "YEAR": "2025", "SALES_VALUE": "148986", "SALES_METRIC": "NEW_VEHICLE_SALES",
        "SALES_PERIOD": "FULL_YEAR", "SALES_PERIOD_END": "2025-12-31",
        "SOURCE_TYPE": "INDUSTRY_REPORT_CITING_OEM",
        "SOURCE_URL": "https://eng.autostat.ru/news/27216/",
        "SOURCE_SCOPE": "RU", "SOURCE_CONFIDENCE": "MEDIUM",
        "STATUS": "RESEARCHED_ALLOCATION_PENDING",
        "NOTES": "AUTOSTAT 引述 AVTOVAZ：乘用 144350 + 商用 4636 = 148986；仅限 RU，待确定尺寸行分配规则。",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def norm(value: str) -> str:
    return " ".join((value or "").strip().casefold().split())


def as_int(value: str) -> int:
    text = str(value or "").strip().replace(",", "")
    return int(float(text)) if text else 0


def queue_key(region: str, make: str, model: str) -> str:
    raw = f"{region}\x1f{norm(make)}\x1f{norm(model)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def year_range(values: list[str]) -> str:
    years: list[int] = []
    for value in values:
        years.extend(int(item) for item in re.findall(r"(?:19|20)\d{2}", value or ""))
    if not years:
        return ""
    return str(min(years)) if min(years) == max(years) else f"{min(years)}-{max(years)}"


def analysis_path(region: str) -> Path:
    paths = sorted((ROOT / "data" / region.lower() / "0916").glob("01_*.csv"))
    if len(paths) != 1:
        raise ValueError(f"{region}: expected exactly one 01_*.csv, got {len(paths)}")
    return paths[0]


def upsert_facts(researched_facts: list[dict[str, str]]) -> list[dict[str, str]]:
    existing = read_csv(CACHE) if CACHE.exists() else []
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    by_key = {
        (row["REGION"], norm(row["MAKE"]), norm(row["MODEL"]), row["YEAR"], row["SALES_METRIC"]): row
        for row in existing
    }
    for fact in researched_facts:
        key = (fact["REGION"], norm(fact["MAKE"]), norm(fact["MODEL"]), fact["YEAR"], fact["SALES_METRIC"])
        old = by_key.get(key)
        new = {**fact, "UPDATED_AT": old.get("UPDATED_AT", stamp) if old else stamp}
        if old and any(old.get(field, "") != new.get(field, "") for field in CACHE_FIELDS if field != "UPDATED_AT"):
            new["UPDATED_AT"] = stamp
        by_key[key] = new
    rows = sorted(by_key.values(), key=lambda row: (row["REGION"], norm(row["MAKE"]), norm(row["MODEL"]), row["YEAR"]))
    write_csv(CACHE, CACHE_FIELDS, rows)
    return rows


def us_atom_totals() -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for row in read_csv(PROJECT / "output" / "atom_sales.csv"):
        base_id = row["atom_record_id"].rsplit("|ATOM_YEAR=", 1)[0]
        totals[base_id] += as_int(row["预估销量"])
    return totals


def existing_queue_rows() -> dict[str, dict[str, str]]:
    if not QUEUE.exists():
        return {}
    return {row["queue_key"]: row for row in read_csv(QUEUE)}


def build_audit() -> tuple[list[dict[str, object]], dict[str, list[dict[str, str]]]]:
    atoms = us_atom_totals()
    audit: list[dict[str, object]] = []
    region_rows: dict[str, list[dict[str, str]]] = {}
    for region in REGIONS:
        path = analysis_path(region)
        rows = read_csv(path)
        region_rows[region] = rows
        suffix = f" {region}"
        for row in rows:
            raw = as_int(row.get("销量合计", ""))
            common = {
                "REGION": region, "COUNTRY_SCOPE": region, "SOURCE_FILE": path.relative_to(ROOT).as_posix(),
                "DIMENSION-ID": row["DIMENSION-ID"], "MAKE": row["MAKE"], "MODEL": row["MODEL"],
                "YEAR": row.get("YEAR", ""), "RAW_销量合计": raw,
            }
            if region == "US":
                base_id = row["DIMENSION-ID"][:-len(suffix)] if row["DIMENSION-ID"].endswith(suffix) else row["DIMENSION-ID"]
                expected = atoms.get(base_id)
                matched = expected is not None and expected == raw
                audit.append({
                    **common, "AUDITED_VALUE": raw if matched else "",
                    "SALES_METRIC": "NEW_VEHICLE_SALES_ESTIMATE", "SALES_PERIOD": "MODEL_YEAR_RANGE",
                    "SOURCE_SCOPE": "US", "VALUE_STATUS": "ACCEPTED_COUNTRY_MATCH" if matched else "PENDING_SOURCE_MISMATCH",
                    "SOURCE_URL": "02.销量评估/output/atom_sales.csv",
                    "NOTES": "已与 US 原子销量逐 DIMENSION-ID 守恒核对。" if matched else "US 尺寸行与原子销量不一致，暂不接受。",
                })
            elif region == "EU":
                audit.append({
                    **common, "AUDITED_VALUE": "", "SALES_METRIC": "UNAVAILABLE", "SALES_PERIOD": "",
                    "SOURCE_SCOPE": "EU", "VALUE_STATUS": "PENDING_NO_COUNTRY_VALUE", "SOURCE_URL": "",
                    "NOTES": "输入 0 是流水线占位，不解释为真实零销量；等待 EU/成员国明确口径数据。",
                })
            else:
                positive = raw > 0
                audit.append({
                    **common, "AUDITED_VALUE": raw if positive else "",
                    "SALES_METRIC": "MARKET_LISTING_COUNT_PROXY" if positive else "UNAVAILABLE",
                    "SALES_PERIOD": "SOURCE_SNAPSHOT" if positive else "", "SOURCE_SCOPE": "RU",
                    "VALUE_STATUS": "PROXY_ONLY_NOT_ANNUAL" if positive else "PENDING_NO_COUNTRY_VALUE",
                    "SOURCE_URL": "data/ru/0916/source/auto_ru_model_sales_with_match_key.csv" if positive else "",
                    "NOTES": "Auto.ru sale_detail 聚合值，仅作 RU 市场在售样本代理，不解释为年度销量。" if positive else "输入 0 不解释为真实零销量。",
                })
    return audit, region_rows


def group_rows(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    result: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        result[(row["MAKE"], row["MODEL"])].append(row)
    return result


def build_queue(
    region_rows: dict[str, list[dict[str, str]]],
    facts: list[dict[str, str]],
) -> list[dict[str, object]]:
    previous_rows = existing_queue_rows()
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    output: list[dict[str, object]] = []

    def append_row(row: dict[str, object]) -> None:
        old = previous_rows.get(str(row["queue_key"]))
        stable_fields = [field for field in QUEUE_FIELDS if field != "updated_at"]
        unchanged = old is not None and all(str(old.get(field, "")) == str(row.get(field, "")) for field in stable_fields)
        row["updated_at"] = old.get("updated_at", stamp) if unchanged and old else stamp
        output.append(row)

    # US 延续既有低置信度模型队列；不把 US 研究结论扩散到其他区域。
    us_groups = group_rows(region_rows["US"])
    us_cache = read_csv(PROJECT / "cache" / "sales_model_year_cache.csv")
    us_values: dict[tuple[str, str], int] = defaultdict(int)
    for row in us_cache:
        us_values[(norm(row["MAKE"]), norm(row["MODEL"]))] += as_int(row.get("MODEL_YEAR_US_SALES", ""))
    for item in read_csv(PROJECT / "research_queue" / "sales_low_confidence_queue.csv"):
        key = queue_key("US", item["MAKE"], item["MODEL"])
        matched_rows = us_groups.get((item["MAKE"], item["MODEL"]), [])
        append_row({
            "queue_key": key, "REGION": "US", "COUNTRY_SCOPE": "US", "MAKE": item["MAKE"], "MODEL": item["MODEL"],
            "DIMENSION_ROWS": len(matched_rows), "MODEL_YEAR_TASKS": item.get("record_count", ""),
            "YEAR_RANGE": item.get("YEARS", ""), "CURRENT_METRIC": "LOW_CONFIDENCE_NEW_VEHICLE_SALES",
            "CURRENT_VALUE_SUM": us_values.get((norm(item["MAKE"]), norm(item["MODEL"])), 0),
            "SOURCE_URLS": item.get("SOURCE_GROUP", ""),
            "SEARCH_QUERY": f'{item["MAKE"]} {item["MODEL"]} US annual sales by model year official',
            "STATUS": "PENDING_US_QUALITY_RESEARCH", "worker": item.get("worker", ""),
        })

    facts_by_model: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for fact in facts:
        facts_by_model[(fact["REGION"], norm(fact["MAKE"]), norm(fact["MODEL"]))].append(fact)

    for region in ("EU", "RU"):
        for (make, model), rows in group_rows(region_rows[region]).items():
            key = queue_key(region, make, model)
            total = sum(as_int(row.get("销量合计", "")) for row in rows)
            has_proxy = region == "RU" and total > 0
            researched = facts_by_model.get((region, norm(make), norm(model)), [])
            researched_value = sum(as_int(row.get("SALES_VALUE", "")) for row in researched)
            researched_metrics = ";".join(sorted({row["SALES_METRIC"] for row in researched}))
            researched_urls = ";".join(sorted({row["SOURCE_URL"] for row in researched if row.get("SOURCE_URL")}))
            append_row({
                "queue_key": key, "REGION": region, "COUNTRY_SCOPE": region, "MAKE": make, "MODEL": model,
                "DIMENSION_ROWS": len(rows), "MODEL_YEAR_TASKS": "", "YEAR_RANGE": year_range([row.get("YEAR", "") for row in rows]),
                "CURRENT_METRIC": researched_metrics or ("MARKET_LISTING_COUNT_PROXY" if has_proxy else "UNAVAILABLE"),
                "CURRENT_VALUE_SUM": researched_value if researched else (total if has_proxy else ""),
                "SOURCE_URLS": researched_urls or ("data/ru/0916/source/auto_ru_model_sales_with_match_key.csv" if has_proxy else ""),
                "SEARCH_QUERY": f"{make} {model} {region} annual sales official registrations",
                "STATUS": (
                    "RESEARCHED_FACT_AVAILABLE_ALLOCATION_PENDING" if researched
                    else "PENDING_RU_ANNUAL_RESEARCH_PROXY_AVAILABLE" if has_proxy
                    else f"PENDING_{region}_SALES_RESEARCH"
                ),
                "worker": "",
            })
    output.sort(key=lambda row: (REGIONS.index(str(row["REGION"])), str(row["STATUS"]), norm(str(row["MAKE"])), norm(str(row["MODEL"]))))
    return output


def build_summary(audit: list[dict[str, object]], queue: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for region in REGIONS:
        rows = [row for row in audit if row["REGION"] == region]
        queue_rows = [row for row in queue if row["REGION"] == region]
        raw_values = [as_int(str(row["RAW_销量合计"])) for row in rows]
        accepted = [row for row in rows if str(row["VALUE_STATUS"]).startswith("ACCEPTED_")]
        proxy = [row for row in rows if row["VALUE_STATUS"] == "PROXY_ONLY_NOT_ANNUAL"]
        pending = [row for row in rows if str(row["VALUE_STATUS"]).startswith("PENDING_")]
        interpretation = {
            "US": "仅 US 年度新车销量估算；已按 DIMENSION-ID 与原子销量守恒核对。",
            "EU": "原表 0 为缺失占位；等待 EU 或明确成员国口径，不作为零销量。",
            "RU": "正值仅为 Auto.ru 在售样本代理；零值为缺失，均不冒充年度销量。",
        }[region]
        result.append({
            "REGION": region, "COUNTRY_SCOPE": region, "DIMENSION_ROWS": len(rows),
            "MODEL_KEYS": len({(row["MAKE"], row["MODEL"]) for row in rows}),
            "RAW_POSITIVE_ROWS": sum(value > 0 for value in raw_values), "RAW_ZERO_ROWS": sum(value == 0 for value in raw_values),
            "RAW_VALUE_SUM": sum(raw_values), "ACCEPTED_ROWS": len(accepted),
            "ACCEPTED_VALUE_SUM": sum(as_int(str(row["AUDITED_VALUE"])) for row in accepted),
            "PROXY_ROWS": len(proxy), "PROXY_VALUE_SUM": sum(as_int(str(row["AUDITED_VALUE"])) for row in proxy),
            "PENDING_ROWS": len(pending), "QUEUE_MODEL_KEYS": len(queue_rows), "INTERPRETATION": interpretation,
        })
    return result


def run(
    batch: Path = BATCH,
    researched_facts: list[dict[str, str]] = RESEARCHED_FACTS,
) -> dict[str, object]:
    facts = upsert_facts(researched_facts)
    audit, region_rows = build_audit()
    queue = build_queue(region_rows, facts)
    summary = build_summary(audit, queue)
    write_csv(QUEUE, QUEUE_FIELDS, queue)
    write_csv(batch / "regional_sales_audit.csv", AUDIT_FIELDS, audit)
    write_csv(batch / "regional_sales_summary.csv", SUMMARY_FIELDS, summary)

    us_mismatches = sum(row["REGION"] == "US" and row["VALUE_STATUS"] != "ACCEPTED_COUNTRY_MATCH" for row in audit)
    queue_unique = len(queue) == len({row["queue_key"] for row in queue})
    fact_scopes_valid = all(row["REGION"] == row["COUNTRY_SCOPE"] and row["SOURCE_SCOPE"] != "GLOBAL" for row in facts)
    region_model_keys = {
        region: {(norm(row["MAKE"]), norm(row["MODEL"])) for row in rows}
        for region, rows in region_rows.items()
    }
    facts_match_region_models = all(
        (norm(row["MAKE"]), norm(row["MODEL"])) in region_model_keys.get(row["REGION"], set())
        for row in facts
    )
    eu_values_blank = all(row["AUDITED_VALUE"] == "" for row in audit if row["REGION"] == "EU")
    ru_not_annual = all(row["SALES_METRIC"] != "NEW_VEHICLE_SALES_ESTIMATE" for row in audit if row["REGION"] == "RU")
    validation = {
        "status": "PASS" if all((us_mismatches == 0, queue_unique, fact_scopes_valid, facts_match_region_models, eu_values_blank, ru_not_annual)) else "FAIL",
        "checks": {
            "us_atom_totals_exact": us_mismatches == 0,
            "regional_queue_keys_unique": queue_unique,
            "research_facts_region_isolated": fact_scopes_valid,
            "research_facts_match_corresponding_region_models": facts_match_region_models,
            "eu_placeholder_zero_not_accepted": eu_values_blank,
            "ru_proxy_not_labeled_annual_sales": ru_not_annual,
        },
        "counts": {row["REGION"]: row for row in summary},
        "researched_facts": len(researched_facts),
        "regional_fact_cache_rows": len(facts),
    }
    batch.mkdir(parents=True, exist_ok=True)
    (batch / "validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# US / EU / RU 销量口径隔离审计", "",
        "本批次不回写 `data/*/0916/01_*` 或 `02_*`。审计先把三种现有口径隔离，再为各区域生成独立研究队列。", "",
        "## 结论", "",
    ]
    for row in summary:
        lines.append(
            f'- {row["REGION"]}: {row["DIMENSION_ROWS"]} 条尺寸记录、{row["MODEL_KEYS"]} 个模型键；'
            f'接受 {row["ACCEPTED_ROWS"]} 条，代理 {row["PROXY_ROWS"]} 条，待研究 {row["PENDING_ROWS"]} 条；'
            f'研究队列 {row["QUEUE_MODEL_KEYS"]} 个模型键。{row["INTERPRETATION"]}'
        )
    lines += ["", "## 本轮新增研究事实", ""]
    for fact in sorted(researched_facts, key=lambda row: (row["REGION"], norm(row["MAKE"]), norm(row["MODEL"]), row["YEAR"])):
        lines.append(
            f'- {fact["REGION"]} {fact["MAKE"]} {fact["MODEL"]} {fact["YEAR"]}：'
            f'{as_int(fact["SALES_VALUE"]):,}，{fact["SALES_METRIC"]} / {fact["SOURCE_SCOPE"]}。'
        )
    lines += [
        "", "这些事实先进入区域缓存，状态为 `RESEARCHED_ALLOCATION_PENDING`；在尺寸行分配规则核定前不回填分析表。", "",
        "## 口径边界", "",
        "- US 只使用 US 销量；EU 只接收 EU/明确成员国数据；RU 只接收 RU 数据。",
        "- EU 原表的 0 视为缺失占位，不作为实际零销量。",
        "- RU `sale_detail` 只作为市场在售样本代理，不与年度新车销量相加或比较。",
    ]
    (batch / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return validation


def main() -> None:
    run()


if __name__ == "__main__":
    main()
