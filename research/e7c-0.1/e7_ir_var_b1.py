"""Versioned E7-IR/0.1 var-only lowering and independent finite evaluator.

Selected WP6 fragment; the IR never defines source semantics or source truth.
"""

from __future__ import annotations

import copy
import json
import re

from e7c_b1_canonical import (CALCULUS_EDITION, DYNAMIC_RULES_ID,
                              INTERPRETATION_EDITION, OUTCOME_EXTENSION_EDITION,
                              RESOURCE_POLICY_EDITION, canonical_key,
                              STATIC_RULES_ID, canonical_bytes, digest,
                              require_canonical_json)
from e7c_b1_admission import validate_typed_binding
from e7c_b1_evaluator import Evaluator
from e7c_b1_static import Diagnostic, parse_type, type_json


IR_EDITION = "E7-IR/0.1-var-B1-provisional"
CAPABILITY = "core.var/0.1"
MAX_BYTES = 1_000_000


class IRAdmissionError(ValueError):
    pass


def _atomic_keys(value: dict) -> set[str]:
    keys = {canonical_key(value)} if value["tag"] in {"base", "config", "entity"} else set()
    for arg in value["args"]:
        if type(arg) is dict:
            keys.update(_atomic_keys(arg))
    return keys


def lower(document: dict) -> dict:
    """Admission uses accepted WP2 and the disposable WP3-I input boundary."""
    source = Evaluator(document)
    term = source.term
    if term["tag"] != "var":
        raise IRAdmissionError("only the closed core.var fragment is admitted")
    variable = term["name"]
    variable_type = source.environment["variables"][variable]
    carriers = source.interpretation["carriers"]
    binding_carriers = {key: copy.deepcopy(carriers[key])
                        for key in sorted(_atomic_keys(variable_type))}
    instruction = {"operator": CAPABILITY, "name": variable,
                   "type": copy.deepcopy(variable_type),
                   "effects": copy.deepcopy(source.static["effects"]),
                   "source_location": {"document": digest(source.document),
                                       "path": "$.term"}}
    instruction["id"] = digest(instruction)
    body = {"ir_edition": IR_EDITION,
            "required_capabilities": [CAPABILITY],
            "pins": {"calculus": CALCULUS_EDITION,
                     "static_rules": STATIC_RULES_ID,
                     "dynamic_rules": DYNAMIC_RULES_ID,
                     "interpretation": INTERPRETATION_EDITION,
                     "outcome_extension": OUTCOME_EXTENSION_EDITION,
                     "resource_policy": RESOURCE_POLICY_EDITION},
            "instruction": instruction,
            "binding": copy.deepcopy(source.values[variable]),
            "binding_carriers": binding_carriers,
            "resource": copy.deepcopy(source.beta)}
    body["id"] = digest(body)
    return parse(serialize(body))


def serialize(ir: dict) -> bytes:
    try:
        require_canonical_json(ir)
        encoded = canonical_bytes(ir)
        if len(encoded) > MAX_BYTES:
            raise IRAdmissionError("IR size bound exceeded")
        return encoded
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise IRAdmissionError("canonical IR encoding required") from exc


def parse(encoded: bytes) -> dict:
    if type(encoded) is not bytes or len(encoded) > MAX_BYTES:
        raise IRAdmissionError("bounded byte encoding required")
    try:
        ir = json.loads(encoded.decode("utf-8"))
        if type(ir) is not dict or canonical_bytes(ir) != encoded:
            raise IRAdmissionError("noncanonical IR")
        if (set(ir) != {"ir_edition", "required_capabilities", "pins", "instruction",
                        "binding", "binding_carriers", "resource", "id"} or
                ir["ir_edition"] != IR_EDITION or
                ir["required_capabilities"] != [CAPABILITY]):
            raise IRAdmissionError("unsupported IR edition or mandatory capability")
        pins = ir["pins"]
        if pins != {"calculus": CALCULUS_EDITION,
                    "static_rules": STATIC_RULES_ID,
                    "dynamic_rules": DYNAMIC_RULES_ID,
                    "interpretation": INTERPRETATION_EDITION,
                    "outcome_extension": OUTCOME_EXTENSION_EDITION,
                    "resource_policy": RESOURCE_POLICY_EDITION}:
            raise IRAdmissionError("source edition mismatch")
        instruction = ir["instruction"]
        if (type(instruction) is not dict or
                set(instruction) != {"operator", "name", "type", "effects", "source_location", "id"} or
                instruction["operator"] != CAPABILITY or
                type(instruction["name"]) is not str or not instruction["name"] or
                type(instruction["type"]) is not dict or
                instruction["effects"] != [] or
                type(instruction["source_location"]) is not dict or
                set(instruction["source_location"]) != {"document", "path"} or
                instruction["source_location"]["path"] != "$.term" or
                type(instruction["source_location"]["document"]) is not str or
                re.fullmatch(r"[0-9a-f]{64}", instruction["source_location"]["document"]) is None or
                instruction["id"] != digest({k: v for k, v in instruction.items() if k != "id"})):
            raise IRAdmissionError("invalid typed instruction or location")
        if type_json(parse_type(instruction["type"])) != instruction["type"]:
            raise IRAdmissionError("noncanonical instruction type")
        validate_typed_binding(ir["binding"], instruction["type"],
                               ir["binding_carriers"])
        beta = ir["resource"]
        if (type(beta) is not dict or
                set(beta) != {"step_bound", "candidate_bound", "ledger_entry_bound", "policy_edition"} or
                beta["policy_edition"] != RESOURCE_POLICY_EDITION or
                any(type(beta[x]) is not int or beta[x] < 0
                    for x in ("step_bound", "candidate_bound", "ledger_entry_bound")) or
                ir["id"] != digest({k: v for k, v in ir.items() if k != "id"})):
            raise IRAdmissionError("invalid resource or deterministic identity")
        return ir
    except (UnicodeDecodeError, ValueError, TypeError, KeyError, RecursionError, Diagnostic) as exc:
        raise IRAdmissionError("invalid IR envelope") from exc


def execute(ir: dict) -> dict:
    """Independent control flow for the one-node var fragment."""
    checked = parse(serialize(ir))
    beta = checked["resource"]
    progress = {"completed_steps": 0, "completed_candidate_checks": 0,
                "completed_ledger_entries": 0, "last_candidate_key": None,
                "ledger_prefix": []}
    if beta["step_bound"] == 0:
        terminal = {"tag": "resource_limit", "bound": copy.deepcopy(beta),
                    "progress": copy.deepcopy(progress)}
    else:
        progress["completed_steps"] = 1
        value = copy.deepcopy(checked["binding"])
        terminal = value if checked["instruction"]["type"].get("tag") == "outcome" else {
            "tag": "success", "value": value, "optional_witness": None}
    return {"terminal_outcome": terminal, "ordered_ledger": [],
            "resource_progress": progress}
