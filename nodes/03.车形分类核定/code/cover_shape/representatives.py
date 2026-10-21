"""每个同市场/代际/版本/尺寸分支只研究一个代表年；全部源记录投影 SHAPE。"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import defaultdict

from .classifier import classify
from .family_cache import outcome as family_outcome
from .ingest import identity, normalize, years


def prototype_candidate(geometry: dict, dimensions: dict, policy: dict) -> tuple[str, list[str], list[str]]:
    values = [dimensions.get(k) for k in ("length_mm", "width_mm", "height_mm")]
    if any(v is None or not math.isfinite(v) or v <= 0 for v in values):
        return policy["missing_dimensions_shape"], [], ["MISSING_OR_INVALID_DIMENSIONS", "GEOMETRY_UNRESOLVED"]
    length, _, height = values
    rules = policy["classification"]
    ratio = height / length
    low = height <= rules["low_height_mm"] and ratio <= rules["low_height_length_ratio"]
    reasons = ["PROTOTYPE_GEOMETRY_ASSUMED", "DIMENSIONS_OBSERVED", "NOT_VEHICLE_VERIFIED"]
    if geometry.get("separate_cab") and geometry.get("open_cargo_bed"):
        return "PICKUP", [], reasons
    if geometry.get("single_volume"):
        return "TALL_BOX", [], reasons
    if geometry.get("extended_roof"):
        return "WAGON", ["TALL_BOX"] if ratio >= rules["tall_height_length_ratio"] else [], reasons
    if geometry.get("box_body"):
        label = "TALL_BOX" if geometry.get("short_hood") and length <= rules["compact_box_length_mm"] else "BOXY_SUV"
        return label, ["SLOPED_CROSSOVER"] if geometry.get("rear_geometry_unknown") else [], reasons
    if geometry.get("sloped_rear"):
        if low:
            return "LOW_FASTBACK", [], reasons
        if height >= rules["crossover_height_mm"]:
            return "SLOPED_CROSSOVER", ["COMPACT_HATCH"] if length <= rules["compact_length_mm"] else [], reasons
        if length <= rules["compact_length_mm"] and ratio >= rules["compact_height_length_ratio"]:
            return "COMPACT_HATCH", [], reasons
        return "SPORT_LIFTBACK", [], reasons
    if geometry.get("high_cabin"):
        if length <= rules["compact_box_length_mm"] and ratio >= rules["tall_height_length_ratio"]:
            return "TALL_BOX", ["BOXY_SUV"], reasons
        # SU0 的前部收窄不是尾部斜背证据；这是尺寸约束下的候选，尾部未验证且保留备选。
        sloped_candidate = geometry.get("tapered_upper_body") and ratio < rules["tall_height_length_ratio"]
        label = "SLOPED_CROSSOVER" if sloped_candidate else "BOXY_SUV"
        return label, ["BOXY_SUV" if sloped_candidate else "SLOPED_CROSSOVER"], reasons + ["REAR_GEOMETRY_UNRESOLVED"]
    if geometry.get("regular_cabin") or geometry.get("low_cabin"):
        return ("LOW_NOTCHBACK", ["LOW_FASTBACK"], reasons + ["REAR_GEOMETRY_UNRESOLVED"]) if low else (
                "STANDARD_SEDAN", ["SPORT_LIFTBACK"], reasons + ["REAR_GEOMETRY_UNRESOLVED"])
    return "OTHER", [], reasons + ["NO_GEOMETRIC_PROTOTYPE"]


def representative_groups(source: list[dict], legacy: list[dict], mapping: dict, policy: dict, source_sha: str, evidence: list[dict]):
    prior = {r["DIMENSION-ID"]: r for r in legacy}
    if len(prior) != len(legacy) or set(prior) != {r["DIMENSION-ID"] for r in source}:
        raise ValueError("旧车形与结构表必须精确全覆盖，且 ID 唯一")
    groups, normalized = defaultdict(list), {}
    for row in source:
        rid = row["DIMENSION-ID"]
        span = years(row, mapping)
        raw = {**row, "YEAR": str(span[(len(span)-1)//2])}
        record = normalize([raw], mapping, source_sha)[0]
        record["raw_fields"] = row.copy()
        record.update({"CAB": row.get("CAB", ""), "BED": row.get("BED", ""),
                       "legacy_shape": prior[rid]["车形"], "legacy_status": prior[rid]["处理状态"], "covered_years": span})
        key = tuple(record.get(k, "") for k in policy["group_scope"])
        if not record.get("generation"):
            key += (rid,)
        group_id = "g:" + hashlib.sha256(json.dumps(key, ensure_ascii=False).encode()).hexdigest()[:24]
        groups[group_id].append(record)
        record["group_id"] = group_id
        normalized[rid] = record
    facts = defaultdict(list)
    for item in evidence:
        rid = item["data_payload"].get("inference_chain", {}).get("upstream_branch")
        if rid in normalized:
            target = normalized[rid]
            claim = item.get("variant_claim", {})
            scope = item["data_payload"].get("target_scope", {})
            if scope:
                same_scope = all(scope.get(k, "") == target.get(k, "") for k in ("make", "model", "generation", "body_type", "trim", "market", "group_id"))
                if same_scope and item["model_year_claim"] in target["covered_years"]:
                    facts[rid].append(item)
                continue
            same_identity = all(str(claim.get(k, "")).casefold() == str(target.get(k, "")).casefold()
                                for k in ("make", "model", "body_type", "trim"))
            same_generation = item["data_payload"].get("inference_chain", {}).get("generation") == target.get("generation")
            same_market = item.get("market_claim", "").casefold() == target.get("market", "").casefold()
            if same_identity and same_generation and same_market and item["model_year_claim"] in target["covered_years"]:
                facts[rid].append(item)
    result = []
    for group_id, members in sorted(groups.items()):
        covered = sorted({y for r in members for y in r["covered_years"]})
        midpoint = covered[(len(covered)-1)//2]
        evidence_group = [e for r in members for e in facts[r["source_record_id"]]]
        supported_years = [e["model_year_claim"] for e in evidence_group if isinstance(e["model_year_claim"], int) and e["model_year_claim"] in covered]
        representative_year = min(supported_years, key=lambda y: (abs(y-midpoint), y)) if supported_years else midpoint
        chosen = next(r for r in members if representative_year in r["covered_years"])
        representative = {**chosen, "model_year": representative_year}
        representative["variant_key"] = identity(representative)
        # 明确登记由同一精确分支的冻结文档向代表年的投影；保留源年款，不冒充 exact_match。
        projected = []
        for fact in evidence_group:
            if fact["evidence_type"] not in {"automatic_description", "automatic_profile"}:
                continue
            item = copy.deepcopy(fact)
            original = item["variant_key"]
            item["variant_key"] = representative["variant_key"]
            item["data_payload"]["representative_projection"] = {"original_variant_key": original, "representative_year": representative_year,
                                                                  "group_id": group_id, "source_records": [r["source_record_id"] for r in members]}
            projected.append(item)
        result.append((group_id, representative, members, projected))
    return result


def build(source, legacy, reference, evidence, mapping, policy, taxonomy, automatic, source_sha, groups=None, cache=None):
    reference_by_code = {r["车身号"].strip(): r for r in reference}
    groups = groups if groups is not None else representative_groups(source, legacy, mapping, policy, source_sha, evidence)
    if cache is not None:
        cache.learn_spans([r for _, _, members, _ in groups for r in members])
    outcomes, audit = {}, []
    for gid, representative, members, facts in groups:
        result, _ = classify(representative, facts, taxonomy, automatic)
        code = representative["legacy_shape"]
        if code not in policy["prototype_geometry"] or code not in reference_by_code:
            raise ValueError(f"没有已登记的几何原型：{code}")
        if result["cover_shape"] != "UNKNOWN":
            shape, alternates, status = result["cover_shape"], result["alternate_shapes"], result["status"]
            method = "representative_evidence"
            sources = sorted({e["source_url"] for e in facts})
            reasons = result["reason_codes"]
        else:
            shape, alternates, reasons = prototype_candidate(policy["prototype_geometry"][code], representative, policy)
            status, method, sources = "INFERRED", "prototype_geometry_dimensions", ["prototype:" + code]
        cached = {}
        for record in members:
            row = {"DIMENSION-ID": record["source_record_id"], "COUNTRY": record["market"],
                   "SHAPE": shape, "SHAPE_STATUS": status, "SHAPE_YEAR": str(representative["model_year"]),
                   "SHAPE_METHOD": method, "SHAPE_ALTERNATES": json.dumps(alternates, ensure_ascii=False),
                   "SHAPE_SOURCE": json.dumps(sources, ensure_ascii=False)}
            # 车型族研究结论按记录（代际/年份/模式）覆盖原型推断；同一精确分支的冻结几何证据仍优先。
            if cache is not None and method != "representative_evidence":
                rule, scope = cache.select(record)
                if rule is not None:
                    row.update(family_outcome(rule, scope, record))
                    cached[record["source_record_id"]] = row["SHAPE_METHOD"]
            outcomes[record["source_record_id"]] = row
        audit.append({"group_id": gid, "representative_source_id": representative["source_record_id"],
                      "representative_year": representative["model_year"], "source_record_ids": [r["source_record_id"] for r in members],
                      "source_years": sorted({y for r in members for y in r["covered_years"]}), "SHAPE": shape,
                      "SHAPE_STATUS": status, "SHAPE_METHOD": method, "reason_codes": reasons,
                      "alternate_shapes": alternates,
                      "legacy_shape": code, "legacy_status": representative["legacy_status"],
                      "prototype_description": reference_by_code[code]["描述"], "geometry_assumptions": policy["prototype_geometry"][code],
                      "dimensions_mm": {k: representative.get(k) for k in ("length_mm", "width_mm", "height_mm")},
                      "evidence_ids": [e["evidence_id"] for e in facts], "family_cache": cached})
    return [outcomes[r["DIMENSION-ID"]] for r in source], audit
