from __future__ import annotations

import csv
import json
import re
import shutil
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "00.差评分析汇总.csv"
SIZE = ROOT / "data" / "01.差评分析精选.csv"
RULES = ROOT / "data" / "车型语义修复映射.json"
ARTIFACTS_DIR = ROOT / "artifacts"
PLACEHOLDERS = {"", "0", "/", "未知"}


def next_artifact_dir(artifacts_dir: Path, description: str) -> Path:
    """与 run.py 相同的批次命名规则，保证同一 artifacts/ 目录下批次号不冲突、不覆盖。"""
    prefix = f"{date.today().isoformat()}_"
    used = [
        int(match.group(1))
        for path in artifacts_dir.glob(f"{prefix}*")
        if (match := re.match(rf"^{re.escape(prefix)}(\d{{2}})_", path.name))
    ]
    return artifacts_dir / f"{prefix}{max(used, default=0) + 1:02d}_model-semantic-repair"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def apply_repairs(artifacts_dir: Path = ARTIFACTS_DIR) -> tuple[int, int]:
    """就地回填 00 表车型、同步 01 表，并按仓库约定的 artifacts/<批次>/ 结构留痕。

    这是一次性人工数据修正（不在 run.py 常规 run 流程里），但仍需遵守根目录 AGENTS.md：
    每次运行先创建不可覆盖的 artifacts/<批次>/、备份改写前的输入，再写 status.json。
    """
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifact = next_artifact_dir(artifacts_dir, "model-semantic-repair")
    (artifact / "input").mkdir(parents=True)
    for source in (RAW, SIZE, RULES):
        if source.is_file():
            shutil.copy2(source, artifact / "input")

    rules = json.loads(RULES.read_text(encoding="utf-8"))["记录"]
    raw_fields, raw_rows = read_csv(RAW)
    by_key = {row["差评汇总主键"]: row for row in raw_rows}
    missing = sorted(set(rules) - set(by_key))
    if missing:
        raise ValueError(f"修复映射包含不存在的主键: {missing}")

    changed_raw = 0
    for key, repair in rules.items():
        row = by_key[key]
        current = row["车型"].strip()
        is_brand_prefix_completion = current and repair["车型"].strip().endswith(current)
        if current not in PLACEHOLDERS and current != repair["车型"] and not is_brand_prefix_completion:
            raise ValueError(f"{key} 已有不同车型，拒绝覆盖: {current}")
        if current != repair["车型"]:
            changed_raw += 1
        row["车型"] = repair["车型"]
        row["原车型"] = repair["车型"]
        row["车型修复依据"] = repair["依据"]
        if repair["年份"]:
            row["提取年份"] = repair["年份"]
        row["皮卡信息提取依据"] = "英文/翻译语义"

    size_fields, size_rows = read_csv(SIZE)
    changed_size = 0
    for row in size_rows:
        key = row["差评汇总外键"]
        if key not in rules:
            continue
        model = rules[key]["车型"]
        if row["车型"].strip() != model:
            row["车型"] = model
            changed_size += 1

    write_csv(RAW, raw_fields, raw_rows)
    write_csv(SIZE, size_fields, size_rows)

    (artifact / "output").mkdir(parents=True)
    shutil.copy2(RAW, artifact / "output" / RAW.name)
    shutil.copy2(SIZE, artifact / "output" / SIZE.name)
    status = {
        "status": "passed",
        "00表车型更新": changed_raw,
        "01表车型同步": changed_size,
        "修复映射条数": len(rules),
    }
    (artifact / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed_raw, changed_size


if __name__ == "__main__":
    raw_count, size_count = apply_repairs()
    print(f"00表车型更新: {raw_count}; 01表车型同步: {size_count}")
