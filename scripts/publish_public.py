#!/usr/bin/env python3
"""把各节点当前 output/ 的稳定交付物发布到 NAS public/data/。

public/ 只是仓库外发布或人工交换区，不是 agent 间数据总线。本脚本只读各节点 output/manifest.json，
校验 sha256 后复制；目标路径按区域分组：
  NAS public data/us_data|eu_data|ru_data/
  NAS public data/

发布目录只保存可直接使用的 CSV 数据表；JSON、TSV、XLSX 等辅助小文件不发布。
节点 output/ 中的 JSON 交付物（如尺码匹配报告）在发布时转成同名 .md 说明文档，
与 CSV 放在同一区域目录，说明该目录文件的生成情况。
README.md 是发布说明和来源清单，不写入 JSON manifest。旧命名 CSV 移到同一 NAS
目录的 data_legacy_names_<日期>/，不删除。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = Path(r"\\NAS8824B4\Public\PQData\pub_all_cars_data")
PUBLIC_DATA = PUBLIC_ROOT / "data"
OWNED_DIRS = ("us_data", "eu_data", "ru_data")
US_FILES = {"尺码匹配规则.csv", "店铺货架.csv"}
PUBLISH_SUFFIXES = {".csv"}


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


def flatten(value, prefix: str = "") -> list[tuple[str, str]]:
    if isinstance(value, dict):
        rows = []
        for key, item in value.items():
            rows.extend(flatten(item, f"{prefix}.{key}" if prefix else str(key)))
        return rows or [(prefix, "{}")]
    if isinstance(value, list):
        if all(not isinstance(i, (dict, list)) for i in value):
            text = ", ".join(map(str, value[:20])) + (f" …（共 {len(value)} 项）" if len(value) > 20 else "")
            return [(prefix, text)]
        rows = []
        for index, item in enumerate(value):
            rows.extend(flatten(item, f"{prefix}[{index}]"))
        return rows
    return [(prefix, str(value))]


def json_to_markdown(source: Path, item: dict, node: dict, version: str) -> str:
    payload = json.loads(source.read_text(encoding="utf-8"))
    cell = lambda text: text.replace("|", "\\|").replace("\n", " ")
    lines = [
        f"# {source.stem} 生成说明",
        "",
        f"- 来源节点：`{node['id']}`（{node['path']}）",
        f"- 节点版本：`{version}`",
        f"- 来源 artifact：`{item['artifact_file']}`",
        f"- 原始 JSON SHA-256：`{item['sha256']}`",
        "- 本文件由发布脚本从节点 output/ 的 JSON 自动转换；JSON 本身不发布到本目录。",
        "",
        "## 生成情况",
        "",
        "| 项目 | 值 |",
        "| --- | --- |",
    ]
    lines.extend(f"| `{cell(key)}` | {cell(value)} |" for key, value in flatten(payload))
    return "\n".join(lines) + "\n"


def collect_docs() -> dict[Path, str]:
    payload = json.loads((ROOT / "pipeline.json").read_text(encoding="utf-8"))
    docs: dict[Path, str] = {}
    for node in payload["nodes"]:
        manifest_path = ROOT / node["path"] / "output" / "manifest.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["deliverables"]:
            name = item["file"]
            if Path(name).suffix.lower() != ".json" or name == "manifest.json":
                continue
            source = ROOT / node["path"] / "output" / name
            if not source.is_file() or sha256(source) != item["sha256"]:
                raise ValueError(f"{node['path']}/output/{name} 缺失或与 manifest sha256 不一致，请先重新发布该节点")
            target = target_for(name).with_suffix(".md")
            if target in docs:
                raise ValueError(f"{name} 说明文档重名")
            docs[target] = json_to_markdown(source, item, node, manifest["version"])
    return docs


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
            if Path(name).suffix.lower() not in PUBLISH_SUFFIXES:
                continue
            source = ROOT / node["path"] / "output" / name
            if not source.is_file() or sha256(source) != item["sha256"]:
                raise ValueError(f"{node['path']}/output/{name} 缺失或与 manifest sha256 不一致，请先重新发布该节点")
            target = target_for(name)
            if target in plan:
                raise ValueError(f"{name} 在 NAS public/data 中重名（{plan[target]['node']} 与 {node['id']}）")
            plan[target] = {
                "file": target.as_posix(), "node": node["id"], "version": manifest["version"],
                "artifact_file": item["artifact_file"], "sha256": item["sha256"],
            }
    return plan


def main() -> int:
    try:
        plan = collect()
        docs = collect_docs()
    except ValueError as error:
        print(f"发布失败：{error}", file=sys.stderr)
        return 2
    wanted = {target.as_posix() for target in plan} | {target.as_posix() for target in docs}
    legacy = PUBLIC_ROOT / f"data_legacy_names_{date.today():%Y%m%d}"
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
    for target, text in docs.items():
        destination = PUBLIC_DATA / target
        temporary = destination.with_name(f".{destination.name}.tmp")
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, destination)
    # 旧版 full_tables/ 下遗留的 JSON 移入 legacy 目录，不删除。
    for path in (PUBLIC_DATA / "full_tables").glob("*.json") if (PUBLIC_DATA / "full_tables").is_dir() else []:
        destination = legacy / path.relative_to(PUBLIC_DATA)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), destination)
    # Earlier publisher versions used JSON manifests.  They are generated
    # metadata, so remove only the two known publisher-owned copies.
    for obsolete in (PUBLIC_DATA / "manifest.json", PUBLIC_DATA / "full_tables" / "manifest.json"):
        if obsolete.is_file():
            obsolete.unlink()
    records = sorted(plan.values(), key=lambda r: r["file"])
    lines = [
        "# 车型数据公开发布目录",
        "",
        "本目录由 `D:\\Licheng\\Repo\\all_cars_data` 的流水线发布。正式输入仅来自各节点的 `output/`，不作为流水线上游或下游的数据源。",
        "",
        f"本次发布：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "仅发布 CSV 数据表；JSON 交付物（如尺码匹配报告）转换为同名 `.md` 说明文档，放在对应区域目录中，说明该目录文件的生成情况；原始 JSON 和其他辅助小文件保留在仓库的 `output/` 与 `artifacts/`，不存入本目录。",
        "",
        "## 文件与来源",
        "",
        "| 文件 | 节点 | 版本 | 来源 artifact | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| `{item['file']}` | `{item['node']}` | `{item['version']}` | `{item['artifact_file']}` | `{item['sha256']}` |"
        for item in records
    )
    readme = PUBLIC_ROOT / "README.md"
    temporary = readme.with_name(f".{readme.name}.tmp")
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(temporary, readme)
    print(f"已发布 {len(plan)} 个 CSV 文件、{len(docs)} 个 md 说明到 {PUBLIC_DATA}；说明见 {readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
