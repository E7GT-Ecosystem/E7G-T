"""Two selected restrictions on one authoritative correlated FG3 Joint.

Stage 1 excludes coordinate-0 AB rows. Stage 2 sees only retained rows and
excludes coordinate-1 BC rows. This is an opt-in profile edition, not B1 bind.
"""

from __future__ import annotations

import copy
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint, restrict_joint_absent
from e7c_b1_canonical import canonical_key, digest, require_canonical_json
from e7c_eecq_joint_restrict_b1 import (
    EDITION as FIRST_EDITION, EFFECTS as FIRST_EFFECTS,
    PREDICATE_EDITION as FIRST_PREDICATE, admit as admit_first,
    document as first_document, evaluate as evaluate_first, rows,
)

EDITION = "E7C-EECQ-JOINT-TWO-STAGE/0.1-provisional"
WITNESS_EDITION = "E7C-EECQ-JOINT-TWO-STAGE-WITNESS/0.1-provisional"
SECOND_PREDICATE = "FG3-JOINT-COORD1-ABSENT-BC/0.1-provisional"
TYPE = "Outcome[ThreeWayPartition[Joint[FG3,FG3]],core-1]"
SECOND_EFFECTS = ["evidence:joint_restrict_second_attempt",
                  "restriction:joint_coordinate_1_absent_BC"]


class TwoStageAdmission(ValueError):
    pass


def document(value, *, step_bound=20, ledger_bound=20,
             first_capability=True, first_obligation="resolved",
             second_capability=True, second_obligation="resolved"):
    first = first_document(value, step_bound=step_bound, ledger_bound=ledger_bound,
                           capability=first_capability, obligation=first_obligation)
    source = {"edition": EDITION, "first": first,
              "second_predicate_edition": SECOND_PREDICATE,
              "second_interpretation": {"capability": second_capability,
                                        "obligation": second_obligation}}
    admit(source)
    return source


def admit(source):
    try:
        require_canonical_json(source)
        if (type(source) is not dict or set(source) != {
                "edition", "first", "second_predicate_edition", "second_interpretation"}
                or source["edition"] != EDITION or
                source["second_predicate_edition"] != SECOND_PREDICATE):
            raise TwoStageAdmission("wrong two-stage edition or source shape")
        first = source["first"]
        if first["edition"] != FIRST_EDITION or first["predicate_edition"] != FIRST_PREDICATE:
            raise TwoStageAdmission("first predicate edition mismatch")
        admitted = admit_first(first)
        second = source["second_interpretation"]
        if (type(second) is not dict or set(second) != {"capability", "obligation"}
                or type(second["capability"]) is not bool
                or second["obligation"] not in ("resolved", "unresolved")):
            raise TwoStageAdmission("second interpretation mismatch")
        return admitted
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise TwoStageAdmission("invalid two-stage Joint input") from exc


def conserves(original, retained, first_excluded, second_excluded):
    """Exact three-way partition with the declared predicate route for each row."""
    parts = (retained, first_excluded, second_excluded)
    if any(type(part) is not list for part in parts):
        return False
    if (any("AB" in row["atoms"][0]["edges"] or
            "BC" in row["atoms"][1]["edges"] for row in retained)
            or any("AB" not in row["atoms"][0]["edges"] for row in first_excluded)
            or any("AB" in row["atoms"][0]["edges"] or
                   "BC" not in row["atoms"][1]["edges"] for row in second_excluded)):
        return False
    keys = [canonical_key(row["atoms"]) for part in parts for row in part]
    return len(keys) == len(set(keys)) and {
        canonical_key(row["atoms"]): row["coefficient"] for row in original
    } == {canonical_key(row["atoms"]): row["coefficient"]
          for part in parts for row in part}


def evaluate(source):
    admitted = admit(source)
    first = evaluate_first(source["first"])
    beta = source["first"]["resource_policy"]
    ledger = copy.deepcopy(first["ordered_ledger"])
    steps = first["resource_progress"]["completed_steps"]
    first_excluded = None
    second_excluded_prefix = []
    second_started = False

    def progress():
        return {"completed_steps": steps, "completed_ledger_entries": len(ledger),
                "ledger_prefix": copy.deepcopy(ledger),
                "first_excluded": copy.deepcopy(first_excluded),
                "second_excluded_prefix": copy.deepcopy(second_excluded_prefix)}

    def finish(terminal):
        claim = {"terminal_outcome": copy.deepcopy(terminal),
                 "ordered_ledger": copy.deepcopy(ledger), "resource_progress": progress()}
        witness = {"edition": WITNESS_EDITION, "source_document": copy.deepcopy(source),
                   "static_judgement": {"type": TYPE,
                                        "effects": FIRST_EFFECTS + SECOND_EFFECTS},
                   "first_witness": copy.deepcopy(first["witness"]),
                   "second_started": second_started, "claim": copy.deepcopy(claim)}
        witness["id"] = digest(witness)
        return {**claim, "witness": witness}

    def limit():
        return {"tag": "resource_limit", "progress": progress()}

    if first["terminal_outcome"]["tag"] != "success":
        terminal = copy.deepcopy(first["terminal_outcome"])
        if terminal["tag"] == "resource_limit":
            terminal = limit()
        return finish(terminal)

    first_excluded = copy.deepcopy(first["terminal_outcome"]["value"]["excluded"])
    retained_rows = first["terminal_outcome"]["value"]["retained"]
    # Re-admit the typed intermediate. No marginals or reconstructed products.
    retained_joint = joint([
        (Fraction(row["coefficient"]["numerator"], row["coefficient"]["denominator"]),
         tuple(Config(tuple(g["edges"]), g["tag"]) for g in row["atoms"]))
        for row in retained_rows
    ], arity=2)
    if rows(retained_joint) != retained_rows:
        raise TwoStageAdmission("first retained Joint was not preserved")
    if steps >= beta["step_bound"]:
        return finish(limit())
    steps += 1
    second_started = True
    if len(ledger) >= beta["ledger_bound"]:
        return finish(limit())
    ledger.append({"ordinal": len(ledger), "event": "second_restriction_attempt",
                   "effect": SECOND_EFFECTS[0], "predicate_edition": SECOND_PREDICATE})
    policy = source["second_interpretation"]
    if not policy["capability"]:
        return finish({"tag": "unsupported", "diagnostic": "second_joint_restriction_unavailable"})
    if policy["obligation"] != "resolved":
        return finish({"tag": "undetermined", "diagnostic": "second_joint_predicate_unresolved"})
    for index, (atoms, coefficient) in enumerate(retained_joint.terms):
        if steps >= beta["step_bound"]:
            return finish(limit())
        steps += 1
        if len(ledger) >= beta["ledger_bound"]:
            return finish(limit())
        row = rows(joint([(coefficient, atoms)], arity=2))[0]
        decision = "second_excluded" if "BC" in atoms[1].edges else "retained"
        ledger.append({"ordinal": len(ledger), "event": "second_joint_row_checked",
                       "effect": SECOND_EFFECTS[1], "row_index": index,
                       "row_key": canonical_key(row), "decision": decision})
        if decision == "second_excluded":
            second_excluded_prefix.append(copy.deepcopy(row))
    final, second_excluded = restrict_joint_absent("BC", 1, retained_joint)
    result = {"retained": rows(final), "first_excluded": first_excluded,
              "second_excluded": rows(second_excluded),
              "predicate_editions": [FIRST_PREDICATE, SECOND_PREDICATE]}
    if not conserves(rows(admitted), result["retained"], first_excluded,
                     result["second_excluded"]):
        raise TwoStageAdmission("joint row conservation failed")
    return finish({"tag": "success", "value": result})
