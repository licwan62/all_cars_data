"""无需人工图片/关键点的取证；Commons 正式 API + 有许可照片 + 本地几何。"""
from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit

from .automatic_geometry import GeometryError, Segmenter, analyze_image
from .evidence import make_evidence
from .fetchers import FetchError


def text(value):
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", str(value or ""))).replace("_", " ").split())


def metadata_match(page: dict, record: dict, policy: dict, require_variant: bool) -> dict:
    info = page["imageinfo"][0]
    metadata = info.get("extmetadata", {})
    description = text(metadata.get("ImageDescription", {}).get("value", ""))
    categories = [text(c.get("title", "")) for c in page.get("categories", [])]
    # EXIF/上传/照片拍摄时间不作为 model_year。只在车型标题/描述/车型分类中查车型年款。
    corpus = text(page["title"]) + " " + description + " " + " ".join(categories)
    low = corpus.casefold()
    tokens = [t for t in re.findall(r"[\w]+", record["model"].casefold()) if t]
    make = record["make"].casefold()
    model_match = make in low and all(re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", low) for t in tokens)
    title_text = text(page["title"]).casefold()
    if make in title_text and not all(re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", title_text) for t in tokens):
        model_match = False  # 描述不能覆盖明确矛盾的文件标题车型。
    year = str(record["model_year"])
    model_year = bool(re.search(r"(?<!\d)" + year + r"\s+(?:model\s+year\s+)?" + re.escape(make), low))
    if not model_year:
        model_year = any(year in c and "category:" in c.casefold() and make in c.casefold() for c in categories)
    if not model_year:
        # 如 Ford Mustang II 1974；不能用 2025-05-01 等拍摄日期尾缀代替年款。
        vehicle_name = re.escape(make) + r"\s+" + r"\s+".join(re.escape(t) for t in tokens)
        model_year = bool(re.search(vehicle_name + r"(?:\s+(?:i{1,4}|v|vi|vii|viii|ix|x|type r))?\s+\(?" + year + r"(?![-/]\d)", title_text))
    explicit_year = re.search(r"(?<!\d)(\d{4})\s+" + re.escape(make), title_text)
    if explicit_year and explicit_year[1] != year:
        model_year = False
    body = record.get("body_type", "").casefold()
    aliases = policy["body_identity_aliases"].get(body, [body])
    body_match = any(a and re.search(r"(?<!\w)" + re.escape(a) + r"(?!\w)", low) for a in aliases)
    excluded = [v for v in policy["excluded_metadata_words"] if re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)", low)]
    trim = record.get("trim", "").casefold()
    trim_match = not trim or trim in low or any(a in low for a in policy.get("trim_identity_aliases", {}).get(trim, []))
    extra_trim = [t for t in policy.get("special_trim_terms", []) if t in title_text and t not in trim and t not in record["model"].casefold()]
    if not trim and extra_trim:
        trim_match = False
    extra_model = [t for t in policy.get("model_variant_terms", []) if re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", title_text)
                   and t not in record["model"].casefold() and t not in trim]
    if extra_model:
        model_match = False
    reasons = []
    if not model_match: reasons.append("SOURCE_MODEL_MISMATCH")
    if not model_year: reasons.append("SOURCE_MODEL_YEAR_UNCONFIRMED")
    if require_variant and not body_match: reasons.append("SOURCE_BODY_VARIANT_UNCONFIRMED")
    if not trim_match: reasons.append("SOURCE_TRIM_UNCONFIRMED")
    if excluded: reasons.append("SOURCE_NON_STOCK_OR_NOT_PHOTOGRAPH")
    return {"acceptable_for_inference": not reasons, "make_model_confirmed": bool(model_match),
            "model_year_confirmed": model_year, "body_variant_confirmed": body_match, "trim_confirmed": trim_match,
            "generation_confirmed": False, "market_confirmed": False, "rejection_reasons": reasons,
            "source_title": page["title"], "source_description": description[:2000], "source_categories": categories,
            "target_generation": record.get("generation", ""), "target_market": record.get("market", "")}


def licence(info: dict, allowed: list[str]) -> dict | None:
    meta = info.get("extmetadata", {})
    name = text(meta.get("LicenseShortName", {}).get("value"))
    if name not in allowed:
        return None
    return {"name": name, "url": text(meta.get("LicenseUrl", {}).get("value")),
            "author": text(meta.get("Artist", {}).get("value")),
            "attribution": text(meta.get("Attribution", {}).get("value")),
            "source_page": info["descriptionurl"]}


def discover(record: dict, client, policy: dict):
    year, make, model = str(record["model_year"]), record["make"], record["model"]
    queries = [f'"{year}" "{make}" "{model}" "side"', f'intitle:"{year}" "{make}" "{model}"',
               f'"{year}" "{make}" "{model}" {record.get("body_type", "")}']
    for query in queries[:policy["search_rounds"]]:
        parameters = {"action": "query", "generator": "search", "gsrsearch": query,
                      "gsrnamespace": 6, "gsrlimit": policy["search_results"], "prop": "imageinfo|categories",
                      "cllimit": 50, "iiprop": "url|extmetadata|mime|size", "iiurlwidth": 960,
                      "format": "json"}
        url = "https://commons.wikimedia.org/w/api.php?" + urlencode(parameters)
        try:
            # 已公开文档的 JSON API，不爬取 HTML 页面；使用 API 返回的授权媒体资源。
            body = client.documented_api(url)
            result = json.loads(body)
            if "error" in result:
                raise FetchError("COMMONS_API_ERROR:" + str(result["error"].get("code")))
            def priority(p):
                title = text(p.get("title", "")).casefold()
                side = any(word in title for word in ("side", "profile"))
                quarter = any(word in title for word in ("front", "rear", "three-quarter"))
                return (0 if side else 2 if quarter else 1, p.get("index", 0), title)
            pages = sorted(result.get("query", {}).get("pages", {}).values(), key=priority)
            yield url, pages, None
        except (FetchError, ValueError, TypeError) as e:
            yield url, [], str(e)


def ensure_model(client, policy: dict) -> Path:
    model = policy["segmentation_model"]
    target = client.cache_dir / "models" / "u2netp.onnx"
    if not target.is_file():
        body = client.pinned_asset(model["url"], model["sha256"], model["redirect_domains"])
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".tmp")
        temporary.write_bytes(body)
        temporary.replace(target)
    if hashlib.sha256(target.read_bytes()).hexdigest() != model["sha256"]:
        raise GeometryError("SEGMENTATION_MODEL_HASH_MISMATCH")
    client.used_files.add(target)
    return target


class AutomaticCollector:
    def __init__(self, client, policy: dict, records: list[dict]):
        self.client, self.policy, self.segmenter = client, policy, None
        self.records = records
        self.used_images = {}

    def collect(self, record: dict, timestamp: str) -> list[dict]:
        from .automatic_documents import collect_documents
        evidence, seen, downloaded, accepted = collect_documents(record, self.client, self.policy, timestamp), set(), 0, 0
        # 同型号同年的多个车身版本，图片必须显式消歧，不能让同一张图流向 Coupe/Hatchback。
        variants = {r.get("body_type") for r in self.records if all(r.get(k) == record.get(k) for k in ("make", "model", "model_year", "market"))}
        strict_variant = len(variants) > 1
        for search_url, pages, error in discover(record, self.client, self.policy):
            evidence.append(make_evidence(record, "search_attempt", search_url, "Wikimedia Commons API", timestamp,
                            {"outcome": "FAILED" if error else "NO_DATA" if not pages else "DISCOVERED",
                             "error_code": error, "results": len(pages)}, ["COMMONS_REQUEST_FAILED"] if error else []))
            for page in pages:
                if not page.get("imageinfo") or page["title"] in seen:
                    continue
                seen.add(page["title"])
                info = page["imageinfo"][0]
                match = metadata_match(page, record, self.policy, strict_variant)
                licence_data = licence(info, self.policy["allowed_licenses"])
                if info.get("mime") not in {"image/jpeg", "image/png"} or not licence_data:
                    match["rejection_reasons"].append("IMAGE_TYPE_OR_LICENSE_REJECTED")
                url = info.get("descriptionurl", "https://commons.wikimedia.org")
                if match["rejection_reasons"]:
                    evidence.append(make_evidence(record, "search_attempt", url, "Wikimedia Commons", timestamp,
                                    {"outcome": "REJECTED_METADATA", "identity_match": match}, match["rejection_reasons"]))
                    continue
                if downloaded >= self.policy["max_images_per_variant"]:
                    break
                downloaded += 1
                asset = info.get("thumburl") or info["url"]
                # imageinfo 附带跟踪参数；去掉不影响资源身份。
                parsed = urlsplit(asset)
                asset = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
                try:
                    body = self.client.licensed_media(asset, licence_data)
                    content_hash = hashlib.sha256(body).hexdigest()
                    association = tuple(record.get(k) for k in ("make", "model", "model_year", "body_type", "trim", "market"))
                    if content_hash in self.used_images and self.used_images[content_hash] != association:
                        raise GeometryError("IMAGE_ALREADY_BOUND_TO_DIFFERENT_VARIANT")
                    if self.segmenter is None:
                        model_path = ensure_model(self.client, self.policy)
                        self.segmenter = Segmenter(model_path, self.policy["segmentation_model"]["sha256"])
                    features, overlay = analyze_image(body, self.segmenter, self.policy["geometry"])
                    self.used_images[content_hash] = association
                    overlay_path = self.client.cache_dir / "overlays" / (content_hash + ".png")
                    overlay_path.parent.mkdir(parents=True, exist_ok=True)
                    overlay_path.write_bytes(overlay)
                    self.client.used_files.add(overlay_path)
                    payload = {"outcome": "AUTO_GEOMETRY_EXTRACTED", "identity_match": match,
                               "features": features, "image_url": asset, "license": licence_data,
                               "independent_source_id": str(page.get("pageid")),
                               "overlay_sha256": hashlib.sha256(overlay).hexdigest(),
                               "segmentation_model_sha256": self.segmenter.model_sha256,
                               "automatic": True, "local_content": True,
                               "limitations": ["source_generation_and_market_not_verified", "stock_condition_not_verified",
                                               "orientation_is_heuristic", "classification_rules_not_calibrated"]}
                    item = make_evidence(record, "automatic_profile", url, "Wikimedia Commons licensed photograph", timestamp,
                                    payload, [], "B", content_hash, method="Commons API + U2netp + OpenCV wheels + silhouette",
                                    market="", license_note=json.dumps(licence_data, ensure_ascii=False))
                    item["variant_claim"]["generation"] = ""
                    if not match["body_variant_confirmed"]:
                        item["variant_claim"]["body_type"] = ""
                    evidence.append(item)
                    accepted += 1
                    if accepted >= self.policy["max_accepted_profiles"]:
                        break
                except (FetchError, GeometryError, ImportError, OSError, ValueError) as e:
                    evidence.append(make_evidence(record, "search_attempt", url, "automatic image geometry", timestamp,
                                    {"outcome": "REJECTED_IMAGE", "error_code": str(e), "identity_match": match,
                                     "image_url": asset}, ["AUTO_IMAGE_REJECTED"]))
            if accepted >= self.policy["max_accepted_profiles"] or downloaded >= self.policy["max_images_per_variant"]:
                break
        if not accepted:
            evidence.append(make_evidence(record, "search_attempt", "", "automatic image geometry", timestamp,
                            {"outcome": "NO_ACCEPTED_IMAGE", "downloaded": downloaded, "candidates": len(seen)},
                            ["AUTO_NO_ELIGIBLE_SIDE_IMAGE"]))
        return evidence
