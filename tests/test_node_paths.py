import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from artifact_refs import batch_of, record_references  # noqa: E402
from node_paths import canonical_path, canonical_record, node_dir_name  # noqa: E402


def make_repo(tmp_path: Path) -> Path:
    (tmp_path / "nodes" / "A0.尺码计算").mkdir(parents=True)
    (tmp_path / "nodes" / "D1.发货评估").mkdir(parents=True)
    (tmp_path / "nodes" / "D2.链接分析" / "皮卡").mkdir(parents=True)
    (tmp_path / "lib").mkdir()
    return tmp_path


def test_legacy_recorded_paths_are_read_as_nodes_paths(tmp_path):
    repo = make_repo(tmp_path)
    assert canonical_path("A0.尺码计算/artifacts/b/output/x.csv", repo) == "nodes/A0.尺码计算/artifacts/b/output/x.csv"
    assert canonical_path("A0.尺码计算", repo) == "nodes/A0.尺码计算"
    assert canonical_path("nodes/A0.尺码计算/output/x.csv", repo) == "nodes/A0.尺码计算/output/x.csv"
    # 节点内相对路径、仓库级目录和普通文本不受影响
    for value in ("US/全量/全量表.csv", "data/规则.csv", "lib/x.py", "尺寸库.csv", "A0.尺码计算 已变化"):
        assert canonical_path(value, repo) == value


def test_renamed_d1_recorded_paths_are_read_as_delivery_evaluation(tmp_path):
    repo = make_repo(tmp_path)
    assert canonical_path("D1.聚类SKU/artifacts/b/output/x.csv", repo) == "nodes/D1.发货评估/artifacts/b/output/x.csv"
    assert canonical_path("nodes/D1.聚类SKU/artifacts/b/output/x.csv", repo) == "nodes/D1.发货评估/artifacts/b/output/x.csv"
    assert canonical_path("D1.聚类SKU", repo) == "nodes/D1.发货评估"
    assert canonical_path("D1.聚类SKU 已变化", repo) == "D1.聚类SKU 已变化"


def test_canonical_record_rewrites_nested_manifest_fields(tmp_path):
    repo = make_repo(tmp_path)
    manifest = {
        "path": "A0.尺码计算", "artifact": "A0.尺码计算/artifacts/b",
        "deliverables": [{"file": "US/表.csv", "artifact_file": "A0.尺码计算/artifacts/b/output/US/表-20260101_01.csv"}],
        "extras": ["A0.尺码计算/artifacts/b/extra/REPORT.md"],
    }
    record = canonical_record(manifest, repo)
    assert record["path"] == "nodes/A0.尺码计算"
    assert record["deliverables"][0] == {"file": "US/表.csv", "artifact_file": "nodes/A0.尺码计算/artifacts/b/output/US/表-20260101_01.csv"}
    assert record["extras"] == ["nodes/A0.尺码计算/artifacts/b/extra/REPORT.md"]


def test_node_dir_name_strips_nodes_prefix():
    assert node_dir_name("nodes/D2.链接分析/皮卡") == "D2.链接分析/皮卡"
    assert node_dir_name("A0.尺码计算") == "A0.尺码计算"


def test_unc_and_arbitrary_text_never_trigger_filesystem_lookup(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("arbitrary records must not stat network paths")
    monkeypatch.setattr(Path, "is_dir", forbidden)
    for value in (r"\\NAS8824B4\Public\archive", "D:/archive/file.csv", "a note", "a"*10000):
        assert canonical_path(value) == value


def test_batch_of_handles_nodes_prefix_and_nested_nodes():
    assert batch_of("nodes/A0.尺码计算/artifacts/b1/output/x.csv") == "nodes/A0.尺码计算/artifacts/b1"
    assert batch_of("nodes/D2.链接分析/皮卡/artifacts/b2/output/x.csv") == "nodes/D2.链接分析/皮卡/artifacts/b2"
    assert batch_of("A0.尺码计算/artifacts/b0/output/x.csv") == "A0.尺码计算/artifacts/b0"
    assert batch_of("nodes/A0.尺码计算/output/x.csv") is None
    assert record_references({"deliverables": [{"artifact_file": "nodes/D2.链接分析/皮卡/artifacts/b2/output/x.csv"}]}) == {
        "nodes/D2.链接分析/皮卡/artifacts/b2"
    }
