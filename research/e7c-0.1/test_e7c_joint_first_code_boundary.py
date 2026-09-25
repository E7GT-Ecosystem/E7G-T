"""Actual first-stage source/IR paths and an IR-domain counterexample."""

from fractions import Fraction
import unittest
from unittest.mock import patch

import e7c_eecq_two_stage_b1 as two_stage
import e7_ir_eecq_two_stage_b1 as outer_ir
from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_eecq_joint_restrict_b1 import document, evaluate
from e7_ir_eecq_joint_restrict_b1 import (JointRestrictionIRAdmission, execute,
                                         lower, serialize as serialize_first)
from e7c_eecq_two_stage_b1 import admit as admit_two, document as document_two, evaluate as evaluate_two
from e7_ir_eecq_two_stage_b1 import TwoStageIRAdmission, lower as lower_two


def selected(tag=None):
    return joint([(Fraction(-2, 3), (Config(("AB",), tag), Config(("BC",), None))),
                  (Fraction(1, 4), (Config(("AC",), None), Config((), "")))], arity=2)


class FirstStageActualCode(unittest.TestCase):
    def test_success_policy_and_both_initial_resource_stops(self):
        for steps, ledger, capability, obligation, expected, charged, count in (
            (0, 4, True, "resolved", "resource_limit", 0, 0),
            (4, 0, True, "resolved", "resource_limit", 1, 0),
            (4, 4, False, "resolved", "unsupported", 1, 1),
            (4, 4, True, "unresolved", "undetermined", 1, 1),
            (3, 3, True, "resolved", "success", 3, 3),
            (3, 2, True, "resolved", "resource_limit", 3, 2),
        ):
            with self.subTest(steps=steps, ledger=ledger, capability=capability,
                              obligation=obligation):
                doc = document(selected(), step_bound=steps, ledger_bound=ledger,
                               capability=capability, obligation=obligation)
                observed = evaluate(doc)
                independent = execute(lower(doc))
                for result in (observed, independent):
                    self.assertEqual(result["terminal_outcome"]["tag"], expected)
                    self.assertEqual(result["resource_progress"]["completed_steps"], charged)
                    self.assertEqual(len(result["ordered_ledger"]), count)
                    self.assertEqual(result["resource_progress"]["ledger_prefix"],
                                     result["ordered_ledger"])
                    if expected == "resource_limit":
                        self.assertNotIn("value", result["terminal_outcome"])
                self.assertEqual({k: observed[k] for k in independent}, independent)
                if expected == "success":
                    self.assertEqual(observed["terminal_outcome"]["value"]["excluded"],
                                     doc["rows"][:1])
                    self.assertEqual(observed["terminal_outcome"]["value"]["retained"],
                                     doc["rows"][1:])

    def test_admitted_source_exceeds_ir_package_bound(self):
        # A single long tag is valid source data. The child IR package repeats
        # source and witness material and exceeds its declared byte limit.
        value = joint([(Fraction(1, 2), (Config(("AB",), "X" * 600_000),
                                         Config((), None)))], arity=2)
        doc = document_two(value, step_bound=0)
        self.assertIsNotNone(admit_two(doc))
        self.assertEqual(evaluate_two(doc)["terminal_outcome"]["tag"], "resource_limit")
        with self.assertRaises(JointRestrictionIRAdmission):
            lower_two(doc)

    def test_nested_package_fits_but_outer_exceeds_its_own_bound(self):
        # The outer package repeats the source, child IR and both witnesses.
        value = joint([(Fraction(1, 2), (Config((), "X" * 200_000),
                                         Config((), None)))], arity=2)
        doc = document_two(value, step_bound=0)
        self.assertIsNotNone(admit_two(doc))
        self.assertEqual(evaluate_two(doc)["terminal_outcome"]["tag"], "resource_limit")
        child = lower(doc["first"])
        self.assertLess(len(serialize_first(child)), outer_ir.MAX_BYTES)
        with patch.object(outer_ir, "MAX_BYTES", 2_000_000):
            outer_size = len(outer_ir.serialize(lower_two(doc)))
        self.assertGreater(outer_size, outer_ir.MAX_BYTES)
        with self.assertRaises(TwoStageIRAdmission):
            lower_two(doc)

    def test_second_stage_rejects_child_that_changes_retained_coefficient(self):
        doc = document_two(selected(), step_bound=8)
        real_child = two_stage.evaluate_first

        def corrupted_child(first, **kwargs):
            result = real_child(first, **kwargs)
            result["terminal_outcome"]["value"]["retained"][0]["coefficient"] = {
                "numerator": 9, "denominator": 1}
            return result

        with patch.object(two_stage, "evaluate_first", side_effect=corrupted_child):
            with self.assertRaisesRegex(two_stage.TwoStageAdmission,
                                        "first retained Joint was not preserved"):
                two_stage.evaluate(doc)


if __name__ == "__main__":
    unittest.main()
