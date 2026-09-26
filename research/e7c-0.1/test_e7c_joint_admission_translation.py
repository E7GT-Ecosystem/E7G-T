"""Selected AST translation, real normal return, and missing-premise example."""

import unittest
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


if __name__ == "__main__":
    unittest.main()
