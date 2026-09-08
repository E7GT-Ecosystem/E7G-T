#!/usr/bin/env python3
"""E7G-T CFS/0.1, CG3/0.1 combined family-state prototype.

Authors: Alexander Gregory Wingate and Oleksandr Razinkov.
Specification example, CC BY-SA 4.0.
Python 3.10+, standard library only. Keep this file beside the SF and EEC
companions. Run it to execute the demonstration and checks.

The outer value is an SF-style exact symbolic family. Each member of that
family is an EEC-Q/FG3 finite rational state. This is a bounded reference
model, not a general solver, compiler, quantum state model or CAD kernel.
"""

from dataclasses import dataclass
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import hashlib
import json
import sys


KERNEL = "0.12-experimental"
PROFILE = "CFS/0.1"
MODEL = "CG3/0.1"
HERE = Path(__file__).resolve().parent


def _load(name, filename):
    spec = spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load required companion {filename}")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sf = _load("e7gt_sf_v01", "E7G-T_Symbolic_Families_v0.1.py")
eec = _load("e7gt_eec_v012", "E7G-T_v0.12_Executable_Examples.py")

Poly = sf.Poly
Interval = sf.Interval
Points = sf.Points
Graph = eec.Graph
State = eec.State
Rule = eec.Rule


class InvalidInput(ValueError):
    pass


class DomainError(ValueError):
    pass


class Unsupported(ValueError):
    pass


class ResourceLimit(ValueError):
    pass


def _domain_key(domain):
    if isinstance(domain, Interval):
        return ("interval", sf.qstr(domain.lo), sf.qstr(domain.hi),
                domain.left_closed, domain.right_closed)
    if isinstance(domain, Points):
        return ("points", tuple(sf.qstr(t) for t in domain.values))
    raise InvalidInput("CG3 requires an IC/0.1 Interval or Points domain")


def _active(poly, domain):
    if poly == Poly((0,)):
        return False
    if isinstance(domain, Interval):
        return domain.lo < domain.hi or domain.contains(domain.lo)
    return any(poly.at(t) != 0 for t in domain.values)


def _canonical_terms(domain, rows):
    totals = {}
    for atom, coefficient in rows:
        eec.key(atom)
        if not isinstance(coefficient, Poly):
            coefficient = Poly((coefficient,))
        totals[atom] = totals.get(atom, Poly((0,))) + coefficient
    return tuple(sorted(((atom, poly) for atom, poly in totals.items()
                         if _active(poly, domain)), key=lambda row: eec.key(row[0])))


@dataclass(frozen=True)
class StateFamily:
    """A finite symbolic description t -> finite EEC-Q state."""

    domain: object
    terms: tuple
    context: str = "CG3/0.1"

    def __post_init__(self):
        try:
            domain = sf.normal_domain(self.domain)
        except sf.InvalidInput as exc:
            raise InvalidInput(str(exc)) from exc
        _domain_key(domain)
        if type(self.terms) is not tuple:
            raise InvalidInput("state-family terms must be a tuple")
        if type(self.context) is not str or not self.context or len(self.context) > 256:
            raise InvalidInput("bounded nonempty context required")
        canonical = _canonical_terms(domain, self.terms)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "terms", canonical)

    @property
    def empty(self):
        return isinstance(self.domain, Points) and not self.domain.values

    def instantiate(self, t):
        t = sf.q(t)
        if not self.domain.contains(t):
            raise InvalidInput("assignment outside state-family domain")
        return eec.state(*((poly.at(t), atom) for atom, poly in self.terms))

    def restrict(self, domain):
        return StateFamily(sf.intersect(self.domain, domain), self.terms, self.context)

    def add(self, other):
        _same_outer(self, other)
        return StateFamily(self.domain, self.terms + other.terms, self.context)

    def scale(self, coefficient):
        coefficient = coefficient if isinstance(coefficient, Poly) else Poly((coefficient,))
        return StateFamily(self.domain,
                           tuple((atom, coefficient * poly) for atom, poly in self.terms),
                           self.context)

    def transform(self, rule):
        if not isinstance(rule, Rule):
            raise InvalidInput("registered FG3 Rule required")
        images = []
        for atom, poly in self.terms:
            try:
                images.append((rule.apply(atom), poly))
            except eec.DomainError as exc:
                raise DomainError(f"rule is not total on the admitted family: {exc}") from exc
        return StateFamily(self.domain, tuple(images), self.context)

    def extend_fixed(self, fixed, mode="union"):
        if not isinstance(fixed, State):
            raise InvalidInput("fixed inner EEC state required")
        if mode not in ("union", "pair"):
            raise InvalidInput("CG3 supports union or pair extension")
        rows = []
        for left, poly in self.terms:
            for right, coefficient in fixed.terms:
                try:
                    target = (eec.union_graphs(left, right) if mode == "union"
                              else eec.Assembly(left, right, "uses"))
                except eec.DomainError as exc:
                    raise DomainError(f"extension is not total on the admitted family: {exc}") from exc
                rows.append((target, poly * coefficient))
        return StateFamily(self.domain, tuple(rows), self.context)

    def shared_union(self, other):
        """Pointwise inner product and graph union using the same outer t."""
        _same_outer(self, other)
        rows = []
        for left, p in self.terms:
            for right, q in other.terms:
                try:
                    target = eec.union_graphs(left, right)
                except eec.DomainError as exc:
                    raise DomainError(f"shared union is not total: {exc}") from exc
                rows.append((target, p * q))
        return StateFamily(self.domain, tuple(rows), self.context)

    def fingerprint(self):
        raw = json.dumps(to_record(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()


def _same_outer(left, right):
    if not isinstance(right, StateFamily):
        raise InvalidInput("StateFamily required")
    if _domain_key(left.domain) != _domain_key(right.domain) or left.context != right.context:
        raise InvalidInput("shared composition requires the same pinned outer domain and context")


@dataclass(frozen=True)
class Observable:
    """A rational linear functional on the inner graph-state coefficients."""

    name: str
    weights: tuple
    direction: str = "max"

    def __post_init__(self):
        if type(self.name) is not str or not self.name or self.direction not in ("min", "max"):
            raise InvalidInput("observable requires a name and min/max direction")
        if type(self.weights) is not tuple:
            raise InvalidInput("observable weights must be a tuple")
        totals = {}
        for atom, weight in self.weights:
            eec.key(atom)
            weight = sf.q(weight)
            totals[atom] = totals.get(atom, Fraction(0)) + weight
        object.__setattr__(self, "weights", tuple(sorted(
            ((atom, weight) for atom, weight in totals.items() if weight),
            key=lambda row: eec.key(row[0]))))

    def expression(self, family):
        weights = dict(self.weights)
        result = Poly((0,))
        for atom, poly in family.terms:
            result = result + poly * weights.get(atom, Fraction(0))
        return result


def coefficient(atom, direction="max"):
    return Observable(f"coefficient:{eec.key(atom)}", ((atom, Fraction(1)),), direction)


@dataclass(frozen=True)
class FamilyQuote:
    payload: StateFamily

    def __post_init__(self):
        if not isinstance(self.payload, StateFamily):
            raise InvalidInput("family-state quote requires StateFamily")


@dataclass(frozen=True)
class Realisation:
    status: str
    source: StateFamily
    residual: StateFamily | None
    state: State | None = None
    witnesses: tuple = ()
    scores: tuple = ()
    reason: str = ""


def _inspect_state_image(family, budget):
    if isinstance(family.domain, Points):
        points = family.domain.values
        varying = False
    else:
        varying = any(poly.degree > 0 for _, poly in family.terms)
        degree = max((poly.degree for _, poly in family.terms), default=0)
        count = max(2, degree + 1) if varying else 1
        points = tuple(sf.q(family.domain.lo +
                            (family.domain.hi - family.domain.lo) * Fraction(i + 1, count + 1))
                       for i in range(count))
    if len(points) > budget:
        raise ResourceLimit("state-image witness candidate limit")
    found = {}
    for t in points:
        state = family.instantiate(t)
        found.setdefault(state, t)
        if len(found) == 2:
            return None, tuple((state, witness) for state, witness in found.items())
    if varying:
        raise AssertionError("nonconstant coefficient failed exact variation witness bound")
    if not found:
        raise AssertionError("nonempty family had no state witness")
    state = next(iter(found))
    return state, ((state, found[state]),)


def realise(family, *objectives, max_candidates=4096):
    if not isinstance(family, StateFamily) or any(not isinstance(o, Observable) for o in objectives):
        raise InvalidInput("StateFamily and Observable objects required")
    if type(max_candidates) is not int or max_candidates < 1:
        raise InvalidInput("positive candidate limit required")
    if len(objectives) > 32:
        raise InvalidInput("at most 32 objectives")
    if family.empty:
        return Realisation("EMPTY", family, family, reason="outer domain is empty")
    current, scores = family, []
    try:
        for objective in objectives:
            expression = objective.expression(current)
            try:
                domain, bound, attained = sf.argopt(
                    expression, current.domain, objective.direction, max_candidates)
            except sf.Unsupported as exc:
                raise Unsupported(str(exc)) from exc
            except sf.ResourceLimit as exc:
                raise ResourceLimit(str(exc)) from exc
            scores.append((objective.name, objective.direction, bound, attained))
            current = current.restrict(domain)
            if not attained:
                return Realisation("UNATTAINED", family, current, scores=tuple(scores),
                                   reason="exact bound exists but is not attained")
        state, witnesses = _inspect_state_image(current, max_candidates)
        return Realisation("UNIQUE" if state is not None else "AMBIGUOUS",
                           family, current, state, witnesses, tuple(scores),
                           "one inner state in the residual image" if state is not None
                           else "at least two distinct residual inner states")
    except Unsupported as exc:
        return Realisation("UNSUPPORTED", family, None, scores=tuple(scores), reason=str(exc))
    except ResourceLimit as exc:
        return Realisation("RESOURCE_LIMIT", family, None, scores=tuple(scores), reason=str(exc))


def _graph_record(graph):
    return {"edges": list(graph.edges), "tag": graph.tag}


def _graph_from_record(record):
    if type(record) is not dict or set(record) != {"edges", "tag"} or type(record["edges"]) is not list:
        raise InvalidInput("invalid graph record")
    return Graph(tuple(record["edges"]), record["tag"])


def to_record(family):
    kind = _domain_key(family.domain)
    domain = ({"kind": "interval", "lo": kind[1], "hi": kind[2],
               "left_closed": kind[3], "right_closed": kind[4]}
              if kind[0] == "interval" else {"kind": "points", "values": list(kind[1])})
    return {"kernel": KERNEL, "profile": PROFILE, "model": MODEL,
            "context": family.context, "domain": domain,
            "terms": [{"config": _graph_record(atom),
                       "coefficient": [sf.qstr(c) for c in poly.coefficients]}
                      for atom, poly in family.terms]}


def from_record(record):
    required = {"kernel", "profile", "model", "context", "domain", "terms"}
    if type(record) is not dict or set(record) != required:
        raise InvalidInput("invalid combined-family record")
    if (record["kernel"], record["profile"], record["model"]) != (KERNEL, PROFILE, MODEL):
        raise InvalidInput("unsupported combined-profile version")
    d = record["domain"]
    if type(d) is not dict:
        raise InvalidInput("domain record required")
    if d.get("kind") == "interval" and set(d) == {"kind", "lo", "hi", "left_closed", "right_closed"}:
        domain = Interval(sf.qparse(d["lo"]), sf.qparse(d["hi"]),
                          d["left_closed"], d["right_closed"])
    elif d.get("kind") == "points" and set(d) == {"kind", "values"} and type(d["values"]) is list:
        domain = Points(tuple(sf.qparse(x) for x in d["values"]))
    else:
        raise InvalidInput("unsupported domain record")
    if type(record["terms"]) is not list or len(record["terms"]) > 64:
        raise InvalidInput("bounded term array required")
    rows = []
    for row in record["terms"]:
        if type(row) is not dict or set(row) != {"config", "coefficient"} or type(row["coefficient"]) is not list:
            raise InvalidInput("invalid symbolic term record")
        rows.append((_graph_from_record(row["config"]),
                     Poly(tuple(sf.qparse(c) for c in row["coefficient"]))))
    return StateFamily(domain, tuple(rows), record["context"])


def state_record(state):
    return [{"config": _graph_record(atom), "coefficient": sf.qstr(value)}
            for atom, value in state.terms]


def result_record(result):
    return {"status": result.status, "source_id": result.source.fingerprint(),
            "residual": None if result.residual is None else to_record(result.residual),
            "state": None if result.state is None else state_record(result.state),
            "scores": [{"name": n, "direction": d, "bound": sf.qstr(v), "attained": a}
                       for n, d, v, a in result.scores],
            "witnesses": [{"t": sf.qstr(t), "state": state_record(state)}
                          for state, t in result.witnesses], "reason": result.reason}


def run_checks():
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def rejects(name, operation, expected=InvalidInput):
        try:
            operation()
        except expected:
            checks.append(name)
        else:
            raise AssertionError(name)

    t = Poly((0, 1))
    one_minus_t = Poly((1, -1))
    empty = Graph()
    ab = Graph(("AB",))
    ac = Graph(("AC",))
    bc = Graph(("BC",))
    domain = Interval(0, 1)

    family = StateFamily(domain, ((empty, t), (ab, one_minus_t)))
    check("outer family retains two symbolic inner terms", len(family.terms) == 2)
    check("left endpoint instantiates exact EEC state", family.instantiate(0) == eec.unit(ab))
    check("right endpoint instantiates exact EEC state", family.instantiate(1) == eec.unit(empty))
    check("interior instantiation uses rational coefficients",
          family.instantiate(Fraction(1, 2)) == eec.state((Fraction(1, 2), empty),
                                                          (Fraction(1, 2), ab)))
    check("unresolved family is ambiguous", realise(family).status == "AMBIGUOUS")

    choose_empty = realise(family, coefficient(empty))
    check("observable realisation is unique", choose_empty.status == "UNIQUE")
    check("observable selects the winning inner state", choose_empty.state == eec.unit(empty))
    check("observable records exact optimum", choose_empty.scores[0][2] == 1)
    choose_ab = realise(family, coefficient(ab))
    check("opposite observable selects other endpoint", choose_ab.state == eec.unit(ab))

    mapped = family.transform(Rule("add", "AB"))
    check("pushforward collects equal configuration images", len(mapped.terms) == 1)
    check("symbolic coefficients combine before instantiation", mapped.terms[0][1] == Poly((1,)))
    check("constant mapped state realises without objectives", realise(mapped).state == eec.unit(ab))
    check("pointwise pushforward law",
          mapped.instantiate(Fraction(1, 3)) == eec.push(Rule("add", "AB"),
                                                        family.instantiate(Fraction(1, 3))))

    cancelled = StateFamily(domain, ((empty, t), (empty, -t)))
    check("pointwise symbolic cancellation produces zero family", not cancelled.terms)
    check("zero state family has singleton image", realise(cancelled).state == State())

    restricted = family.restrict(Points((Fraction(1, 2),)))
    check("restriction preserves exact pointwise state", realise(restricted).status == "UNIQUE")
    check("restriction result is mixed inner state",
          realise(restricted).state == family.instantiate(Fraction(1, 2)))
    check("empty outer restriction remains distinct from zero inner state",
          realise(family.restrict(Points(()))).status == "EMPTY")
    degenerate_open = StateFamily(Interval(0, 0, False, False), ((empty, Poly((1,))),))
    check("degenerate open interval normalises to empty outer family",
          realise(degenerate_open).status == "EMPTY")

    open_family = StateFamily(Interval(0, 1, True, False), ((empty, t),))
    check("open optimum is unattained", realise(open_family, coefficient(empty)).status == "UNATTAINED")
    constant = StateFamily(domain, ((ac, Poly((2,))),))
    check("constant inner state over infinite outer domain is unique",
          realise(constant).state == eec.state((2, ac)))

    fixed_extended = family.extend_fixed(eec.unit(ac), "union")
    check("fixed extension acts pointwise",
          fixed_extended.instantiate(Fraction(1, 2)) ==
          eec.join(eec.independent(family.instantiate(Fraction(1, 2)), eec.unit(ac))))

    left = StateFamily(domain, ((empty, t), (ab, one_minus_t)))
    right = StateFamily(domain, ((ac, t), (bc, one_minus_t)))
    shared = left.shared_union(right)
    check("shared composition uses one outer parameter", shared.instantiate(0) == eec.unit(Graph(("AB", "BC"))))
    check("shared composition right endpoint", shared.instantiate(1) == eec.unit(ac))
    expected_mid = eec.join(eec.independent(left.instantiate(Fraction(1, 2)),
                                             right.instantiate(Fraction(1, 2))))
    check("shared composition equals pointwise EEC extension", shared.instantiate(Fraction(1, 2)) == expected_mid)
    check("shared coefficients multiply as polynomials",
          any(poly.degree == 2 for _, poly in shared.terms))

    summed = family.add(StateFamily(domain, ((empty, one_minus_t), (ab, t))))
    check("family addition is pointwise", summed.instantiate(Fraction(2, 5)) ==
          eec.add(family.instantiate(Fraction(2, 5)),
                  StateFamily(domain, ((empty, one_minus_t), (ab, t))).instantiate(Fraction(2, 5))))
    check("symbolic scaling is pointwise", family.scale(t).instantiate(Fraction(1, 2)) ==
          eec.scale(Fraction(1, 2), family.instantiate(Fraction(1, 2))))

    record = to_record(shared)
    check("canonical interchange round trip", from_record(record) == shared)
    check("canonical fingerprint round trip", from_record(record).fingerprint() == shared.fingerprint())
    check("family quote retains whole combined object", FamilyQuote(shared).payload is shared)

    two_stage = StateFamily(Interval(-1, 1), ((empty, Poly((1, 0, -1))),
                                              (ab, Poly((0, 1, 1)))))
    result = realise(two_stage, coefficient(empty), coefficient(ab))
    check("lexicographic objectives are supported", result.status == "UNIQUE")
    check("first objective fixes its winner before second", result.state == eec.unit(empty))

    partial = StateFamily(domain, ((ab, Poly((1,))),))
    rejects("partial rule is rejected over active family",
            lambda: partial.transform(Rule("require_absent", "AB")), DomainError)
    inactive = StateFamily(Points((0,)), ((ab, t), (empty, Poly((1,)))))
    check("inactive finite-domain term is removed", len(inactive.terms) == 1)
    check("removed inactive term causes no false domain error",
          inactive.transform(Rule("require_absent", "AB")).instantiate(0) == eec.unit(empty))
    rejects("shared composition rejects different outer domains",
            lambda: family.shared_union(StateFamily(Interval(0, 2), ((ac, t),))))
    rejects("assignment outside domain is rejected", lambda: family.instantiate(2))
    rejects("non-rational symbolic coefficient is rejected", lambda: StateFamily(domain, ((empty, 0.5),)), sf.InvalidInput)
    rejects("malformed interchange record is rejected", lambda: from_record({}))

    demonstration = {
        "source": to_record(family),
        "source_at_half": state_record(family.instantiate(Fraction(1, 2))),
        "realisation": result_record(choose_empty),
        "pushforward": to_record(mapped),
        "shared_composition": to_record(shared),
        "shared_at_half": state_record(shared.instantiate(Fraction(1, 2))),
    }
    return checks, demonstration


if __name__ == "__main__":
    checks, demonstration = run_checks()
    print(json.dumps({"kernel": KERNEL, "profile": PROFILE, "model": MODEL,
                      "python": sys.version.split()[0], "passed": len(checks),
                      "checks": checks, "demonstration": demonstration},
                     indent=2, sort_keys=True))
