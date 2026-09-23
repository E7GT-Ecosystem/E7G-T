"""FG3 differential and negative whole-quote cases."""

from __future__ import annotations

import unittest
from fractions import Fraction

from test_eec_q_fg3_b1 import source, source_signature
from eec_q_fg3_b1 import AdmissionError, Config, Rule, collect, push, signature
from eec_q_fg3_quote_b1 import (InsideOutcome, Quote, QuoteState, collect_quotes,
                                inside, pack, quote_signature, unit_quote, unpack)


def source_state(state):
    return source.state(*((c, source.Graph(g.edges, g.tag)) for g, c in state.terms))


def source_quote_signature(state):
    return tuple((source.key(q), c.numerator, c.denominator) for q, c in state.terms)


class QuoteDifferential(unittest.TestCase):
    def test_whole_quote_is_not_branchwise_quotation(self):
        p, q = Config(("AB", "BC"), None), Config(("AC", "BC"), None)
        state = collect([(p, Fraction(1)), (q, Fraction(-1))])
        whole, original = pack(state), source.pack(source_state(state))
        self.assertEqual(whole.identity(), source.key(original))
        self.assertEqual(whole.rank, source.rank(original))
        self.assertEqual(signature(unpack(whole)), source_signature(source.unpack(original)))
        self.assertEqual(quote_signature(unit_quote(whole)),
                         source_quote_signature(source.unit(original)))
        branchwise = collect_quotes([(pack(collect([(p, Fraction(1))])), Fraction(1)),
                                     (pack(collect([(q, Fraction(1))])), Fraction(-1))])
        old_branchwise = source.state((1, source.pack(source.unit(source.Graph(p.edges)))),
                                      (-1, source.pack(source.unit(source.Graph(q.edges)))))
        self.assertEqual(quote_signature(branchwise), source_quote_signature(old_branchwise))
        self.assertNotEqual(quote_signature(branchwise), quote_signature(unit_quote(whole)))

    def test_quote_of_zero_is_one_entity_and_inside_preserves_original(self):
        p, q = Config(("AB", "BC"), None), Config(("AC", "BC"), None)
        state = collect([(p, Fraction(1)), (q, Fraction(-1))])
        original = source.pack(source_state(state))
        quote = pack(state)
        target_first = inside(Rule("add", "AB"), quote)
        self.assertEqual(target_first.tag, "success")
        target_second = inside(Rule("add", "AC"), target_first.value)
        expected = source.inside(source.Rule("add", "AC"),
                                 source.inside(source.Rule("add", "AB"), original))
        self.assertEqual(target_second.tag, "success")
        self.assertEqual(target_second.value.identity(), source.key(expected))
        self.assertEqual(unpack(target_second.value).terms, ())
        self.assertEqual(len(unit_quote(target_second.value).terms), 1)
        self.assertEqual(collect_quotes([]).terms, ())
        self.assertEqual(quote.identity(), source.key(original))  # immutable original

    def test_strict_rule_fails_on_whole_payload_without_partial_quote(self):
        p, q = Config(("AB",), None), Config(("BC",), None)
        whole = pack(collect([(p, Fraction(1)), (q, Fraction(2))]))
        with self.assertRaises(source.DomainError):
            source.inside(source.Rule("require_absent", "AB"), source.pack(source_state(whole.payload)))
        self.assertEqual((inside(Rule("require_absent", "AB"), whole).tag,
                          inside(Rule("require_absent", "AB"), whole).value),
                         ("domain_error", None))
        self.assertEqual(unpack(whole).terms, whole.payload.terms)

    def test_quote_identity_and_exact_outer_cancellation(self):
        a = pack(collect([(Config(("AB",), "semantic"), Fraction(1, 2))]))
        b = pack(collect([(Config(("AB",), None), Fraction(1, 2))]))
        state = collect_quotes([(a, Fraction(1)), (b, Fraction(-1)), (a, Fraction(-1))])
        old = source.state((1, source.pack(source_state(a.payload))),
                           (-1, source.pack(source_state(b.payload))),
                           (-1, source.pack(source_state(a.payload))))
        self.assertEqual(quote_signature(state), source_quote_signature(old))
        self.assertEqual(len(state.terms), 1)

    def test_no_implicit_entry_or_malformed_quote_outcomes(self):
        zero = pack(collect([]))
        with self.assertRaises(source.DomainError):
            source.push(source.Rule("add", "AB"), source.unit(source.pack(source.state())))
        with self.assertRaises(AdmissionError):
            push(Rule("add", "AB"), unit_quote(zero))
        with self.assertRaises(AdmissionError):
            unpack(collect([]))
        with self.assertRaises(AdmissionError):
            pack(unit_quote(zero))
        with self.assertRaises(AdmissionError):
            QuoteState(((zero, Fraction(0)),))
        with self.assertRaises(AdmissionError):
            Quote(collect_quotes([]))
        with self.assertRaises(AdmissionError):
            InsideOutcome("success", None)


if __name__ == "__main__":
    unittest.main()
