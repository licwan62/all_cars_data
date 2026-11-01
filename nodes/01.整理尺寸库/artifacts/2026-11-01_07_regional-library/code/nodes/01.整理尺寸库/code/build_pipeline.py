"""Offline first build. Read only upstream output and own rules; never write data/."""
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

import merge_dimension_library as merge
from regional_sources import build_eu_base, build_ru_base

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from artifact_batch import RunBatch
from regional_size_common import build_dimension_library_rows, write_dimension_library
from us_model_splits import apply_splits, write_table, MIGRATION_FIELDS, CANDIDATE_FIELDS, PENDING_FIELDS
from us_dimension_corrections import apply_corrections
from us_year_supplements import apply_supplements, REVIEW_FIELDS as SUPPLEMENT_FIELDS


def run():
    source = ROOT / "nodes" / "00.自动化尺寸抓取器" / "output"
    config = json.loads((PROJECT / "data" / "build_config.json").read_text(encoding="utf-8"))
    with RunBatch.create(PROJECT / "artifacts", "regional-library", PROJECT / "data") as batch, tempfile.TemporaryDirectory(prefix="dimension-build-") as temporary:
        batch.input_published(source)
        work = Path(temporary)
        for region, builder in (("eu", build_eu_base), ("ru", build_ru_base)):
            args = (source / region.upper(), config["as_of_year"]) if region == "eu" else (source / region.upper(),)
            base, _ = builder(*args)
            library, _, row_ids = build_dimension_library_rows(base)
            destination = work / region
            destination.mkdir()
            write_dimension_library(library, destination / f"00_{region.upper()}尺寸库.csv")
            mapping = __import__("pandas").DataFrame({"来源ID": base["DIMENSION-ID"].astype("string"), "00库ID": row_ids}).drop_duplicates()
            mapping.to_csv(destination / f"来源映射_{region.upper()}.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
        (work / "us").mkdir()
        shutil.copy2(source / "US" / "00_US尺寸库.csv", work / "us" / "00_US尺寸库.csv")
        old_latest = merge.latest_batch
        try:
            merge.latest_batch = lambda region: work / region
            traced = {r: merge.load_region_traced(r) for r in merge.REGIONS}
            plan = json.loads((PROJECT / "data/us/audi_a7_split.json").read_text(encoding="utf-8"))
            evidence = json.loads((PROJECT / "data/us/audi_a7_evidence.json").read_text(encoding="utf-8"))
            for item in evidence["sources"]:
                if item.get("file"):
                    local = (PROJECT / item["file"]).resolve()
                    local.relative_to((PROJECT / "data").resolve())
                    if hashlib.sha256(local.read_bytes()).hexdigest() != item["sha256"]:
                        raise ValueError("本地证据SHA已变化；需重审登记")
            with (PROJECT / "data/data_source/trimslate-vehicles.csv").open(encoding="utf-8-sig", newline="") as stream:
                reference = list(csv.DictReader(stream))
            us_rows, migrations, candidates, pending = apply_splits(traced["us"][0], plan, evidence, reference)
            corrections = json.loads((PROJECT / "data/us/dimension_corrections.json").read_text(encoding="utf-8"))
            us_rows = apply_corrections(us_rows, corrections)
            gap_rules = json.loads((PROJECT / "data/us/year_gap_resolutions.json").read_text(encoding="utf-8"))
            us_rows, supplement_review = apply_supplements(us_rows, gap_rules, PROJECT)
            traced["us"] = (us_rows, traced["us"][1])
            merged = [row for region in merge.REGIONS for row in sorted(traced[region][0], key=lambda r: r["DIMENSION-ID"])]
            write_table(batch.output("US_ID迁移.csv"), MIGRATION_FIELDS, migrations)
            write_table(batch.output("US_拆分候选.csv"), CANDIDATE_FIELDS, candidates)
            write_table(batch.output("US_拆分待核.csv"), PENDING_FIELDS, pending)
            write_table(batch.output("US_补库核对.csv"), SUPPLEMENT_FIELDS, supplement_review)
            pending_supplements = [row for row in supplement_review if row["处理结果"] != "verified_add"]
            write_table(batch.output("US_补库待核.csv"), SUPPLEMENT_FIELDS, pending_supplements)
            merge.validate_eu_migration(traced["eu"][0])
            for region, (rows, _) in traced.items():
                merge.write_csv_atomic(batch.output(f"尺寸库_{region.upper()}.csv"), rows)
            merge.write_csv_atomic(batch.output("尺寸库.csv"), merged)
            for region in merge.SOURCE_MAP_REGIONS:
                rows, stage = traced[region]
                mapping = merge.source_mapping(region, {r["DIMENSION-ID"] for r in rows}, stage)
                merge.write_source_mapping(batch.output(f"来源映射_{region.upper()}.csv"), mapping)
            shutil.copy2(merge.EU_MIGRATION_PATH, batch.output("EU_ID迁移.csv"))
        finally:
            merge.latest_batch = old_latest
        batch.finish({"rows": len(merged), "as_of_year": config["as_of_year"],
                      "us_split_candidates": len(candidates), "us_split_pending": len(pending),
                      "us_applied_migrations": len(migrations),
                      "us_supplements_added": sum(row["处理结果"] == "verified_add" for row in supplement_review),
                      "us_supplements_pending_or_excluded": len(pending_supplements)},
                      publish_to=PROJECT / "output")


if __name__ == "__main__":
    run()
