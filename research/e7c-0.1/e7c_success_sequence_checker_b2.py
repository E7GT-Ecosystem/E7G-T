"""Separately coded B2 success-sequence replay over complete B1 child witness."""

from __future__ import annotations

import copy

from e7c_b1_canonical import canonical_key, digest, outcome, require_canonical_json, resource_limit
from e7c_b1_replay_checker import check_witness as check_b1
from e7c_success_sequence_b2 import WITNESS_EDITION, admit


def _progress(steps, entries):
    return {"completed_steps": steps, "completed_candidate_checks": 0,
            "completed_ledger_entries": len(entries), "last_candidate_key": None,
            "ledger_prefix": copy.deepcopy(entries)}


def check_sequence(witness):
    try:
        require_canonical_json(witness)
        if (type(witness) is not dict or set(witness) != {
                "edition", "source_document", "static_judgement", "child_witness", "claim", "id"} or
                witness["edition"] != WITNESS_EDITION or
                witness["id"] != digest({k: v for k, v in witness.items() if k != "id"})):
            raise ValueError("malformed or changed sequence envelope")
        document = witness["source_document"]
        child, source, static = admit(document)
        if witness["static_judgement"] != static:
            raise ValueError("static judgement mismatch")
        beta = source.beta
        entries = []
        if beta["step_bound"] == 0:
            if witness["child_witness"] is not None:
                raise ValueError("unreached child witness")
            steps = 0
            terminal = resource_limit(beta, _progress(steps, entries))
        else:
            child["resource_policy"]["step_bound"] -= 1
            inner = witness["child_witness"]
            if (check_b1(inner).get("status") != "accepted" or
                    inner["evaluation_claim"]["term"] != child["term"] or
                    inner["static_inputs"]["environment"] != child["environment"] or
                    inner["runtime_inputs"] != {"values": child["values"],
                                                "interpretation": child["interpretation"]} or
                    inner["resource_input"]["beta"] != child["resource_policy"] or
                    inner["external_assumptions"] != child["external_assumptions"] or
                    inner["rule_pins"]["outcome_extension_edition"] != child["pins"]["outcome_extension_edition"]):
                raise ValueError("child does not replay the pinned input")
            child_claim = inner["evaluation_claim"]
            steps = child_claim["resource_progress"]["completed_steps"] + 1
            entries = copy.deepcopy(child_claim["ordered_ledger"])
            terminal = copy.deepcopy(child_claim["terminal_outcome"])
            if terminal["tag"] == "resource_limit":
                terminal = resource_limit(beta, _progress(steps, entries))
            elif terminal["tag"] == "success":
                if steps >= beta["step_bound"]:
                    terminal = resource_limit(beta, _progress(steps, entries))
                else:
                    steps += 1
                    name = document["term"]["then_map"]
                    decl = source.environment["maps"][name]
                    interpretation = source.interpretation["maps"][name]
                    evidence = {"domain_policy": decl["domain_policy"],
                                "failure_family": decl["failure_family"],
                                "map_declaration": name,
                                "map_edition": decl["map_edition"],
                                "outcome_extension": decl["outcome_extension"]}

                    def record(atom, detail):
                        if len(entries) >= beta["ledger_entry_bound"]:
                            return False
                        entries.append({"ordinal": len(entries), "static_atom": atom,
                                        "detail": detail})
                        return True

                    if not record({"dimension": "evidence", "payload": canonical_key(evidence)},
                                  {"declaration": name, "event": "map_attempt"}):
                        terminal = resource_limit(beta, _progress(steps, entries))
                    else:
                        if decl["domain_policy"] == "total":
                            recorded = True
                        else:
                            evidence.pop("outcome_extension")
                            recorded = record({"dimension": "partiality",
                                               "payload": canonical_key(evidence)},
                                              {"declaration": name, "event": "partial_map_attempt"})
                        if not recorded:
                            terminal = resource_limit(beta, _progress(steps, entries))
                        elif interpretation["capability"] is not True:
                            terminal = outcome("unsupported", f"map:{name}")
                        elif interpretation["obligation"] != "resolved":
                            terminal = outcome("undetermined", f"map-domain:{name}")
                        else:
                            value = child_claim["terminal_outcome"]["value"]
                            case = next(item for item in interpretation["cases"]
                                        if canonical_key(item["input"]) == canonical_key(value))
                            if case["in_domain"] is not True:
                                terminal = outcome("domain_error", f"outside-domain:{name}")
                            elif "output" not in case:
                                terminal = outcome("domain_error", f"no-target-value:{name}")
                            else:
                                terminal = outcome("success", case["output"])
        expected = {"terminal_outcome": terminal, "ordered_ledger": entries,
                    "resource_progress": _progress(steps, entries)}
        if expected != witness["claim"]:
            raise ValueError("sequence claim mismatch")
        return {"status": "accepted", "witness_identifier": witness["id"]}
    except (TypeError, KeyError, ValueError, OverflowError, StopIteration, RecursionError) as exc:
        return {"status": "rejected", "diagnostic": "sequence_replay_mismatch",
                "detail": str(exc)}
