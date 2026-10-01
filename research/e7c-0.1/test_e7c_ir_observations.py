import copy
import unittest

from check_e7c_ir_observations import package_gate, examples, capture_text, packets, project_result
from e7c_eecq_two_stage_b1 import evaluate


class IRObservationTests(unittest.TestCase):
    def test_separate_measured_bounds(self):
        self.assertEqual(package_gate(1000000, 1000000), "admitted")
        self.assertEqual(package_gate(1000001, 1), "nested_limit")
        self.assertEqual(package_gate(1, 1000001), "outer_limit")
        self.assertEqual(package_gate(1000001, 1000001), "nested_limit")

    def test_invalid_measurements(self):
        for nested, outer in [(True, 1), (-1, 1), (1, None)]:
            with self.assertRaises(ValueError):
                package_gate(nested, outer)

    def test_all_fresh_literal_captures_render(self):
        for source in examples():
            text = capture_text(source)
            self.assertEqual(text.count("example :"), 3)
            self.assertIn("checkTerminalTransport .source", text)
            self.assertIn("checkTerminalTransport .ir", text)
            self.assertIn("checkTerminalTransportIR", text)
            self.assertNotIn("sorry", text)

    def test_forged_charge_reaches_kernel_unchanged(self):
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        forged = copy.deepcopy(trace)
        forged[0]["steps"] += 1
        encoded, _ = packets(source, result, forged)
        self.assertEqual(encoded[0], "(.charge 2 false)")

    def test_forged_row_payload_is_not_replaced_by_input_row(self):
        import json
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        forged = copy.deepcopy(trace)
        item = next(i for i in forged if i["action"] == "append" and
                    i["event"]["event"] == "joint_row_checked")
        raw = json.loads(item["event"]["row_key"])
        raw["coefficient"]["numerator"] *= 2
        item["event"]["row_key"] = json.dumps(raw)
        encoded, _ = packets(source, result, forged)
        self.assertIn("num := -4", " ".join(encoded))

    def test_unknown_action_is_not_a_terminal(self):
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        trace[0]["action"] = "forged"
        with self.assertRaises(ValueError):
            packets(source, result, trace)

    def test_boolean_charge_is_not_a_natural(self):
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        trace[0]["steps"] = True
        with self.assertRaises(ValueError):
            packets(source, result, trace)

    def test_failed_second_append_exact_boundary(self):
        source = examples()[-1]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        self.assertEqual(result["terminal_outcome"]["tag"], "resource_limit")
        self.assertEqual(result["resource_progress"]["completed_steps"], 3)
        self.assertEqual(len(result["ordered_ledger"]), 2)
        encoded, projected = packets(source, result, trace)
        self.assertTrue(projected["secondStarted"])
        self.assertEqual(encoded[-2], "(.charge 3 true)")

    def test_wrong_success_coefficient_survives_structural_projection(self):
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        result["terminal_outcome"]["value"]["retained"][0]["coefficient"]["numerator"] = 2
        projected = project_result(result, trace[-1])
        self.assertEqual(projected["partition"][0][0].coefficient.numerator, 2)

    def test_resource_terminal_progress_is_not_replaced(self):
        source = examples()[-1]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        result["terminal_outcome"]["progress"]["completed_steps"] = 4
        projected = project_result(result, trace[-1])
        self.assertEqual(projected["completedSteps"], 3)
        self.assertEqual(projected["resourceTerminalProgress"]["completedSteps"], 4)

    def test_terminal_start_bit_is_observed_not_inferred(self):
        source = examples()[-1]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        trace[-1]["second_started"] = False
        self.assertFalse(project_result(result, trace[-1])["secondStarted"])


if __name__ == "__main__":
    unittest.main()
