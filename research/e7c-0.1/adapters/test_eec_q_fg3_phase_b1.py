"""FG3 differential and canonical-only negative tests for phase boundaries."""

from __future__ import annotations

import unittest
from fractions import Fraction

from test_eec_q_fg3_b1 import source, source_signature
from eec_q_fg3_b1 import AdmissionError, Config, Rule, collect, push, signature
from eec_q_fg3_phase_b1 import (BASIS, CRITERION, EdgeView, PhaseState, PhaseView,
                               edge_view, identify_phase, phase_status, phase_view)


class PhaseDifferential(unittest.TestCase):
    def test_edge_view_retains_semantic_tags_and_exact_source(self):
        first, second = Config(("AB",), "first"), Config(("AB",), "second")
        state = collect([(first, Fraction(1)), (second, Fraction(-1))])
        old = source.state((1, source.Graph(first.edges, first.tag)),
                           (-1, source.Graph(second.edges, second.tag)))
        view, old_view = edge_view(state), source.edge_view(old)
        self.assertEqual(view.displayed_rows, old_view.displayed_rows)
        self.assertEqual(signature(view.source), source_signature(old_view.source))
        self.assertEqual(view.displayed_rows[0][0], view.displayed_rows[1][0])
        self.assertEqual(len(view.source.terms), 2)
        self.assertEqual(signature(push(Rule("forget_tag"), state).value),
                         source_signature(source.push(source.Rule("forget_tag"), old)))
        self.assertEqual(push(Rule("forget_tag"), state).value.terms, ())
        with self.assertRaises(AdmissionError):
            EdgeView(state, ())
        with self.assertRaises(AdmissionError):
            push(Rule("empty"), view)

    def test_phase_view_retains_source_while_explicit_quotient_cancels(self):
        p, q = Config(("AB", "BC"), None), Config(("AC", "BC"), None)
        state = collect([(p, Fraction(2, 3)), (q, Fraction(-2, 3))])
        view = phase_view(state)
        self.assertEqual(view.criterion, CRITERION)
        self.assertEqual(view.source, state)
        self.assertEqual(len(view.groups), 1)
        self.assertEqual(len(view.groups[0][1]), 2)
        quotient = identify_phase(state)
        self.assertEqual(quotient.terms, ())
        self.assertEqual(len(state.terms), 2)
        self.assertNotEqual(type(quotient), type(state))
        with self.assertRaises(AdmissionError):
            push(Rule("add", "AB"), quotient)
        with self.assertRaises(AdmissionError):
            PhaseView(state, CRITERION, ())
        with self.assertRaises(AdmissionError):
            PhaseState(CRITERION, ((2, Fraction(0)),))

    def test_phase_bounded_carrier_rejects_undeclared_tag_loss(self):
        tagged = collect([(Config(("AB",), "semantic"), Fraction(1))])
        with self.assertRaises(AdmissionError):
            phase_view(tagged)
        with self.assertRaises(AdmissionError):
            identify_phase(tagged)
        self.assertEqual(phase_view(collect([])).groups, ())
        self.assertEqual(identify_phase(collect([])).terms, ())

    def test_status_matches_source_on_complete_fixed_untagged_basis(self):
        self.assertEqual(len(BASIS), 8)
        self.assertEqual(len(set(BASIS)), 8)
        self.assertEqual(tuple(sorted(g.edges for g in BASIS)),
                         tuple(sorted(g.edges for g in (source.Graph(tuple(edges))
                         for edges in ((), ("AB",), ("AC",), ("BC",), ("AB", "AC"),
                                       ("AB", "BC"), ("AC", "BC"), ("AB", "AC", "BC"))))))
        for name in ("add", "remove", "require_absent", "forget_tag", "empty"):
            for edge in (("AB", "AC", "BC") if name in {"add", "remove", "require_absent"} else (None,)):
                with self.subTest(name=name, edge=edge):
                    expected = source.phase_status(source.Rule(name, edge),
                                                   [source.Graph(g.edges) for g in BASIS])
                    actual = phase_status(Rule(name, edge))
                    self.assertEqual((actual.domain_saturated, actual.result_congruent),
                                     (expected["domain_saturated"], expected["result_congruent"]))

    def test_two_distinct_phase_descent_failures_have_witnesses(self):
        p, q = Config(("AB", "BC"), None), Config(("AC", "BC"), None)
        add_status = phase_status(Rule("add", "AB"))
        domain_status = phase_status(Rule("require_absent", "AB"))
        self.assertTrue(add_status.domain_saturated)
        self.assertFalse(add_status.result_congruent)
        self.assertFalse(domain_status.domain_saturated)
        self.assertEqual(len(p.edges), len(q.edges))
        self.assertNotEqual(len(push(Rule("add", "AB"), collect([(p, Fraction(1))])).value.terms[0][0].edges),
                            len(push(Rule("add", "AB"), collect([(q, Fraction(1))])).value.terms[0][0].edges))
        self.assertIsNotNone(add_status.result_witness)
        self.assertIsNotNone(domain_status.domain_witness)
        for left, right in (add_status.result_witness, domain_status.domain_witness):
            self.assertEqual(len(left.edges), len(right.edges))
        self.assertTrue(phase_status(Rule("remove", "AB")).domain_saturated)


if __name__ == "__main__":
    unittest.main()
