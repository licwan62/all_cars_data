"""按匹配尺码把 A1 全量表的年份和结构压缩为池子。

1. 把每一行的 YEAR 区间展开为逐年原子事实
   (区域, MAKE, MODEL, 变体=(结构,CAB,BED), 年份, 尺码)；同一变体同一年份多个候选尺码时
   按多数票取值，少数派记入冲突报告。
2. 无损压缩：每个变体独立地把尺码相同的连续年份合并为区间，再把同一车型内
   区间与尺码完全相同的变体归并为一个结构池。不制造原表不存在的原子事实。
3. 有损压缩：在无损结果上，同一车型内尺码相同、年份相距不超过 最大年份空洞 的两行
   合并为“变体并集 × 年份并集”。合并后的行不得与其他行重叠，也不得覆盖尺码不同的
   真实原子事实，因此每条原子事实仍唯一对应正确尺码；新增覆盖的不存在组合记为扩张原子。
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, NamedTuple

REGION_SUFFIXES = ("US", "EU", "RU")
YEAR_RANGE_RE = re.compile(r"^(\d{4})-(\d{4})$")
DEFAULT_SIZE_FIELD = "自动尺码"
DEFAULT_MAX_GAP_YEARS = 3


class Variant(NamedTuple):
    structure: str
    cab: str
    bed: str

    def label(self) -> str:
        parts = [part for part in (self.structure, self.cab, self.bed) if part]
        return "/".join(parts) if parts else self.structure


class Block(NamedTuple):
    variants: frozenset
    start: int
    end: int
    size: str

    def area(self) -> int:
        return len(self.variants) * (self.end - self.start + 1)

    def overlaps(self, other: "Block") -> bool:
        return (
            bool(self.variants & other.variants)
            and self.start <= other.end
            and other.start <= self.end
        )


def region_of(dimension_id: str) -> str:
    token = dimension_id.rsplit(" ", 1)[-1] if dimension_id else ""
    return token if token in REGION_SUFFIXES else ""


def parse_year_range(value: str) -> range | None:
    match = YEAR_RANGE_RE.match(value.strip()) if value else None
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    if start > end:
        start, end = end, start
    return range(start, end + 1)


def explode_atoms(rows: Iterable[dict], size_field: str = DEFAULT_SIZE_FIELD) -> tuple[list[tuple], list[dict]]:
    """返回 (原子事实列表, 跳过行的原因记录)。"""
    atoms: list[tuple] = []
    skipped: list[dict] = []
    for row in rows:
        size = (row.get(size_field) or "").strip()
        make, model = (row.get("MAKE") or "").strip(), (row.get("MODEL") or "").strip()
        if not size or not make or not model:
            skipped.append({"reason": f"缺少 {size_field}/MAKE/MODEL", "row": row.get("DIMENSION-ID", "")})
            continue
        year_range = parse_year_range(row.get("YEAR") or "")
        if year_range is None:
            skipped.append({"reason": "YEAR 区间无法解析", "row": row.get("DIMENSION-ID", "")})
            continue
        region = region_of(row.get("DIMENSION-ID") or "")
        variant = Variant(
            (row.get("结构") or "").strip(), (row.get("CAB") or "").strip(), (row.get("BED") or "").strip()
        )
        for year in year_range:
            atoms.append((region, make, model, variant, year, size))
    return atoms, skipped


def resolve_conflicts(atoms: list[tuple]) -> tuple[dict, list[dict]]:
    """同一 (区域,MAKE,MODEL,变体,年份) 多个候选尺码时按多数票取值。"""
    votes: dict[tuple, Counter] = {}
    for region, make, model, variant, year, size in atoms:
        key = (region, make, model, variant, year)
        votes.setdefault(key, Counter())[size] += 1
    resolved: dict[tuple, str] = {}
    conflicts: list[dict] = []
    for key, counter in votes.items():
        size, _ = counter.most_common(1)[0]
        resolved[key] = size
        if len(counter) > 1:
            region, make, model, variant, year = key
            conflicts.append(
                {
                    "区域": region, "MAKE": make, "MODEL": model, "结构": variant.label(), "年份": year,
                    "候选尺码": dict(counter), "采用": size,
                }
            )
    return resolved, conflicts


def group_by_model(resolved: dict) -> dict[tuple, dict[tuple, str]]:
    """{(区域,MAKE,MODEL): {(变体,年份): 尺码}}"""
    models: dict[tuple, dict[tuple, str]] = {}
    for (region, make, model, variant, year), size in resolved.items():
        models.setdefault((region, make, model), {})[(variant, year)] = size
    return models


def lossless_blocks(facts: dict[tuple, str]) -> list[Block]:
    by_variant: dict[Variant, dict[int, str]] = {}
    for (variant, year), size in facts.items():
        by_variant.setdefault(variant, {})[year] = size
    runs: dict[tuple, set] = {}
    for variant, year_sizes in by_variant.items():
        years = sorted(year_sizes)
        start = previous = years[0]
        for year in years[1:] + [None]:
            if year is not None and year == previous + 1 and year_sizes[year] == year_sizes[start]:
                previous = year
                continue
            runs.setdefault((start, previous, year_sizes[start]), set()).add(variant)
            if year is not None:
                start = previous = year
    return [Block(frozenset(variants), start, end, size) for (start, end, size), variants in runs.items()]


def _merge_allowed(candidate: Block, others: list[Block], facts: dict[tuple, str]) -> bool:
    if any(candidate.overlaps(other) for other in others):
        return False
    for variant in candidate.variants:
        for year in range(candidate.start, candidate.end + 1):
            size = facts.get((variant, year))
            if size is not None and size != candidate.size:
                return False
    return True


def lossy_blocks(facts: dict[tuple, str], blocks: list[Block], max_gap_years: int) -> list[Block]:
    blocks = list(blocks)
    while True:
        best: tuple | None = None
        for i, left in enumerate(blocks):
            for j in range(i + 1, len(blocks)):
                right = blocks[j]
                if left.size != right.size:
                    continue
                gap = max(left.start, right.start) - min(left.end, right.end) - 1
                if gap > max_gap_years:
                    continue
                candidate = Block(
                    left.variants | right.variants, min(left.start, right.start), max(left.end, right.end), left.size
                )
                expansion = candidate.area() - left.area() - right.area()
                key = (expansion, candidate.start, sorted(v.label() for v in candidate.variants))
                if best is not None and key >= best[0]:
                    continue
                others = [block for index, block in enumerate(blocks) if index not in (i, j)]
                if _merge_allowed(candidate, others, facts):
                    best = (key, i, j, candidate)
        if best is None:
            return blocks
        _, i, j, candidate = best
        blocks = [block for index, block in enumerate(blocks) if index not in (i, j)] + [candidate]


def _real_atoms(block: Block, facts: dict[tuple, str]) -> int:
    return sum(
        1 for variant in block.variants for year in range(block.start, block.end + 1) if (variant, year) in facts
    )


def _short_year_ranges(years: list[int]) -> str:
    """把缺失年份压成 ``24-25`` 形式，多个不连续区间用 ``/`` 分隔。"""
    if not years:
        return ""
    ranges: list[tuple[int, int]] = []
    start = previous = years[0]
    for year in years[1:]:
        if year == previous + 1:
            previous = year
            continue
        ranges.append((start, previous))
        start = previous = year
    ranges.append((start, previous))

    def short(year: int) -> str:
        return f"{year % 100:02d}"

    return "/".join(short(start) if start == end else f"{short(start)}-{short(end)}" for start, end in ranges)


def _expansion_atoms(block: Block, facts: dict[tuple, str]) -> str:
    """列出有损块新增代表的、不存在于上游原子事实中的结构和年份。"""
    expanded: list[str] = []
    show_variant = len(block.variants) > 1
    for variant in sorted(block.variants, key=lambda item: item.label()):
        missing = [
            year for year in range(block.start, block.end + 1)
            if (variant, year) not in facts
        ]
        ranges = _short_year_ranges(missing)
        if not ranges:
            continue
        prefix = f"{variant.label().lower()}_" if show_variant else ""
        expanded.append(f"{prefix}{ranges}")
    return "; ".join(expanded)


def _to_rows(model_key: tuple, blocks: list[Block], facts: dict[tuple, str], with_expansion: bool) -> list[dict]:
    region, make, model = model_key
    rows = []
    for block in blocks:
        real = _real_atoms(block, facts)
        row = {
            "区域": region, "MAKE": make, "MODEL": model,
            "结构池": "; ".join(sorted(v.label() for v in block.variants)),
            "年份区间": f"{block.start}-{block.end}", "自动尺码": block.size,
            "变体数": len(block.variants), "覆盖原子数": real,
        }
        if with_expansion:
            row["扩张原子数"] = block.area() - real
            row["扩张原子"] = _expansion_atoms(block, facts)
        rows.append(row)
    return rows


def check_atoms(facts_by_model: dict[tuple, dict[tuple, str]], blocks_by_model: dict[tuple, list[Block]]) -> dict:
    """每条原子事实必须恰好命中一行且尺码一致。"""
    unmatched, multiple, wrong = [], [], []
    for model_key, facts in facts_by_model.items():
        blocks = blocks_by_model.get(model_key, [])
        for (variant, year), size in facts.items():
            hits = [b for b in blocks if variant in b.variants and b.start <= year <= b.end]
            sample = {"车型": list(model_key), "结构": variant.label(), "年份": year, "尺码": size}
            if not hits:
                unmatched.append(sample)
            elif len(hits) > 1:
                multiple.append(sample)
            elif hits[0].size != size:
                wrong.append({**sample, "命中尺码": hits[0].size})
    return {
        "通过": not (unmatched or multiple or wrong),
        "未命中": len(unmatched), "重复命中": len(multiple), "尺码不一致": len(wrong),
        "示例": (unmatched + multiple + wrong)[:20],
    }


def _sort_rows(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda row: (row["区域"], row["MAKE"], row["MODEL"], row["年份区间"], row["自动尺码"], row["结构池"]))


def compress_all(
    rows: Iterable[dict], size_field: str = DEFAULT_SIZE_FIELD, max_gap_years: int = DEFAULT_MAX_GAP_YEARS
) -> dict:
    atoms, skipped = explode_atoms(rows, size_field)
    resolved, conflicts = resolve_conflicts(atoms)
    facts_by_model = group_by_model(resolved)
    lossless_by_model = {key: lossless_blocks(facts) for key, facts in facts_by_model.items()}
    lossy_by_model = {
        key: lossy_blocks(facts_by_model[key], blocks, max_gap_years) for key, blocks in lossless_by_model.items()
    }
    lossless = _sort_rows([r for key, b in lossless_by_model.items() for r in _to_rows(key, b, facts_by_model[key], False)])
    lossy = _sort_rows([r for key, b in lossy_by_model.items() for r in _to_rows(key, b, facts_by_model[key], True)])
    report = {
        "原子事实数": len(atoms),
        "去重原子事实数": len(resolved),
        "跳过行数": len(skipped),
        "冲突数": len(conflicts),
        "无损压缩行数": len(lossless),
        "有损压缩行数": len(lossy),
        "有损扩张原子数": sum(row["扩张原子数"] for row in lossy),
        "有损最大年份空洞": max_gap_years,
    }
    return {
        "lossless": lossless,
        "lossy": lossy,
        "report": report,
        "skipped": skipped,
        "conflicts": conflicts,
        "check": {
            "无损": check_atoms(facts_by_model, lossless_by_model),
            "有损": check_atoms(facts_by_model, lossy_by_model),
        },
    }


def compress(rows: Iterable[dict], size_field: str = DEFAULT_SIZE_FIELD) -> tuple[list[dict], dict]:
    """无损压缩（兼容旧接口）。"""
    result = compress_all(rows, size_field)
    return result["lossless"], {"report": result["report"], "skipped": result["skipped"], "conflicts": result["conflicts"]}
