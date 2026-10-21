import csv
import json
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT.parents[1] / "lib"))
sys.path.insert(0, str(PROJECT / "code"))
import shape_family_research as cli
from cover_shape.family_cache import family_id, read_cache

FIELDS = ["DIMENSION-ID", "MAKE", "MODEL", "版本", "CAB", "BED", "结构", "代际", "YEAR", "L-IN", "W-IN", "H-IN"]


def source_row(rid, generation, year, body="Hatchback"):
    return {"DIMENSION-ID": rid, "MAKE": "Synthetic", "MODEL": "Test", "版本": "", "CAB": "", "BED": "", "结构": body,
            "代际": generation, "YEAR": year, "L-IN": "170", "W-IN": "70", "H-IN": "58"}


@pytest.fixture
def env(tmp_path, monkeypatch):
    rows = [source_row("A 2010-2014 US", "gen1", "2010-2014"), source_row("A 2015-2019 US", "gen2", "2015-2019"),
            source_row("A Sedan 2015-2019 US", "gen2", "2015-2019", body="Sedan")]
    source = tmp_path / "source.csv"
    with source.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    families = {}
    for row in rows:
        key = {"market": "US", "make": "Synthetic", "model": "Test", "body_type": row["结构"]}
        families[row["结构"]] = family_id(key)
    queue = tmp_path / "queue.jsonl"
    queue.write_text("".join(json.dumps({"family_id": fid, "market": "US", "make": "Synthetic", "model": "Test", "body_type": body,
                                          "state": "PENDING"}) + "\n" for body, fid in families.items()), encoding="utf-8")
    for name, value in {"SOURCE": source, "CACHE": tmp_path / "family_cache.csv", "QUEUE": queue, "SHAPES": tmp_path / "none.csv",
                        "CLAIMS": tmp_path / "claims.csv", "LOCK": tmp_path / ".lock"}.items():
        monkeypatch.setattr(cli, name, value)
    return tmp_path, families


def test_claim_apply_covers_family_with_one_sample_year_per_rule(env, capsys):
    tmp_path, families = env
    cli.claim(1, "w", ["US"])
    out = capsys.readouterr().out
    assert families["Hatchback"] in out and families["Sedan"] not in out
    batch = tmp_path / "batch.json"
    batch.write_text(json.dumps([{"family_id": families["Hatchback"], "shape": "COMPACT_HATCH", "sample_years": [2012],
                                  "source_url": "https://example.org", "note": "测试"}]), encoding="utf-8")
    with pytest.raises(SystemExit, match="sample_years"):
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps([{"family_id": families["Hatchback"], "shape": "COMPACT_HATCH", "generation": "gen2",
                                    "sample_years": [2012], "source_url": "https://example.org", "note": "测试"}]), encoding="utf-8")
        cli.apply(bad, "w")
    cli.apply(batch, "w")
    rules = read_cache(tmp_path / "family_cache.csv")
    assert len(rules) == 1 and rules[0]["sample_years"] == "2012" and not cli.read_claims()


def test_apply_rejects_uncovered_records_and_foreign_families(env):
    tmp_path, families = env
    cli.claim(1, "w", ["US"])
    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps([{"family_id": families["Hatchback"], "generation": "gen1", "shape": "COMPACT_HATCH",
                                    "sample_years": [2012], "source_url": "https://example.org", "note": "测试"}]), encoding="utf-8")
    with pytest.raises(SystemExit, match="尚未覆盖 1 条"):
        cli.apply(partial, "w")
    foreign = tmp_path / "foreign.json"
    foreign.write_text(json.dumps([{"family_id": families["Sedan"], "shape": "STANDARD_SEDAN", "sample_years": [2016],
                                    "source_url": "https://example.org", "note": "测试"}]), encoding="utf-8")
    with pytest.raises(SystemExit, match="领取不一致"):
        cli.apply(foreign, "w")
    assert not (tmp_path / "family_cache.csv").exists()
