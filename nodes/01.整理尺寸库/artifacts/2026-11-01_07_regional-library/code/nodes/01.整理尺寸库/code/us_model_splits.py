"""Evidence-gated US identity splits; pending plans never alter production rows."""
import copy
import csv
import hashlib
import json
import math
from collections import defaultdict

from id_scheme import append_country_code, dimension_id
from model_members import year_set

MIGRATION_FIELDS = ["旧DIMENSION-ID", "新DIMENSION-ID", "成员", "适用年份", "拆分依据", "证据引用"]
CANDIDATE_FIELDS = ["旧DIMENSION-ID", "成员", "候选年份", "代际", "本地年份线索", "L-IN", "W-IN", "H-IN", "状态", "证据引用"]
PENDING_FIELDS = ["试点", "成员", "代际", "范围", "阻断原因", "证据引用"]


def fingerprint(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def write_table(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def apply_splits(rows, plan, evidence, reference):
    """Validate the whole pilot before changing any row. No copied group dimensions."""
    result = copy.deepcopy(rows)
    migration, candidates, pending = [], [], []
    sources = {s["id"]: s for s in evidence["sources"]}
    if len(sources) != len(evidence["sources"]):
        raise ValueError("重复证据ID")
    reference_years = defaultdict(set)
    for r in reference:
        reference_years[(r["make"], r["model"])].add(int(r["year"]))
    for pilot in plan["pilots"]:
        if not set(pilot["evidence_ids"]) <= sources.keys():
            raise ValueError("拆分计划含未知证据引用")
        old = {r["DIMENSION-ID"]: r for r in result if r["DIMENSION-ID"] in pilot["old_records"]}
        if set(old) != set(pilot["old_records"]):
            raise ValueError("US拆分原身份缺失；拒绝静默跳过")
        for identity, digest in pilot["old_records"].items():
            if fingerprint(old[identity]) != digest:
                raise ValueError("US拆分原记录已变化；需重审规则")
        members = pilot["members"]
        if len(set(members)) != len(members) or not members:
            raise ValueError("拆分成员为空或重复")
        cells = set()
        for identity, row in old.items():
            for member in members:
                local = set().union(*(reference_years[(row["MAKE"], alias)] for alias in pilot["reference_names"][member]))
                for year in sorted(year_set(row["YEAR"])):
                    cell = (member, year)
                    if cell in cells:
                        raise ValueError("原记录成员年份重叠")
                    cells.add(cell)
                    candidates.append({"旧DIMENSION-ID": identity, "成员": member, "候选年份": year,
                        "代际": row["代际"], "本地年份线索": "参考库有记录" if year in local else "参考库无记录，不等于美国未销售",
                        "L-IN": "", "W-IN": "", "H-IN": "", "状态": "待核，非正式尺寸", "证据引用": "|".join(pilot["evidence_ids"])})
                pending.append({"试点": pilot["id"], "成员": member, "代际": row["代际"], "范围": row["YEAR"],
                    "阻断原因": "待逐年核实美国供售/间断、各版本独立尺寸、下游身份与销量分配；不得复制组合尺寸",
                    "证据引用": "|".join(pilot["evidence_ids"])})
        if pilot["status"] == "pending":
            continue
        if pilot["status"] != "approved":
            raise ValueError("无效拆分状态")
        # Every member/year must be explicitly decided, including non-sale years.
        decisions = {(r["member"], r["year"]): r for r in pilot["year_decisions"]}
        if set(decisions) != cells or len(decisions) != len(pilot["year_decisions"]):
            raise ValueError("整组成员年份决定不完整或重复")
        for cell, decision in decisions.items():
            if decision["presence"] not in {"present", "absent"}:
                raise ValueError("成员年份未核实")
            require_evidence(sources, decision["evidence_ids"], cell, "us_presence")
            if not any(record.get("member") == cell[0] and record.get("year") == cell[1]
                and record.get("presence") == decision["presence"]
                for source_id in decision["evidence_ids"]
                if sources.get(source_id, {}).get("status") == "verified" and sources[source_id].get("market") == "US"
                for record in sources[source_id].get("presence_records", [])):
                raise ValueError("美国车型年供售决定与证据不符")
        reviews = pilot.get("downstream_reviews", {})
        required = {"structure-review", "shape-classification", "code-mapping", "sales-estimation", "size-calculation"}
        if set(reviews) != required or any(r.get("reviewed") is not True or not r.get("basis") for r in reviews.values()):
            raise ValueError("下游身份承接审查未完成")
        if reviews["sales-estimation"].get("allocation") not in {"member_evidence", "unallocated"}:
            raise ValueError("禁止复制组合销量给全部成员")
        if reviews["code-mapping"].get("old_codes") != "preserve":
            raise ValueError("必须保留旧编码历史")
        replacements, covered = [], set()
        for segment in pilot["segments"]:
            identity = segment["old_id"]
            parent = old[identity]
            member = segment["member"]
            segment_years = year_set(segment["YEAR"])
            if member not in members or not segment_years <= year_set(parent["YEAR"]):
                raise ValueError("拆分段超出原记录范围")
            for year in segment_years:
                cell = member, year
                if cell in covered or decisions[cell]["presence"] != "present":
                    raise ValueError("重复或未供售年份的尺寸段")
                require_evidence(sources, segment["evidence_ids"], cell, "dimensions")
                supported = [record for source_id in segment["evidence_ids"] for record in sources.get(source_id, {}).get("dimension_records", [])
                    if sources[source_id].get("status") == "verified" and sources[source_id].get("market") == "US"
                    and "dimensions" in sources[source_id].get("facts", [])
                    and record.get("member") == member and record.get("year") == year
                    and record.get("generation") == parent["代际"]
                    and record.get("unit") == "in" and record.get("width_basis") == "without_mirrors"
                    and all(float(record.get(f, "nan")) == float(segment[f]) for f in ("L-IN", "W-IN", "H-IN"))]
                if not supported:
                    raise ValueError("尺寸数值与逐年证据不一致")
                covered.add(cell)
            new = {**parent, "MODEL": member, "YEAR": segment["YEAR"]}
            for field in ("L-IN", "W-IN", "H-IN"):
                value = float(segment[field])
                if not math.isfinite(value) or value <= 0:
                    raise ValueError("独立尺寸必须为正数")
                new[field] = str(segment[field])
            new["参考车型"] = segment["reference"]
            new["备注"] = f"组合拆分；{pilot['id']}；" + "|".join(segment["evidence_ids"])
            new["DIMENSION-ID"] = append_country_code(dimension_id(new), "US")
            replacements.append(new)
            migration.append(dict(zip(MIGRATION_FIELDS, [identity, new["DIMENSION-ID"], member, new["YEAR"], pilot["id"], "|".join(segment["evidence_ids"])])))
        if covered != {cell for cell, d in decisions.items() if d["presence"] == "present"}:
            raise ValueError("缺少成员独立尺寸；整组拒绝替换")
        result = [r for r in result if r["DIMENSION-ID"] not in old] + replacements
        if len({r["DIMENSION-ID"] for r in result}) != len(result):
            raise ValueError("拆分后身份冲突")
        pending = [r for r in pending if r["试点"] != pilot["id"]]
    return result, migration, candidates, pending


def require_evidence(sources, ids, cell, fact):
    if not ids or not any(sources.get(i, {}).get("status") == "verified"
        and sources[i].get("market") == "US" and fact in sources[i].get("facts", [])
        and cell[0] in sources[i].get("members", []) and cell[1] in sources[i].get("years", []) for i in ids):
        raise ValueError(f"证据未核实：{cell} / {fact}")
