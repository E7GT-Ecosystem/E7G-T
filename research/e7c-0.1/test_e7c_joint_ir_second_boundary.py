"""IR second-attempt boundary and separately bounded package replays."""

from fractions import Fraction
import unittest
from unittest.mock import patch

import e7_ir_eecq_two_stage_b1 as outer
import e7_ir_eecq_joint_restrict_b1 as child
from e7c_eecq_two_stage_b1 import document, evaluate
from e7c_joint_ir_second_boundary import check_sites, require_order
from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint


def one_row():
    return joint([(Fraction(-2, 3), (Config((), ""), Config(("BC",), None)))], arity=2)


class IRSecondBoundary(unittest.TestCase):
    def test_pinned_sites(self):
        self.assertEqual(check_sites()["nested_byte_limit"], 1_000_000)
        self.assertEqual(check_sites()["outer_byte_limit"], 1_000_000)
        with self.assertRaises(ValueError):
            require_order("steps += 1; emit('charge'); second_started = True",
                          ("steps += 1", "second_started = True", "emit('charge')"))
        with self.assertRaises(ValueError):
            require_order("second_started = True; emit('charge'); emit('append')",
                          ("second_started = True", "if len(ledger) >= beta['ledger_bound']:",
                           "emit('append')"))

    def test_charged_failed_second_append(self):
        doc = document(one_row(), step_bound=4, ledger_bound=2)
        source_trace, ir_trace = [], []
        src = evaluate(doc, _transition_sink=source_trace.append)
        package = outer.lower(doc)
        ir = outer.execute(package, _transition_sink=ir_trace.append)
        self.assertEqual(src["witness"]["claim"], ir)
        self.assertEqual(source_trace, ir_trace)
        self.assertEqual(ir["terminal_outcome"]["tag"], "resource_limit")
        self.assertEqual(ir["resource_progress"]["completed_steps"], 3)
        self.assertEqual(len(ir["ordered_ledger"]), 2)
        self.assertTrue(src["witness"]["second_started"])
        self.assertEqual(ir_trace[-2]["action"], "charge")
        self.assertTrue(ir_trace[-2]["second_started"])
        self.assertEqual(ir_trace[-2]["ledger_entries"], 2)
        self.assertEqual(ir_trace[-1]["action"], "terminal")
        self.assertNotIn("value", ir["terminal_outcome"])
        self.assertEqual(ir["resource_progress"]["first_excluded"], [])
        self.assertEqual(ir["resource_progress"]["second_excluded_prefix"], [])
        self.assertLessEqual(len(child.serialize(package["first_ir"])), 1_000_000)
        self.assertLessEqual(len(outer.serialize(package)), 1_000_000)

    def test_independent_package_size_guards(self):
        # Already admitted source and a successfully serialized child do not
        # imply the outer package fits. Check both actual serialization calls.
        doc = document(one_row(), step_bound=0)
        package = outer.lower(doc)
        child_length = len(child.serialize(package["first_ir"]))
        outer_length = len(outer.serialize(package))
        self.assertLess(child_length, outer_length)
        self.assertLessEqual(child_length, 1_000_000)
        self.assertLessEqual(outer_length, 1_000_000)
        with patch.object(child, "MAX_BYTES", child_length):
            self.assertEqual(len(child.serialize(package["first_ir"])), child_length)
        with patch.object(child, "MAX_BYTES", child_length - 1):
            with self.assertRaises(child.JointRestrictionIRAdmission):
                child.serialize(package["first_ir"])
        with patch.object(outer, "MAX_BYTES", outer_length):
            self.assertEqual(len(outer.serialize(package)), outer_length)
        with patch.object(outer, "MAX_BYTES", outer_length - 1):
            with self.assertRaises(outer.TwoStageIRAdmission):
                outer.serialize(package)


if __name__ == "__main__":
    unittest.main()
