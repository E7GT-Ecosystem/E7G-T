"""Provisional two-instruction IR for two admitted named maps over var.

Full source replay material is carried inline. The independent IR executor
uses its own control flow; comparison is a separate explicit gate.
"""

from __future__ import annotations

import copy
import json

from e7_ir_var_b1 import lower as lower_var, parse as parse_var, serialize as serialize_var
from e7c_b1_canonical import canonical_bytes, canonical_key, digest, outcome, resource_limit
from e7c_b1_evaluator import Evaluator, evaluate
from e7c_b1_replay_checker import check_witness

EDITION = "E7-IR/0.2-named-map-var-B1-provisional"
CAPABILITY = "core.apply.named/0.2"
MAPS = {"strict_normalise": "strict", "total_identity": "total"}
MAX_BYTES = 1_000_000


class MapIRAdmissionError(ValueError):
    pass


def lower(document):
    source = Evaluator(document)
    term = source.term
    if (term.get("tag") != "apply" or term.get("declaration") not in MAPS or
            term.get("arg") != {"tag": "var", "name": "source_config"} or
            source.environment["maps"][term["declaration"]]["domain_policy"] != MAPS[term["declaration"]]):
        raise MapIRAdmissionError("only registered maps over source_config are admitted")
    child = copy.deepcopy(source.document)
    child["term"] = copy.deepcopy(term["arg"])
    witness = evaluate(source.document)["witness"]
    decl = source.environment["maps"][term["declaration"]]
    instruction = {"operator": CAPABILITY, "declaration": term["declaration"],
                   "source_type": copy.deepcopy(decl["source"]),
                   "target_type": copy.deepcopy(decl["target"]),
                   "map_edition": decl["map_edition"],
                   "domain_policy": decl["domain_policy"],
                   "effects": copy.deepcopy(source.static["effects"]),
                   "source_location": {"document": digest(source.document), "path": "$.term"}}
    instruction["id"] = digest(instruction)
    package = {"ir_edition": EDITION, "required_capabilities": [CAPABILITY],
               "instruction": instruction,
               "source_document": copy.deepcopy(source.document),
               "source_witness": witness, "argument_ir": lower_var(child),
               "source_document_digest": digest(source.document)}
    package["id"] = digest(package)
    return parse(serialize(package))


def serialize(package):
    try:
        encoded = canonical_bytes(package)
        if len(encoded) > MAX_BYTES:
            raise MapIRAdmissionError("size bound")
        return encoded
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise MapIRAdmissionError("canonical encoding") from exc


def parse(encoded):
    if type(encoded) is not bytes or len(encoded) > MAX_BYTES:
        raise MapIRAdmissionError("bounded bytes required")
    try:
        package = json.loads(encoded.decode("utf-8"))
        if canonical_bytes(package) != encoded or set(package) != {
            "ir_edition", "required_capabilities", "source_document", "source_witness",
            "argument_ir", "source_document_digest", "instruction", "id"
        } or package["ir_edition"] != EDITION or package["required_capabilities"] != [CAPABILITY]:
            raise MapIRAdmissionError("unsupported edition or shape")
        source = Evaluator(package["source_document"])
        term = source.term
        if (term.get("tag") != "apply" or term.get("declaration") not in MAPS or
                term.get("arg") != {"tag": "var", "name": "source_config"} or
                source.environment["maps"][term["declaration"]]["domain_policy"] != MAPS[term["declaration"]]):
            raise MapIRAdmissionError("unsupported typed term")
        decl = source.environment["maps"][term["declaration"]]
        instruction = package["instruction"]
        expected = {"operator": CAPABILITY, "declaration": term["declaration"],
                    "source_type": decl["source"], "target_type": decl["target"],
                    "map_edition": decl["map_edition"],
                    "domain_policy": decl["domain_policy"],
                    "effects": source.static["effects"],
                    "source_location": {"document": digest(source.document), "path": "$.term"}}
        if instruction != {**expected, "id": digest(expected)}:
            raise MapIRAdmissionError("typed map instruction mismatch")
        child = copy.deepcopy(source.document)
        child["term"] = copy.deepcopy(term["arg"])
        if (parse_var(serialize_var(package["argument_ir"])) != package["argument_ir"] or
                lower_var(child) != package["argument_ir"] or
                package["source_document_digest"] != digest(source.document) or
                package["id"] != digest({k: v for k, v in package.items() if k != "id"})):
            raise MapIRAdmissionError("argument or source identity mismatch")
        witness = package["source_witness"]
        if (check_witness(witness).get("status") != "accepted" or
                witness["evaluation_claim"]["term"] != term or
                witness["static_inputs"]["environment"] != source.environment or
                witness["runtime_inputs"] != {"values": source.values,
                                               "interpretation": source.interpretation} or
                witness["resource_input"]["beta"] != source.beta or
                witness["external_assumptions"] != source.document["external_assumptions"] or
                witness["rule_pins"]["outcome_extension_edition"] != source.document["pins"]["outcome_extension_edition"]):
            raise MapIRAdmissionError("incomplete or different source replay")
        return package
    except (TypeError, ValueError, KeyError, OverflowError, RecursionError, UnicodeDecodeError) as exc:
        raise MapIRAdmissionError("invalid strict map IR") from exc


def execute(package):
    checked = parse(serialize(package))
    source = checked["source_document"]
    beta = source["resource_policy"]
    progress = {"completed_steps": 0, "completed_candidate_checks": 0,
                "completed_ledger_entries": 0, "last_candidate_key": None,
                "ledger_prefix": []}
    ledger = []

    def result(terminal):
        progress["completed_ledger_entries"] = len(ledger)
        progress["ledger_prefix"] = copy.deepcopy(ledger)
        return {"terminal_outcome": terminal, "ordered_ledger": copy.deepcopy(ledger),
                "resource_progress": copy.deepcopy(progress)}

    def limit():
        return resource_limit(beta, progress)

    def append(atom, detail):
        if len(ledger) >= beta["ledger_entry_bound"]:
            return False
        ledger.append({"ordinal": len(ledger), "static_atom": atom, "detail": detail})
        progress["completed_ledger_entries"] = len(ledger)
        progress["ledger_prefix"] = copy.deepcopy(ledger)
        return True

    if beta["step_bound"] == 0:
        return result(limit())
    progress["completed_steps"] = 1  # outer apply precharge
    if beta["step_bound"] == 1:
        return result(limit())
    progress["completed_steps"] = 2  # var read
    value = copy.deepcopy(checked["argument_ir"]["binding"])
    name = checked["instruction"]["declaration"]
    decl = source["environment"]["maps"][name]
    record = source["interpretation"]["maps"][name]
    identity = {"domain_policy": decl["domain_policy"], "failure_family": decl["failure_family"],
                "map_declaration": name, "map_edition": decl["map_edition"],
                "outcome_extension": decl["outcome_extension"]}
    if not append({"dimension": "evidence", "payload": canonical_key(identity)},
                  {"declaration": name, "event": "map_attempt"}):
        return result(limit())
    if decl["domain_policy"] != "total":
        identity.pop("outcome_extension")
        if not append({"dimension": "partiality", "payload": canonical_key(identity)},
                      {"declaration": name, "event": "partial_map_attempt"}):
            return result(limit())
    if record["capability"] is not True:
        return result(outcome("unsupported", f"map:{name}"))
    if record["obligation"] != "resolved":
        return result(outcome("undetermined", f"map-domain:{name}"))
    match = next(row for row in record["cases"] if canonical_key(row["input"]) == canonical_key(value))
    if match["in_domain"] is not True:
        return result(outcome("domain_error", f"outside-domain:{name}"))
    if "output" not in match:
        return result(outcome("domain_error", f"no-target-value:{name}"))
    return result(outcome("success", copy.deepcopy(match["output"])))


def compare_replay(package):
    """Compare independently executed observables with the checked source claim."""
    actual = execute(package)
    claim = package["source_witness"]["evaluation_claim"]
    expected = {"terminal_outcome": copy.deepcopy(claim["terminal_outcome"]),
                "ordered_ledger": claim["ordered_ledger"],
                "resource_progress": claim["resource_progress"]}
    if expected["terminal_outcome"].get("tag") == "success":
        expected["terminal_outcome"]["optional_witness"] = None
    if actual != expected:
        raise MapIRAdmissionError("source and IR observation mismatch")
    return {"status": "matched_selected_fragment", "ir_result": actual,
            "source_witness_identifier": package["source_witness"]["identity"]["witness_identifier"]}
