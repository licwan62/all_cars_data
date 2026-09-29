#!/usr/bin/env python3
"""把各节点当前 output/ 的稳定交付物发布到 NAS public/。

public/ 只是仓库外发布或人工交换区，不是 agent 间数据总线。本脚本只读各节点 output/manifest.json，
校验 sha256 后复制；目标路径（均相对 PUBLIC_ROOT）按类别分组：
  data/us_data|eu_data|ru_data/    区域数据表
    data/us_data/全量/              US 全量表与各店铺全量表（A0 US/店铺/ 也归到这里）
    data/us_data/压缩/<产线>/       A2 中区域为 US 的产线（US 及各店铺）压缩尺码表
  data/基础数据/                    跨区域尺寸库与销量基础表
  data/编码映射/                    ID、车型与尺寸编码映射
  data/车型分类/                    车型结构、车形分类与参考尺寸
  data/质量分析/                    尺码统计、极值与异常分析
  data/差评分析/                    差评、耳位与皮卡结构分析
  data/代表车型/                    代表车型表及其报告
  customizing/                      定制需求度评分等"定制"类落盘文件

发布目录只保存可直接使用的 CSV 数据表；JSON、TSV、XLSX 等辅助小文件不发布。
节点 output/ 中的 md 交付物（如 A0 尺码匹配报告）原样发布，JSON 交付物转成同名 .md 说明文档，
与 CSV 放在同一目录，说明该目录文件的生成情况。
README.md 是发布说明和来源清单，不写入 JSON manifest。旧命名 CSV 移到 NAS 目录下
集中备份区 backup/data_legacy_names_<日期>/，不删除。
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
# 相对 PUBLIC_ROOT、由本脚本完全接管的目录：不在 wanted 清单里的文件会被归档到 backup/。
OWNED_DIRS = ("data", "customizing")
# 节点 output/ 中按 <国别>/... 分目录的交付物（如 A0 的 US/全量/全量表.csv）保留子路径，
# 发布到 data/<国别>_data/ 下。
REGION_DIR = re.compile(r"^(US|EU|RU)/(.+)$")
# 落盘规则：这些文件发布到 PUBLIC_ROOT/customizing/，不进 data/（B1.压缩定制评分 的
# 定制需求度评分.csv 是"定制"类产物，和区域尺寸数据分开存放）。
CUSTOMIZING_FILES = {"定制需求度评分.csv"}
# 不带国别目录的通用交付物按职责分组，避免 data/ 根目录堆放裸文件。
COMMON_NODE_DIRS = {
    "dimension-library": "基础数据",
    "sales-estimation": "基础数据",
    "code-mapping": "编码映射",
    "structure-review": "车型分类",
    "shape-classification": "车型分类",
    "full-generation": "质量分析",
    "negative-review-analysis": "差评分析",
    "representative-model": "代表车型",
}
# A0 的店铺全量表与国别全量表同放 全量/。
REGION_SUBDIR_ALIASES = {("US", "店铺"): "全量"}
# A2 压缩尺码表按产线分目录（<产线>/压缩尺码表[_皮卡].csv），产线的区域见 A2 data/产线.yaml；
# 发布到 data/<区域>_data/压缩/<产线>/。
COMPRESSION_NODE = "size-compression"
COMPRESSION_LINES_FILE = ROOT / "A2.压缩尺寸信息" / "data" / "产线.yaml"
COMPRESSION_REGIONS = {"US"}
PUBLISH_SUFFIXES = {".csv"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compression_lines(path: Path = COMPRESSION_LINES_FILE) -> dict[str, str]:
    """A2 产线 -> 区域。"""
    import yaml

    config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(line): str(spec["区域"]) for line, spec in (config.get("产线") or {}).items()}


def target_for(name: str, node_id: str = "", lines: dict[str, str] | None = None) -> Path:
    """返回发布目标相对 PUBLIC_ROOT 的路径。"""
    if name in CUSTOMIZING_FILES:
        return Path("customizing") / name
    if node_id == COMPRESSION_NODE:
        line, _, rest = name.partition("/")
        region = (compression_lines() if lines is None else lines).get(line)
        if rest and region in COMPRESSION_REGIONS:
            return Path(f"data/{region.lower()}_data") / "压缩" / line / rest
    nested = REGION_DIR.match(name)
    if nested:
        region, rest = nested.groups()
        head, _, tail = rest.partition("/")
        alias = REGION_SUBDIR_ALIASES.get((region, head))
        if alias and tail:
            rest = f"{alias}/{tail}"
        return Path(f"data/{region.lower()}_data") / rest
    region = re.search(r"_(US|EU|RU)\.[^.]+$", name)
    if region:
        return Path(f"data/{region.group(1).lower()}_data") / name
    common_dir = COMMON_NODE_DIRS.get(node_id)
    if common_dir:
        return Path("data") / common_dir / name
    return Path("data") / name


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
            suffix = Path(name).suffix.lower()
            if suffix not in {".json", ".md"} or name == "manifest.json":
                continue
            source = ROOT / node["path"] / "output" / name
            if not source.is_file() or sha256(source) != item["sha256"]:
                raise ValueError(f"{node['path']}/output/{name} 缺失或与 manifest sha256 不一致，请先重新发布该节点")
            target = target_for(name, node["id"]).with_suffix(".md")
            if target in docs:
                raise ValueError(f"{name} 说明文档重名")
            # md 交付物（如 A0 尺码匹配报告）原样发布；JSON 转成 md 说明
            docs[target] = source.read_text(encoding="utf-8") if suffix == ".md" else json_to_markdown(source, item, node, manifest["version"])
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
            target = target_for(name, node["id"])
            if target in plan:
                raise ValueError(f"{name} 在 NAS public/data 中重名（{plan[target]['node']} 与 {node['id']}）")
            plan[target] = {
                "file": target.as_posix(), "source": source, "node": node["id"], "version": manifest["version"],
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
    legacy = PUBLIC_ROOT / "backup" / f"data_legacy_names_{date.today():%Y%m%d}"
    for folder in OWNED_DIRS:
        base = PUBLIC_ROOT / folder
        for path in [p for p in base.rglob("*") if p.is_file()] if base.is_dir() else []:
            if path.relative_to(PUBLIC_ROOT).as_posix() not in wanted:
                destination = legacy / path.relative_to(PUBLIC_ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), destination)
        # 归档后留下的空目录（如改名前的 us_data/店铺/）一并移除
        for directory in sorted((p for p in base.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True) if base.is_dir() else []:
            if not any(directory.iterdir()):
                directory.rmdir()
    for target, record in plan.items():
        destination = PUBLIC_ROOT / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        shutil.copy2(record["source"], temporary)
        os.replace(temporary, destination)
    for target, text in docs.items():
        destination = PUBLIC_ROOT / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, destination)
    # Earlier publisher versions used JSON manifests.  They are generated
    # metadata, so remove only the one known publisher-owned copy.
    obsolete = PUBLIC_ROOT / "data" / "manifest.json"
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
        "`data/` 和 `customizing/` 是本脚本管理的正式发布地址（本文件与来源清单描述的即是这两个目录的当前内容）。`data/` 下按国别或数据职责分目录，不在根目录堆放数据文件；`customizing/` 存放定制类产物（如定制需求度评分）。被替换的旧命名文件与历史批次统一归档到本目录的 `backup/`，不散落在其他位置；`car_code/`、`reference/`、`reports/`、`sku_cluster/` 为人工维护的参考资料，不受本脚本管理。",
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
    print(f"已发布 {len(plan)} 个 CSV 文件、{len(docs)} 个 md 说明到 {PUBLIC_ROOT}；说明见 {readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
