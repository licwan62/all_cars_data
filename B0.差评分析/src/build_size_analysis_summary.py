"""Build the manually reviewable vehicle-cover size complaint summary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "data" / "00.差评分析汇总.csv"
RULES = PROJECT / "data" / "尺寸分析筛选规则.json"
OUTPUT = PROJECT / "data" / "01.尺寸分析汇总表.csv"
REVIEW_OUTPUT = PROJECT / "data" / "02.尺寸问题复核表.csv"
# The maintained analysis table moved to the node's stable output.  Keep the
# path deterministic so merely importing this module does not depend on an
# unrelated non-numbered CSV being present in data/.
ANALYSIS = PROJECT / "output" / "差评分析表.csv"

SOURCE_FIELDS = ("英文", "翻译", "差评点")
OUTPUT_FIELDS = (
    "尺寸分析主键", "差评汇总外键", "差评分析表-品牌", "差评分析表-车型", "差评分析表-结构",
    "车型", "实际尺寸", "尺寸问题方向", "描述", "判定方式",
)
REVIEW_FIELDS = (
    "尺寸问题复核主键", "差评汇总外键", "车型", "实际尺寸", "问题对象", "复核原因", "英文", "翻译", "差评点",
)
ENGLISH_SIZE_PATTERN = re.compile(
    r"\b(?:does(?:\s+not|n't)|did\s+not|won't|will\s+not|cannot|can't)\s+(?:fit|cover)\b"
    r"|\b(?:too|way|much|far)\s+(?:small|large|big|short|long|tight|loose|narrow|wide)\b"
    r"|\b(?:fit|fits|fitting)\s+(?:poorly|badly|wrong|incorrectly)\b"
    r"|\b(?:doesn't|does not)\s+(?:line up|align)\b",
    re.IGNORECASE,
)
ACCESSORY_PATTERN = re.compile(r"\b(?:sun\s*shade|windshield|window|storage\s+bag)\b", re.IGNORECASE)
NON_VEHICLE_PATTERN = re.compile(r"\b(?:motorcycle|motorbike|moped|harley|bike)\b", re.IGNORECASE)


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().casefold()


def stable_key(prefix: str, values: tuple[str, ...]) -> str:
    payload = "\x1f".join(normalise(value) for value in values).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(payload).hexdigest()[:12].upper()}"


def add_raw_keys(rows: list[dict[str, str]]) -> None:
    occurrences: dict[str, int] = {}
    for row in rows:
        key = stable_key(
            "B0-RAW",
            (row.get("来源工作表", ""), row.get("店铺", ""), row.get("评论日期/站内信购买日期", ""),
             row.get("链接/订单编号", ""), row.get("订单编号", ""), row.get("SKU/ASIN", ""), row.get("英文", ""), row.get("翻译", "")),
        )
        occurrences[key] = occurrences.get(key, 0) + 1
        row["差评汇总主键"] = key if occurrences[key] == 1 else f"{key}-{occurrences[key]:02d}"


def _word_in(needle: str, haystack: str) -> bool:
    """True if `needle` occurs in `haystack` at word boundaries (not as a loose substring).

    A naive substring check let one-letter/short model names (e.g. MG "B", Lexus
    "ES") spuriously match almost any raw description, which is why the old
    hash-based 差评分析主键/差评分析表外键 pair rarely lined up (see B0.差评分析
    AGENTS.md 迁移记录 for context).
    """
    if not needle:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack) is not None


def match_analysis_row(row: dict[str, str], analysis_rows: list[dict[str, str]]) -> dict[str, str] | None:
    """Find the single 差评分析表.csv row (品牌+车型+结构) this raw complaint's 车型 identifies.

    自然键（品牌+车型+结构）本身就是 差评分析表.csv 的主键，不需要另造一个哈希列；这里直接
    返回匹配到的那一行，调用方把 品牌/车型/结构 原样写进输出，可以直接用肉眼核对。
    """
    raw_model = normalise(row.get("车型", ""))
    if not raw_model or raw_model in {"0", "/"}:
        return None
    candidates = [
        candidate for candidate in analysis_rows
        if _word_in(normalise(candidate.get("车型", "")), raw_model)
    ]
    # Prefer candidates whose brand also appears in the raw description; this
    # resolves cases like "BMW X5" matching both BMW/X5 and an unrelated model
    # whose own 车型 happens to be a short word contained in the text.
    with_brand = [c for c in candidates if _word_in(normalise(c.get("品牌", "")), raw_model)]
    final = with_brand or candidates
    return final[0] if len(final) == 1 else None


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def signals_in(text: str, signals: list[str]) -> list[str]:
    folded = normalise(text)
    return [signal for signal in signals if normalise(signal) in folded]


def describe_size_issue(row: dict[str, str], direction: str) -> str:
    """Return a concise Chinese description grounded only in English/translation text."""
    text = normalise(" ".join((row.get("英文", ""), row.get("翻译", ""))))
    if any(token in text for token in ("too short", "太短", "偏短", "不够长")):
        description = "车罩偏短，无法完整覆盖"
    elif any(token in text for token in ("too narrow", "太窄", "不够宽")):
        description = "车罩过窄，无法完整覆盖"
    elif direction == "偏小":
        description = "车罩偏小或过紧，贴合不足"
    elif direction == "偏大":
        description = "车罩偏大或松垮，贴合不足"
    else:
        description = "车罩尺寸或版型不符"
    if any(token in text for token in ("mirror", "后视镜")):
        description += "，后视镜位不对"
    if any(token in text for token in ("bumper", "保险杠")) and "完整覆盖" not in description:
        description += "，无法完整覆盖"
    return description[:50]


def infer_direction(row: dict[str, str], rules: dict) -> str:
    text = " ".join(row.get(field, "") for field in SOURCE_FIELDS)
    for label, signals in rules["size_direction"].items():
        if signals_in(text, signals):
            return label
    return "尺寸或版型不符"


def semantic_classification(row: dict[str, str], rules: dict) -> tuple[str, str] | None:
    """Classify English fit complaints missed by the strict same-field keyword rule."""
    english = row.get("英文", "")
    if not ENGLISH_SIZE_PATTERN.search(english):
        return None
    if ACCESSORY_PATTERN.search(english):
        return "配件尺寸问题", "英文明确为遮阳挡、车窗或收纳袋尺寸问题"
    if NON_VEHICLE_PATTERN.search(english):
        return "非整车车罩", "英文明确为摩托车或自行车类产品"
    model = normalise(row.get("车型", ""))
    if model and model not in {"0", "/"}:
        return "车辆主体车罩", "英文明确描述车辆适配或尺寸问题"
    return "待人工判断", "英文明确尺寸/适配问题，但缺少可确认的车辆主体对象"


def select_row(row: dict[str, str], rules: dict) -> tuple[str, str, str] | None:
    texts = {field: row.get(field, "") for field in SOURCE_FIELDS}
    combined = " ".join(texts.values())
    size_hits = signals_in(combined, rules["main_size_signals"])
    if not size_hits:
        return None
    cover_hits = signals_in(combined, rules["main_cover_signals"])
    fields_with_main_fit_evidence = [
        field for field, value in texts.items()
        if signals_in(value, rules["main_size_signals"])
        and signals_in(value, rules["main_cover_signals"])
    ]
    # A complaint limited to an accessory size is not evidence that the vehicle cover itself is mis-sized.
    main_cover_context = bool(cover_hits) and bool(fields_with_main_fit_evidence)
    if not main_cover_context:
        return None
    direction = infer_direction(row, rules)
    evidence = []
    for field, value in texts.items():
        hits = signals_in(value, rules["main_size_signals"])
        if hits:
            evidence.append(f"{field}：{'、'.join(hits[:3])}")
    return "车辆主体尺寸不合适", direction, "；".join(evidence)


def build(source: Path, rules_path: Path, output: Path, analysis: Path, review_output: Path = REVIEW_OUTPUT) -> tuple[int, int]:
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    # Re-read header separately; DictReader has consumed it.
    with source.open(encoding="utf-8-sig", newline="") as handle:
        raw_fields = list(csv.DictReader(handle).fieldnames or [])
    with analysis.open(encoding="utf-8-sig", newline="") as handle:
        analysis_rows = list(csv.DictReader(handle))
    add_raw_keys(rows)
    write_csv(source, rows, [*raw_fields, "差评汇总主键"] if "差评汇总主键" not in raw_fields else raw_fields)
    # 差评分析表.csv 是人工维护的文件，本节点只读不写；它的主键就是自身已校验唯一的
    # 品牌+车型+结构，不需要再造一列哈希主键（历史上加过 差评分析主键，因匹配逻辑用宽松
    # 子串比对，绝大多数行匹配不上，已删除，见 AGENTS.md 迁移记录）。
    selected, review = [], []
    for row in rows:
        result = select_row(row, rules)
        if result:
            decision, direction, evidence = result
            matched = match_analysis_row(row, analysis_rows)
            selected.append({
                "判定": decision,
                "尺寸分析主键": stable_key("B0-SIZE", (row["差评汇总主键"], direction)),
                "差评汇总外键": row["差评汇总主键"],
                "差评分析表-品牌": matched.get("品牌", "") if matched else "",
                "差评分析表-车型": matched.get("车型", "") if matched else "",
                "差评分析表-结构": matched.get("结构", "") if matched else "",
                "车型": row.get("车型", ""),
                "实际尺寸": row.get("实际尺寸", ""),
                "尺寸问题方向": direction,
                "描述": describe_size_issue(row, direction),
                "判定方式": "字段证据",
                "筛选依据": evidence,
                **row,
            })
            continue
        semantic = semantic_classification(row, rules)
        if not semantic:
            continue
        category, reason = semantic
        if category == "车辆主体车罩":
            direction = infer_direction(row, rules)
            matched = match_analysis_row(row, analysis_rows)
            selected.append({
                "尺寸分析主键": stable_key("B0-SIZE", (row["差评汇总主键"], direction)),
                "差评汇总外键": row["差评汇总主键"],
                "差评分析表-品牌": matched.get("品牌", "") if matched else "",
                "差评分析表-车型": matched.get("车型", "") if matched else "",
                "差评分析表-结构": matched.get("结构", "") if matched else "",
                "车型": row.get("车型", ""),
                "实际尺寸": row.get("实际尺寸", ""),
                "尺寸问题方向": direction,
                "描述": describe_size_issue(row, direction),
                "判定方式": "英文语义",
            })
        else:
            review.append({
                "尺寸问题复核主键": stable_key("B0-SIZE-REVIEW", (row["差评汇总主键"], category)),
                "差评汇总外键": row["差评汇总主键"],
                "车型": row.get("车型", ""), "实际尺寸": row.get("实际尺寸", ""),
                "问题对象": category, "复核原因": reason,
                "英文": row.get("英文", ""), "翻译": row.get("翻译", ""), "差评点": row.get("差评点", ""),
            })
    selected.sort(key=lambda row: (row.get("车型", ""), row.get("评论日期/站内信购买日期", ""), row.get("链接/订单编号", "")))
    write_csv(output, selected, list(OUTPUT_FIELDS))
    write_csv(review_output, review, list(REVIEW_FIELDS))
    return len(selected), len(review)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成车辆主体尺寸不合适的差评汇总表")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--rules", type=Path, default=RULES)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--analysis", type=Path, default=ANALYSIS)
    parser.add_argument("--review-output", type=Path, default=REVIEW_OUTPUT)
    args = parser.parse_args()
    count, review_count = build(args.source, args.rules, args.output, args.analysis, args.review_output)
    print(f"已生成 {args.output}：{count} 条车辆主体尺寸问题；复核表 {review_count} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
