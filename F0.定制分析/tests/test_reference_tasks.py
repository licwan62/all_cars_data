import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run import reference_tasks


def test_cross_generation_sku_creates_separate_reference_tasks():
    config = {"sketchfab_generation_by_internal_generation": {"gen1": "R60", "gen2": "F60"},
              "sketchfab_searches": [{"generation": "R60", "query": "R60", "representative_url": "https://example.com/model"}]}
    members = [{"SKU聚簇": "SKU1", "DIMENSION-ID": "a"}, {"SKU聚簇": "SKU1", "DIMENSION-ID": "b"}]
    rows = [{"DIMENSION-ID": "a", "代际": "gen1"}, {"DIMENSION-ID": "b", "代际": "gen2"}]
    tasks = {task["代际"]: task for task in reference_tasks(config, members, rows)}
    assert len(tasks) == 2
    assert tasks["R60"]["状态"] == "待外形核验"
    assert tasks["F60"]["状态"] == "待补参考模型"
    assert tasks["F60"]["覆盖车型"] == "b"
