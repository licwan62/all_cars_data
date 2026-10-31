"""Publish explicitly registered historical imports, independently of online crawling."""
import csv
import json
import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch, sha256


def run():
    config = json.loads((PROJECT / "data" / "candidate_sources.json").read_text(encoding="utf-8"))
    sources = []
    with RunBatch.create(PROJECT / "artifacts", "offline-candidates", PROJECT / "data") as batch:
        for item in config["files"]:
            source = (PROJECT / "data" / item["source"]).resolve()
            source.relative_to((PROJECT / "data").resolve())
            if sha256(source) != item["sha256"]:
                raise ValueError(f"历史导入源已变化，请核实并更新来源登记：{item['source']}")
            shutil.copy2(source, batch.output(item["output"]))
            sources.append({"file": item["output"], "raw_sha256": item["sha256"], "source_kind": "historical-import", "original_path": item["original_path"], "verified_origin": False})
        batch.output("候选来源.json").write_text(json.dumps({"schema_version": 1, "files": sources}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        batch.finish({"source_kind": "historical-import", "files": len(sources)}, publish_to=PROJECT / "output")


if __name__ == "__main__":
    run()
