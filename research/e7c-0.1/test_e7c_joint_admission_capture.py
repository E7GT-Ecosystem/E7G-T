import copy
from fractions import Fraction
import sys
import unittest
from unittest.mock import patch

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_admission_capture import capture, _lock
from e7c_joint_admission_certificates import certificate_text, validate_literals
from e7c_joint_serializer_native_values import ObservationLimit
from test_e7c_joint_serializer_primitive_capture import fixture_values


def fixture_documents():
    documents = [source.document(value) for value in fixture_values()]
    value = joint([(Fraction(1, 2), (Config(("AB",), None), Config(("BC",), "")))], arity=2)
    single = source.document(value)
    unreduced = copy.deepcopy(single)
    unreduced["rows"][0]["coefficient"] = {"numerator": 2, "denominator": 4}
    duplicate = copy.deepcopy(single)
    duplicate["rows"].append(copy.deepcopy(duplicate["rows"][0]))
    cancelled = copy.deepcopy(duplicate)
    cancelled["rows"][1]["coefficient"]["numerator"] *= -1
    reverse = copy.deepcopy(documents[1])
    reverse["rows"].reverse()

    def reorder(value):
        if type(value) is dict:
            return {k: reorder(v) for k, v in reversed(list(value.items()))}
        return [reorder(v) for v in value] if type(value) is list else value

    return documents + [unreduced, duplicate, cancelled, reverse, reorder(documents[1])]


class AdmissionCaptureTests(unittest.TestCase):
    def setUp(self):
        self.bindings = (source.Config, source.Fraction, source.joint, Joint.__init__)
        self.profile = sys.getprofile()

    def tearDown(self):
        self.assertEqual((source.Config, source.Fraction, source.joint, Joint.__init__), self.bindings)
        self.assertIs(sys.getprofile(), self.profile)
        self.assertFalse(_lock.locked())

    def test_actual_constructor_calls_bind_parser_and_joint_operands(self):
        for document in fixture_documents():
            packet = capture(document)
            self.assertEqual(packet["input_rows"], document["rows"])
            self.assertEqual(len(packet["row_calls"]), len(document["rows"]))
            self.assertEqual(packet["calls"], 3 * len(document["rows"]) + 3)
            for raw, observed in zip(document["rows"], packet["row_calls"]):
                self.assertEqual(observed["input"], raw)
                self.assertEqual(observed["fraction"]["numerator"], raw["coefficient"]["numerator"])
                self.assertEqual(observed["fraction"]["denominator"], raw["coefficient"]["denominator"])
                self.assertEqual([c["input"] for c in observed["configs"]], raw["atoms"])
            c = packet["constructor"]
            self.assertEqual(c["input_tuple_ref"], c["output_tuple_ref"])
            self.assertEqual(c["input_refs"], c["output_refs"])
            self.assertEqual(c["input_terms"], c["output_terms"])
            validate_literals(packet)

    def test_unreduced_raw_pair_is_not_repaired_or_claimed_normal_return(self):
        packet = capture(fixture_documents()[5])
        self.assertEqual(packet["input_rows"][0]["coefficient"], {"numerator": 2, "denominator": 4})
        self.assertEqual(packet["row_calls"][0]["fraction"]["output"], {"numerator": 1, "denominator": 2})
        self.assertFalse(packet["observed_admit_exit"]["returned"])
        self.assertTrue(packet["observed_admit_exit"]["exception_type"].endswith("JointRestrictionAdmission"))
        self.assertIn(".integer (4)", certificate_text([packet]))

    def test_normal_observations_match_unwrapped_sibling_profiler(self):
        from check_e7c_admission_certificates import compare_unwrapped
        count = 0
        for document in fixture_documents():
            packet = capture(document)
            if packet["observed_admit_exit"]["returned"]:
                self.assertGreater(compare_unwrapped(document, packet), 0)
                count += 1
        self.assertEqual(count, 6)

    def test_duplicate_cancelled_and_reordered_inputs_keep_prefix_identity(self):
        duplicate, cancelled, reverse = [capture(d) for d in fixture_documents()[6:9]]
        for packet in (duplicate, cancelled, reverse):
            self.assertFalse(packet["observed_admit_exit"]["returned"])
            self.assertEqual(len(packet["parsed_rows"]), len(packet["input_rows"]))
        self.assertEqual(len(duplicate["constructor"]["output_terms"]), 1)
        self.assertEqual(cancelled["constructor"]["output_terms"], [])
        self.assertNotEqual(reverse["parsed_rows"], reverse["constructor"]["input_terms"])

    def test_every_call_limit_interruption_restores_bindings(self):
        document = fixture_documents()[1]
        for limit in range(9):
            with self.assertRaises(ObservationLimit):
                capture(document, call_limit=limit)
            self.assertEqual((source.Config, source.Fraction, source.joint, Joint.__init__), self.bindings)
            self.assertFalse(_lock.locked())
        self.assertTrue(capture(document, call_limit=9)["observed_admit_exit"]["returned"])

    def test_row_cap_and_complete_capture(self):
        value = joint([(Fraction(-7, 11), (Config((), f"{i:03}"), Config((), None)))
                       for i in range(64)], arity=2)
        packet = capture(source.document(value))
        self.assertEqual(len(packet["row_calls"]), 64)
        self.assertEqual(packet["calls"], 195)
        validate_literals(packet)
        with self.assertRaises(ValueError):
            capture(source.document(value), row_limit=63)

    def test_early_native_rejections_produce_no_complete_prefix_packet(self):
        document = fixture_documents()[0]
        for field in ("numerator", "denominator"):
            invalid = copy.deepcopy(fixture_documents()[1])
            invalid["rows"][0]["coefficient"][field] = True
            with self.assertRaises(source.JointRestrictionAdmission):
                capture(invalid)
        invalid = copy.deepcopy(fixture_documents()[1])
        invalid["rows"][0]["atoms"][0]["edges"] = ["AC", "AB"]
        with self.assertRaises(source.JointRestrictionAdmission):
            capture(invalid)
        self.assertTrue(capture(document)["observed_admit_exit"]["returned"])

    def test_changed_admission_or_config_code_rejects_before_hooks(self):
        for obj, name in ((source, "admit"), (Config, "__post_init__")):
            with patch.object(obj, name, lambda *args: None):
                with self.assertRaisesRegex(ValueError, "live admission/constructor code"):
                    capture(fixture_documents()[0])

    def test_existing_instrumentation_and_overlapping_capture_are_preserved(self):
        observer = lambda *args: None
        sys.setprofile(observer)
        try:
            with self.assertRaisesRegex(ValueError, "uninstrumented"):
                capture(fixture_documents()[0])
            self.assertIs(sys.getprofile(), observer)
        finally:
            sys.setprofile(self.profile)
        _lock.acquire()
        try:
            with self.assertRaisesRegex(ValueError, "overlapping"):
                capture(fixture_documents()[0])
        finally:
            _lock.release()

    def test_byte_and_limit_validation_produce_no_packet(self):
        with self.assertRaises(ObservationLimit):
            capture(fixture_documents()[0], byte_limit=0)
        for kwargs in ({"call_limit": 201}, {"byte_limit": 262145}, {"row_limit": True}):
            with self.assertRaises(ValueError):
                capture(fixture_documents()[0], **kwargs)

    def test_exporter_preserves_semantic_forgeries_and_refuses_injection_types(self):
        packet = capture(fixture_documents()[1])
        forged = copy.deepcopy(packet)
        forged["row_calls"][0]["fraction"]["numerator"] = 99
        forged["constructor"]["output_tuple_ref"] += 100
        text = certificate_text([forged])
        self.assertIn(", (99),", text)
        self.assertIn(str(forged["constructor"]["output_tuple_ref"]), text)
        forged["constructor"]["input_refs"] = [True]
        with self.assertRaises(ValueError):
            certificate_text([forged])


if __name__ == "__main__":
    unittest.main()
