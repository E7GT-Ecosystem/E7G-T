"""Lossless boundary from admitted two-stage Python Joint rows to Lean Row.

The JSON representation is a precise transport contract; Lean's WireGraph
and WireRow in E7CEECQTwoStageExactCodec.lean define its target. No finite
numeric tag table or terminal-code erasure is used here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from e7c_b1_canonical import canonical_key
from e7c_eecq_two_stage_b1 import admit

EDGES = ("AB", "AC", "BC")


class CodecAdmission(ValueError):
    pass


@dataclass(frozen=True)
class LeanGraph:
    ab: bool
    ac: bool
    bc: bool
    tag: str | None

    def edges(self):
        return [edge for edge, present in zip(EDGES, (self.ab, self.ac, self.bc))
                if present]


@dataclass(frozen=True)
class LeanRow:
    left: LeanGraph
    right: LeanGraph
    coefficient: Fraction


@dataclass(frozen=True)
class LeanEvent:
    stage: str
    index: int | None = None
    row: LeanRow | None = None
    excluded: bool | None = None


def graph(g):
    if (type(g) is not dict or set(g) != {"edges", "tag"}
            or type(g["edges"]) is not list
            or g["edges"] != [e for e in EDGES if e in g["edges"]]
            or g["tag"] is not None and type(g["tag"]) is not str):
        raise CodecAdmission("noncanonical graph is outside admitted Joint")
    if g["tag"] is not None:
        try:
            g["tag"].encode("utf-8")
        except UnicodeEncodeError as exc:
            raise CodecAdmission("tag is not canonical UTF-8 JSON") from exc
    return LeanGraph(*(e in g["edges"] for e in EDGES), g["tag"])


def row(r):
    if (type(r) is not dict or set(r) != {"atoms", "coefficient"}
            or type(r["atoms"]) is not list or len(r["atoms"]) != 2
            or type(r["coefficient"]) is not dict
            or set(r["coefficient"]) != {"numerator", "denominator"}):
        raise CodecAdmission("not an admitted binary Joint row")
    c = r["coefficient"]
    if (type(c["numerator"]) is not int or type(c["denominator"]) is not int
            or not c["denominator"] or c["numerator"] == 0
            or c["denominator"] < 0):
        raise CodecAdmission("nonzero signed fraction with positive denominator required")
    coefficient = Fraction(c["numerator"], c["denominator"])
    if (coefficient.numerator, coefficient.denominator) != (
            c["numerator"], c["denominator"]):
        raise CodecAdmission("unreduced fraction is outside admitted Joint")
    return LeanRow(graph(r["atoms"][0]), graph(r["atoms"][1]), coefficient)


def decode_row(r):
    if type(r) is not LeanRow or type(r.coefficient) is not Fraction or not r.coefficient:
        raise CodecAdmission("invalid Lean row")
    for g in (r.left, r.right):
        if (type(g) is not LeanGraph or any(type(getattr(g, e)) is not bool
                                           for e in ("ab", "ac", "bc"))
                or g.tag is not None and type(g.tag) is not str):
            raise CodecAdmission("invalid Lean graph")
    return {"atoms": [{"edges": g.edges(), "tag": g.tag} for g in (r.left, r.right)],
            "coefficient": {"numerator": r.coefficient.numerator,
                            "denominator": r.coefficient.denominator}}


def rows(source):
    admitted = admit(source)
    encoded = tuple(row(r) for r in source["first"]["rows"])
    if (tuple(decode_row(r) for r in encoded) != tuple(source["first"]["rows"])
            or len(encoded) != len(admitted.terms)):
        raise CodecAdmission("Joint row roundtrip or support failed")
    return encoded


def partition(encoded):
    """Three lists in original row order, keeping each exact graph and Rat."""
    retained, first_excluded, second_excluded = [], [], []
    for r in encoded:
        (first_excluded if r.left.ab else
         second_excluded if r.right.bc else retained).append(r)
    return retained, first_excluded, second_excluded


def policy(source):
    admit(source)
    def convert(p):
        if not p["capability"]:
            return "unsupported"
        return "ready" if p["obligation"] == "resolved" else "undetermined"
    return convert(source["first"]["interpretation"]), convert(source["second_interpretation"])


def budget(source):
    admit(source)
    p = source["first"]["resource_policy"]
    return p["step_bound"], p["ledger_bound"]


def events(observation, encoded):
    """Check and map every ledger entry, ordinal, row key and decision."""
    ledger = observation["ordered_ledger"]
    if observation["resource_progress"]["ledger_prefix"] != ledger:
        raise CodecAdmission("ledger and progress disagree")
    first_retained = [r for r in encoded if not r.left.ab]
    mapped = []
    for ordinal, entry in enumerate(ledger):
        if entry["ordinal"] != ordinal:
            raise CodecAdmission("nonsequential event ordinal")
        kind = entry["event"]
        if kind in ("restriction_attempt", "second_restriction_attempt"):
            stage = "first" if kind == "restriction_attempt" else "second"
            mapped.append(LeanEvent(stage))
            continue
        if kind not in ("joint_row_checked", "second_joint_row_checked"):
            raise CodecAdmission("unknown event")
        stage = "first" if kind == "joint_row_checked" else "second"
        candidates = encoded if stage == "first" else first_retained
        index = entry["row_index"]
        if type(index) is not int or index < 0 or index >= len(candidates):
            raise CodecAdmission("row event index outside correlated support")
        current = candidates[index]
        excluded = current.left.ab if stage == "first" else current.right.bc
        decision = ("excluded" if excluded else "retained") if stage == "first" else (
            "second_excluded" if excluded else "retained")
        if (entry["row_key"] != canonical_key(decode_row(current))
                or entry["decision"] != decision):
            raise CodecAdmission("event loses row identity or predicate")
        mapped.append(LeanEvent(stage, index, current, excluded))
    return tuple(mapped)


def observation(source, result):
    """Exact observable projection for Lean Operational.Observation.

    Witness digest and static annotations stay in the Python witness; they are
    not fields of Lean Observation. All fields of the Lean observation survive.
    """
    encoded = rows(source)
    mapped = events(result, encoded)
    progress = result["resource_progress"]
    first = progress["first_excluded"]
    second = progress["second_excluded_prefix"]
    if (progress["completed_ledger_entries"] != len(mapped)
            or (first is not None and tuple(row(r) for r in first) !=
                tuple(r for r in encoded if r.left.ab))
            or tuple(row(r) for r in second) !=
                tuple(e.row for e in mapped if e.stage == "second" and e.row is not None
                      and e.excluded)):
        raise CodecAdmission("progress does not preserve exact rows")
    terminal = result["terminal_outcome"]
    value = None
    if terminal["tag"] == "success":
        v = terminal["value"]
        value = tuple(tuple(row(r) for r in v[k]) for k in
                      ("retained", "first_excluded", "second_excluded"))
        if value != tuple(tuple(part) for part in partition(encoded)):
            raise CodecAdmission("success partition differs from exact Joint")
    elif terminal["tag"] == "resource_limit":
        if terminal["progress"] != progress:
            raise CodecAdmission("resource progress mismatch")
    elif terminal["tag"] not in ("unsupported", "undetermined"):
        raise CodecAdmission("unsupported terminal mapping")
    terminal_stage = None
    if terminal["tag"] in ("unsupported", "undetermined"):
        terminal_stage = "second" if first is not None else "first"
        expected_diagnostic = {
            ("first", "unsupported"): "joint_restriction_unavailable",
            ("first", "undetermined"): "joint_predicate_unresolved",
            ("second", "unsupported"): "second_joint_restriction_unavailable",
            ("second", "undetermined"): "second_joint_predicate_unresolved",
        }[terminal_stage, terminal["tag"]]
        if terminal["diagnostic"] != expected_diagnostic:
            raise CodecAdmission("failure stage or diagnostic mismatch")
    return {"terminal": terminal["tag"], "partition": value,
            "terminalStage": terminal_stage,
            "orderedLedger": mapped, "completedSteps": progress["completed_steps"],
            "firstExcluded": None if first is None else tuple(row(r) for r in first),
            "secondExcludedPrefix": tuple(row(r) for r in second),
            "secondStarted": result["witness"]["second_started"] if "witness" in result
                             else _second_started(mapped, progress, encoded, policy(source)[0])}


def _second_started(mapped, progress, encoded, first_policy):
    # A charged second attempt counts even when the append fails.
    return (first_policy == "ready" and
            progress["completed_steps"] > 1 + len(encoded))


def staged_spec(source):
    """Fuelled selected rule: stop before inspecting a row when out of fuel.

    Its transition schedule is independent of source.evaluate and IR.execute.
    Every yielded row is one actual visited row, not a prebuilt event plan.
    """
    encoded = rows(source)
    first_policy, second_policy = policy(source)
    step_bound, ledger_bound = budget(source)
    ledger = []
    steps = 0
    first_excluded = None
    second_excluded = []
    second_started = False

    def charge(event):
        nonlocal steps, second_started
        if steps == step_bound:
            return False
        steps += 1
        if event.stage == "second" and event.index is None:
            second_started = True
        if len(ledger) == ledger_bound:
            return False
        ledger.append(event)
        return True

    def finish(terminal, value=None):
        return {"terminal": terminal, "partition": value,
                "terminalStage": ("first" if first_excluded is None else "second")
                if terminal in ("unsupported", "undetermined") else None,
                "orderedLedger": tuple(ledger), "completedSteps": steps,
                "firstExcluded": first_excluded,
                "secondExcludedPrefix": tuple(second_excluded),
                "secondStarted": second_started}

    if not charge(LeanEvent("first")):
        return finish("resource_limit")
    if first_policy != "ready":
        return finish(first_policy)
    kept = []
    excluded = []
    for i, current in enumerate(encoded):
        event = LeanEvent("first", i, current, current.left.ab)
        if not charge(event):
            return finish("resource_limit")
        (excluded if current.left.ab else kept).append(current)
    first_excluded = tuple(excluded)
    if not charge(LeanEvent("second")):
        return finish("resource_limit")
    if second_policy != "ready":
        return finish(second_policy)
    final = []
    for i, current in enumerate(kept):
        event = LeanEvent("second", i, current, current.right.bc)
        if not charge(event):
            return finish("resource_limit")
        (second_excluded if current.right.bc else final).append(current)
    return finish("success", (tuple(final), tuple(excluded), tuple(second_excluded)))
