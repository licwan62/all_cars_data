"""车型族研究队列：同市场/车型/结构为一个研究单元，每个代际只抽少数年份研究。

研究结论写入 data/cover_shape/family_cache.csv（规则可按代际/年份/模式细分），整族按规则覆盖；
队列状态由缓存覆盖情况重建，自动联网研究的失败/重试进度按族保存并在成员变化时失效。
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from .family_cache import family_id, family_key, natural, norm, sample_years

STATES = {"PENDING", "PARTIAL", "CACHED", "BLOCKED_INPUT", "NO_EVIDENCE", "DEFERRED_LIMIT", "CONFLICT"}
PROGRESS_KEYS = ("attempts", "last_attempt_at_utc", "next_retry_at_utc", "last_result", "last_batch", "last_evidence_ids", "last_outcomes")
COVERED_METHODS = {"representative_evidence", "family_cache_sampled", "family_cache_inherited"}
OPEN_STATES = {"PENDING", "PARTIAL", "NO_EVIDENCE", "DEFERRED_LIMIT"}


def read_queue(path):
    if not path.is_file():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    # 旧版按尺寸分支的队列没有 family_id，视为无进度，由新规则重建。
    rows = [r for r in rows if "family_id" in r]
    if len({r["family_id"] for r in rows}) != len(rows) or any(r["state"] not in STATES for r in rows):
        raise ValueError("研究队列重复车型族或状态无效")
    return rows


def _matches_selector(selector, first, generations):
    for key, value in selector.items():
        if key == "generation":
            if norm(value) not in {norm(g) for g in generations}:
                return False
        elif norm(first.get(key, "")) != norm(value):
            return False
    return True


def families_of(groups):
    families = defaultdict(list)
    for gid, _, members, _ in groups:
        for record in members:
            families[family_key(record)].append((gid, record))
    return families


def refresh_queue(groups, audit, outcomes, previous, policy):
    old = {r["family_id"]: r for r in previous}
    classified = {r["group_id"]: r for r in audit}
    order = {value: i for i, value in enumerate(policy["market_priority"])}
    queue = []
    for members in families_of(groups).values():
        first = members[0][1]
        fid = family_id(first)
        fingerprint = hashlib.sha256(json.dumps(sorted((r["source_record_id"], r["covered_years"]) for _, r in members),
                                                ensure_ascii=False).encode()).hexdigest()
        prior = old.get(fid, {})
        if prior.get("input_fingerprint") != fingerprint:
            prior = {}
        methods = {r["source_record_id"]: outcomes[r["source_record_id"]]["SHAPE_METHOD"] for _, r in members}
        by_generation = defaultdict(list)
        for _, record in members:
            by_generation[record.get("generation", "")].append(record)
        generations = []
        for generation, records in sorted(by_generation.items(), key=lambda item: natural(item[0])):
            covered_years = sorted({y for r in records for y in r["covered_years"]})
            covered = sum(methods[r["source_record_id"]] in COVERED_METHODS for r in records)
            generations.append({"generation": generation, "year_min": covered_years[0], "year_max": covered_years[-1],
                                "records": len(records), "covered": covered, "sample_years": sample_years(covered_years, policy)})
        open_generations = [g for g in generations if g["covered"] < g["records"]]
        covered = sum(g["covered"] for g in generations)
        incomplete = all(any(r.get(k) is None for k in ("length_mm", "width_mm", "height_mm")) for _, r in members)
        audits = [classified[gid] for gid in {gid for gid, _ in members}]
        kickoff = any(_matches_selector(s, first, by_generation) for s in policy.get("kickoff_selectors", []))
        alternates = [a for a in audits if a.get("alternate_shapes")]
        why = "conflict" if any(a["SHAPE_STATUS"] == "CONFLICT" for a in audits) else "kickoff" if kickoff else (
              "ambiguous_low_roof" if any(a["SHAPE"] in {"LOW_NOTCHBACK", "LOW_FASTBACK"} for a in alternates) else
              "ambiguous" if alternates else "prototype")
        if incomplete:
            state = policy["missing_dimensions_state"]
        elif not open_generations:
            state = "CACHED"
        elif prior.get("state") in {"NO_EVIDENCE", "DEFERRED_LIMIT", "CONFLICT"}:
            state = prior["state"]
        else:
            state = "PARTIAL" if covered else "PENDING"
        item = {"family_id": fid, "input_fingerprint": fingerprint, "priority": policy["priority_order"].index(why),
                "priority_reason": why, "state": state, "market": first["market"], "make": first["make"],
                "model": first["model"], "body_type": first.get("body_type", ""), "affected_records": len(members),
                "groups": len({gid for gid, _ in members}), "covered_records": covered,
                "cross_market_records": sum(m == "family_cache_cross_market" for m in methods.values()),
                "pending_records": len(members) - covered, "generations": generations,
                "research_generations": [g["generation"] for g in open_generations],
                "suggested_sample_years": sorted({y for g in open_generations for y in g["sample_years"]}),
                "SHAPE_counts": dict(Counter(outcomes[r["source_record_id"]]["SHAPE"] for _, r in members)), "attempts": 0}
        item.update({k: prior[k] for k in PROGRESS_KEYS if k in prior})
        queue.append(item)
    queue.sort(key=lambda r: (r["priority"], order.get(r["market"], 99), -r["pending_records"], r["family_id"]))
    return queue


def open_tasks(queue, policy, markets=None, now=None):
    """可研究车型族（已全覆盖、缺尺寸、冲突、重试未到期或次数用尽的不选）。"""
    now = now or datetime.now(timezone.utc)
    markets = markets if markets is not None else policy.get("research_markets", ["US"])
    result = []
    for row in queue:
        if row["market"] not in markets or row["state"] not in OPEN_STATES or row["attempts"] >= policy["max_attempts"]:
            continue
        if row.get("next_retry_at_utc") and datetime.fromisoformat(row["next_retry_at_utc"].replace("Z", "+00:00")) > now:
            continue
        result.append(row)
    order = {market: i for i, market in enumerate(markets)}
    result.sort(key=lambda r: (r["priority"], order[r["market"]], -r["pending_records"], r["family_id"]))
    return result


def select_tasks(queue, policy, limit, now=None, markets=None):
    if limit <= 0:
        raise ValueError("研究数量必须为正数")
    result, models = [], Counter()
    for row in open_tasks(queue, policy, markets, now):
        model = (row["market"], norm(row["make"]), norm(row["model"]))
        if models[model] >= policy.get("max_per_model_per_batch", 1):
            continue
        models[model] += 1
        result.append(row)
        if len(result) == limit:
            break
    return result


def record_attempt(task, evidence, results, rules_written, policy, batch_name, timestamp):
    result = dict(task)
    limited = any(e["data_payload"].get("error_code") == "REQUEST_BUDGET_EXHAUSTED" for e in evidence)
    if rules_written:
        state = "PARTIAL"
    elif any(r["status"] == "CONFLICT" for r in results):
        state = "CONFLICT"
    else:
        state = "DEFERRED_LIMIT" if limited else "NO_EVIDENCE"
    result.update({"state": state, "attempts": task["attempts"] + (0 if limited and not rules_written else 1),
                   "last_attempt_at_utc": timestamp, "last_result": ";".join(r["cover_shape"] for r in results) or "UNKNOWN",
                   "last_batch": batch_name, "last_evidence_ids": [e["evidence_id"] for e in evidence],
                   "last_outcomes": dict(Counter(e["data_payload"].get("outcome", "IMPORTED") for e in evidence))})
    moment = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    result["next_retry_at_utc"] = (moment + timedelta(hours=policy["retry_after_hours"])).isoformat().replace("+00:00", "Z") if state == "NO_EVIDENCE" else ""
    return result
