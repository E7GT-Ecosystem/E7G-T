"""FG3 graph-pair and explicit wiring-choice joins for the WP5 adapter.

Graph identities are fixed A/B/C; an Assembly stores its two whole operands
and the admitted relation. This is not a general E7C gluing interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from eec_q_fg3_b1 import AdmissionError, Config
from eec_q_fg3_joint_b1 import Joint

RELATIONS = frozenset(("uses", "contains"))


@dataclass(frozen=True)
class Assembly:
    left: Config
    right: Config
    relation: str = "uses"

    def __post_init__(self) -> None:
        if (type(self.left) is not Config or type(self.right) is not Config
                or type(self.relation) is not str or self.relation not in RELATIONS):
            raise AdmissionError("FG3 graph assembly requires two graphs and a registered relation")

    def identity(self) -> tuple:
        return ("assembly", self.relation, self.left.identity(), self.right.identity())


@dataclass(frozen=True)
class AssemblyState:
    terms: tuple[tuple[Assembly, Fraction], ...]

    def __post_init__(self) -> None:
        if type(self.terms) is not tuple:
            raise AdmissionError("canonical assembly tuple required")
        keys = []
        for row in self.terms:
            if (type(row) is not tuple or len(row) != 2
                    or type(row[0]) is not Assembly or type(row[1]) is not Fraction or not row[1]):
                raise AdmissionError("nonzero exact assembly row required")
            keys.append(row[0].identity())
        if keys != sorted(set(keys)):
            raise AdmissionError("assembly support must be unique and canonical")


def collect_assemblies(rows: list[tuple[Assembly, Fraction]]) -> AssemblyState:
    if type(rows) is not list:
        raise AdmissionError("finite assembly row list required")
    totals: dict[Assembly, Fraction] = {}
    for row in rows:
        if (type(row) is not tuple or len(row) != 2
                or type(row[0]) is not Assembly or type(row[1]) is not Fraction):
            raise AdmissionError("admitted assembly and exact coefficient required")
        assembly, coefficient = row
        totals[assembly] = totals.get(assembly, Fraction(0)) + coefficient
    return AssemblyState(tuple(sorted(((a, c) for a, c in totals.items() if c),
                                      key=lambda pair: pair[0].identity())))


@dataclass(frozen=True)
class AssemblyOutcome:
    tag: str
    value: AssemblyState | None = None

    def __post_init__(self) -> None:
        if not ((self.tag == "success" and type(self.value) is AssemblyState)
                or (self.tag == "domain_error" and self.value is None)):
            raise AdmissionError("invalid assembly outcome")


def join_pair(source: Joint) -> AssemblyOutcome:
    """Preserve pair dependence and multiply no extra coefficients."""
    if type(source) is not Joint or source.arity != 2:
        raise AdmissionError("binary graph joint required")
    return AssemblyOutcome("success", collect_assemblies(
        [(Assembly(left, right), c) for (left, right), c in source.terms]))


def join_wire_choice(source: Joint) -> AssemblyOutcome:
    """Invalid wiring in any supported triple fails the entire joint."""
    if type(source) is not Joint or source.arity != 3:
        raise AdmissionError("ternary graph joint required")
    images: list[tuple[Assembly, Fraction]] = []
    for (left, right, wiring), coefficient in source.terms:
        if wiring.edges or wiring.tag not in RELATIONS:
            return AssemblyOutcome("domain_error")
        images.append((Assembly(left, right, wiring.tag), coefficient))
    return AssemblyOutcome("success", collect_assemblies(images))


def assembly_signature(source: AssemblyState) -> tuple:
    return tuple((assembly.identity(), c.numerator, c.denominator)
                 for assembly, c in source.terms)
