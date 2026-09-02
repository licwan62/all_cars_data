from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone

import shape_project as project


REPORT = project.PROJECT / "artifacts" / "suv_shape_id_migration_2026-09-02.json"
LEGACY_TO_CURRENT = {"40": "42", "41": "40", "42": "41"}
SENTINELS = {
    ("Honda", "CR-V"): ("41", "40"),
    ("BMW", "X6"): ("42", "41"),
    ("Toyota", "4Runner"): ("40", "42"),
}


def sentinel_shape(cache: list[dict[str, str]], make: str, model: str) -> str:
    matches = [
        row for row in cache
        if row.get("MAKE") == make
        and row.get("MODEL") == model
        and not row.get("match_pattern")
        and not row.get("generation")
        and not row.get("year_start")
        and not row.get("year_end")
    ]
    if len(matches) != 1:
        raise SystemExit(f"SUV 编号迁移哨兵不唯一：{make} {model} -> {len(matches)} 条")
    return matches[0]["shape"]


def migrate() -> None:
    cache = project.read_csv(project.CACHE)
    states = {
        key: sentinel_shape(cache, *key)
        for key in SENTINELS
    }
    legacy = all(states[key] == expected[0] for key, expected in SENTINELS.items())
    current = all(states[key] == expected[1] for key, expected in SENTINELS.items())
    if not legacy and not current:
        details = ", ".join(f"{make} {model}={states[(make, model)]}" for make, model in SENTINELS)
        raise SystemExit(f"SUV 编号处于混合或未知状态，拒绝自动迁移：{details}")

    before_counts = Counter(row["shape"] for row in cache if row.get("shape") in LEGACY_TO_CURRENT)
    changed = 0
    if legacy:
        stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        for row in cache:
            before = row.get("shape", "")
            if before not in LEGACY_TO_CURRENT:
                continue
            row["shape"] = LEGACY_TO_CURRENT[before]
            row["updated_at"] = stamp
            changed += 1
        project.atomic_write(
            project.CACHE,
            project.CACHE_FIELDS,
            sorted(cache, key=lambda row: (project.norm(row["MAKE"]), project.norm(row["MODEL"]), -project.specificity(row))),
        )

    after_counts = Counter(row["shape"] for row in cache if row.get("shape") in LEGACY_TO_CURRENT)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": True,
        "applied": legacy,
        "reference": "doc/reference.csv",
        "agent": "doc/AGENT.md",
        "mapping": {
            "legacy_40_boxy_suv": "42 Boxy SUV",
            "legacy_41_conventional_suv": "40 Conventional SUV",
            "legacy_42_fastback_suv": "41 Fastback SUV",
        },
        "cache_rules_changed": changed,
        "before_counts": dict(sorted(before_counts.items())),
        "after_counts": dict(sorted(after_counts.items())),
        "sentinels_after": {
            f"{make} {model}": sentinel_shape(cache, make, model)
            for make, model in SENTINELS
        },
        "source_directory_written": False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="按 reference.csv 和新版 AGENT 迁移 SUV 40/41/42 编号语义。")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        raise SystemExit("请显式使用 --apply")
    migrate()


if __name__ == "__main__":
    main()
