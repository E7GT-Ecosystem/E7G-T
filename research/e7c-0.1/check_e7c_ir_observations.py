"""Kernel-check fresh source/IR observation literals; native transport is trusted."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_eecq_two_stage_b1 import document, evaluate
from e7_ir_eecq_two_stage_b1 import lower, execute, serialize
from e7_ir_eecq_joint_restrict_b1 import serialize as serialize_first
from e7c_eecq_two_stage_exact_codec import rows, policy, events
from e7c_eecq_two_stage_transition_certificate import check


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


def packets(source, result, transcript):
    projected = check(source, result, transcript)
    ledger = events(result, rows(source))
    output = []
    for item in transcript:
        if item["action"] == "charge":
            output.append("(.charge " + str(item["steps"]) + " " +
                          boolean(item.get("second_started", False)) + ")")
        elif item["action"] == "append":
            output.append("(.append " + event(ledger[item["ledger_entries"] - 1]) +
                          " " + str(item["ledger_entries"]) + ")")
        else:
            output.append("(.terminal (" + observation(projected) + "))")
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
        stream = "checkStream ." + path + " " + args +     " (initial (" + wire + ")) " + seq(encoded)
        lines.append("example : " + stream + " = some (" +
                     observation(projected) + ") := by decide")
        if path == "ir":
            bounded = "checkIR " + str(nested) + " " + str(outer) + " ." + first +         " ." + second + " (" + wire_rows + ") ⟨" + str(step) + ", " +         str(ledger) + "⟩ " + seq(encoded)
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


def main():
    header = """import E7CEECQIRObservationChecker
open E7CEECQTwoStageAllInput E7CEECQTwoStageOperational
open E7CEECQTwoStageExactCodec E7CEECQTwoStageImplementationPath
open E7CEECQIRObservationChecker
"""
    sources = examples()
    text = header + "\n".join(capture_text(source) for source in sources) + "\n"
    package = Path(__file__).parent / "proof-packages" / "lean-core"
    with tempfile.TemporaryDirectory(prefix="e7c-ir-observations-") as directory:
        target = Path(directory) / "ObservedIR.lean"
        target.write_text(text)
        subprocess.run(["lake", "env", "lean", str(target)], cwd=package, check=True)
    print(json.dumps({"fresh_documents_checked": len(sources),
                      "source_ir_kernel_checks": 3 * len(sources),
                      "native_trace_and_decoder_adequacy": "trusted/open"}))


if __name__ == "__main__":
    main()
