#!/usr/bin/env python3
"""发布当前已审核的 EU 尺码研究覆盖。

这不会将未研究的 EU 尺寸库行伪装成已匹配结果；发布报告会记录覆盖率。
"""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "A0.尺码计算"
RESEARCH = PROJECT / "data" / "eu" / "当前已审核全量.csv"
DIMENSIONS = ROOT / "02.分类结构审核" / "output" / "车型结构_EU.csv"
CODE_MAP = ROOT / "02.代码映射" / "output" / "尺寸编码映射.csv"
OUTPUT = PROJECT / "output"
ARTIFACTS = PROJECT / "artifacts"


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def next_artifact_dir() -> Path:
    prefix = f"{date.today().isoformat()}_"
    used = []
    for path in ARTIFACTS.glob(f"{prefix}[0-9][0-9]_*"):
        match = re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name)
        if match:
            used.append(int(match.group(1)))
    return ARTIFACTS / f"{prefix}{max(used, default=0) + 1:02d}_eu-current-research"


def build() -> tuple[pd.DataFrame, dict[str, object]]:
    research = read_csv(RESEARCH)
    dimensions = read_csv(DIMENSIONS)
    codes = read_csv(CODE_MAP)[["DIMENSION-ID", "DIMENSION-CODE"]]
    if research["DIMENSION-ID"].duplicated().any():
        raise ValueError("EU 审核结果 DIMENSION-ID 不唯一")
    if codes["DIMENSION-ID"].duplicated().any():
        raise ValueError("尺寸编码映射 DIMENSION-ID 不唯一")
    dimension_ids = set(dimensions["DIMENSION-ID"])
    missing_dimensions = set(research["DIMENSION-ID"]) - dimension_ids
    research = research.loc[research["DIMENSION-ID"].isin(dimension_ids)].copy()
    if research.empty:
        raise ValueError("EU 审核结果与当前尺寸库没有交集")
    result = research.merge(codes, on="DIMENSION-ID", how="left", validate="one_to_one")
    if result["DIMENSION-CODE"].eq("").any() or result["DIMENSION-CODE"].isna().any():
        raise ValueError("EU 审核结果存在缺失的 DIMENSION-CODE")
    columns = list(result.columns)
    columns.remove("DIMENSION-CODE")
    columns.insert(columns.index("DIMENSION-ID"), "DIMENSION-CODE")
    result = result[columns]
    report = {
        "status": "passed",
        "scope": "current-reviewed-research",
        "published_rows": len(result),
        "eu_dimension_library_rows": len(dimensions),
        "coverage_ratio": round(len(result) / len(dimensions), 8),
        "unresearched_rows": len(dimensions) - len(result),
        "stale_reviewed_rows_excluded": len(missing_dimensions),
        "matched_sizes": int(
            (~result["自动尺码"].isin(["无可用尺码", "数据不全", ""])).sum()
        ),
        "unavailable_sizes": int(result["自动尺码"].eq("无可用尺码").sum()),
        "note": "EU 仅发布当前已完成审核的研究覆盖，不代表整个 EU 尺寸库已完成尺码匹配。",
    }
    return result, report


def main() -> int:
    artifact = next_artifact_dir()
    staging = artifact.with_name(f".{artifact.name}.tmp")
    try:
        result, report = build()
        (staging / "input").mkdir(parents=True)
        (staging / "output").mkdir(parents=True)
        shutil.copy2(RESEARCH, staging / "input" / RESEARCH.name)
        shutil.copy2(DIMENSIONS, staging / "input" / DIMENSIONS.name)
        target = staging / "output" / "全量表_EU.csv"
        result.to_csv(target, index=False, encoding="utf-8-sig", lineterminator="\n")
        (staging / "output" / "尺码匹配报告_EU.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (staging / "status.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(staging, artifact)
        for name in ["全量表_EU.csv", "尺码匹配报告_EU.json"]:
            temporary = OUTPUT / f".{name}.tmp"
            shutil.copy2(artifact / "output" / name, temporary)
            os.replace(temporary, OUTPUT / name)
        print(json.dumps({**report, "artifact": str(artifact)}, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        if staging.exists():
            shutil.rmtree(staging)
        print(f"EU 发布失败：{error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
