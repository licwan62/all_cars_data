"""自动读取来源的几何描述，作为无合格图片时的定性推断，不伪造轮廓采样。"""
from __future__ import annotations

import hashlib
import html
import re
from html.parser import HTMLParser

from .evidence import make_evidence
from .fetchers import FetchError


class DocumentText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.chunks, self.buffer, self.title = [], [], ""
        self.in_title = False

    def flush(self):
        value = " ".join(" ".join(self.buffer).split())
        if value:
            self.chunks.append(value)
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "aside"}: self.hidden += 1
        if tag == "title": self.in_title = True
        if tag in {"p", "li", "h1", "h2", "h3", "br", "td"} and not self.hidden: self.flush()

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "aside"}: self.hidden = max(0, self.hidden - 1)
        if tag == "title": self.in_title = False
        if tag in {"p", "li", "h1", "h2", "h3", "td"} and not self.hidden: self.flush()

    def handle_data(self, data):
        if self.in_title: self.title += data
        if not self.hidden: self.buffer.append(data)


def geometric_descriptions(chunks: list[str], lexicon: dict, body_aliases=None) -> dict:
    result, snippets = {}, {}
    for chunk in chunks:
        # 不把同句 Coupe 与 Hatchback 的几何混用；按并列分句隔离版本描述。
        clauses = re.split(r"(?<=[.!?;])\s+|\s*,?\s+and\s+(?=(?:a |the )?(?:two|three|four|five|2|3|4|5)[- ]door)", chunk, flags=re.I)
        for clause in clauses:
            if body_aliases and not any(re.search(r"(?<!\w)" + re.escape(a) + r"(?!\w)", clause, re.I) for a in body_aliases):
                continue
            if re.search(r"\b(?:not|without|no longer)\b.{0,25}(?:slop|boxy|notchback|fastback|compact)", clause, re.I):
                continue
            if re.search(r"\b(?:concept|prototype|interior|cargo cover|roof rack|sunshade|previous generation)\b", clause, re.I):
                continue
            for name, patterns in lexicon.items():
                for pattern in patterns:
                    match = re.search(pattern, clause, re.I)
                    if match:
                        result[name] = True
                        # 最小证据片段，不在结果中复制整篇文章。
                        words = clause[max(0, match.start() - 30):match.end() + 45].split()
                        snippets.setdefault(name, " ".join(words[:10]))
                        break
    return {"observations": result, "source_snippets": snippets}


def describe_candidate(observations: dict, dimensions: dict, policy: dict) -> dict:
    length, height = dimensions.get("length_mm"), dimensions.get("height_mm")
    if not observations or not length or not height:
        return {"label": "UNKNOWN", "alternates": [], "rule": "NO_DOCUMENTED_GEOMETRY_AND_DIMENSIONS"}
    ratio = height / length
    low = height <= policy["low_height_mm"] and ratio <= policy["low_height_length_ratio"]
    if observations.get("rear_step"):
        return {"label": "LOW_NOTCHBACK" if low else "STANDARD_SEDAN", "alternates": [], "rule": "DOCUMENTED_REAR_STEP_AND_BODY_PROPORTIONS"}
    if observations.get("box_outline") or observations.get("upright_rear"):
        if ratio >= policy["tall_height_length_ratio"]:
            return {"label": "TALL_BOX" if length <= policy["compact_length_mm"] else "BOXY_SUV", "alternates": [], "rule": "DOCUMENTED_BOX_OUTLINE_AND_TALL_PROPORTIONS"}
    if observations.get("roof_slope"):
        label = "LOW_FASTBACK" if low else "SLOPED_CROSSOVER" if height >= policy["crossover_height_mm"] else "SPORT_LIFTBACK"
        return {"label": label, "alternates": ["SLOPED_CROSSOVER"] if not low and 1480 <= height < policy["crossover_height_mm"] else [],
                "rule": "DOCUMENTED_SLOPING_ROOFLINE_AND_BODY_PROPORTIONS"}
    if observations.get("streamlined_profile") and height < policy["crossover_height_mm"] and length > policy["compact_length_mm"]:
        return {"label": "SPORT_LIFTBACK", "alternates": ["STANDARD_SEDAN"],
                "rule": "DOCUMENTED_STREAMLINED_LOW_BODY_REAR_GEOMETRY_UNCONFIRMED"}
    if (observations.get("compact_packaging") or observations.get("cabin_setback")) and length <= policy["compact_length_mm"] and ratio >= policy["compact_height_length_ratio"]:
        return {"label": "COMPACT_HATCH", "alternates": [], "rule": "DOCUMENTED_COMPACT_PACKAGING_AND_HIGH_CABIN_PROPORTIONS"}
    return {"label": "UNKNOWN", "alternates": [], "rule": "DOCUMENT_DESCRIPTION_INSUFFICIENT"}


def collect_documents(record: dict, client, policy: dict, timestamp: str) -> list[dict]:
    evidence = []
    for source in policy.get("document_sources", []):
        selector = source["selector"]
        if any(str(record.get(k, "")).casefold() != str(v).casefold() for k, v in selector.items() if k != "body_types"):
            continue
        if record.get("body_type") not in selector["body_types"]:
            continue
        url = source["url"]
        try:
            body = client.get(url)
            parser = DocumentText()
            parser.feed(body.decode("utf-8", errors="replace"))
            parser.flush()
            if not re.search(source["title_pattern"], html.unescape(parser.title), re.I):
                raise FetchError("DOCUMENT_TITLE_IDENTITY_MISMATCH")
            # 旧资料只能在上游明确的同一分支年份区间内作为推断；记录继承链，永不 VERIFIED。
            source_year = source["source_model_year"]
            raw_year = record["raw_fields"].get("YEAR", str(record["model_year"]))
            numbers = [int(v) for v in re.findall(r"\d{4}", raw_year)]
            if source_year != record["model_year"] and (not numbers or not min(numbers) <= source_year <= max(numbers)):
                raise FetchError("DOCUMENT_YEAR_OUTSIDE_SOURCE_BRANCH")
            aliases = policy["body_identity_aliases"].get(record.get("body_type", "").casefold()) if source.get("body_scoped_sentences") else None
            extracted = geometric_descriptions(parser.chunks, policy["description_lexicon"], aliases)
            if not extracted["observations"]:
                raise FetchError("NO_GEOMETRY_DESCRIPTION")
            # 定性描述没有精确轮廓，top_profile_64 留空。
            features = {"usable": True, "feature_version": "automatic-document-v1", "measurement_units": "qualitative",
                        "top_profile_64": [], "geometric_observations": extracted["observations"],
                        "image_quality": {}, "uncertainty": "来源几何描述 + 尺寸约束；不是实测侧面轮廓"}
            payload = {"automatic": True, "local_content": True, "outcome": "AUTO_DESCRIPTION_EXTRACTED",
                       "features": features, **extracted, "source_model_year": source_year,
                       "source_title": html.unescape(parser.title), "source_market": source["source_market"],
                       "identity_match": {"acceptable_for_inference": True, "make_model_confirmed": True,
                                          "model_year_confirmed": source_year == record["model_year"],
                                          "market_confirmed": source["source_market"] == record.get("market"),
                                          "generation_confirmed": False},
                       "inference_chain": {"source_year": source_year, "target_year": record["model_year"],
                                           "upstream_branch": record["source_record_id"], "generation": record.get("generation"),
                                           "minor_facelift_geometry_not_independently_verified": source_year != record["model_year"]}}
            item = make_evidence(record, "automatic_description", url, source["publisher"], timestamp, payload,
                            [], source["source_rank"], hashlib.sha256(body).hexdigest(), market=source["source_market"],
                            method="automatic HTML geometry phrase extraction + explicit source scope",
                            license_note="保留来源及短几何片段；原始网页仅私有研究归档，不公开再分发图片")
            item["model_year_claim"] = source_year
            item["variant_claim"]["generation"] = ""
            evidence.append(item)
        except (FetchError, ValueError, OSError) as e:
            evidence.append(make_evidence(record, "search_attempt", url, source["publisher"], timestamp,
                            {"outcome": "DOCUMENT_FAILED", "error_code": str(e)}, ["AUTO_DOCUMENT_FAILED"]))
    return evidence
