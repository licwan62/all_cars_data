import csv
import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "src" / "merge_partition_tables.py"
SPEC = importlib.util.spec_from_file_location("merge_partition_tables", MODULE_PATH)
merger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(merger)


MAPPING_HEADER = ["id", "Ktype", "DIMENSION_GROUP_ID"]
DIMENSION_HEADER = [
    "DIMENSION_GROUP_ID",
    "LengthMM",
    "WidthMM",
    "HeightMM",
    "DimensionSource",
    "SourceURL",
]


def write_tsv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def build_run(tmp_path, statuses=("成功", "成功", "成功", "成功")):
    project = tmp_path / "project"
    table_root = project / "tables"
    input_path = project / "input.tsv"
    write_tsv(input_path, ["Ktype"], [[str(index)] for index in range(1, 5)])
    tasks = []
    for part in range(1, 5):
        task_id = f"task-{part}"
        tasks.append({"index": part - 1, "partition": part, "task_id": task_id})
        checkpoint = project / "checkpoints" / f"part-{part:02d}" / f"{task_id}.json"
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        checkpoint.write_text(
            json.dumps({"task_id": task_id, "status": statuses[part - 1]}),
            encoding="utf-8",
        )
        group_id = "CAR-01"
        dimensions = ["4000", "1800", "1500"] if part < 3 else ["4200", "1800", "1500"]
        write_tsv(
            table_root / f"part-{part:02d}" / "ktype_mapping_final.tsv",
            MAPPING_HEADER,
            [[str(part), str(part), group_id]],
        )
        write_tsv(
            table_root / f"part-{part:02d}" / "dimension_groups_final.tsv",
            DIMENSION_HEADER,
            [[group_id, *dimensions, "source", f"https://example.com/{part}"]],
        )
    manifest = {
        "version": 2,
        "hash_mode": "portable_utf8_lf_v1",
        "run_id": "test-run",
        "partition_count": 4,
        "task_count": 4,
        "input_files": [
            {"path": "input.tsv", "sha256": merger.portable_text_sha256(input_path)}
        ],
        "tasks": tasks,
    }
    manifest_path = project / "partition_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return project, table_root, manifest_path


def test_merge_reconciles_dimension_ids_and_audits(tmp_path):
    project, table_root, manifest_path = build_run(tmp_path)
    manifest = merger.validate_manifest(project, manifest_path, 4)
    assert merger.validate_completion(project, manifest, False) == []
    mh, mappings, dh, dimensions, remaps = merger.merge_tables(table_root, 4)
    report = merger.audit(project, manifest, mh, mappings, dh, dimensions, [], remaps)
    assert report["passed"] is True
    assert [row[2] for row in mappings] == ["CAR-01", "CAR-01", "CAR-02", "CAR-02"]
    assert len(dimensions) == 2
    assert len(remaps) == 2


def test_incomplete_checkpoint_blocks_final_merge(tmp_path):
    project, _, manifest_path = build_run(
        tmp_path, statuses=("成功", "成功", "进行中", "成功")
    )
    manifest = merger.validate_manifest(project, manifest_path, 4)
    try:
        merger.validate_completion(project, manifest, False)
    except ValueError as exc:
        assert "未成功" in str(exc)
    else:
        raise AssertionError("incomplete task was not rejected")


def test_almost_checkpoint_is_incomplete_and_reported_when_allowed(tmp_path):
    project, _, manifest_path = build_run(
        tmp_path, statuses=("成功", "Almost", "成功", "成功")
    )
    manifest = merger.validate_manifest(project, manifest_path, 4)

    try:
        merger.validate_completion(project, manifest, False)
    except ValueError as exc:
        assert "Almost" in str(exc)
        assert "task-2" in str(exc)
    else:
        raise AssertionError("Almost task was treated as a successful final merge")

    issues = merger.validate_completion(project, manifest, True)
    assert len(issues) == 1
    assert "task-2" in issues[0]
    assert "Almost" in issues[0]


def test_input_hash_change_is_rejected(tmp_path):
    project, _, manifest_path = build_run(tmp_path)
    (project / "input.tsv").write_text("Ktype\nchanged\n", encoding="utf-8")
    try:
        merger.validate_manifest(project, manifest_path, 4)
    except ValueError as exc:
        assert "哈希不匹配" in str(exc)
    else:
        raise AssertionError("changed input was not rejected")


def test_manifest_accepts_equivalent_crlf_checkout(tmp_path):
    project, _, manifest_path = build_run(tmp_path)
    input_path = project / "input.tsv"
    input_path.write_bytes(input_path.read_bytes().replace(b"\n", b"\r\n"))
    merger.validate_manifest(project, manifest_path, 4)
