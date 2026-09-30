"""Observe unchanged CPython helpers and export concrete mathematical certificates.

Frame events are not opcode/attribute observations or a general host-adequacy
proof. Runtime pins, capture fidelity and native denotation remain trusted.
"""
import ast
import hashlib
import json
import marshal
import math
import platform
import sys
import threading
import types
from fractions import Fraction
from pathlib import Path

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_serializer_source import ROOT, check

EDITION = "E7C-serializer-observation/0.1-provisional"
HELPERS = ("_graph", "_row", "rows")
NATIVE_LIST, NATIVE_TYPE = list, type
PIN_FILES = ("e7c_eecq_joint_restrict_b1.py", "adapters/eec_q_fg3_b1.py",
             "adapters/eec_q_fg3_joint_b1.py")


class ObservationLimit(Exception):
    pass


def code_digest(code):
    """Pin executable code while removing installation-specific filenames."""
    constants = tuple(normalize_code(c) if type(c) is types.CodeType else c
                      for c in code.co_consts)
    return hashlib.sha256(marshal.dumps(code.replace(co_filename="<pinned>",
                                                     co_consts=constants))).hexdigest()


def normalize_code(code):
    return code.replace(co_filename="<pinned>", co_consts=tuple(
        normalize_code(c) if type(c) is types.CodeType else c for c in code.co_consts))


def freeze_manifest():
    """Freeze the exact current runtime and source/code image; no semantic proof."""
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12):
        raise ValueError("only the selected CPython 3.12 host family is supported")
    check()
    source_text = (ROOT / PIN_FILES[0]).read_text()
    source_metadata = {}
    for node in ast.parse(source_text).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in {"EDITION", "SOURCE_BLOB", "MODEL_BLOB"}):
            name = node.targets[0].id
            source_metadata[name] = ast.literal_eval(node.value)
            if getattr(source, name) != source_metadata[name]:
                raise ValueError("live source edition/blob binding changed: " + name)
    code = compile(source_text, str(ROOT / PIN_FILES[0]),
                   "exec", dont_inherit=True, optimize=sys.flags.optimize)
    expected = {c.co_name: c for c in code.co_consts if type(c) is types.CodeType}
    fingerprints = {}
    for name in HELPERS:
        helper = getattr(source, name)
        if (type(helper) is not types.FunctionType or helper.__globals__ is not vars(source)
                or helper.__defaults__ or helper.__kwdefaults__ or helper.__closure__
                or code_digest(helper.__code__) != code_digest(expected[name])):
            raise ValueError("live helper code differs from the compiled source: " + name)
        fingerprints[name] = code_digest(helper.__code__)
    for helper_name in HELPERS:
        helper = getattr(source, helper_name)
        for name, expected_binding in (("Joint", Joint), ("_row", source._row),
                                       ("_graph", source._graph), ("list", NATIVE_LIST),
                                       ("type", NATIVE_TYPE)):
            binding = vars(source).get(name, helper.__builtins__.get(name))
            if binding is not expected_binding:
                raise ValueError("unsupported live helper binding: " + name)
    return {"edition": EDITION, "implementation": sys.implementation.name,
            "version": list(sys.version_info), "version_string": sys.version,
            "cache_tag": sys.implementation.cache_tag, "platform": platform.platform(),
            "optimize": sys.flags.optimize,
            "source_operation_pins": source_metadata,
            "executable_sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
            "fraction_module_sha256": hashlib.sha256(Path(sys.modules["fractions"].__file__).read_bytes()).hexdigest(),
            "files": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                      for name in PIN_FILES}, "helpers": fingerprints}


def graph_snapshot(graph):
    if type(graph) is not Config or type(graph.edges) is not tuple:
        raise ValueError("exact native Config and edge tuple required")
    if (any(type(edge) is not str or edge not in {"AB", "AC", "BC"} for edge in graph.edges)
            or graph.edges != tuple(sorted(set(graph.edges)))
            or (graph.tag is not None and type(graph.tag) is not str)):
        raise ValueError("canonical native graph fields required")
    return {"edges": list(graph.edges), "tag": graph.tag}


def row_snapshot(atoms, coefficient):
    if type(atoms) is not tuple or len(atoms) != 2 or type(coefficient) is not Fraction:
        raise ValueError("binary native atoms and exact Fraction required")
    n, d = coefficient.numerator, coefficient.denominator
    if (type(n) is not int or type(d) is not int or d <= 0 or n == 0
            or math.gcd(n, d) != 1):
        raise ValueError("nonzero reduced signed fraction required")
    if max(n.bit_length(), d.bit_length()) > 256:
        raise ObservationLimit("selected coefficient snapshot bit limit")
    return {"atoms": [graph_snapshot(g) for g in atoms],
            "coefficient": {"numerator": n, "denominator": d}}


def joint_snapshot(value, row_limit):
    if type(value) is not Joint or type(value.arity) is not int or value.arity != 2:
        raise ValueError("exact native binary Joint required")
    if type(value.terms) is not tuple:
        raise ValueError("native terms tuple required")
    if len(value.terms) > row_limit:
        raise ObservationLimit("selected row snapshot limit")
    rows, keys = [], []
    for term in value.terms:
        if type(term) is not tuple or len(term) != 2:
            raise ValueError("native term pair required")
        atoms, coefficient = term
        row = row_snapshot(atoms, coefficient)
        rows.append(row)
        keys.append(tuple((tuple(g["edges"]), g["tag"] is not None, g["tag"] or "")
                          for g in row["atoms"]))
    if keys != sorted(set(keys)):
        raise ValueError("unique ordered support required in selected observation domain")
    return rows


def raw_snapshot(value, depth=8):
    """Copy already-decoded native JSON values without invoking a serializer."""
    if value is None or type(value) in (str, bool):
        return value
    if type(value) is int:
        if value.bit_length() > 256:
            raise ObservationLimit("selected raw integer bit limit")
        return value
    if depth <= 0:
        raise ObservationLimit("selected snapshot nesting limit")
    if type(value) is list:
        return [raw_snapshot(child, depth - 1) for child in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: raw_snapshot(child, depth - 1) for key, child in value.items()}
    raise ValueError("reported result is outside the selected native JSON domain")


def observe(value, expected_manifest, *, row_limit=64, event_limit=386, byte_limit=262144):
    """Observe the original rows call. A normal packet is not yet kernel-checked.

    Bounds cover accounted snapshots/events/packet bytes, not peak memory, CPU,
    wall time, CPython allocation or EEC-Q charged-step/ledger semantics.
    """
    events, installed = [], False
    phase = "preflight"

    def outcome(tag, reason):
        return {"edition": EDITION, "tag": tag, "reason": reason,
                "phase": phase, "events": events}

    if (type(expected_manifest) is not dict or
            any(type(bound) is not int or bound < 0 for bound in
                (row_limit, event_limit, byte_limit)) or row_limit > 64):
        return outcome("invalid_input", "invalid observation manifest or bounds")
    if sys.getprofile() is not None or sys.gettrace() is not None or threading.active_count() != 1:
        return outcome("unsupported", "requires an uninstrumented single-thread observation session")
    try:
        manifest = freeze_manifest()
    except MemoryError:
        return outcome("resource_limit", "manifest MemoryError")
    except (ValueError, KeyError, TypeError) as error:
        return outcome("unsupported", str(error))
    if manifest != expected_manifest:
        return outcome("unsupported", "exact runtime/source manifest mismatch")
    try:
        before = joint_snapshot(value, row_limit)
        if 6 * len(before) + 2 > event_limit:
            raise ObservationLimit("complete frame ledger exceeds the selected event limit")
        if len(json.dumps(before, ensure_ascii=False).encode()) > byte_limit:
            raise ObservationLimit("input snapshot exceeds selected byte limit")
    except (ObservationLimit, MemoryError) as error:
        return outcome("resource_limit", type(error).__name__ + ": " + str(error))
    except (ValueError, TypeError, AttributeError, UnicodeError) as error:
        return outcome("invalid_input", str(error))
    helpers = {getattr(source, name).__code__: name for name in HELPERS}
    bindings = tuple(getattr(source, name) for name in HELPERS)

    def profile(frame, event, returned):
        if frame.f_code not in helpers or event not in ("call", "return"):
            return
        if len(events) >= event_limit:
            raise ObservationLimit("frame ledger append limit")
        name = helpers[frame.f_code]
        if frame.f_globals is not vars(source):
            raise ValueError("helper frame has unsupported global bindings")
        if event == "return":
            payload = raw_snapshot(returned)
        elif name == "rows":
            payload = joint_snapshot(frame.f_locals["value"], row_limit)
        elif name == "_row":
            payload = row_snapshot(frame.f_locals["atoms"], frame.f_locals["coefficient"])
        else:
            payload = graph_snapshot(frame.f_locals["g"])
        events.append({"site": name + "." + event, "payload": payload})

    try:
        phase = "observer_install"
        sys.setprofile(profile)
        installed = True
        phase = "running_helpers"
        returned = source.rows(value)  # unchanged pinned source, not the selected AST interpreter
        phase = "postflight"
        output = raw_snapshot(returned)
    except (ObservationLimit, MemoryError) as error:
        return outcome("resource_limit", type(error).__name__ + ": " + str(error))
    except (KeyboardInterrupt, SystemExit) as error:
        return outcome("abnormal", type(error).__name__)
    except Exception as error:
        return outcome("undetermined" if phase == "postflight" else "abnormal",
                       type(error).__name__ + ": " + str(error))
    finally:
        if installed:
            try:
                sys.setprofile(None)
            except (Exception, KeyboardInterrupt, SystemExit) as error:
                return outcome("undetermined", "profiler restoration failed: " + type(error).__name__)
    try:
        if (freeze_manifest() != manifest or joint_snapshot(value, row_limit) != before
                or any(getattr(source, name) is not original for name, original in zip(HELPERS, bindings))
                or threading.active_count() != 1 or sys.gettrace() is not None):
            return outcome("undetermined", "postflight binding or input stability check failed")
        sites = ["rows.call"] + ["_row.call", "_graph.call", "_graph.return",
                                  "_graph.call", "_graph.return", "_row.return"] * len(before) + ["rows.return"]
        if [event["site"] for event in events] != sites:
            return outcome("undetermined", "complete expected helper-frame order was not observed")
        packet = {"edition": EDITION, "tag": "observed_normal", "manifest": manifest,
                  "input": before, "output": output, "events": events,
                  "limits": {"rows": row_limit, "events": event_limit, "bytes": byte_limit},
                  "trust_boundary": "observer/native denotation unproved; frame events are not primitive traces"}
        if len(json.dumps(packet, ensure_ascii=False).encode()) > byte_limit:
            return outcome("resource_limit", "reported packet exceeds selected byte limit")
        return packet
    except (ObservationLimit, MemoryError) as error:
        return outcome("resource_limit", type(error).__name__ + ": " + str(error))
    except Exception as error:
        return outcome("undetermined", type(error).__name__ + ": " + str(error))


def lean_string(value):
    if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise ValueError("certificate strings require Unicode scalar values")
    escaped = []
    for char in value:
        escaped.append({"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}.get(
            char, "\\u" + format(ord(char), "04x") if ord(char) < 32 or ord(char) == 127 else char))
    return '"' + "".join(escaped) + '"'


def raw_term(value):
    if value is None:
        return ".null"
    if type(value) is bool:
        return ".boolean " + str(value).lower()
    if type(value) is int:
        return ".integer (" + str(value) + ")"
    if type(value) is str:
        return ".string " + lean_string(value)
    if type(value) is list:
        return ".array [" + ", ".join("(" + raw_term(v) + ")" for v in value) + "]"
    if type(value) is dict and all(type(k) is str for k in value):
        return ".object [" + ", ".join("(" + lean_string(k) + ", (" + raw_term(v) + "))"
                                        for k, v in value.items()) + "]"
    raise ValueError("unsupported certificate raw value")


def graph_term(graph):
    return "⟨[" + ", ".join(lean_string(e) for e in graph["edges"]) + "], " + (
        "none" if graph["tag"] is None else "some " + lean_string(graph["tag"])) + "⟩"


def validate_packet_literals(packet):
    """Reject code injection and bound exporter input; do not pre-prove results."""
    if type(packet) is not dict or packet.get("edition") != EDITION or packet.get("tag") != "observed_normal":
        raise ValueError("only reported normal observations can be exported")
    rows = packet.get("input")
    if type(rows) is not list or len(rows) > 64:
        raise ValueError("selected input row list required")
    for row in rows:
        if type(row) is not dict or set(row) != {"atoms", "coefficient"}:
            raise ValueError("selected row fields required")
        if type(row["atoms"]) is not list or len(row["atoms"]) != 2:
            raise ValueError("two graph coordinates required")
        for graph in row["atoms"]:
            if type(graph) is not dict or set(graph) != {"edges", "tag"}:
                raise ValueError("selected graph fields required")
            edges, tag = graph["edges"], graph["tag"]
            if (type(edges) is not list or any(type(e) is not str or e not in {"AB", "AC", "BC"} for e in edges)
                    or edges != sorted(set(edges)) or (tag is not None and type(tag) is not str)):
                raise ValueError("canonical graph fields required")
        coefficient = row["coefficient"]
        if type(coefficient) is not dict or set(coefficient) != {"numerator", "denominator"}:
            raise ValueError("selected fraction fields required")
        n, d = coefficient["numerator"], coefficient["denominator"]
        if (type(n) is not int or type(d) is not int or d <= 0 or n == 0 or math.gcd(n, d) != 1
                or max(n.bit_length(), d.bit_length()) > 256):
            raise ValueError("reduced exact integer fraction literals required")
    events = packet.get("events")
    if type(events) is not list or len(events) > 386:
        raise ValueError("selected frame event list required")
    for event in events:
        if (type(event) is not dict or set(event) != {"site", "payload"}
                or type(event["site"]) is not str):
            raise ValueError("selected frame event fields required")
        raw_snapshot(event["payload"])
    raw_snapshot(packet["output"])
    if len(json.dumps(packet, ensure_ascii=False).encode()) > 262144:
        raise ValueError("certificate input exceeds selected packet byte limit")


def certificate_text(packets):
    """Export supplied observations verbatim. Lean must check both equalities.

    A forged packet may generate an ill-proved file; export is not validation.
    Matching data do not prove the claimed runtime origin or observer fidelity.
    """
    lines = ["import E7CJointSerializerObservedCertificate", "",
             "namespace E7CJointSerializerObservedFixtures",
             "open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission",
             "open E7CJointSerializerObservedCertificate", ""]
    for index, packet in enumerate(packets):
        validate_packet_literals(packet)
        rows = []
        for row in packet["input"]:
            left, right = row["atoms"]
            coefficient = row["coefficient"]
            rows.append("⟨" + graph_term(left) + ", " + graph_term(right) + ", (" +
                        "(" + str(coefficient["numerator"]) + " : Rat) / (" +
                        str(coefficient["denominator"]) + " : Rat))⟩")
        lines.extend([f"def rows{index} : List WireRow := [" + ", ".join(rows) + "]",
                      f"def output{index} : RawJson := " + raw_term(packet["output"]),
                      f"def ledger{index} : FrameLedger := [" + ", ".join(
                          "(" + lean_string(event["site"]) + ", (" + raw_term(event["payload"]) + "))"
                          for event in packet["events"]) + "]",
                      f"theorem checked{index} : CaptureValid rows{index} output{index} ledger{index} := by",
                      "  constructor <;> rfl", ""])
    return "\n".join(lines + ["end E7CJointSerializerObservedFixtures", ""])
