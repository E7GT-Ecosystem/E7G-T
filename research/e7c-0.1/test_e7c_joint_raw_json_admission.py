"""Focused raw-shape, key-set and Fraction checks for pinned EEC-Q admission."""

from __future__ import annotations

import copy
import unittest
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint
from e7c_eecq_joint_restrict_b1 import (
    JointRestrictionAdmission,
    admit,
    document,
)


def one_row_document(coefficient=Fraction(1, 3)):
    left = Config(("AB",), None)
    right = Config(("BC",), "")
    joint = Joint(2, (((left, right), coefficient),))
    return document(joint)


class RawJointJsonAdmission(unittest.TestCase):
    def assert_invalid(self, value):
        with self.assertRaises(JointRestrictionAdmission):
            admit(value)

    def test_canonical_raw_document_preserves_null_empty_and_reduced_fraction(self):
        raw = one_row_document(Fraction(-2, 3))
        value = admit(raw)
        self.assertEqual(value.terms[0][0][0].tag, None)
        self.assertEqual(value.terms[0][0][1].tag, "")
        self.assertEqual(value.terms[0][1], Fraction(-2, 3))
        self.assertEqual(raw["rows"][0]["coefficient"],
                         {"numerator": -2, "denominator": 3})

    def test_exact_top_level_and_nested_key_sets(self):
        raw = one_row_document()
        extra = copy.deepcopy(raw)
        extra["unexpected"] = 1
        self.assert_invalid(extra)
        missing = copy.deepcopy(raw)
        del missing["interpretation"]
        self.assert_invalid(missing)
        bad_row = copy.deepcopy(raw)
        bad_row["rows"][0]["extra"] = 1
        self.assert_invalid(bad_row)
        bad_graph = copy.deepcopy(raw)
        bad_graph["rows"][0]["atoms"][0]["extra"] = 1
        self.assert_invalid(bad_graph)
        bad_fraction = copy.deepcopy(raw)
        bad_fraction["rows"][0]["coefficient"]["extra"] = 1
        self.assert_invalid(bad_fraction)

    def test_raw_fraction_requires_exact_integers_positive_denominator_and_nonzero(self):
        for numerator, denominator in ((True, 2), (1, True), (1, 0), (1, -2), (0, 3)):
            with self.subTest(numerator=numerator, denominator=denominator):
                raw = one_row_document()
                raw["rows"][0]["coefficient"] = {
                    "numerator": numerator, "denominator": denominator}
                self.assert_invalid(raw)

    def test_fraction_pair_must_match_fraction_reduction(self):
        raw = one_row_document(Fraction(1, 2))
        raw["rows"][0]["coefficient"] = {"numerator": 2, "denominator": 4}
        self.assert_invalid(raw)

    def test_graph_edges_must_already_be_canonical(self):
        raw = one_row_document()
        raw["rows"][0]["atoms"][0]["edges"] = ["AC", "AB"]
        self.assert_invalid(raw)
        raw = one_row_document()
        raw["rows"][0]["atoms"][0]["edges"] = ["AB", "AB"]
        self.assert_invalid(raw)

    def test_joint_guard_rejects_duplicate_reordered_and_cancelled_rows(self):
        raw = one_row_document()
        raw["rows"] = raw["rows"] * 2
        self.assert_invalid(raw)

        p = Config(("AB",), None)
        q = Config(("BC",), "")
        terms = (
            (((p, q), Fraction(1, 3))),
            (((q, p), Fraction(2, 5))),
        )
        ordered = document(Joint(2, terms))
        ordered["rows"].reverse()
        self.assert_invalid(ordered)

        raw = one_row_document()
        raw["rows"] = [
            {"atoms": raw["rows"][0]["atoms"],
             "coefficient": {"numerator": 1, "denominator": 3}},
            {"atoms": raw["rows"][0]["atoms"],
             "coefficient": {"numerator": -1, "denominator": 3}},
        ]
        self.assert_invalid(raw)

    def test_row_cap_is_admission_failure_not_evaluation_resource_outcome(self):
        terms = tuple(
            ((Config(("AB",), f"tag-{index:02d}"),
              Config(("BC",), None)), Fraction(1, index + 1))
            for index in range(65)
        )
        raw = document(Joint(2, terms))
        self.assert_invalid(raw)

    def test_policy_key_sets_and_exact_integer_bounds(self):
        raw = one_row_document()
        raw["resource_policy"]["extra"] = 1
        self.assert_invalid(raw)
        raw = one_row_document()
        raw["resource_policy"]["step_bound"] = True
        self.assert_invalid(raw)
        raw = one_row_document()
        raw["resource_policy"]["ledger_bound"] = -1
        self.assert_invalid(raw)
        raw = one_row_document()
        raw["interpretation"]["capability"] = 1
        self.assert_invalid(raw)
        raw = one_row_document()
        raw["interpretation"]["obligation"] = "unknown"
        self.assert_invalid(raw)


if __name__ == "__main__":
    unittest.main()
