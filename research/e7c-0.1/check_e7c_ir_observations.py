"""Kernel-check fresh source/IR observation literals; native transport is trusted."""
from __future__ import annotations

import json
import copy
import subprocess
import tempfile
from pathlib import Path
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_eecq_two_stage_b1 import document, evaluate
from e7_ir_eecq_two_stage_b1 import lower, execute, serialize
from e7_ir_eecq_joint_restrict_b1 import serialize as serialize_first
from e7c_eecq_two_stage_exact_codec import rows, policy, row as decode_row, observation as project_observation


def package_gate(nested_bytes, outer_bytes):
    if any(type(n) is not int or n < 0 for n in (nested_bytes, outer_bytes)):
        raise ValueError("nonnegative measured lengths required")
    if nested_bytes > 1_000_000:
        return "nested_limit"
    if outer_bytes > 1_000_000:
        return "outer_limit"
    return "admitted"


def seq(values):
    return "[" + ", ".join(values) + "]"


def boolean(value):
    return "true" if value else "false"


def graph(value):
    tag = "none" if value.tag is None else "some " + json.dumps(value.tag, ensure_ascii=True)
    return "⟨" + ", ".join([boolean(value.ab), boolean(value.ac),
                           boolean(value.bc), tag]) + "⟩"


def row(value, wire=False):
    n, d = value.coefficient.numerator, value.coefficient.denominator
    rat = "{ num := " + str(n) + ", den := " + str(d) + ", den_nz := by decide, reduced := by decide }"
    def selected_graph(g):
        if not wire:
            return graph(g)
        tag = "none" if g.tag is None else "some " + json.dumps(g.tag, ensure_ascii=True)
        return "⟨" + seq(json.dumps(edge) for edge in g.edges()) + ", " + tag + "⟩"
    return "⟨" + selected_graph(value.left) + ", " + selected_graph(value.right) + ", " + rat + "⟩"


def event(value):
    if value.index is None:
        return "(.attempt ." + value.stage + ")"
    return "(.row ." + value.stage + " " + str(value.index) + " (" + row(value.row) + ") " + boolean(value.excluded) + ")"


def progress(value):
    first = "none" if value["firstExcluded"] is None else "some " + seq(row(r) for r in value["firstExcluded"])
    return "{ completedSteps := " + str(value["completedSteps"]) + ", ledgerPrefix := " + seq(event(e) for e in value["orderedLedger"]) + ", firstExcluded := " + first + ", secondExcludedPrefix := " + seq(row(r) for r in value["secondExcludedPrefix"]) + " }"


def observation(value):
    p = progress(value)
    if value["terminal"] == "success":
        terminal = "(.success ⟨" + ", ".join(seq(row(r) for r in part)
                                             for part in value["partition"]) + "⟩)"
    elif value["terminal"] == "resource_limit":
        terminal = "(.resourceLimit (" + p + "))"
    else:
        terminal = "(." + value["terminal"] + " ." + value["terminalStage"] + ")"
    return "{ terminal := " + terminal + ", orderedLedger := " + seq(event(e) for e in value["orderedLedger"]) + ", progress := " + p + ", secondStarted := " + boolean(value["secondStarted"]) + " }"


def natural(value):
    if type(value) is not int or value < 0:
        raise ValueError("natural number required")
    return str(value)


def transport_event(entry):
    """Read the emitted payload itself; never substitute an expected row.

    Static effect/edition validation remains in observation projection. This
    transport preserves the dynamic stage, index, decision and full row.
    """
    kind = entry["event"]
    if kind in ("restriction_attempt", "second_restriction_attempt"):
        return "(.attempt ." + ("first" if kind == "restriction_attempt" else "second") + ")"
    if kind not in ("joint_row_checked", "second_joint_row_checked"):
        raise ValueError("unknown emitted event")
    stage = "first" if kind == "joint_row_checked" else "second"
    decision = entry["decision"]
    if decision not in (("retained", "excluded") if stage == "first" else
                        ("retained", "second_excluded")):
        raise ValueError("unknown row decision")
    raw = json.loads(entry["row_key"])
    value = decode_row(raw)
    return ("(.row ." + stage + " " + natural(entry["row_index"]) + " (" +
            row(value, wire=True) + ") " + boolean(decision != "retained") + ")")


def packets(source, result, transcript):
    projected = project_observation(source, result)
    output = []
    for item in transcript:
        if item["action"] == "charge":
            started = item.get("second_started", False)
            if type(started) is not bool:
                raise ValueError("Boolean second_started required")
            output.append("(.charge " + natural(item["steps"]) + " " +
                          boolean(started) + ")")
        elif item["action"] == "append":
            output.append("(.append " + transport_event(item["event"]) +
                          " " + natural(item["ledger_entries"]) + ")")
        elif item["action"] == "terminal":
            if (item["terminal_outcome"] != result["terminal_outcome"] or
                    item["progress"] != result["resource_progress"]):
                raise ValueError("terminal record differs from returned observation")
            output.append("(.terminal (" + observation(projected) + "))")
        else:
            raise ValueError("unknown transition action")
    return output, projected


def capture_text(source):
    source_trace, ir_trace = [], []
    source_result = evaluate(source, _transition_sink=source_trace.append)
    package = lower(source)
    ir_result = execute(package, _transition_sink=ir_trace.append)
    nested, outer = len(serialize_first(package["first_ir"])), len(serialize(package))
    if package_gate(nested, outer) != "admitted":
        raise ValueError("independent package bounds not met")
    wire = seq(row(r) for r in rows(source))
    wire_rows = seq(row(r, wire=True) for r in rows(source))
    first, second = policy(source)
    step, ledger = (source["first"]["resource_policy"][key]
                    for key in ("step_bound", "ledger_bound"))
    lines = []
    for path, result, trace in (("source", source_result, source_trace),
                               ("ir", ir_result, ir_trace)):
        encoded, projected = packets(source, result, trace)
        args = "." + first + " ." + second + " " + str(step) + " " + str(ledger)
        stream = "checkTransport ." + path + " " + args + " (initial (" + wire + ")) " + seq(encoded)
        lines.append("example : " + stream + " = some (" +
                     observation(projected) + ") := by decide")
        if path == "ir":
            bounded = "checkTransportIR " + str(nested) + " " + str(outer) + " ." + first + " ." + second + " (" + wire_rows + ") ⟨" + str(step) + ", " + str(ledger) + "⟩ " + seq(encoded)
            lines.append("example : " + bounded + " = some (" +
                         observation(projected) + ") := by decide")
    return "\n".join(lines)


def examples():
    value = joint([(Fraction(-2, 3), (Config(("AC",), None), Config(("BC",), ""))),
                   (Fraction(1, 7), (Config(("BC",), ""), Config(("AB",), None)))], arity=2)
    return [document(value), document(value, step_bound=4, ledger_bound=3),
            document(value, step_bound=0, ledger_bound=0),
            document(value, second_capability=False),
            document(value, first_obligation="unresolved"),
            document(joint([], arity=2)),
            document(joint([(coefficient, atoms) for atoms, coefficient in value.terms[:1]], arity=2), step_bound=4, ledger_bound=2)]


def rejection_text():
    """Fresh forged records are transported without a semantic Python precheck."""
    source = examples()[-1]
    trace = []
    result = evaluate(source, _transition_sink=trace.append)
    variants = []
    forged = copy.deepcopy(trace)
    forged[0]["steps"] += 1
    variants.append(forged)
    variants.append(copy.deepcopy(trace[1:]))
    variants.append(copy.deepcopy(trace + [trace[-1]]))
    forged = copy.deepcopy(trace)
    forged[-2]["second_started"] = False
    variants.append(forged)
    forged = copy.deepcopy(trace)
    raw = json.loads(forged[3]["event"]["row_key"])
    raw["coefficient"]["numerator"] *= 2
    forged[3]["event"]["row_key"] = json.dumps(raw)
    variants.append(forged)
    initial_rows = seq(row(r) for r in rows(source))
    return "\n".join("example : checkTransport .source .ready .ready 4 2 " +
                     "(initial (" + initial_rows + ")) " +
                     seq(packets(source, result, variant)[0]) + " = none := by decide"
                     for variant in variants)


def main():
    header = """import E7CEECQIRObservationChecker
open E7CEECQTwoStageAllInput E7CEECQTwoStageOperational
open E7CEECQTwoStageExactCodec E7CEECQTwoStageImplementationPath
open E7CEECQIRObservationChecker
"""
    sources = examples()
    text = header + "\n".join(capture_text(source) for source in sources) + "\n" + rejection_text() + "\n"
    package = Path(__file__).parent / "proof-packages" / "lean-core"
    with tempfile.TemporaryDirectory(prefix="e7c-ir-observations-") as directory:
        target = Path(directory) / "ObservedIR.lean"
        target.write_text(text)
        subprocess.run(["lake", "env", "lean", str(target)], cwd=package, check=True)
    print(json.dumps({"fresh_documents_checked": len(sources),
                      "source_ir_kernel_checks": 3 * len(sources),
                      "forged_transport_kernel_rejections": 5,
                      "native_trace_and_decoder_adequacy": "trusted/open"}))


if __name__ == "__main__":
    main()
