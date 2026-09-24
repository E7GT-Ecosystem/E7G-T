"""Opt-in E7C-B3 sequencing of a strict first map into a total map.

The accepted B1 grammar and evaluator remain unchanged. This small successor
uses an explicit constructor; it cannot consume a failure as a value.
"""

from __future__ import annotations

import copy

from e7c_b1_canonical import canonical_key, digest, outcome, resource_limit, require_canonical_json
from e7c_b1_evaluator import Evaluator, evaluate
from e7c_b1_static import Checker, Diagnostic

EDITION = "E7C-B3/0.1-strict-first-provisional"
WITNESS_EDITION = "e7c-b3-strict-first-witness-0.1-provisional"
FIRST = {"tag": "apply", "declaration": "strict_normalise",
         "arg": {"tag": "var", "name": "source_config"}}
CONTINUATIONS = {"total_identity_b": "total"}


class SequenceAdmissionError(ValueError):
    pass


def admit(document):
    try:
        require_canonical_json(document)
        if type(document) is not dict or set(document) != {
                "edition", "environment", "term", "values", "interpretation",
                "resource_policy", "pins", "external_assumptions"} or document["edition"] != EDITION:
            raise SequenceAdmissionError("wrong successor edition or source shape")
        term = document["term"]
        if (type(term) is not dict or set(term) != {"tag", "first", "then_map"} or
                term["tag"] != "sequence_success" or term["first"] != FIRST or
                term["then_map"] not in CONTINUATIONS):
            raise SequenceAdmissionError("unsupported explicit success sequence")
        child = {key: copy.deepcopy(value) for key, value in document.items()
                 if key != "edition"}
        child["term"] = copy.deepcopy(FIRST)
        source = Evaluator(child)  # B1 checks full runtime and interpretation admission.
        env = source.environment
        first = env["maps"]["strict_normalise"]
        next_map = env["maps"][term["then_map"]]
        first_type = Checker(env).check(FIRST).type
        if (first["domain_policy"] != "strict" or
                next_map["domain_policy"] != CONTINUATIONS[term["then_map"]] or
                first_type.tag != "outcome" or
                first_type.args[0].render() != 'Config["Sigma-B"]' or
                first["target"] != next_map["source"] or
                first["target"] != next_map["target"] or
                first["outcome_extension"] != next_map["outcome_extension"]):
            raise SequenceAdmissionError("typed continuation or outcome edition mismatch")
        if any(row.get("in_domain") is not True or row.get("output") != row.get("input")
               for row in source.interpretation["maps"]["total_identity_b"]["cases"]):
            raise SequenceAdmissionError("second map is not total identity on the finite carrier")
        # Static checking only: a fresh variable stands for the successful
        # first result. It is never admitted as a runtime source binding.
        virtual_env = copy.deepcopy(env)
        virtual_env["variables"]["_b3_result"] = copy.deepcopy(first["target"])
        outer = Checker(virtual_env).check({"tag": "apply", "declaration": term["then_map"],
                                             "arg": {"tag": "var", "name": "_b3_result"}})
        child_static = Checker(env).check(FIRST)
        effects = sorted(set(child_static.effects) | set(outer.effects))
        static = {"type": outer.type.render(),
                  "effects": [{"dimension": item.dimension, "payload": item.payload}
                              for item in effects]}
        return child, source, static
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError, Diagnostic) as exc:
        raise SequenceAdmissionError("invalid success sequence input") from exc


def _progress(steps, ledger):
    return {"completed_steps": steps, "completed_candidate_checks": 0,
            "completed_ledger_entries": len(ledger), "last_candidate_key": None,
            "ledger_prefix": copy.deepcopy(ledger)}


def evaluate_sequence(document):
    child, source, static = admit(document)
    beta = source.beta
    ledger = []
    if beta["step_bound"] == 0:
        progress = _progress(0, ledger)
        terminal = resource_limit(beta, progress)
        child_witness = None  # parent step was never charged
    else:
        child["resource_policy"]["step_bound"] = beta["step_bound"] - 1
        first = evaluate(child)
        child_witness = first["witness"]
        ledger = copy.deepcopy(first["ordered_ledger"])
        steps = first["resource_progress"]["completed_steps"] + 1
        progress = _progress(steps, ledger)
        terminal = copy.deepcopy(first["terminal_outcome"])
        if terminal["tag"] == "resource_limit":
            terminal = resource_limit(beta, progress)
        elif terminal["tag"] == "success":
            if steps >= beta["step_bound"]:
                terminal = resource_limit(beta, progress)
            else:
                steps += 1  # continuation step charged before ledger/guard
                progress = _progress(steps, ledger)
                name = document["term"]["then_map"]
                decl = source.environment["maps"][name]
                record = source.interpretation["maps"][name]
                identity = {"domain_policy": decl["domain_policy"],
                            "failure_family": decl["failure_family"],
                            "map_declaration": name, "map_edition": decl["map_edition"],
                            "outcome_extension": decl["outcome_extension"]}

                def append(atom, detail):
                    if len(ledger) >= beta["ledger_entry_bound"]:
                        return False
                    ledger.append({"ordinal": len(ledger), "static_atom": atom, "detail": detail})
                    return True

                if not append({"dimension": "evidence", "payload": canonical_key(identity)},
                              {"declaration": name, "event": "map_attempt"}):
                    terminal = resource_limit(beta, _progress(steps, ledger))
                else:
                    if decl["domain_policy"] != "total":
                        identity.pop("outcome_extension")
                        appended = append({"dimension": "partiality", "payload": canonical_key(identity)},
                                          {"declaration": name, "event": "partial_map_attempt"})
                    else:
                        appended = True
                    if not appended:
                        terminal = resource_limit(beta, _progress(steps, ledger))
                    elif record["capability"] is not True:
                        terminal = outcome("unsupported", f"map:{name}")
                    elif record["obligation"] != "resolved":
                        terminal = outcome("undetermined", f"map-domain:{name}")
                    else:
                        value = first["terminal_outcome"]["value"]
                        case = next(row for row in record["cases"]
                                    if canonical_key(row["input"]) == canonical_key(value))
                        if case["in_domain"] is not True:
                            terminal = outcome("domain_error", f"outside-domain:{name}")
                        elif "output" not in case:
                            terminal = outcome("domain_error", f"no-target-value:{name}")
                        else:
                            terminal = outcome("success", case["output"])
                progress = _progress(steps, ledger)
    claim = {"terminal_outcome": copy.deepcopy(terminal),
             "ordered_ledger": copy.deepcopy(ledger),
             "resource_progress": copy.deepcopy(progress)}
    envelope = {"edition": WITNESS_EDITION, "source_document": copy.deepcopy(document),
                "static_judgement": static, "child_witness": child_witness,
                "claim": claim}
    envelope["id"] = digest(envelope)
    return {**claim, "witness": envelope}
