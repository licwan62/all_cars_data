#!/usr/bin/env python3
"""Validate and publish the current RU dimension, full-size, and matching-rule CSVs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
PUBLIC_DIR = Path(r"\\NAS8824B4\Public\PQData\pub_all_cars_data") / "data" / "ru_data"
ARTIFACTS_DIR = PROJECT / "artifacts"

SOURCES = {
    "00_RU尺寸库.csv": ROOT / "02.分类结构审核" / "output" / "车型结构_RU.csv",
    "02_RU全量.csv": PROJECT / "output" / "全量表_RU.csv",
    "全量表_RU.csv": PROJECT / "output" / "全量表_RU.csv",
    "03_RU尺码匹配规则.csv": PROJECT / "data" / "ru" / "尺寸" / "0921.3-两厢车候选-2L200.csv",
    "尺码匹配规则_RU.csv": PROJECT / "data" / "ru" / "尺寸" / "0921.3-两厢车候选-2L200.csv",
}


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def next_artifact_dir() -> Path:
    prefix = f"{date.today().isoformat()}_"
    numbers = [
        int(match.group(1))
        for path in ARTIFACTS_DIR.glob(f"{prefix}[0-9][0-9]_*_")
        if (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))
    ]
    # The narrow glob above intentionally avoids relying on descriptions; scan all dated dirs too.
    numbers.extend(
        int(match.group(1))
        for path in ARTIFACTS_DIR.glob(f"{prefix}*")
        if path.is_dir() and (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))
    )
    return ARTIFACTS_DIR / f"{prefix}{max(numbers, default=0) + 1:02d}_ru-public-release"


def validate_release() -> dict[str, object]:
    for path in SOURCES.values():
        if not path.is_file():
            raise ValueError(f"发布输入不存在：{path}")
    dimensions = read_csv(SOURCES["00_RU尺寸库.csv"])
    full = read_csv(SOURCES["02_RU全量.csv"])
    rules = read_csv(SOURCES["03_RU尺码匹配规则.csv"])
    for name, frame in (("RU尺寸库", dimensions), ("RU全量", full)):
        if "DIMENSION-ID" not in frame.columns:
            raise ValueError(f"{name} 缺少 DIMENSION-ID")
        if frame["DIMENSION-ID"].eq("").any() or frame["DIMENSION-ID"].duplicated().any():
            raise ValueError(f"{name} 的 DIMENSION-ID 必须非空且唯一")
        if not frame["DIMENSION-ID"].str.endswith(" RU").all():
            raise ValueError(f"{name} 存在未追加 RU 后缀的 DIMENSION-ID")
    dimension_ids = set(dimensions["DIMENSION-ID"])
    full_ids = set(full["DIMENSION-ID"])
    if dimension_ids != full_ids:
        raise ValueError(
            f"尺寸库与全量 ID 集合不一致：尺寸独有 {len(dimension_ids - full_ids)}，全量独有 {len(full_ids - dimension_ids)}"
        )
    required_rules = {"亚马逊尺码", "OZON尺码", "发货尺码", "分类", "长_mm", "宽_mm", "高_mm"}
    if not required_rules.issubset(rules.columns):
        raise ValueError(f"匹配规则缺少字段：{sorted(required_rules - set(rules.columns))}")
    if rules[["亚马逊尺码", "分类"]].eq("").any().any():
        raise ValueError("匹配规则的亚马逊尺码和分类不能为空")
    if rules.duplicated(["分类", "亚马逊尺码"]).any():
        raise ValueError("匹配规则存在重复的分类+亚马逊尺码")
    published_sizes = set(full["自动尺码"]) - {"", "无可用尺码", "数据不全"}
    unknown_sizes = published_sizes - set(rules["亚马逊尺码"])
    if unknown_sizes:
        raise ValueError(f"全量表存在规则中未定义的自动尺码：{sorted(unknown_sizes)}")
    sales = pd.to_numeric(full["销量合计"], errors="coerce")
    if sales.isna().any():
        raise ValueError("RU 全量表销量合计存在非数值")
    return {
        "dimension_rows": int(len(dimensions)),
        "full_rows": int(len(full)),
        "unique_dimension_ids": int(full["DIMENSION-ID"].nunique()),
        "rule_rows": int(len(rules)),
        "matched_sizes": int((~full["自动尺码"].isin(["", "无可用尺码", "数据不全"])).sum()),
        "unavailable_sizes": int(full["自动尺码"].eq("无可用尺码").sum()),
        "sales_total": int(sales.sum()),
    }


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, destination)


def main() -> int:
    artifact_dir = next_artifact_dir()
    try:
        summary = validate_release()
        artifact_input = artifact_dir / "input"
        artifact_output = artifact_dir / "output"
        artifact_rules = artifact_dir / "rules"
        artifact_input.mkdir(parents=True)
        artifact_output.mkdir(parents=True)
        artifact_rules.mkdir(parents=True)
        for target_name, source in SOURCES.items():
            shutil.copy2(source, artifact_input / source.name)
            shutil.copy2(source, artifact_output / target_name)
        shutil.copy2(Path(__file__), artifact_rules / Path(__file__).name)
        hashes = {name: sha256(artifact_output / name) for name in SOURCES}
        status = {"status": "passed", **summary, "sha256": hashes}
        (artifact_dir / "status.json").write_text(
            json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for target_name in SOURCES:
            atomic_copy(artifact_output / target_name, PUBLIC_DIR / target_name)
        print(json.dumps({**status, "public_dir": str(PUBLIC_DIR)}, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "status.json").write_text(
            json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"RU public 发布失败：{error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
