from __future__ import annotations

import csv
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from src.config import Settings
from src.main import determine_mode, run


def settings(tmp_path: Path, input_path: Path) -> Settings:
    return Settings(
        project_root=tmp_path,
        input_path=input_path,
        encoding="utf-8-sig",
        make_column="MAKE",
        model_column="MODEL",
        sales_column="销量合计",
        code_width=2,
        max_code=99,
        make_mapping_path=tmp_path / "mapping" / "make_mapping.csv",
        model_mapping_path=tmp_path / "mapping" / "model_mapping.csv",
        artifact_root=tmp_path / "artifacts",
        artifact_slug="code-mapping-publish",
        publish_path=tmp_path / "public" / "code" / "_mapping" / "vehicle_mapping.csv",
        public_publish_path=tmp_path / "public_publish" / "vehicle_mapping.csv",
        backup_enabled=True,
        backup_path=tmp_path / "mapping" / "backups",
    )


def write_input(path: Path, rows: list[tuple[str, str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["MAKE", "MODEL", "销量合计"])
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_initial_then_update_preserves_codes_and_creates_backup(tmp_path):
    source = tmp_path / "full.csv"
    cfg = settings(tmp_path, source)
    write_input(source, [("Toyota", "Corolla", "1000"), ("Ford", "Focus", "800")])
    assert run(cfg)["mode"] == "INITIAL"
    initial = {(r["MAKE"], r["MAKE_CODE"]) for r in read_csv(cfg.make_mapping_path)}
    assert initial == {("Toyota", "00"), ("Ford", "01")}

    write_input(source, [("Ford", "Focus", "5000"), ("Toyota", "RAV4", "100"), ("Honda", "Civic", "900")])
    result = run(cfg)
    assert result["mode"] == "UPDATE"
    makes = {r["MAKE"]: r["MAKE_CODE"] for r in read_csv(cfg.make_mapping_path)}
    assert makes == {"Toyota": "00", "Ford": "01", "Honda": "02"}
    models = {(r["MAKE"], r["MODEL"]): (r["MODEL_CODE"], r["STATUS"]) for r in read_csv(cfg.model_mapping_path)}
    assert models[("Toyota", "Corolla")] == ("00", "INACTIVE")
    assert models[("Toyota", "RAV4")] == ("01", "ACTIVE")
    assert len(list(cfg.backup_path.glob("*.csv"))) == 2


def test_dry_run_writes_nothing(tmp_path):
    source = tmp_path / "full.csv"
    cfg = settings(tmp_path, source)
    write_input(source, [("Toyota", "Corolla", "1000")])
    result = run(cfg, dry_run=True)
    assert result["new_makes"] == 1
    assert not cfg.make_mapping_path.exists()
    assert not cfg.model_mapping_path.exists()
    assert not cfg.publish_path.exists()
    assert not cfg.artifact_root.exists()


def test_inconsistent_mapping_state_is_rejected(tmp_path):
    source = tmp_path / "full.csv"
    cfg = settings(tmp_path, source)
    cfg.make_mapping_path.parent.mkdir(parents=True)
    cfg.make_mapping_path.write_text("MAKE,MAKE_CODE\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Mapping state is inconsistent"):
        determine_mode(cfg)


def test_case_and_outer_whitespace_share_one_mapping(tmp_path):
    source = tmp_path / "full.csv"
    cfg = settings(tmp_path, source)
    write_input(source, [(" Toyota ", " Corolla ", "1,234"), ("toyota", "corolla", "6")])
    result = run(cfg)
    assert result["unique_makes"] == 1
    assert result["unique_models"] == 1
    row = read_csv(cfg.model_mapping_path)[0]
    assert row["INITIAL_SALES"] == "1240"


def test_formal_run_creates_immutable_artifact_and_publication(tmp_path):
    source = tmp_path / "full.csv"
    cfg = settings(tmp_path, source)
    write_input(source, [("Toyota", "Corolla", "1000")])
    run(cfg)
    run(cfg)
    batches = sorted(path for path in cfg.artifact_root.iterdir() if path.is_dir())
    day = date.today().isoformat()
    assert [path.name for path in batches] == [
        f"{day}_01_code-mapping-publish",
        f"{day}_02_code-mapping-publish",
    ]
    assert (batches[0] / "output" / "vehicle_mapping.csv").exists()
    assert (batches[0] / "mapping" / "make_mapping.csv").exists()
    assert (batches[0] / "mapping" / "model_mapping.csv").exists()
    assert (batches[0] / "input" / source.name).exists()
    assert (batches[0] / "run_report.json").exists()
    assert (batches[0] / "validation.json").exists()
    assert read_csv(cfg.publish_path)[0]["MAKE_CODE"] == "00"
