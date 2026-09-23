"""Differential checks of declared FG3 joint and restriction subfragment."""

from __future__ import annotations

import unittest
from fractions import Fraction

from test_eec_q_fg3_b1 import source, source_signature
from eec_q_fg3_b1 import AdmissionError, Config, collect, signature
from eec_q_fg3_joint_b1 import (Joint, independent, join_union, joint,
                               joint_signature, marginal, restrict_absent)


def graph(edges=(), tag=None):
    return Config(tuple(edges), tag)


def original(g):
    return source.Graph(g.edges, g.tag)


def source_joint(rows):
    return source.joint(*((c, tuple(original(g) for g in atoms)) for c, atoms in rows))


def original_joint_signature(rows):
    return tuple((tuple(source.key(g) for g in atoms), c.numerator, c.denominator)
                 for atoms, c in rows)


class JointDifferential(unittest.TestCase):
    def test_correlated_choices_are_not_an_independent_product(self):
        p, q = graph(("AB",)), graph(("BC",))
        rows = [(Fraction(2, 3), (p, p)), (Fraction(-1, 2), (q, q))]
        correlated = joint(rows)
        self.assertEqual(joint_signature(correlated), original_joint_signature(source_joint(rows)))
        left = collect([(p, Fraction(2, 3)), (q, Fraction(-1, 2))])
        right = collect([(p, Fraction(1)), (q, Fraction(1))])
        product = independent(left, right)
        expected = source.independent(source.state(*((c, original(g)) for g, c in left.terms)),
                                      source.state(*((c, original(g)) for g, c in right.terms)))
        self.assertEqual(joint_signature(product), original_joint_signature(expected))
        self.assertEqual(len(correlated.terms), 2)
        self.assertEqual(len(product.terms), 4)
        self.assertEqual(signature(marginal(correlated, 0)),
                         source_signature(source.marginal(source_joint(rows), 0)))

    def test_joint_collection_and_marginal_cancellation(self):
        p, q = graph(("AB",)), graph(("AC",))
        rows = [(Fraction(1), (p, q)), (Fraction(-1), (p, q)),
                (Fraction(2), (q, q)), (Fraction(-2), (p, p))]
        result = joint(rows)
        self.assertEqual(joint_signature(result), original_joint_signature(source_joint(rows)))
        self.assertEqual(signature(marginal(result, 1)),
                         source_signature(source.marginal(source_joint(rows), 1)))

    def test_union_collects_colliding_results(self):
        a, b, ab = graph(("AB",), "same"), graph(("BC",), "same"), graph(("AB", "BC"), "same")
        rows = [(Fraction(3, 5), (a, b)), (Fraction(-3, 5), (ab, b))]
        result = join_union(joint(rows))
        self.assertEqual(result.tag, "success")
        self.assertEqual(signature(result.value), source_signature(source.join(source_joint(rows))))
        self.assertEqual(result.value.terms, ())

    def test_incompatible_union_fails_entire_joint(self):
        p, q = graph(("AB",), "red"), graph(("BC",), "blue")
        rows = [(Fraction(1), (p, p)), (Fraction(1), (p, q))]
        with self.assertRaises(source.DomainError):
            source.join(source_joint(rows))
        result = join_union(joint(rows))
        self.assertEqual((result.tag, result.value), ("domain_error", None))

    def test_restriction_returns_both_states_without_renormalizing(self):
        p, q = graph(("AB",)), graph(("BC",))
        state = collect([(p, Fraction(-2, 3)), (q, Fraction(1, 4))])
        expected = source.restrict_absent("AB", source.state(*((c, original(g)) for g, c in state.terms)))
        result = restrict_absent("AB", state)
        self.assertEqual(tuple(signature(s) for s in result),
                         tuple(source_signature(s) for s in expected))
        self.assertEqual(signature(restrict_absent("AB", collect([]))[0]), ())

    def test_admission_boundary_and_zero_joint_arity(self):
        p = graph(("AB",))
        with self.assertRaises(source.InvalidInput):
            source.joint((Fraction(1), (original(p), original(p))),
                         (Fraction(-1), (original(p), object())))
        with self.assertRaises(AdmissionError):
            joint([(Fraction(1), (p, p)), (Fraction(-1), (p, object()))])
        with self.assertRaises(AdmissionError):
            joint([(Fraction(1), (p, p)), (Fraction(1), (p,))])
        self.assertEqual(source.independent(source.state(), source.unit(original(p))), ())
        zero = independent(collect([]), collect([(p, Fraction(1))]))
        self.assertEqual((zero.arity, zero.terms), (2, ()))
        self.assertEqual(joint_signature(zero), original_joint_signature(
            source.independent(source.state(), source.unit(original(p)))))
        self.assertEqual(signature(marginal(zero, 1)), ())
        with self.assertRaises(AdmissionError):
            marginal(zero, 2)
        with self.assertRaises(AdmissionError):
            Joint(2, (((p,), Fraction(1)),))


if __name__ == "__main__":
    unittest.main()
