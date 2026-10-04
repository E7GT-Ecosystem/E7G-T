"""Finite profiler receipts for selected pinned admission operations."""
import sys
import unittest
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint
from e7c_eecq_joint_restrict_b1 import JointRestrictionAdmission, document
from e7c_joint_admission_operation_capture import capture


class AdmissionOperationCapture(unittest.TestCase):
    def test_original_normal_path_records_exact_fraction_config_joint_and_rows(self):
        value = joint([(Fraction(-2, 3),
                        (Config(("AB",), None), Config(("BC",), "")))], arity=2)
        raw = document(value)
        packet = capture(raw)
        self.assertEqual(packet["edition"], "E7C-native-admission-operations/0.1-provisional")
        self.assertIn("CPython profiler receipt", packet["adequacy"])
        sites = [(event["site"], event["phase"]) for event in packet["events"]]
        for site in ("admit", "Fraction.__new__", "Config.__init__",
                     "Config.__post_init__", "joint", "Joint.__init__",
                     "Joint.__post_init__", "rows", "_row", "_graph"):
            self.assertIn((site, "call"), sites)
        fraction_calls = [event["payload"] for event in packet["events"]
                          if event["site"] == "Fraction.__new__"
                          and event["phase"] == "call"]
        self.assertEqual(fraction_calls, [
            {"numerator": -2, "denominator": 3},
            {"numerator": 0, "denominator": None},
        ])
        self.assertEqual(packet["returned"]["joint"]["terms"][0][1],
                         {"fraction": [-2, 3]})
        self.assertEqual(packet["returned"]["joint"]["terms"][0][0][0]["config"]["tag"], None)
        self.assertEqual(packet["returned"]["joint"]["terms"][0][0][1]["config"]["tag"], "")

    def test_invalid_boolean_integer_fails_without_leaving_profiler_installed(self):
        raw = document(joint([(Fraction(1, 2),
                               (Config(("AB",), None), Config(("BC",), "")))], arity=2))
        raw["rows"][0]["coefficient"]["numerator"] = True
        with self.assertRaises(JointRestrictionAdmission):
            capture(raw)
        self.assertIsNone(sys.getprofile())


if __name__ == "__main__":
    unittest.main()
