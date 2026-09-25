"""Boundary matrix for the extracted first-stage control schedule."""

from fractions import Fraction
import unittest

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_eecq_joint_restrict_b1 import document, evaluate
from e7_ir_eecq_joint_restrict_b1 import execute, lower
from e7c_joint_first_control_translation import extract, run


def sample(size):
    support = [
        (Fraction(-2, 3), (Config(("AB",), ""), Config(("BC",), None))),
        (Fraction(1, 7), (Config(("AC",), None), Config((), "α"))),
        (Fraction(3, 5), (Config(("BC",), "third"), Config(("AB",), None))),
    ]
    return joint(support[:size], arity=2)


class ExtractedFirstStage(unittest.TestCase):
    def test_checked_schedule_and_all_boundary_budgets(self):
        source = extract("e7c_eecq_joint_restrict_b1.py")
        ir = extract("e7_ir_eecq_joint_restrict_b1.py")
        self.assertEqual(source.instructions, ir.instructions)
        for size in range(4):
            for capability, obligation in ((False, "resolved"),
                                           (True, "unresolved"),
                                           (True, "resolved")):
                for steps in range(size + 3):
                    for capacity in range(size + 3):
                        with self.subTest(size=size, capability=capability,
                                          obligation=obligation, steps=steps,
                                          capacity=capacity):
                            doc = document(sample(size), step_bound=steps,
                                           ledger_bound=capacity,
                                           capability=capability,
                                           obligation=obligation)
                            args = (doc["rows"], steps, capacity,
                                    capability, obligation)
                            source_trace, ir_trace, model_trace = [], [], []
                            expected = run(source, *args, transitions=model_trace)
                            self.assertEqual(run(ir, *args), expected)
                            actual = evaluate(doc, _transition_sink=source_trace.append)
                            independent = execute(lower(doc), _transition_sink=ir_trace.append)
                            self.assertEqual(source_trace, model_trace)
                            self.assertEqual(ir_trace, model_trace)
                            self.assertEqual({key: actual[key] for key in expected},
                                             expected)
                            self.assertEqual(independent, expected)
                            self.assertEqual(actual["witness"]["claim"], expected)
                            if expected["terminal_outcome"]["tag"] == "resource_limit":
                                self.assertNotIn("value", expected["terminal_outcome"])

    def test_rejects_unreviewed_schedule_and_domains(self):
        from dataclasses import replace
        program = extract("e7c_eecq_joint_restrict_b1.py")
        with self.assertRaises(ValueError):
            run(replace(program, instructions=program.instructions[:-1]), [], 1, 1,
                True, "resolved")
        with self.assertRaises(ValueError):
            run(program, [], True, 1, True, "resolved")


if __name__ == "__main__":
    unittest.main()
