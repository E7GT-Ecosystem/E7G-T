"""Selected finite-point SF/CFS family-of-FG3-states integration fragment.

The outer family has exact parameter membership; the inner state uses exact
EEC-Q coefficients. Shared and independent parameters have different sorts.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from eec_q_fg3_b1 import AdmissionError, Config, State, collect
from eec_q_fg3_phase_b1 import BASIS

EDITION = "E7C-SFCFS-POINTS-B1/0.1-provisional"
SOURCE = "CFS/0.1:CG3/0.1:SF/0.1:IC/0.1"
MAX_POINTS = 32
MAX_DEGREE = 2


def _q(value):
    if type(value) not in (int, Fraction):
        raise AdmissionError("exact rational required")
    return Fraction(value)


@dataclass(frozen=True)
class Poly:
    coefficients: tuple[Fraction, ...]

    def __post_init__(self):
        if type(self.coefficients) is not tuple or len(self.coefficients) > MAX_DEGREE + 1:
            raise AdmissionError("unsupported polynomial degree")
        values = tuple(_q(c) for c in self.coefficients) or (Fraction(0),)
        while len(values) > 1 and values[-1] == 0:
            values = values[:-1]
        object.__setattr__(self, "coefficients", values)

    def at(self, point: Fraction) -> Fraction:
        point = _q(point)
        result = Fraction(0)
        for coefficient in reversed(self.coefficients):
            result = result * point + coefficient
        return result

    def __add__(self, other: Poly) -> Poly:
        if type(other) is not Poly:
            raise AdmissionError("polynomial required")
        return Poly(tuple((self.coefficients[i] if i < len(self.coefficients) else 0) +
                          (other.coefficients[i] if i < len(other.coefficients) else 0)
                          for i in range(max(len(self.coefficients), len(other.coefficients)))))

    def __mul__(self, other: Poly) -> Poly:
        if type(other) is not Poly or len(self.coefficients) + len(other.coefficients) - 2 > MAX_DEGREE:
            raise AdmissionError("unsupported polynomial product degree")
        result = [Fraction(0)] * (len(self.coefficients) + len(other.coefficients) - 1)
        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(other.coefficients):
                result[i + j] += left * right
        return Poly(tuple(result))


ZERO = Poly((Fraction(0),))


@dataclass(frozen=True)
class Points:
    values: tuple[Fraction, ...]

    def __post_init__(self):
        if type(self.values) is not tuple or len(self.values) > MAX_POINTS:
            raise AdmissionError("bounded finite point tuple required")
        values = tuple(_q(value) for value in self.values)
        if values != tuple(sorted(set(values))):
            raise AdmissionError("points must be unique and canonical")
        object.__setattr__(self, "values", values)


@dataclass(frozen=True)
class Family:
    edition: str
    context: str
    domain: Points
    terms: tuple[tuple[Config, Poly], ...]

    def __post_init__(self):
        if (self.edition != EDITION or type(self.context) is not str or not self.context or
                type(self.domain) is not Points or type(self.terms) is not tuple):
            raise AdmissionError("invalid family edition context or domain")
        keys = []
        for graph, poly in self.terms:
            if type(graph) is not Config or graph not in BASIS or type(poly) is not Poly:
                raise AdmissionError("only untagged FG3 polynomials admitted")
            if poly == ZERO or not any(poly.at(t) for t in self.domain.values):
                raise AdmissionError("inactive or zero symbolic term")
            keys.append(graph.identity())
        if keys != sorted(set(keys)):
            raise AdmissionError("family symbolic terms must be canonical")

    @property
    def empty(self) -> bool:
        return not self.domain.values

    def instantiate(self, point: Fraction) -> State:
        point = _q(point)
        if point not in self.domain.values:
            raise AdmissionError("assignment outside family domain")
        return collect([(graph, poly.at(point)) for graph, poly in self.terms])


def family(points: tuple, rows: tuple[tuple[Config, Poly], ...], context: str) -> Family:
    domain = Points(points)
    if type(rows) is not tuple:
        raise AdmissionError("symbolic row tuple required")
    totals: dict[Config, Poly] = {}
    for graph, poly in rows:
        if type(graph) is not Config or graph not in BASIS or type(poly) is not Poly:
            raise AdmissionError("unadmitted family row")
        totals[graph] = totals.get(graph, ZERO) + poly
    canonical = tuple(sorted(((graph, poly) for graph, poly in totals.items()
                              if any(poly.at(t) for t in domain.values)),
                             key=lambda item: item[0].identity()))
    return Family(EDITION, context, domain, canonical)


def restrict(source: Family, points: tuple) -> Family:
    if type(source) is not Family or type(points) is not tuple:
        raise AdmissionError("typed family and point restriction required")
    selected = Points(points)
    kept = tuple(t for t in source.domain.values if t in selected.values)
    return family(kept, source.terms, source.context)


def _union(left: Config, right: Config) -> Config:
    return Config(tuple(sorted(set(left.edges) | set(right.edges))), None)


def shared_union(left: Family, right: Family) -> Family:
    if (type(left) is not Family or type(right) is not Family or
            left.context != right.context or left.domain != right.domain):
        raise AdmissionError("shared composition requires same outer parameter and context")
    rows = tuple((_union(g, h), p * q)
                 for g, p in left.terms for h, q in right.terms)
    return family(left.domain.values, rows, left.context)


@dataclass(frozen=True)
class IndependentPairs:
    left: Family
    right: Family
    assignments: tuple[tuple[Fraction, Fraction, State], ...]


def independent_pairs(left: Family, right: Family) -> IndependentPairs:
    """Local comparison operation; no claim that source CG3 exports this API."""
    if type(left) is not Family or type(right) is not Family:
        raise AdmissionError("two typed families required")
    if len(left.domain.values) * len(right.domain.values) > MAX_POINTS:
        raise AdmissionError("independent assignment product exceeds bound")
    rows = []
    for t in left.domain.values:
        for u in right.domain.values:
            l, r = left.instantiate(t), right.instantiate(u)
            rows.append((t, u, collect([(_union(g, h), a * b)
                                        for g, a in l.terms for h, b in r.terms])))
    return IndependentPairs(left, right, tuple(rows))


@dataclass(frozen=True)
class Realisation:
    status: str
    state: State | None
    assignments: tuple[Fraction, ...]


def realise(source: Family, budget: int) -> Realisation:
    if type(source) is not Family or type(budget) is not int or budget < 0:
        raise AdmissionError("typed family and nonnegative resource bound required")
    if source.empty:
        return Realisation("EMPTY", None, ())
    if len(source.domain.values) > budget:
        return Realisation("RESOURCE_LIMIT", None, ())
    results = tuple((point, source.instantiate(point)) for point in source.domain.values)
    states = {state for _, state in results}
    if len(states) != 1:
        return Realisation("AMBIGUOUS", None, tuple(point for point, _ in results))
    return Realisation("UNIQUE", results[0][1], tuple(point for point, _ in results))
