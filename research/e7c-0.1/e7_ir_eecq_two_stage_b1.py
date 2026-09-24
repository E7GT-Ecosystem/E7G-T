"""Typed IR for two sequential restrictions of a correlated binary Joint."""

from __future__ import annotations

import copy
import json

from e7c_b1_canonical import canonical_bytes, canonical_key, digest
from e7_ir_eecq_joint_restrict_b1 import (
    compare_replay as compare_first, execute as execute_first, lower as lower_first,
    parse as parse_first, serialize as serialize_first,
)
from e7c_eecq_joint_restrict_b1 import EFFECTS as FIRST_EFFECTS, PREDICATE_EDITION as FIRST_PREDICATE
from e7c_eecq_two_stage_b1 import (
    EDITION as SOURCE_EDITION, SECOND_EFFECTS, SECOND_PREDICATE, TYPE,
    WITNESS_EDITION, TwoStageAdmission, admit, conserves, evaluate,
)

EDITION = "E7-IR/0.6-EECQ-JOINT-TWO-STAGE-provisional"
CAPABILITY = "eecq.joint.restrict.success_then_restrict/0.1"
MAX_BYTES = 1_000_000


class TwoStageIRAdmission(ValueError):
    pass


def instruction(source):
    node = {"operator": CAPABILITY, "source_edition": SOURCE_EDITION,
            "input_type": "Joint[FG3,FG3]", "output_type": TYPE,
            "predicate_editions": [FIRST_PREDICATE, SECOND_PREDICATE],
            "fields": ["retained", "first_excluded", "second_excluded"],
            "effects": FIRST_EFFECTS + SECOND_EFFECTS,
            "source_digest": digest(source)}
    node["id"] = digest(node)
    return node


def serialize(package):
    try:
        encoded = canonical_bytes(package)
        if len(encoded) > MAX_BYTES:
            raise TwoStageIRAdmission("size bound")
        return encoded
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise TwoStageIRAdmission("invalid encoding") from exc


def lower(source):
    admit(source)
    first_ir = lower_first(source["first"])
    witness = evaluate(source)["witness"]
    package = {"ir_edition": EDITION, "required_capabilities": [CAPABILITY],
               "instruction": instruction(source), "source_document": copy.deepcopy(source),
               "first_ir": first_ir, "source_witness": witness}
    package["id"] = digest(package)
    return parse(serialize(package))


def parse(encoded):
    if type(encoded) is not bytes or len(encoded) > MAX_BYTES:
        raise TwoStageIRAdmission("bounded canonical bytes required")
    try:
        package = json.loads(encoded.decode("utf-8"))
        if (canonical_bytes(package) != encoded or type(package) is not dict
                or set(package) != {"ir_edition", "required_capabilities", "instruction",
                                    "source_document", "first_ir", "source_witness", "id"}
                or package["ir_edition"] != EDITION
                or package["required_capabilities"] != [CAPABILITY]):
            raise TwoStageIRAdmission("wrong edition or package shape")
        source, witness = package["source_document"], package["source_witness"]
        admit(source)
        first_ir = package["first_ir"]
        if (package["instruction"] != instruction(source)
                or parse_first(serialize_first(first_ir)) != first_ir
                or first_ir["source_document"] != source["first"]
                or compare_first(first_ir)["ir_result"] != first_ir["source_witness"]["claim"]
                or type(witness) is not dict
                or set(witness) != {"edition", "source_document", "static_judgement",
                                    "first_witness", "second_started", "claim", "id"}
                or witness["edition"] != WITNESS_EDITION
                or witness["source_document"] != source
                or witness["first_witness"] != first_ir["source_witness"]
                or type(witness["second_started"]) is not bool
                or witness["static_judgement"] != {
                    "type": TYPE, "effects": FIRST_EFFECTS + SECOND_EFFECTS}
                or witness["id"] != digest({k: v for k, v in witness.items() if k != "id"})
                or package["id"] != digest({k: v for k, v in package.items() if k != "id"})):
            raise TwoStageIRAdmission("typed source, child or witness mismatch")
        return package
    except (TypeError, KeyError, ValueError, OverflowError, UnicodeDecodeError,
            RecursionError, TwoStageAdmission) as exc:
        raise TwoStageIRAdmission("invalid two-stage Joint IR") from exc


def execute(package):
    checked = parse(serialize(package))
    source = checked["source_document"]
    first = execute_first(checked["first_ir"])
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

    def result(terminal):
        return {"terminal_outcome": copy.deepcopy(terminal),
                "ordered_ledger": copy.deepcopy(ledger), "resource_progress": progress()}

    def limit():
        return {"tag": "resource_limit", "progress": progress()}

    if first["terminal_outcome"]["tag"] != "success":
        terminal = first["terminal_outcome"]
        return result(limit() if terminal["tag"] == "resource_limit" else terminal)
    value = first["terminal_outcome"]["value"]
    first_excluded = copy.deepcopy(value["excluded"])
    rows = value["retained"]
    if steps >= beta["step_bound"]:
        return result(limit())
    steps += 1
    second_started = True
    if len(ledger) >= beta["ledger_bound"]:
        return result(limit())
    ledger.append({"ordinal": len(ledger), "event": "second_restriction_attempt",
                   "effect": SECOND_EFFECTS[0], "predicate_edition": SECOND_PREDICATE})
    policy = source["second_interpretation"]
    if not policy["capability"]:
        return result({"tag": "unsupported", "diagnostic": "second_joint_restriction_unavailable"})
    if policy["obligation"] == "unresolved":
        return result({"tag": "undetermined", "diagnostic": "second_joint_predicate_unresolved"})
    retained, second_excluded = [], []
    for index, row in enumerate(rows):
        if steps >= beta["step_bound"]:
            return result(limit())
        steps += 1
        if len(ledger) >= beta["ledger_bound"]:
            return result(limit())
        decision = "second_excluded" if "BC" in row["atoms"][1]["edges"] else "retained"
        ledger.append({"ordinal": len(ledger), "event": "second_joint_row_checked",
                       "effect": SECOND_EFFECTS[1], "row_index": index,
                       "row_key": canonical_key(row), "decision": decision})
        (second_excluded if decision == "second_excluded" else retained).append(copy.deepcopy(row))
        if decision == "second_excluded":
            second_excluded_prefix.append(copy.deepcopy(row))
    value = {"retained": retained, "first_excluded": first_excluded,
             "second_excluded": second_excluded,
             "predicate_editions": [FIRST_PREDICATE, SECOND_PREDICATE]}
    if not conserves(source["first"]["rows"], retained, first_excluded, second_excluded):
        raise TwoStageIRAdmission("exact-rational Joint conservation failed")
    return result({"tag": "success", "value": value})


def compare_replay(package):
    checked = parse(serialize(package))
    actual = execute(checked)
    child = checked["first_ir"]["source_witness"]["claim"]
    expected_started = (child["terminal_outcome"]["tag"] == "success" and
                        child["resource_progress"]["completed_steps"] <
                        checked["source_document"]["first"]["resource_policy"]["step_bound"])
    if (actual != checked["source_witness"]["claim"]
            or checked["source_witness"]["second_started"] != expected_started):
        raise TwoStageIRAdmission("source/IR two-stage observation mismatch")
    return {"status": "matched_selected_two_stage_joint_restriction",
            "ir_result": actual, "source_witness_identifier": checked["source_witness"]["id"]}
