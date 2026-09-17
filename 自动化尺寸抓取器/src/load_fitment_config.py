#!/usr/bin/env python3
"""Load and validate a fitment config, then emit JSON for PowerShell."""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("缺少 PyYAML，请运行: python -m pip install PyYAML") from exc


def require_mapping(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} 必须是 YAML mapping")
    return value


def load_requirement_contract(path):
    content = path.read_text(encoding="utf-8-sig")
    match = re.search(
        r"<!--\s*fitment-data-contract\s*\r?\n(.*?)\r?\n\s*-->",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        raise ValueError(
            "requirement 缺少 <!-- fitment-data-contract ... --> 固定字段定义"
        )
    parsed = yaml.safe_load(match.group(1)) or {}
    return require_mapping(parsed, "requirement.fitment-data-contract")


def validate_table(definition, name, required=True):
    definition = require_mapping(definition, f"requirement.{name}")
    enabled = bool(definition.get("enabled", True))
    columns = definition.get("columns", [])
    if required and not columns:
        raise ValueError(f"requirement.{name}.columns 不能为空")
    if enabled:
        if not isinstance(columns, list) or any(
            not isinstance(item, str) or not item.strip() for item in columns
        ):
            raise ValueError(f"requirement.{name}.columns 必须是非空字符串列表")
        if len(columns) != len(set(columns)):
            raise ValueError(f"requirement.{name}.columns 不允许重复列名")
    elif columns and not isinstance(columns, list):
        raise ValueError(f"requirement.{name}.columns 必须是列表")

    auto_columns = definition.get("auto_empty_columns", [])
    if not isinstance(auto_columns, list):
        raise ValueError(f"requirement.{name}.auto_empty_columns 必须是列表")
    unknown = [item for item in auto_columns if item not in columns]
    if unknown:
        raise ValueError(
            f"requirement.{name}.auto_empty_columns 包含未定义列: {unknown}"
        )
    definition["enabled"] = enabled
    definition["columns"] = columns
    definition["auto_empty_columns"] = auto_columns
    return definition


def validate_instructions(value):
    if value is None:
        return []
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise ValueError(
            "requirement.fitment-data-contract.instructions 必须是非空字符串列表"
        )
    return [item.strip() for item in value]


def validate_dimension_representative(definition, full_table):
    definition = require_mapping(
        definition, "data_contract.dimension_representative"
    )
    enabled = bool(definition.get("enabled", False))
    definition["enabled"] = enabled
    if not enabled:
        definition["_instruction"] = ""
        return definition

    full_columns = full_table["columns"]
    auto_empty_columns = set(full_table.get("auto_empty_columns", []))

    def require_columns(value, name, allow_empty=False):
        if (
            not isinstance(value, list)
            or (not allow_empty and not value)
            or any(not isinstance(item, str) or not item.strip() for item in value)
        ):
            suffix = "字符串列表" if allow_empty else "非空字符串列表"
            raise ValueError(f"data_contract.dimension_representative.{name} 必须是{suffix}")
        unknown = [item for item in value if item not in full_columns]
        if unknown:
            raise ValueError(
                f"data_contract.dimension_representative.{name} 包含全量表中不存在的列: {unknown}"
            )
        return value

    key_columns = require_columns(definition.get("key_columns", []), "key_columns")
    year_column = definition.get("year_column")
    if not isinstance(year_column, str) or year_column not in full_columns:
        raise ValueError(
            "data_contract.dimension_representative.year_column 必须是全量表中的列"
        )
    dimension_columns = require_columns(
        definition.get("dimension_columns", []), "dimension_columns"
    )
    forbidden_dimensions = [
        item for item in dimension_columns if item in auto_empty_columns
    ]
    if forbidden_dimensions:
        raise ValueError(
            "尺寸代表年字段不能是自动留空列: " + ", ".join(forbidden_dimensions)
        )

    minimum_years = int(definition.get("minimum_comparison_years", 2))
    if minimum_years < 2:
        raise ValueError(
            "data_contract.dimension_representative.minimum_comparison_years 必须至少为 2"
        )

    outlier = require_mapping(
        definition.get("outlier", {}),
        "data_contract.dimension_representative.outlier",
    )
    comparison_rule = outlier.get("comparison_rule", "absolute_or_relative")
    if comparison_rule not in {"absolute_or_relative", "absolute_and_relative"}:
        raise ValueError(
            "dimension_representative.outlier.comparison_rule "
            "只能是 absolute_or_relative 或 absolute_and_relative"
        )
    absolute = require_mapping(
        outlier.get("max_absolute_difference", {}),
        "data_contract.dimension_representative.outlier.max_absolute_difference",
    )
    missing_tolerances = [item for item in dimension_columns if item not in absolute]
    unknown_tolerances = [item for item in absolute if item not in dimension_columns]
    if missing_tolerances or unknown_tolerances:
        raise ValueError(
            "dimension_representative 的绝对差阈值必须与 dimension_columns 一一对应；"
            f"缺少={missing_tolerances}，多余={unknown_tolerances}"
        )
    for column, value in absolute.items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"尺寸列 {column} 的绝对差阈值必须大于 0")
    relative_percent = float(outlier.get("max_relative_difference_percent", 3.0))
    if relative_percent <= 0:
        raise ValueError(
            "dimension_representative.outlier.max_relative_difference_percent 必须大于 0"
        )

    representative = require_mapping(
        definition.get("representative_year", {}),
        "data_contract.dimension_representative.representative_year",
    )
    strategy = representative.get("strategy", "best_documented")
    if strategy != "best_documented":
        raise ValueError(
            "dimension_representative.representative_year.strategy "
            "目前只支持 best_documented"
        )
    audit_columns = require_columns(
        definition.get("audit_columns", []), "audit_columns", allow_empty=True
    )

    rule_text = (
        "【尺寸代表年复用规则】"
        f"把 {', '.join(key_columns)} 的完整组合视为一个尺寸 key；"
        f"年份字段为 {year_column}，尺寸字段为 {', '.join(dimension_columns)}。"
        "只允许在同一完整 key、同一代际的年份范围内比较和复用，禁止跨 key、跨代际借用。"
        f"复用前至少取得 {minimum_years} 个不同年份的可靠尺寸证据，并尽量覆盖范围首年、"
        "末年及中期改款/结构变化点；逐尺寸计算可靠样本的 max-min spread。"
        f"离群判定规则为 {comparison_rule}：绝对差上限分别为 "
        + "、".join(f"{column}={absolute[column]}" for column in dimension_columns)
        + f"，相对差上限为 {relative_percent:g}%。"
        "若任何尺寸触发离群阈值，或资料显示车身、版本、CAB、BED、轴距/结构发生变化，"
        "必须视为 outlier，禁止整段复用；应继续核实并按年份或变化边界拆分。"
        "只有确认无较大 outlier 后，才从该 key 范围内选择资料最完整、口径最可靠、最好查证"
        "的一个年份作为代表年；直接采用该代表年的真实尺寸覆盖已验证范围，禁止对尺寸求平均。"
        "证据不足、年份覆盖不足或来源口径冲突时不得复用，也不得给出完成信号。"
    )
    if audit_columns:
        rule_text += (
            f"必须在 {', '.join(audit_columns)} 中留痕：尺寸 key、代表年份、"
            "验证年份范围、各尺寸 spread、阈值结论以及代表年来源。"
        )

    definition["key_columns"] = key_columns
    definition["year_column"] = year_column
    definition["dimension_columns"] = dimension_columns
    definition["minimum_comparison_years"] = minimum_years
    outlier["comparison_rule"] = comparison_rule
    outlier["max_relative_difference_percent"] = relative_percent
    representative["strategy"] = strategy
    definition["outlier"] = outlier
    definition["representative_year"] = representative
    definition["audit_columns"] = audit_columns
    definition["_instruction"] = rule_text
    return definition


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    args = parser.parse_args()
    path = Path(args.config).resolve()
    if not path.is_file():
        raise ValueError(f"配置文件不存在: {path}")

    with path.open("r", encoding="utf-8-sig") as stream:
        config = yaml.safe_load(stream) or {}
    require_mapping(config, "config")

    if config.get("version", 1) != 1:
        raise ValueError("目前只支持 config version: 1")
    mode = config.get("mode", "work")
    if mode not in {"work", "check", "dry_run"}:
        raise ValueError("mode 只能是 work、check 或 dry_run")

    workspace = require_mapping(config.get("workspace", {}), "workspace")
    traversal = require_mapping(workspace.get("traversal", {}), "workspace.traversal")
    strategy = traversal.get("strategy", "directories")
    if strategy not in {"directories", "glob", "explicit"}:
        raise ValueError("traversal.strategy 只能是 directories、glob 或 explicit")

    contract = require_mapping(config.get("data_contract", {}), "data_contract")
    if not contract.get("requirement"):
        raise ValueError("缺少 data_contract.requirement")
    forbidden = [
        name
        for name in (
            "full_table",
            "dimension_group_table",
            "subseries_match",
            "instructions",
        )
        if name in contract
    ]
    if forbidden:
        raise ValueError(
            "固定字段只能在 requirement 中配置，请从 data_contract 删除: "
            + ", ".join(forbidden)
        )

    requirement_value = contract["requirement"]
    if os.sep == "/":
        requirement_value = requirement_value.replace("\\", "/")
    requirement_path = Path(requirement_value)
    if not requirement_path.is_absolute():
        requirement_path = path.parent / requirement_path
    requirement_path = requirement_path.resolve()
    if not requirement_path.is_file():
        raise ValueError(f"requirement 文件不存在: {requirement_path}")

    requirement_contract = load_requirement_contract(requirement_path)
    contract["full_table"] = validate_table(
        requirement_contract.get("full_table", {}), "full_table"
    )
    contract["dimension_group_table"] = validate_table(
        requirement_contract.get("dimension_group_table", {"enabled": False}),
        "dimension_group_table",
        required=False,
    )
    contract["subseries_match"] = validate_table(
        requirement_contract.get("subseries_match", {"enabled": False}),
        "subseries_match",
        required=False,
    )
    contract["instructions"] = validate_instructions(
        requirement_contract.get("instructions", [])
    )
    contract["dimension_representative"] = validate_dimension_representative(
        contract.get("dimension_representative", {}),
        contract["full_table"],
    )

    runtime = require_mapping(config.get("runtime", {}), "runtime")
    if int(runtime.get("max_rounds", 30)) <= 0:
        raise ValueError("runtime.max_rounds 必须大于 0")
    if int(runtime.get("max_reply_wait_seconds", 900)) <= 0:
        raise ValueError("runtime.max_reply_wait_seconds 必须大于 0")
    timing = require_mapping(runtime.get("timing", {}), "runtime.timing")
    timing_fields = {
        "reply_stability_seconds": 0,
        "operation_delay_seconds": 0,
        "large_payload_delay_seconds": 0,
        "post_reply_delay_seconds": 0,
        "stuck_generating_grace_seconds": 1,
        "xbrowser_retry_count": 0,
        "recover_delay_seconds": 0,
    }
    for name, minimum in timing_fields.items():
        if name not in timing:
            continue
        value = timing[name]
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"runtime.timing.{name} 必须是大于等于 {minimum} 的整数")
    conversation = require_mapping(runtime.get("conversation", {}), "runtime.conversation")
    if conversation.get("mode", "new") not in {"new", "manual_resume", "archive_resume"}:
        raise ValueError(
            "runtime.conversation.mode 只能是 new、manual_resume 或 archive_resume"
        )
    if conversation.get("mode") == "archive_resume" and not conversation.get("archive_code"):
        raise ValueError("archive_resume 模式必须配置 runtime.conversation.archive_code")
    vehicle_iteration = require_mapping(
        runtime.get("vehicle_iteration", {}), "runtime.vehicle_iteration"
    )
    if vehicle_iteration.get("enabled", False):
        key_columns = vehicle_iteration.get("key_columns", ["MAKE", "MODEL"])
        if (
            not isinstance(key_columns, list)
            or not key_columns
            or any(not isinstance(item, str) or not item.strip() for item in key_columns)
        ):
            raise ValueError(
                "runtime.vehicle_iteration.key_columns 必须是非空字符串列表"
            )
        if conversation.get("mode", "new") != "new":
            raise ValueError(
                "启用 vehicle_iteration 时 conversation.mode 必须是 new；"
                "单车型续跑由 checkpoint 自动完成"
            )
    input_sources = require_mapping(
        runtime.get("input_sources", {}), "runtime.input_sources"
    )
    if "input_sources" in runtime:
        directories = input_sources.get("directories", [])
        files = input_sources.get("files", [])
        if not isinstance(directories, list) or not isinstance(files, list):
            raise ValueError(
                "runtime.input_sources.directories 和 files 必须是列表"
            )
        normalized_directories = []
        for index, item in enumerate(directories):
            if isinstance(item, str):
                item = {"path": item}
            item = require_mapping(
                item, f"runtime.input_sources.directories[{index}]"
            )
            if not isinstance(item.get("path"), str) or not item["path"].strip():
                raise ValueError(
                    f"runtime.input_sources.directories[{index}].path 不能为空"
                )
            pattern = item.get("pattern", "*.tsv")
            if not isinstance(pattern, str) or not pattern.strip():
                raise ValueError(
                    f"runtime.input_sources.directories[{index}].pattern 不能为空"
                )
            normalized_directories.append(
                {
                    "path": item["path"],
                    "pattern": pattern,
                    "recursive": bool(item.get("recursive", False)),
                }
            )
        normalized_files = []
        for index, item in enumerate(files):
            if isinstance(item, str):
                item = {"path": item}
            item = require_mapping(item, f"runtime.input_sources.files[{index}]")
            if not isinstance(item.get("path"), str) or not item["path"].strip():
                raise ValueError(
                    f"runtime.input_sources.files[{index}].path 不能为空"
                )
            normalized_files.append({"path": item["path"]})
        if not normalized_directories and not normalized_files:
            raise ValueError(
                "runtime.input_sources 至少需要一个 directories 或 files 条目"
            )
        input_sources["directories"] = normalized_directories
        input_sources["files"] = normalized_files
        if input_sources.get("order", "name_asc") not in {
            "name_asc",
            "name_desc",
            "modified_asc",
            "modified_desc",
        }:
            raise ValueError("runtime.input_sources.order 值无效")

    processing = require_mapping(runtime.get("processing", {}), "runtime.processing")
    if processing:
        if vehicle_iteration.get("enabled", False):
            raise ValueError(
                "runtime.processing 与旧版 runtime.vehicle_iteration 不能同时启用"
            )
        processing_mode = processing.get("mode", "file")
        if processing_mode not in {"row", "file", "batch"}:
            raise ValueError("runtime.processing.mode 只能是 row、file 或 batch")
        rows_per_task = processing.get("rows_per_task", 0)
        if isinstance(rows_per_task, bool) or not isinstance(rows_per_task, int):
            raise ValueError("runtime.processing.rows_per_task 必须是整数")
        if processing_mode == "batch" and rows_per_task <= 0:
            raise ValueError(
                "processing.mode 为 batch 时 rows_per_task 必须大于 0"
            )
        if processing_mode != "batch" and rows_per_task < 0:
            raise ValueError("runtime.processing.rows_per_task 不能小于 0")
        max_input_chars = processing.get("max_input_chars_per_task", 0)
        if (
            isinstance(max_input_chars, bool)
            or not isinstance(max_input_chars, int)
            or max_input_chars < 0
        ):
            raise ValueError(
                "runtime.processing.max_input_chars_per_task 必须是大于等于 0 的整数"
            )
        row_label_columns = processing.get("row_label_columns", [])
        if not isinstance(row_label_columns, list) or any(
            not isinstance(item, str) or not item.strip()
            for item in row_label_columns
        ):
            raise ValueError(
                "runtime.processing.row_label_columns 必须是字符串列表"
            )
        if processing_mode in {"row", "batch"} and conversation.get("mode", "new") != "new":
            raise ValueError(
                "processing.mode 为 row 或 batch 时 conversation.mode 必须是 new；"
                "独立任务续跑由 checkpoint 自动完成"
            )
        partitions = require_mapping(
            processing.get("partitions", {}), "runtime.processing.partitions"
        )
        if partitions:
            count = partitions.get("count", 1)
            if isinstance(count, bool) or not isinstance(count, int) or count < 2:
                raise ValueError(
                    "runtime.processing.partitions.count 必须是大于等于 2 的整数"
                )
            strategy = partitions.get("strategy", "contiguous")
            if strategy not in {"contiguous", "round_robin"}:
                raise ValueError(
                    "runtime.processing.partitions.strategy 只能是 contiguous 或 round_robin"
                )
            partitions["count"] = count
            partitions["strategy"] = strategy
            manifest_path = partitions.get("manifest_path", "partition_manifest.json")
            if not isinstance(manifest_path, str) or not manifest_path.strip():
                raise ValueError(
                    "runtime.processing.partitions.manifest_path 必须是非空字符串"
                )
            partitions["manifest_path"] = manifest_path
    input_files = require_mapping(runtime.get("input_files", {}), "runtime.input_files")
    if input_files.get("order", "name_asc") not in {"name_asc", "name_desc", "modified_asc", "modified_desc"}:
        raise ValueError("runtime.input_files.order 值无效")

    config["_meta"] = {
        "config_path": str(path),
        "config_dir": str(path.parent),
        "requirement_path": str(requirement_path),
    }
    json.dump(config, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"config.yaml 错误: {exc}", file=sys.stderr)
        raise SystemExit(2)
