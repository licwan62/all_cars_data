"""找出 EU/RU 原始库中"裸 SUV"（未标注车门数）与"SUV 3-door"疑似重复抓取的候选。

背景：结构规范化（structure_normalization.json）默认把 3-door 当作省略的默认值，
所以"裸 SUV"和"SUV 3-door"理论上应该是同一种车身。但 00_<REGION>尺寸库.csv 里
两者经常都存在（同 MAKE+MODEL），且尺寸几乎一致，很可能是同一辆车被源站重复抓取
（一次标了门数、一次没标），而不是两种真实不同的车身。

只做报告，不自动合并——是否真的是同一车型需要人工确认后写入
data/identity_merge_rules.json（做法与已确认的 УАЗ Хантер 案例一致）。

用法：
    python code/find_bare_suv_duplicate_candidates.py --region ru
    python code/find_bare_suv_duplicate_candidates.py --region eu
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]


def latest_batch(region: str) -> Path:
    region_dir = PROJECT_DIR / "data" / region
    batches = sorted(path for path in region_dir.iterdir() if path.is_dir())
    if not batches:
        raise FileNotFoundError(f"data/{region} 下没有批次目录")
    return batches[-1]


def read_rows(region: str) -> list[dict]:
    path = latest_batch(region) / f"00_{region.upper()}尺寸库.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def relative_diff(a: str, b: str) -> float | None:
    try:
        a_value, b_value = float(a), float(b)
    except (TypeError, ValueError):
        return None
    if a_value == 0 and b_value == 0:
        return 0.0
    denominator = max(abs(a_value), abs(b_value)) or 1.0
    return abs(a_value - b_value) / denominator


def find_candidates(rows: list[dict], max_diff: float = 0.05) -> list[dict]:
    by_model: dict[tuple[str, str], dict[str, list[dict]]] = {}
    for row in rows:
        structure = (row.get("结构") or "").strip()
        if structure not in ("SUV", "SUV 3-door"):
            continue
        key = ((row.get("MAKE") or "").strip(), (row.get("MODEL") or "").strip())
        by_model.setdefault(key, {"SUV": [], "SUV 3-door": []})[structure].append(row)

    candidates: list[dict] = []
    for (make, model), groups in by_model.items():
        for bare in groups["SUV"]:
            for three_door in groups["SUV 3-door"]:
                diffs = {
                    axis: relative_diff(bare.get(column, ""), three_door.get(column, ""))
                    for axis, column in (("L", "L-IN"), ("W", "W-IN"), ("H", "H-IN"))
                }
                if any(value is None for value in diffs.values()):
                    continue
                max_observed = max(diffs.values())
                if max_observed > max_diff:
                    continue
                candidates.append(
                    {
                        "MAKE": make, "MODEL": model,
                        "裸SUV-DIMENSION-ID": bare.get("DIMENSION-ID", ""), "裸SUV-年份": bare.get("YEAR", ""),
                        "3door-DIMENSION-ID": three_door.get("DIMENSION-ID", ""), "3door-年份": three_door.get("YEAR", ""),
                        "L差异%": round(diffs["L"] * 100, 2), "W差异%": round(diffs["W"] * 100, 2),
                        "H差异%": round(diffs["H"] * 100, 2), "最大差异%": round(max_observed * 100, 2),
                        "建议": "疑似重复抓取，人工确认后写入 identity_merge_rules.json" if max_observed <= 0.02 else "尺寸接近，建议人工复核",
                    }
                )
    candidates.sort(key=lambda item: item["最大差异%"])
    return candidates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", choices=("eu", "ru"), required=True)
    parser.add_argument("--max-diff", type=float, default=0.05, help="L/W/H 相对差异阈值（默认 5%%）")
    parser.add_argument(
        "--output", type=Path, default=None,
        help="默认写入 data/<REGION>裸SUV疑似重复候选.csv",
    )
    args = parser.parse_args(argv)

    rows = read_rows(args.region)
    candidates = find_candidates(rows, args.max_diff)
    output = args.output or PROJECT_DIR / "data" / f"{args.region.upper()}裸SUV疑似重复候选.csv"
    fields = [
        "MAKE", "MODEL", "裸SUV-DIMENSION-ID", "裸SUV-年份", "3door-DIMENSION-ID", "3door-年份",
        "L差异%", "W差异%", "H差异%", "最大差异%", "建议",
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(candidates)
    print(f"{args.region.upper()}: {len(candidates)} 个候选，写入 {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
