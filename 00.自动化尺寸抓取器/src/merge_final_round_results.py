"""Merge the latest complete TSV rounds from fitment result files."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROUND_RE = re.compile(r"^---\s*Round\s+(\d+)\s*/\s*(?:下一步|首次发送)\s*---\s*$")
RESULT_RE_TEMPLATE = r"^{base}_result(?:_(\d+))?\.md$"
PART_SUFFIX_RE = re.compile(r"_part_\d+$")
MIN_FITMENT_COLUMNS = 12
HEADER_ALIASES = {
    "年份": "年份区间",
    "货斗长度 (ft)": "货斗长度_ft",
    "状态": "迭代状态",
    "车型名": "前台车型",
    "max_width_in (w/o)": "max_width_in",
}
STANDARD_HEADER = [
    "主车型",
    "年份区间",
    "结构",
    "对应尺码",
    "品牌",
    "前台车型",
    "排序依据车型",
    "子车系",
    "分类",
    "版本",
    "门数",
    "代际",
    "区间最小年份",
    "区间最大年份",
    "max_length_in",
    "max_width_in",
    "max_height_in",
    "max_length_cm",
    "max_width_cm",
    "max_height_cm",
    "驾驶室类型",
    "货斗长度_ft",
    "长度余量",
    "无尺码原因",
    "参考车型",
    "备注",
    "迭代状态",
]
MATCH_HEADER = ["Year", "主车型", "结构", "版本", "候选车型", "匹配数量"]
AUTO_BLANK_FIELDS = {
    "对应尺码",
    "排序依据车型",
    "子车系",
    "区间最小年份",
    "区间最大年份",
    "max_length_cm",
    "max_width_cm",
    "max_height_cm",
    "长度余量",
    "无尺码原因",
}
LEGACY_HEADERS = [
    [
        "主车型",
        "分类",
        "品牌",
        "车型名",
        "结构",
        "版本",
        "门数",
        "代际",
        "代际说明",
        "年份区间",
        "区间最小年份",
        "区间最大年份",
        "驾驶室类型",
        "货斗长度_ft",
        "max_length_in",
        "max_width_in",
        "max_height_in",
        "参考车型",
        "备注",
        "迭代状态",
    ],
    [
        "主车型",
        "分类",
        "品牌",
        "车型名",
        "结构",
        "版本",
        "代际",
        "年份区间",
        "驾驶室类型",
        "货斗长度_ft",
        "max_length_in",
        "max_width_in",
        "max_height_in",
        "参考车型",
        "备注",
        "迭代状态",
    ],
    [
        "主车型",
        "品牌",
        "分类",
        "结构",
        "版本",
        "代际",
        "年份区间",
        "max_length_in",
        "max_width_in",
        "max_height_in",
        "参考车型",
        "备注",
        "迭代状态",
    ],
]


@dataclass
class ExtractedResult:
    source: Path
    round_number: int
    header: list[str]
    lines: list[str]
    match_header: list[str]
    match_lines: list[str]


def version_number(path: Path, base: str) -> int:
    match = re.match(RESULT_RE_TEMPLATE.format(base=re.escape(base)), path.name)
    if not match:
        raise ValueError(f"not a result file for {base}: {path.name}")
    suffix = match.group(1)
    return int(suffix) if suffix else 1


def find_latest_result(results_dir: Path, base: str) -> Path | None:
    pattern = f"{base}_result*.md"
    candidates = [
        path
        for path in results_dir.glob(pattern)
        if re.match(RESULT_RE_TEMPLATE.format(base=re.escape(base)), path.name)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: version_number(path, base))


def extract_last_round(path: Path) -> ExtractedResult | None:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    round_indexes: list[tuple[int, int]] = []

    for index, line in enumerate(lines):
        match = ROUND_RE.match(line)
        if match:
            round_indexes.append((index, int(match.group(1))))

    if not round_indexes:
        return None

    def clean_content(content: list[str]) -> tuple[list[str], list[str], list[str], list[str]]:
        table_segments: list[tuple[list[str], list[str]]] = []
        match_segments: list[tuple[list[str], list[str]]] = []
        current_header: list[str] | None = None
        current_rows: list[str] | None = None
        current_kind: str | None = None
        accepts_unheaded_rows = False

        def flush_current() -> None:
            nonlocal current_header, current_rows, current_kind, accepts_unheaded_rows
            if current_header is not None and current_rows:
                if current_kind == "match":
                    match_segments.append((current_header, current_rows))
                else:
                    table_segments.append((current_header, current_rows))
            current_header = None
            current_rows = None
            current_kind = None
            accepts_unheaded_rows = False

        for line in content:
            stripped = line.strip()
            if not stripped:
                flush_current()
                continue
            if stripped in {"本批次完成。", "本批次完成"}:
                continue
            if stripped.startswith("```"):
                if stripped.lower() in {"```tsv", "```text"}:
                    flush_current()
                    current_header = []
                    current_rows = []
                    current_kind = None
                    accepts_unheaded_rows = True
                continue
            if stripped.lower() == "tsv":
                flush_current()
                current_header = []
                current_rows = []
                current_kind = None
                accepts_unheaded_rows = True
                continue
            if stripped.startswith("主车型\t"):
                flush_current()
                current_header = stripped.split("\t")
                current_rows = []
                current_kind = "fitment"
                continue
            if stripped.startswith("Year\t主车型\t"):
                flush_current()
                current_header = stripped.split("\t")
                current_rows = []
                current_kind = "match"
                continue
            if "\t" not in line:
                flush_current()
                continue
            columns = line.rstrip("\r").split("\t")
            if current_kind == "match" and len(columns) >= len(MATCH_HEADER):
                current_rows.append(line.rstrip("\r"))
            elif len(columns) >= MIN_FITMENT_COLUMNS:
                if current_header is None or current_rows is None:
                    current_header = []
                    current_rows = []
                    current_kind = "fitment"
                current_rows.append(line.rstrip("\r"))
            elif current_rows:
                flush_current()

        flush_current()

        fitment_header, fitment_rows = table_segments[-1] if table_segments else ([], [])
        match_header, match_rows = match_segments[-1] if match_segments else ([], [])
        return fitment_header, fitment_rows, match_header, match_rows

    start_index, round_number = round_indexes[-1]
    header, cleaned, match_header, match_lines = clean_content(lines[start_index + 1 :])
    return ExtractedResult(
        source=path,
        round_number=round_number,
        header=header,
        lines=cleaned,
        match_header=match_header,
        match_lines=match_lines,
    )


def read_origin_header(origin_files: list[Path]) -> list[str]:
    for origin_file in origin_files:
        for line in origin_file.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                columns = line.rstrip("\r").split("\t")
                if normalize_header_name(columns[0]) == "主车型":
                    return upgrade_header([normalize_header_name(column) for column in columns])
                full_tsv = origin_file.parent.parent / "full.tsv"
                if full_tsv.exists():
                    for full_line in full_tsv.read_text(encoding="utf-8-sig").splitlines():
                        if full_line.strip():
                            full_columns = full_line.rstrip("\r").split("\t")
                            if normalize_header_name(full_columns[0]) == "主车型":
                                return upgrade_header([normalize_header_name(column) for column in full_columns])
                            break
                return STANDARD_HEADER
    return STANDARD_HEADER.copy()


def normalize_header_name(name: str) -> str:
    return HEADER_ALIASES.get(name.strip(), name.strip())


def upgrade_header(header: list[str]) -> list[str]:
    if header == STANDARD_HEADER:
        return header
    return STANDARD_HEADER.copy()


def split_generation(value: str) -> tuple[str, str]:
    value = value.strip()
    match = re.match(r"^(gen\d+[a-zA-Z]?)\s+(.+)$", value)
    if not match:
        return value, ""
    return match.group(1), match.group(2)


def infer_result_header(values: list[str]) -> list[str]:
    normalized_legacy_headers = [
        [normalize_header_name(column) for column in header]
        for header in LEGACY_HEADERS
    ]
    for header in normalized_legacy_headers:
        if len(values) == len(header):
            return header
    if len(values) == len(STANDARD_HEADER):
        return STANDARD_HEADER.copy()
    return []


def align_result_line(result_header: list[str], output_header: list[str], line: str) -> str:
    values = line.rstrip("\r").split("\t")
    if not result_header:
        result_header = infer_result_header(values)
        if not result_header:
            if not output_header:
                return line.rstrip("\r")
            return "\t".join((values + [""] * len(output_header))[: len(output_header)])

    normalized_result_header = [normalize_header_name(name) for name in result_header]
    row_by_header = {
        header: values[index] if index < len(values) else ""
        for index, header in enumerate(normalized_result_header)
    }
    if row_by_header.get("代际") and not row_by_header.get("代际说明"):
        generation, generation_note = split_generation(row_by_header["代际"])
        row_by_header["代际"] = generation
        row_by_header["代际说明"] = generation_note
    if row_by_header.get("代际说明"):
        if row_by_header.get("备注"):
            row_by_header["备注"] = f"{row_by_header['备注']}；{row_by_header['代际说明']}"
        else:
            row_by_header["备注"] = row_by_header["代际说明"]
    for field in AUTO_BLANK_FIELDS:
        row_by_header[field] = ""
    return "\t".join(row_by_header.get(header, "") for header in output_header)


def align_match_line(match_header: list[str], line: str) -> str:
    values = line.rstrip("\r").split("\t")
    normalized_header = [name.strip() for name in match_header]
    if not normalized_header and len(values) == len(MATCH_HEADER):
        normalized_header = MATCH_HEADER.copy()
    if not normalized_header:
        return "\t".join((values + [""] * len(MATCH_HEADER))[: len(MATCH_HEADER)])

    row_by_header = {
        header: values[index] if index < len(values) else ""
        for index, header in enumerate(normalized_header)
    }
    row_by_header["匹配数量"] = ""
    return "\t".join(row_by_header.get(header, "") for header in MATCH_HEADER)


def sort_key(path: Path) -> tuple:
    parts = re.split(r"(\d+)", path.stem)
    return tuple(int(part) if part.isdigit() else part for part in parts)


def merged_basename(origin_files: list[Path]) -> str:
    if not origin_files:
        return "merged"
    base = PART_SUFFIX_RE.sub("", origin_files[0].stem)
    return base or origin_files[0].stem


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_origin_dir = script_dir / "input_sheets"
    default_results_dir = script_dir / "output_sheets"
    default_output_dir = script_dir / "output_merged"
    default_log_dir = script_dir / "output_merged"

    parser = argparse.ArgumentParser(
        description="Merge the last Round / 下一步 section from the latest result markdown for each origin TSV."
    )
    parser.add_argument("--project", "--project-dir", "--project_dir", type=Path)
    parser.add_argument("--origin-dir", "--origin_dir", type=Path)
    parser.add_argument("--results-dir", "--results_dir", type=Path)
    parser.add_argument("--output-dir", "--output_dir", type=Path)
    parser.add_argument("--log-dir", "--log_dir", type=Path)
    parser.add_argument("--output", type=Path, help="Optional explicit merged TSV output path.")
    parser.add_argument("--log", type=Path, help="Optional explicit log output path.")
    parser.add_argument("--no-header", action="store_true", help="Do not write the merged TSV header row.")
    args = parser.parse_args()

    project_dir = args.project.resolve() if args.project else None
    if project_dir:
        origin_dir = (args.origin_dir or (project_dir / "input")).resolve()
        results_dir = (args.results_dir or (project_dir / "output")).resolve()
        output_dir = (args.output_dir or project_dir).resolve()
        log_dir = (args.log_dir or project_dir).resolve()
    else:
        origin_dir = (args.origin_dir or default_origin_dir).resolve()
        results_dir = (args.results_dir or default_results_dir).resolve()
        output_dir = (args.output_dir or default_output_dir).resolve()
        log_dir = (args.log_dir or default_log_dir).resolve()

    if not origin_dir.exists():
        raise FileNotFoundError(f"origin dir not found: {origin_dir}")
    if not results_dir.exists():
        raise FileNotFoundError(f"results dir not found: {results_dir}")

    origin_files = sorted(origin_dir.glob("*.tsv"), key=sort_key)
    origin_header = read_origin_header(origin_files)
    output_stem = merged_basename(origin_files)
    output_path = args.output.resolve() if args.output else (output_dir / f"{output_stem}_merged.tsv").resolve()
    log_path = args.log.resolve() if args.log else (log_dir / f"{output_stem}_merged.log").resolve()
    match_output_path = (output_path.parent / f"{output_path.stem}_subseries_match.tsv").resolve()

    merged_lines: list[str] = []
    match_lines: list[str] = []
    log_lines: list[str] = []

    if not args.no_header:
        merged_lines.append("\t".join(["来源文件", *origin_header]))
        match_lines.append("\t".join(MATCH_HEADER))
        log_lines.append(f"HEADER\torigin-dir\t{origin_header and origin_files[0].name or '(none)'}")

    stats = {"origin": len(origin_files), "merged_files": 0, "missing": 0, "no_round": 0, "rows": 0}

    for origin_file in origin_files:
        base = origin_file.stem
        latest_result = find_latest_result(results_dir, base)
        if latest_result is None:
            stats["missing"] += 1
            log_lines.append(f"MISSING\t{base}\t(no result md)")
            continue

        extracted = extract_last_round(latest_result)
        if extracted is None:
            stats["no_round"] += 1
            log_lines.append(f"NO_ROUND\t{base}\t{latest_result.name}")
            continue

        if extracted.lines:
            merged_lines.extend(
                f"{latest_result.name}\t{align_result_line(extracted.header, origin_header, line)}"
                for line in extracted.lines
            )
            stats["rows"] += len(extracted.lines)
            stats["merged_files"] += 1
            if extracted.match_lines:
                match_lines.extend(
                    align_match_line(extracted.match_header, line)
                    for line in extracted.match_lines
                )
            log_lines.append(
                f"MERGED\t{base}\t{latest_result.name}\tRound {extracted.round_number}\t{len(extracted.lines)} rows"
            )
        else:
            log_lines.append(f"EMPTY_ROUND\t{base}\t{latest_result.name}\tRound {extracted.round_number}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(merged_lines) + ("\n" if merged_lines else ""), encoding="utf-8")
    match_output_path.write_text("\n".join(match_lines) + ("\n" if match_lines else ""), encoding="utf-8")
    log_path.write_text("\n".join(log_lines) + ("\n" if log_lines else ""), encoding="utf-8")

    print(f"origin files: {stats['origin']}")
    print(f"merged files: {stats['merged_files']}")
    print(f"merged rows: {stats['rows']}")
    print(f"missing result md: {stats['missing']}")
    print(f"no round marker: {stats['no_round']}")
    print(f"output: {output_path}")
    print(f"subseries match output: {match_output_path}")
    print(f"log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
