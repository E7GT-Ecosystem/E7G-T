"""Provisional two-instruction IR for source-preserving and lossy views.

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

EDITION = "E7-IR/0.2-view-var-B1-provisional"
CAPABILITY = "core.view.named/0.2"
VIEWS = {"source_preserving_inventory": "source_preserving",
         "lossy_projection": "projection"}
MAX_BYTES = 1_000_000


class ViewIRAdmissionError(ValueError):
    pass


def lower(document):
    source = Evaluator(document)
    term = source.term
    if (term.get("tag") != "view" or term.get("declaration") not in VIEWS or
            term.get("arg") != {"tag": "var", "name": "source_config"} or
            source.environment["views"][term["declaration"]]["kind"] != VIEWS[term["declaration"]]):
        raise ViewIRAdmissionError("only registered views over source_config are admitted")
    child = copy.deepcopy(source.document)
    child["term"] = copy.deepcopy(term["arg"])
    witness = evaluate(source.document)["witness"]
    decl = source.environment["views"][term["declaration"]]
    instruction = {"operator": CAPABILITY, "declaration": term["declaration"],
                   "source_type": copy.deepcopy(decl["source"]),
                   "target_type": copy.deepcopy(decl["target"]),
                   "kind": decl["kind"], "inquiry": decl["inquiry"],
                   "preserved_observations": copy.deepcopy(decl["preserved_observations"]),
                   "excluded_observations": copy.deepcopy(decl["excluded_observations"]),
                   "quotient_relation": decl["quotient_relation"],
                   "reconstruction_obligation": decl["reconstruction_obligation"],
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
            raise ViewIRAdmissionError("size bound")
        return encoded
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ViewIRAdmissionError("canonical encoding") from exc


def parse(encoded):
    if type(encoded) is not bytes or len(encoded) > MAX_BYTES:
        raise ViewIRAdmissionError("bounded bytes required")
    try:
        package = json.loads(encoded.decode("utf-8"))
        if canonical_bytes(package) != encoded or set(package) != {
            "ir_edition", "required_capabilities", "source_document", "source_witness",
            "argument_ir", "source_document_digest", "instruction", "id"
        } or package["ir_edition"] != EDITION or package["required_capabilities"] != [CAPABILITY]:
            raise ViewIRAdmissionError("unsupported edition or shape")
        source = Evaluator(package["source_document"])
        term = source.term
        if (term.get("tag") != "view" or term.get("declaration") not in VIEWS or
                term.get("arg") != {"tag": "var", "name": "source_config"} or
                source.environment["views"][term["declaration"]]["kind"] != VIEWS[term["declaration"]]):
            raise ViewIRAdmissionError("unsupported typed term")
        decl = source.environment["views"][term["declaration"]]
        instruction = package["instruction"]
        expected = {"operator": CAPABILITY, "declaration": term["declaration"],
                    "source_type": decl["source"], "target_type": decl["target"],
                    "kind": decl["kind"], "inquiry": decl["inquiry"],
                    "preserved_observations": decl["preserved_observations"],
                    "excluded_observations": decl["excluded_observations"],
                    "quotient_relation": decl["quotient_relation"],
                    "reconstruction_obligation": decl["reconstruction_obligation"],
                    "effects": source.static["effects"],
                    "source_location": {"document": digest(source.document), "path": "$.term"}}
        if instruction != {**expected, "id": digest(expected)}:
            raise ViewIRAdmissionError("typed view instruction mismatch")
        child = copy.deepcopy(source.document)
        child["term"] = copy.deepcopy(term["arg"])
        if (parse_var(serialize_var(package["argument_ir"])) != package["argument_ir"] or
                lower_var(child) != package["argument_ir"] or
                package["source_document_digest"] != digest(source.document) or
                package["id"] != digest({k: v for k, v in package.items() if k != "id"})):
            raise ViewIRAdmissionError("argument or source identity mismatch")
        witness = package["source_witness"]
        if (check_witness(witness).get("status") != "accepted" or
                witness["evaluation_claim"]["term"] != term or
                witness["static_inputs"]["environment"] != source.environment or
                witness["runtime_inputs"] != {"values": source.values,
                                               "interpretation": source.interpretation} or
                witness["resource_input"]["beta"] != source.beta or
                witness["external_assumptions"] != source.document["external_assumptions"] or
                witness["rule_pins"]["outcome_extension_edition"] != source.document["pins"]["outcome_extension_edition"]):
            raise ViewIRAdmissionError("incomplete or different source replay")
        return package
    except (TypeError, ValueError, KeyError, OverflowError, RecursionError, UnicodeDecodeError) as exc:
        raise ViewIRAdmissionError("invalid view IR") from exc


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
    progress["completed_steps"] = 1  # outer view precharge
    if beta["step_bound"] == 1:
        return result(limit())
    progress["completed_steps"] = 2  # var read
    value = copy.deepcopy(checked["argument_ir"]["binding"])
    name = checked["instruction"]["declaration"]
    decl = source["environment"]["views"][name]
    record = source["interpretation"]["views"][name]
    detail = {"declaration": name, "event": "view",
              "preserved_observations": sorted(set(decl["preserved_observations"])),
              "excluded_observations": sorted(set(decl["excluded_observations"])),
              "quotient_relation": decl["quotient_relation"]}
    if not append({"dimension": "inquiry", "payload": decl["inquiry"]}, detail):
        return result(limit())
    if decl["kind"] == "projection":
        loss = {"excluded": sorted(set(decl["excluded_observations"])),
                "preserved": sorted(set(decl["preserved_observations"])),
                "quotient_relation": decl["quotient_relation"]}
        if not append({"dimension": "loss", "payload": canonical_key(loss)},
                      {"declaration": name, "event": "projection_loss"}):
            return result(limit())
    if not append({"dimension": "alternatives", "payload": decl["reconstruction_obligation"]},
                  {"declaration": name, "event": "reconstruction_boundary"}):
        return result(limit())
    if record["capability"] is not True:
        return result(outcome("unsupported", f"view:{name}"))
    if record["obligation"] != "resolved":
        return result(outcome("undetermined", f"view:{name}"))
    match = next(row for row in record["cases"] if canonical_key(row["input"]) == canonical_key(value))
    return result(outcome("success", {"kind": decl["kind"], "declaration": name,
                                      "representation": copy.deepcopy(match["output"]),
                                      "source_return_token": copy.deepcopy(value)
                                      if decl["kind"] == "source_preserving" else None}))


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
        raise ViewIRAdmissionError("source and IR observation mismatch")
    return {"status": "matched_selected_fragment", "ir_result": actual,
            "source_witness_identifier": package["source_witness"]["identity"]["witness_identifier"]}
