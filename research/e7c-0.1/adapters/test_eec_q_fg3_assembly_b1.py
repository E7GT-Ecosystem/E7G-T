"""Differential checks of FG3 pair and wiring-choice joins."""

from __future__ import annotations

import unittest
from fractions import Fraction

from test_eec_q_fg3_b1 import source
from eec_q_fg3_b1 import AdmissionError, Config, collect
from eec_q_fg3_joint_b1 import independent, joint, marginal
from eec_q_fg3_assembly_b1 import (Assembly, AssemblyOutcome, AssemblyState,
                                   assembly_signature, collect_assemblies,
                                   join_pair, join_wire_choice)


def old_joint(rows):
    return source.joint(*((c, tuple(source.Graph(g.edges, g.tag) for g in atoms))
                          for c, atoms in rows))


def old_signature(state):
    return tuple((source.key(a), c.numerator, c.denominator) for a, c in state.terms)


class AssemblyDifferential(unittest.TestCase):
    def test_correlated_pair_is_not_product_of_marginals(self):
        round_, square = Config((), "round"), Config((), "square")
        red, blue = Config((), "red"), Config((), "blue")
        rows = [(Fraction(2), (round_, red)), (Fraction(-1), (square, blue))]
        shared = joint(rows)
        expected = source.join(old_joint(rows), "pair")
        direct = join_pair(shared)
        self.assertEqual(direct.tag, "success")
        self.assertEqual(assembly_signature(direct.value), old_signature(expected))
        self.assertEqual(len(direct.value.terms), 2)
        factorized = join_pair(independent(marginal(shared, 0), marginal(shared, 1)))
        self.assertEqual(len(factorized.value.terms), 4)
        self.assertNotEqual(assembly_signature(factorized.value), assembly_signature(direct.value))

    def test_wiring_choice_retains_relation_and_shared_coefficient(self):
        x, y = Config(("AB",), "left"), Config(("BC",), "right")
        uses, contains = Config((), "uses"), Config((), "contains")
        rows = [(Fraction(2, 3), (x, y, uses)), (Fraction(-1, 2), (x, y, contains))]
        result = join_wire_choice(joint(rows))
        self.assertEqual(result.tag, "success")
        self.assertEqual(assembly_signature(result.value),
                         old_signature(source.join(old_joint(rows), "wire_choice")))
        self.assertEqual(len(result.value.terms), 2)
        self.assertNotEqual(result.value.terms[0][0].relation,
                            result.value.terms[1][0].relation)

    def test_invalid_supported_wiring_fails_the_whole_join(self):
        x, y = Config(("AB",), None), Config(("BC",), None)
        valid, invalid = Config((), "uses"), Config(("AB",), "contains")
        rows = [(Fraction(1), (x, y, valid)), (Fraction(-1), (x, y, invalid))]
        with self.assertRaises(source.DomainError):
            source.join(old_joint(rows), "wire_choice")
        result = join_wire_choice(joint(rows))
        self.assertEqual((result.tag, result.value), ("domain_error", None))

    def test_cancelled_invalid_wiring_is_not_a_supported_branch(self):
        x, y = Config(("AB",), None), Config(("BC",), None)
        invalid = Config(("AB",), "uses")
        rows = [(Fraction(1), (x, y, invalid)), (Fraction(-1), (x, y, invalid))]
        self.assertEqual(old_joint(rows), ())
        self.assertEqual(old_signature(source.join(old_joint(rows), "wire_choice")), ())
        self.assertEqual(join_wire_choice(joint(rows)).value.terms, ())

    def test_outer_assembly_identity_collection_and_zero(self):
        x, y = Config(("AB",), "left"), Config(("BC",), "right")
        uses, contains = Assembly(x, y), Assembly(x, y, "contains")
        result = collect_assemblies([(uses, Fraction(1)), (uses, Fraction(-1)),
                                     (contains, Fraction(1, 3))])
        old = source.state((1, source.Assembly(source.Graph(x.edges, x.tag),
                                               source.Graph(y.edges, y.tag))),
                           (-1, source.Assembly(source.Graph(x.edges, x.tag),
                                                source.Graph(y.edges, y.tag))),
                           (Fraction(1, 3), source.Assembly(source.Graph(x.edges, x.tag),
                                                             source.Graph(y.edges, y.tag), "contains")))
        self.assertEqual(assembly_signature(result), old_signature(old))
        self.assertEqual(len(result.terms), 1)
        self.assertEqual(join_pair(independent(collect([]), collect([(x, Fraction(1))]))).value.terms, ())

    def test_admission_does_not_convert_graph_state_or_wrong_arity(self):
        x = Config(("AB",), None)
        with self.assertRaises(AdmissionError):
            Assembly(x, x, "unknown")
        with self.assertRaises(AdmissionError):
            join_pair(joint([(Fraction(1), (x, x, x))]))
        with self.assertRaises(AdmissionError):
            join_wire_choice(joint([(Fraction(1), (x, x))]))
        with self.assertRaises(AdmissionError):
            AssemblyState(((Assembly(x, x), Fraction(0)),))
        with self.assertRaises(AdmissionError):
            AssemblyOutcome("success", None)
        with self.assertRaises(AdmissionError):
            collect_assemblies([(x, Fraction(1))])


if __name__ == "__main__":
    unittest.main()
