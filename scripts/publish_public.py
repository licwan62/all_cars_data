#!/usr/bin/env python3
"""把各节点当前 output/ 的稳定交付物按规范文件名（无 artifact 后缀）发布到 public/data/。

public/ 只是仓库外发布或人工交换区，不是 agent 间数据总线。本脚本只读各节点 output/manifest.json，
校验 sha256 后复制；目标路径按区域分组：
  public/data/us_data|eu_data|ru_data/  区域文件（名称含 _US/_EU/_RU；US 规则、店铺表放 us_data，店铺表在 stores/）
  public/data/                          跨区域文件（如 全量表_汇总.csv）
同时写 public/data/manifest.json，记录每个文件的来源节点、版本、artifact 和 sha256。
旧命名文件（ru_all.csv 等）移到 public/data_legacy_names_<日期>/，不删除。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PUBLIC_DATA = ROOT / "public" / "data"
OWNED_DIRS = ("us_data", "eu_data", "ru_data")
US_FILES = {"尺码匹配规则.csv", "店铺货架.csv"}
SKIP = {"manifest.json"}
SKIP_PATTERN = re.compile(r"\.(xlsx|tsv|md)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target_for(name: str) -> Path:
    if name.startswith("店铺全量_"):
        return Path("us_data") / "stores" / name
    region = re.search(r"_(US|EU|RU)\.[^.]+$", name)
    if region:
        return Path(f"{region.group(1).lower()}_data") / name
    if name in US_FILES:
        return Path("us_data") / name
    return Path(name)


def collect() -> dict[Path, dict]:
    payload = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))
    plan: dict[Path, dict] = {}
    for node in payload["nodes"]:
        manifest_path = ROOT / node["path"] / "output" / "manifest.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["deliverables"]:
            name = item["file"]
            if name in SKIP or SKIP_PATTERN.search(name):
                continue
            source = ROOT / node["path"] / "output" / name
            if not source.is_file() or sha256(source) != item["sha256"]:
                raise ValueError(f"{node['path']}/output/{name} 缺失或与 manifest sha256 不一致，请先重新发布该节点")
            target = target_for(name)
            if target in plan:
                raise ValueError(f"{name} 在 public/data 中重名（{plan[target]['node']} 与 {node['id']}）")
            plan[target] = {
                "file": target.as_posix(), "node": node["id"], "version": manifest["version"],
                "artifact_file": item["artifact_file"], "sha256": item["sha256"],
            }
    return plan


def main() -> int:
    try:
        plan = collect()
    except ValueError as error:
        print(f"发布失败：{error}", file=sys.stderr)
        return 2
    wanted = {target.as_posix() for target in plan}
    legacy = ROOT / "public" / f"data_legacy_names_{date.today():%Y%m%d}"
    for folder in OWNED_DIRS:
        base = PUBLIC_DATA / folder
        for path in [p for p in base.rglob("*") if p.is_file()] if base.is_dir() else []:
            if path.relative_to(PUBLIC_DATA).as_posix() not in wanted:
                destination = legacy / path.relative_to(PUBLIC_DATA)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), destination)
    for target, record in plan.items():
        source = ROOT / next(n["path"] for n in json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))["nodes"] if n["id"] == record["node"]) / "output" / target.name
        destination = PUBLIC_DATA / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    manifest = {"schema_version": 1, "files": sorted(plan.values(), key=lambda r: r["file"])}
    (PUBLIC_DATA / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已发布 {len(plan)} 个文件到 {PUBLIC_DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
