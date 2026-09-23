"""Finite-point CFS differential against the pinned first-party CG3 model."""

import importlib.util
from fractions import Fraction
from pathlib import Path
import sys
import unittest

from eec_q_fg3_b1 import AdmissionError, Config, State
from sfcfs_points_b1 import (EDITION, Family, Poly, Points, family,
                              independent_pairs, realise, restrict, shared_union)

SOURCE = Path(__file__).resolve().parents[3] / "E7G-T_Combined_Family_State_v0.1.py"
spec = importlib.util.spec_from_file_location("cfs_source_for_adapter", SOURCE)
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)


def rows(state):
    return tuple((graph.edges, graph.tag, coefficient) for graph, coefficient in state.terms)


class SFCFSPointsDifferential(unittest.TestCase):
    def setUp(self):
        self.points = (Fraction(0), Fraction(1, 2), Fraction(1))
        self.empty, self.ab = Config((), None), Config(("AB",), None)
        self.ac, self.bc = Config(("AC",), None), Config(("BC",), None)
        self.t, self.one_minus_t = Poly((0, 1)), Poly((1, -1))
        self.left = family(self.points, ((self.empty, self.t),
                                         (self.ab, self.one_minus_t)), "CG3/0.1")
        self.right = family(self.points, ((self.ac, self.t),
                                          (self.bc, self.one_minus_t)), "CG3/0.1")
        S = source
        self.old_left = S.StateFamily(S.Points(self.points),
                         ((S.Graph(), S.Poly((0, 1))),
                          (S.Graph(("AB",)), S.Poly((1, -1)))))
        self.old_right = S.StateFamily(S.Points(self.points),
                         ((S.Graph(("AC",)), S.Poly((0, 1))),
                          (S.Graph(("BC",)), S.Poly((1, -1)))))

    def test_symbolic_family_and_shared_parameter_differential(self):
        shared, old_shared = shared_union(self.left, self.right), self.old_left.shared_union(self.old_right)
        self.assertEqual(shared.domain.values, old_shared.domain.values)
        self.assertEqual(tuple((g.edges, p.coefficients) for g, p in shared.terms),
                         tuple((g.edges, p.coefficients) for g, p in old_shared.terms))
        for point in self.points:
            with self.subTest(point=point):
                self.assertEqual(rows(self.left.instantiate(point)),
                                 rows(self.old_left.instantiate(point)))
                self.assertEqual(rows(shared.instantiate(point)),
                                 rows(old_shared.instantiate(point)))
        self.assertEqual(realise(shared, 3).status,
                         source.realise(old_shared, max_candidates=3).status)

    def test_empty_outer_family_is_not_zero_inner_state(self):
        zero = family(self.points, (), "CG3/0.1")
        empty = restrict(zero, ())
        self.assertFalse(zero.empty)
        self.assertTrue(empty.empty)
        self.assertEqual(zero.instantiate(Fraction(0)), State(()))
        self.assertEqual((realise(zero, 3).status, realise(zero, 3).state),
                         ("UNIQUE", State(())))
        self.assertEqual((realise(empty, 3).status, realise(empty, 3).state),
                         ("EMPTY", None))
        old_zero = source.StateFamily(source.Points(self.points), ())
        self.assertEqual(source.realise(old_zero).status, "UNIQUE")
        self.assertEqual(source.realise(old_zero.restrict(source.Points(()))).status, "EMPTY")

    def test_shared_assignment_cannot_become_independent_product(self):
        pairs = independent_pairs(self.left, self.right)
        self.assertEqual(len(pairs.assignments), 9)
        self.assertEqual(len(shared_union(self.left, self.right).domain.values), 3)
        cross = next(state for t, u, state in pairs.assignments if t == 0 and u == 1)
        diagonal = next(state for t, u, state in pairs.assignments if t == 0 and u == 0)
        self.assertNotEqual(cross, diagonal)
        self.assertEqual(tuple(g.edges for g, _ in cross.terms), (("AB", "AC"),))
        self.assertEqual(tuple(g.edges for g, _ in diagonal.terms), (("AB", "BC"),))
        with self.assertRaises(AdmissionError):
            shared_union(self.left, pairs)

    def test_bounded_realisation_and_context_admission(self):
        self.assertEqual(realise(self.left, 3).status,
                         source.realise(self.old_left, max_candidates=3).status)
        self.assertEqual(realise(self.left, 2).status,
                         source.realise(self.old_left, max_candidates=2).status)
        with self.assertRaises(AdmissionError):
            shared_union(self.left, family(self.points, (), "other-context"))
        with self.assertRaises(AdmissionError):
            Family("future", "CG3/0.1", Points(self.points), ())
        with self.assertRaises(AdmissionError):
            Points((Fraction(1), Fraction(0)))
        with self.assertRaises(AdmissionError):
            family(self.points, ((Config(("AB",), "tagged"), Poly((1,))),), "CG3/0.1")


if __name__ == "__main__":
    unittest.main()
