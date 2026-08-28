from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TRIM_HEADER = ["DIMENSION-ID", "Year", "Make", "Model"]
AUDIT_HEADER = TRIM_HEADER + [
    "主车型",
    "结构",
    "版本",
    "CAB",
    "BED",
    "匹配方式",
    "置信度",
    "说明",
    "审核状态",
    "证据URL",
]
UNMAPPED_HEADER = [
    "DIMENSION-ID",
    "Year",
    "主车型",
    "结构",
    "版本",
    "CAB",
    "BED",
    "原因",
]
CONFLICT_HEADER = [
    "Year",
    "Make",
    "Model",
    "DIMENSION-ID数量",
    "DIMENSION-ID列表",
    "判定",
]
OVERRIDE_HEADER = ["DIMENSION-ID", "Year", "Action", "Make", "Model", "Note"]
ONLINE_EVIDENCE_HEADER = [
    "DIMENSION-ID",
    "Year",
    "Make",
    "Model",
    "版本",
    "结构",
    "Decision",
    "SourceURL",
    "SourceTitle",
    "EvidenceNote",
    "ReviewedAt",
]
ONLINE_REVIEW_HEADER = [
    "DIMENSION-ID",
    "Year",
    "源MAKE",
    "源MODEL",
    "主车型",
    "版本",
    "结构",
    "CAB",
    "BED",
    "候选Make",
    "候选Model",
    "原匹配方式",
    "审核状态",
    "原因",
    "建议搜索词",
    "证据要求",
]
ONLINE_REVIEW_GROUP_HEADER = [
    "源MAKE",
    "源MODEL",
    "主车型",
    "版本",
    "结构",
    "候选Make",
    "候选Model",
    "原匹配方式",
    "Year数量",
    "Year列表",
    "DIMENSION-ID数量",
    "DIMENSION-ID列表",
    "审核状态",
    "建议搜索词",
    "证据要求",
]

YEAR_PATTERN = re.compile(r"\d{4}")


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def normalized(value: object) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", clean(value))
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    return re.sub(r"[^a-z0-9]+", "", ascii_text)


def expanded_years(value: object) -> list[int]:
    years = [int(item) for item in YEAR_PATTERN.findall(clean(value))]
    if not years:
        return []
    if len(years) == 1:
        return years
    start, end = sorted(years[:2])
    return list(range(start, end + 1))


def split_candidates(value: object) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in clean(value).split(";"):
        candidate = item.strip()
        if not candidate or "|" not in candidate:
            continue
        make, model = (part.strip() for part in candidate.split("|", 1))
        pair = (make, model)
        if make and model and pair not in seen:
            seen.add(pair)
            result.append(pair)
    return result


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [
            {clean(key): clean(value) for key, value in row.items()}
            for row in csv.DictReader(file)
        ]


def require_columns(
    rows: list[dict[str, str]], required: Iterable[str], source: Path
) -> None:
    if not rows:
        raise ValueError(f"输入为空: {source}")
    missing = [column for column in required if column not in rows[0]]
    if missing:
        raise ValueError(f"{source} 缺少字段: {', '.join(missing)}")


def write_csv(path: Path, header: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def group_online_review_rows(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    groups: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        key = tuple(
            clean(row[column])
            for column in (
                "源MAKE",
                "源MODEL",
                "主车型",
                "版本",
                "结构",
                "候选Make",
                "候选Model",
                "原匹配方式",
                "审核状态",
            )
        )
        groups[key].append(row)

    result: list[dict[str, object]] = []
    for key, members in groups.items():
        years = sorted({int(row["Year"]) for row in members})
        dimension_ids = sorted({clean(row["DIMENSION-ID"]) for row in members})
        result.append(
            {
                "源MAKE": key[0],
                "源MODEL": key[1],
                "主车型": key[2],
                "版本": key[3],
                "结构": key[4],
                "候选Make": key[5],
                "候选Model": key[6],
                "原匹配方式": key[7],
                "Year数量": len(years),
                "Year列表": "; ".join(str(year) for year in years),
                "DIMENSION-ID数量": len(dimension_ids),
                "DIMENSION-ID列表": "; ".join(dimension_ids),
                "审核状态": key[8],
                "建议搜索词": clean(members[0]["建议搜索词"]),
                "证据要求": clean(members[0]["证据要求"]),
            }
        )
    result.sort(
        key=lambda row: (
            clean(row["源MAKE"]).casefold(),
            clean(row["源MODEL"]).casefold(),
            clean(row["版本"]).casefold(),
            clean(row["结构"]).casefold(),
            clean(row["候选Make"]).casefold(),
            clean(row["候选Model"]).casefold(),
        )
    )
    return result


def canonical_structure(value: object) -> str:
    text = normalized(value)
    groups = {
        "roadster": "convertible",
        "convertible": "convertible",
        "sportback": "liftback",
        "liftback": "liftback",
        "minivan": "mpv",
        "mpv": "mpv",
        "cuv": "crossover",
        "crossover": "crossover",
        "coupesuv": "suv",
        "suv": "suv",
    }
    return groups.get(text, text)


@dataclass(frozen=True)
class LogicalKey:
    year: int
    main_model: str
    structure: str
    version: str


@dataclass(frozen=True)
class Resolution:
    candidates: tuple[tuple[str, str], ...]
    method: str
    confidence: str
    note: str = ""


@dataclass
class BuildResult:
    trim_rows: list[dict[str, object]]
    audit_rows: list[dict[str, object]]
    unmapped_rows: list[dict[str, object]]
    conflict_rows: list[dict[str, object]]
    online_review_rows: list[dict[str, object]]
    report: dict[str, object]


class Resolver:
    def __init__(
        self,
        fitment_rows: list[dict[str, str]],
        maintenance_rows: list[dict[str, str]],
    ) -> None:
        self.fitment_set: set[tuple[int, str, str]] = set()
        self.fitment_by_year: dict[int, list[tuple[str, str]]] = defaultdict(list)
        for row in fitment_rows:
            try:
                year = int(row["year"])
            except (KeyError, TypeError, ValueError):
                continue
            value = (year, clean(row["make"]), clean(row["model"]))
            if not all(value) or value in self.fitment_set:
                continue
            self.fitment_set.add(value)
            self.fitment_by_year[year].append((value[1], value[2]))

        self.current_exact: dict[LogicalKey, tuple[tuple[str, str], ...]] = {}
        self.current_loose: dict[
            tuple[int, str, str], list[tuple[str, tuple[tuple[str, str], ...]]]
        ] = defaultdict(list)
        self.learned_signatures: dict[
            tuple[str, str], set[tuple[str, str]]
        ] = defaultdict(set)

        for row in maintenance_rows:
            try:
                year = int(row["Year"])
            except (KeyError, TypeError, ValueError):
                continue
            key = LogicalKey(
                year,
                clean(row["主车型"]),
                clean(row["结构"]),
                clean(row["版本"]),
            )
            candidates = tuple(split_candidates(row.get("候选车型", "")))
            self.current_exact[key] = candidates
            self.current_loose[
                (year, normalized(key.main_model), normalized(key.version))
            ].append((key.structure, candidates))
            for make, model in candidates:
                self.learned_signatures[
                    (normalized(key.main_model), normalized(key.version))
                ].add((normalized(make), normalized(model)))

    def valid_for_year(
        self, year: int, candidates: Iterable[tuple[str, str]]
    ) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted(
                {
                    candidate
                    for candidate in candidates
                    if (year, candidate[0], candidate[1]) in self.fitment_set
                },
                key=lambda item: (item[0].casefold(), item[1].casefold()),
            )
        )

    def named_candidates(
        self, year: int, make: str, model_names: Iterable[str]
    ) -> tuple[tuple[str, str], ...]:
        model_signatures = {normalized(value) for value in model_names}
        return tuple(
            candidate
            for candidate in self.fitment_by_year.get(year, [])
            if normalized(candidate[0]) == normalized(make)
            and normalized(candidate[1]) in model_signatures
        )

    def alias_resolution(
        self, key: LogicalKey, make: str
    ) -> Resolution | None:
        main = normalized(key.main_model)
        version = normalized(key.version)
        year = key.year
        aliases: list[str] = []
        note = ""

        if main == normalized("Chevrolet Malibu") and year <= 1977:
            aliases, note = ["Chevelle"], "早期 Malibu 按4A的 Chevelle 口径匹配"
        elif main == normalized("Chevrolet Nova") and year <= 1968:
            aliases, note = ["Chevy II"], "早期 Nova 按4A的 Chevy II 名称匹配"
        elif main == normalized("Chevrolet S-10 Blazer") and year >= 1995:
            aliases, note = ["Blazer"], "1995年后按4A的 Blazer 名称匹配"
        elif main == normalized("Ford Crown Victoria") and 1983 <= year <= 1988:
            aliases, note = ["LTD", "LTD Crown Victoria"], "按当年4A的LTD名称匹配"
        elif main == normalized("GMC Sierra 2500HD/3500HD"):
            aliases = (
                ["Sierra 3500", "Sierra 3500 HD"]
                if version == normalized("DRW")
                else ["Sierra 2500 HD", "Sierra 3500", "Sierra 3500 HD"]
            )
            note = "主表合并2500HD/3500HD，按当年4A实际车型展开"
        elif main == normalized("Jeep Wagoneer") and year == 1991:
            aliases, note = ["Grand Wagoneer"], "1991年按4A的 Grand Wagoneer 名称匹配"
        elif main == normalized("Land Rover Discovery") and 2010 <= year <= 2013:
            aliases, note = ["LR4"], "北美车型名按4A的 LR4 口径匹配"
        elif main == normalized("Lexus LX") and year == 2012:
            aliases, note = ["LX570"], "主表车系名 LX 按4A具体 Model 匹配"
        elif main == normalized("Lincoln Continental") and year in {1956, 1957}:
            aliases, note = ["Mark II"], "1956-1957按4A的 Mark II 名称匹配"
        elif main == normalized("Mercedes-Benz 190") and 1984 <= year <= 1993:
            aliases, note = ["190E"], "主表车系名190按4A具体Model匹配"
        elif main == normalized("Mercedes-Benz SL-Class") and key.version:
            aliases, note = [key.version], "SL-Class显式版本按4A具体Model匹配"
        elif main == normalized("MINI Clubman") and 2008 <= year <= 2014:
            aliases, note = ["Cooper"], "早期 Clubman 在4A中合并于 Cooper"
        elif main in {normalized("MINI Hardtop"), normalized("MINI Hatchback")}:
            aliases, note = ["Cooper"], "Hardtop/Hatchback在4A中合并于 Cooper"
        elif main == normalized("Nissan Armada") and year == 2004:
            aliases, note = ["Pathfinder Armada"], "2004首年按4A的 Pathfinder Armada 匹配"
        elif main == normalized("Subaru Outback Sport"):
            aliases, note = ["Impreza"], "Outback Sport按4A的Impreza口径匹配"
        elif main == normalized("Subaru Outback") and 1995 <= year <= 1999:
            aliases, note = ["Legacy"], "早期Outback按4A的Legacy口径匹配"
        elif main == normalized("Subaru Tribeca") and 2006 <= year <= 2007:
            aliases, note = ["B9 Tribeca"], "2006-2007按4A的B9 Tribeca名称匹配"
        elif main == normalized("Tesla Model Y L"):
            aliases, note = ["Y"], "Model Y L按4A的Y车型口径匹配"
        elif main == normalized("Toyota Supra") and 1979 <= year <= 1985:
            aliases, note = ["Celica"], "早期Supra按4A的Celica名称匹配"
        elif main == normalized("Volkswagen Passat") and 1974 <= year <= 1981:
            aliases, note = ["Dasher"], "北美早期Passat按4A的Dasher名称匹配"
        elif main == normalized("Volkswagen Passat") and 1982 <= year <= 1988:
            aliases, note = ["Quantum"], "北美早期Passat按4A的Quantum名称匹配"
        elif main == normalized("Mercedes-Benz S-Class") and key.version:
            aliases, note = [key.version.replace(" PHEV", "")], "S-Class显式版本按4A具体Model匹配"
        elif main == normalized("Chevrolet Avalanche") and version in {"1500", "2500"}:
            aliases, note = [f"Avalanche {key.version}"], "显式载重级别按4A具体Model匹配"

        if not aliases:
            return None
        candidates = self.named_candidates(year, make, aliases)
        if not candidates:
            return None
        return Resolution(candidates, "4A历史名称规则", "中", note)

    def resolve(self, key: LogicalKey, make: str, model: str) -> Resolution:
        exact = self.valid_for_year(key.year, self.current_exact.get(key, ()))
        if exact:
            return Resolution(exact, "继承现有精确键", "高")

        loose_entries = self.current_loose.get(
            (key.year, normalized(key.main_model), normalized(key.version)), []
        )
        same_family = [
            candidate
            for structure, candidates in loose_entries
            if canonical_structure(structure) == canonical_structure(key.structure)
            for candidate in candidates
        ]
        loose_family = self.valid_for_year(key.year, same_family)
        if loose_family:
            return Resolution(
                loose_family,
                "继承结构规范化键",
                "高",
                "结构名称按同义组规范化",
            )

        valid_signatures = {
            self.valid_for_year(key.year, candidates)
            for _, candidates in loose_entries
            if self.valid_for_year(key.year, candidates)
        }
        if len(valid_signatures) == 1:
            return Resolution(
                next(iter(valid_signatures)),
                "继承单一规范化键",
                "中",
                "同年同主车型同版本只有一组可验证候选",
            )

        learned = self.learned_signatures.get(
            (normalized(key.main_model), normalized(key.version)), set()
        )
        learned_matches = tuple(
            candidate
            for candidate in self.fitment_by_year.get(key.year, [])
            if (normalized(candidate[0]), normalized(candidate[1])) in learned
        )
        if learned_matches:
            return Resolution(
                learned_matches,
                "继承同车型跨年映射",
                "中",
                "候选签名来自现维护表的其他年份且当年4A存在",
            )

        direct = tuple(
            candidate
            for candidate in self.fitment_by_year.get(key.year, [])
            if normalized(candidate[0]) == normalized(make)
            and normalized(candidate[1]) == normalized(model)
        )
        if direct:
            return Resolution(
                direct,
                "4A品牌车型精确匹配",
                "高",
                "显式版本在4A未单列时按基础Model映射",
            )

        global_model = tuple(
            candidate
            for candidate in self.fitment_by_year.get(key.year, [])
            if normalized(candidate[1]) == normalized(model)
        )
        if len(global_model) == 1:
            return Resolution(
                global_model,
                "4A车型全局唯一匹配",
                "中",
                f"主表品牌为{make}，4A品牌为{global_model[0][0]}",
            )

        alias = self.alias_resolution(key, make)
        if alias:
            return alias

        reason = "当年4A中未找到可由现有映射、精确名称或已审核别名证明的候选"
        if len(valid_signatures) > 1:
            reason = "同年同主车型同版本存在多组结构候选，未自动跨结构合并"
        return Resolution((), "待人工核验", "待核", reason)


def load_overrides(path: Path | None) -> dict[tuple[str, int], list[dict[str, str]]]:
    if path is None or not path.exists():
        return {}
    rows = read_csv(path)
    if not rows:
        return {}
    missing = [column for column in OVERRIDE_HEADER if column not in rows[0]]
    if missing:
        raise ValueError(f"{path} 缺少字段: {', '.join(missing)}")
    result: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for line, row in enumerate(rows, start=2):
        if not any(row.values()):
            continue
        action = row["Action"].upper()
        if action not in {"ADD", "REMOVE", "CLEAR"}:
            raise ValueError(f"{path} 第{line}行 Action 无效: {row['Action']}")
        try:
            year = int(row["Year"])
        except ValueError as exc:
            raise ValueError(f"{path} 第{line}行 Year 无效: {row['Year']}") from exc
        if action in {"ADD", "REMOVE"} and not (row["Make"] and row["Model"]):
            raise ValueError(f"{path} 第{line}行 {action} 必须填写 Make/Model")
        row = dict(row)
        row["Action"] = action
        result[(row["DIMENSION-ID"], year)].append(row)
    return result


def load_online_evidence(
    path: Path | None,
) -> dict[tuple[str, int, str, str], dict[str, str]]:
    """Load manually reviewed web evidence keyed to one atomic 4A candidate."""
    if path is None or not path.exists():
        return {}
    rows = read_csv(path)
    if not rows:
        return {}
    missing = [column for column in ONLINE_EVIDENCE_HEADER if column not in rows[0]]
    if missing:
        raise ValueError(f"{path} 缺少字段: {', '.join(missing)}")

    result: dict[tuple[str, int, str, str], dict[str, str]] = {}
    for line, row in enumerate(rows, start=2):
        if not any(row.values()):
            continue
        try:
            year = int(row["Year"])
        except ValueError as exc:
            raise ValueError(f"{path} 第{line}行 Year 无效: {row['Year']}") from exc
        decision = row["Decision"].upper()
        if decision not in {"APPROVE", "REJECT"}:
            raise ValueError(f"{path} 第{line}行 Decision 必须为 APPROVE/REJECT")
        if not row["DIMENSION-ID"] or not row["Make"] or not row["Model"]:
            raise ValueError(f"{path} 第{line}行缺少 DIMENSION-ID/Make/Model")
        if decision == "APPROVE" and not re.match(
            r"^https?://", row["SourceURL"], flags=re.IGNORECASE
        ):
            raise ValueError(f"{path} 第{line}行 APPROVE 必须填写 http(s) 证据URL")
        key = (row["DIMENSION-ID"], year, row["Make"], row["Model"])
        if key in result:
            raise ValueError(f"{path} 第{line}行证据原子键重复: {key}")
        normalized_row = dict(row)
        normalized_row["Decision"] = decision
        result[key] = normalized_row
    return result


def apply_overrides(
    dimension_id: str,
    year: int,
    resolution: Resolution,
    override_index: dict[tuple[str, int], list[dict[str, str]]],
    fitment_set: set[tuple[int, str, str]],
) -> Resolution:
    actions = override_index.get((dimension_id, year), [])
    if not actions:
        return resolution

    candidates = set(resolution.candidates)
    notes = [resolution.note] if resolution.note else []
    for row in actions:
        action = row["Action"]
        candidate = (row["Make"], row["Model"])
        if action == "CLEAR":
            candidates.clear()
        elif action == "REMOVE":
            candidates.discard(candidate)
        elif action == "ADD":
            if (year, candidate[0], candidate[1]) not in fitment_set:
                raise ValueError(
                    f"例外 ADD 候选不在当年4A: {dimension_id}, {year}, "
                    f"{candidate[0]}|{candidate[1]}"
                )
            candidates.add(candidate)
        note = clean(row.get("Note"))
        if note:
            notes.append(f"{action}: {note}")

    return Resolution(
        tuple(sorted(candidates, key=lambda item: (item[0].casefold(), item[1].casefold()))),
        f"{resolution.method}+例外" if resolution.method else "例外",
        "人工核定",
        " | ".join(notes),
    )


def build_trimlist(
    dimension_rows: list[dict[str, str]],
    fitment_rows: list[dict[str, str]],
    maintenance_rows: list[dict[str, str]],
    override_rows: dict[tuple[str, int], list[dict[str, str]]] | None = None,
    online_evidence: dict[
        tuple[str, int, str, str], dict[str, str]
    ] | None = None,
) -> BuildResult:
    resolver = Resolver(fitment_rows, maintenance_rows)
    override_index = override_rows or {}
    evidence_index = online_evidence or {}
    evidence_by_dimension_year: dict[
        tuple[str, int], list[tuple[tuple[str, int, str, str], dict[str, str]]]
    ] = defaultdict(list)
    for evidence_key, evidence_row in evidence_index.items():
        evidence_by_dimension_year[(evidence_key[0], evidence_key[1])].append(
            (evidence_key, evidence_row)
        )

    dimension_ids = [row["DIMENSION-ID"] for row in dimension_rows]
    duplicate_dimension_ids = sorted(
        dimension_id
        for dimension_id, count in Counter(dimension_ids).items()
        if dimension_id and count > 1
    )
    if any(not value for value in dimension_ids):
        raise ValueError("车型尺寸库存在空 DIMENSION-ID")
    if duplicate_dimension_ids:
        raise ValueError(
            f"车型尺寸库存在重复 DIMENSION-ID: {duplicate_dimension_ids[:10]}"
        )

    dimension_year_keys: set[tuple[str, int]] = set()
    trim_rows: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    unmapped_rows: list[dict[str, object]] = []
    online_review_rows: list[dict[str, object]] = []
    method_counts: Counter[str] = Counter()
    published_method_counts: Counter[str] = Counter()
    exact_candidate_rows = 0
    online_approved_candidate_rows = 0
    generated_candidate_rows = 0
    used_evidence_keys: set[tuple[str, int, str, str]] = set()
    evidence_errors: list[str] = []

    for row in dimension_rows:
        dimension_id = row["DIMENSION-ID"]
        make = row["MAKE"]
        model = row["MODEL"]
        main_model = " ".join(value for value in (make, model) if value)
        years = expanded_years(row["YEAR"])
        if not years:
            raise ValueError(f"DIMENSION-ID 无法解析 YEAR: {dimension_id}, {row['YEAR']}")

        for year in years:
            dimension_year_keys.add((dimension_id, year))
            key = LogicalKey(year, main_model, row["结构"], row["版本"])
            base_resolution = resolver.resolve(key, make, model)
            exact_candidates = (
                set(base_resolution.candidates)
                if base_resolution.method == "继承现有精确键"
                else set()
            )
            resolution = apply_overrides(
                dimension_id,
                year,
                base_resolution,
                override_index,
                resolver.fitment_set,
            )
            method_counts[resolution.method] += 1

            resolution_candidates = set(resolution.candidates)
            evidence_candidates: set[tuple[str, str]] = set()
            for evidence_key, evidence_row in evidence_by_dimension_year.get(
                (dimension_id, year), []
            ):
                if evidence_row["Decision"] != "APPROVE":
                    continue
                candidate = (evidence_key[2], evidence_key[3])
                if (year, candidate[0], candidate[1]) not in resolver.fitment_set:
                    evidence_errors.append(
                        f"联网证据新增候选不在当年4A: {evidence_key}"
                    )
                    continue
                evidence_candidates.add(candidate)
            candidate_pool = resolution_candidates | evidence_candidates

            if not candidate_pool:
                unmapped_rows.append(
                    {
                        "DIMENSION-ID": dimension_id,
                        "Year": year,
                        "主车型": main_model,
                        "结构": row["结构"],
                        "版本": row["版本"],
                        "CAB": row.get("CAB", ""),
                        "BED": row.get("BED", ""),
                        "原因": resolution.note,
                    }
                )
                continue

            for candidate_make, candidate_model in sorted(
                candidate_pool,
                key=lambda item: (item[0].casefold(), item[1].casefold()),
            ):
                generated_candidate_rows += 1
                evidence_key = (dimension_id, year, candidate_make, candidate_model)
                evidence = evidence_index.get(evidence_key)
                is_exact_inherited = (candidate_make, candidate_model) in exact_candidates
                is_evidence_added = (
                    candidate_make,
                    candidate_model,
                ) not in resolution_candidates
                candidate_method = (
                    "联网证据新增候选" if is_evidence_added else resolution.method
                )
                approved = is_exact_inherited
                review_status = "现有精确键" if approved else "待联网审核"
                evidence_url = ""

                if not is_exact_inherited and evidence is not None:
                    used_evidence_keys.add(evidence_key)
                    if evidence["版本"] != row["版本"] or evidence["结构"] != row["结构"]:
                        review_status = "证据字段不匹配"
                        evidence_errors.append(
                            f"联网证据版本/结构与尺寸库不一致: {evidence_key}; "
                            f"证据=({evidence['版本']}, {evidence['结构']}), "
                            f"尺寸库=({row['版本']}, {row['结构']})"
                        )
                    elif evidence["Decision"] == "APPROVE":
                        approved = True
                        review_status = "联网证据批准"
                        evidence_url = evidence["SourceURL"]
                    else:
                        review_status = "联网证据拒绝"

                if not approved:
                    query_parts = [
                        str(year),
                        f'"{main_model}"',
                        f'"{candidate_make} {candidate_model}"',
                    ]
                    if row["版本"]:
                        query_parts.append(f'"{row["版本"]}"')
                    if row["结构"]:
                        query_parts.append(f'"{row["结构"]}"')
                    online_review_rows.append(
                        {
                            "DIMENSION-ID": dimension_id,
                            "Year": year,
                            "源MAKE": make,
                            "源MODEL": model,
                            "主车型": main_model,
                            "版本": row["版本"],
                            "结构": row["结构"],
                            "CAB": row.get("CAB", ""),
                            "BED": row.get("BED", ""),
                            "候选Make": candidate_make,
                            "候选Model": candidate_model,
                            "原匹配方式": candidate_method,
                            "审核状态": review_status,
                            "原因": resolution.note or "非现有精确键必须提供联网证据",
                            "建议搜索词": " ".join(query_parts),
                            "证据要求": "年份、Make、Model、版本、结构均与DIMENSION-ID语义一致",
                        }
                    )
                    continue

                trim = {
                    "DIMENSION-ID": dimension_id,
                    "Year": year,
                    "Make": candidate_make,
                    "Model": candidate_model,
                }
                trim_rows.append(trim)
                audit_rows.append(
                    {
                        **trim,
                        "主车型": main_model,
                        "结构": row["结构"],
                        "版本": row["版本"],
                        "CAB": row.get("CAB", ""),
                        "BED": row.get("BED", ""),
                        "匹配方式": candidate_method,
                        "置信度": "高" if is_evidence_added else resolution.confidence,
                        "说明": (
                            evidence.get("EvidenceNote", "")
                            if is_evidence_added and evidence
                            else resolution.note
                        ),
                        "审核状态": review_status,
                        "证据URL": evidence_url,
                    }
                )
                published_method_counts[candidate_method] += 1
                if is_exact_inherited:
                    exact_candidate_rows += 1
                else:
                    online_approved_candidate_rows += 1

    def trim_sort_key(item: dict[str, object]) -> tuple[object, ...]:
        return (
            clean(item["DIMENSION-ID"]),
            int(item["Year"]),
            clean(item["Make"]).casefold(),
            clean(item["Model"]).casefold(),
        )

    unique_trim: dict[tuple[str, int, str, str], dict[str, object]] = {}
    for row in trim_rows:
        key = (
            clean(row["DIMENSION-ID"]),
            int(row["Year"]),
            clean(row["Make"]),
            clean(row["Model"]),
        )
        unique_trim[key] = row
    trim_rows = sorted(unique_trim.values(), key=trim_sort_key)

    unique_audit: dict[tuple[str, int, str, str], dict[str, object]] = {}
    for row in audit_rows:
        key = (
            clean(row["DIMENSION-ID"]),
            int(row["Year"]),
            clean(row["Make"]),
            clean(row["Model"]),
        )
        unique_audit[key] = row
    audit_rows = sorted(unique_audit.values(), key=trim_sort_key)
    unmapped_rows.sort(key=lambda item: (clean(item["DIMENSION-ID"]), int(item["Year"])))
    online_review_rows.sort(
        key=lambda item: (
            clean(item["DIMENSION-ID"]),
            int(item["Year"]),
            clean(item["候选Make"]).casefold(),
            clean(item["候选Model"]).casefold(),
        )
    )

    fitment_to_dimensions: dict[tuple[int, str, str], set[str]] = defaultdict(set)
    for row in trim_rows:
        fitment_to_dimensions[
            (int(row["Year"]), clean(row["Make"]), clean(row["Model"]))
        ].add(clean(row["DIMENSION-ID"]))

    conflict_rows: list[dict[str, object]] = []
    for (year, make, model), ids in fitment_to_dimensions.items():
        if len(ids) <= 1:
            continue
        conflict_rows.append(
            {
                "Year": year,
                "Make": make,
                "Model": model,
                "DIMENSION-ID数量": len(ids),
                "DIMENSION-ID列表": "; ".join(sorted(ids)),
                "判定": "正常多分支展开",
            }
        )
    conflict_rows.sort(
        key=lambda item: (
            int(item["Year"]),
            clean(item["Make"]).casefold(),
            clean(item["Model"]).casefold(),
        )
    )

    output_keys = {
        (
            clean(row["DIMENSION-ID"]),
            int(row["Year"]),
            clean(row["Make"]),
            clean(row["Model"]),
        )
        for row in trim_rows
    }
    invalid_fitment = sorted(
        key
        for key in output_keys
        if (key[1], key[2], key[3]) not in resolver.fitment_set
    )
    out_of_range = sorted(
        (key[0], key[1])
        for key in output_keys
        if (key[0], key[1]) not in dimension_year_keys
    )
    covered_dimension_years = {(key[0], key[1]) for key in output_keys}
    unmapped_dimension_years = {
        (clean(row["DIMENSION-ID"]), int(row["Year"])) for row in unmapped_rows
    }
    pending_review_dimension_years = {
        (clean(row["DIMENSION-ID"]), int(row["Year"]))
        for row in online_review_rows
    }
    coverage_partition_ok = (
        covered_dimension_years
        | unmapped_dimension_years
        | pending_review_dimension_years
        == dimension_year_keys
        and not unmapped_dimension_years
        & (covered_dimension_years | pending_review_dimension_years)
    )
    orphan_override_keys = sorted(set(override_index) - dimension_year_keys)
    unused_evidence_keys = sorted(set(evidence_index) - used_evidence_keys)

    hard_errors: list[str] = []
    if invalid_fitment:
        hard_errors.append(f"输出中有 {len(invalid_fitment)} 条候选不在当年4A")
    if out_of_range:
        hard_errors.append(f"输出中有 {len(out_of_range)} 条年份超出 DIMENSION-ID 范围")
    if len(output_keys) != len(trim_rows):
        hard_errors.append("输出存在重复原子键")
    if not coverage_partition_ok:
        hard_errors.append("DIMENSION-ID 年份的已匹配/未匹配分区不完整")
    if orphan_override_keys:
        hard_errors.append(
            f"例外表有 {len(orphan_override_keys)} 个 DIMENSION-ID+年份不在尺寸库中"
        )
    hard_errors.extend(evidence_errors)

    report: dict[str, object] = {
        "schema_version": "3.0",
        "counts": {
            "dimension_rows": len(dimension_rows),
            "dimension_year_atoms": len(dimension_year_keys),
            "trim_rows": len(trim_rows),
            "mapped_dimension_year_atoms": len(covered_dimension_years),
            "unmapped_dimension_year_atoms": len(unmapped_dimension_years),
            "pending_online_review_dimension_year_atoms": len(
                pending_review_dimension_years
            ),
            "generated_candidate_rows_before_online_review": generated_candidate_rows,
            "published_exact_candidate_rows": exact_candidate_rows,
            "published_online_approved_candidate_rows": online_approved_candidate_rows,
            "pending_or_rejected_online_candidate_rows": len(online_review_rows),
            "unique_fitment_atoms": len(fitment_to_dimensions),
            "multi_dimension_fitment_expansions": len(conflict_rows),
        },
        "candidate_matching_methods": dict(method_counts.most_common()),
        "published_matching_methods": dict(published_method_counts.most_common()),
        "checks": {
            "dimension_ids_unique": not duplicate_dimension_ids,
            "all_candidates_exist_in_4a_year": not invalid_fitment,
            "all_years_within_dimension_range": not out_of_range,
            "trim_primary_key_unique": len(output_keys) == len(trim_rows),
            "coverage_partition_complete": coverage_partition_ok,
            "all_overrides_target_existing_dimension_year": not orphan_override_keys,
            "all_non_exact_published_have_online_evidence": all(
                row["审核状态"] in {"现有精确键", "联网证据批准"}
                for row in audit_rows
            ),
            "online_evidence_fields_match_dimension": not evidence_errors,
            "online_evidence_entries_target_current_candidates": not unused_evidence_keys,
        },
        "warnings": (
            [f"有 {len(unused_evidence_keys)} 条联网证据未命中当前候选"]
            if unused_evidence_keys
            else []
        ),
        "hard_errors": hard_errors,
    }

    return BuildResult(
        trim_rows=trim_rows,
        audit_rows=audit_rows,
        unmapped_rows=unmapped_rows,
        conflict_rows=conflict_rows,
        online_review_rows=online_review_rows,
        report=report,
    )


def build_files(
    dimensions_path: Path,
    fitment_path: Path,
    maintenance_path: Path,
    overrides_path: Path | None,
    online_evidence_path: Path | None,
    output_dir: Path,
) -> BuildResult:
    dimension_rows = read_csv(dimensions_path)
    fitment_rows = read_csv(fitment_path)
    maintenance_rows = read_csv(maintenance_path)

    require_columns(
        dimension_rows,
        ["DIMENSION-ID", "MAKE", "MODEL", "版本", "结构", "YEAR"],
        dimensions_path,
    )
    require_columns(fitment_rows, ["year", "make", "model"], fitment_path)
    require_columns(
        maintenance_rows,
        ["Year", "主车型", "结构", "版本", "候选车型"],
        maintenance_path,
    )

    overrides = load_overrides(overrides_path)
    online_evidence = load_online_evidence(online_evidence_path)
    result = build_trimlist(
        dimension_rows,
        fitment_rows,
        maintenance_rows,
        overrides,
        online_evidence,
    )
    result.report["sources"] = {
        "dimensions": {
            "path": str(dimensions_path),
            "sha256": sha256_file(dimensions_path),
        },
        "fitment": {
            "path": str(fitment_path),
            "sha256": sha256_file(fitment_path),
        },
        "maintenance": {
            "path": str(maintenance_path),
            "sha256": sha256_file(maintenance_path),
        },
        "overrides": (
            {
                "path": str(overrides_path),
                "sha256": sha256_file(overrides_path),
            }
            if overrides_path is not None and overrides_path.exists()
            else None
        ),
        "online_evidence": (
            {
                "path": str(online_evidence_path),
                "sha256": sha256_file(online_evidence_path),
            }
            if online_evidence_path is not None and online_evidence_path.exists()
            else None
        ),
    }
    if result.report["hard_errors"]:
        raise ValueError("\n".join(result.report["hard_errors"]))

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "TrimList.csv", TRIM_HEADER, result.trim_rows)
    write_csv(output_dir / "TrimList_audit.csv", AUDIT_HEADER, result.audit_rows)
    write_csv(output_dir / "TrimList_unmapped.csv", UNMAPPED_HEADER, result.unmapped_rows)
    write_csv(output_dir / "TrimList_conflicts.csv", CONFLICT_HEADER, result.conflict_rows)
    write_csv(
        output_dir / "TrimList_multi_dimension.csv",
        CONFLICT_HEADER,
        result.conflict_rows,
    )
    write_csv(
        output_dir / "TrimList_online_review.csv",
        ONLINE_REVIEW_HEADER,
        result.online_review_rows,
    )
    online_review_groups = group_online_review_rows(result.online_review_rows)
    result.report["counts"]["pending_online_review_groups"] = len(
        online_review_groups
    )
    write_csv(
        output_dir / "TrimList_online_review_groups.csv",
        ONLINE_REVIEW_GROUP_HEADER,
        online_review_groups,
    )
    with (output_dir / "validation_report.json").open("w", encoding="utf-8") as file:
        json.dump(result.report, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return result
