from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone

import shape_project as project


AUDIT = project.PROJECT / "artifacts" / "all_dimension_shape_audit_2026-08-25.csv"
SUMMARY = project.PROJECT / "artifacts" / "all_dimension_shape_audit_2026-08-25.json"
AUDIT_FIELDS = [
    "DIMENSION-ID", "MAKE", "MODEL", "代际", "YEAR", "结构", "车形",
    "2000年前记录", "最高优先级判定", "缓存层级", "判定说明", "审计状态",
]


def priority(shape: str) -> str:
    if shape == "32":
        return "方形宽车头已确认：最高优先级直接归32"
    if shape == "31":
        return "已排除方形宽车头：实际轮廓为Low Sport"
    if shape == "30":
        return "已排除方形宽车头与Low Sport：归Standard/Fastback"
    if shape == "21":
        return "两厢/旅行车方头：归Boxy Front"
    if shape == "20":
        return "两厢/旅行车圆头：归Rounded Front"
    if shape == "42":
        return "SUV方头：归Boxy SUV"
    if shape == "50":
        return "硬派方盒SUV：归Jeep-like Boxy"
    return "按固定车形类别的实际轮廓结论"


def main() -> None:
    parser = argparse.ArgumentParser(description="把新版 AGENT 优先级逐条应用并审计到所有 DIMENSION-ID。")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        raise SystemExit("请显式使用 --write")

    source = project.read_csv(project.SOURCE)
    cache = project.read_csv(project.CACHE)
    result = project.read_csv(project.RESULT)
    result_map = {row["DIMENSION-ID"]: row["车形"] for row in result}
    if list(result_map) != [row["DIMENSION-ID"] for row in source]:
        raise SystemExit("record_shape 与规范快照的 DIMENSION-ID 顺序或覆盖不一致")

    rows = []
    invalid_generation_3x = []
    historical_count = 0
    historical_shapes: Counter[str] = Counter()
    for row in source:
        shape = result_map[row["DIMENSION-ID"]]
        selected = project.select_cache(row, cache)
        if selected is None:
            raise SystemExit(f"记录未命中缓存：{row['DIMENSION-ID']}")
        if shape in {"30", "31", "32"} and not (
            selected.get("generation") == row.get("代际")
            and not selected.get("match_pattern")
            and selected.get("note", "").startswith("按新版 AGENT 代际复用")
        ):
            invalid_generation_3x.append(row["DIMENSION-ID"])
        start, _ = project.years(row["YEAR"])
        historical = start is not None and start < 2000
        if historical:
            historical_count += 1
            historical_shapes[shape] += 1
        if selected.get("match_pattern"):
            cache_scope = "版本/外廓证据规则"
        elif selected.get("generation"):
            cache_scope = "车型+代际复用"
        else:
            cache_scope = "车型基础规则"
        rows.append({
            "DIMENSION-ID": row["DIMENSION-ID"],
            "MAKE": row["MAKE"],
            "MODEL": row["MODEL"],
            "代际": row.get("代际", ""),
            "YEAR": row["YEAR"],
            "结构": row.get("结构", ""),
            "车形": shape,
            "2000年前记录": "YES" if historical else "NO",
            "最高优先级判定": priority(shape),
            "缓存层级": cache_scope,
            "判定说明": selected.get("note", ""),
            "审计状态": "APPLIED",
        })
    if invalid_generation_3x:
        raise SystemExit(f"3x 未使用独立代际缓存：{invalid_generation_3x[:10]}")

    project.atomic_write(AUDIT, AUDIT_FIELDS, rows)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": True,
        "scope": "Every DIMENSION-ID in the canonical snapshot; 1900s means YEAR starts before 2000",
        "records_audited": len(rows),
        "dimension_ids_unique": len({row["DIMENSION-ID"] for row in rows}),
        "pre_2000_records_audited": historical_count,
        "shape_counts": dict(sorted(Counter(row["车形"] for row in rows).items(), key=lambda item: int(item[0]))),
        "pre_2000_shape_counts": dict(sorted(historical_shapes.items(), key=lambda item: int(item[0]))),
        "independent_generation_3x_failures": 0,
        "source_directory_written": False,
    }
    SUMMARY.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
