import copy
import unittest

from check_e7c_ir_observations import package_gate, examples, capture_text, packets, project_result
from e7c_eecq_two_stage_b1 import evaluate
from check_e7c_ir_observations import admit_raw_capture, PackageCapture, capture_packages
from e7_ir_eecq_two_stage_b1 import lower, serialize
from e7_ir_eecq_joint_restrict_b1 import serialize as serialize_first


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
            self.assertEqual(text.count("example : check"), 3)
            self.assertIn("checkTerminalTransport .source", text)
            self.assertIn("checkTerminalTransport .ir", text)
            self.assertIn("checkCapturedIR", text)
            self.assertNotIn("sorry", text)

    def test_forged_charge_reaches_kernel_unchanged(self):
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        forged = copy.deepcopy(trace)
        forged[0]["steps"] += 1
        encoded, _ = packets(source, result, forged, admit_raw=False)
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
        from e7c_b1_canonical import canonical_key
        item["event"]["row_key"] = canonical_key(raw)
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

    def test_raw_metadata_mutations_reject(self):
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        variants = []
        for key, value in (("effect", "forged"), ("predicate_edition", "forged"),
                           ("ordinal", 1), ("ordinal", True), ("extra", "forged")):
            changed = copy.deepcopy(trace)
            changed[1]["event"][key] = value
            variants.append(changed)
        for key, value in (("stage", "second"), ("row_index", 0),
                           ("extra", "forged"), ("steps", True),
                           ("steps", 99), ("ledger_entries", 99)):
            changed = copy.deepcopy(trace)
            changed[1][key] = value
            variants.append(changed)
        changed = copy.deepcopy(trace)
        changed[3]["event"]["row_key"] = '{"atoms":[],"atoms":[],"coefficient":{}}'
        variants.append(changed)
        changed = copy.deepcopy(trace)
        changed[3]["event"]["decision"] = "second_excluded"
        variants.append(changed)
        for number, changed in enumerate(variants):
            with self.subTest(number=number), self.assertRaises(ValueError):
                admit_raw_capture(result, changed)

    def test_missing_duplicate_and_nonfinal_terminal_reject(self):
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        for changed in (trace[:-1], trace + [trace[-1]], trace + [trace[0]]):
            with self.assertRaises(ValueError):
                packets(source, result, changed)

    def test_terminal_metadata_mutations_reject(self):
        source = examples()[0]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        for key, value in (("stage", "first"), ("row_index", 0), ("steps", True),
                           ("second_started", 1), ("event", {}), ("extra", 1)):
            changed = copy.deepcopy(trace)
            changed[-1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                admit_raw_capture(result, changed)

    def test_byte_capture_uses_actual_serializer_returns(self):
        package = lower(examples()[0])
        capture = capture_packages(package)
        self.assertEqual(capture.nested, serialize_first(package["first_ir"]))
        self.assertEqual(capture.outer, serialize(package))
        self.assertEqual(capture.receipt()["nested_bytes"], len(capture.nested))
        self.assertEqual(capture.receipt()["outer_bytes"], len(capture.outer))
        capture.verify_receipt(capture.receipt())

    def test_capture_rejects_mutable_or_reported_lengths(self):
        for first, second in ((1, b"x"), (b"x", 1), (bytearray(b"x"), b"x")):
            with self.assertRaises(ValueError):
                PackageCapture(first, second)

    def test_byte_receipt_tampering_rejects(self):
        capture = PackageCapture(b"x", b"y")
        for key, value in (("nested_bytes", 0), ("outer_bytes", True),
                           ("nested_sha256", "forged"), ("outer_sha256", "forged")):
            receipt = capture.receipt()
            receipt[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                capture.verify_receipt(receipt)

    def test_byte_boundary_is_independent_and_inclusive(self):
        # Synthetic bytes exercise the capture contract, not admitted IR packages.
        for nested, outer, expected in ((1000000, 1000000, "admitted"),
                                        (1000001, 1, "nested_limit"),
                                        (1, 1000001, "outer_limit")):
            capture = PackageCapture(bytes(nested), bytes(outer))
            self.assertEqual(package_gate(len(capture.nested), len(capture.outer)), expected)


if __name__ == "__main__":
    unittest.main()
