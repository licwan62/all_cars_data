"""默认关闭网络；白名单、robots、限速、有限重试与响应缓存。"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from .evidence import make_evidence

AGENT = "CoverShapeResearch/0.1"


class FetchError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FetchError(f"REDIRECT_REQUIRES_EXPLICIT_SOURCE:{code}")


class HttpClient:
    def __init__(self, sources: dict, cache_dir: Path, max_requests: int):
        self.sources, self.cache_dir, self.max_requests = sources, cache_dir, max_requests
        self.count, self.cache_hits = 0, 0
        self.last, self.robots, self.logs, self.used_files, self.crawl_delays = {}, {}, [], set(), {}
        self.interval = max(float(sources.get("seconds_per_request", 1)), 1.0)
        self.timeout = min(max(float(sources.get("timeout_seconds", 15)), 1), 30)
        self.retries = min(max(int(sources.get("retries", 1)), 0), 2)
        client = self
        class CanonicalRedirect(urllib.request.HTTPRedirectHandler):
            max_repeats = 2
            max_redirections = 3
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                host = client.check_url(newurl)
                if host != urlsplit(req.full_url).hostname:
                    raise FetchError("CROSS_DOMAIN_REDIRECT_REQUIRES_EXPLICIT_SOURCE")
                if client.count >= client.max_requests:
                    raise FetchError("REQUEST_BUDGET_EXHAUSTED")
                wait = max(client.interval, client.crawl_delays.get(host, 0)) - (time.monotonic() - client.last.get(host, 0))
                if wait > 0: time.sleep(wait)
                client.last[host] = time.monotonic()
                client.count += 1
                client.logs.append({"url": req.full_url, "outcome": "CANONICAL_REDIRECT", "status": code, "redirect_to": newurl})
                return super().redirect_request(req, fp, code, msg, headers, newurl)
        self.opener = urllib.request.build_opener(CanonicalRedirect())

    def check_url(self, url: str) -> str:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname not in self.sources["allowed_domains"]:
            raise FetchError("DOMAIN_NOT_ALLOWED")
        if parsed.username or parsed.password or parsed.port not in {None, 443}:
            raise FetchError("URL_CREDENTIALS_OR_PORT_NOT_ALLOWED")
        if any(word in parsed.query.lower() for word in ("token", "key", "secret", "password")):
            raise FetchError("SECRET_QUERY_NOT_ALLOWED")
        return parsed.hostname

    def _request(self, url: str) -> bytes:
        host = self.check_url(url)
        key = hashlib.sha256(url.encode()).hexdigest()
        cached = self.cache_dir / f"{key}.body"
        meta = self.cache_dir / f"{key}.json"
        if cached.is_file() and meta.is_file():
            metadata = json.loads(meta.read_text(encoding="utf-8"))
            body = cached.read_bytes()
            if metadata.get("url") == url and hashlib.sha256(body).hexdigest() == metadata.get("sha256"):
                self.cache_hits += 1
                self.used_files.update((cached, meta))
                self.logs.append({"url": url, "outcome": "CACHE_HIT", "sha256": metadata["sha256"], "bytes": len(body)})
                return body
            raise FetchError("CACHE_HASH_MISMATCH")
        for attempt in range(self.retries + 1):
            if self.count >= self.max_requests:
                raise FetchError("REQUEST_BUDGET_EXHAUSTED")
            wait = max(self.interval, self.crawl_delays.get(host, 0)) - (time.monotonic() - self.last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            self.last[host] = time.monotonic()
            self.count += 1
            started = time.monotonic()
            try:
                with self.opener.open(urllib.request.Request(url, headers={"User-Agent": AGENT}), timeout=self.timeout) as response:
                    body = response.read(8 * 1024 * 1024 + 1)
                    if len(body) > 8 * 1024 * 1024:
                        raise FetchError("RESPONSE_TOO_LARGE")
                digest = hashlib.sha256(body).hexdigest()
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                temporary = cached.with_suffix(".tmp")
                temporary.write_bytes(body)
                temporary.replace(cached)
                meta.write_text(json.dumps({"url": url, "sha256": digest}, indent=2), encoding="utf-8")
                self.used_files.update((cached, meta))
                self.logs.append({"url": url, "outcome": "HTTP_SUCCESS", "attempt": attempt + 1,
                                  "sha256": digest, "bytes": len(body), "seconds": round(time.monotonic() - started, 3)})
                return body
            except (urllib.error.URLError, TimeoutError, FetchError) as e:
                code = f"HTTP_{e.code}" if isinstance(e, urllib.error.HTTPError) else type(e).__name__
                self.logs.append({"url": url, "outcome": "FAILED", "error_code": code,
                                  "attempt": attempt + 1, "seconds": round(time.monotonic() - started, 3)})
                if isinstance(e, FetchError):
                    raise
                if attempt == self.retries or isinstance(e, urllib.error.HTTPError) and e.code < 500 and e.code != 429:
                    raise FetchError(code) from e
                time.sleep(2 ** attempt)
        raise FetchError("UNREACHABLE")

    def get(self, url: str) -> bytes:
        host = self.check_url(url)
        if host not in self.robots:
            robots_url = f"https://{host}/robots.txt"
            try:
                body = self._request(robots_url)
                parser = urllib.robotparser.RobotFileParser(robots_url)
                parser.parse(body.decode("utf-8", errors="replace").splitlines())
                self.robots[host] = parser
                self.crawl_delays[host] = parser.crawl_delay(AGENT) or parser.crawl_delay("*") or 0
                # 某些站点将全站 Crawl-delay 放在 User-agent 之前；也遵守此限速。
                for line in body.decode("utf-8", errors="replace").splitlines():
                    if line.lower().startswith("crawl-delay:"):
                        try: self.crawl_delays[host] = max(self.crawl_delays[host], float(line.split(":", 1)[1].strip()))
                        except ValueError: pass
            except FetchError as e:
                if str(e) == "HTTP_404":
                    self.robots[host] = None  # robots 不存在；403/超时不等于许可。
                else:
                    raise FetchError("ROBOTS_UNAVAILABLE:" + str(e)) from e
        parser = self.robots[host]
        if parser is not None and not parser.can_fetch(AGENT, url):
            raise FetchError("ROBOTS_DENIED")
        return self._request(url)

    def documented_api(self, url: str) -> bytes:
        """明确登记的正式 API；不将 API 自动化混同于 HTML 爬虫。"""
        parsed = urlsplit(url)
        allowed = self.sources.get("documented_api_endpoints", [])
        if f"https://{parsed.hostname}{parsed.path}" not in allowed:
            raise FetchError("UNDOCUMENTED_API_ENDPOINT")
        self.check_url(url)
        return self._request(url)

    def licensed_media(self, url: str, licence: dict) -> bytes:
        if not licence.get("name") or not licence.get("source_page", "").startswith("https://commons.wikimedia.org/"):
            raise FetchError("LICENSE_METADATA_REQUIRED")
        self.check_url(url)
        if urlsplit(url).hostname not in self.sources.get("licensed_media_domains", []):
            raise FetchError("MEDIA_DOMAIN_NOT_ALLOWED")
        return self._request(url)

    def pinned_asset(self, url: str, expected_sha256: str, redirect_domains: list[str]) -> bytes:
        """只下载已固定校验和的模型资产；重定向域名受限，不记录临时签名参数。"""
        self.check_url(url)
        client = self
        class AssetRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                parsed = urlsplit(newurl)
                if parsed.scheme != "https" or parsed.hostname not in redirect_domains:
                    raise FetchError("MODEL_REDIRECT_DOMAIN_NOT_ALLOWED")
                if client.count >= client.max_requests:
                    raise FetchError("REQUEST_BUDGET_EXHAUSTED")
                client.count += 1
                return super().redirect_request(req, fp, code, msg, headers, newurl)
        if self.count >= self.max_requests:
            raise FetchError("REQUEST_BUDGET_EXHAUSTED")
        self.count += 1
        try:
            with urllib.request.build_opener(AssetRedirect()).open(
                    urllib.request.Request(url, headers={"User-Agent": AGENT}), timeout=self.timeout) as response:
                body = response.read(8 * 1024 * 1024 + 1)
            if hashlib.sha256(body).hexdigest() != expected_sha256:
                raise FetchError("SEGMENTATION_MODEL_HASH_MISMATCH")
            self.logs.append({"url": url, "outcome": "PINNED_MODEL_SUCCESS", "sha256": expected_sha256, "bytes": len(body)})
            return body
        except (urllib.error.URLError, TimeoutError, FetchError) as e:
            self.logs.append({"url": url, "outcome": "PINNED_MODEL_FAILED", "error_code": type(e).__name__})
            raise FetchError("MODEL_DOWNLOAD_FAILED:" + type(e).__name__) from e


def parse_cvs(payload: dict) -> list[dict]:
    if not isinstance(payload.get("Results"), list) or not isinstance(payload.get("Count"), int):
        raise FetchError("CVS_SCHEMA_CHANGED")
    if payload["Count"] != len(payload["Results"]):
        raise FetchError("CVS_COUNT_MISMATCH")
    rows = []
    for item in payload["Results"]:
        if not isinstance(item, dict) or not isinstance(item.get("Specs"), list):
            raise FetchError("CVS_SPECS_SCHEMA_CHANGED")
        fields = {}
        for spec in item["Specs"]:
            if not isinstance(spec, dict) or "Name" not in spec or "Value" not in spec or spec["Name"] in fields:
                raise FetchError("CVS_FIELD_SCHEMA_CHANGED")
            fields[spec["Name"]] = spec["Value"]
        rows.append(fields)
    return rows


def cvs_evidence(record: dict, client: HttpClient, timestamp: str) -> dict:
    url = "https://vpic.nhtsa.dot.gov/api/vehicles/GetCanadianVehicleSpecifications/?" + urlencode(
        {"year": record["model_year"], "make": record["make"], "model": record["model"], "format": "json", "units": "Metric"})
    try:
        body = client.get(url)
        payload = json.loads(body)
        rows = parse_cvs(payload)
        # 请求匹配可为部分匹配；不得将任意第一条或其他版本填充到该车型。
        exact = [r for r in rows if str(r.get("Make", "")).casefold() == record["make"].casefold()
                 and str(r.get("Model", "")).casefold() == record["model"].casefold()]
        flags = ["CANADIAN_MARKET_UNCONFIRMED", "CVS_GENERATION_VARIANT_UNCONFIRMED"]
        selected = exact[0] if len(exact) == 1 else {}
        if not rows:
            flags.append("NO_DATA")
        elif not selected:
            flags.append("CVS_VARIANT_AMBIGUOUS")
        data = {"outcome": "NO_DATA" if not rows else "VARIANT_AMBIGUOUS" if not selected else "UNCONFIRMED_MATCH",
                "raw_results": rows, "query_year": record["model_year"], "units": "cm",
                "width_definition": "unknown", "MYR_definition": "last two digits of data compilation year",
                "B_definition": "body-dependent; not a universal rear-deck measurement",
                "identity_confirmed": False}
        for source, target in (("OL", "length_mm"), ("OW", "width_mm"), ("OH", "height_mm"),
                               ("WB", "wheelbase_mm"), ("F", "front_overhang_mm"), ("G", "rear_overhang_mm")):
            try:
                value = float(selected[source])
                if value > 0 and value < float("inf"):
                    data[target] = value * 10
            except (KeyError, TypeError, ValueError):
                pass
        return make_evidence(record, "dimensions", url, "NHTSA / Transport Canada CVS", timestamp, data,
                             flags, rank="A", content_hash=hashlib.sha256(body).hexdigest(), market="CA",
                             method="CVS Specs Name/Value; Metric cm -> mm")
    except (FetchError, ValueError, TypeError, UnicodeError) as e:
        return make_evidence(record, "search_attempt", url, "NHTSA CVS", timestamp,
                             {"outcome": "FAILED", "error_code": str(e) if isinstance(e, FetchError) else type(e).__name__},
                             ["CVS_REQUEST_FAILED"])


def official_evidence(record: dict, client: HttpClient, timestamp: str, source: dict) -> dict:
    """显式官方 URL 下载/归档；不将未解析文档自动当作尺寸/轮廓证据。"""
    url = source["url"]
    try:
        body = client.get(url)
        return make_evidence(record, "official_document", url, source["publisher"], timestamp,
                             {"outcome": "DOWNLOADED", "bytes": len(body), "identity_confirmed": False,
                              "page": source.get("page"), "local_content": True},
                             ["MANUAL_EXTRACTION_REQUIRED"], "A", hashlib.sha256(body).hexdigest(),
                             method="explicit official URL; no automatic claims", license_note=source["license_note"])
    except FetchError as e:
        return make_evidence(record, "search_attempt", url, source["publisher"], timestamp,
                             {"outcome": "FAILED", "error_code": str(e)}, ["OFFICIAL_REQUEST_FAILED"])


def search_plan(record: dict, timestamp: str, mode: str) -> dict:
    words = [str(record.get(k, "")) for k in ("model_year", "make", "model", "trim", "generation", "body_type", "market")]
    query = " ".join(w for w in words if w) + " side profile official factory brochure side elevation"
    return make_evidence(record, "search_attempt", "", "manual image search adapter", timestamp,
                         {"query": query, "outcome": "NOT_ATTEMPTED", "mode": mode,
                          "reason": "No configured licensed image search provider; manual evidence import supported"},
                         ["IMAGE_SEARCH_NOT_CONFIGURED"])
