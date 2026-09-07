#!/usr/bin/env python3
"""使用三套 07 版库存尺码，按半周长差值独立匹配车型尺寸库。"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
RULE_SOURCE_DIR_NAME = "source"
PUBLISH_DIR_NAME = "source-0903"
COVER_FILE = "07-车衣数据.csv"
DIMENSION_FILE = "尺寸库.csv"
PARAMETER_FILE = "参数.csv"
RULESETS = {
    "all-07": "all-07.csv",
    "hnt-07": "hnt-07.csv",
    "tm-07": "tm-07.csv",
}
MM_PER_INCH = 25.4
CM_TO_MM = 10.0
COVER_ALLOWANCE_MM = 1500.0
REQUIRED_SOURCE_COLUMNS = {"DIMENSION-ID", "分类", "L-IN", "H-IN"}
REQUIRED_RULE_COLUMNS = {"内部尺码", "档位序号", "分类"}
REQUIRED_COVER_COLUMNS = {"型号", "侧片长"}

# 07 库存规则名与车衣数据型号之间能够明确确认的特殊命名差异。
EXPLICIT_COVER_ALIASES = {
    "3XL+0": "3XL+-0",
}


@dataclass(frozen=True)
class Parameters:
    lower: float
    upper: float

    def as_dict(self) -> dict[str, float]:
        return {
            "半周长余量下限": self.lower,
            "半周长余量上限": self.upper,
        }


@dataclass(frozen=True)
class Rule:
    line_no: int
    internal_size: str
    common_size: str
    sequence: float
    category: str
    cab: str
    note: str
    cover_model: str | None
    side_length_cm: float | None
    cover_half_perimeter_mm: float | None

    @property
    def identity(self) -> tuple[object, ...]:
        return (
            self.internal_size,
            self.common_size,
            self.sequence,
            self.category,
            self.cab,
            self.note,
            self.cover_model,
            self.side_length_cm,
            self.cover_half_perimeter_mm,
        )


def clean_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def parse_number(value: object) -> float | None:
    text = clean_text(value)
    if not text or text in {"—", "-", "–"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def number_text(value: float | None) -> str:
    if value is None:
        return ""
    rounded = round(value, 3)
    if float(rounded).is_integer():
        return str(int(rounded))
    return f"{rounded:.3f}".rstrip("0").rstrip(".")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"空 CSV：{path}")
        return list(reader.fieldnames), [dict(row) for row in reader]


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def require_columns(fieldnames: Iterable[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(fieldnames))
    if missing:
        raise ValueError(f"{label} 缺少字段：{', '.join(missing)}")


def load_parameters(path: Path) -> Parameters:
    fieldnames, rows = read_csv(path)
    require_columns(fieldnames, {"参数", "毫米值"}, path.name)
    values: dict[str, float] = {}
    for index, row in enumerate(rows, start=2):
        name = clean_text(row.get("参数"))
        value = parse_number(row.get("毫米值"))
        if not name or value is None:
            raise ValueError(f"{path.name} 第 {index} 行存在空白或非数字参数")
        if name in values:
            raise ValueError(f"{path.name} 参数重复：{name}")
        values[name] = value
    required = {"半周长余量下限", "半周长余量上限"}
    missing = sorted(required - set(values))
    if missing:
        raise ValueError(f"{path.name} 缺少参数：{', '.join(missing)}")
    lower = values["半周长余量下限"]
    upper = values["半周长余量上限"]
    if lower < 0 or upper <= lower:
        raise ValueError(f"{path.name} 要求 0 <= 半周长余量下限 < 半周长余量上限")
    return Parameters(lower=lower, upper=upper)


def load_cover_sizes(path: Path) -> dict[str, float]:
    fieldnames, rows = read_csv(path)
    require_columns(fieldnames, REQUIRED_COVER_COLUMNS, path.name)
    result: dict[str, float] = {}
    for index, row in enumerate(rows, start=2):
        model = clean_text(row.get("型号"))
        if not model:
            raise ValueError(f"{path.name} 第 {index} 行型号为空")
        if model in result:
            raise ValueError(f"{path.name} 型号重复：{model}")
        side_length = parse_number(row.get("侧片长"))
        if side_length is not None:
            if side_length <= 0:
                raise ValueError(f"{path.name} 第 {index} 行侧片长必须为正数")
            result[model] = side_length
    return result


def cover_alias_candidates(internal_size: str) -> list[str]:
    candidates = [internal_size]
    explicit = EXPLICIT_COVER_ALIASES.get(internal_size)
    if explicit and explicit not in candidates:
        candidates.append(explicit)
    if internal_size.endswith("-0"):
        without_suffix = internal_size[:-2]
        if without_suffix not in candidates:
            candidates.append(without_suffix)
    return candidates


def resolve_cover_size(
    internal_size: str, cover_sizes: Mapping[str, float]
) -> tuple[str | None, float | None, float | None]:
    for candidate in cover_alias_candidates(internal_size):
        side_length_cm = cover_sizes.get(candidate)
        if side_length_cm is not None:
            half_perimeter = side_length_cm * CM_TO_MM + COVER_ALLOWANCE_MM
            return candidate, side_length_cm, half_perimeter
    return None, None, None


def load_rules(
    path: Path, cover_sizes: Mapping[str, float]
) -> tuple[list[str], list[dict[str, str]], list[Rule], list[dict[str, object]]]:
    fieldnames, rows = read_csv(path)
    require_columns(fieldnames, REQUIRED_RULE_COLUMNS, path.name)
    rules: list[Rule] = []
    duplicates: list[dict[str, object]] = []
    seen: dict[tuple[object, ...], Rule] = {}
    for index, row in enumerate(rows, start=2):
        internal_size = clean_text(row.get("内部尺码"))
        sequence = parse_number(row.get("档位序号"))
        category = clean_text(row.get("分类"))
        if not internal_size or sequence is None or not category:
            raise ValueError(f"{path.name} 第 {index} 行存在空白或非数字必填值")
        cover_model, side_length_cm, cover_half_perimeter_mm = resolve_cover_size(
            internal_size, cover_sizes
        )
        rule = Rule(
            line_no=index,
            internal_size=internal_size,
            common_size=clean_text(row.get("通用尺码")),
            sequence=sequence,
            category=category,
            cab=clean_text(row.get("CAB")),
            note=clean_text(row.get("备注")),
            cover_model=cover_model,
            side_length_cm=side_length_cm,
            cover_half_perimeter_mm=cover_half_perimeter_mm,
        )
        prior = seen.get(rule.identity)
        if prior is not None:
            duplicates.append(
                {
                    "重复行": index,
                    "保留行": prior.line_no,
                    "内部尺码": internal_size,
                    "分类": category,
                }
            )
            continue
        seen[rule.identity] = rule
        rules.append(rule)
    rules.sort(key=lambda rule: (rule.category, rule.sequence, rule.line_no))
    return fieldnames, rows, rules, duplicates


def enrich_rule_rows(
    rows: Sequence[Mapping[str, str]], cover_sizes: Mapping[str, float]
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for row in rows:
        internal_size = clean_text(row.get("内部尺码"))
        cover_model, side_length_cm, half_perimeter_mm = resolve_cover_size(
            internal_size, cover_sizes
        )
        result.append(
            {
                **row,
                "车衣数据型号": cover_model or "",
                "侧片长_cm": number_text(side_length_cm),
                "车衣半周长_mm": number_text(half_perimeter_mm),
                "半周长状态": "可参与匹配" if half_perimeter_mm is not None else "缺少可用侧片长",
            }
        )
    return result


def build_pools(rules: Sequence[Rule]) -> dict[str, list[Rule]]:
    pools: dict[str, list[Rule]] = defaultdict(list)
    for rule in rules:
        if rule.cover_half_perimeter_mm is not None:
            pools[rule.category].append(rule)
    for pool in pools.values():
        pool.sort(key=lambda rule: (rule.sequence, rule.line_no))
    return dict(pools)


def record_half_perimeter_mm(row: Mapping[str, str]) -> float | None:
    length_in = parse_number(row.get("L-IN"))
    height_in = parse_number(row.get("H-IN"))
    if length_in is None or height_in is None or length_in <= 0 or height_in <= 0:
        return None
    return (length_in + height_in) * MM_PER_INCH


def difference_mm(rule: Rule, record_half_perimeter: float) -> float:
    assert rule.cover_half_perimeter_mm is not None
    return rule.cover_half_perimeter_mm - record_half_perimeter


def inside_strict_interval(value: float, parameters: Parameters) -> bool:
    return parameters.lower < value < parameters.upper


def interval_distance(value: float, parameters: Parameters) -> float:
    if value <= parameters.lower:
        return parameters.lower - value
    if value >= parameters.upper:
        return value - parameters.upper
    return 0.0


def candidate_text(rule: Rule, difference: float) -> str:
    return (
        f"{rule.internal_size}[档位={number_text(rule.sequence)},"
        f"差值={number_text(difference)}mm]"
    )


def empty_match_result() -> dict[str, object]:
    return {
        "匹配状态": "",
        "匹配池": "",
        "内部尺码": "",
        "通用尺码": "",
        "档位序号": "",
        "规则CAB": "",
        "车衣数据型号": "",
        "侧片长_cm": "",
        "车衣半周长_mm": "",
        "半周长差值_mm": "",
        "半周长余量下限_mm": "",
        "半周长余量上限_mm": "",
        "入池候选": "",
        "最近候选内部尺码": "",
        "最近候选差值_mm": "",
        "距最近边界_mm": "",
        "匹配原因": "",
        "__rule_line": None,
    }


def match_vehicle(
    row: Mapping[str, str],
    pools: Mapping[str, Sequence[Rule]],
    parameters: Parameters,
) -> dict[str, object]:
    result = empty_match_result()
    category = clean_text(row.get("分类"))
    record_half_perimeter = record_half_perimeter_mm(row)
    if record_half_perimeter is None:
        result.update({"匹配状态": "数据不全", "匹配原因": "L-IN/H-IN 缺失或非正数"})
        return result

    pool = list(pools.get(category, ()))
    if not pool:
        result.update(
            {
                "匹配状态": "无可用尺码",
                "匹配池": category,
                "匹配原因": "该分类没有具备可用侧片长的库存尺码",
            }
        )
        return result

    candidates = [(rule, difference_mm(rule, record_half_perimeter)) for rule in pool]
    qualifying = [
        (rule, difference)
        for rule, difference in candidates
        if inside_strict_interval(difference, parameters)
    ]
    if qualifying:
        selected_rule, selected_difference = min(
            qualifying, key=lambda item: (item[0].sequence, item[0].line_no)
        )
        result.update(
            {
                "匹配状态": "已匹配",
                "匹配池": category,
                "内部尺码": selected_rule.internal_size,
                "通用尺码": selected_rule.common_size,
                "档位序号": number_text(selected_rule.sequence),
                "规则CAB": selected_rule.cab,
                "车衣数据型号": selected_rule.cover_model or "",
                "侧片长_cm": number_text(selected_rule.side_length_cm),
                "车衣半周长_mm": number_text(selected_rule.cover_half_perimeter_mm),
                "半周长差值_mm": number_text(selected_difference),
                "半周长余量下限_mm": number_text(parameters.lower),
                "半周长余量上限_mm": number_text(parameters.upper),
                "入池候选": " | ".join(candidate_text(*item) for item in qualifying),
                "匹配原因": "同分类候选的半周长差值严格位于参数区间内，按档位序号升序取首条",
                "__rule_line": selected_rule.line_no,
            }
        )
        return result

    nearest_rule, nearest_difference = min(
        candidates,
        key=lambda item: (
            interval_distance(item[1], parameters),
            item[0].sequence,
            item[0].line_no,
        ),
    )
    if nearest_difference <= parameters.lower:
        reason = "最近候选差值不大于半周长余量下限"
    else:
        reason = "最近候选差值不小于半周长余量上限"
    result.update(
        {
            "匹配状态": "无可用尺码",
            "匹配池": category,
            "半周长余量下限_mm": number_text(parameters.lower),
            "半周长余量上限_mm": number_text(parameters.upper),
            "最近候选内部尺码": nearest_rule.internal_size,
            "最近候选差值_mm": number_text(nearest_difference),
            "距最近边界_mm": number_text(interval_distance(nearest_difference, parameters)),
            "匹配原因": reason,
        }
    )
    return result


def category_summary(final_rows: Sequence[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in final_rows:
        grouped[clean_text(row.get("分类"))].append(row)
    summary: dict[str, dict[str, object]] = {}
    for category, rows in sorted(grouped.items()):
        counts = Counter(clean_text(row.get("匹配状态")) for row in rows)
        eligible = len(rows) - counts["数据不全"]
        summary[category] = {
            "总数": len(rows),
            "已匹配": counts["已匹配"],
            "无可用尺码": counts["无可用尺码"],
            "数据不全": counts["数据不全"],
            "有效数据覆盖率": round(counts["已匹配"] / eligible, 6) if eligible else None,
        }
    return summary


def build_usage_rows(
    rules: Sequence[Rule], usage: Counter[int], total_matched: int, parameters: Parameters
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rule in rules:
        count = usage[rule.line_no]
        cover_hp = rule.cover_half_perimeter_mm
        rows.append(
            {
                "规则行号": rule.line_no,
                "内部尺码": rule.internal_size,
                "通用尺码": rule.common_size,
                "档位序号": number_text(rule.sequence),
                "分类": rule.category,
                "CAB": rule.cab,
                "车衣数据型号": rule.cover_model or "",
                "侧片长_cm": number_text(rule.side_length_cm),
                "车衣半周长_mm": number_text(cover_hp),
                "可匹配记录半周长下界_mm": number_text(
                    cover_hp - parameters.upper if cover_hp is not None else None
                ),
                "可匹配记录半周长上界_mm": number_text(
                    cover_hp - parameters.lower if cover_hp is not None else None
                ),
                "边界类型": "严格开区间" if cover_hp is not None else "",
                "匹配数": count,
                "占已匹配比例": f"{count / total_matched:.2%}" if total_matched else "0.00%",
                "规则状态": "可参与匹配" if cover_hp is not None else "缺少可用侧片长",
                "备注": rule.note,
            }
        )
    return rows


def analyze_ruleset(
    ruleset: str,
    rule_source_dir: Path,
    publish_dir: Path,
    source_fields: Sequence[str],
    source_rows: Sequence[Mapping[str, str]],
    cover_sizes: Mapping[str, float],
    parameters: Parameters,
) -> dict[str, object]:
    rule_path = rule_source_dir / RULESETS[ruleset]
    rule_fields, raw_rule_rows, rules, duplicates = load_rules(rule_path, cover_sizes)
    enriched_fields = list(rule_fields) + [
        "车衣数据型号",
        "侧片长_cm",
        "车衣半周长_mm",
        "半周长状态",
    ]
    write_csv(
        publish_dir / RULESETS[ruleset],
        enriched_fields,
        enrich_rule_rows(raw_rule_rows, cover_sizes),
    )

    pools = build_pools(rules)
    final_rows: list[dict[str, object]] = []
    usage: Counter[int] = Counter()
    for source_row in source_rows:
        record_hp = record_half_perimeter_mm(source_row)
        match = match_vehicle(source_row, pools, parameters)
        rule_line = match.pop("__rule_line")
        if isinstance(rule_line, int):
            usage[rule_line] += 1
        final_rows.append(
            {
                **source_row,
                "记录半周长_mm": number_text(record_hp),
                "规则集": ruleset,
                **match,
            }
        )

    output_fields = list(source_fields) + [
        "记录半周长_mm",
        "规则集",
        "匹配状态",
        "匹配池",
        "内部尺码",
        "通用尺码",
        "档位序号",
        "规则CAB",
        "车衣数据型号",
        "侧片长_cm",
        "车衣半周长_mm",
        "半周长差值_mm",
        "半周长余量下限_mm",
        "半周长余量上限_mm",
        "入池候选",
        "最近候选内部尺码",
        "最近候选差值_mm",
        "距最近边界_mm",
        "匹配原因",
    ]
    output_path = publish_dir / f"{ruleset}-尺码匹配分析.csv"
    write_csv(output_path, output_fields, final_rows)
    write_csv(
        publish_dir / f"{ruleset}-未匹配.csv",
        output_fields,
        (row for row in final_rows if row["匹配状态"] != "已匹配"),
    )

    statuses = Counter(clean_text(row["匹配状态"]) for row in final_rows)
    usage_rows = build_usage_rows(rules, usage, statuses["已匹配"], parameters)
    write_csv(
        publish_dir / f"{ruleset}-规则使用统计.csv",
        list(usage_rows[0].keys()) if usage_rows else [],
        usage_rows,
    )
    eligible = len(final_rows) - statuses["数据不全"]
    missing_cover_rules = [rule.internal_size for rule in rules if rule.cover_half_perimeter_mm is None]
    return {
        "规则集": ruleset,
        "规则源": str(rule_path),
        "发布规则": str(publish_dir / RULESETS[ruleset]),
        "匹配输出": str(output_path),
        "源数据行数": len(final_rows),
        "规则原始行数": len(raw_rule_rows),
        "规则有效行数": len(rules),
        "重复规则数": len(duplicates),
        "重复规则": duplicates,
        "具备半周长规则数": sum(rule.cover_half_perimeter_mm is not None for rule in rules),
        "缺少可用侧片长规则数": len(missing_cover_rules),
        "缺少可用侧片长规则": missing_cover_rules,
        "已匹配": statuses["已匹配"],
        "无可用尺码": statuses["无可用尺码"],
        "数据不全": statuses["数据不全"],
        "有效数据覆盖率": round(statuses["已匹配"] / eligible, 6) if eligible else None,
        "分类统计": category_summary(final_rows),
    }


def write_markdown(path: Path, reports: Sequence[Mapping[str, object]], parameters: Parameters) -> None:
    lines = [
        "# 07 版旧尺码半周长匹配分析",
        "",
        "匹配口径：",
        "",
        f"- 尺寸库记录半周长 = `(L-IN + H-IN) × {MM_PER_INCH}` 毫米。",
        f"- 车衣半周长 = `侧片长(cm) × {CM_TO_MM:g} + {COVER_ALLOWANCE_MM:g}` 毫米。",
        "- 差值 = 车衣半周长 - 尺寸库记录半周长。",
        f"- 仅当差值严格大于 {number_text(parameters.lower)}mm 且严格小于 {number_text(parameters.upper)}mm 时进入同分类候选池。",
        "- 候选按档位序号升序、原规则行号升序取首条；CAB 不作为本次匹配条件。",
        "",
        "| 规则集 | 数据行 | 已匹配 | 无可用 | 数据不全 | 有效覆盖率 | 可用规则/有效规则 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for report in reports:
        coverage = report["有效数据覆盖率"]
        coverage_text = "-" if coverage is None else f"{coverage:.2%}"
        lines.append(
            f"| {report['规则集']} | {report['源数据行数']} | {report['已匹配']} | "
            f"{report['无可用尺码']} | {report['数据不全']} | {coverage_text} | "
            f"{report['具备半周长规则数']}/{report['规则有效行数']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    rule_source_dir: Path,
    publish_dir: Path,
    cover_source: Path,
    dimension_source: Path,
    parameter_source: Path,
    selected_rulesets: Sequence[str],
) -> list[dict[str, object]]:
    publish_dir.mkdir(parents=True, exist_ok=True)
    source_fields, source_rows = read_csv(dimension_source)
    require_columns(source_fields, REQUIRED_SOURCE_COLUMNS, dimension_source.name)
    cover_sizes = load_cover_sizes(cover_source)
    parameters = load_parameters(parameter_source)
    reports = [
        analyze_ruleset(
            ruleset,
            rule_source_dir,
            publish_dir,
            source_fields,
            source_rows,
            cover_sizes,
            parameters,
        )
        for ruleset in selected_rulesets
    ]
    validation = {
        "数据源": str(dimension_source),
        "车衣数据源": str(cover_source),
        "参数源": str(parameter_source),
        "参数": parameters.as_dict(),
        "单位换算": {
            "英寸转毫米": MM_PER_INCH,
            "侧片长厘米转毫米": CM_TO_MM,
            "车衣附加量_mm": COVER_ALLOWANCE_MM,
        },
        "尺寸库记录半周长公式": "(L-IN + H-IN) * 25.4",
        "车衣半周长公式": "侧片长_cm * 10 + 1500",
        "差值公式": "车衣半周长_mm - 记录半周长_mm",
        "边界": "严格开区间：差值 > 下限 且 差值 < 上限",
        "匹配顺序": "同分类候选按档位序号、原规则行号升序取首条；不使用 CAB",
        "规则集报告": reports,
    }
    (publish_dir / "校验报告.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_markdown(publish_dir / "分析报告.md", reports, parameters)
    return reports


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="lagacy 项目目录")
    parser.add_argument("--rule-source-dir", type=Path, help="三套库存规则所在目录")
    parser.add_argument("--publish-dir", type=Path, help="发布目录")
    parser.add_argument("--cover-source", type=Path, help="07-车衣数据.csv 路径")
    parser.add_argument("--dimension-source", type=Path, help="尺寸库.csv 路径")
    parser.add_argument("--parameters", type=Path, help="参数.csv 路径")
    parser.add_argument(
        "--ruleset",
        action="append",
        choices=sorted(RULESETS),
        help="仅运行指定规则集；可重复，默认运行全部",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    rule_source_dir = (args.rule_source_dir or root / RULE_SOURCE_DIR_NAME).resolve()
    publish_dir = (args.publish_dir or root / PUBLISH_DIR_NAME).resolve()
    cover_source = (args.cover_source or root / COVER_FILE).resolve()
    dimension_source = (args.dimension_source or publish_dir / DIMENSION_FILE).resolve()
    parameter_source = (args.parameters or publish_dir / PARAMETER_FILE).resolve()
    selected = args.ruleset or list(RULESETS)
    try:
        reports = run(
            rule_source_dir,
            publish_dir,
            cover_source,
            dimension_source,
            parameter_source,
            selected,
        )
    except (FileNotFoundError, ValueError, csv.Error) as error:
        print(f"半周长匹配计算失败：{error}")
        return 2
    for report in reports:
        print(
            f"{report['规则集']}: matched={report['已匹配']} "
            f"unmatched={report['无可用尺码']} incomplete={report['数据不全']} "
            f"eligible_coverage={report['有效数据覆盖率']:.2%}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
