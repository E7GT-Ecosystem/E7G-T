#!/usr/bin/env python3
"""E7G-T v0.12 experimental: FG3/0.1 finite example evaluator.

Authors: Alexander Gregory Wingate and Oleksandr Razinkov.
Specification companion, CC BY-SA 4.0.
Python 3.10+, standard library only. Run this file to print its checks.
This is a bounded example model, not a full EEC-Q interpreter or compiler.
FG3 includes fixed-labelled graphs, immutable state quotes and binary assemblies.
Only the registered graph rules below are executable rule descriptions.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
import json
import sys

KERNEL = "0.12-experimental"
PROFILE = "EEC-Q/0.1"
MODEL = "FG3/0.1"
EDGES = frozenset(("AB", "AC", "BC"))


class InvalidInput(ValueError):
    pass


class DomainError(ValueError):
    pass


def rational(x):
    if type(x) not in (int, Fraction):
        raise InvalidInput("exact integer or Fraction required")
    return Fraction(x)


@dataclass(frozen=True)
class Graph:
    edges: tuple = ()
    tag: str | None = None

    def __post_init__(self):
        if not isinstance(self.edges, tuple) or any(
            type(e) is not str or e not in EDGES for e in self.edges
        ):
            raise InvalidInput("FG3 edges must be AB, AC or BC")
        if self.tag is not None and type(self.tag) is not str:
            raise InvalidInput("tag must be a string or null")
        object.__setattr__(self, "edges", tuple(sorted(set(self.edges))))


@dataclass(frozen=True)
class State:
    # Construct through state(); entries are (atom, coefficient).
    terms: tuple = ()

    def __post_init__(self):
        if type(self.terms) is not tuple:
            raise InvalidInput("canonical tuple required")
        keys = []
        for atom, coefficient in self.terms:
            keys.append(key(atom))
            if type(coefficient) is not Fraction or not coefficient:
                raise InvalidInput("canonical nonzero Fraction required")
        if keys != sorted(set(keys)):
            raise InvalidInput("state terms must be unique and canonical")


@dataclass(frozen=True)
class Box:
    payload: State

    def __post_init__(self):
        if not isinstance(self.payload, State):
            raise InvalidInput("this model quotes whole states only")


@dataclass(frozen=True)
class Assembly:
    left: object
    right: object
    relation: str = "uses"

    def __post_init__(self):
        key(self.left)
        key(self.right)
        if self.relation not in ("uses", "contains"):
            raise InvalidInput("unsupported assembly relation")


def key(atom):
    if isinstance(atom, Graph):
        return ("graph", atom.edges, atom.tag is not None, atom.tag or "")
    if isinstance(atom, Box):
        return ("box", tuple((key(a), c.numerator, c.denominator)
                             for a, c in atom.payload.terms))
    if isinstance(atom, Assembly):
        return ("assembly", atom.relation, key(atom.left), key(atom.right))
    raise InvalidInput("unsupported configuration sort")


def state(*rows):
    # Rows are (coefficient, atom); validate each row before collection.
    totals = {}
    for coefficient, atom in rows:
        key(atom)
        coefficient = rational(coefficient)
        totals[atom] = totals.get(atom, Fraction(0)) + coefficient
    return State(tuple(sorted(((a, c) for a, c in totals.items() if c),
                              key=lambda pair: key(pair[0]))))


def unit(atom):
    return state((1, atom))


def add(*states):
    return state(*((c, a) for s in states for a, c in s.terms))


def scale(c, s):
    c = rational(c)
    return state(*((c * d, a) for a, d in s.terms))


@dataclass(frozen=True)
class Rule:
    name: str
    edge: str | None = None

    def __post_init__(self):
        if self.name not in ("add", "remove", "require_absent", "forget_tag", "empty"):
            raise InvalidInput("unregistered rule")
        if self.name in ("add", "remove", "require_absent"):
            if self.edge not in EDGES:
                raise InvalidInput("rule requires one FG3 edge")
        elif self.edge is not None:
            raise InvalidInput("this rule takes no edge parameter")

    def apply(self, atom):
        if not isinstance(atom, Graph):
            raise DomainError("graph rule cannot implicitly enter a quote or assembly")
        edges = set(atom.edges)
        if self.name == "add":
            edges.add(self.edge)
        elif self.name == "remove":
            edges.discard(self.edge)
        elif self.name == "require_absent" and self.edge in edges:
            raise DomainError("required absent edge is present")
        elif self.name == "empty":
            edges.clear()
        tag = None if self.name == "forget_tag" else atom.tag
        return Graph(tuple(sorted(edges)), tag)


def push(rule, s):
    if not isinstance(rule, Rule):
        raise InvalidInput("registered Rule required")
    # Construct all images before returning a canonical result: strict execution.
    images = [(c, rule.apply(a)) for a, c in s.terms]
    return state(*images)


def restrict_absent(edge, s):
    if edge not in EDGES:
        raise InvalidInput("invalid restriction edge")
    retained, excluded = [], []
    for atom, c in s.terms:
        if not isinstance(atom, Graph):
            raise DomainError("graph predicate required")
        (retained if edge not in atom.edges else excluded).append((c, atom))
    return state(*retained), state(*excluded)


def joint(*rows):
    totals = {}
    arity = None
    for coefficient, atoms in rows:
        if type(atoms) is not tuple or not atoms:
            raise InvalidInput("nonempty tuple required")
        if arity is None:
            arity = len(atoms)
        if len(atoms) != arity:
            raise InvalidInput("mixed joint arity")
        for atom in atoms:
            key(atom)
        c = rational(coefficient)
        totals[atoms] = totals.get(atoms, Fraction(0)) + c
    return tuple(sorted(((atoms, c) for atoms, c in totals.items() if c),
                        key=lambda row: tuple(key(a) for a in row[0])))


def independent(s, t):
    return joint(*((a * b, (x, y)) for x, a in s.terms for y, b in t.terms))


def union_graphs(x, y):
    if not isinstance(x, Graph) or not isinstance(y, Graph) or x.tag != y.tag:
        raise DomainError("union requires graphs agreeing on their shared tag")
    # The fixed identities A/B/C intentionally overlap; links deduplicate.
    return Graph(tuple(sorted(set(x.edges) | set(y.edges))), x.tag)


def join(rows, mode="union"):
    if mode not in ("union", "pair", "wire_choice"):
        raise InvalidInput("unregistered join mode")
    images = []
    for atoms, coefficient in rows:
        expected = 3 if mode == "wire_choice" else 2
        if len(atoms) != expected:
            raise DomainError("joint arity differs from join domain")
        x, y = atoms[:2]
        if mode == "union":
            target = union_graphs(x, y)
        elif mode == "pair":
            target = Assembly(x, y, "uses")
        else:
            wiring = atoms[2]
            if not isinstance(wiring, Graph) or wiring.edges or wiring.tag not in ("uses", "contains"):
                raise DomainError("unsupported connection declaration")
            target = Assembly(x, y, wiring.tag)
        images.append((coefficient, target))
    return state(*images)


def marginal(rows, coordinate):
    return state(*((c, atoms[coordinate]) for atoms, c in rows))


def pack(s):
    return Box(s)


def unpack(box):
    if not isinstance(box, Box):
        raise InvalidInput("Box required")
    return box.payload


def inside(rule, box):
    return pack(push(rule, unpack(box)))


def rank(atom):
    if isinstance(atom, Graph):
        return 0
    if isinstance(atom, Box):
        return 1 + max((rank(a) for a, _ in atom.payload.terms), default=0)
    if isinstance(atom, Assembly):
        return max(rank(atom.left), rank(atom.right))
    raise InvalidInput("unsupported atom")


@dataclass(frozen=True)
class View:
    source: State
    displayed_rows: tuple


def edge_view(s):
    if any(not isinstance(a, Graph) for a, _ in s.terms):
        raise DomainError("edge view only supports Graph")
    return View(s, tuple((a.edges, str(c)) for a, c in s.terms))


def dump_graph_state(s):
    if any(not isinstance(a, Graph) for a, _ in s.terms):
        raise DomainError("JSON interchange only supports Graph states")
    return json.dumps({"kernel": KERNEL, "profile": PROFILE, "model": MODEL,
                       "state": [{"coefficient": f"{c.numerator}/{c.denominator}",
                                  "config": {"edges": list(a.edges), "tag": a.tag}}
                                 for a, c in s.terms]}, sort_keys=True)


def load_graph_state(text):
    obj = json.loads(text)
    if not isinstance(obj, dict) or set(obj) - {"kernel", "profile", "model", "context", "inquiry", "state"}:
        raise InvalidInput("invalid top-level record")
    if (obj.get("kernel"), obj.get("profile"), obj.get("model")) != (KERNEL, PROFILE, MODEL):
        raise InvalidInput("version mismatch")
    if type(obj.get("state")) is not list:
        raise InvalidInput("state array required")
    rows = []
    for row in obj["state"]:
        if not isinstance(row, dict) or set(row) != {"coefficient", "config"}:
            raise InvalidInput("invalid term record")
        cfg = row["config"]
        if not isinstance(cfg, dict) or set(cfg) != {"edges", "tag"} or type(cfg["edges"]) is not list:
            raise InvalidInput("invalid graph record")
        atom = Graph(tuple(cfg["edges"]), cfg["tag"])
        raw = row["coefficient"]
        if type(raw) is not str:
            raise InvalidInput("rational string required")
        try:
            coefficient = Fraction(raw)
        except (ValueError, ZeroDivisionError) as exc:
            raise InvalidInput("invalid rational") from exc
        if raw != f"{coefficient.numerator}/{coefficient.denominator}":
            raise InvalidInput("reduced rational encoding required")
        rows.append((coefficient, atom))
    return state(*rows)


def phase_status(rule, basis):
    groups = {}
    for g in basis:
        groups.setdefault(len(g.edges), []).append(g)
    domain_stable, congruent = True, True
    for group in groups.values():
        outcomes = []
        for g in group:
            try:
                outcomes.append(len(rule.apply(g).edges))
            except DomainError:
                outcomes.append(None)
        if any(o is None for o in outcomes) and any(o is not None for o in outcomes):
            domain_stable = False
        if len({o for o in outcomes if o is not None}) > 1:
            congruent = False
    return {"domain_saturated": domain_stable, "result_congruent": congruent}


def run_checks():
    passed = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        passed.append(name)

    def rejects(name, operation, expected):
        try:
            operation()
        except expected:
            passed.append(name)
        else:
            raise AssertionError(name)

    p, q = Graph(("AB", "BC")), Graph(("AC", "BC"))
    empty, triangle = Graph(), Graph(("AB", "AC", "BC"))
    zero = state()
    s = state((1, p), (-1, q))
    ab, ac = Rule("add", "AB"), Rule("add", "AC")
    check("exact configurations stay distinct", len(s.terms) == 2)
    check("empty graph is not zero", unit(empty) != zero)
    check("exact cancellation", state((1, p), (-1, p)) == zero)
    check("fraction arithmetic", state((Fraction(1, 3), p), (Fraction(2, 3), p)) == unit(p))
    check("first extension", push(ab, s) == state((1, p), (-1, triangle)))
    check("second extension cancels", push(ac, push(ab, s)) == zero)
    check("total-map composition", push(ac, push(ab, s)) ==
          state(*((c, ac.apply(ab.apply(a))) for a, c in s.terms)))
    check("total-map linearity", push(ab, add(s, scale(2, unit(q)))) ==
          add(push(ab, s), scale(2, push(ab, unit(q)))))

    tagged = state((1, Graph(p.edges, "first")), (-1, Graph(q.edges, "second")))
    kept = push(ac, push(ab, tagged))
    check("semantic tags preserve distinction", len(kept.terms) == 2)
    check("explicit tag removal cancels", push(Rule("forget_tag"), kept) == zero)
    view = edge_view(kept)
    check("view retains source", view.source == kept and len(view.source.terms) == 2)
    check("identical displayed graphs do not merge", view.displayed_rows[0][0] == view.displayed_rows[1][0])

    require = Rule("require_absent", "AB")
    rejects("strict supported-domain rejection", lambda: push(require, s), DomainError)
    retained, excluded = restrict_absent("AB", s)
    check("restriction preserves signed coefficients", retained == scale(-1, unit(q)) and excluded == unit(p))
    check("restriction accounts for input", add(retained, excluded) == s)
    rejects("unknown node rejected", lambda: Graph(("AD",)), InvalidInput)
    rejects("invalid opposite terms rejected", lambda: state((1, object()), (-1, object())), InvalidInput)
    rejects("invalid zero term rejected", lambda: state((0, object())), InvalidInput)
    rejects("float coefficient rejected", lambda: state((0.1, p)), InvalidInput)

    rnd, sqr = Graph((), "round"), Graph((), "square")
    red, blue = Graph((), "red"), Graph((), "blue")
    shared = joint((2, (rnd, red)), (-1, (sqr, blue)))
    direct = join(shared, "pair")
    wrong = join(independent(marginal(shared, 0), marginal(shared, 1)), "pair")
    check("shared coefficient used once", direct == state((2, Assembly(rnd, red)), (-1, Assembly(sqr, blue))))
    check("marginal product changes dependencies", len(wrong.terms) == 4 and wrong != direct)
    wiring = joint((2, (rnd, red, Graph((), "uses"))),
                   (-1, (rnd, red, Graph((), "contains"))))
    check("joint wiring alternatives", join(wiring, "wire_choice") ==
          state((2, Assembly(rnd, red, "uses")), (-1, Assembly(rnd, red, "contains"))))
    rejects("strict incompatible gluing", lambda: join(joint((1, (p, q)), (1, (rnd, red)))), DomainError)
    check("bilinear independent gluing", join(independent(add(unit(p), unit(q)), unit(empty))) ==
          add(join(independent(unit(p), unit(empty))), join(independent(unit(q), unit(empty)))))

    box = pack(s)
    check("whole-family unpack", unpack(box) == s)
    check("packing is not branchwise distribution", unit(box) != state((1, pack(unit(p))), (-1, pack(unit(q)))))
    box_zero = inside(ac, inside(ab, box))
    check("quoted zero is an entity", unpack(box_zero) == zero and unit(box_zero) != zero)
    outer = Assembly(box, Graph((), "consumer"), "uses")
    check("recursive construction rank", rank(pack(unit(outer))) == 2)
    check("immutable original quote", unpack(box) == s)
    rejects("no implicit quote execution", lambda: push(ab, unit(box)), DomainError)

    all_graphs = [Graph(tuple(es)) for n in range(4) for es in combinations(sorted(EDGES), n)]
    count = 0
    for a, b, c in product(all_graphs, repeat=3):
        if union_graphs(union_graphs(a, b), c) != union_graphs(a, union_graphs(b, c)):
            raise AssertionError("fixed-label union associativity")
        count += 1
    check("fixed-label union associativity", count == 512)
    phase_add = phase_status(ab, all_graphs)
    phase_domain = phase_status(require, all_graphs)
    check("phase-result counterexample", not phase_add["result_congruent"])
    check("phase-domain counterexample", not phase_domain["domain_saturated"])
    remove = Rule("remove", "AB")
    check("noncommuting operations", push(remove, push(ab, unit(empty))) != push(ab, push(remove, unit(empty))))

    # A cancelled intermediate state can avoid a later partial-domain failure.
    forget = Rule("empty")
    # Use a partial rule whose failure appears after a many-to-one total map.
    intermediate = push(ab, push(ac, s))
    check("zero support succeeds under a partial rule", push(require, intermediate) == zero)
    rejects("partial composition cannot be rewritten across cancellation",
            lambda: state(*((c, require.apply(ab.apply(ac.apply(a)))) for a, c in s.terms)), DomainError)
    check("zero under a total map", push(forget, zero) == zero)

    encoded = dump_graph_state(tagged)
    check("exact JSON round trip", load_graph_state(encoded) == tagged)
    invalid = json.loads(encoded)
    invalid["state"][0]["config"]["edges"] = ["AD"]
    invalid["state"][0]["coefficient"] = "0/1"
    rejects("invalid imported zero term rejected", lambda: load_graph_state(json.dumps(invalid)), InvalidInput)
    return {"kernel": KERNEL, "profile": PROFILE, "example_model": MODEL,
            "python": sys.version.split()[0], "checks_passed": len(passed),
            "basis_graphs": len(all_graphs), "associativity_triples": count,
            "phase_add_AB": phase_add, "phase_require_absent_AB": phase_domain,
            "checks": passed,
            "scope": "Finite internal checks; no general gluing, hardware, performance or full-kernel proof."}


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2, ensure_ascii=False))
