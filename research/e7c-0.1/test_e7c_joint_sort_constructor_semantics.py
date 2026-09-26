"""Focused host checks for pinned identity sorting and Joint admission."""

from __future__ import annotations

import unittest
from fractions import Fraction

from eec_q_fg3_joint_b1 import AdmissionError, Config, Joint, joint


def graph(edges=(), tag=None):
    return Config(tuple(edges), tag)


class JointSortConstructorSemantics(unittest.TestCase):
    def test_edge_order_matches_pinned_identity_key(self):
        values = [graph(("BC",)), graph(("AC",)), graph(("AB",)), graph(())]
        result = joint([(Fraction(1), (item,)) for item in values], arity=1)
        keys = [row[0][0].identity() for row in result.terms]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual([item.edges for (item,), _ in result.terms],
                         [(), ("AB",), ("AC",), ("BC",)])

    def test_null_and_empty_tags_remain_distinct_and_ordered(self):
        absent, empty = graph(("AB",), None), graph(("AB",), "")
        result = joint([(Fraction(1), (empty,)), (Fraction(2), (absent,))], arity=1)
        self.assertEqual([item.tag for (item,), _ in result.terms], [None, ""])
        self.assertEqual([coefficient for _, coefficient in result.terms],
                         [Fraction(2), Fraction(1)])
        self.assertNotEqual(absent.identity(), empty.identity())

    def test_duplicate_keys_accumulate_exact_signed_rationals(self):
        p, q = graph(("AB",)), graph(("BC",))
        result = joint([(Fraction(1, 3), (p, q)),
                        (Fraction(-1, 6), (p, q)),
                        (Fraction(5, 7), (q, p))])
        self.assertEqual(result.terms,
                         (((p, q), Fraction(1, 6)), ((q, p), Fraction(5, 7))))

    def test_exact_cancellation_removes_support_before_construction(self):
        p = graph(("AB",))
        result = joint([(Fraction(7, 11), (p, p)),
                        (Fraction(-7, 11), (p, p))])
        self.assertEqual(result.terms, ())

    def test_constructor_rejects_duplicate_unsorted_zero_and_bad_arity_rows(self):
        p, q = graph(("AB",)), graph(("BC",))
        with self.assertRaises(AdmissionError):
            Joint(2, (((p, p), Fraction(1)), ((p, p), Fraction(2))))
        with self.assertRaises(AdmissionError):
            Joint(2, (((q, q), Fraction(1)), ((p, p), Fraction(1))))
        with self.assertRaises(AdmissionError):
            Joint(2, (((p, p), Fraction(0)),))
        with self.assertRaises(AdmissionError):
            Joint(2, (((p,), Fraction(1)),))

    def test_constructor_rejects_non_fraction_and_wrong_atom_type(self):
        p = graph(("AB",))
        with self.assertRaises(AdmissionError):
            Joint(1, (((p,), 1),))
        with self.assertRaises(AdmissionError):
            Joint(1, (((object(),), Fraction(1)),))

    def test_constructor_rejects_bool_arity_and_non_tuple_term_container(self):
        p = graph(("AB",))
        with self.assertRaises(AdmissionError):
            Joint(True, (((p,), Fraction(1)),))
        with self.assertRaises(AdmissionError):
            Joint(1, [((p,), Fraction(1))])


if __name__ == "__main__":
    unittest.main()
