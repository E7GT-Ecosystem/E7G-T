"""Disposable E7C WP5 adapter target for the graph-only FG3/EEC-Q fragment.

Inputs are finite, explicit graph records. This module does not import or call
FG3's evaluator; the differential suite compares the independent algorithms.
It is a proposed profile module, not part of the accepted E7C-B1 core/API.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

EDGES = frozenset(("AB", "AC", "BC"))
TOTAL = frozenset(("add", "remove", "forget_tag", "empty"))
STRICT = frozenset(("require_absent",))


class AdmissionError(ValueError):
    """Controlled invalid-input boundary before any coefficient collection."""


@dataclass(frozen=True)
class Config:
    edges: tuple[str, ...]
    tag: str | None

    def __post_init__(self) -> None:
        if type(self.edges) is not tuple or any(type(e) is not str or e not in EDGES for e in self.edges):
            raise AdmissionError("FG3 edges must be AB, AC or BC")
        if self.tag is not None and type(self.tag) is not str:
            raise AdmissionError("tag must be a string or null")
        object.__setattr__(self, "edges", tuple(sorted(set(self.edges))))

    def identity(self) -> tuple[Any, ...]:
        return ("graph", self.edges, self.tag is not None, self.tag or "")


@dataclass(frozen=True)
class State:
    terms: tuple[tuple[Config, Fraction], ...]

    def __post_init__(self) -> None:
        if type(self.terms) is not tuple or any(
            type(config) is not Config or type(coefficient) is not Fraction or not coefficient
            for config, coefficient in self.terms
        ):
            raise AdmissionError("state requires canonical nonzero exact terms")
        ids = [config.identity() for config, _ in self.terms]
        if ids != sorted(set(ids)):
            raise AdmissionError("state support must be unique and canonical")


def _graph(record: Any) -> Config:
    if type(record) is not dict or set(record) != {"edges", "tag"}:
        raise AdmissionError("graph record requires edges and tag")
    if type(record["edges"]) is not list:
        raise AdmissionError("graph edges must be a list")
    return Config(tuple(record["edges"]), record["tag"])


def _coefficient(record: Any) -> Fraction:
    if type(record) is not dict or set(record) != {"numerator", "denominator"}:
        raise AdmissionError("coefficient requires numerator and denominator")
    n, d = record["numerator"], record["denominator"]
    if type(n) is not int or type(d) is not int or d <= 0:
        raise AdmissionError("exact integer numerator and positive denominator required")
    return Fraction(n, d)


def collect(rows: list[tuple[Config, Fraction]]) -> State:
    totals: dict[Config, Fraction] = {}
    for config, coefficient in rows:
        if type(config) is not Config or type(coefficient) is not Fraction:
            raise AdmissionError("unadmitted term")
        totals[config] = totals.get(config, Fraction(0)) + coefficient
    return State(tuple(sorted(((g, c) for g, c in totals.items() if c),
                              key=lambda pair: pair[0].identity())))


def translate_rows(rows: Any) -> State:
    """Admit every supplied row before cancellation, even a zero row."""
    if type(rows) is not list:
        raise AdmissionError("finite row list required")
    admitted: list[tuple[Config, Fraction]] = []
    for row in rows:
        if type(row) is not dict or set(row) != {"config", "coefficient"}:
            raise AdmissionError("row requires config and coefficient")
        admitted.append((_graph(row["config"]), _coefficient(row["coefficient"])))
    return collect(admitted)


def add(left: State, right: State) -> State:
    if type(left) is not State or type(right) is not State:
        raise AdmissionError("typed states required")
    return collect(list(left.terms) + list(right.terms))


def scale(coefficient: Any, source: State) -> State:
    if type(source) is not State:
        raise AdmissionError("typed state required")
    factor = _coefficient(coefficient)
    return collect([(g, factor * c) for g, c in source.terms])


@dataclass(frozen=True)
class Rule:
    name: str
    edge: str | None = None

    def __post_init__(self) -> None:
        if type(self.name) is not str or self.name not in TOTAL | STRICT:
            raise AdmissionError("unregistered FG3 rule")
        if self.name in {"add", "remove", "require_absent"}:
            if type(self.edge) is not str or self.edge not in EDGES:
                raise AdmissionError("registered edge required")
        elif self.edge is not None:
            raise AdmissionError("rule has no edge parameter")

    @property
    def domain_policy(self) -> str:
        return "strict" if self.name in STRICT else "total"


@dataclass(frozen=True)
class Outcome:
    tag: str
    value: State | None = None


def push(rule: Rule, source: State) -> Outcome:
    if type(rule) is not Rule or type(source) is not State:
        raise AdmissionError("admitted rule and typed state required")
    images: list[tuple[Config, Fraction]] = []
    for config, coefficient in source.terms:
        edges = set(config.edges)
        if rule.name == "require_absent" and rule.edge in edges:
            return Outcome("domain_error")  # strict: no partial success
        if rule.name == "add":
            edges.add(rule.edge)
        elif rule.name == "remove":
            edges.discard(rule.edge)
        elif rule.name == "empty":
            edges.clear()
        tag = None if rule.name == "forget_tag" else config.tag
        images.append((Config(tuple(edges), tag), coefficient))
    return Outcome("success", collect(images))


def signature(state: State) -> tuple[tuple[tuple[Any, ...], int, int], ...]:
    """Value comparison under exact FG3 graph identity; not a witness format."""
    return tuple((g.identity(), c.numerator, c.denominator) for g, c in state.terms)
