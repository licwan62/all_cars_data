from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path

import pandas as pd

from run_iteration import (
    PROJECT_DIR,
    ROOT,
    SOURCE_COLUMNS,
    build_candidate,
    build_coverage,
    read_csv,
)


BASE_CONFIG = PROJECT_DIR / "data" / "2026-09-16_jeep_wrangler_side_views.json"
SOURCE = ROOT / "data" / "us" / "source" / "US尺寸库.csv"
ITERATION_ID = "2026-09-16_02_jeep-wrangler-final-review-release"
OUTPUT_DIR = PROJECT_DIR / "artifacts" / ITERATION_ID
WRANGLER_2025_URL = "https://www.jeep.com/2025/wrangler/faq.html"
WRANGLER_2026_URL = "https://www.jeep.com/wrangler/faq.html"
GLADIATOR_2025_GUIDE = (
    "https://www.stellantisfleet.com/content/dam/fca-fleet/na/fleet/en_us/"
    "shopping-tools/brochures-literature/docs/buyers-guide/2025/2025-buyers-guide.pdf"
)
GLADIATOR_2025_BROCHURE = "https://cdn.dealereprocess.org/cdn/brochures/jeep/2025-gladiator.pdf"
GLADIATOR_2026_FAQ = "https://www.jeep.com/gladiator/faq.html"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replacement(config: dict[str, object], version: str, year: str) -> dict[str, object]:
    matches = [
        item
        for item in config["replacements"]
        if item["row"].get("版本") == version and item["row"].get("YEAR") == year
    ]
    if len(matches) != 1:
        raise ValueError(f"无法唯一定位替换项：版本={version!r}, YEAR={year!r}")
    return matches[0]


def build_release_config() -> dict[str, object]:
    config = copy.deepcopy(json.loads(BASE_CONFIG.read_text(encoding="utf-8")))
    config["iteration_id"] = ITERATION_ID
    config["title"] = "Jeep Wrangler 侧视图尺寸迭代终核发布"

    # Release rows have completed human review. Renegade remains deferred because
    # available sources disagree on whether the decor group's outer width is
    # 66.0 or 68.7 inches.
    config["replacements"] = [
        item for item in config["replacements"] if item["row"].get("版本") != "2dr YJ Renegade"
    ]
    for item in config["replacements"]:
        item["row"]["迭代状态"] = "可入库"

    for version in ("2dr JL", "4dr JLU"):
        item = replacement(config, version, "2025-2026")
        item["source_url"] = WRANGLER_2026_URL
        item["row"]["参考车型"] = (
            f"2025-2026 Jeep Wrangler {'2-door' if version == '2dr JL' else '4-door'}, "
            "Jeep official FAQ"
        )
        item["row"]["备注"] = (
            "2025 与 2026 Jeep 官方 FAQ 均确认普通车身外廓："
            f"长度 {item['row']['L-IN']} in、宽度 {item['row']['W-IN']} in、"
            f"高度 {item['row']['H-IN']} in。"
        )

    xtreme_2dr = replacement(config, "2dr JL Xtreme", "2024-2026")
    xtreme_2dr["row"].update(
        {
            "YEAR": "2026",
            "W-IN": "73.9",
            "参考车型": "2026 Jeep Wrangler 2-door Xtreme 35, Jeep official FAQ",
            "备注": (
                "2026 官方 FAQ 首次明确列出两门 Xtreme 35：长 170.9 in、宽 73.9 in、"
                "高 75.5 in；79.3 in 宽度仅适用于四门 Xtreme。"
            ),
        }
    )
    xtreme_2dr["source_url"] = WRANGLER_2026_URL

    xtreme_4dr = replacement(config, "4dr JLU Xtreme", "2024-2026")
    xtreme_4dr["source_url"] = WRANGLER_2026_URL
    xtreme_4dr["row"]["参考车型"] = (
        "2024-2026 Jeep Wrangler 4-door Xtreme 35, existing library and Jeep official FAQs"
    )
    xtreme_4dr["row"]["备注"] = (
        "四门 Xtreme 特殊外廓保留；2025 与 2026 Jeep 官方 FAQ 均确认长 192.5 in、"
        "宽 79.3 in、高 75.5 in。"
    )

    jt_base = replacement(config, "4dr JT", "2025-2026")
    jt_base["source_url"] = GLADIATOR_2026_FAQ
    jt_base["row"]["参考车型"] = "2025-2026 Jeep Gladiator Sport/Sport S, official buyer guides"
    jt_base["row"]["备注"] = (
        "2025 Stellantis Fleet 指南与 2026 Jeep 官方资料确认长 218 in、宽 73.8 in；"
        "普通版软顶最大高度 75.0 in。"
    )

    combined = replacement(config, "4dr JT Rubicon/Mojave", "2021-2026")
    config["replacements"].remove(combined)
    source_ids = combined["source_ids"]
    common = {
        "MAKE": "Jeep",
        "MODEL": "Gladiator",
        "CAB": "Crew",
        "BED": "5",
        "结构": "Pickup",
        "代际": "gen1",
        "分类": "皮卡",
        "L-IN": "218",
        "W-IN": "73.8",
        "迭代状态": "可入库",
    }
    config["replacements"].extend(
        [
            {
                "source_ids": source_ids,
                "row": {
                    **common,
                    "版本": "4dr JT Rubicon/Mojave",
                    "YEAR": "2021-2024",
                    "H-IN": "76.1",
                    "参考车型": "2021-2024 Jeep Gladiator Rubicon/Mojave, existing US size library sources",
                    "备注": "保留既有 2021-2024 高车身口径；补全 JT 平台码与门数。",
                },
                "source_url": combined["source_url"],
            },
            {
                "source_ids": source_ids,
                "row": {
                    **common,
                    "版本": "4dr JT Rubicon",
                    "YEAR": "2025-2026",
                    "H-IN": "76.1",
                    "参考车型": "2025-2026 Jeep Gladiator Rubicon, official buyer guides",
                    "备注": "2025/2026 规格表确认 Rubicon 软顶最大高度 76.1 in。",
                },
                "source_url": GLADIATOR_2025_BROCHURE,
            },
            {
                "source_ids": source_ids,
                "row": {
                    **common,
                    "版本": "4dr JT Mojave",
                    "YEAR": "2025-2026",
                    "H-IN": "76.3",
                    "参考车型": "2025-2026 Jeep Gladiator Mojave, official buyer guides",
                    "备注": "2025/2026 规格表确认 Mojave 软顶最大高度 76.3 in，不能与 Rubicon 合并。",
                },
                "source_url": GLADIATOR_2025_BROCHURE,
            },
        ]
    )

    for row in config["coverage"]:
        if row["页面车型"] == "YJ Renegade":
            row.update(
                {
                    "处理结论": "暂缓-外廓来源冲突",
                    "对应DIMENSION-ID": "",
                    "依据": "现有来源对外廓宽度给出 66.0/68.7 in 冲突值，暂不发布独立记录",
                }
            )
        elif row["页面车型"] == "JL Wrangler":
            row["依据"] = "两门量产车型；2025-2026 已由 Jeep 官方 FAQ 终核"
        elif row["页面车型"] == "JLU Wrangler":
            row["依据"] = "四门 Unlimited 量产车型；2025-2026 已由 Jeep 官方 FAQ 终核"
    return config


def write_report(path: Path, validation: dict[str, object]) -> None:
    text = f"""# Jeep Wrangler 侧视图尺寸迭代终核发布报告

## 发布结论

本批次在 01 候选基础上完成终核，修正后可发布到 `data/us/source/US尺寸库.csv`。

- 源尺寸库：{validation['source_rows']} 行
- 发布候选：{validation['candidate_rows']} 行
- 删除旧分段：{validation['removed_rows']} 行
- 新增发布分段：{validation['added_rows']} 行
- 未触及记录逐字段一致：是
- DIMENSION-ID 唯一且符合统一格式：是
- `correct.csv` 与 `尺寸库候选.csv` 哈希一致：是
- 页面车型清单：{validation['coverage_rows']} 项，均已入库、明确排除或记录暂缓原因

## 终核修正

- 两门 JL Xtreme 调整为 2026 单年，外廓为 170.9 × 73.9 × 75.5 in；79.3 in 宽度仅适用于四门 Xtreme。
- 2025-2026 普通两门/四门 Wrangler 已用 Jeep 官方 FAQ 核定为 166.8/188.4 × 73.9 × 73.6 in。
- 2025-2026 Gladiator 将 Rubicon 与 Mojave 拆分，高度分别为 76.1 与 76.3 in。
- YJ Renegade 的外廓宽度存在 66.0 与 68.7 in 来源冲突，本轮暂缓发布独立记录。

## 主要来源

- 2025 Wrangler：{WRANGLER_2025_URL}
- 2026 Wrangler：{WRANGLER_2026_URL}
- 2025 Gladiator Fleet guide：{GLADIATOR_2025_GUIDE}
- 2025 Gladiator brochure：{GLADIATOR_2025_BROCHURE}
- 2026 Gladiator FAQ：{GLADIATOR_2026_FAQ}

## 发布说明

`correct.csv` 是本批次唯一发布输入。发布前后均需核对 SHA-256，并运行本项目测试与独立结构校验。
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if OUTPUT_DIR.exists():
        raise FileExistsError(f"已归档批次不得覆盖：{OUTPUT_DIR}")

    config = build_release_config()
    source_hash = sha256(SOURCE)
    source = read_csv(SOURCE)
    candidate, changes, validation = build_candidate(source, config)
    coverage, coverage_validation = build_coverage(candidate, config)
    validation.update(coverage_validation)
    validation["release_ready"] = True
    validation["deferred_records"] = ["Jeep Wrangler 2dr YJ Renegade SUV 1990-1994"]

    OUTPUT_DIR.mkdir(parents=True)
    for name in ("尺寸库候选.csv", "correct.csv"):
        candidate.to_csv(
            OUTPUT_DIR / name,
            index=False,
            encoding="utf-8-sig",
            lineterminator="\n",
            quoting=csv.QUOTE_MINIMAL,
        )
    changes.to_csv(
        OUTPUT_DIR / "变更.csv",
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    coverage.to_csv(
        OUTPUT_DIR / "完整性验证.csv",
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    validation["source_sha256"] = source_hash
    validation["candidate_sha256"] = sha256(OUTPUT_DIR / "尺寸库候选.csv")
    validation["correct_sha256"] = sha256(OUTPUT_DIR / "correct.csv")
    validation["correct_matches_candidate"] = (
        validation["candidate_sha256"] == validation["correct_sha256"]
    )
    validation["source_unchanged"] = sha256(SOURCE) == source_hash
    (OUTPUT_DIR / "验证.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_report(OUTPUT_DIR / "报告.md", validation)
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
