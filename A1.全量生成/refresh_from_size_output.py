#!/usr/bin/env python3
"""用当前 A0 US 全量表和已审核 TrimList 刷新 B1 交付物。"""

from __future__ import annotations

import json
import csv
import os
import re
import shutil
from datetime import date
from pathlib import Path

import pandas as pd

from src.size_analysis import build_size_analysis_files


PROJECT = Path(__file__).resolve().parent
SOURCE = PROJECT.parent / "A0.尺码计算" / "output" / "全量表_US.csv"
DATA = PROJECT / "data"
TRIM_VALUES = DATA / "trim_values.csv"
OUTPUT = PROJECT / "output"
ARTIFACTS = PROJECT / "artifacts"
DELIVERABLES = ("尺寸TRIM映射.csv", "TRIM适配器.csv")


def next_artifact() -> Path:
    day = date.today().isoformat()
    used = [int(m.group(1)) for p in ARTIFACTS.glob(f"{day}_*")
            if (m := re.match(rf"{day}_(\d{{2}})_", p.name))]
    return ARTIFACTS / f"{day}_{max(used, default=0) + 1:02d}_refresh-size-analysis"


def main() -> int:
    artifact = next_artifact()
    staging = artifact.with_name(f".{artifact.name}.tmp")
    if staging.exists() or artifact.exists():
        raise FileExistsError(artifact)
    try:
        (staging / "input").mkdir(parents=True)
        (staging / "output").mkdir()
        (staging / "reports").mkdir()
        source = pd.read_csv(SOURCE, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        if source["DIMENSION-ID"].duplicated().any() or not source["DIMENSION-ID"].str.endswith(" US").all():
            raise ValueError("A0 US 全量表 DIMENSION-ID 缺少 US 后缀或重复")
        source["DIMENSION-ID"] = source["DIMENSION-ID"].str.removesuffix(" US")
        values = pd.read_csv(TRIM_VALUES, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        if values["DIMENSION-ID"].duplicated().any():
            raise ValueError("维护的 TRIM 值存在重复 DIMENSION-ID")
        trim_map = values.set_index("DIMENSION-ID")["Trims"]
        filled = source["TRIM"].eq("") & source["DIMENSION-ID"].isin(trim_map.index)
        source.loc[filled, "TRIM"] = source.loc[filled, "DIMENSION-ID"].map(trim_map)
        prepared = staging / "input" / "全量表_US_基础ID.csv"
        source.to_csv(prepared, index=False, encoding="utf-8-sig", lineterminator="\n")
        shutil.copy2(TRIM_VALUES, staging / "input" / TRIM_VALUES.name)
        current_ids = set(source["DIMENSION-ID"])
        excluded: dict[str, int] = {}
        for name in ("TrimList.csv", "TrimList_audit.csv"):
            with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                fields = reader.fieldnames
                rows = list(reader)
            selected = [row for row in rows if row["DIMENSION-ID"] in current_ids]
            excluded[name] = len(rows) - len(selected)
            with (staging / "input" / name).open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerows(selected)
        result = build_size_analysis_files(
            staging / "input" / "TrimList.csv",
            staging / "input" / "TrimList_audit.csv",
            prepared,
            "尺码匹配",
            staging / "output",
            staging / "reports",
        )
        status = {"status": "passed", "source": str(SOURCE), "rows": len(source),
                  "maintained_trim_values_used": int(filled.sum()),
                  "nonempty_trim_values": int(source["TRIM"].ne("").sum()),
                  "excluded_obsolete_trim_rows": excluded,
                  "counts": result.report["counts"]}
        (staging / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(staging, artifact)
        for name in DELIVERABLES:
            target = OUTPUT / name
            temporary = target.with_name(f".{name}.tmp")
            shutil.copy2(artifact / "output" / name, temporary)
            os.replace(temporary, target)
        print(json.dumps({**status, "artifact": str(artifact)}, ensure_ascii=False))
        return 0
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
