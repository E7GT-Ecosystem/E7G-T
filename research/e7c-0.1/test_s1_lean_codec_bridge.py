"""Selected Python-side checks for the bounded Lean FG3 wire bridge.

These exercise the real S1 codec. They are finite differential evidence,
not a proof that the Python implementation refines the Lean definitions.
"""

import itertools
import unittest
from fractions import Fraction

from e7c_s1_values import (RuntimeAdmissionError, canonical, coeff,
                           encode_value, graph)


class SelectedLeanCodecBridge(unittest.TestCase):
    def test_arbitrary_python_tag_remains_distinct(self):
        for tag in ("marked", "phase-x", "reviewed"):
            with self.subTest(tag=tag):
                key = graph({"edges": ["AC"], "tag": tag})
                self.assertEqual(key, (("AC",), tag))
                self.assertEqual(encode_value(1, canonical([((key,), Fraction(1))], 1))
                                 ["rows"][0]["configs"][0]["tag"], tag)

    def test_registered_graph_edges_and_tags(self):
        labels = ("AB", "AC", "BC")
        for bits, tag in itertools.product(itertools.product((False, True), repeat=3),
                                           (None, "marked")):
            with self.subTest(bits=bits, tag=tag):
                expected = tuple(label for label, present in zip(labels, bits) if present)
                wire = {"edges": list(reversed(expected)) + list(expected[:1]),
                        "tag": tag}
                self.assertEqual(graph(wire), (expected, tag))
                self.assertEqual(
                    encode_value(1, canonical([(((expected, tag),), Fraction(1))], 1))
                    ["rows"][0]["configs"][0],
                    {"edges": list(expected), "tag": tag})

    def test_exact_fraction_value_and_admission(self):
        for numerator, denominator, expected in ((1, 2, Fraction(1, 2)),
                                                 (-2, 4, Fraction(-1, 2)),
                                                 (0, 7, Fraction(0))):
            with self.subTest(numerator=numerator, denominator=denominator):
                actual = coeff({"numerator": numerator, "denominator": denominator})
                self.assertEqual(actual, expected)
                self.assertEqual(numerator * actual.denominator,
                                 actual.numerator * denominator)
        with self.assertRaises(RuntimeAdmissionError):
            coeff({"numerator": 1, "denominator": 0})

    def test_collision_cancellation_and_canonical_value(self):
        marked_ab = graph({"edges": ["AB"], "tag": "marked"})
        untagged_bc = graph({"edges": ["BC"], "tag": None})
        rows = [((marked_ab,), coeff({"numerator": 1, "denominator": 2})),
                ((untagged_bc,), coeff({"numerator": 2, "denominator": 3})),
                ((marked_ab,), coeff({"numerator": -2, "denominator": 4})),
                ((untagged_bc,), coeff({"numerator": 1, "denominator": 6}))]
        expected = {"kind": "state", "rows": [
            {"configs": [{"edges": ["BC"], "tag": None}],
             "coefficient": {"numerator": 5, "denominator": 6}}]}
        self.assertEqual(encode_value(1, canonical(rows, 1)), expected)
        self.assertEqual(encode_value(1, canonical(list(reversed(rows)), 1)), expected)


if __name__ == "__main__":
    unittest.main()
