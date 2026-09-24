"""Finite source/IR observations encoded into the abstract B2 Lean control.

The code erases JSON values and event payloads only after exact replay and
three-way conservation checks. It proves no general refinement theorem.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from e7c_b1_canonical import canonical_key, digest
from e7c_eecq_two_stage_b1 import conserves, document, evaluate
from e7_ir_eecq_two_stage_b1 import compare_replay, lower
from test_e7_ir_eecq_two_stage_b1 import FIXTURE, selected

HERE = Path(__file__).resolve().parent
LEAN = HERE / "proof-packages/lean-core/E7CEECQTwoStageBridge.lean"
MANIFEST = HERE / "fixtures/wp5_ir/eecq_two_stage_lean_manifest.json"
EDITION = "E7C-EECQ-TWO-STAGE-LEAN-BRIDGE/0.1-provisional"
CASES = ("success", "same_marginals_alternative", "first_unsupported",
         "second_unsupported", "second_undetermined", "zero_bound",
         "first_resource_limit", "second_pre_step_limit",
         "second_row_limit", "second_ledger_limit")


def _source(name):
    kwargs = {"step_bound": 20, "ledger_bound": 20}
    if name == "same_marginals_alternative":
        return document(selected(swapped=True), **kwargs)
    if name == "first_unsupported":
        kwargs["first_capability"] = False
    elif name == "second_unsupported":
        kwargs["second_capability"] = False
    elif name == "second_undetermined":
        kwargs["second_obligation"] = "unresolved"
    elif name == "zero_bound":
        kwargs["step_bound"] = 0
    elif name == "first_resource_limit":
        kwargs["step_bound"] = 2
    elif name == "second_pre_step_limit":
        kwargs["step_bound"] = 4
    elif name == "second_row_limit":
        kwargs["step_bound"] = 6
    elif name == "second_ledger_limit":
        kwargs["ledger_bound"] = 4
    elif name != "success":
        raise ValueError("unregistered finite vector")
    return document(selected(), **kwargs)


def _exit(terminal):
    if terminal["tag"] == "resource_limit":
        return {"tag": "resource_limit"}
    if terminal["tag"] == "success":
        return {"tag": "success", "value": terminal["value"]}
    return {"tag": terminal["tag"], "diagnostic": terminal["diagnostic"]}


def _trace(terminal, steps, ledger):
    return {"exit": _exit(terminal), "steps": steps,
            "ledger": copy.deepcopy(ledger)}


def _abstract_sequence(bound, child, tail):
    """Control oracle for the Lean statement, after explicitly named erasures."""
    if bound == 0:
        return _trace({"tag": "resource_limit"}, 0, [])
    if child["exit"]["tag"] != "success":
        return {"exit": child["exit"], "steps": 1 + child["steps"],
                "ledger": copy.deepcopy(child["ledger"])}
    if 1 + child["steps"] >= bound:
        return _trace({"tag": "resource_limit"}, 1 + child["steps"],
                      child["ledger"])
    return {"exit": tail["exit"], "steps": 2 + child["steps"] + tail["steps"],
            "ledger": copy.deepcopy(child["ledger"] + tail["ledger"])}


def _render(trace, values, diagnostics, events):
    exit_ = trace["exit"]
    tag = exit_["tag"]
    if tag == "success":
        lean_exit = f".success {values[canonical_key(exit_['value'])]}"
    elif tag == "resource_limit":
        lean_exit = ".resourceLimit"
    else:
        name = {"unsupported": "unsupported", "undetermined": "undetermined",
                "domain_error": "domainError"}[tag]
        lean_exit = f".{name} {diagnostics[canonical_key(exit_['diagnostic'])]}"
    ledger = ", ".join(str(events[canonical_key(event)]) for event in trace["ledger"])
    return (f"({{ exit := {lean_exit}, steps := {trace['steps']}, ledger := [{ledger}] }}"
            " : E7CB2Sequence.Trace Nat)")


def build():
    seed = FIXTURE.read_bytes()
    records = []
    for name in CASES:
        source = _source(name)
        source_result = evaluate(source)
        package = lower(source)
        actual = compare_replay(package)["ir_result"]
        assert actual == source_result["witness"]["claim"]
        child = package["first_ir"]["source_witness"]["claim"]
        assert child == source_result["witness"]["first_witness"]["claim"]
        bound = source["first"]["resource_policy"]["step_bound"]
        child_steps = child["resource_progress"]["completed_steps"]
        total_steps = actual["resource_progress"]["completed_steps"]
        first_ledger = child["ordered_ledger"]
        assert actual["ordered_ledger"][:len(first_ledger)] == first_ledger
        if actual["terminal_outcome"]["tag"] == "success":
            value = actual["terminal_outcome"]["value"]
            assert conserves(source["first"]["rows"], value["retained"],
                             value["first_excluded"], value["second_excluded"])
        if bound == 0:
            abstract_child_steps = 0
        else:
            assert child_steps >= 1
            abstract_child_steps = child_steps - 1
        has_tail = (child["terminal_outcome"]["tag"] == "success"
                    and child_steps < bound)
        if has_tail:
            assert total_steps >= child_steps + 1
            tail = _trace(actual["terminal_outcome"], total_steps - child_steps - 1,
                          actual["ordered_ledger"][len(first_ledger):])
        else:
            tail = _trace({"tag": "resource_limit"}, 0, [])
        records.append({"case": name, "source_digest": digest(source),
                        "source_witness": source_result["witness"]["id"],
                        "ir_package": package["id"], "bound": bound,
                        "child_trace": _trace(child["terminal_outcome"],
                                              abstract_child_steps, first_ledger),
                        "tail_trace": tail,
                        "target_trace": _trace(actual["terminal_outcome"], total_steps,
                                               actual["ordered_ledger"]),
                        "source_claim": actual})
        record = records[-1]
        assert _abstract_sequence(bound, record["child_trace"], record["tail_trace"]) == \
            record["target_trace"]
    traces = [r[k] for r in records for k in
              ("child_trace", "tail_trace", "target_trace")]
    values = sorted({canonical_key(t["exit"]["value"]) for t in traces
                     if t["exit"]["tag"] == "success"})
    diagnostics = sorted({canonical_key(t["exit"]["diagnostic"]) for t in traces
                          if t["exit"]["tag"] in
                          ("unsupported", "undetermined", "domain_error")})
    events = sorted({canonical_key(e) for t in traces for e in t["ledger"]})
    value_codes = {x: n for n, x in enumerate(values)}
    diagnostic_codes = {x: n for n, x in enumerate(diagnostics)}
    event_codes = {x: n for n, x in enumerate(events)}
    lines = ["import E7CB2Sequence", "",
             "/- Finite encoded source/IR observations. No general Python/Lean refinement. -/",
             "namespace E7CEECQTwoStageBridge", ""]
    for r in records:
        child = _render(r["child_trace"], value_codes, diagnostic_codes, event_codes)
        tail = _render(r["tail_trace"], value_codes, diagnostic_codes, event_codes)
        target = _render(r["target_trace"], value_codes, diagnostic_codes, event_codes)
        lines += [f"theorem vector_{r['case']} :",
                  f"    E7CB2Sequence.sequence {r['bound']} {child}",
                  f"      (fun _ => {tail}) =", f"    {target} := by decide", ""]
    lines.append("end E7CEECQTwoStageBridge")
    manifest = {"edition": EDITION, "seed_sha256": hashlib.sha256(seed).hexdigest(),
                "source_authority": "E7G-T-v0.12.1/RGP2-experimental",
                "claim": "finite encoded control observations only",
                "erasure": ["exact JSON Joint rows to Nat value codes",
                            "ordered JSON ledger events to Nat codes",
                            "resource_limit progress and diagnostics to abstract Exit",
                            "first attempt step absorbed by Lean outer step",
                            "second attempt step absorbed by Lean continuation entry"],
                "value_codes": values, "diagnostic_codes": diagnostics,
                "event_codes": events, "cases": records}
    return manifest, "\n".join(lines) + "\n"
