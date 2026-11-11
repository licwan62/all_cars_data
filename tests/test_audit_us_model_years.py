import csv
import json

from audit_us_model_years import audit


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        columns = list(rows[0])
        path.write_text(json.dumps({"schema":"vehicle-pipeline/table-v1", "columns":columns, "rows":[[str(r[c]) for c in columns] for r in rows]}),encoding="utf-8")
        return
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_combined_rs7_error_is_reclassified_and_previous_report_preserved(tmp_path):
    node = tmp_path / "nodes/01.整理尺寸库"
    write(tmp_path / "json/dimension-library/尺寸库_US.json", [
        {"DIMENSION-ID": "combined", "MAKE": "Audi", "MODEL": "A7/S7/RS7", "YEAR": "2012-2025", "L-IN": "197", "W-IN": "75", "H-IN": "55"},
        {"DIMENSION-ID": "rs7-2026", "MAKE": "Audi", "MODEL": "RS7", "YEAR": "2026", "L-IN": "197", "W-IN": "76", "H-IN": "55"}])
    write(tmp_path / "nodes/M0.车型年覆盖/data/data_source/trimslate-vehicles.csv", [
        {"make": "Audi", "model": "RS 7", "year": str(year)} for year in (2025, 2026, 2027)])
    write(tmp_path / "nodes/M0.车型年覆盖/data/data_source/vehicles.csv", [{"make_name": "Audi", "model_name": "RS 7", "countries": "us", "aliases": "", "body_types": "liftback"}])
    (node / "data").mkdir(parents=True, exist_ok=True)
    (node / "data/build_config.json").write_text('{"as_of_year":2026}')
    (node / "data/us").mkdir()
    (node / "data/us/model_members.json").write_text(json.dumps({"schema_version": 1, "groups": [
        {"make": "Audi", "model": "A7/S7/RS7", "status": "registered", "members": [{"model": "RS7", "aliases": ["RS 7"]}]}]}))
    prior = tmp_path / "prior"
    write(prior / "车型年份核对.csv", [{"MAKE": "Audi", "SOURCE_MODEL": "RS 7", "YEAR": "2025", "结果": "同名车型年份缺口"}])
    original = (prior / "车型年份核对.csv").read_bytes()
    report = audit(tmp_path, tmp_path / "new", prior)
    assert report["in_scope_counts"] == {"组合记录覆盖、成员年份待核": 1, "独立记录覆盖": 1}
    assert report["future_counts"] == {"确认年份缺口（本地参考差集）": 1}
    assert report["previous_gap_reclassified_as_group"] == 1
    assert (prior / "车型年份核对.csv").read_bytes() == original


def test_research_dispositions_do_not_claim_publication_or_override_coverage(tmp_path):
    node = tmp_path / "nodes/01.整理尺寸库"
    write(tmp_path / "json/dimension-library/尺寸库_US.json", [
        {"DIMENSION-ID": "independent", "MAKE": "A", "MODEL": "M", "YEAR": "2020", "L-IN": "180", "W-IN": "70", "H-IN": "60"},
        {"DIMENSION-ID": "group", "MAKE": "A", "MODEL": "X/Y", "YEAR": "2021", "L-IN": "180", "W-IN": "70", "H-IN": "60"}])
    write(tmp_path / "nodes/M0.车型年覆盖/data/data_source/trimslate-vehicles.csv", [
        {"make": "A", "model": model, "year": str(year)}
        for model, year in [("M", 2020), ("M", 2021), ("M", 2022), ("M", 2023), ("X", 2021)]])
    write(tmp_path / "nodes/M0.车型年覆盖/data/data_source/vehicles.csv", [{"make_name": "A", "model_name": "M", "countries": "us", "aliases": "", "body_types": ""}])
    (node / "data").mkdir(parents=True, exist_ok=True)
    (node / "data/build_config.json").write_text('{"as_of_year":2026}')
    (node / "data/us").mkdir()
    (node / "data/us/model_members.json").write_text(json.dumps({"schema_version": 1, "groups": [
        {"make": "A", "model": "X/Y", "status": "registered", "members": [{"model": "X", "aliases": []}]}]}))
    def rule(model, year, status):
        return {"make": "A", "model": model, "year": year, "status": status,
                "sources": [{"url": "https://example.com"}]}
    (node / "data/us/year_gap_resolutions.json").write_text(json.dumps({"schema_version": 1, "resolutions": [
        rule("M", 2020, "excluded_reference_year"), rule("M", 2021, "verified_add"),
        rule("M", 2022, "excluded_reference_year"), rule("M", 2023, "pending"),
        rule("X", 2021, "verified_add")]}))
    report = audit(tmp_path, tmp_path / "report")
    assert report["in_scope_counts"] == {"独立记录覆盖": 1, "尺寸候选待发布": 1,
        "参考年份排除": 1, "候选待核": 1, "组合记录覆盖、成员年份待核": 1}
    assert "year_resolutions" in report["sources"]
