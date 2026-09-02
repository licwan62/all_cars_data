#!/usr/bin/env python3
"""使用三套 07 版旧尺码规则，分别重放车型尺寸匹配。

所有输入、代码、中间诊断与输出均位于 source/lagacy 内；不会读取或写入
现行的 source/尺码分析.csv 和 尺码计算 目录。
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
INPUT_DIR_NAME = "source"
SOURCE_FILE = "车型尺寸库.csv"
PARAMETER_FILE = "余量参数.csv"
RULESETS = {
    "all-07": "all-07.csv",
    "hnt-07": "hnt-07.csv",
    "tm-07": "tm-07.csv",
}
REQUIRED_SOURCE_COLUMNS = {"DIMENSION-ID", "分类", "CAB", "L-IN", "W-IN", "H-IN"}
REQUIRED_RULE_COLUMNS = {"内部尺码", "档位序号", "分类", "CAB", "长_in", "宽_in", "高_in"}


@dataclass(frozen=True)
class Rule:
    line_no: int
    internal_size: str
    common_size: str
    sequence: float
    category: str
    cab: str
    max_length: float
    max_width: float
    max_height: float
    note: str

    @property
    def identity(self) -> tuple[object, ...]:
        return (
            self.internal_size,
            self.common_size,
            self.sequence,
            self.category,
            self.cab,
            self.max_length,
            self.max_width,
            self.max_height,
        )

    @property
    def pool_key(self) -> tuple[str, str]:
        return self.category, self.cab


@dataclass(frozen=True)
class Tolerances:
    length_upper: float
    width_upper: float
    height_upper: float
    length_surplus: float

    def length_lower_bound(self, rule: Rule) -> float:
        return rule.max_length - self.length_surplus

    def length_upper_bound(self, rule: Rule) -> float:
        return rule.max_length + self.length_upper

    def width_upper_bound(self, rule: Rule) -> float:
        return rule.max_width + self.width_upper

    def height_upper_bound(self, rule: Rule) -> float:
        return rule.max_height + self.height_upper

    def as_dict(self) -> dict[str, float]:
        return {
            "长容差": self.length_upper,
            "宽容差": self.width_upper,
            "高容差": self.height_upper,
            "余量长容差": self.length_surplus,
        }


def clean_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def parse_number(value: object) -> float | None:
    text = clean_text(value)
    if not text:
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
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames), rows


def require_columns(fieldnames: Iterable[str], required: set[str], label: str) -> None:
    missing = sorted(required - set(fieldnames))
    if missing:
        raise ValueError(f"{label} 缺少字段：{', '.join(missing)}")


def load_rules(path: Path) -> tuple[list[Rule], list[dict[str, object]]]:
    fieldnames, rows = read_csv(path)
    require_columns(fieldnames, REQUIRED_RULE_COLUMNS, path.name)
    rules: list[Rule] = []
    duplicate_rows: list[dict[str, object]] = []
    seen: dict[tuple[object, ...], Rule] = {}

    for index, row in enumerate(rows, start=2):
        sequence = parse_number(row.get("档位序号"))
        max_length = parse_number(row.get("长_in"))
        max_width = parse_number(row.get("宽_in"))
        max_height = parse_number(row.get("高_in"))
        internal_size = clean_text(row.get("内部尺码"))
        category = clean_text(row.get("分类"))
        if not internal_size or not category or None in (sequence, max_length, max_width, max_height):
            raise ValueError(f"{path.name} 第 {index} 行存在空白或非数字必填值")
        assert sequence is not None and max_length is not None
        assert max_width is not None and max_height is not None
        rule = Rule(
            line_no=index,
            internal_size=internal_size,
            common_size=clean_text(row.get("通用尺码")),
            sequence=sequence,
            category=category,
            cab=clean_text(row.get("CAB")),
            max_length=max_length,
            max_width=max_width,
            max_height=max_height,
            note=clean_text(row.get("备注")),
        )
        prior = seen.get(rule.identity)
        if prior is not None:
            duplicate_rows.append(
                {
                    "重复行": index,
                    "保留行": prior.line_no,
                    "内部尺码": rule.internal_size,
                    "通用尺码": rule.common_size,
                    "分类": rule.category,
                    "CAB": rule.cab,
                }
            )
            continue
        seen[rule.identity] = rule
        rules.append(rule)

    return sorted(rules, key=lambda item: (item.category, item.cab, item.sequence, item.line_no)), duplicate_rows


def load_tolerances(path: Path) -> Tolerances:
    fieldnames, rows = read_csv(path)
    require_columns(fieldnames, {"参数", "值"}, path.name)
    values: dict[str, float] = {}
    duplicates: set[str] = set()
    for index, row in enumerate(rows, start=2):
        name = clean_text(row.get("参数"))
        value = parse_number(row.get("值"))
        if not name or value is None:
            raise ValueError(f"{path.name} 第 {index} 行存在空白或非数字参数")
        if name in values:
            duplicates.add(name)
        values[name] = value
    if duplicates:
        raise ValueError(f"{path.name} 参数重复：{', '.join(sorted(duplicates))}")
    required = {"长容差", "宽容差", "高容差", "余量长容差"}
    missing = sorted(required - set(values))
    if missing:
        raise ValueError(f"{path.name} 缺少参数：{', '.join(missing)}")
    if any(values[name] < 0 for name in required):
        raise ValueError(f"{path.name} 容差参数不得为负数")
    return Tolerances(
        length_upper=values["长容差"],
        width_upper=values["宽容差"],
        height_upper=values["高容差"],
        length_surplus=values["余量长容差"],
    )


def build_pools(rules: Sequence[Rule]) -> dict[tuple[str, str], list[Rule]]:
    pools: dict[tuple[str, str], list[Rule]] = defaultdict(list)
    for rule in rules:
        pools[rule.pool_key].append(rule)
    for key in pools:
        pools[key].sort(key=lambda item: (item.sequence, item.line_no))
    return dict(pools)


def fits(
    rule: Rule, length: float, width: float, height: float, tolerances: Tolerances
) -> bool:
    return (
        tolerances.length_lower_bound(rule) <= length <= tolerances.length_upper_bound(rule)
        and width <= tolerances.width_upper_bound(rule)
        and height <= tolerances.height_upper_bound(rule)
    )


def boundary_violations(
    rule: Rule, length: float, width: float, height: float, tolerances: Tolerances
) -> tuple[float, float, float, float]:
    return (
        max(0.0, length - tolerances.length_upper_bound(rule)),
        max(0.0, tolerances.length_lower_bound(rule) - length),
        max(0.0, width - tolerances.width_upper_bound(rule)),
        max(0.0, height - tolerances.height_upper_bound(rule)),
    )


def describe_violation(values: tuple[float, float, float, float]) -> str:
    labels = [
        label
        for label, value in zip(("超长", "超余量", "超宽", "超高"), values, strict=True)
        if value > 0
    ]
    return "+".join(labels) if labels else ""


def match_vehicle(
    row: Mapping[str, str],
    pools: Mapping[tuple[str, str], Sequence[Rule]],
    tolerances: Tolerances,
) -> dict[str, object]:
    category = clean_text(row.get("分类"))
    cab = clean_text(row.get("CAB"))
    length = parse_number(row.get("L-IN"))
    width = parse_number(row.get("W-IN"))
    height = parse_number(row.get("H-IN"))
    result: dict[str, object] = {
        "匹配状态": "",
        "匹配池": "",
        "内部尺码": "",
        "通用尺码": "",
        "档位序号": "",
        "规则长基准_in": "",
        "规则宽基准_in": "",
        "规则高基准_in": "",
        "实际长下限_in": "",
        "实际长上限_in": "",
        "实际宽上限_in": "",
        "实际高上限_in": "",
        "长度余量_in": "",
        "距长下限_in": "",
        "距长上限_in": "",
        "距宽上限_in": "",
        "距高上限_in": "",
        "最近候选内部尺码": "",
        "最近候选通用尺码": "",
        "最近候选最大超界_in": "",
        "匹配原因": "",
        "__rule_line": None,
    }

    if None in (length, width, height) or any(
        value is not None and value <= 0 for value in (length, width, height)
    ):
        result.update({"匹配状态": "数据不全", "匹配原因": "L-IN/W-IN/H-IN 缺失或非正数"})
        return result
    assert length is not None and width is not None and height is not None

    attempts: list[tuple[str, Sequence[Rule]]] = []
    if cab and (category, cab) in pools:
        attempts.append((f"{category}|CAB={cab}", pools[(category, cab)]))
    if (category, "") in pools:
        attempts.append((f"{category}|CAB=通用", pools[(category, "")]))

    for pool_label, pool in attempts:
        for rule in pool:
            if fits(rule, length, width, height, tolerances):
                length_lower = tolerances.length_lower_bound(rule)
                length_upper = tolerances.length_upper_bound(rule)
                width_upper = tolerances.width_upper_bound(rule)
                height_upper = tolerances.height_upper_bound(rule)
                result.update(
                    {
                        "匹配状态": "已匹配",
                        "匹配池": pool_label,
                        "内部尺码": rule.internal_size,
                        "通用尺码": rule.common_size,
                        "档位序号": number_text(rule.sequence),
                        "规则长基准_in": number_text(rule.max_length),
                        "规则宽基准_in": number_text(rule.max_width),
                        "规则高基准_in": number_text(rule.max_height),
                        "实际长下限_in": number_text(length_lower),
                        "实际长上限_in": number_text(length_upper),
                        "实际宽上限_in": number_text(width_upper),
                        "实际高上限_in": number_text(height_upper),
                        "长度余量_in": number_text(rule.max_length - length),
                        "距长下限_in": number_text(length - length_lower),
                        "距长上限_in": number_text(length_upper - length),
                        "距宽上限_in": number_text(width_upper - width),
                        "距高上限_in": number_text(height_upper - height),
                        "匹配原因": "长度在上下限内且宽高不超过容差后上限",
                        "__rule_line": rule.line_no,
                    }
                )
                return result

    candidates = [(pool_label, rule) for pool_label, pool in attempts for rule in pool]
    if not candidates:
        result.update({"匹配状态": "无可用尺码", "匹配原因": "无该分类/CAB 可回退规则"})
        return result

    pool_label, nearest = min(
        candidates,
        key=lambda item: (
            max(boundary_violations(item[1], length, width, height, tolerances)),
            sum(boundary_violations(item[1], length, width, height, tolerances)),
            item[1].sequence,
            item[1].line_no,
        ),
    )
    violations = boundary_violations(nearest, length, width, height, tolerances)
    result.update(
        {
            "匹配状态": "无可用尺码",
            "匹配池": pool_label,
            "最近候选内部尺码": nearest.internal_size,
            "最近候选通用尺码": nearest.common_size,
            "最近候选最大超界_in": number_text(max(violations)),
            "匹配原因": describe_violation(violations) or "无满足规则",
        }
    )
    return result


def find_shadowing(rules: Sequence[Rule], tolerances: Tolerances) -> dict[int, Rule]:
    shadows: dict[int, Rule] = {}
    pools = build_pools(rules)
    for pool in pools.values():
        for index, current in enumerate(pool):
            for prior in pool[:index]:
                if (
                    tolerances.length_lower_bound(prior)
                    <= tolerances.length_lower_bound(current)
                    and tolerances.length_upper_bound(prior)
                    >= tolerances.length_upper_bound(current)
                    and tolerances.width_upper_bound(prior)
                    >= tolerances.width_upper_bound(current)
                    and tolerances.height_upper_bound(prior)
                    >= tolerances.height_upper_bound(current)
                ):
                    shadows[current.line_no] = prior
                    break
    return shadows


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_rule_rows(
    rules: Sequence[Rule],
    usage: Counter[int],
    total_matched: int,
    shadows: Mapping[int, Rule],
    tolerances: Tolerances,
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for rule in rules:
        shadow = shadows.get(rule.line_no)
        count = usage[rule.line_no]
        result.append(
            {
                "规则行号": rule.line_no,
                "内部尺码": rule.internal_size,
                "通用尺码": rule.common_size,
                "档位序号": number_text(rule.sequence),
                "分类": rule.category,
                "CAB": rule.cab,
                "长_in": number_text(rule.max_length),
                "宽_in": number_text(rule.max_width),
                "高_in": number_text(rule.max_height),
                "实际长下限_in": number_text(tolerances.length_lower_bound(rule)),
                "实际长上限_in": number_text(tolerances.length_upper_bound(rule)),
                "实际宽上限_in": number_text(tolerances.width_upper_bound(rule)),
                "实际高上限_in": number_text(tolerances.height_upper_bound(rule)),
                "备注": rule.note,
                "匹配数": count,
                "占已匹配比例": f"{count / total_matched:.2%}" if total_matched else "0.00%",
                "结构状态": "被更早规则完全遮蔽" if shadow else "可达",
                "遮蔽规则": f"第{shadow.line_no}行 {shadow.internal_size}" if shadow else "",
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


def write_markdown(path: Path, ruleset: str, report: Mapping[str, object]) -> None:
    categories = report["分类统计"]
    parameters = report["余量参数"]
    lines = [
        f"# {ruleset} 独立尺码分析",
        "",
        "匹配口径：同分类；若存在同 CAB 专属池则先尝试专属池，再回退通用 CAB；",
        "候选长度必须位于 `长_in-余量长容差` 至 `长_in+长容差`；宽、高不得超过各自基准加容差；",
        "满足时按档位序号升序取首条。所有参数单位均为英寸。",
        "",
        f"- 长容差：{number_text(parameters['长容差'])}",
        f"- 宽容差：{number_text(parameters['宽容差'])}",
        f"- 高容差：{number_text(parameters['高容差'])}",
        f"- 余量长容差：{number_text(parameters['余量长容差'])}",
        "",
        f"- 数据行：{report['源数据行数']}",
        f"- 已匹配：{report['已匹配']}",
        f"- 无可用尺码：{report['无可用尺码']}",
        f"- 数据不全：{report['数据不全']}",
        f"- 有效数据覆盖率：{report['有效数据覆盖率']:.2%}",
        f"- 去除的完全重复规则：{report['重复规则数']}",
        f"- 被更早规则完全遮蔽：{report['被遮蔽规则数']}",
        "",
        "| 分类 | 总数 | 已匹配 | 无可用 | 数据不全 | 有效覆盖率 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for category, values in categories.items():
        coverage = values["有效数据覆盖率"]
        coverage_text = "-" if coverage is None else f"{coverage:.2%}"
        lines.append(
            f"| {category} | {values['总数']} | {values['已匹配']} | "
            f"{values['无可用尺码']} | {values['数据不全']} | {coverage_text} |"
        )
    if report["规则问题"]:
        lines.extend(["", "## 规则问题", ""])
        lines.extend(f"- {item}" for item in report["规则问题"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze_ruleset(root: Path, ruleset: str) -> dict[str, object]:
    input_dir = root / INPUT_DIR_NAME
    source_path = input_dir / SOURCE_FILE
    parameter_path = input_dir / PARAMETER_FILE
    rule_path = input_dir / RULESETS[ruleset]
    source_fields, source_rows = read_csv(source_path)
    require_columns(source_fields, REQUIRED_SOURCE_COLUMNS, source_path.name)
    tolerances = load_tolerances(parameter_path)
    rules, duplicates = load_rules(rule_path)
    pools = build_pools(rules)
    shadows = find_shadowing(rules, tolerances)

    output_fields = source_fields + [
        "规则集",
        "匹配状态",
        "匹配池",
        "内部尺码",
        "通用尺码",
        "档位序号",
        "规则长基准_in",
        "规则宽基准_in",
        "规则高基准_in",
        "实际长下限_in",
        "实际长上限_in",
        "实际宽上限_in",
        "实际高上限_in",
        "长度余量_in",
        "距长下限_in",
        "距长上限_in",
        "距宽上限_in",
        "距高上限_in",
        "最近候选内部尺码",
        "最近候选通用尺码",
        "最近候选最大超界_in",
        "匹配原因",
    ]
    final_rows: list[dict[str, object]] = []
    usage: Counter[int] = Counter()
    for source_row in source_rows:
        match = match_vehicle(source_row, pools, tolerances)
        rule_line = match.pop("__rule_line")
        if isinstance(rule_line, int):
            usage[rule_line] += 1
        final_rows.append({**source_row, "规则集": ruleset, **match})

    statuses = Counter(clean_text(row["匹配状态"]) for row in final_rows)
    eligible = len(final_rows) - statuses["数据不全"]
    rule_rows = build_rule_rows(rules, usage, statuses["已匹配"], shadows, tolerances)
    issues = []
    if duplicates:
        issues.append(f"存在 {len(duplicates)} 条完全重复规则，匹配前已保留首条并去重。")
    for line_no, prior in sorted(shadows.items()):
        current = next(rule for rule in rules if rule.line_no == line_no)
        issues.append(
            f"第 {line_no} 行 {current.category}/{current.internal_size} 被第 {prior.line_no} 行 "
            f"{prior.internal_size} 完全遮蔽，按档位优先逻辑不会命中。"
        )
    unused = [row for row in rule_rows if row["匹配数"] == 0]
    report: dict[str, object] = {
        "规则集": ruleset,
        "数据源": f"{INPUT_DIR_NAME}/{SOURCE_FILE}",
        "规则源": f"{INPUT_DIR_NAME}/{RULESETS[ruleset]}",
        "容差参数源": f"{INPUT_DIR_NAME}/{PARAMETER_FILE}",
        "余量参数": tolerances.as_dict(),
        "匹配口径": "同分类；CAB 专属池优先、通用 CAB 回退；长度在基准减余量至基准加长容差之间；宽高不超过基准加各自容差；档位序号升序首条",
        "源数据行数": len(source_rows),
        "DIMENSION-ID唯一数": len({clean_text(row.get("DIMENSION-ID")) for row in source_rows}),
        "规则原始行数": len(rules) + len(duplicates),
        "规则有效行数": len(rules),
        "重复规则数": len(duplicates),
        "重复规则": duplicates,
        "被遮蔽规则数": len(shadows),
        "未使用规则数": len(unused),
        "未使用规则": [f"{row['分类']}/{row['内部尺码']}" for row in unused],
        "已匹配": statuses["已匹配"],
        "无可用尺码": statuses["无可用尺码"],
        "数据不全": statuses["数据不全"],
        "总覆盖率": round(statuses["已匹配"] / len(final_rows), 6) if final_rows else None,
        "有效数据覆盖率": round(statuses["已匹配"] / eligible, 6) if eligible else None,
        "分类统计": category_summary(final_rows),
        "未匹配原因": dict(sorted(Counter(clean_text(row["匹配原因"]) for row in final_rows if row["匹配状态"] != "已匹配").items())),
        "规则问题": issues,
    }

    analysis_dir = root / "analysis" / ruleset
    output_dir = analysis_dir / "output"
    data_dir = analysis_dir / "data"
    write_csv(output_dir / "尺码匹配分析.csv", output_fields, final_rows)
    write_csv(data_dir / "未匹配.csv", output_fields, (row for row in final_rows if row["匹配状态"] != "已匹配"))
    rule_fields = list(rule_rows[0].keys()) if rule_rows else []
    write_csv(data_dir / "规则使用统计.csv", rule_fields, rule_rows)
    normalized_rule_fields = [
        "规则行号",
        "内部尺码",
        "通用尺码",
        "档位序号",
        "分类",
        "CAB",
        "长_in",
        "宽_in",
        "高_in",
        "实际长下限_in",
        "实际长上限_in",
        "实际宽上限_in",
        "实际高上限_in",
        "备注",
    ]
    write_csv(data_dir / "规则标准化.csv", normalized_rule_fields, rule_rows)
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "校验报告.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_markdown(data_dir / "分析报告.md", ruleset, report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="分别运行 07 版旧尺码规则分析")
    parser.add_argument("--root", type=Path, default=ROOT, help="lagacy 项目目录；输入从其 source 子目录读取")
    parser.add_argument(
        "--ruleset",
        action="append",
        choices=sorted(RULESETS),
        help="仅运行指定规则集；可重复，默认运行全部",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = args.ruleset or list(RULESETS)
    reports = [analyze_ruleset(args.root.resolve(), ruleset) for ruleset in selected]
    for report in reports:
        print(
            f"{report['规则集']}: matched={report['已匹配']} "
            f"unmatched={report['无可用尺码']} incomplete={report['数据不全']} "
            f"eligible_coverage={report['有效数据覆盖率']:.2%}"
        )


if __name__ == "__main__":
    main()
