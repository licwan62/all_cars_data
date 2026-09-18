"""Split a source TSV into ordered, auditable chunks."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AuditResult:
    origin_rows: int
    part_files: int
    part_rows: int
    missing_rows: list[str]
    extra_rows: list[str]
    order_matches: bool
    first_order_mismatch: tuple[int, str, str] | None


def read_rows(path: Path) -> list[str]:
    return [line.rstrip("\r\n") for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def split_header(rows: list[str]) -> tuple[str | None, list[str]]:
    if not rows:
        return None, []
    return rows[0], rows[1:]


def strip_part_header(rows: list[str], header: str | None) -> list[str]:
    if header is not None and rows and rows[0] == header:
        return rows[1:]
    return rows


def part_number(path: Path) -> int:
    stem = path.stem
    try:
        return int(stem.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return 0


def find_part_files(parts_dir: Path, prefix: str) -> list[Path]:
    return sorted(parts_dir.glob(f"{prefix}_part_*.tsv"), key=part_number)


def audit_split(origin_path: Path, parts_dir: Path, prefix: str) -> AuditResult:
    origin_rows = read_rows(origin_path)
    header, origin_data_rows = split_header(origin_rows)
    part_files = find_part_files(parts_dir, prefix)

    part_rows: list[str] = []
    for part_file in part_files:
        part_rows.extend(strip_part_header(read_rows(part_file), header))

    missing_rows = list((Counter(origin_data_rows) - Counter(part_rows)).elements())
    extra_rows = list((Counter(part_rows) - Counter(origin_data_rows)).elements())
    order_matches = origin_data_rows == part_rows

    first_order_mismatch = None
    if not order_matches:
        for index, (origin_row, part_row) in enumerate(zip(origin_data_rows, part_rows), start=1):
            if origin_row != part_row:
                first_order_mismatch = (index, origin_row, part_row)
                break
        if first_order_mismatch is None and len(origin_data_rows) != len(part_rows):
            row_index = min(len(origin_data_rows), len(part_rows))
            origin_row = origin_data_rows[row_index] if len(origin_data_rows) > len(part_rows) else ""
            part_row = part_rows[row_index] if len(part_rows) > len(origin_data_rows) else ""
            first_order_mismatch = (row_index + 1, origin_row, part_row)

    return AuditResult(
        origin_rows=len(origin_data_rows),
        part_files=len(part_files),
        part_rows=len(part_rows),
        missing_rows=missing_rows,
        extra_rows=extra_rows,
        order_matches=order_matches,
        first_order_mismatch=first_order_mismatch,
    )


def write_ordered_split(origin_path: Path, output_dir: Path, prefix: str, chunk_size: int, force: bool) -> list[Path]:
    rows = read_rows(origin_path)
    header, data_rows = split_header(rows)
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = list(output_dir.glob(f"{prefix}_part_*.tsv"))
    if existing and not force:
        names = ", ".join(path.name for path in sorted(existing, key=part_number)[:5])
        raise FileExistsError(
            f"{output_dir} already contains {len(existing)} matching part files ({names}...). "
            "Use --force to overwrite them."
        )

    if force:
        for path in existing:
            path.unlink()

    written: list[Path] = []
    if header is None:
        return written

    for index in range(0, len(data_rows), chunk_size):
        part_index = index // chunk_size + 1
        part_path = output_dir / f"{prefix}_part_{part_index:02d}.tsv"
        chunk = [header, *data_rows[index : index + chunk_size]]
        part_path.write_text("\n".join(chunk) + "\n", encoding="utf-8")
        written.append(part_path)

    if not data_rows:
        part_path = output_dir / f"{prefix}_part_01.tsv"
        part_path.write_text(header + "\n", encoding="utf-8")
        written.append(part_path)

    return written


def print_audit(result: AuditResult) -> None:
    print(f"origin data rows: {result.origin_rows}")
    print(f"part files: {result.part_files}")
    print(f"part rows: {result.part_rows}")
    print(f"missing exact rows: {len(result.missing_rows)}")
    print(f"extra exact rows: {len(result.extra_rows)}")
    print(f"order matches origin: {'yes' if result.order_matches else 'no'}")

    if result.first_order_mismatch:
        index, origin_row, part_row = result.first_order_mismatch
        print(f"first order mismatch at row: {index}")
        print(f"origin row: {origin_row}")
        print(f"part row: {part_row}")

    if result.missing_rows:
        print("first missing rows:")
        for row in result.missing_rows[:10]:
            print(row)

    if result.extra_rows:
        print("first extra rows:")
        for row in result.extra_rows[:10]:
            print(row)


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_origin = script_dir / "input_sheets" / "0530_origin.tsv"
    default_parts_dir = script_dir / "input_sheets" / "0530_split_origin"
    default_output_dir = script_dir / "input_sheets" / "0530_split_origin_ordered"

    parser = argparse.ArgumentParser(
        description="Audit split TSV files against the origin TSV, and optionally write ordered split files."
    )
    parser.add_argument("--origin", type=Path, default=default_origin)
    parser.add_argument("--parts-dir", type=Path, default=default_parts_dir)
    parser.add_argument("--output-dir", type=Path, default=default_output_dir)
    parser.add_argument("--prefix", default="1_brand50")
    parser.add_argument("--chunk-size", type=int, default=50)
    parser.add_argument("--write", action="store_true", help="Write ordered split files to --output-dir.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing matching files in --output-dir.")
    args = parser.parse_args()

    origin_path = args.origin.resolve()
    parts_dir = args.parts_dir.resolve()
    output_dir = args.output_dir.resolve()

    if not origin_path.exists():
        raise FileNotFoundError(f"origin TSV not found: {origin_path}")

    if args.chunk_size <= 0:
        raise ValueError("--chunk-size must be greater than 0")

    if args.write:
        written = write_ordered_split(origin_path, output_dir, args.prefix, args.chunk_size, args.force)
        print(f"written files: {len(written)}")
        print(f"output dir: {output_dir}")
        print(f"rows per full part: {args.chunk_size}")

        result = audit_split(origin_path, output_dir, args.prefix)
        print()
        print("audit ordered output:")
        print_audit(result)
        return 0

    if not parts_dir.exists():
        raise FileNotFoundError(f"parts dir not found: {parts_dir}")

    result = audit_split(origin_path, parts_dir, args.prefix)
    print_audit(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
