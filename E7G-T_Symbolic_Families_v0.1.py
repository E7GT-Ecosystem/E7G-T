#!/usr/bin/env python3
"""E7G-T SF/0.1, IC/0.1 exact symbolic-family prototype.

Authors: Alexander Gregory Wingate and Oleksandr Razinkov.
Specification example, CC BY-SA 4.0.
Python 3.10+, standard library. Run to execute the demonstration and checks.
No point grid, random search, external solver, service or hardware is used.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
import hashlib
import json
import sys

PROFILE = "SF/0.1"
MODEL = "IC/0.1"
MAX_DEGREE = 8
MAX_POINTS = 1024


class InvalidInput(ValueError):
    pass


class Unsupported(ValueError):
    pass


class ResourceLimit(ValueError):
    pass


def q(value):
    if type(value) not in (int, Fraction):
        raise InvalidInput("exact int or Fraction required")
    value = Fraction(value)
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > 4096:
        raise ResourceLimit("rational representation limit")
    return value


def qstr(value):
    return f"{value.numerator}/{value.denominator}"


def qparse(value):
    if type(value) is not str or len(value) > 2500:
        raise InvalidInput("bounded reduced fraction string required")
    try:
        result = q(Fraction(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise InvalidInput("invalid rational encoding") from exc
    if qstr(result) != value:
        raise InvalidInput("fraction must be reduced with positive denominator")
    return result


@dataclass(frozen=True)
class Poly:
    # Constant coefficient first. Normalised exact polynomial, degree <= 8.
    coefficients: tuple

    def __post_init__(self):
        if type(self.coefficients) is not tuple or len(self.coefficients) > MAX_DEGREE + 1:
            raise InvalidInput("polynomial tuple exceeds supported degree")
        cs = tuple(q(c) for c in self.coefficients) or (q(0),)
        while len(cs) > 1 and cs[-1] == 0:
            cs = cs[:-1]
        object.__setattr__(self, "coefficients", cs)

    @property
    def degree(self):
        return len(self.coefficients) - 1

    def at(self, t, sign=1):
        value = q(0)
        for c in reversed(self.coefficients):
            value = q(value * t + c)
        return value

    def __add__(self, other):
        other = other if isinstance(other, Poly) else Poly((q(other),))
        a, b = self.coefficients, other.coefficients
        return Poly(tuple((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                          for i in range(max(len(a), len(b)))))

    __radd__ = __add__

    def __neg__(self):
        return Poly(tuple(-c for c in self.coefficients))

    def __sub__(self, other):
        return self + (-(other if isinstance(other, Poly) else Poly((q(other),))))

    def __mul__(self, other):
        other = other if isinstance(other, Poly) else Poly((q(other),))
        if self.degree + other.degree > MAX_DEGREE:
            raise Unsupported("result exceeds polynomial representation degree")
        cs = [q(0)] * (self.degree + other.degree + 1)
        for i, a in enumerate(self.coefficients):
            for j, b in enumerate(other.coefficients):
                cs[i + j] = q(cs[i + j] + a * b)
        return Poly(tuple(cs))

    __rmul__ = __mul__


@dataclass(frozen=True)
class Radical:
    # Canonical non-rational value sign * sqrt(radicand), no free multiplier.
    sign: int
    radicand: Fraction

    def __post_init__(self):
        if type(self.sign) is not int or self.sign not in (-1, 1):
            raise InvalidInput("radical sign required")
        r = q(self.radicand)
        if r <= 0:
            raise InvalidInput("non-rational positive radicand required")
        if isqrt(r.numerator) ** 2 == r.numerator and isqrt(r.denominator) ** 2 == r.denominator:
            raise InvalidInput("rational square roots must be reduced to Fraction")
        object.__setattr__(self, "radicand", r)


def sqrt_value(radicand, sign):
    r = q(radicand)
    if r < 0:
        raise InvalidInput("negative real radicand")
    n, d = isqrt(r.numerator), isqrt(r.denominator)
    if n * n == r.numerator and d * d == r.denominator:
        return q(sign * Fraction(n, d))
    return Radical(sign, r)


@dataclass(frozen=True)
class CircleY:
    def at(self, t, sign):
        return sqrt_value(1 - t * t, sign)


@dataclass(frozen=True)
class Interval:
    lo: Fraction
    hi: Fraction
    left_closed: bool = True
    right_closed: bool = True

    def __post_init__(self):
        object.__setattr__(self, "lo", q(self.lo))
        object.__setattr__(self, "hi", q(self.hi))
        if self.lo > self.hi or type(self.left_closed) is not bool or type(self.right_closed) is not bool:
            raise InvalidInput("invalid interval")

    def contains(self, t):
        return (self.lo < t < self.hi or
                t == self.lo and self.left_closed and (t < self.hi or self.right_closed) or
                t == self.hi and self.right_closed and (t > self.lo or self.left_closed))


@dataclass(frozen=True)
class Points:
    values: tuple = ()

    def __post_init__(self):
        if type(self.values) is not tuple or len(self.values) > MAX_POINTS:
            raise InvalidInput("bounded point tuple required")
        object.__setattr__(self, "values", tuple(sorted(set(q(v) for v in self.values))))

    def contains(self, t):
        return t in self.values


def normal_domain(domain):
    if isinstance(domain, Interval):
        if domain.lo == domain.hi:
            return Points((domain.lo,)) if domain.left_closed and domain.right_closed else Points()
        return domain
    if isinstance(domain, Points):
        return domain
    raise InvalidInput("IC requires a rational bounded interval or finite rational points")


def intersect(a, b):
    a, b = normal_domain(a), normal_domain(b)
    if isinstance(a, Points):
        return Points(tuple(t for t in a.values if b.contains(t)))
    if isinstance(b, Points):
        return intersect(b, a)
    lo, hi = max(a.lo, b.lo), min(a.hi, b.hi)
    if lo > hi:
        return Points()
    return normal_domain(Interval(lo, hi, a.contains(lo) and b.contains(lo), a.contains(hi) and b.contains(hi)))


@dataclass(frozen=True)
class Entity:
    kind: str
    coordinates: tuple


@dataclass(frozen=True)
class Family:
    domain: object
    coordinates: tuple
    signs: tuple = (-1, 1)
    kind: str = "geometric_entity"
    context: str = "E7G-T symbolic geometry"

    def __post_init__(self):
        domain = normal_domain(self.domain)
        if type(self.signs) is not tuple or any(type(s) is not int or s not in (-1, 1) for s in self.signs):
            raise InvalidInput("signs must be -1 or 1")
        if type(self.coordinates) is not tuple or not 1 <= len(self.coordinates) <= 32:
            raise InvalidInput("1 to 32 coordinates required")
        names = []
        for name, expr in self.coordinates:
            if type(name) is not str or not name.isidentifier() or len(name) > 64:
                raise InvalidInput("coordinate identifier required")
            if not isinstance(expr, (Poly, CircleY)):
                raise InvalidInput("unregistered expression; no source-code evaluation")
            names.append(name)
        if len(set(names)) != len(names):
            raise InvalidInput("duplicate coordinate")
        for value in (self.kind, self.context):
            if type(value) is not str or not value or len(value) > 256:
                raise InvalidInput("bounded kind and context strings required")
        if any(isinstance(e, CircleY) for _, e in self.coordinates):
            points = domain.values if isinstance(domain, Points) else (domain.lo, domain.hi)
            if any(t < -1 or t > 1 for t in points):
                raise InvalidInput("circle coordinate requires t in [-1,1]")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "signs", tuple(sorted(set(self.signs))))
        object.__setattr__(self, "coordinates", tuple(sorted(self.coordinates)))

    @property
    def empty(self):
        return not self.signs or isinstance(self.domain, Points) and not self.domain.values

    def field(self, name):
        for k, expr in self.coordinates:
            if k == name:
                return expr
        raise InvalidInput(f"unknown coordinate: {name}")

    def instantiate(self, t, sign=1):
        t = q(t)
        if type(sign) is not int or sign not in self.signs or not self.domain.contains(t):
            raise InvalidInput("assignment outside family")
        return Entity(self.kind, tuple((k, e.at(t, sign)) for k, e in self.coordinates))

    def with_domain(self, domain):
        return Family(domain, self.coordinates, self.signs, self.kind, self.context)

    def extend(self, **fields):
        if set(fields) & {k for k, _ in self.coordinates}:
            raise InvalidInput("extend cannot overwrite a coordinate; use transform")
        return Family(self.domain, self.coordinates + tuple(fields.items()), self.signs, self.kind, self.context)

    def transform(self, **fields):
        return Family(self.domain, tuple(fields.items()), self.signs, self.kind, self.context)

    def project(self, *names):
        return Family(self.domain, tuple((k, self.field(k)) for k in names), self.signs, self.kind, self.context)

    def restrict(self, domain=None, signs=None):
        d = self.domain if domain is None else intersect(self.domain, domain)
        if signs is not None and (type(signs) is not tuple or any(type(s) is not int or s not in (-1, 1) for s in signs)):
            raise InvalidInput("invalid sign restriction")
        s = self.signs if signs is None else tuple(k for k in self.signs if k in signs)
        return Family(d, self.coordinates, s, self.kind, self.context)

    def fingerprint(self):
        text = json.dumps(to_record(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode()).hexdigest()


@dataclass(frozen=True)
class FamilyQuote:
    payload: Family

    def __post_init__(self):
        if not isinstance(self.payload, Family):
            raise InvalidInput("family quote requires Family")


@dataclass(frozen=True)
class FamilyView:
    source: Family
    selected_fields: tuple

    def __post_init__(self):
        if not isinstance(self.source, Family) or type(self.selected_fields) is not tuple:
            raise InvalidInput("view requires a Family and a field tuple")
        for name in self.selected_fields:
            self.source.field(name)


@dataclass(frozen=True)
class Objective:
    field: str
    direction: str = "max"

    def __post_init__(self):
        if type(self.field) is not str or self.direction not in ("min", "max"):
            raise InvalidInput("objective requires field and min/max direction")


@dataclass(frozen=True)
class Realisation:
    status: str
    source: Family
    residual: Family | None
    entity: Entity | None = None
    witnesses: tuple = ()
    scores: tuple = ()
    reason: str = ""


def argopt(poly, domain, direction, budget):
    """Exact optimisation of degree <=2 on intervals, any supported degree on points."""
    if not isinstance(poly, Poly):
        raise Unsupported("objective must be a polynomial coordinate in IC/0.1")
    choose = max if direction == "max" else min
    if isinstance(domain, Points):
        if len(domain.values) > budget:
            raise ResourceLimit("candidate limit")
        values = [(t, poly.at(t)) for t in domain.values]
        best = choose(v for _, v in values)
        return Points(tuple(t for t, v in values if v == best)), best, True
    if poly.degree == 0:
        return domain, poly.at(domain.lo), True
    if poly.degree > 2:
        raise Unsupported("continuous optimisation above quadratic degree is not implemented")
    candidates = {domain.lo, domain.hi}
    if poly.degree == 2:
        _, b, a = poly.coefficients
        critical = q(-b / (2 * a))
        if domain.lo <= critical <= domain.hi:
            candidates.add(critical)
    if len(candidates) > budget:
        raise ResourceLimit("candidate limit")
    best = choose(poly.at(t) for t in candidates)
    winners = Points(tuple(t for t in candidates if domain.contains(t) and poly.at(t) == best))
    return winners, best, bool(winners.values)


def inspect_image(family, budget):
    """Determine uniqueness; witness sampling is used only after variation is proved."""
    domain = family.domain
    if isinstance(domain, Points):
        ts = domain.values
        varying_interval = False
    else:
        varying_interval = any(isinstance(e, CircleY) or e.degree > 0 for _, e in family.coordinates)
        degree = max((e.degree for _, e in family.coordinates if isinstance(e, Poly)), default=0)
        n = max(3, degree + 1) if varying_interval else 1
        ts = tuple(q(domain.lo + (domain.hi - domain.lo) * Fraction(i + 1, n + 1)) for i in range(n))
    if len(ts) * len(family.signs) > budget:
        raise ResourceLimit("entity-witness candidate limit")
    found = {}
    for t in ts:
        for sign in family.signs:
            entity = family.instantiate(t, sign)
            found.setdefault(entity, (t, sign))
            if len(found) == 2:
                return None, tuple((e, w) for e, w in found.items())
    if varying_interval:
        raise AssertionError("nonconstant admitted coordinate failed variation witness bound")
    if not found:
        raise AssertionError("nonempty family had no entity witness")
    entity = next(iter(found))
    return entity, ((entity, found[entity]),)


def realise(family, *objectives, max_candidates=4096):
    if not isinstance(family, Family) or any(not isinstance(o, Objective) for o in objectives):
        raise InvalidInput("Family and Objective objects required")
    if type(max_candidates) is not int or max_candidates < 1:
        raise InvalidInput("positive candidate limit required")
    if len(objectives) > 32:
        raise InvalidInput("at most 32 objectives")
    for objective in objectives:
        family.field(objective.field)
    if family.empty:
        return Realisation("EMPTY", family, family, reason="input family has no admitted assignments")
    current, scores = family, []
    try:
        for objective in objectives:
            domain, bound, attained = argopt(current.field(objective.field), current.domain,
                                             objective.direction, max_candidates)
            scores.append((objective.field, objective.direction, bound, attained))
            current = current.with_domain(domain)
            if not attained:
                return Realisation("UNATTAINED", family, current, scores=tuple(scores),
                                   reason="exact bound exists but no admitted assignment attains it")
        entity, witnesses = inspect_image(current, max_candidates)
        status = "UNIQUE" if entity is not None else "AMBIGUOUS"
        return Realisation(status, family, current, entity, witnesses, tuple(scores),
                           "one entity in the residual image" if entity is not None else "at least two distinct residual entities")
    except Unsupported as exc:
        return Realisation("UNSUPPORTED", family, None, scores=tuple(scores), reason=str(exc))
    except ResourceLimit as exc:
        return Realisation("RESOURCE_LIMIT", family, None, scores=tuple(scores), reason=str(exc))


def to_record(family):
    d = family.domain
    domain = ({"kind": "interval", "lo": qstr(d.lo), "hi": qstr(d.hi),
               "left_closed": d.left_closed, "right_closed": d.right_closed} if isinstance(d, Interval)
              else {"kind": "points", "values": [qstr(t) for t in d.values]})
    coordinates = []
    for name, expr in family.coordinates:
        formula = ({"kind": "polynomial", "coefficients": [qstr(c) for c in expr.coefficients]}
                   if isinstance(expr, Poly) else {"kind": "circle_y"})
        coordinates.append({"name": name, "expression": formula})
    return {"kernel": "0.12-experimental", "profile": PROFILE, "model": MODEL,
            "kind": family.kind, "context": family.context, "domain": domain,
            "signs": list(family.signs), "coordinates": coordinates}


def from_record(record):
    required = {"kernel", "profile", "model", "kind", "context", "domain", "signs", "coordinates"}
    if type(record) is not dict or set(record) != required:
        raise InvalidInput("invalid family record fields")
    if (record["kernel"], record["profile"], record["model"]) != ("0.12-experimental", PROFILE, MODEL):
        raise InvalidInput("unsupported version")
    d = record["domain"]
    if type(d) is not dict:
        raise InvalidInput("domain record required")
    if d.get("kind") == "interval" and set(d) == {"kind", "lo", "hi", "left_closed", "right_closed"}:
        domain = Interval(qparse(d["lo"]), qparse(d["hi"]), d["left_closed"], d["right_closed"])
    elif d.get("kind") == "points" and set(d) == {"kind", "values"} and type(d["values"]) is list and len(d["values"]) <= MAX_POINTS:
        domain = Points(tuple(qparse(t) for t in d["values"]))
    else:
        raise InvalidInput("unsupported domain record")
    if type(record["signs"]) is not list or type(record["coordinates"]) is not list or len(record["coordinates"]) > 32:
        raise InvalidInput("bounded coordinate and sign arrays required")
    coordinates = []
    for row in record["coordinates"]:
        if type(row) is not dict or set(row) != {"name", "expression"} or type(row["expression"]) is not dict:
            raise InvalidInput("invalid coordinate record")
        e = row["expression"]
        if e.get("kind") == "polynomial" and set(e) == {"kind", "coefficients"} and type(e["coefficients"]) is list and len(e["coefficients"]) <= MAX_DEGREE + 1:
            expr = Poly(tuple(qparse(c) for c in e["coefficients"]))
        elif e == {"kind": "circle_y"}:
            expr = CircleY()
        else:
            raise InvalidInput("unsupported expression record")
        coordinates.append((row["name"], expr))
    return Family(domain, tuple(coordinates), tuple(record["signs"]), record["kind"], record["context"])


def value_record(value):
    if isinstance(value, Fraction):
        return {"rational": qstr(value)}
    return {"sign": value.sign, "sqrt": qstr(value.radicand)}


def entity_record(entity):
    return None if entity is None else {"kind": entity.kind,
                                       "coordinates": {k: value_record(v) for k, v in entity.coordinates}}


def result_record(result):
    return {"status": result.status, "source_id": result.source.fingerprint(),
            "residual": None if result.residual is None else to_record(result.residual),
            "entity": entity_record(result.entity), "reason": result.reason,
            "scores": [{"field": f, "direction": d, "bound": qstr(v), "attained": a}
                       for f, d, v, a in result.scores],
            "witnesses": [{"entity": entity_record(e), "t": qstr(t), "sign": s}
                          for e, (t, s) in result.witnesses]}


def circle():
    return Family(Interval(-1, 1), (("x", Poly((0, 1))), ("y", CircleY())))


def run_checks():
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def rejects(name, operation, expected):
        try:
            operation()
        except expected:
            checks.append(name)
        else:
            raise AssertionError(name)

    t = Poly((0, 1))
    source = circle()
    initial_id = source.fingerprint()
    lifted = source.extend(z=2 * t * t - 1)
    answer = realise(lifted, Objective("z"), Objective("x"))
    expected = Entity("geometric_entity", (("x", q(1)), ("y", q(0)), ("z", q(1))))
    check("circle extension and realisation", answer.status == "UNIQUE" and answer.entity == expected)
    check("exact scores", answer.scores == (("z", "max", q(1), True), ("x", "max", q(1), True)))
    check("source family retained", answer.source == lifted and source.fingerprint() == initial_id)
    check("infinite source stays symbolic", isinstance(source.domain, Interval) and len(source.coordinates) == 2)
    check("unique entity despite duplicate chart witnesses", answer.residual.signs == (-1, 1) and answer.residual.domain == Points((1,)))
    tied = realise(lifted, Objective("z"))
    check("ties remain explicit", tied.status == "AMBIGUOUS" and tied.residual.domain == Points((-1, 1)))
    check("tie has two distinct entity witnesses", len({e for e, _ in tied.witnesses}) == 2)
    other = realise(lifted, Objective("z"), Objective("x", "min"))
    check("tie rule determines the selected entity", dict(other.entity.coordinates)["x"] == -1)
    reversed_order = realise(lifted, Objective("x"), Objective("z", "min"))
    first_min_z = realise(lifted, Objective("z", "min"), Objective("x"))
    check("lexicographic order matters", reversed_order.residual.domain != first_min_z.residual.domain)
    check("shared parameters preserve dependencies", first_min_z.residual.domain == Points((0,)) and first_min_z.status == "AMBIGUOUS")
    upper = realise(lifted.restrict(signs=(1,)), Objective("z", "min"))
    check("explicit branch restriction", upper.status == "UNIQUE" and dict(upper.entity.coordinates) == {"x": q(0), "y": q(1), "z": q(-1)})
    for witness in (Fraction(-1), Fraction(-1, 2), Fraction(0), Fraction(1, 2), Fraction(1)):
        e = dict(lifted.instantiate(witness, 1).coordinates)
        y_squared = e["y"].radicand if isinstance(e["y"], Radical) else e["y"] ** 2
        if e["x"] ** 2 + y_squared != 1 or e["z"] != 2 * e["x"] ** 2 - 1:
            raise AssertionError("circle and lift identities")
    check("circle and lift identity witnesses", True)

    family = Family(Interval(-2, 3), (("x", t), ("score", -(t * t) + t)))
    peak = realise(family, Objective("score"))
    check("interior quadratic optimum", peak.status == "UNIQUE" and dict(peak.entity.coordinates)["x"] == Fraction(1, 2))
    check("interior bound is exact", peak.scores[0][2] == Fraction(1, 4))
    open_family = Family(Interval(0, 1, False, False), (("x", t),))
    unattained = realise(open_family, Objective("x"))
    check("unattained supremum is not a result", unattained.status == "UNATTAINED" and unattained.entity is None and unattained.scores[0][2] == 1)
    check("unattained infimum", realise(open_family, Objective("x", "min")).status == "UNATTAINED")
    open_peak = Family(Interval(0, 1, False, False), (("score", -(t * t) + t), ("x", t)))
    check("open domain can have attained interior optimum", realise(open_peak, Objective("score")).status == "UNIQUE")
    one_closed = Family(Interval(-1, 1, True, False), (("x", t), ("score", t * t)))
    edge_winner = realise(one_closed, Objective("score"))
    check("closed endpoint wins when open endpoint ties", edge_winner.status == "UNIQUE" and dict(edge_winner.entity.coordinates)["x"] == -1)
    empty = source.restrict(domain=Interval(2, 3))
    check("empty restriction", realise(empty).status == "EMPTY")
    check("empty sign restriction", realise(source.restrict(signs=())).status == "EMPTY")
    check("degenerate open interval is empty", realise(Family(Interval(1, 1, False, True), (("x", t),))).status == "EMPTY")
    check("interval intersection respects open endpoints", open_family.restrict(Interval(1, 2)).empty)

    constant = Family(Interval(-1, 1), (("answer", Poly((7,))),))
    check("infinitely many assignments can denote one entity", realise(constant).status == "UNIQUE")
    check("unresolved continuum has multiple entities", realise(source).status == "AMBIGUOUS")
    projected = lifted.project("z")
    check("projection changes entity uniqueness", realise(projected, Objective("z")).status == "UNIQUE")
    view = FamilyView(lifted, ("z",))
    check("view preserves source alternatives", view.source == lifted and realise(view.source, Objective("z")).status == "AMBIGUOUS")
    packed = FamilyQuote(lifted)
    check("packing retains the whole family", packed.payload == lifted and not isinstance(packed, Entity))
    rejects("quote has no implicit realisation coercion", lambda: realise(packed), InvalidInput)
    quad = source.restrict(Points((Fraction(1, 2),)), signs=(1,))
    radical_entity = realise(quad).entity
    check("non-rational coordinates remain exact", dict(radical_entity.coordinates)["y"] == Radical(1, Fraction(3, 4)))

    quartic = Family(Interval(-1, 1), (("score", t * t * t * t),))
    check("unsupported continuous objective is explicit", realise(quartic, Objective("score")).status == "UNSUPPORTED")
    check("finite-domain higher-degree objective", realise(quartic.restrict(Points((-1, 0, 1))), Objective("score")).status == "UNIQUE")
    check("radical objective is not silently approximated", realise(source, Objective("y")).status == "UNSUPPORTED")
    limited = realise(lifted, Objective("z"), max_candidates=1)
    check("resource limit is not an empty or successful answer", limited.status == "RESOURCE_LIMIT" and limited.entity is None)
    rejects("floating-point input rejected", lambda: Poly((0.1,)), InvalidInput)
    rejects("coordinate overwrite rejected", lambda: source.extend(x=Poly((5,))), InvalidInput)
    rejects("unregistered expression rejected", lambda: source.extend(z="eval(anything)"), InvalidInput)
    rejects("outside assignment rejected", lambda: source.instantiate(2), InvalidInput)
    rejects("invalid circle domain rejected", lambda: Family(Interval(-2, 2), (("y", CircleY()),)), InvalidInput)
    rejects("unknown objective rejected", lambda: realise(source, Objective("absent")), InvalidInput)
    rejects("invalid sign restriction rejected", lambda: source.restrict(signs=(2,)), InvalidInput)
    rejects("negative candidate limit rejected", lambda: realise(source, max_candidates=-1), InvalidInput)
    check("exact interchange round trip", from_record(json.loads(json.dumps(to_record(lifted)))) == lifted)
    invalid = to_record(lifted)
    invalid["coordinates"][0]["expression"] = {"kind": "host_code", "value": "anything"}
    rejects("import rejects executable strings", lambda: from_record(invalid), InvalidInput)
    rejects("noncanonical rational import rejected", lambda: qparse("2/2"), InvalidInput)
    check("normalised description identity", Poly((1, 0, 0)) == Poly((1,)))

    selected = dict(answer.entity.coordinates)
    next_family = Family(Interval(-1, 1), (("x", selected["x"] + t),
                                         ("y", Poly((selected["y"],))),
                                         ("z", Poly((selected["z"],)))))
    next_result = realise(next_family, Objective("x"))
    check("realised entity seeds a new family", next_result.status == "UNIQUE" and dict(next_result.entity.coordinates)["x"] == 2)
    translated = source.transform(x=2 * t + 1, y=CircleY())
    check("family transformation changes exact geometry", dict(realise(translated, Objective("x")).entity.coordinates)["x"] == 3)
    check("new domain dependency is explicit", next_result.source.fingerprint() != answer.source.fingerprint())
    return {"profile": PROFILE, "model": MODEL, "python": sys.version.split()[0],
            "checks_passed": len(checks), "checks": checks,
            "demo": {"circle": to_record(source), "extended_family": to_record(lifted),
                     "realisation": result_record(answer), "tied_result": result_record(tied),
                     "unattained_result": result_record(unattained),
                     "subsequent_realisation": result_record(next_result)},
            "scope": "Internal tests of exact bounded symbolic rules; no full SF implementation, amplitude semantics, quantum mechanism or performance advantage established."}


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2, ensure_ascii=False))
