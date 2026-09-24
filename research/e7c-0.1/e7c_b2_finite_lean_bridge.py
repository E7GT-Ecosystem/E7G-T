"""Selected finite B2/B1/IR observations encoded for an abstract Lean trace.

This checks an explicit relation for finite cases; it does not prove the
relation for all admitted source documents or encode full JSON in Lean.
"""

import copy
import hashlib
import json
from pathlib import Path

from e7_ir_success_sequence_b2 import compare_replay, lower
from e7c_b1_canonical import canonical_key, digest, outcome, resource_limit
from e7c_b1_evaluator import evaluate as evaluate_b1
from e7c_b1_replay_checker import check_witness as replay_b1
from e7c_success_sequence_b2 import evaluate_sequence
from e7c_success_sequence_checker_b2 import check_sequence

HERE = Path(__file__).resolve().parent
SEED = HERE / "fixtures/wp5_ir/success_sequence_ir.json"
EDITION = "E7C-B2-LEAN-FINITE-BRIDGE/0.1-provisional"
NAMES = ("success_strict", "success_total", "continuation_domain_error",
         "first_unsupported", "first_undetermined", "child_step_limit",
         "continuation_step_limit", "zero_bound", "first_ledger_limit",
         "continuation_ledger_limit", "partiality_ledger_limit",
         "continuation_unsupported", "continuation_undetermined")


def _source(seed, name):
    source = copy.deepcopy(seed)
    first = source["interpretation"]["maps"]["total_identity"]
    next_map = source["interpretation"]["maps"]["strict_normalise"]
    beta = source["resource_policy"]
    if name == "success_total":
        source["term"]["then_map"] = "total_identity"
    elif name == "continuation_domain_error":
        source["values"]["source_config"] = next(
            row["input"] for row in next_map["cases"] if row["in_domain"] is False)
    elif name == "first_unsupported":
        first["capability"] = False
    elif name == "first_undetermined":
        first["obligation"] = "unresolved"
    elif name == "child_step_limit":
        beta["step_bound"] = 2
    elif name == "continuation_step_limit":
        beta["step_bound"] = 3
    elif name == "zero_bound":
        beta["step_bound"] = 0
    elif name == "first_ledger_limit":
        beta["ledger_entry_bound"] = 0
    elif name == "continuation_ledger_limit":
        beta["ledger_entry_bound"] = 1
    elif name == "partiality_ledger_limit":
        beta["ledger_entry_bound"] = 2
    elif name == "continuation_unsupported":
        next_map["capability"] = False
    elif name == "continuation_undetermined":
        next_map["obligation"] = "unresolved"
    elif name != "success_strict":
        raise ValueError("unselected vector")
    return source


def _progress(steps, ledger):
    return {"completed_steps": steps, "completed_candidate_checks": 0,
            "completed_ledger_entries": len(ledger), "last_candidate_key": None,
            "ledger_prefix": copy.deepcopy(ledger)}


def _check_ledger(ledger):
    assert all(entry["ordinal"] == index for index, entry in enumerate(ledger))


def _terminal_signature(terminal):
    if terminal["tag"] == "resource_limit":
        return {"tag": "resource_limit"}
    return {key: value for key, value in terminal.items() if key != "optional_witness"}


def _trace(terminal, steps, ledger):
    _check_ledger(ledger)
    return {"exit": _terminal_signature(terminal), "steps": steps,
            "ledger": [{"static_atom": e["static_atom"], "detail": e["detail"]}
                       for e in ledger]}


def _expected(source, child, tail):
    beta = source["resource_policy"]
    bound = beta["step_bound"]
    if bound == 0:
        terminal, steps, ledger = resource_limit(beta, _progress(0, [])), 0, []
    else:
        child_terminal = child["terminal_outcome"]
        steps = 1 + child["resource_progress"]["completed_steps"]
        ledger = copy.deepcopy(child["ordered_ledger"])
        if child_terminal["tag"] == "resource_limit" or (
                child_terminal["tag"] == "success" and steps >= bound):
            terminal = resource_limit(beta, _progress(steps, ledger))
        elif child_terminal["tag"] != "success":
            terminal = copy.deepcopy(child_terminal)
        else:
            assert tail is not None
            steps += 1
            offset = len(ledger)
            ledger.extend({**copy.deepcopy(entry), "ordinal": offset + index}
                          for index, entry in enumerate(tail["ordered_ledger"]))
            _check_ledger(ledger)
            direct = tail["terminal_outcome"]
            if direct["tag"] == "resource_limit":
                terminal = resource_limit(beta, _progress(steps, ledger))
            elif direct["tag"] == "success":
                terminal = outcome("success", direct["value"])
            else:
                payload = next(direct[key] for key in ("diagnostic", "capability", "obligation")
                               if key in direct)
                terminal = outcome(direct["tag"], payload)
    return {"terminal_outcome": terminal, "ordered_ledger": ledger,
            "resource_progress": _progress(steps, ledger)}


def _render_trace(trace, values, diagnostics, events):
    exit_ = trace["exit"]
    tag = exit_["tag"]
    if tag == "success":
        code = values[canonical_key(exit_["value"])]
        encoded = f".success {code}"
    elif tag == "resource_limit":
        encoded = ".resourceLimit"
    else:
        payload = next(exit_[key] for key in ("diagnostic", "capability", "obligation")
                       if key in exit_)
        lean_tag = {"domain_error": "domainError", "unsupported": "unsupported",
                    "undetermined": "undetermined"}[tag]
        encoded = f".{lean_tag} {diagnostics[canonical_key(payload)]}"
    ledger = ", ".join(str(events[canonical_key(e)]) for e in trace["ledger"])
    return (f"({{ exit := {encoded}, steps := {trace['steps']}, ledger := [{ledger}] }}"
            " : E7CB2Sequence.Trace Nat)")


def build():
    raw = SEED.read_bytes()
    seed = json.loads(raw)["source_document"]
    rows = []
    for name in NAMES:
        source = _source(seed, name)
        result = evaluate_sequence(source)
        witness = result["witness"]
        assert check_sequence(witness)["status"] == "accepted"
        ir = lower(source)
        assert compare_replay(ir)["ir_result"] == witness["claim"]
        bound = source["resource_policy"]["step_bound"]
        child_witness = witness["child_witness"]
        if child_witness is None:
            assert bound == 0
            child = {"terminal_outcome": {"tag": "resource_limit"},
                     "resource_progress": _progress(0, []), "ordered_ledger": []}
        else:
            assert replay_b1(child_witness)["status"] == "accepted"
            child = child_witness["evaluation_claim"]
        tail = None
        child_terminal = child["terminal_outcome"]
        if (bound > 0 and child_terminal["tag"] == "success" and
                1 + child["resource_progress"]["completed_steps"] < bound):
            # Independently evaluate a B1 direct map at the child value. Its
            # variable read is already paid by the child; the B2 continuation
            # charges just the map step. B1's two charges are validated below.
            direct = {key: copy.deepcopy(value) for key, value in source.items()
                      if key != "edition"}
            direct["term"] = {"tag": "apply", "declaration": source["term"]["then_map"],
                              "arg": {"tag": "var", "name": "source_config"}}
            direct["values"]["source_config"] = copy.deepcopy(child_terminal["value"])
            direct["resource_policy"]["step_bound"] = 2
            direct["resource_policy"]["ledger_entry_bound"] -= len(child["ordered_ledger"])
            tail = evaluate_b1(direct)
            assert replay_b1(tail["witness"])["status"] == "accepted"
            assert tail["resource_progress"]["completed_steps"] == 2
        expected = _expected(source, child, tail)
        assert expected == witness["claim"]
        # The Lean trace erases the full resource-limit payload and B1 success
        # witness pointer only after the exact JSON observation has matched.
        child_trace = _trace(child["terminal_outcome"],
                             child["resource_progress"]["completed_steps"],
                             child["ordered_ledger"])
        dummy = {"exit": {"tag": "resource_limit"}, "steps": 0, "ledger": []}
        tail_trace = (_trace(tail["terminal_outcome"], 0, tail["ordered_ledger"])
                      if tail is not None else dummy)
        target_trace = _trace(expected["terminal_outcome"],
                              expected["resource_progress"]["completed_steps"],
                              expected["ordered_ledger"])
        rows.append({"case": name, "source_digest": digest(source),
                     "source_witness": witness["id"],
                     "direct_b1_witness": tail["witness"]["identity"]["witness_identifier"]
                     if tail is not None else None,
                     "source_claim": expected,
                     "child_trace": child_trace, "tail_trace": tail_trace,
                     "target_trace": target_trace, "bound": bound})
    traces = [row[key] for row in rows
              for key in ("child_trace", "tail_trace", "target_trace")]
    values = sorted({canonical_key(t["exit"]["value"]) for t in traces
                     if t["exit"]["tag"] == "success"})
    diagnostics = sorted({canonical_key(next(t["exit"][k] for k in
                                           ("diagnostic", "capability", "obligation")
                                           if k in t["exit"])) for t in traces
                          if t["exit"]["tag"] in ("unsupported", "undetermined", "domain_error")})
    events = sorted({canonical_key(e) for t in traces for e in t["ledger"]})
    value_codes = {key: i for i, key in enumerate(values)}
    diagnostic_codes = {key: i for i, key in enumerate(diagnostics)}
    event_codes = {key: i for i, key in enumerate(events)}
    lines = ["import E7CB2Sequence", "", "/- Generated finite vectors from complete B2/B1/IR replay.",
             "   Equality here is for the encoded abstract traces only. -/", ""]
    for row in rows:
        child = _render_trace(row["child_trace"], value_codes, diagnostic_codes, event_codes)
        tail = _render_trace(row["tail_trace"], value_codes, diagnostic_codes, event_codes)
        target = _render_trace(row["target_trace"], value_codes, diagnostic_codes, event_codes)
        lines += [f"-- {row['case']}", "example :", f"    E7CB2Sequence.sequence {row['bound']} {child}",
                  f"      (fun _ => {tail}) =", f"    {target} := by decide", ""]
    manifest = {"edition": EDITION, "seed_sha256": hashlib.sha256(raw).hexdigest(),
                "source_authority": "E7G-T-v0.12.1/RGP2-experimental",
                "claim": "finite encoded observations, no general Python/Lean theorem",
                "value_codes": values, "diagnostic_codes": diagnostics,
                "event_codes": events, "cases": rows}
    return manifest, "\n".join(lines)
