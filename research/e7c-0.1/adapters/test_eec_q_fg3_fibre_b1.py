"""Source-return and finite-carrier fibre regressions for FG3 phase loss."""

from __future__ import annotations

import unittest
from fractions import Fraction

from test_eec_q_fg3_b1 import source, source_signature
from eec_q_fg3_b1 import AdmissionError, Config, State, collect, signature
from eec_q_fg3_phase_b1 import identify_phase
from eec_q_fg3_fibre_b1 import (FibreOutcome, FiniteCarrier, HIDDEN, PRESERVED,
                                PROJECTION, SOURCE_RETURN, SourceProjection,
                                project_view, reconstruct_fibre, source_return)


def source_state(state):
    return source.state(*((c, source.Graph(g.edges, g.tag)) for g, c in state.terms))


def candidates(*states):
    return FiniteCarrier("FG3-FINITE-STATES/fixture-01",
                         tuple(sorted(states, key=signature)))


class FiniteFibreTests(unittest.TestCase):
    def setUp(self):
        self.p = collect([(Config(("AB", "BC"), None), Fraction(1))])
        self.q = collect([(Config(("AC", "BC"), None), Fraction(1))])
        self.cancel = collect([(Config(("AB", "BC"), None), Fraction(1)),
                               (Config(("AC", "BC"), None), Fraction(-1))])
        self.zero = collect([])

    def test_source_return_requires_retained_view(self):
        projection = project_view(self.cancel)
        self.assertEqual((projection.edition, projection.preserved,
                          projection.hidden, projection.source_return_policy),
                         (PROJECTION, PRESERVED, HIDDEN, SOURCE_RETURN))
        self.assertEqual(signature(source_return(projection)),
                         source_signature(source.edge_view(source_state(self.cancel)).source))
        self.assertEqual(projection.identified.terms, ())
        self.assertNotEqual(source_return(projection), self.zero)
        with self.assertRaises(AdmissionError):
            source_return(projection.identified)
        with self.assertRaises(AdmissionError):
            SourceProjection(PROJECTION, projection.displayed, identify_phase(self.p),
                             PRESERVED, HIDDEN, SOURCE_RETURN)

    def test_ambiguous_fibre_and_cancellation_preimage(self):
        carrier = candidates(self.zero, self.p, self.q, self.cancel)
        result = reconstruct_fibre(identify_phase(self.p), carrier, budget=4)
        self.assertEqual((result.tag, result.checked, result.candidates),
                         ("success", 4, (self.p, self.q)))
        zero_result = reconstruct_fibre(identify_phase(self.zero), carrier, budget=4)
        self.assertEqual(zero_result.candidates, (self.zero, self.cancel))
        self.assertEqual(zero_result.target, identify_phase(self.cancel))
        self.assertNotEqual(self.zero, self.cancel)
        for candidate in result.candidates + zero_result.candidates:
            self.assertEqual(identify_phase(candidate),
                             result.target if candidate in result.candidates else zero_result.target)

    def test_budget_cannot_report_incomplete_success(self):
        carrier = candidates(self.zero, self.p, self.q, self.cancel)
        outcome = reconstruct_fibre(identify_phase(self.p), carrier, budget=3)
        self.assertEqual((outcome.tag, outcome.checked, outcome.candidates),
                         ("resource_limit", 0, None))
        with self.assertRaises(AdmissionError):
            FibreOutcome("success", identify_phase(self.p), carrier, 3, (self.p,))
        with self.assertRaises(AdmissionError):
            FibreOutcome("success", identify_phase(self.p), carrier, 4, (self.p,))
        with self.assertRaises(AdmissionError):
            FibreOutcome("resource_limit", identify_phase(self.p), carrier, 1, (self.p,))

    def test_completeness_only_relative_to_declared_carrier(self):
        one = candidates(self.p)
        result = reconstruct_fibre(identify_phase(self.q), one, budget=1)
        self.assertEqual(result.candidates, (self.p,))
        self.assertEqual(result.carrier, one)
        self.assertNotIn(self.q, one.candidates)
        empty = candidates()
        zero_result = reconstruct_fibre(identify_phase(self.zero), empty, budget=0)
        self.assertEqual((zero_result.checked, zero_result.candidates), (0, ()))

    def test_invalid_carrier_and_target_rejected_before_filtering(self):
        tagged = collect([(Config(("AB",), "secret"), Fraction(1))])
        with self.assertRaises(AdmissionError):
            candidates(self.zero, tagged)
        with self.assertRaises(AdmissionError):
            candidates(self.p, self.p)
        with self.assertRaises(AdmissionError):
            project_view(tagged)
        with self.assertRaises(AdmissionError):
            reconstruct_fibre(self.p, candidates(self.p), budget=1)
        with self.assertRaises(AdmissionError):
            reconstruct_fibre(identify_phase(self.p), candidates(self.p), budget=False)
        with self.assertRaises(AdmissionError):
            reconstruct_fibre(identify_phase(self.p), candidates(self.p), budget=-1)


if __name__ == "__main__":
    unittest.main()
