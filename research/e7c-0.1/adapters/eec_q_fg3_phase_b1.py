"""Provisional FG3 view and finite equal-edge-count phase adapter.

The only phase carrier here is the complete eight-graph, untagged FG3 basis.
The phase quotient is derived from canonical EEC-Q §X.8, not an FG3 API.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from eec_q_fg3_b1 import AdmissionError, Config, Rule, State

CRITERION = "FG3-UNTAGGED-EDGE-COUNT/0.1"
BASIS = tuple(Config(tuple(edges), None) for n in range(4)
              for edges in combinations(("AB", "AC", "BC"), n))


@dataclass(frozen=True)
class EdgeView:
    source: State
    displayed_rows: tuple[tuple[tuple[str, ...], str], ...]

    def __post_init__(self) -> None:
        if type(self.source) is not State or type(self.displayed_rows) is not tuple:
            raise AdmissionError("view requires a source and display")
        if self.displayed_rows != tuple((g.edges, str(c)) for g, c in self.source.terms):
            raise AdmissionError("display must derive from the retained source")


def edge_view(source: State) -> EdgeView:
    if type(source) is not State:
        raise AdmissionError("typed graph state required")
    return EdgeView(source, tuple((g.edges, str(c)) for g, c in source.terms))


@dataclass(frozen=True)
class PhaseView:
    source: State
    criterion: str
    groups: tuple[tuple[int, tuple[tuple[Config, Fraction], ...]], ...]

    def __post_init__(self) -> None:
        if type(self.source) is not State or self.criterion != CRITERION or type(self.groups) is not tuple:
            raise AdmissionError("invalid phase view")
        if self.groups != _groups(self.source):
            raise AdmissionError("phase display must retain every source term")


def _admit_untagged(source: State) -> None:
    if type(source) is not State or any(g.tag is not None or g not in BASIS for g, _ in source.terms):
        raise AdmissionError("only untagged FG3 graph states admitted")


def _groups(source: State) -> tuple[tuple[int, tuple[tuple[Config, Fraction], ...]], ...]:
    _admit_untagged(source)
    return tuple((n, tuple((g, c) for g, c in source.terms if len(g.edges) == n))
                 for n in range(4) if any(len(g.edges) == n for g, _ in source.terms))


def phase_view(source: State) -> PhaseView:
    _admit_untagged(source)
    return PhaseView(source, CRITERION, _groups(source))


@dataclass(frozen=True)
class PhaseState:
    criterion: str
    terms: tuple[tuple[int, Fraction], ...]

    def __post_init__(self) -> None:
        if self.criterion != CRITERION or type(self.terms) is not tuple:
            raise AdmissionError("invalid phase state criterion or terms")
        keys = []
        for row in self.terms:
            if (type(row) is not tuple or len(row) != 2 or type(row[0]) is not int
                    or row[0] not in range(4) or type(row[1]) is not Fraction or not row[1]):
                raise AdmissionError("phase terms require nonzero exact coefficients")
            keys.append(row[0])
        if keys != sorted(set(keys)):
            raise AdmissionError("phase coefficients must be unique and canonical")


def identify_phase(source: State) -> PhaseState:
    """Explicit lossy quotient q_*; the result cannot be used as graph State."""
    _admit_untagged(source)
    totals = {n: Fraction(0) for n in range(4)}
    for graph, coefficient in source.terms:
        totals[len(graph.edges)] += coefficient
    return PhaseState(CRITERION, tuple((n, totals[n]) for n in range(4) if totals[n]))


@dataclass(frozen=True)
class PhaseStatus:
    criterion: str
    domain_saturated: bool
    result_congruent: bool
    domain_witness: tuple[Config, Config] | None
    result_witness: tuple[Config, Config] | None

    def __post_init__(self) -> None:
        if (self.criterion != CRITERION
                or type(self.domain_saturated) is not bool
                or type(self.result_congruent) is not bool
                or (self.domain_saturated != (self.domain_witness is None))
                or (self.result_congruent != (self.result_witness is None))):
            raise AdmissionError("invalid phase status")


def _apply(rule: Rule, graph: Config) -> Config | None:
    edges = set(graph.edges)
    if rule.name == "require_absent" and rule.edge in edges:
        return None
    if rule.name == "add":
        edges.add(rule.edge)
    elif rule.name == "remove":
        edges.discard(rule.edge)
    elif rule.name == "empty":
        edges.clear()
    return Config(tuple(edges), graph.tag if rule.name != "forget_tag" else None)


def phase_status(rule: Rule) -> PhaseStatus:
    """Check both descent conditions on every pair in each of four classes."""
    if type(rule) is not Rule:
        raise AdmissionError("registered FG3 graph rule required")
    domain_witness, result_witness = None, None
    for n in range(4):
        group = tuple(g for g in BASIS if len(g.edges) == n)
        for left, right in combinations(group, 2):
            a, b = _apply(rule, left), _apply(rule, right)
            if domain_witness is None and ((a is None) != (b is None)):
                domain_witness = (left, right)
            if result_witness is None and a is not None and b is not None and len(a.edges) != len(b.edges):
                result_witness = (left, right)
    return PhaseStatus(CRITERION, domain_witness is None, result_witness is None,
                       domain_witness, result_witness)
