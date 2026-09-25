"""Provisional FG3 joint-dependence and explicit restriction adapter.

This module extends the graph-only WP5 target; the FG3 source implementation
is used by differential tests alone. No generic E7C joint carrier is claimed.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from eec_q_fg3_b1 import AdmissionError, Config, State, collect


@dataclass(frozen=True)
class Joint:
    arity: int
    terms: tuple[tuple[tuple[Config, ...], Fraction], ...]

    def __post_init__(self) -> None:
        if type(self.arity) is not int or self.arity < 1 or type(self.terms) is not tuple:
            raise AdmissionError("positive joint arity and canonical tuple required")
        keys = []
        for row in self.terms:
            if type(row) is not tuple or len(row) != 2:
                raise AdmissionError("canonical joint row required")
            atoms, coefficient = row
            if (type(atoms) is not tuple or len(atoms) != self.arity
                    or any(type(atom) is not Config for atom in atoms)
                    or type(coefficient) is not Fraction or not coefficient):
                raise AdmissionError("canonical nonzero joint row required")
            keys.append(tuple(atom.identity() for atom in atoms))
        if keys != sorted(set(keys)):
            raise AdmissionError("joint support must be unique and canonical")


def joint(rows: Any, *, arity: int | None = None) -> Joint:
    """Admit every tuple before collection; retain its shared choice."""
    if type(rows) is not list or (arity is not None and (type(arity) is not int or arity < 1)):
        raise AdmissionError("finite joint rows and positive arity required")
    totals: dict[tuple[Config, ...], Fraction] = {}
    for row in rows:
        if type(row) is not tuple or len(row) != 2:
            raise AdmissionError("joint row requires coefficient and tuple")
        coefficient, atoms = row
        if (type(atoms) is not tuple or not atoms
                or any(type(atom) is not Config for atom in atoms)
                or type(coefficient) is not Fraction):
            raise AdmissionError("admitted exact joint row required")
        if arity is None:
            arity = len(atoms)
        if len(atoms) != arity:
            raise AdmissionError("mixed joint arity")
        totals[atoms] = totals.get(atoms, Fraction(0)) + coefficient
    if arity is None:
        raise AdmissionError("zero joint requires declared arity")
    return Joint(arity, tuple(sorted(((atoms, c) for atoms, c in totals.items() if c),
                                     key=lambda pair: tuple(a.identity() for a in pair[0]))))


def independent(left: State, right: State) -> Joint:
    if type(left) is not State or type(right) is not State:
        raise AdmissionError("typed graph states required")
    return joint([(a * b, (x, y)) for x, a in left.terms for y, b in right.terms], arity=2)


def marginal(source: Joint, coordinate: int) -> State:
    if type(source) is not Joint or type(coordinate) is not int or not 0 <= coordinate < source.arity:
        raise AdmissionError("joint and in-range coordinate required")
    return collect([(atoms[coordinate], c) for atoms, c in source.terms])


@dataclass(frozen=True)
class JointOutcome:
    tag: str
    value: State | None = None

    def __post_init__(self) -> None:
        if not ((self.tag == "success" and type(self.value) is State)
                or (self.tag == "domain_error" and self.value is None)):
            raise AdmissionError("invalid joint outcome tag or payload")


def join_union(source: Joint) -> JointOutcome:
    """FG3 union intentionally shares A/B/C; incompatible tags fail as a whole."""
    if type(source) is not Joint or source.arity != 2:
        raise AdmissionError("binary joint required")
    images: list[tuple[Config, Fraction]] = []
    for (left, right), coefficient in source.terms:
        if left.tag != right.tag:
            return JointOutcome("domain_error")
        images.append((Config(tuple(set(left.edges) | set(right.edges)), left.tag), coefficient))
    return JointOutcome("success", collect(images))


def restrict_absent(edge: str, source: State) -> tuple[State, State]:
    """Return retained and excluded states; restriction is not strict join."""
    if type(edge) is not str or edge not in {"AB", "AC", "BC"} or type(source) is not State:
        raise AdmissionError("registered edge and typed state required")
    retained, excluded = [], []
    for atom, coefficient in source.terms:
        (excluded if edge in atom.edges else retained).append((atom, coefficient))
    return collect(retained), collect(excluded)


def restrict_joint_absent(edge: str, coordinate: int, source: Joint) -> tuple[Joint, Joint]:
    """Partition canonical support directly, preserving its order and coefficients."""
    if (type(edge) is not str or edge not in {"AB", "AC", "BC"}
            or type(source) is not Joint or type(coordinate) is not int
            or not 0 <= coordinate < source.arity):
        raise AdmissionError("registered edge, coordinate and typed joint required")
    # A filtered subsequence of a canonical Joint is already sorted, unique,
    # typed and nonzero. Construct both children directly; re-collection could
    # otherwise hide a change to the selected coefficients or row order.
    retained = tuple((atoms, c) for atoms, c in source.terms
                     if edge not in atoms[coordinate].edges)
    excluded = tuple((atoms, c) for atoms, c in source.terms
                     if edge in atoms[coordinate].edges)
    return Joint(source.arity, retained), Joint(source.arity, excluded)


def joint_signature(source: Joint) -> tuple[tuple[tuple[Any, ...], int, int], ...]:
    return tuple((tuple(atom.identity() for atom in atoms), c.numerator, c.denominator)
                 for atoms, c in source.terms)
