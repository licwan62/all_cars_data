"""Replace an audited group of US pickup rows and trace retired identities."""

from collections import defaultdict
from decimal import Decimal

from id_scheme import append_country_code, dimension_id
from us_model_splits import MIGRATION_FIELDS


def years(span):
    start, _, end = span.partition("-")
    first, last = int(start), int(end or start)
    if not 1900 <= first <= last <= 2100:
        raise ValueError(f"无效车型年份：{span}")
    return set(range(first, last + 1))


def apply_pickup_replacements(rows, plan):
    by_id = {row["DIMENSION-ID"]: row for row in rows}
    migrations = []
    for rule in plan["replacements"]:
        old_rows = []
        for identity, expected in rule["expected"].items():
            row = by_id.get(identity)
            if not row or any(row.get(field) != value for field, value in expected.items()):
                raise ValueError(f"皮卡替换前置条件不匹配：{identity}")
            old_rows.append(row)
        scope = rule["scope"]
        scoped_ids = {
            identity for identity, row in by_id.items()
            if all(row.get(field) == value for field, value in scope.items())
        }
        if scoped_ids != rule["expected"].keys():
            raise ValueError("皮卡替换范围与已审身份不一致")
        retained = {tuple(pair) for pair in rule["verified_configurations"]}
        expected_years = years(rule["year"])
        covered = defaultdict(set)
        new_rows = defaultdict(list)
        source_years = {}
        for source in rule["sources"]:
            if not source["url"].startswith("https://") or not source["note"]:
                raise ValueError("皮卡替换缺少来源")
            source_years[source["id"]] = years(source["year"])
        for segment in rule["segments"]:
            cab, bed = segment["cab"], segment["bed"]
            key = (cab, bed)
            segment_years = years(segment["year"])
            refs = segment["sources"]
            if key not in retained or covered[key] & segment_years or not segment_years <= expected_years:
                raise ValueError(f"皮卡配置或车型年份重叠：{segment}")
            if not refs or not segment_years <= set().union(*(source_years[ref] for ref in refs)):
                raise ValueError(f"皮卡车型年份缺少对应来源：{segment}")
            dimensions = [Decimal(value) for value in segment["dimensions"]]
            if len(dimensions) != 3 or any(not value.is_finite() or value <= 0 for value in dimensions):
                raise ValueError(f"皮卡替换尺寸无效：{segment}")
            covered[key].update(segment_years)
            cab_label = "Regular Cab" if cab == "Regular" else cab
            row = {
                **old_rows[0], **scope, "CAB": cab, "BED": bed, "YEAR": segment["year"],
                **dict(zip(("L-IN", "W-IN", "H-IN"), segment["dimensions"])),
                "参考车型": f"{segment['year']} {scope['MAKE']} {scope['MODEL']} {cab_label} {bed} ft (4x2)",
                "备注": f"{segment['note']}；依据 {'、'.join(refs)}",
            }
            row["DIMENSION-ID"] = append_country_code(dimension_id(row), "US")
            if row["DIMENSION-ID"] in by_id:
                raise ValueError(f"皮卡替换身份重复：{row['DIMENSION-ID']}")
            new_rows[key].append((row, refs))
        if any(covered[key] != expected_years for key in retained):
            raise ValueError("皮卡替换缺少车型年份")
        for old in old_rows:
            del by_id[old["DIMENSION-ID"]]
            targets = new_rows[(old["CAB"], old["BED"])]
            if not targets:
                migrations.append(dict(zip(MIGRATION_FIELDS, [
                    old["DIMENSION-ID"], "", scope["MODEL"], old["YEAR"], rule["retirement_reason"],
                    "|".join(source_years),
                ])))
            for target, refs in targets:
                migrations.append(dict(zip(MIGRATION_FIELDS, [
                    old["DIMENSION-ID"], target["DIMENSION-ID"], scope["MODEL"], target["YEAR"],
                    rule["reason"], "|".join(refs),
                ])))
        by_id.update((row["DIMENSION-ID"], row) for group in new_rows.values() for row, _ in group)
    return list(by_id.values()), migrations
