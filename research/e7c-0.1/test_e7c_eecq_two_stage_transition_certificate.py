"""Actual charge/append probes on both selected Python implementation paths."""

import copy
from fractions import Fraction
import itertools
import unittest

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_eecq_two_stage_b1 import document, evaluate
from e7_ir_eecq_two_stage_b1 import execute, lower
from e7c_eecq_two_stage_transition_certificate import (
    TransitionAdmission, certify_both, check,
)


def correlated():
    left = Config(("AC",), None)
    right = Config(("BC",), "")
    return joint([(Fraction(-2, 3), (left, right)),
                  (Fraction(3, 5), (right, left))], arity=2)


class ActualTransitionCertificate(unittest.TestCase):
    def test_replayable_instance_binds_both_paths(self):
        for value in (joint([], arity=2), correlated()):
            for step_bound, ledger_bound in ((0, 0), (4, 2), (8, 8)):
                source = document(value, step_bound=step_bound,
                                  ledger_bound=ledger_bound)
                with self.subTest(size=len(value.terms), step=step_bound,
                                  ledger=ledger_bound):
                    record = certify_both(source)
                    self.assertEqual(record["source"], source)
                    self.assertEqual(record["source_transcript"],
                                     record["ir_transcript"])
                    self.assertEqual(record["source_result"]["witness"]["claim"],
                                     record["ir_result"])

    def test_both_paths_emit_every_charge_and_append(self):
        for support, steps, ledger, first_cap, second_obl in itertools.product(
                (joint([], arity=2), correlated()), range(6), range(6),
                (False, True), ("resolved", "unresolved")):
            source = document(support, step_bound=steps, ledger_bound=ledger,
                              first_capability=first_cap, second_obligation=second_obl)
            with self.subTest(rows=len(support.terms), steps=steps,
                              ledger=ledger, first_cap=first_cap, second=second_obl):
                source_trace, ir_trace = [], []
                observed_source = evaluate(source, _transition_sink=source_trace.append)
                observed_ir = execute(lower(source), _transition_sink=ir_trace.append)
                self.assertEqual(source_trace, ir_trace)
                self.assertEqual(check(source, observed_source, source_trace),
                                 check(source, observed_ir, ir_trace))
                self.assertEqual(evaluate(source), observed_source)

    def test_second_attempt_failed_append_and_adversarial_transcripts(self):
        source = document(joint([(Fraction(-2, 3),
                                  (Config(("AC",), None), Config(("BC",), "")))],
                                arity=2), step_bound=4, ledger_bound=2)
        trace = []
        observed = evaluate(source, _transition_sink=trace.append)
        self.assertEqual(check(source, observed, trace)["completedSteps"], 3)
        self.assertEqual([(t["action"], t["stage"], t["ledger_entries"])
                          for t in trace], [("charge", "first", 0),
                                           ("append", "first", 1),
                                           ("charge", "first", 1),
                                           ("append", "first", 2),
                                           ("charge", "second", 2),
                                           ("terminal", "second", 2)])
        self.assertTrue(trace[-2]["second_started"])
        omissions = (trace[:-1], trace[:3] + trace[4:],
                     trace[:4] + trace[5:], trace + [trace[-1]], trace[1:])
        for corrupted in omissions:
            with self.assertRaises(TransitionAdmission):
                check(source, observed, corrupted)
        wrong_started = copy.deepcopy(trace)
        wrong_started[-2]["second_started"] = False
        with self.assertRaises(TransitionAdmission):
            check(source, observed, wrong_started)
        missing_started = copy.deepcopy(trace)
        del missing_started[-2]["second_started"]
        with self.assertRaises(TransitionAdmission):
            check(source, observed, missing_started)
        forged_terminal = copy.deepcopy(trace)
        forged_terminal[-1]["terminal_outcome"] = {"tag": "success"}
        with self.assertRaises(TransitionAdmission):
            check(source, observed, forged_terminal)
        ghost_row = copy.deepcopy(trace)
        ghost_row[2]["row_index"] = 99
        with self.assertRaises(TransitionAdmission):
            check(source, observed, ghost_row)

    def test_forged_completion_at_first_stage_resource_stop(self):
        # The old transcript-only checker could accept this self-consistent
        # lie: the first stage ran out of fuel after one row, yet the result
        # claims the whole first exclusion portion was completed.
        value = joint([(Fraction(1, 3), (Config(("AB",), None),
                                         Config(("AC",), None))),
                       (Fraction(2, 5), (Config(("AC",), None),
                                         Config(("BC",), "")))], arity=2)
        source = document(value, step_bound=2, ledger_bound=5)
        trace = []
        observed = evaluate(source, _transition_sink=trace.append)
        self.assertIsNone(observed["resource_progress"]["first_excluded"])
        forged = copy.deepcopy(observed)
        excluded = [row for row in source["first"]["rows"]
                    if "AB" in row["atoms"][0]["edges"]]
        forged["resource_progress"]["first_excluded"] = excluded
        forged["terminal_outcome"]["progress"]["first_excluded"] = excluded
        forged_trace = copy.deepcopy(trace)
        forged_trace[-1]["stage"] = "second"
        forged_trace[-1]["progress"] = copy.deepcopy(forged["resource_progress"])
        with self.assertRaisesRegex(TransitionAdmission, "does not refine staged rule"):
            check(source, forged, forged_trace)

    def test_forged_second_started_without_second_attempt(self):
        source = document(correlated(), step_bound=0, ledger_bound=8)
        trace = []
        observed = evaluate(source, _transition_sink=trace.append)
        forged = copy.deepcopy(observed)
        forged["witness"]["second_started"] = True
        with self.assertRaisesRegex(TransitionAdmission, "does not refine staged rule"):
            check(source, forged, trace)


if __name__ == "__main__":
    unittest.main()
