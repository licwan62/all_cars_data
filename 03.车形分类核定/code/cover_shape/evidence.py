"""证据校验与精确身份绑定。声明本身不会成为实际打样结论。"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from urllib.parse import urlsplit

REQUIRED = {"evidence_id", "variant_key", "evidence_type", "source_url", "publisher", "retrieved_at_utc",
            "model_year_claim", "variant_claim", "market_claim", "source_rank", "sha256",
            "extraction_method", "license_note", "data_payload", "validation_flags"}
IDENTITY_FIELDS = ("make", "model", "generation", "body_type", "trim")


def validate(evidence: dict) -> None:
    if REQUIRED - evidence.keys():
        raise ValueError(f"证据缺字段: {sorted(REQUIRED - evidence.keys())}")
    if not evidence["evidence_id"] or not evidence["variant_key"]:
        raise ValueError("证据 ID/variant_key 为空")
    if evidence["source_rank"] not in {"A", "B", "C", "D"}:
        raise ValueError("来源等级无效")
    if evidence["evidence_type"] not in {"dimensions", "side_profile", "automatic_profile", "automatic_description", "search_attempt", "official_document"}:
        raise ValueError("证据类型无效")
    if not isinstance(evidence["data_payload"], dict) or not isinstance(evidence["validation_flags"], list):
        raise ValueError("证据载荷/标记类型无效")
    timestamp = datetime.fromisoformat(evidence["retrieved_at_utc"].replace("Z", "+00:00"))
    if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("证据时间必须为 UTC")
    source = urlsplit(evidence["source_url"])
    if evidence["evidence_type"] != "search_attempt" and (not evidence["source_url"] or not evidence["publisher"] or not evidence["license_note"]):
        raise ValueError("实际证据必须有来源 URL/发布者/使用许可说明")
    if evidence["source_url"] and (source.scheme != "https" or not source.hostname or source.username or source.password):
        raise ValueError("证据来源必须为无凭证 HTTPS URL")
    content_hash = evidence["sha256"]
    if content_hash and (len(content_hash) != 64 or any(c not in "0123456789abcdef" for c in content_hash)):
        raise ValueError("证据 sha256 无效")
    if evidence["data_payload"].get("local_content") and not content_hash:
        raise ValueError("本地内容必须有 sha256")
    if evidence["evidence_type"] == "automatic_profile":
        payload = evidence["data_payload"]
        if payload.get("automatic") is not True or not payload.get("identity_match", {}).get("acceptable_for_inference"):
            raise ValueError("自动证据必须保留通过匹配检查的来源元数据")
        features = payload.get("features", {})
        if not features.get("usable") or len(features.get("top_profile_64", [])) != 64:
            raise ValueError("自动侧面几何必须有合格轮廓及 64 点采样")
    if evidence["evidence_type"] == "automatic_description":
        payload = evidence["data_payload"]
        if payload.get("automatic") is not True or not payload.get("observations") or not payload.get("source_snippets"):
            raise ValueError("自动描述必须有已提取的几何观测和来源短片段")
        if payload.get("features", {}).get("top_profile_64"):
            raise ValueError("定性描述不能伪造轮廓采样")


def exact_match(evidence: dict, record: dict) -> bool:
    if evidence["variant_key"] != record["variant_key"]:
        return False
    if evidence["model_year_claim"] != record["model_year"] or not record.get("market"):
        return False
    if str(evidence["market_claim"]).casefold() != record["market"].casefold():
        return False
    claim = evidence["variant_claim"]
    return isinstance(claim, dict) and all(
        str(claim.get(k, "")).strip().casefold() == str(record.get(k, "")).strip().casefold()
        for k in IDENTITY_FIELDS
    ) and all(record.get(k) for k in ("make", "model", "generation", "body_type"))


def make_evidence(record: dict, kind: str, url: str, publisher: str, timestamp: str, payload: dict,
                  flags: list[str], rank: str = "D", content_hash: str = "", market: str | None = None,
                  method: str = "adapter", license_note: str = "仅保存元数据；未授予图片再分发许可") -> dict:
    key_data = [record["variant_key"], kind, url, payload, flags]
    evidence_id = "e:" + hashlib.sha256(json.dumps(key_data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]
    result = {"evidence_id": evidence_id, "variant_key": record["variant_key"], "evidence_type": kind,
              "source_url": url, "publisher": publisher, "retrieved_at_utc": timestamp,
              "model_year_claim": record["model_year"],
              "variant_claim": {k: record.get(k, "") for k in IDENTITY_FIELDS},
              "market_claim": record.get("market", "") if market is None else market,
              "source_rank": rank, "sha256": content_hash, "extraction_method": method,
              "license_note": license_note, "data_payload": payload, "validation_flags": flags}
    validate(result)
    return result


def load_evidence(path) -> list[dict]:
    result, seen = [], set()
    with path.open(encoding="utf-8-sig") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            validate(item)
            if item["evidence_id"] in seen:
                raise ValueError(f"重复 evidence_id: {item['evidence_id']}")
            seen.add(item["evidence_id"])
            result.append(item)
    return result
