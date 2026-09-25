"""Edition-pinned finite SF/CFS replay against the unchanged CG3 model."""

from dataclasses import replace
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from eec_q_fg3_b1 import Config, State
from sfcfs_points_b1 import Poly, family
from sfcfs_successor_binding_b1 import (
    EditionAdmission, KERNEL_FILES, bind, realise_bound, restrict_points,
    shared, source_pins,
)

MODEL = Path(__file__).resolve().parents[3] / "E7G-T_Combined_Family_State_v0.1.py"
spec = importlib.util.spec_from_file_location("cg3_successor_reference", MODEL)
cg3 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = cg3
spec.loader.exec_module(cg3)


def fixture():
    points = (Fraction(0), Fraction(1, 2), Fraction(1))
    left = family(points, ((Config((), None), Poly((0, 1))),
                           (Config(("AB",), None), Poly((1, -1)))), "CG3/0.1")
    right = family(points, ((Config(("AC",), None), Poly((0, 1))),
                            (Config(("BC",), None), Poly((1, -1)))), "CG3/0.1")
    old_left = cg3.StateFamily(cg3.Points(points),
                               ((cg3.Graph(), cg3.Poly((0, 1))),
                                (cg3.Graph(("AB",)), cg3.Poly((1, -1)))))
    old_right = cg3.StateFamily(cg3.Points(points),
                                ((cg3.Graph(("AC",)), cg3.Poly((0, 1))),
                                 (cg3.Graph(("BC",)), cg3.Poly((1, -1)))))
    return left, right, old_left, old_right


class InheritedSFCFS(unittest.TestCase):
    def test_both_editions_against_pinned_cg3(self):
        left, right, old_left, old_right = fixture()
        old_shared = old_left.shared_union(old_right)
        for kernel in ("0.13-experimental-draft", "0.14-experimental-draft"):
            with self.subTest(kernel=kernel):
                result = shared(bind(kernel, left), bind(kernel, right))
                self.assertEqual(result.kernel, kernel)
                self.assertEqual(tuple((g.edges, p.coefficients)
                                       for g, p in result.value.terms),
                                 tuple((g.edges, p.coefficients)
                                       for g, p in old_shared.terms))
                for point in left.domain.values:
                    self.assertEqual(tuple((g.edges, c) for g, c in
                                           result.value.instantiate(point).terms),
                                     tuple((g.edges, c) for g, c in
                                           old_shared.instantiate(point).terms))
                self.assertEqual(realise_bound(result, 3).result.status,
                                 cg3.realise(old_shared, max_candidates=3).status)
                self.assertEqual(realise_bound(result, 2).result.status,
                                 "RESOURCE_LIMIT")

    def test_empty_family_differs_from_zero_state_at_each_edition(self):
        points = (Fraction(0), Fraction(1))
        for kernel in ("0.13-experimental-draft", "0.14-experimental-draft"):
            zero = bind(kernel, family(points, (), "CG3/0.1"))
            empty = restrict_points(zero, ())
            self.assertEqual(realise_bound(zero, 2).result.state, State(()))
            self.assertEqual(realise_bound(zero, 2).result.status, "UNIQUE")
            self.assertEqual(realise_bound(empty, 2).result.status, "EMPTY")

    def test_cross_edition_and_tampered_pins_rejected(self):
        left, right, _, _ = fixture()
        old = bind("0.13-experimental-draft", left)
        new = bind("0.14-experimental-draft", right)
        with self.assertRaises(EditionAdmission):
            shared(old, new)
        with self.assertRaises(EditionAdmission):
            realise_bound(replace(old, kernel_sha256="wrong"), 3)
        with patch.dict(KERNEL_FILES, {"0.14-experimental-draft":
                                  (KERNEL_FILES["0.14-experimental-draft"][0], "wrong")}):
            with self.assertRaisesRegex(EditionAdmission, "source digest drift"):
                source_pins("0.14-experimental-draft")


if __name__ == "__main__":
    unittest.main()
