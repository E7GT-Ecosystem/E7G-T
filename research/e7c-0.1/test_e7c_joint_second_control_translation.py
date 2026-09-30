"""Differential boundary for the separately checked second-stage schedule."""

from dataclasses import replace
from fractions import Fraction
import unittest

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_eecq_joint_restrict_b1 import evaluate as evaluate_first
from e7c_eecq_two_stage_b1 import document, evaluate
from e7_ir_eecq_two_stage_b1 import execute, lower, serialize
from e7c_joint_second_control_translation import extract, run


SUPPORT = [
    (Fraction(-2, 3), (Config(("AB",), None), Config(("BC",), ""))),
    (Fraction(1, 7), (Config(("AC",), None), Config(("BC",), "α"))),
    (Fraction(3, 5), (Config(("BC",), "third"), Config(("AB",), None))),
]


class ExtractedSecondStage(unittest.TestCase):
    def test_selected_first_and_second_stage_boundary_matrix(self):
        source_program = extract("e7c_eecq_two_stage_b1.py")
        ir_program = extract("e7_ir_eecq_two_stage_b1.py")
        self.assertEqual(source_program.instructions, ir_program.instructions)
        for size in range(4):
            value = joint(SUPPORT[:size], arity=2)
            for first_capability, second_capability, obligation in (
                    (False, True, "resolved"), (True, False, "resolved"),
                    (True, True, "unresolved"), (True, True, "resolved")):
                for steps in range(size * 2 + 4):
                    for capacity in range(size * 2 + 4):
                        with self.subTest(size=size, first=first_capability,
                                          second=second_capability, obligation=obligation,
                                          steps=steps, capacity=capacity):
                            doc = document(value, step_bound=steps, ledger_bound=capacity,
                                           first_capability=first_capability,
                                           second_capability=second_capability,
                                           second_obligation=obligation)
                            child_trace = []
                            child = evaluate_first(doc["first"],
                                                   _transition_sink=child_trace.append)
                            model_trace = []
                            args = (child, steps, capacity, second_capability, obligation)
                            expected, started = run(source_program, *args,
                                                    transitions=model_trace)
                            self.assertEqual(run(ir_program, *args)[0], expected)
                            source_trace, ir_trace = [], []
                            actual = evaluate(doc, _transition_sink=source_trace.append)
                            package = lower(doc)
                            self.assertLessEqual(len(serialize(package)), 1_000_000)
                            independent = execute(package, _transition_sink=ir_trace.append)
                            self.assertEqual({k: actual[k] for k in expected}, expected)
                            self.assertEqual(independent, expected)
                            self.assertEqual(actual["witness"]["second_started"], started)
                            self.assertEqual(package["source_witness"]["second_started"], started)
                            self.assertEqual(source_trace, child_trace + model_trace)
                            self.assertEqual(ir_trace, child_trace + model_trace)

    def test_charged_failed_second_attempt_has_no_append(self):
        program = extract("e7_ir_eecq_two_stage_b1.py")
        value = joint([(Fraction(-2, 3),
                        (Config(("AC",), None), Config(("BC",), "")))], arity=2)
        doc = document(value, step_bound=4, ledger_bound=2)
        child = evaluate_first(doc["first"])
        transitions = []
        result, started = run(program, child, 4, 2, True, "resolved",
                              transitions=transitions)
        self.assertTrue(started)
        self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
        self.assertEqual(result["resource_progress"]["completed_steps"], 3)
        self.assertEqual(len(result["ordered_ledger"]), 2)
        self.assertEqual([event["action"] for event in transitions],
                         ["charge", "terminal"])
        self.assertTrue(transitions[0]["second_started"])

    def test_rejects_unreviewed_schedule_and_domain(self):
        program = extract("e7c_eecq_two_stage_b1.py")
        with self.assertRaises(ValueError):
            run(replace(program, instructions=program.instructions[:-1]), {}, 1, 1,
                True, "resolved")
        with self.assertRaises(ValueError):
            run(program, {}, True, 1, True, "resolved")


if __name__ == "__main__":
    unittest.main()
