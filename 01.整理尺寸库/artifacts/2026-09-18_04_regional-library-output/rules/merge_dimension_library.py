"""把 US/EU/RU 三个区域各自压缩去重后的 00_XX尺寸库.csv 合并为
output/尺寸库.csv，供下游节点（分类结构审核、02.车形分类核定、02.销量评估、
03.尺码计算……）统一读取。

三条产线各自的建库规则相互独立（各区域自己的 source 解析、去重口径都在各自
的 code 里，不在这里做任何跨区域改写），这里只做：
- 找到每个区域最新批次目录下唯一的 00_*.csv；
- 三个区域均使用 id_scheme.append_country_code 加上 " US"/" EU"/" RU"
  后缀，避免跨区域撞车；
- EU、RU 的“参考车型”和“备注”保持为空，US 保留原始内容；
- 按区域、DIMENSION-ID 排序后拼接。

注意：下游如果按 `dimension_id(row) == row["DIMENSION-ID"]` 做强校验，需要
先用 `id_scheme.base_dimension_id` 去掉区域后缀再比较（02.销量评估的
expand_years.py 会直接跳过带后缀的行；02.车形分类核定/validate_project.py
已经改成用 base_dimension_id 比较）。
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
ROOT = PROJECT_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from id_scheme import append_country_code  # noqa: E402
from regional_size_common import DIMENSION_COLUMNS, RegionalDataError, read_csv  # noqa: E402

REGIONS = ("us", "eu", "ru")
STRUCTURE_RULES_PATH = PROJECT_DIR / "data" / "structure_normalization.json"


def load_structure_rules() -> dict[str, object]:
    payload = json.loads(STRUCTURE_RULES_PATH.read_text(encoding="utf-8"))
    required = {"schema_version", "field", "regions", "transformations"}
    if not required.issubset(payload):
        missing = ", ".join(sorted(required - set(payload)))
        raise RegionalDataError(f"结构规范化规则缺少字段：{missing}")
    if payload["field"] != "结构":
        raise RegionalDataError("结构规范化规则的 field 必须为‘结构’")
    return payload


def normalize_structure(value: str, rules: dict[str, object]) -> str:
    normalized = str(value or "").strip()
    for transformation in rules["transformations"]:
        normalized = re.sub(
            transformation["pattern"], transformation["replacement"], normalized,
            flags=re.IGNORECASE,
        )
    return re.sub(r"\s+", " ", normalized).strip()


def latest_batch(region: str) -> Path:
    region_dir = PROJECT_DIR / "data" / region
    batches = sorted(path for path in region_dir.iterdir() if path.is_dir())
    if not batches:
        raise RegionalDataError(f"data/{region} 下没有批次目录")
    return batches[-1]


def region_library_path(region: str) -> Path:
    batch = latest_batch(region)
    candidates = sorted(batch.glob("00_*.csv"))
    if len(candidates) != 1:
        raise RegionalDataError(f"{batch} 应且仅应包含一份 00_*.csv，实际为 {len(candidates)}")
    return candidates[0]


def load_region(region: str) -> list[dict[str, str]]:
    path = region_library_path(region)
    frame = read_csv(path)
    if list(frame.columns) != DIMENSION_COLUMNS:
        raise RegionalDataError(f"{path} 字段与 DIMENSION_COLUMNS 不一致：{list(frame.columns)}")
    rows = frame.to_dict("records")
    code = region.upper()
    structure_rules = load_structure_rules()
    normalize_region = region.lower() in structure_rules["regions"]
    for row in rows:
        row["DIMENSION-ID"] = append_country_code(row["DIMENSION-ID"], code)
        if normalize_region:
            row["结构"] = normalize_structure(row["结构"], structure_rules)
        if code in {"EU", "RU"}:
            row["参考车型"] = ""
            row["备注"] = ""
    seen: set[str] = set()
    for row in rows:
        if row["DIMENSION-ID"] in seen:
            raise RegionalDataError(f"{path} 合并后 DIMENSION-ID 重复：{row['DIMENSION-ID']}")
        seen.add(row["DIMENSION-ID"])
    return rows


def merge(regions: tuple[str, ...] = REGIONS) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    seen: set[str] = set()
    for region in regions:
        rows = load_region(region)
        for row in rows:
            if row["DIMENSION-ID"] in seen:
                raise RegionalDataError(f"跨区域 DIMENSION-ID 冲突：{row['DIMENSION-ID']}")
            seen.add(row["DIMENSION-ID"])
        merged.extend(rows)
    merged.sort(key=lambda row: (regions.index(_region_of(row["DIMENSION-ID"])), row["DIMENSION-ID"]))
    return merged


def next_artifact_dir() -> Path:
    prefix = f"{date.today():%Y-%m-%d}_"
    existing = [path.name for path in (PROJECT_DIR / "artifacts").glob(f"{prefix}*") if path.is_dir()]
    sequence = max((int(name[len(prefix):len(prefix) + 2]) for name in existing if name[len(prefix):len(prefix) + 2].isdigit()), default=0) + 1
    return PROJECT_DIR / "artifacts" / f"{prefix}{sequence:02d}_regional-library-output"


def _region_of(record_id: str) -> str:
    last_token = record_id.rsplit(" ", 1)[-1].upper()
    if last_token not in {"US", "EU", "RU"}:
        raise RegionalDataError(f"DIMENSION-ID 缺少区域后缀：{record_id}")
    return last_token.lower()


def write_csv_atomic(path: Path, rows: list[dict[str, str]]) -> None:
    """Write one stable handoff file without exposing a partial CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8-sig", newline="", dir=path.parent, delete=False
    ) as handle:
        temporary_path = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=DIMENSION_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary_path.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="合并 US/EU/RU 尺寸库为 output/尺寸库.csv")
    parser.add_argument("--output", type=Path, default=PROJECT_DIR / "output" / "尺寸库.csv")
    parser.add_argument(
        "--output-dir", type=Path, default=PROJECT_DIR / "output",
        help="区域尺寸库输出目录（写入 US尺寸库.csv、EU尺寸库.csv、RU尺寸库.csv）",
    )
    parser.add_argument("--artifact-dir", type=Path, help="本次不可变运行归档目录")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        merged = merge()
    except RegionalDataError as error:
        print(f"尺寸库合并失败：{error}", file=sys.stderr)
        return 2
    output_path = args.output.resolve()
    output_dir = args.output_dir.resolve()
    artifact_dir = (args.artifact_dir or next_artifact_dir()).resolve()
    if artifact_dir.exists():
        print(f"归档目录已存在，不允许覆盖：{artifact_dir}", file=sys.stderr)
        return 2
    region_rows = {region: load_region(region) for region in REGIONS}
    # All validation happens before touching stable output files.
    artifact_output = artifact_dir / "output"
    artifact_inputs = artifact_dir / "inputs"
    for region in REGIONS:
        source_path = region_library_path(region)
        target = artifact_inputs / region / source_path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target)
    rules_snapshot = artifact_dir / "rules"
    rules_snapshot.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), rules_snapshot / Path(__file__).name)
    shutil.copy2(PROJECT_DIR / "AGENTS.md", rules_snapshot / "AGENTS.md")
    shutil.copy2(STRUCTURE_RULES_PATH, rules_snapshot / STRUCTURE_RULES_PATH.name)
    for region, rows in region_rows.items():
        write_csv_atomic(artifact_output / f"{region.upper()}尺寸库.csv", rows)
    write_csv_atomic(artifact_output / "尺寸库.csv", merged)
    (artifact_dir / "status.json").write_text(
        json.dumps({"status": "validated", "rows": {region.upper(): len(rows) for region, rows in region_rows.items()}}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for region, rows in region_rows.items():
        write_csv_atomic(output_dir / f"{region.upper()}尺寸库.csv", rows)
    write_csv_atomic(output_path, merged)
    counts = ", ".join(f"{region.upper()}={len(rows)}" for region, rows in region_rows.items())
    print(f"合并完成：{counts}；合并={len(merged)} 行 -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
