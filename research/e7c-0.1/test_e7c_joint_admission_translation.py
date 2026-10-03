"""Selected AST translation, real normal return, and missing-premise example."""

import unittest
import copy
from fractions import Fraction
from unittest.mock import patch

from e7c_joint_admission_translation import OUTPUT, translated_program
import e7c_eecq_joint_restrict_b1 as first
from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint


class AdmissionTranslation(unittest.TestCase):
    def test_generated_lean_matches_checked_running_sites(self):
        self.assertEqual(OUTPUT.read_text(), translated_program())

    def test_signed_rational_null_empty_real_normal_return(self):
        null = Config(("AB",), None)
        empty = Config(("AC",), "")
        value = joint([(Fraction(-2, 3), (null, empty))], arity=2)
        source = first.document(value)
        returned = first.admit(source)
        self.assertEqual(first.rows(returned), source["rows"])
        self.assertEqual(returned.terms[0][1], Fraction(-2, 3))
        self.assertIsNone(returned.terms[0][0][0].tag)
        self.assertEqual(returned.terms[0][0][1].tag, "")

    def test_counterexample_if_serializer_binding_is_forged(self):
        null = Config(("AB",), None)
        empty = Config(("AC",), "")
        source = first.document(joint([(Fraction(-2, 3), (null, empty))], arity=2))
        bad = Joint(2, (((null, empty), Fraction(1, 7)),))
        actual_rows = first.rows
        # This is deliberately outside the theorem's fixed-bindings premise:
        # a forged row serializer can mask a changed Joint behind the guard.
        with patch.object(first, "joint", return_value=bad), patch.object(
                first, "rows", return_value=source["rows"]):
            returned = first.admit(source)
        self.assertNotEqual(actual_rows(returned), source["rows"])

    def test_changed_coefficient_changes_the_admitted_observation(self):
        p = Config(("AB",), None)
        q = Config(("AC",), "")
        source = first.document(joint([(Fraction(1), (p, q))], arity=2))
        changed = copy.deepcopy(source)
        changed["rows"][0]["coefficient"] = {"numerator": 1, "denominator": 7}
        admitted = first.admit(changed)
        self.assertEqual(first.rows(admitted), changed["rows"])
        self.assertNotEqual(admitted.terms[0][1], Fraction(1))

    def test_correlation_is_preserved_and_noncanonical_row_order_is_rejected(self):
        p, q = Config(("AB",), None), Config(("AC",), "")
        r = Config(("BC",), "R")
        value = joint([(Fraction(1), (p, q)), (Fraction(2), (q, r))], arity=2)
        source = first.document(value)
        crossed = copy.deepcopy(source)
        crossed["rows"][0]["atoms"] = [
            crossed["rows"][0]["atoms"][1], crossed["rows"][0]["atoms"][0]]
        crossed_value = first.admit(crossed)
        self.assertEqual(first.rows(crossed_value), crossed["rows"])
        self.assertNotEqual(crossed_value.terms[0][0], value.terms[0][0])
        reversed_rows = copy.deepcopy(source)
        reversed_rows["rows"] = list(reversed(source["rows"]))
        with self.assertRaises(first.JointRestrictionAdmission):
            first.admit(reversed_rows)

    def test_duplicate_and_cancellation_are_rejected(self):
        p, q = Config(("AB",), None), Config(("AC",), "")
        value = joint([(Fraction(1), (p, q))], arity=2)
        source = first.document(value)
        duplicate = copy.deepcopy(source)
        duplicate["rows"] = source["rows"] + [source["rows"][0]]
        with self.assertRaises(first.JointRestrictionAdmission):
            first.admit(duplicate)
        cancelled = copy.deepcopy(source)
        cancelled["rows"] = [source["rows"][0], {
            **source["rows"][0], "coefficient": {"numerator": -1, "denominator": 1}}]
        with self.assertRaises(first.JointRestrictionAdmission):
            first.admit(cancelled)

    def test_tag_is_preserved_and_noncanonical_wire_order_is_rejected(self):
        p, q = Config(("AB",), None), Config(("AC",), "")
        source = first.document(joint([(Fraction(1), (p, q))], arity=2))
        changed_tag = copy.deepcopy(source)
        changed_tag["rows"][0]["atoms"][0]["tag"] = "altered"
        tagged_value = first.admit(changed_tag)
        self.assertEqual(first.rows(tagged_value), changed_tag["rows"])
        self.assertEqual(tagged_value.terms[0][0][0].tag, "altered")
        changed_edges = copy.deepcopy(source)
        changed_edges["rows"][0]["atoms"][0]["edges"] = ["AC", "AB"]
        with self.assertRaises(first.JointRestrictionAdmission):
            first.admit(changed_edges)


if __name__ == "__main__":
    unittest.main()
