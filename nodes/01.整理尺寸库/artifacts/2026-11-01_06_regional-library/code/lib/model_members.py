"""Explicit model membership; group coverage never proves a member's model years."""
import json
import re
import unicodedata
from collections import defaultdict


def model_key(value):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKC", value).casefold())


def year_set(value):
    match = re.fullmatch(r"(\d{4})(?:-(\d{4}))?", value.strip())
    if not match or int(match[2] or match[1]) < int(match[1]):
        raise ValueError(f"Invalid year range: {value}")
    return set(range(int(match[1]), int(match[2] or match[1]) + 1))


def load_members(path):
    rules = json.loads(path.read_text(encoding="utf-8"))
    if rules.get("schema_version") != 1:
        raise ValueError("Unsupported model membership schema")
    seen, aliases = set(), {}
    for group in rules["groups"]:
        pair = model_key(group["make"]), model_key(group["model"])
        if pair in seen:
            raise ValueError("Duplicate combined model rule")
        seen.add(pair)
        if group["status"] not in {"registered", "pending"}:
            raise ValueError("Invalid membership status")
        if group["status"] == "registered" and not group["members"]:
            raise ValueError("Registered group needs explicit members")
        for member in group["members"]:
            for name in [member["model"], *member.get("aliases", [])]:
                alias = pair[0], model_key(name)
                canonical = model_key(member["model"])
                if alias in aliases and aliases[alias] != canonical:
                    raise ValueError("Ambiguous model alias")
                aliases[alias] = canonical
    return rules


class ModelCoverage:
    def __init__(self, rows, rules):
        self.rows = rows
        self.independent = defaultdict(set)
        self.names = defaultdict(set)
        self.members = defaultdict(list)
        self.aliases = {}
        self.groups = {(model_key(g["make"]), model_key(g["model"])): g for g in rules["groups"]}
        for group in rules["groups"]:
            for member in group["members"]:
                for name in [member["model"], *member.get("aliases", [])]:
                    self.aliases[(model_key(group["make"]), model_key(name))] = model_key(member["model"])
        for row in rows:
            pair = model_key(row["MAKE"]), model_key(row["MODEL"])
            group = self.groups.get(pair)
            if "/" in row["MODEL"] or group:
                if group and group["status"] == "registered":
                    for member in group["members"]:
                        self.members[(pair[0], model_key(member["model"]))].append(row)
                continue
            self.independent[pair].update(year_set(row["YEAR"]))
            self.names[pair].add(row["MODEL"])

    def canonical(self, make, model):
        make, model = model_key(make), model_key(model)
        return make, self.aliases.get((make, model), model)

    def classify(self, make, model, year=None):
        pair = self.canonical(make, model)
        current = self.independent.get(pair, set())
        groups = self.members.get(pair, [])
        matching = [r for r in groups if year is None or year in year_set(r["YEAR"])]
        if current and (year is None or year in current):
            state = "独立记录覆盖"
        elif matching:
            state = "组合记录覆盖、成员年份待核"
        elif current or groups:
            state = "确认年份缺口（本地参考差集）"
        else:
            state = "名称待核"
        # Substring suggestions must never determine coverage.
        suggestions = set(self.names.get(pair, set()))
        if state == "名称待核":
            for (brand, candidate), display in self.names.items():
                if brand == pair[0] and min(len(candidate), len(pair[1])) >= 3 and (candidate.startswith(pair[1]) or pair[1].startswith(candidate)):
                    suggestions.update(display)
        suggestions.update(r["MODEL"] for r in matching)
        return {"state": state, "years": set(current), "candidates": "|".join(sorted(suggestions)),
                "group_ids": "|".join(sorted({r["DIMENSION-ID"] for r in matching}))}
