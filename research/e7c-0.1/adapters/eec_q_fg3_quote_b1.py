"""Rank-one, whole-graph-state quotation for the provisional EEC-Q target.

Only graph states may be quoted. There is no recursive mixed-rank signature,
assembly constructor, arbitrary rule quotation or implicit graph-rule entry.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from eec_q_fg3_b1 import AdmissionError, Rule, State, push, signature


@dataclass(frozen=True)
class Quote:
    payload: State

    def __post_init__(self) -> None:
        if type(self.payload) is not State:
            raise AdmissionError("whole admitted graph state required")

    def identity(self) -> tuple:
        return ("box", signature(self.payload))

    @property
    def rank(self) -> int:
        return 1


@dataclass(frozen=True)
class QuoteState:
    terms: tuple[tuple[Quote, Fraction], ...]

    def __post_init__(self) -> None:
        if type(self.terms) is not tuple:
            raise AdmissionError("canonical quote terms required")
        keys = []
        for row in self.terms:
            if (type(row) is not tuple or len(row) != 2
                    or type(row[0]) is not Quote or type(row[1]) is not Fraction or not row[1]):
                raise AdmissionError("nonzero exact quote coefficient required")
            keys.append(row[0].identity())
        if keys != sorted(set(keys)):
            raise AdmissionError("quote terms must be unique and canonical")


def collect_quotes(rows: list[tuple[Quote, Fraction]]) -> QuoteState:
    if type(rows) is not list:
        raise AdmissionError("finite quote rows required")
    totals: dict[Quote, Fraction] = {}
    for row in rows:
        if (type(row) is not tuple or len(row) != 2
                or type(row[0]) is not Quote or type(row[1]) is not Fraction):
            raise AdmissionError("admitted whole quote and exact coefficient required")
        quote, coefficient = row
        totals[quote] = totals.get(quote, Fraction(0)) + coefficient
    return QuoteState(tuple(sorted(((q, c) for q, c in totals.items() if c),
                                   key=lambda pair: pair[0].identity())))


def pack(source: State) -> Quote:
    if type(source) is not State:
        raise AdmissionError("graph state required for whole quote")
    return Quote(source)


def unpack(quote: Quote) -> State:
    if type(quote) is not Quote:
        raise AdmissionError("whole graph quote required")
    return quote.payload


def unit_quote(quote: Quote) -> QuoteState:
    if type(quote) is not Quote:
        raise AdmissionError("whole graph quote required")
    return collect_quotes([(quote, Fraction(1))])


@dataclass(frozen=True)
class InsideOutcome:
    tag: str
    value: Quote | None = None

    def __post_init__(self) -> None:
        if not ((self.tag == "success" and type(self.value) is Quote)
                or (self.tag == "domain_error" and self.value is None)):
            raise AdmissionError("invalid inside outcome")


def inside(rule: Rule, quote: Quote) -> InsideOutcome:
    """Execute an admitted graph rule on a whole payload, then requote it."""
    if type(rule) is not Rule or type(quote) is not Quote:
        raise AdmissionError("registered graph rule and whole quote required")
    result = push(rule, quote.payload)
    if result.tag == "domain_error":
        return InsideOutcome("domain_error")
    return InsideOutcome("success", pack(result.value))


def quote_signature(source: QuoteState) -> tuple:
    return tuple((q.identity(), c.numerator, c.denominator) for q, c in source.terms)
