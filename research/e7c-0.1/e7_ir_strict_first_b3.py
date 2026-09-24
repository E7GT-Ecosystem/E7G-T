"""Versioned independent IR execution for the selected B3 strict-first sequence."""

from __future__ import annotations

import copy
import json

from e7_ir_var_b1 import lower as lower_var, parse as parse_var, serialize as serialize_var
from e7c_b1_canonical import canonical_bytes, canonical_key, digest, outcome, resource_limit
from e7c_strict_first_b3 import EDITION as SOURCE_EDITION, FIRST, admit, evaluate_sequence
from e7c_strict_first_checker_b3 import check_sequence

EDITION = "E7-IR/0.4-strict-first-B3-provisional"
CAPABILITY = "core.sequence.strict-first/0.4"
MAX_BYTES = 1_000_000


class SequenceIRAdmissionError(ValueError):
    pass


def _var_document(source):
    document = {key: copy.deepcopy(value) for key, value in source.items() if key != "edition"}
    document["term"] = copy.deepcopy(FIRST["arg"])
    return document


def _instruction(source, static):
    env = source["environment"]
    continuation = source["term"]["then_map"]
    first = env["maps"]["strict_normalise"]
    next_map = env["maps"][continuation]
    node = {"operator": CAPABILITY, "first_map": "strict_normalise",
            "then_map": continuation, "source_edition": SOURCE_EDITION,
            "input_type": copy.deepcopy(first["source"]),
            "intermediate_type": copy.deepcopy(first["target"]),
            "output_type": copy.deepcopy(next_map["target"]),
            "first_map_edition": first["map_edition"],
            "then_map_edition": next_map["map_edition"],
            "then_domain_policy": next_map["domain_policy"],
            "effects": copy.deepcopy(static["effects"]),
            "source_location": {"document": digest(source), "path": "$.term"}}
    node["id"] = digest(node)
    return node


def lower(document):
    _, _, static = admit(document)
    result = evaluate_sequence(document)
    package = {"ir_edition": EDITION, "required_capabilities": [CAPABILITY],
               "instruction": _instruction(document, static),
               "argument_ir": lower_var(_var_document(document)),
               "source_document": copy.deepcopy(document),
               "source_witness": result["witness"]}
    package["id"] = digest(package)
    return parse(serialize(package))


def serialize(package):
    try:
        encoded = canonical_bytes(package)
        if len(encoded) > MAX_BYTES:
            raise SequenceIRAdmissionError("size bound")
        return encoded
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise SequenceIRAdmissionError("canonical encoding") from exc


def parse(encoded):
    if type(encoded) is not bytes or len(encoded) > MAX_BYTES:
        raise SequenceIRAdmissionError("bounded bytes required")
    try:
        package = json.loads(encoded.decode("utf-8"))
        if (canonical_bytes(package) != encoded or set(package) != {
                "ir_edition", "required_capabilities", "instruction", "argument_ir",
                "source_document", "source_witness", "id"} or
                package["ir_edition"] != EDITION or
                package["required_capabilities"] != [CAPABILITY]):
            raise SequenceIRAdmissionError("unsupported edition or shape")
        source = package["source_document"]
        _, _, static = admit(source)
        if (package["instruction"] != _instruction(source, static) or
                parse_var(serialize_var(package["argument_ir"])) != package["argument_ir"] or
                package["argument_ir"] != lower_var(_var_document(source)) or
                package["source_witness"]["source_document"] != source or
                check_sequence(package["source_witness"]).get("status") != "accepted" or
                package["id"] != digest({k: v for k, v in package.items() if k != "id"})):
            raise SequenceIRAdmissionError("typed instruction, replay or binding mismatch")
        return package
    except (TypeError, ValueError, KeyError, OverflowError, UnicodeDecodeError, RecursionError) as exc:
        raise SequenceIRAdmissionError("invalid success-sequence IR") from exc


def execute(package):
    checked = parse(serialize(package))
    document = checked["source_document"]
    beta = document["resource_policy"]
    ledger = []
    steps = 0

    def progress():
        return {"completed_steps": steps, "completed_candidate_checks": 0,
                "completed_ledger_entries": len(ledger), "last_candidate_key": None,
                "ledger_prefix": copy.deepcopy(ledger)}

    def finish(terminal):
        return {"terminal_outcome": terminal, "ordered_ledger": copy.deepcopy(ledger),
                "resource_progress": progress()}

    def limit():
        return resource_limit(beta, progress())

    def charge():
        nonlocal steps
        if steps >= beta["step_bound"]:
            return False
        steps += 1
        return True

    def append(atom, detail):
        if len(ledger) >= beta["ledger_entry_bound"]:
            return False
        ledger.append({"ordinal": len(ledger), "static_atom": atom, "detail": detail})
        return True

    if not charge():  # explicit sequence
        return finish(limit())
    if not charge():  # inner strict map
        return finish(limit())
    if not charge():  # var read
        return finish(limit())
    value = copy.deepcopy(checked["argument_ir"]["binding"])
    env = document["environment"]
    tables = document["interpretation"]["maps"]
    first = env["maps"]["strict_normalise"]
    first_atom = {"dimension": "evidence", "payload": canonical_key({
        "domain_policy": first["domain_policy"], "failure_family": first["failure_family"],
        "map_declaration": "strict_normalise", "map_edition": first["map_edition"],
        "outcome_extension": first["outcome_extension"]})}
    if not append(first_atom, {"declaration": "strict_normalise", "event": "map_attempt"}):
        return finish(limit())
    first_partial = {"dimension": "partiality", "payload": canonical_key({
        "domain_policy": first["domain_policy"], "failure_family": first["failure_family"],
        "map_declaration": "strict_normalise", "map_edition": first["map_edition"]})}
    if not append(first_partial, {"declaration": "strict_normalise", "event": "partial_map_attempt"}):
        return finish(limit())
    first_table = tables["strict_normalise"]
    if first_table["capability"] is not True:
        return finish(outcome("unsupported", "map:strict_normalise"))
    if first_table["obligation"] != "resolved":
        return finish(outcome("undetermined", "map-domain:strict_normalise"))
    first_case = next(item for item in first_table["cases"]
                      if canonical_key(item["input"]) == canonical_key(value))
    if first_case["in_domain"] is not True:
        return finish(outcome("domain_error", "outside-domain:strict_normalise"))
    if "output" not in first_case:
        return finish(outcome("domain_error", "no-target-value:strict_normalise"))
    value = copy.deepcopy(first_case["output"])
    if not charge():  # continuation begins only after inner success
        return finish(limit())
    name = checked["instruction"]["then_map"]
    decl = env["maps"][name]
    table = tables[name]
    identity = {"domain_policy": decl["domain_policy"],
                "failure_family": decl["failure_family"],
                "map_declaration": name, "map_edition": decl["map_edition"],
                "outcome_extension": decl["outcome_extension"]}
    if not append({"dimension": "evidence", "payload": canonical_key(identity)},
                  {"declaration": name, "event": "map_attempt"}):
        return finish(limit())
    if decl["domain_policy"] != "total":
        identity.pop("outcome_extension")
        if not append({"dimension": "partiality", "payload": canonical_key(identity)},
                      {"declaration": name, "event": "partial_map_attempt"}):
            return finish(limit())
    if table["capability"] is not True:
        return finish(outcome("unsupported", f"map:{name}"))
    if table["obligation"] != "resolved":
        return finish(outcome("undetermined", f"map-domain:{name}"))
    case = next(item for item in table["cases"] if canonical_key(item["input"]) == canonical_key(value))
    if case["in_domain"] is not True:
        return finish(outcome("domain_error", f"outside-domain:{name}"))
    if "output" not in case:
        return finish(outcome("domain_error", f"no-target-value:{name}"))
    return finish(outcome("success", copy.deepcopy(case["output"])))


def compare_replay(package):
    actual = execute(package)
    expected = copy.deepcopy(package["source_witness"]["claim"])
    if actual != expected:
        raise SequenceIRAdmissionError("source B3 and IR observation mismatch")
    return {"status": "matched_selected_strict_first", "ir_result": actual,
            "source_witness_identifier": package["source_witness"]["id"]}
