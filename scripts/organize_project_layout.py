"""Concentrate current JSON, publish business-named pages beside each node.

Copies and verifies every destination before retiring old working copies. Never
modifies data/, historical artifact batches, or portal/data/.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import sha256
from node_paths import node_output, node_page
from node_html import build_reports, check_reports
from content_store import resolve_source

PRESENTATIONS = {
    "dimension-crawler": ("车型尺寸采集", "scan"),
    "dimension-library": ("车型尺寸库", "database"),
    "structure-review": ("车型分类审核", "check"),
    "sales-estimation": ("销量与市场潜力", "chart"),
    "code-mapping": ("车型编码映射", "link"),
    "shape-classification": ("车形核定与尺寸参考", "layers"),
    "size-calculation": ("尺码计算与匹配", "ruler"),
    "size-compression": ("压缩尺码方案", "layers"),
    "negative-review-analysis": ("差评与适配问题", "check"),
    "compression-scoring": ("定制需求评分", "chart"),
    "custom-analysis": ("定制车型分析", "ruler"),
    "representative-model": ("代表车型分析", "truck"),
    "sku-clustering": ("车型发货评估", "truck"),
    "link-analysis-pickup": ("皮卡链接与发货核对", "link"),
    "link-analysis": ("链接分析总览", "link"),
    "size-analysis": ("尺码尺寸统计", "chart"),
    "dimension-iteration": ("尺寸迭代工作台", "ruler"),
    "size-cluster-analysis": ("尺码边界历史分析", "chart"),
    "link-analysis-regular": ("普通车链接与发货核对", "link"),
    "link-analysis-w": ("W型车链接工作台", "link"),
    "model-year-coverage": ("车型年全集与覆盖率", "chart"),
}


def contract(payload):
    updated = copy.deepcopy(payload)
    for node in updated["nodes"]:
        title, icon = PRESENTATIONS.get(node["id"], (Path(node["path"]).name, "chart"))
        node.update(output_dir=f"json/{node['id']}", html_at_root=True,
                    html_output=title + ".html", presentation={"title": title, "icon": icon})
    updated["directory_contract"].update(
        data="人工提供和维护的规则、映射与参考资料，以CSV为主；复杂配置可保留JSON/YAML；不写机器生成结果",
        output="旧节点output目录已退役；当前正式接口位置由各节点output_dir声明",
        json="仓库根json/<节点ID>/集中当前JSON接口及manifest/html_manifest；json/_meta/集中发布、归档及整理审计索引",
        html="节点根目录的业务名称.html是直接阅读入口；图表与搜索联动、表格单行紧凑、横向滚动、CSV导出",
        work="可重建运行工作区；work/legacy-output保留未登记旧工作结果，不能作为正式节点输入",
        reports="检查、测试、浏览器截图与资料目录等仓库级报告；不作为节点数据接口",
    )
    updated["html_contract"].update(output="nodes/<节点路径>/<业务名称>.html", manifest="json/<节点ID>/html_manifest.json")
    updated["interface_contract"]["directory"] = "json/<节点ID>/"
    return updated


def safe(root, path):
    resolved = path.resolve()
    resolved.relative_to(root.resolve())
    if resolved == root.resolve():
        raise ValueError("不能把仓库根目录当作操作目标")
    return path


def plan(root, old, updated):
    rows = []
    for original, node in zip(old["nodes"], updated["nodes"]):
        source_dir = root / original["path"] / "output"
        html_meta = source_dir / "html_manifest.json"
        metadata = json.loads(html_meta.read_text(encoding="utf-8")) if html_meta.is_file() else {}
        known_html = {i["file"]: i for i in metadata.get("deliverables", [])}
        for source in sorted(source_dir.rglob("*")):
            if not source.is_file():
                continue
            if source.is_symlink():
                raise ValueError(f"目录迁移不处理符号链接：{source}")
            relative = source.relative_to(source_dir)
            digest = sha256(source)
            action = "move"
            if source.suffix.lower() == ".json":
                destination = node_output(root, node) / relative
            elif relative.as_posix() in known_html and digest == known_html[relative.as_posix()]["sha256"]:
                destination = resolve_source(root, known_html[relative.as_posix()]["artifact_file"])
                if not destination.is_file() or sha256(destination) != digest:
                    raise ValueError(f"旧HTML缺少一致的版本存档：{source}")
                action = "retire-archived-html"
            else:
                destination = root / "work/legacy-output" / node["id"] / relative
            rows.append({"source": source.relative_to(root).as_posix(), "destination": destination.relative_to(root).as_posix(),
                         "sha256": digest, "bytes": source.stat().st_size, "action": action})
    for name in ("release.json", "artifacts_archive.json"):
        source = root / name
        if source.is_file():
            rows.append({"source": name, "destination": f"json/_meta/{name}", "sha256": sha256(source), "bytes": source.stat().st_size, "action": "move"})
    # The former root output directory only held browser QA from the preceding migration.
    for source in sorted((root / "output/playwright").glob("*")):
        if source.is_file():
            folder = "json/_meta/browser-checks" if source.suffix == ".json" else "reports/browser-checks/previous"
            rows.append({"source": source.relative_to(root).as_posix(), "destination": f"{folder}/{source.name}",
                         "sha256": sha256(source), "bytes": source.stat().st_size, "action": "move"})
    for row in rows:
        source, destination = safe(root, root / row["source"]), safe(root, root / row["destination"])
        if destination.is_file() and sha256(destination) != row["sha256"]:
            raise ValueError(f"目标已有不同内容，保留原文件：{destination}")
    return rows


def organize(root, apply=False):
    root = Path(root).resolve()
    config = root / "pipeline.json"
    old_bytes = config.read_bytes()
    old = json.loads(old_bytes)
    updated = contract(old)
    rows = plan(root, old, updated)
    print(f"目录整理：{len(rows)} 个工作文件；{len(updated['nodes'])} 个节点HTML入口")
    if not apply:
        return rows
    if not rows and updated == old:
        print("目录已符合约定；没有搬动文件")
        return rows
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d_%H%M%S")
    audit = root / "json/_meta/layout_changes" / stamp
    audit.mkdir(parents=True, exist_ok=False)
    (audit / "pipeline.before.json").write_bytes(old_bytes)
    (audit / "plan.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in rows:
        source, destination = root / row["source"], root / row["destination"]
        if row["action"] != "retire-archived-html" and not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        if sha256(source) != row["sha256"] or sha256(destination) != row["sha256"]:
            raise RuntimeError(f"搬迁期间内容变化：{source}")
    temporary = config.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_before = {node_page(root, n): node_page(root, n).read_bytes() if node_page(root, n).is_file() else None
                    for n in updated["nodes"]}
    os.replace(temporary, config)
    # Original working copies remain available until every replacement page is checked.
    try:
        build_reports(root)
        errors = check_reports(root, updated["nodes"])
        if errors:
            raise RuntimeError("\n".join(errors))
    except BaseException:
        # Keep the old layout operational and make a retry safe. Immutable batches
        # produced before the failure remain evidence; only working copies revert.
        temporary.write_bytes(old_bytes)
        os.replace(temporary, config)
        for page, previous in pages_before.items():
            safe(root, page)
            if previous is None:
                page.unlink(missing_ok=True)
            else:
                page.write_bytes(previous)
        for row in rows:
            if row["action"] != "retire-archived-html":
                shutil.copy2(root / row["source"], root / row["destination"])
        raise
    for row in rows:
        source = safe(root, root / row["source"])
        if sha256(source) != row["sha256"]:
            raise RuntimeError(f"原工作文件在迁移中变化，保留：{source}")
        source.unlink()
    obsolete = [root / n["path"] / "output" for n in old["nodes"]] + [root / "output"]
    for folder in obsolete:
        safe(root, folder)
        if folder.is_dir():
            for child in sorted((p for p in folder.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
                if not any(child.iterdir()):
                    child.rmdir()
            if not any(folder.iterdir()):
                folder.rmdir()
    (audit / "completed.json").write_text(json.dumps({"completed": True, "files": len(rows), "data_rules_changed": False,
                                                      "historical_artifacts_changed": False}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已校验并整理 {len(rows)} 个工作文件；审计清单：{audit.relative_to(root)}")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    organize(ROOT, args.apply)
