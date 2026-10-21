"""车型族研究缓存：同市场/车型/结构抽样少数年份研究，结论按代际/年份/模式规则覆盖整族。

参照旧车身号缓存 cache/model_shape_cache.csv：研究单元是车型族而非每个尺寸/年份分支；
结构（BODY_TYPE）不同的族分开研究，只用于身份分组，不直接决定 SHAPE。
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

CACHE_FIELDS = ["market", "make", "model", "body_type", "generation", "year_start", "year_end", "match_pattern",
                "shape", "alternates", "sample_years", "source_url", "note", "worker", "updated_at"]
RULE_IDENTITY = ("market", "make", "model", "body_type", "generation", "year_start", "year_end", "match_pattern")


def norm(value) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def family_key(record: dict) -> tuple[str, str, str, str]:
    return tuple(norm(record.get(k)) for k in ("market", "make", "model", "body_type"))


def family_id(record: dict) -> str:
    return "f:" + hashlib.sha256(json.dumps(family_key(record), ensure_ascii=False).encode()).hexdigest()[:20]


def int_years(text) -> list[int]:
    return [int(x) for x in re.findall(r"\d{4}", str(text or ""))]


def read_cache(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [{k: (r.get(k) or "").strip() for k in CACHE_FIELDS} for r in csv.DictReader(handle)]
    validate_rules(rows)
    return rows


def write_cache(path: Path, rows: list[dict]) -> None:
    validate_rules(rows)
    ordered = sorted(rows, key=lambda r: (*[norm(r[k]) for k in ("market", "make", "model", "body_type")], -specificity(r),
                                          r["generation"], r["year_start"], r["match_pattern"]))
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CACHE_FIELDS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(ordered)
    temp.replace(path)


def validate_rules(rows: list[dict], labels: set[str] | None = None) -> None:
    from cover_shape_contract import SHAPE_LABELS
    labels = labels or (SHAPE_LABELS - {"UNKNOWN"})
    seen = set()
    for row in rows:
        name = " ".join(row.get(k, "") for k in ("market", "make", "model", "body_type"))
        if not all(row.get(k) for k in ("market", "make", "model", "body_type")):
            raise ValueError(f"缓存规则必须指定 market/make/model/body_type：{name}")
        if row.get("shape") not in labels:
            raise ValueError(f"非法 SHAPE：{name} -> {row.get('shape')}")
        alternates = [x for x in row.get("alternates", "").split(";") if x]
        if any(x not in labels or x == row["shape"] for x in alternates):
            raise ValueError(f"非法备选：{name} -> {row.get('alternates')}")
        if not row.get("source_url") or not row.get("note"):
            raise ValueError(f"缺少 source_url 或 note：{name}")
        samples = int_years(row.get("sample_years"))
        if not samples:
            raise ValueError(f"缺少实际研究的 sample_years：{name}")
        for key in ("year_start", "year_end"):
            if row.get(key) and not re.fullmatch(r"\d{4}", row[key]):
                raise ValueError(f"{key} 必须是四位年份：{name}")
        if row.get("match_pattern"):
            re.compile(row["match_pattern"])
        identity = tuple(norm(row.get(k)) if k != "match_pattern" else row.get(k, "") for k in RULE_IDENTITY)
        if identity in seen:
            raise ValueError(f"重复缓存规则：{name}")
        seen.add(identity)


def specificity(rule: dict) -> int:
    return 4 * bool(rule.get("match_pattern")) + 2 * bool(rule.get("generation")) + bool(rule.get("year_start") or rule.get("year_end"))


def haystack(record: dict) -> str:
    raw = record.get("raw_fields", {})
    return " | ".join([record.get("source_record_id", ""), f"MAKE={record.get('make', '')}", f"MODEL={record.get('model', '')}",
                       f"VERSION={record.get('trim', '')}", f"STRUCTURE={record.get('body_type', '')}",
                       f"YEAR={raw.get('YEAR', '')}", f"CAB={record.get('CAB', '')}", f"BED={record.get('BED', '')}",
                       f"GEN={record.get('generation', '')}"])


def year_overlap(rule: dict, covered: list[int]) -> bool:
    start = int(rule["year_start"]) if rule.get("year_start") else None
    end = int(rule["year_end"]) if rule.get("year_end") else None
    return (start is None or max(covered) >= start) and (end is None or min(covered) <= end)


def matches(rule: dict, record: dict, cross_market: bool = False) -> bool:
    if family_key(rule)[1:] != family_key(record)[1:]:
        return False
    if not cross_market and norm(rule["market"]) != norm(record.get("market")):
        return False
    if not cross_market and rule.get("generation") and norm(rule["generation"]) != norm(record.get("generation")):
        return False
    if not year_overlap(rule, record["covered_years"]):
        return False
    pattern = rule.get("match_pattern", "")
    return not pattern or re.search(pattern, haystack(record), re.IGNORECASE) is not None


class FamilyCache:
    """按车型族索引规则；同市场优先，可选地按年份重叠复用其他市场同车型/结构的结论。"""

    def __init__(self, rules: list[dict], policy: dict | None = None):
        policy = policy or {}
        self.rules = rules
        self.cross_markets = [m.upper() for m in policy.get("cross_market_sources", [])]
        self.by_model = defaultdict(list)
        for rule in rules:
            self.by_model[family_key(rule)[1:]].append(rule)
        self.spans: dict[int, list[int]] = {}

    def learn_spans(self, records: list[dict]) -> None:
        """代际规则跨市场时没有可比代际号，按其在原市场实际覆盖的年份推出有效区间。"""
        for record in records:
            for rule in self.by_model.get(family_key(record)[1:], []):
                if matches(rule, record):
                    span = self.spans.setdefault(id(rule), [9999, 0])
                    span[0], span[1] = min(span[0], min(record["covered_years"])), max(span[1], max(record["covered_years"]))

    def select(self, record: dict) -> tuple[dict | None, str]:
        candidates = self.by_model.get(family_key(record)[1:], [])
        same = [r for r in candidates if matches(r, record)]
        if same:
            same.sort(key=specificity, reverse=True)
            top = specificity(same[0])
            shapes = {r["shape"] for r in same if specificity(r) == top}
            if len(shapes) != 1:
                raise ValueError(f"缓存规则冲突：{record['source_record_id']} -> {sorted(shapes)}")
            return same[0], "same_market"
        market = norm(record.get("market")).upper()
        best, best_overlap, tie = None, 0, False
        for rule in candidates:
            source = norm(rule["market"]).upper()
            if source == market or source not in self.cross_markets or rule.get("match_pattern"):
                continue
            span = self.spans.get(id(rule))
            lo = int(rule["year_start"]) if rule.get("year_start") else (span[0] if span else None)
            hi = int(rule["year_end"]) if rule.get("year_end") else (span[1] if span else None)
            if lo is None or hi is None:
                continue
            overlap = len([y for y in record["covered_years"] if lo <= y <= hi])
            if overlap > best_overlap:
                best, best_overlap, tie = rule, overlap, False
            elif overlap and overlap == best_overlap and rule["shape"] != best["shape"]:
                tie = True
        if best is None or tie:
            return None, ""
        return best, "cross_market"


def outcome(rule: dict, scope: str, record: dict) -> dict:
    samples = int_years(rule["sample_years"])
    covered = record["covered_years"]
    sampled = scope == "same_market" and any(y in covered for y in samples)
    year = min(samples, key=lambda y: (0 if y in covered else min(abs(y - c) for c in covered), y))
    method = "family_cache_cross_market" if scope != "same_market" else "family_cache_sampled" if sampled else "family_cache_inherited"
    return {"SHAPE": rule["shape"], "SHAPE_STATUS": "PROBABLE" if sampled else "INFERRED", "SHAPE_YEAR": str(year),
            "SHAPE_METHOD": method, "SHAPE_ALTERNATES": json.dumps([x for x in rule["alternates"].split(";") if x], ensure_ascii=False),
            "SHAPE_SOURCE": json.dumps(sorted({u.strip() for u in rule["source_url"].split(";") if u.strip()}), ensure_ascii=False)}


def sample_years(years: list[int], policy: dict) -> list[int]:
    """普通车型只研究少数年份：短代际取中位年；长代际按分位均匀取少数年份（前期/后期）以覆盖改款。"""
    years = sorted(set(years))
    if not years:
        return []
    count = 1 if years[-1] - years[0] + 1 < policy.get("long_span_years", 9) else policy.get("max_samples_per_span", 2)
    return sorted({years[min(len(years) - 1, int((i + 0.5) * len(years) / count))] if count > 1 else years[(len(years) - 1) // 2]
                   for i in range(count)})


def natural(text: str) -> list:
    """gen2 排在 gen10 之前。"""
    return [(0, int(part), "") if part.isascii() and part.isdigit() else (1, 0, part)
            for part in re.split(r"([0-9]+)", str(text or ""))]
