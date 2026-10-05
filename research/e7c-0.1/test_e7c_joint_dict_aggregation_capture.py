"""Finite event-order checks for the actual pinned Joint dictionary loop."""
import sys
import unittest
from fractions import Fraction

from eec_q_fg3_b1 import AdmissionError, Config
from eec_q_fg3_joint_b1 import Joint
from e7c_joint_dict_aggregation_capture import capture


class JointDictionaryCapture(unittest.TestCase):
    def test_duplicate_addition_cancellation_and_nonzero_filter_are_observed(self):
        p, q = Config(("AB",), None), Config(("BC",), "")
        p_equal, q_equal = Config(("AB",), None), Config(("BC",), "")
        terms = [(Fraction(1, 3), (p, q)),
                 (Fraction(1, 6), (p_equal, q_equal)),
                 (Fraction(-1, 2), (p, q)),
                 (Fraction(2, 5), (q, p))]
        packet = capture(terms)
        events = packet["events"]
        transitions = packet["dictionary_transitions"]
        self.assertEqual([event["index"] for event in transitions], [0, 1, 2, 3])
        self.assertTrue(all(event["dict_get_call"] for event in transitions))
        self.assertEqual([event["lookup_result"] for event in transitions], [
            {"fraction": [0, 1]}, {"fraction": [1, 3]},
            {"fraction": [1, 2]}, {"fraction": [0, 1]}])
        self.assertEqual([event["addition_result"] for event in transitions], [
            {"fraction": [1, 3]}, {"fraction": [1, 2]},
            {"fraction": [0, 1]}, {"fraction": [2, 5]}])
        self.assertEqual([len(event["before"]) for event in transitions], [0, 1, 1, 1])
        self.assertEqual([len(event["after"]) for event in transitions], [1, 1, 1, 2])
        self.assertEqual(transitions[0]["row"]["coefficient"], {"fraction": [1, 3]})
        self.assertEqual(transitions[1]["row"]["coefficient"], {"fraction": [1, 6]})
        self.assertEqual(transitions[2]["row"]["coefficient"], {"fraction": [-1, 2]})
        self.assertEqual(transitions[3]["row"]["coefficient"], {"fraction": [2, 5]})

        updates = [event for event in events if event["site"] == "dictionary-row"]
        before = [event for event in updates if event["phase"] == "before-update"]
        after = [event for event in updates if event["phase"] == "after-update"]
        self.assertEqual([event["index"] for event in before], [0, 1, 2, 3])
        self.assertEqual([event["index"] for event in after], [0, 1, 2, 3])
        self.assertEqual([len(event["entries"]) for event in after], [1, 1, 1, 2])
        self.assertEqual(after[0]["entries"][0]["coefficient"], {"fraction": [1, 3]})
        self.assertEqual(after[1]["entries"][0]["coefficient"], {"fraction": [1, 2]})
        self.assertEqual(after[2]["entries"][0]["coefficient"], {"fraction": [0, 1]})

        lookups = [event for event in events
                   if event["site"] == "dict.get" and event["phase"] == "c_call"]
        self.assertEqual(len(lookups), 4)
        self.assertEqual([len(event["entries"]) for event in lookups], [0, 1, 1, 1])

        additions = [event for event in events
                     if event["site"] == "Fraction.add" and event["phase"] == "return"]
        self.assertEqual([event["result"] for event in additions], [
            {"fraction": [1, 3]}, {"fraction": [1, 2]},
            {"fraction": [0, 1]}, {"fraction": [2, 5]}])
        truth = [event for event in events
                 if event["site"] == "Fraction.truth-filter" and event["phase"] == "return"]
        self.assertEqual([event["result"] for event in truth], [False, True])
        constructor = next(event for event in events if event["site"] == "Joint.constructor")
        self.assertEqual(len(constructor["terms"]["tuple"]), 1)
        self.assertEqual(packet["returned"]["joint"]["terms"][0][1],
                         {"fraction": [2, 5]})

    def test_invalid_constructor_order_is_rejected_and_hooks_are_restored(self):
        a, b = Config(("AB",), None), Config(("BC",), None)
        with self.assertRaises(AdmissionError):
            Joint(2, ((((b, a)), Fraction(1)), (((a, b)), Fraction(1))))
        self.assertIsNone(sys.getprofile())
        self.assertIsNone(sys.gettrace())


if __name__ == "__main__":
    unittest.main()
