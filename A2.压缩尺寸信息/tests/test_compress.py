from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from src import run as run_mod  # noqa: E402
from src import publish_ssh  # noqa: E402

FIELDS = ["MAKE", "MODEL", "版本", "结构", "CAB", "BED", "YEAR", "分类", "尺寸组销量", "自动尺码", "DIMENSION-ID"]


def row(make="Ford", model="Focus", version="", structure="Sedan", cab="", bed="", year="2018-2019", category="三厢车", size="M", region="US", sales=0):
    return {
        "MAKE": make, "MODEL": model, "版本": version, "结构": structure, "CAB": cab, "BED": bed,
        "YEAR": year, "分类": category, "尺寸组销量": str(sales), "自动尺码": size,
        "DIMENSION-ID": " ".join(part for part in [make, model, version, structure, year, region] if part),
    }


def profile() -> dict:
    return run_mod.load_field_profile((PROJECT_DIR / "data" / run_mod.FIELD_PROFILE).resolve())


def compress(rows: list[dict], region: str = "US") -> dict[str, pd.DataFrame]:
    frame = pd.DataFrame(rows, columns=FIELDS).astype(str)
    return run_mod.compress_line(region, frame, profile(), region)["tables"]


def years_of(table: pd.DataFrame) -> list[str]:
    return sorted(table["YEAR"].tolist())


def test_single_year_rows_are_kept():
    # 旧算法只认 YYYY-YYYY，单年份行被整行跳过（US 约 30%）
    tables = compress([row(year="1987"), row(year="1988"), row(year="1989-1990")])
    assert years_of(tables["non_pickup_lossless"]) == ["1987-1990"]


def test_versions_with_different_sizes_are_not_majority_voted():
    tables = compress([
        row(model="Blazer", version="2dr", structure="SUV", year="1995-1997", size="YM"),
        row(model="Blazer", version="4dr", structure="SUV", year="1995-1997", size="YL"),
    ])
    high = tables["non_pickup_high"]
    assert set(zip(high["VERSION"], high["BACKSIZE"])) == {("2dr", "YM"), ("4dr", "YL")}


def test_same_size_rows_merge_in_high_table():
    tables = compress([row(year="2018-2019", size="M"), row(year="2020-2021", size="M")])
    assert years_of(tables["non_pickup_high"]) == ["2018-2021"]


def test_overlapping_same_size_versions_merge_into_one_row():
    # Golf：GTI、GTI/R、R 两两年份重叠且同尺码，任意两条合并后第三条仍命中同一原子；同尺码重复命中不算冲突
    tables = compress([
        row(model="Golf", structure="Hatchback", year="2000-2021", size="2XL"),
        row(model="Golf", structure="Hatchback", version="GTI", year="2015-2026", size="2XL"),
        row(model="Golf", structure="Hatchback", version="GTI/R", year="2022-2026", size="2XL"),
        row(model="Golf", structure="Hatchback", version="R", year="2022-2026", size="2XL"),
    ])
    high = tables["non_pickup_high"]
    assert high[["YEAR", "VERSION"]].values.tolist() == [["2000-2026", "Incl: GTI/R"]]


def test_merge_never_loses_atoms_when_versions_contain_slashes():
    # Berlingo：合并版本串 "Incl: m low/m/m high" 中 "m/m" 按单字母版本保护，切出 "m/m high"，m high 原子会变成 MISS；
    # 合并必须保留左右两条原来覆盖的原子
    berlingo = dict(model="Berlingo", size="2L+", region="EU")
    frame = pd.DataFrame([
        row(structure="Van", year="2008-2026", **berlingo),
        row(structure="MPV", version="m", year="2018-2026", **berlingo),
        row(structure="Van", version="m", year="2018-2026", **berlingo),
        row(structure="Van", version="m high", year="2021-2026", **berlingo),
        row(structure="Van", version="m low", year="2021-2026", **berlingo),
    ], columns=FIELDS).astype(str)
    check = run_mod.compress_line("EU", frame, profile(), "EU")["checks"]["非皮卡"]
    assert set(check["检查结果"]) == {"OK"}


def test_atom_check_matches_combined_model_names():
    # A0 的 MODEL 可能本身是组合名（Audi A3/S3），原子检查不能因此误报 MISS，销量也要归到该行
    frame = pd.DataFrame([row(make="Audi", model="A3/S3", year="2015-2016", size="3M", sales=40)], columns=FIELDS).astype(str)
    result = run_mod.compress_line("US", frame, profile(), "US")
    assert set(result["checks"]["非皮卡"]["检查结果"]) == {"OK"}
    assert result["tables"]["non_pickup_high"]["尺码销量总和"].tolist() == [40]


def test_merge_still_refuses_to_claim_a_different_size():
    # Civic：Type R 2017-2026 与基础款 2022-2026 同为 2XXL，但基础款 2017-2021 是 2XL，不得合并
    tables = compress([
        row(model="Civic", structure="Hatchback", year="2017-2021", size="2XL"),
        row(model="Civic", structure="Hatchback", year="2022-2026", size="2XXL"),
        row(model="Civic", structure="Hatchback", version="Type R", year="2017-2026", size="2XXL"),
    ])
    assert len(tables["non_pickup_high"]) == 3


def test_merge_does_not_bridge_long_gaps_without_atoms():
    # Prelude：2002–2025 无原子（停产 24 年），超过 最大空档年数 不桥接
    tables = compress([
        row(model="Prelude", structure="Coupe", year="1983-2001", size="3M-0"),
        row(model="Prelude", structure="Coupe", year="2026", size="3M-0"),
    ])
    assert years_of(tables["non_pickup_high"]) == ["1983-2001", "2026"]


def test_merge_bridges_short_gaps_and_exempt_sizes():
    assert run_mod.load_merge_rules().max_gap_years == 3
    tables = compress([
        row(model="Focus", year="2010-2012", size="M"),
        row(model="Focus", year="2016-2018", size="M"),  # 空档 2013–2015 共 3 年
        row(model="Century", structure="Wagon", year="1958", size="无可用尺码"),
        row(model="Century", structure="Wagon", year="1973-1977", size="无可用尺码"),
    ])
    assert years_of(tables["non_pickup_high"]) == ["1958-1977", "2010-2018"]


def test_pickup_merge_does_not_bridge_long_gaps():
    pickup = dict(structure="", cab="Crew", bed="5.5", category="皮卡", size="PK-M")
    tables = compress([
        row(model="Ranger", year="1990-1995", **pickup),
        row(model="Ranger", year="2000-2002", **pickup),  # 空档 4 年
        row(model="Tacoma", year="2010-2012", **pickup),
        row(model="Tacoma", year="2014-2016", **pickup),
    ])
    assert sorted(zip(tables["pickup_high"]["MODEL"], tables["pickup_high"]["YEAR"])) == [
        ("Ranger", "1990-1995"), ("Ranger", "2000-2002"), ("Tacoma", "2010-2016"),
    ]


def test_record_sales_sum_the_rows_it_compresses():
    tables = compress([
        row(year="2018-2019", size="M", sales=100),
        row(year="2020-2021", size="M", sales=50),
        row(model="Fusion", year="2018", size="L", sales=7),
    ])
    high = tables["non_pickup_high"].set_index("MODEL")
    assert high.loc["Focus", "尺码销量总和"] == 150
    assert high.loc["Fusion", "尺码销量总和"] == 7


def test_row_sales_split_across_records_by_year_share():
    # 同一行的年份被拆到不同尺码的记录中时，行销量按原子（年份）均摊，总量守恒
    tables = compress([
        row(version="Base", year="2018-2021", size="M", sales=80),
        row(version="Sport", year="2018-2019", size="M", sales=0),
        row(version="Sport", year="2020-2021", size="L", sales=0),
    ])
    high = tables["non_pickup_high"]
    assert high["尺码销量总和"].sum() == 80


def test_pickup_sales_follow_cab_atoms():
    tables = compress([
        row(model="F-150", structure="", cab="Crew", bed="5.5", category="皮卡", year="2019-2020", size="PK-M", sales=30),
    ])
    assert tables["pickup_high"]["尺码销量总和"].tolist() == [30]


def test_ru_format_renames_size_and_fills_ozon_and_shipping_sizes():
    size_format = run_mod.load_size_formats(PROJECT_DIR / "data")["RU"]
    assert size_format == {"尺码列名": "亚马逊尺码", "附加尺码列": ["OZON尺码", "发货尺码"]}
    rows = [
        {**row(model="Vesta", size="3M", region="RU"), "OZON尺码": "3M", "发货尺码": "L"},
        {**row(model="Niva", structure="SUV", size="YS-410", region="RU"), "OZON尺码": "S", "发货尺码": "YM"},
    ]
    frame = pd.DataFrame(rows).astype(str)
    tables = run_mod.compress_line("RU", frame, profile(), "RU", size_format=size_format)["tables"]
    high = tables["non_pickup_high"]
    assert list(high.columns[-4:]) == ["亚马逊尺码", "OZON尺码", "发货尺码", "尺码销量总和"]
    assert "BACKSIZE" not in high.columns
    assert set(zip(high["亚马逊尺码"], high["OZON尺码"], high["发货尺码"])) == {("3M", "3M", "L"), ("YS-410", "S", "YM")}


def test_ru_format_rejects_ambiguous_extra_sizes():
    rows = [
        {**row(model="Vesta", year="2018", size="3M", region="RU"), "OZON尺码": "3M", "发货尺码": "L"},
        {**row(model="Vesta", year="2019", size="3M", region="RU"), "OZON尺码": "3L", "发货尺码": "L"},
    ]
    frame = pd.DataFrame(rows).astype(str)
    with pytest.raises(run_mod.CompressionError):
        run_mod.compress_line("RU", frame, profile(), "RU", size_format=run_mod.load_size_formats(PROJECT_DIR / "data")["RU"])


def test_pickups_are_split_into_pickup_tables():
    tables = compress([
        row(),
        row(make="Ford", model="F-150", structure="", cab="Crew", bed="5.5", category="皮卡", year="2019-2020", size="PK-M"),
    ])
    assert len(tables["pickup_lossless"]) == 1
    assert tables["pickup_lossless"].iloc[0]["CAB"] == "Crew"
    assert "F-150" not in set(tables["non_pickup_lossless"]["MODEL"])


def test_wrong_region_rows_fail():
    with pytest.raises(run_mod.CompressionError):
        compress([row(region="EU")], region="US")


def test_model_combo_comes_from_node_data():
    assert run_mod.engine.DEFAULT_MODEL_COMBO_PATH == PROJECT_DIR / "data" / run_mod.MODEL_COMBO


def write_sources(source_dir: Path, rows_by_line: dict[str, list[dict]]) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    configured = lines()
    for line, rows in rows_by_line.items():
        path = source_dir / run_mod.upstream_file(line, configured[line])
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            # A0 RU 全量表带 OZON尺码/发货尺码，其余产线没有
            fieldnames = [*FIELDS, "OZON尺码", "发货尺码"] if configured[line] == "RU" else FIELDS
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def lines() -> dict[str, str]:
    return run_mod.load_lines(PROJECT_DIR / "data")


def test_lines_cover_regions_and_us_stores():
    assert lines() == {"US": "US", "HNT": "US", "TM": "US", "TM_拆分": "US", "EU": "EU", "RU": "RU"}


def test_default_lines_include_country_and_us_store_outputs():
    assert run_mod.default_lines(lines()) == lines()


def test_output_names_are_grouped_by_line_without_lossy_suffix():
    assert run_mod.output_names("HNT") == {
        "non_pickup_high": "HNT/压缩尺码表.csv",
        "pickup_high": "HNT/压缩尺码表_皮卡.csv",
    }


def test_run_writes_artifact_and_outputs(tmp_path: Path):
    countries = run_mod.default_lines(lines())
    write_sources(tmp_path / "src", {line: [row(region=region)] for line, region in countries.items()})
    result = run_mod.run(tmp_path / "src", PROJECT_DIR / "data", tmp_path / "output", tmp_path / "artifacts", workers=1)
    expected = sorted(name for line in countries for name in run_mod.output_names(line).values())
    assert sorted(path.relative_to(tmp_path / "output").as_posix() for path in (tmp_path / "output").rglob("*.csv")) == expected
    artifact = Path(result["artifact"])
    status = json.loads((artifact / "status.json").read_text(encoding="utf-8"))
    assert status["status"] == "passed"
    assert (artifact / "input" / run_mod.FIELD_PROFILE).is_file()
    assert (artifact / "input" / run_mod.MODEL_COMBO).is_file()
    assert set(status["lines"]) == set(countries)


def test_failed_run_leaves_output_untouched(tmp_path: Path):
    output = tmp_path / "output"
    output.mkdir()
    (output / "keep.csv").write_text("x", encoding="utf-8")
    sources = {line: [row(region=region)] for line, region in run_mod.default_lines(lines()).items()}
    sources["EU"] = [row(region="US")]  # EU 产线混入 US 行
    write_sources(tmp_path / "src", sources)
    with pytest.raises(run_mod.CompressionError):
        run_mod.run(tmp_path / "src", PROJECT_DIR / "data", output, tmp_path / "artifacts", workers=1)
    assert [path.name for path in output.iterdir()] == ["keep.csv"]


def test_parallel_run_matches_serial(tmp_path: Path):
    write_sources(tmp_path / "src", {line: [row(region=region), row(year="2020", size="L", region=region)] for line, region in run_mod.default_lines(lines()).items()})
    run_mod.run(tmp_path / "src", PROJECT_DIR / "data", tmp_path / "serial", tmp_path / "a1", workers=1)
    run_mod.run(tmp_path / "src", PROJECT_DIR / "data", tmp_path / "parallel", tmp_path / "a2", workers=2)
    for path in (tmp_path / "serial").rglob("*.csv"):
        assert path.read_bytes() == (tmp_path / "parallel" / path.relative_to(tmp_path / "serial")).read_bytes()


def test_ssh_publish_plan_uses_us_manifest_outputs():
    plan = publish_ssh.load_plan(PROJECT_DIR / "data" / "ssh发布.yaml")
    assert plan.host == "qnap-nas"
    assert plan.destination.as_posix() == "/share/Public/PQData/pub_all_cars_data/size_compressed"
    assert [name for _, name, _ in plan.files] == ["压缩尺码表.csv", "压缩尺码表_皮卡.csv"]
    assert all(path.parent == PROJECT_DIR / "output" / "US" for path, _, _ in plan.files)


def test_upstream_files_follow_a0_layout():
    assert run_mod.upstream_file("EU") == "EU/全量/全量表.csv"
    assert run_mod.upstream_file("TM_拆分", "US") == "US/店铺/店铺全量_TM_拆分.csv"


def write_code_mapping(path: Path, rows: list[tuple[str, str, str, str, str]]) -> Path:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["REGION", "MAKE", "MODEL", "MAKE_CODE", "MODEL_CODE"])
        writer.writerows(rows)
    return path


def test_year_code_matches_dimension_code_rule():
    assert run_mod.year_code("1964-1974") == "6474"
    assert run_mod.year_code("1968") == "6868"
    with pytest.raises(run_mod.CompressionError):
        run_mod.year_code("2020-2021,2023")


def test_code_regions_are_us_only():
    assert run_mod.load_code_regions(PROJECT_DIR / "data") == {"US"}


def test_apply_codes_inserts_first_column_with_case_insensitive_names(tmp_path: Path):
    mapping = run_mod.load_code_mapping(write_code_mapping(tmp_path / "map.csv", [("US", "ford", "FOCUS", "07", "12"), ("US", "Ford", "F-150", "07", "00")]))
    tables = compress([row(), row(year="2020", size="L"), row(model="F-150", structure="", cab="Crew", bed="5.5", category="皮卡", year="2015-2020")])
    run_mod.apply_codes(tables, mapping, "US", "US")
    assert list(tables["non_pickup_high"].columns[:2]) == ["CODE", "CAR"]
    assert dict(zip(tables["non_pickup_high"]["YEAR"], tables["non_pickup_high"]["CODE"])) == {"2018-2019": "07121819", "2020": "07122020"}
    assert tables["pickup_high"]["CODE"].tolist() == ["07001520"]


def test_apply_codes_fails_for_unmapped_model(tmp_path: Path):
    mapping = run_mod.load_code_mapping(write_code_mapping(tmp_path / "map.csv", [("US", "Ford", "Fiesta", "07", "13")]))
    with pytest.raises(run_mod.CompressionError, match="Ford Focus"):
        run_mod.apply_codes(compress([row()]), mapping, "US", "US")


def test_run_adds_codes_only_to_code_regions(tmp_path: Path):
    countries = run_mod.default_lines(lines())
    write_sources(tmp_path / "src", {line: [row(region=region)] for line, region in countries.items()})
    code_map = write_code_mapping(tmp_path / "map.csv", [("US", "Ford", "Focus", "07", "12")])
    result = run_mod.run(tmp_path / "src", PROJECT_DIR / "data", tmp_path / "output", tmp_path / "artifacts", workers=1, code_mapping=code_map)
    for line, region in countries.items():
        table = pd.read_csv(tmp_path / "output" / line / "压缩尺码表.csv", dtype=str, encoding="utf-8-sig")
        if region == "US":
            assert table.columns[0] == "CODE" and table["CODE"].tolist() == ["07121819"]
        else:
            assert "CODE" not in table.columns
    assert (Path(result["artifact"]) / "input" / "map.csv").is_file()
