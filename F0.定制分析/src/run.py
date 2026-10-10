"""Run configured custom SKU analyses with immutable, traceable batches."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch
from custom_analysis import active_rows, dimension_codes
from report import render_report

DETAILS = ROOT / "A0.尺码计算" / "output" / "US" / "全量" / "全量表.csv"
CODES = ROOT / "02.代码映射" / "output" / "尺寸编码映射.csv"
REVIEWS = ROOT / "B0.差评分析" / "output" / "差评分析表.csv"
REPORT_NAME = "定制SKU聚簇报告.md"


def reference_tasks(config: dict, members: list[dict], rows: list[dict]) -> list[dict]:
    generations = config.get("sketchfab_generation_by_internal_generation", {})
    row_generations = {
        row["DIMENSION-ID"]: generations.get(
            f"{row.get('MODEL', '')}:{row.get('代际', '')}",
            generations.get(row.get("代际", ""), row.get("代际", "")),
        )
        for row in rows
    }
    references = {item["generation"]: item for item in config["sketchfab_searches"]}
    grouped: dict[tuple[str, str], list[str]] = {}
    for member in members:
        key = (member["SKU聚簇"], row_generations[member["DIMENSION-ID"]])
        grouped.setdefault(key, []).append(member["DIMENSION-ID"])
    return [
        {"SKU聚簇": sku, "代际": generation, "覆盖车型": "；".join(identifiers),
         "检索式": references.get(generation, {}).get("query", ""),
         "参考链接": references.get(generation, {}).get("representative_url", ""),
         "状态": "待外形核验" if references.get(generation, {}).get("representative_url") else "待补参考模型",
         "核验项目": "车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性"}
        for (sku, generation), identifiers in sorted(grouped.items())
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="配置名，如 mini_countryman；默认运行全部配置")
    args = parser.parse_args()
    configs = sorted((PROJECT / "data").glob("*_custom_analysis.json"))
    if args.case:
        configs = [p for p in configs if p.name == f"{args.case}_custom_analysis.json"]
    if not configs:
        parser.error("没有匹配的定制分析配置")
    with RunBatch.create(PROJECT / "artifacts", "custom-analysis", data_dir=PROJECT / "data") as batch:
        details = batch.input(DETAILS)
        codes = dimension_codes(batch.input(CODES))
        with batch.input(REVIEWS).open(encoding="utf-8-sig", newline="") as handle:
            reviews = list(csv.DictReader(handle))
        cases = []
        for path in configs:
            config = json.loads(path.read_text(encoding="utf-8"))
            if config.get("region") != "US":
                raise ValueError("当前定制分析仅支持 US 配置")
            if set(config["dimension_tolerances_mm"]) != {"L-MM", "W-MM", "H-MM"} or any(int(x) < 0 for x in config["dimension_tolerances_mm"].values()):
                raise ValueError("L/W/H 阈值必须完整且非负")
            case = path.stem.removesuffix("_custom_analysis")
            rows = active_rows(
                details, config["make"], config.get("model", ""), config.get("structure", ""),
                models=config.get("models"), structures=config.get("structures"),
            )
            report = render_report(config, rows, codes, reviews, batch.inputs, reference_tasks)
            batch.output(f"{case}/{REPORT_NAME}").write_text(report, encoding="utf-8")
            cases.append({"case": case, "input_rows": len(rows)})
        batch.finish({"cases": cases, "change": "仅交付完整 Markdown，新增 Prius 和差评依据；历史批次保留"}, publish_to=PROJECT / "output")
        print(f"batch={batch.directory} cases={len(cases)}")


if __name__ == "__main__":
    main()
