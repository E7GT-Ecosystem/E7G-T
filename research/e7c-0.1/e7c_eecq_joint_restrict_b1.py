"""Selected, provisional EEC-Q restriction on an authoritative binary FG3 Joint.

The published calculus and the earlier graph-state-only adapter are unchanged.
"""

from __future__ import annotations

import copy
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint, restrict_joint_absent
from e7c_b1_canonical import canonical_key, digest, require_canonical_json

EDITION = "E7C-EECQ-JOINT-RESTRICT/0.1-provisional"
WITNESS_EDITION = "E7C-EECQ-JOINT-RESTRICT-WITNESS/0.1-provisional"
PREDICATE_EDITION = "FG3-JOINT-COORD0-ABSENT-AB/0.1-provisional"
SOURCE_BLOB = "a84da2c4de2ada23577cde4512a10c3369aba2b5"
MODEL_BLOB = "6c624fcd49b95e473a3e80160979183e8d3b58aa"
INPUT_TYPE = "Joint[FG3,FG3]"
OUTPUT_TYPE = "Outcome[Partition[Joint[FG3,FG3]],core-1]"
EFFECTS = ["evidence:joint_restrict_attempt", "restriction:joint_coordinate_0_absent_AB"]
MAX_ROWS = 64


class JointRestrictionAdmission(ValueError):
    pass


def _graph(g):
    return {"edges": list(g.edges), "tag": g.tag}


def _row(atoms, coefficient):
    return {"atoms": [_graph(g) for g in atoms],
            "coefficient": {"numerator": coefficient.numerator,
                            "denominator": coefficient.denominator}}


def rows(value):
    if type(value) is not Joint or value.arity != 2:
        raise JointRestrictionAdmission("binary typed joint required")
    return [_row(atoms, coefficient) for atoms, coefficient in value.terms]


def document(value, *, step_bound=20, ledger_bound=20,
             capability=True, obligation="resolved"):
    result = {"edition": EDITION, "canonical_source_blob": SOURCE_BLOB,
              "model_blob": MODEL_BLOB, "predicate_edition": PREDICATE_EDITION,
              "input_type": INPUT_TYPE, "output_type": OUTPUT_TYPE,
              "rows": rows(value), "resource_policy": {
                  "step_bound": step_bound, "ledger_bound": ledger_bound},
              "interpretation": {"capability": capability, "obligation": obligation}}
    admit(result)
    return result


def admit(source):
    try:
        require_canonical_json(source)
        if (type(source) is not dict or set(source) != {
                "edition", "canonical_source_blob", "model_blob", "predicate_edition",
                "input_type", "output_type", "rows", "resource_policy", "interpretation"}
                or (source["edition"], source["canonical_source_blob"],
                    source["model_blob"], source["predicate_edition"],
                    source["input_type"], source["output_type"]) !=
                (EDITION, SOURCE_BLOB, MODEL_BLOB, PREDICATE_EDITION,
                 INPUT_TYPE, OUTPUT_TYPE)):
            raise JointRestrictionAdmission("wrong edition, type or source shape")
        beta, interpretation = source["resource_policy"], source["interpretation"]
        if (type(beta) is not dict or set(beta) != {"step_bound", "ledger_bound"}
                or any(type(beta[k]) is not int or beta[k] < 0 for k in beta)
                or type(interpretation) is not dict
                or set(interpretation) != {"capability", "obligation"}
                or type(interpretation["capability"]) is not bool
                or interpretation["obligation"] not in ("resolved", "unresolved")):
            raise JointRestrictionAdmission("invalid resource or interpretation policy")
        if type(source["rows"]) is not list or len(source["rows"]) > MAX_ROWS:
            raise JointRestrictionAdmission("joint rows must be a bounded list")
        parsed = []
        for row in source["rows"]:
            if type(row) is not dict or set(row) != {"atoms", "coefficient"}:
                raise JointRestrictionAdmission("invalid joint row")
            atoms, c = row["atoms"], row["coefficient"]
            if (type(atoms) is not list or len(atoms) != 2 or
                    type(c) is not dict or set(c) != {"numerator", "denominator"} or
                    type(c["numerator"]) is not int or type(c["denominator"]) is not int or
                    c["denominator"] <= 0 or c["numerator"] == 0):
                raise JointRestrictionAdmission("invalid rational joint row")
            graphs = []
            for g in atoms:
                if type(g) is not dict or set(g) != {"edges", "tag"} or type(g["edges"]) is not list:
                    raise JointRestrictionAdmission("invalid graph")
                graph = Config(tuple(g["edges"]), g["tag"])
                if _graph(graph) != g:
                    raise JointRestrictionAdmission("noncanonical graph edges")
                graphs.append(graph)
            parsed.append((Fraction(c["numerator"], c["denominator"]), tuple(graphs)))
        value = joint(parsed, arity=2)
        if rows(value) != source["rows"]:
            raise JointRestrictionAdmission("uncanonical, duplicate or cancelled joint rows")
        return value
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise JointRestrictionAdmission("invalid selected joint restriction input") from exc


def evaluate(source):
    value = admit(source)
    beta, interp = source["resource_policy"], source["interpretation"]
    ledger, steps = [], 0

    def progress():
        return {"completed_steps": steps, "completed_ledger_entries": len(ledger),
                "ledger_prefix": copy.deepcopy(ledger)}

    def finish(terminal):
        claim = {"terminal_outcome": terminal, "ordered_ledger": copy.deepcopy(ledger),
                 "resource_progress": progress()}
        witness = {"edition": WITNESS_EDITION, "source_document": copy.deepcopy(source),
                   "static_judgement": {"type": OUTPUT_TYPE, "effects": EFFECTS},
                   "claim": copy.deepcopy(claim)}
        witness["id"] = digest(witness)
        return {**claim, "witness": witness}

    def limit():
        return {"tag": "resource_limit", "progress": progress()}

    if beta["step_bound"] == 0:
        return finish(limit())
    steps += 1
    if beta["ledger_bound"] == 0:
        return finish(limit())
    ledger.append({"ordinal": 0, "event": "restriction_attempt",
                   "effect": EFFECTS[0], "predicate_edition": PREDICATE_EDITION})
    if not interp["capability"]:
        return finish({"tag": "unsupported", "diagnostic": "joint_restriction_unavailable"})
    if interp["obligation"] != "resolved":
        return finish({"tag": "undetermined", "diagnostic": "joint_predicate_unresolved"})
    for index, (atoms, coefficient) in enumerate(value.terms):
        if steps >= beta["step_bound"]:
            return finish(limit())
        steps += 1
        if len(ledger) >= beta["ledger_bound"]:
            return finish(limit())
        decision = "excluded" if "AB" in atoms[0].edges else "retained"
        ledger.append({"ordinal": len(ledger), "event": "joint_row_checked",
                       "effect": EFFECTS[1], "row_index": index,
                       "row_key": canonical_key(_row(atoms, coefficient)),
                       "decision": decision})
    retained, excluded = restrict_joint_absent("AB", 0, value)
    return finish({"tag": "success", "value": {"retained": rows(retained),
                                                "excluded": rows(excluded),
                                                "predicate_edition": PREDICATE_EDITION}})
