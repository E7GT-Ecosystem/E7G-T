"""Kernel-check fresh source/IR observation literals; native transport is trusted."""
from __future__ import annotations

import json
import copy
import hashlib
from dataclasses import dataclass
import subprocess
import tempfile
from pathlib import Path
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from e7c_eecq_two_stage_b1 import document, evaluate
from e7_ir_eecq_two_stage_b1 import lower, execute, serialize
from e7_ir_eecq_joint_restrict_b1 import serialize as serialize_first
from e7c_eecq_two_stage_exact_codec import rows, policy, row as decode_row, LeanEvent
from e7c_eecq_joint_restrict_b1 import EFFECTS as FIRST_EFFECTS, PREDICATE_EDITION as FIRST_PREDICATE
from e7c_eecq_two_stage_b1 import SECOND_EFFECTS, SECOND_PREDICATE
from e7c_b1_canonical import canonical_key


@dataclass(frozen=True)
class PackageCapture:
    """Immutable bytes returned separately by the nested and outer serializers.

    Bytes are the length source; a caller-supplied integer is never substituted.
    Native serializer identity and provenance remain trusted host boundaries.
    """
    nested: bytes
    outer: bytes

    def __post_init__(self):
        if type(self.nested) is not bytes or type(self.outer) is not bytes:
            raise ValueError("immutable serialized bytes required")

    def receipt(self):
        return {"nested_bytes": len(self.nested), "outer_bytes": len(self.outer),
                "nested_sha256": hashlib.sha256(self.nested).hexdigest(),
                "outer_sha256": hashlib.sha256(self.outer).hexdigest()}

    def verify_receipt(self, reported):
        shape(reported, ("nested_bytes", "outer_bytes", "nested_sha256", "outer_sha256"))
        natural(reported["nested_bytes"])
        natural(reported["outer_bytes"])
        if reported != self.receipt():
            raise ValueError("package measurement or digest mismatch")


def capture_packages(package):
    return PackageCapture(serialize_first(package["first_ir"]), serialize(package))


def lean_bytes(value):
    if type(value) is not bytes:
        raise ValueError("serialized bytes required")
    chunks = ["#[" + ",".join(str(byte) for byte in value[start:start + 128]) + "]"
              for start in range(0, len(value), 128)]
    def balanced(parts):
        if not parts:
            return "#[]"
        if len(parts) == 1:
            return parts[0]
        mid = len(parts) // 2
        return "(" + balanced(parts[:mid]) + " ++ " + balanced(parts[mid:]) + ")"
    # Retain every byte in order while avoiding one deeply nested array literal.
    return "⟨" + balanced(chunks) + "⟩"


def shape(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError("unexpected raw record fields")


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON object key")
        value[key] = item
    return value


def admit_event(entry, ordinal=None):
    if type(entry) is not dict:
        raise ValueError("event object required")
    natural(entry["ordinal"])
    if ordinal is not None and entry["ordinal"] != ordinal:
        raise ValueError("nonsequential ordinal")
    kind = entry["event"]
    table = {"restriction_attempt": ("first", FIRST_EFFECTS[0], FIRST_PREDICATE),
             "second_restriction_attempt": ("second", SECOND_EFFECTS[0], SECOND_PREDICATE),
             "joint_row_checked": ("first", FIRST_EFFECTS[1], None),
             "second_joint_row_checked": ("second", SECOND_EFFECTS[1], None)}
    if kind not in table:
        raise ValueError("unknown event kind")
    stage, effect, predicate = table[kind]
    if entry["effect"] != effect:
        raise ValueError("event effect mismatch")
    if predicate is not None:
        shape(entry, ("ordinal", "event", "effect", "predicate_edition"))
        if entry["predicate_edition"] != predicate:
            raise ValueError("event predicate edition mismatch")
        return stage, None
    shape(entry, ("ordinal", "event", "effect", "row_index", "row_key", "decision"))
    natural(entry["row_index"])
    if type(entry["row_key"]) is not str:
        raise ValueError("row key string required")
    raw = json.loads(entry["row_key"], object_pairs_hook=unique_object)
    decode_row(raw)
    if canonical_key(raw) != entry["row_key"]:
        raise ValueError("noncanonical row key")
    allowed = ("retained", "excluded") if stage == "first" else ("retained", "second_excluded")
    if entry["decision"] not in allowed:
        raise ValueError("invalid stage-specific decision")
    return stage, entry["row_index"]


def admit_progress(raw):
    shape(raw, ("completed_steps", "completed_ledger_entries", "ledger_prefix",
                "first_excluded", "second_excluded_prefix"))
    natural(raw["completed_steps"])
    natural(raw["completed_ledger_entries"])
    if type(raw["ledger_prefix"]) is not list or len(raw["ledger_prefix"]) != raw["completed_ledger_entries"]:
        raise ValueError("progress ledger count mismatch")
    for ordinal, entry in enumerate(raw["ledger_prefix"]):
        admit_event(entry, ordinal)
    for key in ("first_excluded", "second_excluded_prefix"):
        values = raw[key]
        if values is None and key == "first_excluded":
            continue
        if type(values) is not list:
            raise ValueError("row array required")
        for value in values:
            decode_row(value)


def admit_terminal(raw):
    if type(raw) is not dict:
        raise ValueError("terminal object required")
    kind = raw["tag"]
    if kind == "success":
        shape(raw, ("tag", "value"))
        shape(raw["value"], ("retained", "first_excluded", "second_excluded", "predicate_editions"))
        if raw["value"]["predicate_editions"] != [FIRST_PREDICATE, SECOND_PREDICATE]:
            raise ValueError("terminal predicate editions mismatch")
        for key in ("retained", "first_excluded", "second_excluded"):
            if type(raw["value"][key]) is not list:
                raise ValueError("terminal row array required")
            for value in raw["value"][key]:
                decode_row(value)
    elif kind == "resource_limit":
        shape(raw, ("tag", "progress"))
        admit_progress(raw["progress"])
    elif kind in ("unsupported", "undetermined"):
        shape(raw, ("tag", "diagnostic"))
        allowed = (("joint_restriction_unavailable", "second_joint_restriction_unavailable")
                   if kind == "unsupported" else
                   ("joint_predicate_unresolved", "second_joint_predicate_unresolved"))
        if raw["diagnostic"] not in allowed:
            raise ValueError("terminal diagnostic mismatch")
    else:
        raise ValueError("unknown terminal kind")


def _admit_raw_capture(result, transcript):
    """Operation-local shapes/metadata only; no expected partition or run plan.

    Checks frame counters and charge/append pairing without computing expected
    row routing. Capture origin/completeness against execution is not proved.
    """
    if type(result) is not dict:
        raise ValueError("returned observation object required")
    fields = {"terminal_outcome", "ordered_ledger", "resource_progress"}
    if "witness" in result:
        fields.add("witness")  # Native witness validation stays outside this wire carrier.
    shape(result, fields)
    if type(transcript) is not list or not transcript:
        raise ValueError("nonempty transition array required")
    terminal_positions = [i for i, item in enumerate(transcript)
                          if type(item) is dict and item.get("action") == "terminal"]
    if terminal_positions != [len(transcript) - 1]:
        raise ValueError("exactly one final terminal required")
    charged_steps, ledger_entries, pending = 0, 0, None
    for item in transcript:
        if type(item) is not dict or item.get("stage") not in ("first", "second"):
            raise ValueError("known stage required")
        action = item.get("action")
        fields = {"action", "stage", "row_index", "steps", "ledger_entries", "event"}
        if action == "terminal":
            fields |= {"second_started", "terminal_outcome", "progress"}
        elif action not in ("charge", "append"):
            raise ValueError("known action required")
        elif item["stage"] == "second":
            fields.add("second_started")
        shape(item, fields)
        natural(item["steps"])
        natural(item["ledger_entries"])
        if item["row_index"] is not None:
            natural(item["row_index"])
        if "second_started" in item and type(item["second_started"]) is not bool:
            raise ValueError("Boolean stage-start field required")
        if action == "charge":
            if (pending is not None or item["steps"] != charged_steps + 1 or
                    item["ledger_entries"] != ledger_entries):
                raise ValueError("charge frame counters/pairing mismatch")
            charged_steps = item["steps"]
            pending = (item["stage"], item["row_index"])
        if action == "append":
            if (pending != (item["stage"], item["row_index"]) or
                    item["steps"] != charged_steps or item["ledger_entries"] != ledger_entries + 1):
                raise ValueError("append frame counters/pairing mismatch")
            ledger_entries = item["ledger_entries"]
            pending = None
            stage, index = admit_event(item["event"], item["ledger_entries"] - 1)
            if (stage, index) != (item["stage"], item["row_index"]):
                raise ValueError("append frame/payload mismatch")
        elif item["event"] is not None:
            raise ValueError("non-append event must be null")
        if action == "terminal":
            if item["steps"] != charged_steps or item["ledger_entries"] != ledger_entries:
                raise ValueError("terminal frame/capture counters mismatch")
            if item["row_index"] is not None:
                raise ValueError("terminal has no row index")
            admit_terminal(item["terminal_outcome"])
            admit_progress(item["progress"])
            expected_stage = "second" if item["progress"]["first_excluded"] is not None else "first"
            if item["stage"] != expected_stage:
                raise ValueError("terminal stage/progress mismatch")
            if (item["steps"] != item["progress"]["completed_steps"] or
                    item["ledger_entries"] != item["progress"]["completed_ledger_entries"]):
                raise ValueError("terminal counters/progress mismatch")
    admit_terminal(result["terminal_outcome"])
    admit_progress(result["resource_progress"])
    if type(result["ordered_ledger"]) is not list:
        raise ValueError("ordered ledger array required")
    for ordinal, entry in enumerate(result["ordered_ledger"]):
        admit_event(entry, ordinal)


def admit_raw_capture(result, transcript):
    try:
        _admit_raw_capture(result, transcript)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("raw capture admission failed") from exc


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


def event(value, wire=False):
    if value.index is None:
        return "(.attempt ." + value.stage + ")"
    return "(.row ." + value.stage + " " + str(value.index) + " (" + row(value.row, wire=wire) + ") " + boolean(value.excluded) + ")"


def progress(value, wire=False):
    first = "none" if value["firstExcluded"] is None else "some " + seq(row(r, wire=wire) for r in value["firstExcluded"])
    return "{ completedSteps := " + natural(value["completedSteps"]) + ", ledgerPrefix := " + seq(event(e, wire=wire) for e in value["progressLedger"]) + ", firstExcluded := " + first + ", secondExcludedPrefix := " + seq(row(r, wire=wire) for r in value["secondExcludedPrefix"]) + " }"


def observation(value, wire=False):
    p = progress(value, wire=wire)
    if value["terminal"] == "success":
        parts = [seq(row(r, wire=wire) for r in part) for part in value["partition"]]
        terminal = ("(.success " + " ".join(parts) + ")" if wire else
                    "(.success ⟨" + ", ".join(parts) + "⟩)")
    elif value["terminal"] == "resource_limit":
        terminal = "(.resourceLimit (" + progress(value["resourceTerminalProgress"], wire=wire) + "))"
    else:
        terminal = "(." + value["terminal"] + " ." + value["terminalStage"] + ")"
    return "{ terminal := " + terminal + ", orderedLedger := " + seq(event(e, wire=wire) for e in value["orderedLedger"]) + ", progress := " + p + ", secondStarted := " + boolean(value["secondStarted"]) + " }"


def natural(value):
    if type(value) is not int or value < 0:
        raise ValueError("natural number required")
    return str(value)


def project_event(entry):
    """Read the emitted payload itself; never substitute an expected row.

    Static effect/edition and ordinal metadata are outside this selected
    carrier. It preserves dynamic stage, index, decision and the full row.
    """
    kind = entry["event"]
    if kind in ("restriction_attempt", "second_restriction_attempt"):
        return LeanEvent("first" if kind == "restriction_attempt" else "second")
    if kind not in ("joint_row_checked", "second_joint_row_checked"):
        raise ValueError("unknown emitted event")
    stage = "first" if kind == "joint_row_checked" else "second"
    decision = entry["decision"]
    if decision not in (("retained", "excluded") if stage == "first" else
                        ("retained", "second_excluded")):
        raise ValueError("unknown row decision")
    raw = json.loads(entry["row_key"])
    value = decode_row(raw)
    natural(entry["row_index"])
    return LeanEvent(stage, entry["row_index"], value, decision != "retained")


def transport_event(entry):
    return event(project_event(entry), wire=True)


def project_progress(raw):
    natural(raw["completed_steps"])
    natural(raw["completed_ledger_entries"])
    if raw["completed_ledger_entries"] != len(raw["ledger_prefix"]):
        raise ValueError("progress entry count differs from its own ledger")
    return {"completedSteps": raw["completed_steps"],
            "progressLedger": tuple(project_event(e) for e in raw["ledger_prefix"]),
            "firstExcluded": None if raw["first_excluded"] is None else
                tuple(decode_row(r) for r in raw["first_excluded"]),
            "secondExcludedPrefix": tuple(decode_row(r) for r in raw["second_excluded_prefix"])}


def project_result(result, terminal_record):
    """Structural projection only: no expected partition, policy or plan."""
    value = project_progress(result["resource_progress"])
    terminal = result["terminal_outcome"]
    kind = terminal["tag"]
    value.update(terminal=kind, partition=None, terminalStage=None,
                 orderedLedger=tuple(project_event(e) for e in result["ordered_ledger"]))
    if kind == "success":
        value["partition"] = tuple(tuple(decode_row(r) for r in terminal["value"][key])
                                   for key in ("retained", "first_excluded", "second_excluded"))
    elif kind == "resource_limit":
        value["resourceTerminalProgress"] = project_progress(terminal["progress"])
    elif kind in ("unsupported", "undetermined"):
        diagnostics = {"joint_restriction_unavailable": ("unsupported", "first"),
                       "joint_predicate_unresolved": ("undetermined", "first"),
                       "second_joint_restriction_unavailable": ("unsupported", "second"),
                       "second_joint_predicate_unresolved": ("undetermined", "second")}
        if diagnostics.get(terminal["diagnostic"], (None, None))[0] != kind:
            raise ValueError("unknown terminal diagnostic")
        value["terminalStage"] = diagnostics[terminal["diagnostic"]][1]
    else:
        raise ValueError("unknown terminal outcome")
    started = terminal_record["second_started"]
    if type(started) is not bool:
        raise ValueError("Boolean terminal second_started required")
    value["secondStarted"] = started
    return value


def packets(source, result, transcript, *, admit_raw=True):
    if admit_raw:
        admit_raw_capture(result, transcript)
    terminals = [item for item in transcript if item["action"] == "terminal"]
    if not terminals:
        raise ValueError("terminal observation needed for projection")
    projected = project_result(result, terminals[-1])
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
            output.append("(.terminal (" + observation(projected, wire=True) + "))")
        else:
            raise ValueError("unknown transition action")
    return output, projected


def capture_text(source):
    source_trace, ir_trace = [], []
    source_result = evaluate(source, _transition_sink=source_trace.append)
    package = lower(source)
    ir_result = execute(package, _transition_sink=ir_trace.append)
    capture = capture_packages(package)
    nested, outer = len(capture.nested), len(capture.outer)
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
        stream = "checkTerminalTransport ." + path + " " + args + " (initial (" + wire + ")) " + seq(encoded)
        lines.append("example : " + stream + " = some (" +
                     observation(projected) + ") := by decide")
        for item in trace:
            if item["action"] != "append":
                continue
            entry = item["event"]
            payload = transport_event(entry)
            predicate = ("some " + json.dumps(entry["predicate_edition"]) if
                         "predicate_edition" in entry else "none")
            envelope = ("⟨" + str(entry["ordinal"]) + ", " + json.dumps(entry["effect"]) +
                        ", " + predicate + ", " + payload + "⟩")
            lines.append("example : admitEnvelope " + str(item["ledger_entries"] - 1) +
                         " " + envelope + " = some " + payload + " := by decide")
        if path == "ir":
            captured = "⟨" + lean_bytes(capture.nested) + ", " + lean_bytes(capture.outer) + "⟩"
            bounded = "checkCapturedIR (" + captured + ") ." + first + " ." + second + " (" + wire_rows + ") ⟨" + str(step) + ", " + str(ledger) + "⟩ " + seq(encoded)
            lines.append("example : " + bounded + " = some (" +
                         observation(projected) + ") := by decide")
            lines.append("-- byte capture receipt: " + json.dumps(capture.receipt(), sort_keys=True))
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
    return "\n".join("example : checkTerminalTransport .source .ready .ready 4 2 " +
                     "(initial (" + initial_rows + ")) " +
                     seq(packets(source, result, variant, admit_raw=False)[0]) + " = none := by decide"
                     for variant in variants)


def terminal_rejection_text():
    lines = []
    for variant in range(5):
        source = examples()[0] if variant in (0, 1, 4) else examples()[-1]
        trace = []
        result = evaluate(source, _transition_sink=trace.append)
        if variant == 0:
            result["terminal_outcome"]["value"]["retained"][0]["coefficient"]["numerator"] = 2
        elif variant == 1:
            result["ordered_ledger"] = result["ordered_ledger"][:-1]
        elif variant == 2:
            result["terminal_outcome"]["progress"]["completed_steps"] += 1
        elif variant == 3:
            trace[-1]["second_started"] = False
        else:
            result["terminal_outcome"] = {"tag": "undetermined", "diagnostic": "joint_predicate_unresolved"}
        trace[-1]["terminal_outcome"] = copy.deepcopy(result["terminal_outcome"])
        trace[-1]["progress"] = copy.deepcopy(result["resource_progress"])
        encoded, _ = packets(source, result, trace, admit_raw=False)
        budget = source["first"]["resource_policy"]
        lines.append("example : checkTerminalTransport .source .ready .ready " +
                     str(budget["step_bound"]) + " " + str(budget["ledger_bound"]) +
                     " (initial (" + seq(row(r) for r in rows(source)) + ")) " +
                     seq(encoded) + " = none := by decide")
    return "\n".join(lines)


def metadata_rejection_text():
    lines = []
    for ordinal, effect, predicate in (
            (0, "forged", FIRST_PREDICATE),
            (0, FIRST_EFFECTS[0], "forged"),
            (1, FIRST_EFFECTS[0], FIRST_PREDICATE)):
        envelope = "⟨" + str(ordinal) + ", " + json.dumps(effect) + ", some " + json.dumps(predicate) + ", .attempt .first⟩"
        lines.append("example : admitEnvelope 0 " + envelope + " = none := by decide")
    return "\n".join(lines)


def main():
    header = """import E7CEECQIRObservationChecker
open E7CEECQTwoStageAllInput E7CEECQTwoStageOperational
open E7CEECQTwoStageExactCodec E7CEECQTwoStageImplementationPath
open E7CEECQIRObservationChecker
-- Driver-only limits for checking seven finite captured byte-array literals.
-- These are not EEC-Q operational budgets or native-host resource premises.
set_option maxRecDepth 32768
set_option maxHeartbeats 4000000
"""
    sources = examples()
    text = (header + "\n".join(capture_text(source) for source in sources) + "\n" +
            rejection_text() + "\n" + terminal_rejection_text() + "\n" + metadata_rejection_text() + "\n")
    package = Path(__file__).parent / "proof-packages" / "lean-core"
    with tempfile.TemporaryDirectory(prefix="e7c-ir-observations-") as directory:
        target = Path(directory) / "ObservedIR.lean"
        target.write_text(text)
        subprocess.run(["lake", "env", "lean", str(target)], cwd=package, check=True)
    print(json.dumps({"fresh_documents_checked": len(sources),
                      "source_ir_kernel_checks": 3 * len(sources),
                      "forged_transport_kernel_rejections": 5,
                      "forged_terminal_kernel_rejections": 5,
                      "event_metadata_kernel_checks": text.count("example : admitEnvelope") - 3,
                      "forged_metadata_kernel_rejections": 3,
                      "package_length_source": "separately captured serializer ByteArrays",
                      "native_trace_and_decoder_adequacy": "trusted/open"}))


if __name__ == "__main__":
    main()
