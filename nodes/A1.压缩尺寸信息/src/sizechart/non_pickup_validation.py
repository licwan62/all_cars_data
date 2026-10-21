from __future__ import annotations

import re
import unicodedata
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import lru_cache

import pandas as pd


@dataclass(frozen=True)
class MergeRules:
    """高度压缩两两合并的扩张约束（节点 data/合并规则.yaml）。

    max_gap_years：合并记录的年份区间内，连续无原子（同车型、同车身/驾驶室范围）的年数上限；None 不限。
    gap_exempt_sizes：不受空档限制的尺码（如“无可用尺码”，店铺页不展示）。
    """

    max_gap_years: int | None = None
    gap_exempt_sizes: frozenset[str] = frozenset()

    def gap_reason(self, size: str, years: Iterable[int], has_atom: Callable[[int], bool]) -> str:
        if self.max_gap_years is None or size in self.gap_exempt_sizes:
            return ""
        years = sorted(years)
        if not years:
            return ""
        longest = current = 0
        for year in range(years[0], years[-1] + 1):
            current = 0 if has_atom(year) else current + 1
            longest = max(longest, current)
        if longest > self.max_gap_years:
            return f"候选年份区间跨越 {longest} 年无原子空档（上限 {self.max_gap_years}）"
        return ""


def normalize_text(value: object) -> str:
    if isinstance(value, str):
        return _normalize_str(value)
    if pd.isna(value):
        return ""
    return _normalize_str(str(value))


@lru_cache(maxsize=1 << 20)
def _normalize_str(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
    return text.strip()


def to_int(value: object) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        match = re.search(r"\d{4}", text)
        return int(match.group(0)) if match else None


def parse_year_list(value: object) -> list[int]:
    text = normalize_text(value).replace("，", "/").replace(",", "/").replace(";", "/")
    years: list[int] = []
    for part in text.split("/"):
        part = normalize_text(part)
        if not part:
            continue
        pieces = [item.strip() for item in part.split("-")]
        start = to_int(pieces[0]) if pieces else None
        end = to_int(pieces[1]) if len(pieces) >= 2 else start
        if start is None or end is None:
            continue
        lo, hi = sorted((start, end))
        years.extend(range(lo, hi + 1))
    return sorted(set(years))


def split_output_tokens(value: object) -> set[str]:
    text = normalize_text(value)
    if not text:
        return set()
    return {part for part in (normalize_text(item) for item in text.split("/")) if part}


def split_version_tokens(value: object) -> list[str]:
    text = normalize_text(value)
    if not text:
        return []
    text = re.sub(r"\b(?:INCL|Incl|incl|EXCL|Excl|excl|EXP|Exp|exp)\s*:", "", text)
    text = re.sub(r"\b([A-Za-z])\s*/\s*([A-Za-z])\b", r"\1__VERSION_SLASH__\2", text)
    result: list[str] = []
    seen: set[str] = set()
    for part in text.split("/"):
        version = normalize_text(part).replace("__VERSION_SLASH__", "/")
        if version and version not in seen:
            seen.add(version)
            result.append(version)
    return result


def record_version_matches(record_version: object, atom_version: object) -> bool:
    record_text = normalize_text(record_version)
    atom_text = normalize_text(atom_version)
    if not record_text:
        return atom_text == ""
    atom_tokens = set(split_version_tokens(atom_text))
    lower = record_text.lower()
    if lower.startswith("incl:"):
        tokens = set(split_version_tokens(record_text))
        return atom_text == "" or atom_text in tokens or bool(atom_tokens & tokens)
    tokens = set(split_version_tokens(record_text))
    return atom_text in tokens or bool(atom_tokens & tokens)


def split_model_expression(value: object) -> list[str]:
    text = normalize_text(value)
    if not text:
        return []
    result: list[str] = []
    seen: set[str] = set()
    for part in text.split("/"):
        model = normalize_text(part)
        if model and model not in seen:
            seen.add(model)
            result.append(model)
    return result


def model_expression_matches(record_model: object, atom_model: object) -> bool:
    if normalize_text(record_model) == normalize_text(atom_model):
        return True
    models = split_model_expression(record_model)
    atom = normalize_text(atom_model)
    return atom in models if models else atom == ""


def row_value(row: pd.Series, *columns: str) -> object:
    for column in columns:
        if column in row.index:
            return row.get(column, "")
    return ""


def atom_year_value(atom: pd.Series) -> int | None:
    value = row_value(atom, "YEAR_SINGLE", "YEAR")
    return to_int(value)


def record_years(record: pd.Series) -> set[int]:
    if "year_start" in record.index and "year_end" in record.index:
        start = to_int(record.get("year_start", ""))
        end = to_int(record.get("year_end", ""))
        if start is not None and end is not None:
            lo, hi = sorted((start, end))
            return set(range(lo, hi + 1))
    return set(parse_year_list(row_value(record, "YEAR")))


def non_pickup_record_matches_atom_size(record: pd.Series, atom: pd.Series) -> str | None:
    if normalize_text(row_value(record, "BRAND", "MAKE")) != normalize_text(row_value(atom, "BRAND", "MAKE")):
        return None
    if not model_expression_matches(row_value(record, "MODEL"), row_value(atom, "MODEL")):
        return None

    atom_year = atom_year_value(atom)
    if atom_year is None or atom_year not in record_years(record):
        return None

    record_consts = split_output_tokens(row_value(record, "CONST")) or split_output_tokens(row_value(record, "RAW-CONST"))
    atom_const = normalize_text(row_value(atom, "Const", "CONST"))
    if record_consts and atom_const not in record_consts:
        return None

    if not record_version_matches(row_value(record, "VERSION"), row_value(atom, "VERSION_RAW", "VERSION")):
        return None
    return normalize_text(row_value(record, "BACKSIZE"))


def non_pickup_atom_matches(records: pd.DataFrame, atom: pd.Series) -> list[tuple[object, str]]:
    matches: list[tuple[object, str]] = []
    for record_index, record in records.iterrows():
        size = non_pickup_record_matches_atom_size(record, atom)
        if size:
            matches.append((record_index, size))
    return matches


def non_pickup_candidate_validation_reason(records: pd.DataFrame, atoms: pd.DataFrame) -> str:
    for _, atom in atoms.iterrows():
        matches = non_pickup_atom_matches(records, atom)
        matched_sizes = [size for _, size in matches]
        atom_brand = normalize_text(row_value(atom, "BRAND", "MAKE"))
        atom_model = normalize_text(row_value(atom, "MODEL"))
        atom_year = atom_year_value(atom)
        atom_const = normalize_text(row_value(atom, "Const", "CONST"))
        atom_size = normalize_text(row_value(atom, "BackSize", "BACKSIZE"))
        # 多条记录命中同一原子只要尺码都一致就不算冲突（冗余而非矛盾），允许积极合并。
        if not matched_sizes:
            return f"{atom_brand} {atom_model} {atom_year} {atom_const} 原子事实未被候选记录覆盖"
        wrong = next((size for size in matched_sizes if size != atom_size), None)
        if wrong is not None:
            return f"{atom_brand} {atom_model} {atom_year} 命中尺码 {wrong} != 原子尺码 {atom_size}"
    return ""


def non_pickup_atoms_in_record_scope(atoms: pd.DataFrame, record: pd.Series | dict[str, object]) -> pd.DataFrame:
    scoped_indexes: list[object] = []
    record_series = record if isinstance(record, pd.Series) else pd.Series(record)
    for atom_index, atom in atoms.iterrows():
        if non_pickup_record_matches_atom_size(record_series, atom):
            scoped_indexes.append(atom_index)
    return atoms.loc[scoped_indexes]


def _first_value(row: object, *columns: str) -> object:
    """与 row_value 相同，但同时支持 dict 和 Series。"""
    keys = row.index if isinstance(row, pd.Series) else row
    for column in columns:
        if column in keys:
            return row.get(column, "")
    return ""


def record_profile(record: object) -> tuple:
    """把 non_pickup_record_matches_atom_size 用到的记录字段预先解析成可哈希元组。"""
    model = _first_value(record, "MODEL")
    keys = record.index if isinstance(record, pd.Series) else record
    years: set[int] | None = None
    if "year_start" in keys and "year_end" in keys:
        start = to_int(record.get("year_start", ""))
        end = to_int(record.get("year_end", ""))
        if start is not None and end is not None:
            lo, hi = sorted((start, end))
            years = set(range(lo, hi + 1))
    if years is None:
        years = set(parse_year_list(_first_value(record, "YEAR")))
    consts = split_output_tokens(_first_value(record, "CONST")) or split_output_tokens(_first_value(record, "RAW-CONST"))
    version = normalize_text(_first_value(record, "VERSION"))
    return (
        normalize_text(_first_value(record, "BRAND", "MAKE")),
        normalize_text(model),
        tuple(split_model_expression(model)),
        frozenset(years),
        frozenset(consts),
        version,
        version.lower().startswith("incl:"),
        frozenset(split_version_tokens(version)),
        normalize_text(_first_value(record, "BACKSIZE")),
    )


def atom_profile(atom: object) -> tuple:
    version = normalize_text(_first_value(atom, "VERSION_RAW", "VERSION"))
    return (
        normalize_text(_first_value(atom, "BRAND", "MAKE")),
        normalize_text(_first_value(atom, "MODEL")),
        to_int(_first_value(atom, "YEAR_SINGLE", "YEAR")),
        normalize_text(_first_value(atom, "Const", "CONST")),
        version,
        frozenset(split_version_tokens(version)),
        normalize_text(_first_value(atom, "BackSize", "BACKSIZE")),
    )


def profile_matches(record: tuple, atom: tuple) -> bool:
    """等价于 bool(non_pickup_record_matches_atom_size(record, atom))。"""
    brand, model, models, years, consts, version, incl, version_tokens, size = record
    atom_brand, atom_model, atom_year, atom_const, atom_version, atom_tokens, _ = atom
    if not size or brand != atom_brand:
        return False
    if model != atom_model and (atom_model not in models if models else atom_model != ""):
        return False
    if atom_year is None or atom_year not in years:
        return False
    if consts and atom_const not in consts:
        return False
    if not version:
        return atom_version == ""
    if incl and atom_version == "":
        return True
    return atom_version in version_tokens or bool(atom_tokens & version_tokens)


class NonPickupMergeValidator:
    """两两合并的增量校验，尺码判定与
    non_pickup_candidate_validation_reason(candidate, non_pickup_atoms_in_record_scope(atoms, merged)) 一致：
    合并记录命中的每个原子尺码都必须等于合并尺码；其余记录同尺码的重复命中不算冲突，故只需看合并记录范围内的原子。
    另要求左右两条原来命中的原子仍被合并记录覆盖（版本串拼接可能改变切分，如 m/m 与 m high），
    并按 MergeRules 限制合并记录跨越的无原子年份空档。"""

    def __init__(self, atoms: list[dict[str, object]], rules: MergeRules | None = None) -> None:
        self.atoms = [atom_profile(atom) for atom in atoms]
        self.rules = rules or MergeRules()
        self._atoms_by_year: dict[int, list[int]] = {}
        for index, atom in enumerate(self.atoms):
            if atom[2] is not None:
                self._atoms_by_year.setdefault(atom[2], []).append(index)
        self._matched_cache: dict[tuple, tuple[int, ...]] = {}
        self.record_sets: list[frozenset[int]] = []

    def matched_atoms(self, record: object) -> tuple[int, ...]:
        """记录命中（带非空尺码）的原子下标，按原子顺序。"""
        profile = record_profile(record)
        cached = self._matched_cache.get(profile)
        if cached is None:
            candidates = sorted(
                index for year in profile[3] for index in self._atoms_by_year.get(year, ())
            )
            cached = tuple(index for index in candidates if profile_matches(profile, self.atoms[index]))
            self._matched_cache[profile] = cached
        return cached

    def reset(self, records: list[dict[str, object]]) -> None:
        self.record_sets = [frozenset(self.matched_atoms(record)) for record in records]

    def _has_scope_atom(self, brand: str, models: frozenset[str], consts: frozenset[str], year: int) -> bool:
        return any(
            atom[0] == brand and atom[1] in models and (not consts or atom[3] in consts)
            for atom in (self.atoms[index] for index in self._atoms_by_year.get(year, ()))
        )

    def merge_reason(self, left_index: int, right_index: int, merged: dict[str, object]) -> str:
        scoped = self.matched_atoms(merged)
        if not scoped:
            return "候选合并范围内没有可验证原子事实"
        merged_size = normalize_text(_first_value(merged, "BACKSIZE"))
        for index in scoped:
            atom_brand, atom_model, atom_year, _atom_const, _, _, atom_size = self.atoms[index]
            if merged_size != atom_size:
                return f"{atom_brand} {atom_model} {atom_year} 命中尺码 {merged_size} != 原子尺码 {atom_size}"
        lost = (self.record_sets[left_index] | self.record_sets[right_index]) - set(scoped)
        if lost:
            atom_brand, atom_model, atom_year, atom_const, *_ = self.atoms[min(lost)]
            return f"{atom_brand} {atom_model} {atom_year} {atom_const} 原子事实未被候选记录覆盖"
        brand, model, models, years, consts, *_ = record_profile(merged)
        names = frozenset(models) | {model}
        return self.rules.gap_reason(merged_size, years, lambda year: self._has_scope_atom(brand, names, consts, year))
