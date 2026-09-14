"""Bounded WPC/0.2 reciprocal whole-part reference model.

This standard-library model implements only the allocation-example/0.1 scope
recorded by the v0.13 experimental draft. It is not a general WPC runtime.
"""

from dataclasses import dataclass, replace
from itertools import product
import json

IDS = ("A", "B", "C")
PROFILE = "E7G-T-v0.13-draft:WPC/0.2-proposed:allocation-example/0.1"


class Reject(Exception):
    pass


@dataclass(frozen=True)
class Whole:
    epoch: int
    members: tuple
    values: tuple
    events: tuple = ()
    budget: int = 2

    def __post_init__(self):
        if type(self.epoch) is not int or self.epoch < 0:
            raise Reject("invalid_epoch")
        if (type(self.members) is not tuple or not self.members
                or self.members != tuple(sorted(set(self.members)))
                or not set(self.members) <= set(IDS)):
            raise Reject("invalid_membership")
        if type(self.values) is not tuple or len(self.values) != len(self.members):
            raise Reject("coverage_incomplete")
        if any(type(v) is not int or not 0 <= v <= 2 for v in self.values):
            raise Reject("invalid_value")
        if type(self.budget) is not int or self.budget != 2:
            raise Reject("unsupported_budget")
        if sum(self.values) > self.budget:
            raise Reject("global_incompatibility")
        if type(self.events) is not tuple or any(type(e) is not tuple for e in self.events):
            raise Reject("invalid_history")


def encode(w):
    return json.dumps([PROFILE, w.epoch, w.members, w.values, w.events, w.budget],
                      separators=(",", ":"), ensure_ascii=True)


def decode(payload):
    # Trusted model-produced bytes only; this is not an adversarial importer.
    p, epoch, members, values, events, budget = json.loads(payload)
    if p != PROFILE:
        raise Reject("unsupported_profile")
    return Whole(epoch, tuple(members), tuple(values), tuple(tuple(e) for e in events), budget)


@dataclass(frozen=True)
class Assembly:
    epoch: int
    manifest: tuple
    # Each row is (occurrence, actual local semantic allocation, whole encoding).
    rows: tuple
    events: tuple


def alpha(w):
    return Assembly(w.epoch, w.members,
                    tuple((i, v, encode(w)) for i, v in zip(w.members, w.values)),
                    w.events)


def beta(z):
    if tuple(row[0] for row in z.rows) != z.manifest:
        raise Reject("coverage_incomplete")
    actual = Whole(z.epoch, z.manifest, tuple(row[1] for row in z.rows), z.events)
    for _, _, payload in z.rows:
        if decode(payload) != actual:
            raise Reject("source_conflict")
    if alpha(actual) != z:
        raise Reject("noncanonical_assembly")
    return actual


@dataclass(frozen=True)
class Proposal:
    event_id: str
    actor: str
    base: str  # Complete canonical base identity in this tiny model, not epoch alone.
    target: str
    value: int


def reconcile(w, proposals):
    unique = {}
    for p in proposals:
        if type(p.event_id) is not str or not p.event_id:
            raise Reject("invalid_event_id")
        if p.event_id in unique and unique[p.event_id] != p:
            raise Reject("event_equivocation")
        unique[p.event_id] = p
    if not unique:
        return w
    writes, events = {}, []
    seen = {event[0] for event in w.events}
    for event_id, p in sorted(unique.items()):
        if event_id in seen:
            raise Reject("already_committed_event")
        if p.base != encode(w):
            raise Reject("precondition_conflict")
        if p.actor != p.target or p.target not in w.members:
            raise Reject("unauthorised")
        if p.target in writes:
            raise Reject("write_conflict")
        if type(p.value) is not int or not 0 <= p.value <= 2:
            raise Reject("invalid_value")
        writes[p.target] = p.value
        events.append((event_id, p.actor, w.epoch, "set", p.target, p.value))
    values = dict(zip(w.members, w.values))
    values.update(writes)
    # Whole admission checks the joint budget, without dropping any event.
    return Whole(w.epoch + 1, w.members, tuple(values[i] for i in w.members),
                 w.events + tuple(events))


def membership_candidate(w, actor, members, event_id):
    if actor != "coordinator":
        raise Reject("unauthorised")
    if not event_id or event_id in {event[0] for event in w.events}:
        raise Reject("invalid_event_id")
    values = dict(zip(w.members, w.values))
    members = tuple(members)
    historical_members = set(w.members)
    for event in w.events:
        if event[3] == "membership":
            historical_members.update(event[4].split(","))
            historical_members.update(event[5].split(","))
    if (set(members) - set(w.members)) & historical_members:
        raise Reject("occurrence_reuse")
    return Whole(w.epoch + 1, members, tuple(values.get(i, 0) for i in members),
                 w.events + ((event_id, actor, w.epoch, "membership",
                              ",".join(w.members), ",".join(members)),))


def run():
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def rejects(name, reason, thunk):
        try:
            thunk()
        except Reject as exc:
            check(name, str(exc) == reason)
        else:
            raise AssertionError(name)

    w = Whole(0, IDS, (0, 0, 0))
    a = Proposal("a1", "A", encode(w), "A", 1)
    b = Proposal("b1", "B", encode(w), "B", 1)
    c = Proposal("c1", "C", encode(w), "C", 1)
    successor = reconcile(w, (a, b))  # Candidate only; no external commitment.
    check("semantic constitution needs no encoding", w.members == IDS and sum(w.values) <= w.budget)
    check("bottom-up joint contribution", successor.values == (1, 1, 0))
    check("all accepted contributions retained", len(successor.events) == 2)
    check("original remains immutable", w.values == (0, 0, 0) and not w.events)
    check("disjoint batch order does not alter result", reconcile(w, (b, a)) == successor)
    check("duplicate event within batch is idempotent", reconcile(w, (a, a, b)) == successor)
    rejects("event equivocation", "event_equivocation",
            lambda: reconcile(w, (a, replace(a, value=2))))
    rejects("competing writes", "write_conflict",
            lambda: reconcile(w, (a, replace(a, event_id="a2", value=2))))
    rejects("unauthorised local write", "unauthorised",
            lambda: reconcile(w, (replace(a, actor="B"),)))
    rejects("stale base", "precondition_conflict",
            lambda: reconcile(successor, (c,)))
    rejects("committed replay cannot apply twice", "already_committed_event",
            lambda: reconcile(successor, (a,)))
    check("every pair fits", all(sum(reconcile(w, pair).values) == 2
          for pair in ((a, b), (a, c), (b, c))))
    rejects("pairwise admission is not global admission", "global_incompatibility",
            lambda: reconcile(w, (a, b, c)))
    z = alpha(successor)
    check("semantic round trip", beta(z) == successor)
    check("assembly round trip", alpha(beta(z)) == z)
    check("equal payloads distinct occurrences", len({r[2] for r in z.rows}) == 1
          and len({r[0] for r in z.rows}) == 3)
    check("all portions exact current source", all(decode(r[2]) == successor for r in z.rows))
    rejects("missing member", "coverage_incomplete", lambda: beta(replace(z, rows=z.rows[:-1])))
    rejects("duplicate occurrence", "coverage_incomplete",
            lambda: beta(replace(z, rows=(z.rows[0], z.rows[0], z.rows[2]))))
    mixed = replace(z, rows=(z.rows[0], z.rows[1], ("C", 0, encode(w))))
    check("stale source remains exact historically", decode(mixed.rows[2][2]) == w)
    rejects("mixed sources not current coherent", "source_conflict", lambda: beta(mixed))
    changed = replace(alpha(w), rows=(("A", 1, encode(w)),) + alpha(w).rows[1:])
    rejects("unencoded semantic local change", "source_conflict", lambda: beta(changed))
    left = membership_candidate(successor, "coordinator", ("A", "B"), "leave-c")
    check("admitted withdrawal gets new manifest", left.members == ("A", "B"))
    check("withdrawal re-encodes exact new whole", beta(alpha(left)) == left)
    rejects("retired occurrence ID cannot be reused", "occurrence_reuse",
            lambda: membership_candidate(left, "coordinator", IDS, "reuse-c"))
    fresh = Whole(0, ("A", "B"), (1, 1))
    joined = membership_candidate(fresh, "coordinator", IDS, "join-c")
    check("join initialises and revalidates", joined.values == (1, 1, 0) and beta(alpha(joined)) == joined)
    rejects("unauthorised membership", "unauthorised",
            lambda: membership_candidate(w, "A", ("A", "B"), "bad-leave"))
    rejects("no vacuous all-portions success", "invalid_membership", lambda: Whole(0, (), ()))
    other_history = reconcile(w, (replace(a, event_id="a-other"), b))
    check("same values distinct histories", other_history.values == successor.values
          and encode(other_history) != encode(successor))
    check("epoch alone is not identity", other_history.epoch == successor.epoch
          and other_history != successor)
    admitted = [Whole(0, IDS, vs) for vs in product(range(3), repeat=3) if sum(vs) <= 2]
    check("finite initial carrier contains ten wholes", len(admitted) == 10)
    check("exact encoder injective on finite carrier", len({encode(x) for x in admitted}) == 10)
    check("both closure laws on finite carrier", all(beta(alpha(x)) == x and
          alpha(beta(alpha(x))) == alpha(x) for x in admitted))
    check("thirty bounded portion round trips", all(decode(row[2]) == x
          for x in admitted for row in alpha(x).rows))
    return {"profile": PROFILE, "checks_passed": len(checks), "checks": checks,
            "finite_initial_wholes": len(admitted), "portion_round_trips": 3 * len(admitted),
            "scope": "Illustrative finite in-memory subset; not full WPC conformance or independent validation."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))

