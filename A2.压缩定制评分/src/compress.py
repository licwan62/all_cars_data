"""按匹配尺码把 A1 全量表的年份和结构压缩为池子。

核心思路（简化自 compress_to_size_chart/process_tsv.py，去掉了该项目里皮卡专属的
CAB/BED 特殊合并规则，改为把 结构+CAB+BED 一起当作"变体"参与池化）：

1. 把每一行的 YEAR 区间（如 "2018-2021"）展开为逐年原子事实
   (区域, MAKE, MODEL, 变体=(结构,CAB,BED), 年份, 尺码)。
2. 同一 (区域,MAKE,MODEL,变体,年份) 若来自多行且尺码不一致，按多数票取值，
   少数派记入冲突报告（不静默丢弃）。
3. 同一 (区域,MAKE,MODEL,年份) 内，把尺码相同的变体归并为一个"结构池"。
4. 结构池组合（年份签名）在相邻年份间完全相同时，合并为一个年份区间；
   年份不连续（数据未覆盖的年份）不跨越合并，避免虚报覆盖范围。

不确定/待人工复核的地方：
- 尺码字段固定用 "自动尺码"（100% 覆盖），"发货尺码"/"OZON尺码" 覆盖率低，
  仅在原表中留存，不参与池化匹配。可在 data/压缩配置.json 调整。
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, NamedTuple

REGION_SUFFIXES = ("US", "EU", "RU")
YEAR_RANGE_RE = re.compile(r"^(\d{4})-(\d{4})$")
DEFAULT_SIZE_FIELD = "自动尺码"


class Variant(NamedTuple):
    structure: str
    cab: str
    bed: str

    def label(self) -> str:
        parts = [part for part in (self.structure, self.cab, self.bed) if part]
        return "/".join(parts) if parts else self.structure


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


def _signature(pools: dict[str, list[Variant]]) -> tuple:
    return tuple(sorted((size, tuple(sorted(variants))) for size, variants in pools.items()))


def compress(rows: Iterable[dict], size_field: str = DEFAULT_SIZE_FIELD) -> tuple[list[dict], dict]:
    atoms, skipped = explode_atoms(rows, size_field)
    resolved, conflicts = resolve_conflicts(atoms)

    by_model_year: dict[tuple, dict[int, dict[str, list[Variant]]]] = {}
    for (region, make, model, variant, year), size in resolved.items():
        year_pools = by_model_year.setdefault((region, make, model), {}).setdefault(year, {})
        year_pools.setdefault(size, []).append(variant)

    compressed: list[dict] = []
    for (region, make, model), year_map in by_model_year.items():
        years = sorted(year_map)
        run_start = years[0]
        run_signature = _signature(year_map[run_start])
        previous_year = run_start

        def flush(start: int, end: int, signature: tuple) -> None:
            for size, variants in signature:
                compressed.append(
                    {
                        "区域": region, "MAKE": make, "MODEL": model,
                        "结构池": "; ".join(v.label() for v in variants),
                        "年份区间": f"{start}-{end}", "自动尺码": size,
                        "变体数": len(variants), "覆盖原子数": len(variants) * (end - start + 1),
                    }
                )

        for year in years[1:]:
            signature = _signature(year_map[year])
            if year == previous_year + 1 and signature == run_signature:
                previous_year = year
                continue
            flush(run_start, previous_year, run_signature)
            run_start, run_signature, previous_year = year, signature, year
        flush(run_start, previous_year, run_signature)

    compressed.sort(key=lambda row: (row["区域"], row["MAKE"], row["MODEL"], row["年份区间"], row["自动尺码"]))
    report = {
        "原子事实数": len(atoms),
        "跳过行数": len(skipped),
        "冲突数": len(conflicts),
        "压缩后行数": len(compressed),
    }
    return compressed, {"report": report, "skipped": skipped, "conflicts": conflicts}
