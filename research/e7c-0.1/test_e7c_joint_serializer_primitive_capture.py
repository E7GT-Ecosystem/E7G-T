import copy
from fractions import Fraction
import sys
import unittest
from unittest.mock import patch

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_serializer_native_values import ObservationLimit
from e7c_joint_serializer_primitive_capture import capture, _lock
from e7c_joint_serializer_primitive_certificates import certificate_text, validate_literals


def fixture_values():
    left, right = Config(("AB",), None), Config(("BC",), "")
    return [
        Joint(2, ()),
        joint([(Fraction(-2, 3), (left, right)),
               (Fraction(3, 7), (right, left))], arity=2),
        joint([(Fraction(1, 2), (left, left)),
               (Fraction(1, 2), (right, right))], arity=2),
        joint([(Fraction(1, 2), (left, right)),
               (Fraction(1, 2), (right, left))], arity=2),
        joint([(Fraction(-7, 11), (Config(("AB", "AC", "BC"), "Ω"),
                                  Config((), "line\nquote\"")))], arity=2),
    ]


class PrimitiveCaptureTests(unittest.TestCase):
    def setUp(self):
        self.originals = {cls: cls.__getattribute__ for cls in (Config, Fraction, Joint)}
        self.local_list = "list" in vars(source)
        self.profile = sys.getprofile()

    def tearDown(self):
        self.assertEqual({cls: cls.__getattribute__ for cls in self.originals}, self.originals)
        self.assertEqual("list" in vars(source), self.local_list)
        self.assertIs(sys.getprofile(), self.profile)
        self.assertFalse(_lock.locked())

    def test_actual_primitives_frames_and_native_returns(self):
        for value in fixture_values():
            before = source.rows(value)
            packet = capture(value)
            self.assertEqual(packet["output"], before)
            self.assertEqual(source.rows(value), before)
            self.assertEqual(len(packet["events"]), 16 * len(value.terms) + 4)
            self.assertEqual(len(packet["copies"]), 2 * len(value.terms))
            self.assertEqual([e["site"] for e in packet["events"][:3]],
                             ["rows.call", "rows.arity", "rows.terms"])
            for cells in packet["copies"]:
                self.assertEqual(cells["input_refs"], cells["output_refs"])
            validate_literals(packet)

    def test_all_fg3_supports_tags_and_signed_fractions(self):
        for mask in range(8):
            edges = tuple(e for bit, e in enumerate(("AB", "AC", "BC")) if mask & (1 << bit))
            for tag in (None, "", "x", "Ω"):
                value = joint([(Fraction(-7, 11), (Config(edges, tag), Config((), None)))], arity=2)
                packet = capture(value)
                reads = [e["payload"] for e in packet["events"] if e["site"] == "_graph.edges"]
                tags = [e["payload"] for e in packet["events"] if e["site"] == "_graph.tag"]
                self.assertEqual(reads, [list(edges), []])
                self.assertEqual(tags, [tag, None])

    def test_correlations_and_repeated_object_tokens_are_retained(self):
        values = fixture_values()
        diagonal, crossed = capture(values[2]), capture(values[3])
        self.assertNotEqual(diagonal["output"], crossed["output"])
        self.assertEqual(diagonal["copies"][0]["input_refs"],
                         diagonal["copies"][1]["input_refs"])

    def test_complete_capture_at_selected_row_cap(self):
        value = joint([(Fraction(-2, 3), (Config((), f"{i:03}"), Config((), None)))
                       for i in range(64)], arity=2)
        packet = capture(value)
        self.assertEqual(len(packet["events"]), 1028)
        self.assertEqual(len(packet["copies"]), 128)
        validate_literals(packet)

    def test_native_object_domain_and_row_limit(self):
        class SubJoint(Joint):
            pass
        for value in (object(), Joint(1, ()), SubJoint(2, ())):
            with self.assertRaises(ValueError):
                capture(value)
        with self.assertRaises(ObservationLimit):
            capture(fixture_values()[1], row_limit=1)

    def test_interrupted_event_capture_restores_every_binding(self):
        with self.assertRaises(ObservationLimit):
            capture(fixture_values()[1], event_limit=5)
        # The native helper can run again after the rejected capture.
        self.assertTrue(source.rows(fixture_values()[1]))

    def test_byte_limit_produces_no_successful_packet(self):
        with self.assertRaises(ObservationLimit):
            capture(fixture_values()[0], byte_limit=0)

    def test_changed_helper_code_is_rejected_before_instrumentation(self):
        with patch.object(source, "_graph", lambda g: {"edges": [], "tag": None}):
            with self.assertRaisesRegex(ValueError, "live helper code"):
                capture(fixture_values()[1])

    def test_nonordinary_attribute_dispatch_is_rejected(self):
        def custom(obj, name):
            return object.__getattribute__(obj, name)
        with patch.object(Config, "__getattribute__", custom):
            with self.assertRaisesRegex(ValueError, "ordinary attribute"):
                capture(fixture_values()[1])

    def test_existing_profiler_is_preserved(self):
        observer = lambda *args: None
        sys.setprofile(observer)
        try:
            with self.assertRaisesRegex(ValueError, "uninstrumented"):
                capture(fixture_values()[0])
            self.assertIs(sys.getprofile(), observer)
        finally:
            sys.setprofile(self.profile)

    def test_overlapping_capture_refuses_to_rebind(self):
        _lock.acquire()
        try:
            with self.assertRaisesRegex(ValueError, "overlapping"):
                capture(fixture_values()[0])
        finally:
            _lock.release()

    def test_literals_reject_injection_types_but_do_not_repair_forgeries(self):
        packet = capture(fixture_values()[1])
        forged = copy.deepcopy(packet)
        forged["copies"][0]["output_refs"][0] += 100
        forged["output"][0]["coefficient"] = {"numerator": 2, "denominator": 4}
        text = certificate_text([forged])
        self.assertIn(".integer (4)", text)
        self.assertIn(str(forged["copies"][0]["output_refs"]), text)
        invalid = copy.deepcopy(packet)
        invalid["copies"][0]["input_refs"][0] = True
        with self.assertRaises(ValueError):
            certificate_text([invalid])


if __name__ == "__main__":
    unittest.main()
