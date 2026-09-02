from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".pq",
    ".ps1",
    ".py",
    ".txt",
    ".tsv",
    ".yaml",
    ".yml",
}
EXCLUDED_PARTS = {
    ".git",
    ".bak",
    ".qwen",
    ".pytest_cache",
    ".qsyncclient",
    "__pycache__",
    "changes",
    "logs",
}
LEGACY_ID = re.compile(
    r"MAKE=(?P<make>[^|\r\n]*)"
    r"\|MODEL=(?P<model>[^|\r\n]*)"
    r"\|VERSION=(?P<version>[^|\r\n]*)"
    r"\|STRUCTURE=(?P<structure>[^|\r\n]*)"
    r"\|YEAR=(?P<year>\d{4}(?:-\d{4})?)"
    r"(?:\|CAB=(?P<cab>[^|,;\r\n`\"\)\]]*)"
    r"\|BED=(?P<bed>[^|,;\r\n`\"\)\]]*))?"
)


def decode_legacy_value(value: str) -> str:
    return value.replace("%7C", "|").replace("%25", "%").strip()


def compact_match(match: re.Match[str]) -> str:
    fields = ("make", "model", "version", "structure", "year", "cab", "bed")
    values = [decode_legacy_value(match.group(field) or "") for field in fields]
    return " ".join(value for value in values if value)


def migrate_text(text: str) -> tuple[str, int]:
    return LEGACY_ID.subn(compact_match, text)


def candidate_files(root: Path) -> list[Path]:
    current_script = Path(__file__).resolve()
    return [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and path.resolve() != current_script
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts)
    ]


def migrate_file(path: Path, *, apply: bool) -> int:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return 0
    migrated, count = migrate_text(text)
    if count and apply:
        temporary = path.with_suffix(path.suffix + ".tmp")
        encoded = migrated.encode("utf-8")
        if has_bom:
            encoded = b"\xef\xbb\xbf" + encoded
        temporary.write_bytes(encoded)
        os.replace(temporary, path)
    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将旧字段标签式 DIMENSION-ID 迁移为以空格连接的紧凑格式"
    )
    parser.add_argument("--apply", action="store_true", help="实际写入；默认只预览")
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    changed_files = 0
    replacements = 0
    for path in candidate_files(root):
        count = migrate_file(path, apply=args.apply)
        if count:
            changed_files += 1
            replacements += count
            print(f"{path.relative_to(root)}: {count}")
    mode = "已迁移" if args.apply else "预览"
    print(f"{mode}: {changed_files} 个文件，{replacements} 处 DIMENSION-ID")


if __name__ == "__main__":
    main()
