from __future__ import annotations

import unittest

from src.trimlist import (
    LogicalKey,
    Resolver,
    apply_overrides,
    build_trimlist,
    expanded_years,
)


def dimension(
    dimension_id: str = "D1",
    year: str = "2020-2021",
    structure: str = "SUV",
) -> dict[str, str]:
    return {
        "DIMENSION-ID": dimension_id,
        "MAKE": "Acura",
        "MODEL": "ADX",
        "版本": "",
        "结构": structure,
        "YEAR": year,
        "CAB": "",
        "BED": "",
    }


def fitment(year: int, model: str = "ADX") -> dict[str, str]:
    return {"year": str(year), "make": "Acura", "model": model}


def maintenance(
    year: int,
    candidate: str,
    structure: str = "SUV",
) -> dict[str, str]:
    return {
        "Year": str(year),
        "主车型": "Acura ADX",
        "结构": structure,
        "版本": "",
        "候选车型": candidate,
    }


class TrimListTests(unittest.TestCase):
    def test_expand_year_range(self) -> None:
        self.assertEqual(expanded_years("2020-2022"), [2020, 2021, 2022])
        self.assertEqual(expanded_years("2025"), [2025])

    def test_preserves_year_specific_candidates(self) -> None:
        result = build_trimlist(
            [dimension()],
            [fitment(2020, "ADX"), fitment(2021, "ADX Type S")],
            [
                maintenance(2020, "Acura|ADX"),
                maintenance(2021, "Acura|ADX Type S"),
            ],
        )
        actual = [(row["Year"], row["Model"]) for row in result.trim_rows]
        self.assertEqual(actual, [(2020, "ADX"), (2021, "ADX Type S")])

    def test_structure_alias_requires_online_evidence(self) -> None:
        row = dimension(year="2020", structure="Convertible")
        result = build_trimlist(
            [row],
            [fitment(2020)],
            [maintenance(2020, "Acura|ADX", structure="Roadster")],
        )
        self.assertEqual(len(result.trim_rows), 0)
        self.assertEqual(len(result.online_review_rows), 1)
        self.assertEqual(result.online_review_rows[0]["审核状态"], "待联网审核")

    def test_structure_alias_is_published_with_matching_online_evidence(self) -> None:
        row = dimension(year="2020", structure="Convertible")
        evidence = {
            ("D1", 2020, "Acura", "ADX"): {
                "DIMENSION-ID": "D1",
                "Year": "2020",
                "Make": "Acura",
                "Model": "ADX",
                "版本": "",
                "结构": "Convertible",
                "Decision": "APPROVE",
                "SourceURL": "https://example.com/evidence",
                "SourceTitle": "Evidence",
                "EvidenceNote": "year/model/body verified",
                "ReviewedAt": "2026-08-27",
            }
        }
        result = build_trimlist(
            [row],
            [fitment(2020)],
            [maintenance(2020, "Acura|ADX", structure="Roadster")],
            online_evidence=evidence,
        )
        self.assertEqual(len(result.trim_rows), 1)
        self.assertEqual(result.audit_rows[0]["审核状态"], "联网证据批准")

    def test_online_evidence_can_add_new_4a_candidate(self) -> None:
        row = dimension(year="2020", structure="SUV")
        evidence = {
            ("D1", 2020, "Acura", "ADX Type S"): {
                "DIMENSION-ID": "D1",
                "Year": "2020",
                "Make": "Acura",
                "Model": "ADX Type S",
                "版本": "",
                "结构": "SUV",
                "Decision": "APPROVE",
                "SourceURL": "https://example.com/evidence",
                "SourceTitle": "Evidence",
                "EvidenceNote": "semantic candidate verified",
                "ReviewedAt": "2026-08-27",
            }
        }
        result = build_trimlist(
            [row],
            [fitment(2020), fitment(2020, "ADX Type S")],
            [maintenance(2020, "Acura|ADX")],
            online_evidence=evidence,
        )
        self.assertEqual(
            {(row["Make"], row["Model"]) for row in result.trim_rows},
            {("Acura", "ADX"), ("Acura", "ADX Type S")},
        )
        added = next(
            row for row in result.audit_rows if row["Model"] == "ADX Type S"
        )
        self.assertEqual(added["匹配方式"], "联网证据新增候选")

    def test_cross_year_candidate_must_exist_in_target_year(self) -> None:
        resolver = Resolver(
            [fitment(2020), fitment(2021)],
            [maintenance(2020, "Acura|ADX")],
        )
        resolution = resolver.resolve(
            LogicalKey(2021, "Acura ADX", "SUV", ""), "Acura", "ADX"
        )
        self.assertEqual(resolution.candidates, (("Acura", "ADX"),))

    def test_override_clear_and_add(self) -> None:
        resolver = Resolver([fitment(2020), fitment(2020, "ADX Type S")], [])
        base = resolver.resolve(
            LogicalKey(2020, "Acura ADX", "SUV", ""), "Acura", "ADX"
        )
        overrides = {
            ("D1", 2020): [
                {
                    "DIMENSION-ID": "D1",
                    "Year": "2020",
                    "Action": "CLEAR",
                    "Make": "",
                    "Model": "",
                    "Note": "",
                },
                {
                    "DIMENSION-ID": "D1",
                    "Year": "2020",
                    "Action": "ADD",
                    "Make": "Acura",
                    "Model": "ADX Type S",
                    "Note": "reviewed",
                },
            ]
        }
        actual = apply_overrides(
            "D1", 2020, base, overrides, resolver.fitment_set
        )
        self.assertEqual(actual.candidates, (("Acura", "ADX Type S"),))

    def test_reports_multi_dimension_fitment_expansion(self) -> None:
        result = build_trimlist(
            [dimension("D1", "2020"), dimension("D2", "2020")],
            [fitment(2020)],
            [maintenance(2020, "Acura|ADX")],
        )
        self.assertEqual(len(result.conflict_rows), 1)
        self.assertEqual(result.conflict_rows[0]["DIMENSION-ID数量"], 2)

    def test_rejects_orphan_override_target(self) -> None:
        result = build_trimlist(
            [dimension("D1", "2020")],
            [fitment(2020)],
            [maintenance(2020, "Acura|ADX")],
            {
                ("MISSING", 2020): [
                    {
                        "DIMENSION-ID": "MISSING",
                        "Year": "2020",
                        "Action": "CLEAR",
                        "Make": "",
                        "Model": "",
                        "Note": "",
                    }
                ]
            },
        )
        self.assertFalse(
            result.report["checks"]["all_overrides_target_existing_dimension_year"]
        )
        self.assertTrue(result.report["hard_errors"])


if __name__ == "__main__":
    unittest.main()
