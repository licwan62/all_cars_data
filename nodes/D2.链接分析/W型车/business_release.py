"""Create the business-facing W-car release keyed by the approved SKU codes.

This does not rerun clustering, year merging or allocation.  It reads the
slimmed 0915.5 artifact, replaces SKU_NAME with ``data/SKU修改.csv`` and splits
the mixed tables into shipment, quality-check and adjustment tables that join
on SKU_NAME, plus one summary table for daily use.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from rename_to_new_size_codes import SIZE_RENAMES
from run import read_csv, read_table, write_table


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "artifacts" / "0915.5-slim-new-size-codes"
TARGET = ROOT / "artifacts" / "0915.6-SKU编码-业务目录"
SKU_RENAMES = ROOT / "data" / "SKU修改.csv"

SHIPMENT_DIR = "1_发货量"
CHECK_DIR = "2_质量检测"
ADJUSTMENT_DIR = "3_调整记录"
DETAIL_DIR = "4_底层明细"
SUMMARY_FILE = "SKU汇总表.csv"
SUMMARY_COLUMNS = [
    "SKU_NAME", "链接名称", "适配车型", "适配年份", "尺码", "发货数量", "预估销量", "销量占比",
    "车长(mm)", "车宽(mm)", "车高(mm)", "尺寸集中度", "适配记录数", "年份合并结论", "原SKU_NAME", "聚类ID",
]


def match_sku_renames(listing: list[dict[str, str]], renames: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """Map each listing CLUSTER_ID to its business SKU row.

    The business file names a vehicle by 车型 plus either the full fitment years
    or the first-last span used in 链接名称; every listing row must match once.
    """
    matched: dict[str, dict[str, str]] = {}
    for rename in renames:
        candidates = [
            row for row in listing
            if row["适配车型"] == rename["车型"]
            and rename["年份"] in (row["适配年份"], row["链接名称"].removeprefix(row["适配车型"] + " "))
        ]
        if len(candidates) != 1:
            raise ValueError(f"SKU修改 {rename['车型']} {rename['年份']} 匹配到 {len(candidates)} 条链接")
        cluster_id = candidates[0]["CLUSTER_ID"]
        if cluster_id in matched:
            raise ValueError(f"链接 {candidates[0]['SKU_NAME']} 被多条 SKU修改 匹配")
        if rename["尺寸"].removesuffix("-0") != candidates[0]["尺码"]:
            raise ValueError(f"SKU修改 {rename['车型']} {rename['年份']} 的尺寸 {rename['尺寸']} 与链接尺码 {candidates[0]['尺码']} 不符")
        matched[cluster_id] = rename
    missing = [row["SKU_NAME"] for row in listing if row["CLUSTER_ID"] not in matched]
    if missing:
        raise ValueError(f"SKU修改 缺少链接：{missing}")
    if len({rename["SKU输出"] for rename in renames}) != len(renames):
        raise ValueError("SKU修改 的 SKU输出 有重复")
    return matched


def value_range(row: dict[str, str], name: str) -> str:
    low, high = row[f"{name}最小毫米"], row[f"{name}最大毫米"]
    return low if low == high else f"{low}-{high}"


def with_sku(rows: list[dict[str, str]], id_column: str, sku_by_cluster: dict[str, str]) -> list[dict[str, str]]:
    return [{"SKU_NAME": sku_by_cluster.get(row[id_column], ""), **row} for row in rows]


def build(source: Path, target: Path, sku_rename_path: Path) -> None:
    listing = read_csv(source / "05_输出" / "链接发货适配表.csv")
    master = {row["聚类ID"]: row for row in read_csv(source / "02_聚类数据" / "聚类主表.csv")}
    renames = match_sku_renames(listing, read_csv(sku_rename_path))
    sku_by_cluster = {cluster_id: rename["SKU输出"] for cluster_id, rename in renames.items()}
    for folder in (SHIPMENT_DIR, CHECK_DIR, ADJUSTMENT_DIR, DETAIL_DIR):
        (target / folder).mkdir(parents=True)

    skus = []
    for row in listing:
        source_row = master[row["CLUSTER_ID"]]
        skus.append({**source_row, **row, "SKU_NAME": sku_by_cluster[row["CLUSTER_ID"]], "原SKU_NAME": row["SKU_NAME"]})

    # 发货量：只放分配口径与结果。
    write_table(target / SHIPMENT_DIR / "SKU发货量.csv", [
        "SKU_NAME", "尺码", "预估销量", "销量倍率", "加权销量", "销量占比", "理论发货量", "发货数量", "取整补量",
    ], skus)
    shutil.copyfile(source / "05_输出" / "尺码发货汇总.csv", target / SHIPMENT_DIR / "尺码发货汇总.csv")
    unshipped = [
        {**row, "尺码": row["逻辑尺码"], "销量占比": row["全局销量占比"]}
        for cluster_id, row in master.items() if cluster_id not in sku_by_cluster
    ]
    write_table(target / SHIPMENT_DIR / "未发货车型.csv", [
        "聚类ID", "链接名称", "尺码", "预估销量", "销量倍率", "加权销量", "销量占比", "理论发货量", "发货数量",
    ], unshipped)

    # 质量检测：尺寸范围与合并测试证据。
    write_table(target / CHECK_DIR / "SKU尺寸检测.csv", [
        "SKU_NAME", "适配记录数", "车长最小毫米", "车长最大毫米", "车宽最小毫米", "车宽最大毫米",
        "车高最小毫米", "车高最大毫米", "尺寸集中度",
    ], skus)
    columns, rows = read_table(source / "04_校验报告" / "聚类合并校验.csv")
    write_table(target / CHECK_DIR / "聚类合并检测.csv", ["SKU_NAME", *columns], with_sku(rows, "新聚类ID", sku_by_cluster))
    columns, rows = read_table(source / "04_校验报告" / "年份合并校验.csv")
    write_table(target / CHECK_DIR / "年份合并检测.csv", ["SKU_NAME", *columns], with_sku(rows, "聚类ID", sku_by_cluster))
    siblings = [{
        "SKU_NAME": sku_by_cluster.get(row["CLUSTER_ID"], ""), "聚类ID": row["CLUSTER_ID"], "链接名称": row["链接名称"],
        "兄弟SKU_NAME": sku_by_cluster.get(row["兄弟CLUSTER_ID"], ""), "兄弟聚类ID": row["兄弟CLUSTER_ID"],
        "兄弟链接名称": row["兄弟链接名称"], "分开原因": row["分开原因"],
    } for row in read_csv(source / "02_聚类数据" / "关联链接明细.csv")]
    write_table(target / CHECK_DIR / "兄弟链接分开原因.csv", list(siblings[0]), siblings)

    # 调整记录：SKU 编码、尺码名称与年份的改动。
    write_table(target / ADJUSTMENT_DIR / "SKU编码调整.csv", ["SKU_NAME", "原SKU_NAME", "聚类ID", "业务车型", "业务年份", "业务尺寸"], [
        {"SKU_NAME": row["SKU_NAME"], "原SKU_NAME": row["原SKU_NAME"], "聚类ID": row["CLUSTER_ID"],
         "业务车型": renames[row["CLUSTER_ID"]]["车型"], "业务年份": renames[row["CLUSTER_ID"]]["年份"],
         "业务尺寸": renames[row["CLUSTER_ID"]]["尺寸"]}
        for row in skus
    ])
    write_table(target / ADJUSTMENT_DIR / "尺码名称调整.csv", ["老尺码", "新尺码", "尺码代码"], [
        {"老尺码": old, "新尺码": new, "尺码代码": code} for old, (new, code) in SIZE_RENAMES.items()
    ])
    write_table(target / ADJUSTMENT_DIR / "年份调整.csv", [
        "SKU_NAME", "原始年份", "命名年份", "适配年份", "年份合并结论", "新增年份数",
    ], skus)

    # 底层明细：车型年份原子事实，按 SKU 可查。
    columns, rows = read_table(source / "02_聚类数据" / "聚类原子明细.csv")
    atoms = [{"SKU_NAME": sku_by_cluster.get(row["CLUSTER_ID"], ""), "聚类ID": row["CLUSTER_ID"], **row} for row in rows]
    write_table(target / DETAIL_DIR / "车型适配明细.csv", ["SKU_NAME", "聚类ID", *[c for c in columns if c != "CLUSTER_ID"]], atoms)

    write_table(target / SUMMARY_FILE, SUMMARY_COLUMNS, [{
        **row, "车长(mm)": value_range(row, "车长"), "车宽(mm)": value_range(row, "车宽"), "车高(mm)": value_range(row, "车高"),
    } for row in skus])
    validate(target, len(master))
    write_notes(target, skus, renames)


def validate(target: Path, cluster_count: int) -> None:
    summary = read_csv(target / SUMMARY_FILE)
    keys = [row["SKU_NAME"] for row in summary]
    if len(set(keys)) != len(keys) or "" in keys:
        raise ValueError("SKU汇总表 的 SKU_NAME 不唯一或为空")
    for path in (
        target / SHIPMENT_DIR / "SKU发货量.csv", target / CHECK_DIR / "SKU尺寸检测.csv",
        target / ADJUSTMENT_DIR / "SKU编码调整.csv", target / ADJUSTMENT_DIR / "年份调整.csv",
    ):
        if [row["SKU_NAME"] for row in read_csv(path)] != keys:
            raise ValueError(f"{path.name} 的 SKU_NAME 与 SKU汇总表 不一致")
    shipments = {row["SKU_NAME"]: row for row in read_csv(target / SHIPMENT_DIR / "SKU发货量.csv")}
    if any(row["发货数量"] != shipments[row["SKU_NAME"]]["发货数量"] for row in summary):
        raise ValueError("SKU汇总表 的发货数量与 SKU发货量 不一致")
    unshipped = read_csv(target / SHIPMENT_DIR / "未发货车型.csv")
    if len(summary) + len(unshipped) != cluster_count or any(row["发货数量"] != "0" for row in unshipped):
        raise ValueError("SKU 与未发货车型合计不等于全部聚类")
    total = read_csv(target / SHIPMENT_DIR / "尺码发货汇总.csv")[-1]
    if sum(int(row["发货数量"]) for row in summary) != int(total["发货数量"]):
        raise ValueError("SKU汇总表 发货数量合计与尺码发货汇总不一致")


def write_notes(target: Path, skus: list[dict[str, str]], renames: dict[str, dict[str, str]]) -> None:
    irregular = [
        rename["SKU输出"] for rename in renames.values()
        if rename["SKU输出"].split("-")[1] not in {"", *(code for _, code in SIZE_RENAMES.values())}
    ]
    lines = [
        "# W 型车发货方案（业务版）", "",
        f"- 来源：`{SOURCE.name}`，未重跑聚类、年份合并与分配；SKU_NAME 按 `data/SKU修改.csv` 替换为业务编码。",
        f"- SKU 数：{len(skus)}，发货合计：{sum(int(row['发货数量']) for row in skus):,}。",
        "- 所有表以 SKU_NAME 关联；聚类级的检测表和明细里，未发货聚类的 SKU_NAME 为空。",
        *(["- 待业务确认：以下 SKU 编码尺码代码后缺少 `-`，按原值使用：" + "、".join(f"`{sku}`" for sku in irregular)] if irregular else []),
        "",
        "## 文件", "",
        f"- `{SUMMARY_FILE}`：最终汇总，一行一个 SKU，含适配车型年份、尺码、发货数量、尺寸范围和年份合并结论。",
        f"- `{SHIPMENT_DIR}/`：`SKU发货量.csv`（分配口径与取整）、`尺码发货汇总.csv`、`未发货车型.csv`（分到 0 件的聚类）。",
        f"- `{CHECK_DIR}/`：`SKU尺寸检测.csv`、`聚类合并检测.csv`、`年份合并检测.csv`、`兄弟链接分开原因.csv`。",
        f"- `{ADJUSTMENT_DIR}/`：`SKU编码调整.csv`（新旧 SKU 对照）、`尺码名称调整.csv`、`年份调整.csv`。",
        f"- `{DETAIL_DIR}/`：`车型适配明细.csv`（每个 SKU 覆盖的车型年份与尺寸原子记录）。",
    ]
    (target / "说明.md").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main() -> None:
    if TARGET.exists():
        if "--replace" not in sys.argv:
            raise FileExistsError(f"refusing to overwrite existing artifact: {TARGET}")
        if TARGET.parent != ROOT / "artifacts" or TARGET.name != "0915.6-SKU编码-业务目录":
            raise RuntimeError(f"unexpected replacement target: {TARGET}")
        # 只清空内容：Windows 上目录本身常被资源管理器或编辑器占用，无法删除。
        for child in TARGET.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    try:
        build(SOURCE, TARGET, SKU_RENAMES)
    except Exception:
        shutil.rmtree(TARGET, ignore_errors=True)
        raise
    print(TARGET)


if __name__ == "__main__":
    main()
