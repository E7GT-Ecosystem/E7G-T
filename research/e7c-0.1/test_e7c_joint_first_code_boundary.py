"""Actual first-stage source/IR paths and an IR-domain counterexample."""

from fractions import Fraction
import unittest

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_eecq_joint_restrict_b1 import document, evaluate
from e7_ir_eecq_joint_restrict_b1 import JointRestrictionIRAdmission, execute, lower
from e7c_eecq_two_stage_b1 import admit as admit_two, document as document_two, evaluate as evaluate_two
from e7_ir_eecq_two_stage_b1 import lower as lower_two


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


if __name__ == "__main__":
    unittest.main()
