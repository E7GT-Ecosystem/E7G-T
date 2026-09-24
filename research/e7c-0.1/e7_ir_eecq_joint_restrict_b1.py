"""Versioned typed IR for one FG3 correlated Joint restriction.

Execution interprets complete exact-rational row records; it never derives
joint rows by multiplying marginal states or discards the excluded partition.
"""

from __future__ import annotations

import copy
import json
from fractions import Fraction

from e7c_b1_canonical import canonical_bytes, canonical_key, digest
from e7c_eecq_joint_restrict_b1 import (
    EFFECTS, EDITION as SOURCE_EDITION, INPUT_TYPE, OUTPUT_TYPE,
    PREDICATE_EDITION, WITNESS_EDITION, JointRestrictionAdmission, admit, evaluate,
)

EDITION = "E7-IR/0.5-EECQ-JOINT-RESTRICT-provisional"
CAPABILITY = "eecq.joint.restrict.coord0.absent_ab/0.1"
MAX_BYTES = 1_000_000


class JointRestrictionIRAdmission(ValueError):
    pass


def instruction(source):
    node = {"operator": CAPABILITY, "source_edition": SOURCE_EDITION,
            "predicate_edition": PREDICATE_EDITION, "input_type": INPUT_TYPE,
            "output_type": OUTPUT_TYPE, "source_digest": digest(source),
            "retained_field": "retained", "excluded_field": "excluded",
            "effects": EFFECTS}
    node["id"] = digest(node)
    return node


def lower(source):
    admit(source)
    result = evaluate(source)
    package = {"ir_edition": EDITION, "required_capabilities": [CAPABILITY],
               "instruction": instruction(source), "source_document": copy.deepcopy(source),
               "source_witness": result["witness"]}
    package["id"] = digest(package)
    return parse(serialize(package))


def serialize(package):
    try:
        encoded = canonical_bytes(package)
        if len(encoded) > MAX_BYTES:
            raise JointRestrictionIRAdmission("size bound")
        return encoded
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise JointRestrictionIRAdmission("invalid encoding") from exc


def parse(encoded):
    if type(encoded) is not bytes or len(encoded) > MAX_BYTES:
        raise JointRestrictionIRAdmission("bounded canonical bytes required")
    try:
        package = json.loads(encoded.decode("utf-8"))
        if (canonical_bytes(package) != encoded or type(package) is not dict
                or set(package) != {"ir_edition", "required_capabilities", "instruction",
                                    "source_document", "source_witness", "id"}
                or package["ir_edition"] != EDITION or
                package["required_capabilities"] != [CAPABILITY]):
            raise JointRestrictionIRAdmission("wrong edition, capability or package shape")
        source = package["source_document"]
        admit(source)
        witness = package["source_witness"]
        if (package["instruction"] != instruction(source) or
                type(witness) is not dict or set(witness) != {
                    "edition", "source_document", "static_judgement", "claim", "id"}
                or witness["edition"] != WITNESS_EDITION or
                witness["source_document"] != source or
                witness["id"] != digest({k: v for k, v in witness.items() if k != "id"}) or
                witness["static_judgement"] != {"type": OUTPUT_TYPE, "effects": EFFECTS} or
                package["id"] != digest({k: v for k, v in package.items() if k != "id"})):
            raise JointRestrictionIRAdmission("rebound instruction, source or witness")
        return package
    except (TypeError, KeyError, ValueError, OverflowError, UnicodeDecodeError,
            RecursionError, JointRestrictionAdmission) as exc:
        raise JointRestrictionIRAdmission("invalid typed joint restriction IR") from exc


def execute(package):
    checked = parse(serialize(package))
    source = checked["source_document"]
    beta, interp = source["resource_policy"], source["interpretation"]
    ledger, retained, excluded = [], [], []
    steps = 0

    def progress():
        return {"completed_steps": steps, "completed_ledger_entries": len(ledger),
                "ledger_prefix": copy.deepcopy(ledger)}

    def result(terminal):
        return {"terminal_outcome": terminal, "ordered_ledger": copy.deepcopy(ledger),
                "resource_progress": progress()}

    def limit():
        return {"tag": "resource_limit", "progress": progress()}

    if beta["step_bound"] == 0:
        return result(limit())
    steps += 1
    if beta["ledger_bound"] == 0:
        return result(limit())
    ledger.append({"ordinal": 0, "event": "restriction_attempt",
                   "effect": EFFECTS[0], "predicate_edition": PREDICATE_EDITION})
    if not interp["capability"]:
        return result({"tag": "unsupported", "diagnostic": "joint_restriction_unavailable"})
    if interp["obligation"] == "unresolved":
        return result({"tag": "undetermined", "diagnostic": "joint_predicate_unresolved"})
    for index, row in enumerate(source["rows"]):
        if steps >= beta["step_bound"]:
            return result(limit())
        steps += 1
        if len(ledger) >= beta["ledger_bound"]:
            return result(limit())
        decision = "excluded" if "AB" in row["atoms"][0]["edges"] else "retained"
        ledger.append({"ordinal": len(ledger), "event": "joint_row_checked",
                       "effect": EFFECTS[1], "row_index": index,
                       "row_key": canonical_key(row), "decision": decision})
        (excluded if decision == "excluded" else retained).append(copy.deepcopy(row))
    # A separate exact rational check guards the partition and coefficient
    # preservation before returning a successful observable result.
    def amounts(rows):
        return {canonical_key(row["atoms"]): Fraction(row["coefficient"]["numerator"],
                                                      row["coefficient"]["denominator"])
                for row in rows}
    whole, kept, removed = amounts(source["rows"]), amounts(retained), amounts(excluded)
    if not set(kept).isdisjoint(removed) or whole != (kept | removed):
        raise JointRestrictionIRAdmission("joint partition loses exact rational rows")
    return result({"tag": "success", "value": {"retained": retained,
                                                "excluded": excluded,
                                                "predicate_edition": PREDICATE_EDITION}})


def compare_replay(package):
    checked = parse(serialize(package))
    actual = execute(checked)
    if actual != checked["source_witness"]["claim"]:
        raise JointRestrictionIRAdmission("independent IR and source replay differ")
    return {"status": "matched_selected_correlated_joint_restriction",
            "ir_result": actual, "source_witness_identifier": checked["source_witness"]["id"]}
