"""可解释的已审原型距离。没有标定原型时拒绝猜测标签。"""
from __future__ import annotations

import math
from collections import defaultdict
from urllib.parse import urlsplit

from .evidence import exact_match
from .geometry import FEATURE_NAMES, profile_features

LABELS = {"LOW_FASTBACK", "LOW_NOTCHBACK", "SPORT_LIFTBACK", "STANDARD_SEDAN", "COMPACT_HATCH",
          "TALL_BOX", "WAGON", "SLOPED_CROSSOVER", "BOXY_SUV", "PICKUP", "OTHER", "UNKNOWN"}


def validate_taxonomy(taxonomy: dict) -> None:
    if not taxonomy.get("taxonomy_version"):
        raise ValueError("缺少 taxonomy_version")
    for key in ("profile_conflict_tolerance", "dimension_conflict_relative", "alternate_distance_margin"):
        if not math.isfinite(taxonomy[key]) or taxonomy[key] < 0:
            raise ValueError(f"无效阈值: {key}")
    gate = taxonomy["image_gate"]
    if any(not 0 <= gate[k] <= 1 for k in ("max_wheel_level_delta", "max_wheel_radius_delta")):
        raise ValueError("图像门禁阈值无效")
    for p in taxonomy["prototypes"]:
        if p.get("reviewed") is not True or not all(p.get(k) for k in ("reviewer", "reviewed_at_utc", "calibration_evidence_ids")):
            raise ValueError("原型未人工标定/缺审核来源")
        if p["label"] not in LABELS - {"UNKNOWN"} or not math.isfinite(p["max_distance"]) or p["max_distance"] <= 0:
            raise ValueError("原型标签/距离无效")
        if set(p["features"]) - set(FEATURE_NAMES) or len(p["features"]) < 3:
            raise ValueError("原型至少含三项已定义的几何特征")
        if not {"roof_start_x", "roof_end_x"}.issubset(p["features"]):
            raise ValueError("分类必须使用侧面轮廓几何")
        for k, value in p["features"].items():
            if not math.isfinite(value) or not math.isfinite(p["scales"].get(k, 0)) or p["scales"].get(k, 0) <= 0:
                raise ValueError("原型数值/尺度无效")


def classify(record: dict, evidence: list[dict], taxonomy: dict, automatic_policy: dict | None = None) -> tuple[dict, dict]:
    validate_taxonomy(taxonomy)
    reasons = list(record.get("identity_flags", []))
    candidates, profiles, matched, automatic_profiles = [], [], [], []
    features = {"variant_key": record["variant_key"], "feature_version": "manual-profile-v1",
                "measurement_units": "relative_shape", "top_profile_64": [], "image_quality": {},
                "uncertainty": "没有合格侧面几何", **{k: None for k in FEATURE_NAMES}, "field_provenance": {}}
    conflict = "SOURCE_DIMENSION_CONFLICT" in reasons
    for item in evidence:
        if item["evidence_type"] == "search_attempt":
            reasons.extend(item["validation_flags"])
            continue
        if item["validation_flags"]:
            reasons.extend(item["validation_flags"])
            if "CONFLICT" in item["validation_flags"]:
                conflict = True
            continue
        if item["evidence_type"] in {"automatic_profile", "automatic_description"}:
            # 自动匹配仅允许精确目标 key 的推断，不把未知市场/代际声明为已验证。
            payload = item["data_payload"]
            if item["variant_key"] == record["variant_key"] and payload.get("identity_match", {}).get("acceptable_for_inference") and payload.get("features", {}).get("usable"):
                automatic_profiles.append(item)
            continue
        if not exact_match(item, record):
            reasons.append("EVIDENCE_IDENTITY_MISMATCH")
            conflict = True
            continue
        if "CONFLICT" in item["validation_flags"]:
            conflict = True
        if item["validation_flags"] or item["source_rank"] not in {"A", "B"}:
            reasons.extend(item["validation_flags"] or ["LOW_RANK_EVIDENCE"])
            continue
        matched.append(item)
        if item["evidence_type"] == "side_profile":
            profile = profile_features(item["data_payload"], taxonomy["image_gate"])
            reasons.extend(profile["flags"])
            if profile["usable"]:
                profiles.append((item, profile))
    dimensions = defaultdict(list)
    for item in matched:
        if item["evidence_type"] == "dimensions":
            for k in ("length_mm", "width_mm", "height_mm", "wheelbase_mm", "front_overhang_mm", "rear_overhang_mm"):
                v = item["data_payload"].get(k)
                if isinstance(v, (int, float)) and math.isfinite(v) and v > 0:
                    dimensions[k].append((float(v), item["evidence_id"]))
    resolved = {}
    for k, values in dimensions.items():
        numbers = [v for v, _ in values]
        if record.get(k) is not None:
            numbers.append(record[k])
        if (max(numbers) - min(numbers)) / max(numbers) > taxonomy["dimension_conflict_relative"]:
            conflict = True
            reasons.append("DIMENSION_CONFLICT_" + k.upper())
        resolved[k] = values[0][0]  # 保留第一项；不以均值掩盖冲突。
        features["field_provenance"][k] = [e for _, e in values]
    if profiles:
        item, profile = profiles[0]
        features.update({k: v for k, v in profile.items() if k not in {"usable", "flags"}})
        for k in FEATURE_NAMES[:6]:
            features["field_provenance"][k] = [item["evidence_id"]]
        for _, other in profiles[1:]:
            if max(abs(a - b) for a, b in zip(profile["top_profile_64"], other["top_profile_64"])) > taxonomy["profile_conflict_tolerance"]:
                conflict = True
                reasons.append("PROFILE_CONFLICT")
        for name, numerator in (("height_length_ratio", "height_mm"), ("wb_length_ratio", "wheelbase_mm")):
            length = resolved.get("length_mm") or record.get("length_mm")
            value = resolved.get(numerator) or record.get(numerator)
            if value and length:
                features[name] = round(value / length, 8)
                features["field_provenance"][name] = [*features["field_provenance"].get(numerator, ["source_record"]),
                                                      *features["field_provenance"].get("length_mm", ["source_record"])]
        for p in taxonomy["prototypes"]:
            if any(features.get(k) is None for k in p["features"]):
                continue
            distance = math.sqrt(sum(((features[k] - v) / p["scales"][k]) ** 2 for k, v in p["features"].items()) / len(p["features"]))
            if distance <= p["max_distance"]:
                candidates.append({"label": p["label"], "distance": round(distance, 8),
                                   "prototype_id": p["id"], "calibration_evidence_ids": p["calibration_evidence_ids"]})
    else:
        reasons.append("NO_QUALIFIED_SIDE_PROFILE")
    candidates.sort(key=lambda p: (p["distance"], p["label"]))
    best = candidates[0]["label"] if candidates else "UNKNOWN"
    alternates = sorted({p["label"] for p in candidates if p["label"] != best and
                         p["distance"] <= candidates[0]["distance"] + taxonomy["alternate_distance_margin"]})
    if not taxonomy["prototypes"]:
        reasons.append("TAXONOMY_UNCALIBRATED")
    if not candidates:
        reasons.append("NO_CALIBRATED_MATCH")
    if alternates:
        reasons.append("AMBIGUOUS_PROTOTYPES")
    authoritative = any(i["source_rank"] == "A" and i["evidence_type"] in {"dimensions", "official_document"}
                        and i["data_payload"].get("identity_confirmed") is True for i in matched)
    def independence(item):
        payload = item["data_payload"]
        return (urlsplit(item["source_url"]).hostname or item["publisher"].casefold(),
                payload.get("independent_source_id"), item["sha256"])
    # 独立的域名、声明的原始素材 ID 和内容 hash 均需不同；转载/同图不同 URL 不算交叉验证。
    independent = any(all(x and y and x != y for x, y in zip(independence(a), independence(b)))
                      for a, _ in profiles for b, _ in profiles if a is not b)
    status = "CONFLICT" if conflict else "UNKNOWN" if best == "UNKNOWN" else "PROBABLE"
    if status == "PROBABLE" and authoritative and independent and not alternates and not record.get("identity_flags"):
        status = "VERIFIED"
    if status == "PROBABLE":
        reasons.append("INDEPENDENT_VALIDATION_OR_AUTHORITY_INCOMPLETE")
    method = "calibrated_prototype_distance"
    if best == "UNKNOWN" and automatic_policy and automatic_policy.get("enabled") and automatic_profiles:
        from .automatic_geometry import candidate_from_features
        from .automatic_documents import describe_candidate
        inferred = []
        for item in automatic_profiles:
            geometric = item["data_payload"]["features"]
            candidate = describe_candidate(geometric["geometric_observations"], record, automatic_policy["classification"]) if item["evidence_type"] == "automatic_description" else candidate_from_features(geometric, record, automatic_policy["classification"])
            if candidate["label"] != "UNKNOWN":
                inferred.append((item, geometric, candidate))
        if inferred:
            item, geometric, candidate = inferred[0]
            features.update(geometric)
            features["height_length_ratio"] = record["height_mm"] / record["length_mm"]
            features["field_provenance"] = {k: [item["evidence_id"]] for k in geometric if k in FEATURE_NAMES}
            features["field_provenance"]["height_length_ratio"] = ["source_record:length_mm", "source_record:height_mm"]
            best = candidate["label"]
            alternates = sorted(set(candidate["alternates"] + [c["label"] for _, _, c in inferred[1:] if c["label"] != best]))
            auto_conflict = any(c["label"] != best for _, _, c in inferred[1:])
            status = "CONFLICT" if conflict or auto_conflict else "INFERRED"
            reasons = [r for r in reasons if r not in {"NO_CALIBRATED_MATCH", "NO_QUALIFIED_SIDE_PROFILE"}]
            reasons.extend(["AUTO_GEOMETRY_INFERENCE", "EXPERIMENTAL_RULES_NOT_CALIBRATED", "SOURCE_MARKET_GENERATION_UNVERIFIED"])
            if auto_conflict: reasons.append("AUTO_SOURCE_CLASSIFICATION_CONFLICT")
            candidates = [{"label": c["label"], "rule": c["rule"], "evidence_id": e["evidence_id"]} for e, _, c in inferred]
            method = automatic_policy["rule_version"]
    result = {k: record.get(k, "") for k in ("source_record_id", "variant_key", "make", "model", "model_year",
                                             "generation", "body_type", "trim", "market", "length_mm", "width_mm", "height_mm")}
    result.update({"source_record_ids": record.get("source_record_ids", [record["source_record_id"]]),
                   "cover_shape": best, "primary_shape": best, "alternate_shapes": alternates,
                   "taxonomy_version": taxonomy["taxonomy_version"], "status": status,
                   "review_required": status != "VERIFIED", "fit_tested": False, "fit_status": "NOT_TESTED",
                   "reason_codes": sorted(set(reasons)), "evidence_ids": [e["evidence_id"] for e in evidence],
                   "classification_rationale": {"method": method, "candidates": candidates,
                                                "distance_is_probability": False}, "raw_fields": record["raw_fields"]})
    return result, features
