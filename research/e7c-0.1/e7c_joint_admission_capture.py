"""Observe the actual raw-row constructor calls inside pinned admit/joint.

The original function and constructor code executes once per forwarded call.
This isolated adapter supplies literal evidence, not CPython adequacy. A full
row-prefix packet can exist even when the later native equality guard rejects.
"""
from contextlib import ExitStack
import json
import sys
from threading import Lock
import threading
import types
from unittest.mock import patch

from fractions import Fraction
from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint
import eec_q_fg3_joint_b1 as model
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_serializer_native_values import (
    ROOT, ObservationLimit, code_digest, freeze_manifest, graph_snapshot,
    joint_snapshot, raw_snapshot, row_snapshot,
)

EDITION = "E7C-native-admission-prefix/0.1-provisional"
_lock = Lock()


def _manifest():
    result = freeze_manifest()
    selected = [
        (source.admit, "e7c_eecq_joint_restrict_b1.py", ("admit",)),
        (model.joint, "adapters/eec_q_fg3_joint_b1.py", ("joint",)),
        (Joint.__post_init__, "adapters/eec_q_fg3_joint_b1.py", ("Joint", "__post_init__")),
        (Config.__post_init__, "adapters/eec_q_fg3_b1.py", ("Config", "__post_init__")),
        (Config.identity, "adapters/eec_q_fg3_b1.py", ("Config", "identity")),
    ]
    fingerprints = {}
    for function, path, names in selected:
        code = compile((ROOT / path).read_text(), str(ROOT / path), "exec",
                       dont_inherit=True, optimize=sys.flags.optimize)
        for name in names:
            code, = [c for c in code.co_consts
                     if type(c) is types.CodeType and c.co_name == name]
        if type(function) is not types.FunctionType or code_digest(function.__code__) != code_digest(code):
            raise ValueError("live admission/constructor code differs: " + ".".join(names))
        fingerprints[".".join(names)] = code_digest(function.__code__)
    for module, name, expected in [
        (source, "Config", Config), (source, "Fraction", Fraction),
        (source, "joint", model.joint), (source, "Joint", Joint),
        (model, "Config", Config), (model, "Fraction", Fraction), (model, "Joint", Joint),
    ]:
        if getattr(module, name) is not expected:
            raise ValueError("live constructor binding changed: " + name)
    if any(cls.__getattribute__ is not object.__getattribute__ for cls in (Config, Fraction, Joint)):
        raise ValueError("ordinary attribute dispatch required")
    result = dict(result)
    result["admission_code"] = fingerprints
    # Dataclass-generated initializers and installed Fraction are host evidence,
    # not a proved translation of their implementations.
    result["native_initializers"] = {name: code_digest(fn.__code__) for name, fn in
                                     [("Config", Config.__init__), ("Joint", Joint.__init__),
                                      ("Fraction", Fraction.__new__)]}
    return result


def capture(document, *, row_limit=64, call_limit=200, byte_limit=262144):
    if not _lock.acquire(blocking=False):
        raise ValueError("overlapping admission capture is unsupported")
    try:
        return _capture(document, row_limit, call_limit, byte_limit)
    finally:
        _lock.release()


def _capture(document, row_limit, call_limit, byte_limit):
    if (any(type(n) is not int or n < 0 for n in (row_limit, call_limit, byte_limit))
            or row_limit > 64 or call_limit > 200 or byte_limit > 262144):
        raise ValueError("invalid admission evidence limits")
    if sys.getprofile() is not None or sys.gettrace() is not None or threading.active_count() != 1:
        raise ValueError("isolated uninstrumented host required")
    manifest = _manifest()
    before = raw_snapshot(document)
    if (type(document) is not dict or type(document.get("rows")) is not list
            or len(document["rows"]) > row_limit):
        raise ValueError("bounded native raw-row document required")
    if len(json.dumps(before, ensure_ascii=False).encode()) > byte_limit:
        raise ObservationLimit("input evidence byte limit")
    raw_rows = document["rows"]
    bindings = (source.admit, source.joint, Config.__init__, Joint.__init__)
    original_config, original_fraction, original_joint = Config, Fraction, model.joint
    original_init = Joint.__init__
    row_calls, parsed_rows, constructor = [], None, None
    retained, tokens = [], {}
    root_frame, calls = None, 0
    joint_value = None
    constructed_object = None

    def tick():
        nonlocal calls
        if calls >= call_limit:
            raise ObservationLimit("constructor call evidence limit")
        calls += 1

    def token(obj):
        identity = id(obj)
        if identity not in tokens:
            tokens[identity] = (obj, len(tokens) + 1)
        elif tokens[identity][0] is not obj:
            raise ValueError("reused native object identity")
        return tokens[identity][1]

    def bind(frame):
        nonlocal root_frame
        if frame.f_code is not source.admit.__code__ or frame.f_globals is not vars(source):
            raise ValueError("constructor call is outside pinned admit")
        if frame.f_locals["source"] is not document:
            raise ValueError("rebound admission source")
        if root_frame is None:
            root_frame = frame
        if frame is not root_frame:
            raise ValueError("repeated admission frame")

    def config_call(edges, tag):
        tick()
        frame = sys._getframe(1)
        bind(frame)
        index = len(row_calls)
        if index >= len(raw_rows) or frame.f_locals["row"] is not raw_rows[index]:
            raise ValueError("Config call does not bind the next raw row")
        raw_row, raw_graph = raw_rows[index], frame.f_locals["g"]
        graph_index = len(frame.f_locals["graphs"])
        if (graph_index not in (0, 1) or raw_graph is not raw_row["atoms"][graph_index]
                or type(edges) is not tuple or len(edges) != len(raw_graph["edges"])
                or any(a is not b for a, b in zip(edges, raw_graph["edges"]))
                or tag is not raw_graph["tag"]):
            raise ValueError("Config operands rebound from their raw fields")
        if graph_index == 0:
            retained.append({"raw": raw_row, "graphs": []})
        pending = retained[-1]
        if pending["raw"] is not raw_row or len(pending["graphs"]) != graph_index:
            raise ValueError("Config call order changed")
        graph = original_config(edges, tag)
        observation = {"input": raw_snapshot(raw_graph), "edges_operand": [x for x in edges],
                       "tag_operand": tag, "output": graph_snapshot(graph)}
        pending["graphs"].append((graph, observation))
        return graph

    def fraction_call(numerator, denominator):
        tick()
        frame = sys._getframe(1)
        bind(frame)
        index = len(row_calls)
        if index >= len(raw_rows) or frame.f_locals["row"] is not raw_rows[index]:
            raise ValueError("Fraction call does not bind the next raw row")
        raw_row, raw_coefficient = raw_rows[index], frame.f_locals["c"]
        if (raw_coefficient is not raw_row["coefficient"]
                or numerator is not raw_coefficient["numerator"]
                or denominator is not raw_coefficient["denominator"]
                or type(numerator) is not int or type(denominator) is not int
                or max(numerator.bit_length(), denominator.bit_length()) > 256):
            raise ValueError("Fraction operands are unsupported or rebound")
        pending = retained[-1]
        graphs = frame.f_locals["graphs"]
        if (pending["raw"] is not raw_row or len(pending["graphs"]) != 2
                or len(graphs) != 2
                or any(g is not seen[0] for g, seen in zip(graphs, pending["graphs"]))):
            raise ValueError("Fraction call is outside completed graph calls")
        value = original_fraction(numerator, denominator)
        output = {"numerator": value.numerator, "denominator": value.denominator}
        pending["coefficient"] = value
        row_calls.append({"input": raw_snapshot(raw_row),
                          "configs": [seen[1] for seen in pending["graphs"]],
                          "fraction": {"input": raw_snapshot(raw_coefficient),
                                       "numerator": numerator, "denominator": denominator,
                                       "output": output}})
        return value

    def joint_init(obj, arity, terms):
        nonlocal constructor, constructed_object
        tick()
        frame = sys._getframe(1)
        if (constructor is not None or frame.f_code is not original_joint.__code__
                or frame.f_globals is not vars(model) or type(terms) is not tuple):
            raise ValueError("Joint constructor is outside the bound joint helper")
        supplied = [row_snapshot(atoms, coefficient) for atoms, coefficient in terms]
        input_refs = [token(term) for term in terms]
        original_init(obj, arity, terms)
        if obj.terms is not terms or obj.arity is not arity:
            raise ValueError("Joint constructor did not retain the supplied fields")
        constructor = {"arity": arity, "stored_arity": obj.arity,
                       "input_terms": supplied, "output_terms": joint_snapshot(obj, row_limit),
                       "input_tuple_ref": token(terms), "output_tuple_ref": token(obj.terms),
                       "input_refs": input_refs, "output_refs": [token(term) for term in obj.terms]}
        constructed_object = obj
        return None

    def joint_call(parsed, *, arity):
        nonlocal parsed_rows, joint_value
        tick()
        frame = sys._getframe(1)
        bind(frame)
        if (parsed_rows is not None or parsed is not frame.f_locals["parsed"]
                or type(parsed) is not list or len(parsed) != len(raw_rows)
                or len(row_calls) != len(raw_rows) or arity != 2):
            raise ValueError("joint operand is not the complete observed parser list")
        for term, pending in zip(parsed, retained):
            coefficient, atoms = term
            if (coefficient is not pending["coefficient"] or type(atoms) is not tuple
                    or len(atoms) != 2
                    or any(g is not seen[0] for g, seen in zip(atoms, pending["graphs"]))):
                raise ValueError("parsed terms do not bind actual constructor returns")
        parsed_rows = [row_snapshot(atoms, coefficient) for coefficient, atoms in parsed]
        joint_value = original_joint(parsed, arity=arity)
        tick()
        if constructor is None or joint_value is not constructed_object:
            raise ValueError("joint return does not bind its observed constructor")
        return joint_value

    exit_observation = {"returned": False, "exception_type": None}
    with ExitStack() as restoration:
        restoration.enter_context(patch.object(source, "Config", config_call))
        restoration.enter_context(patch.object(source, "Fraction", fraction_call))
        restoration.enter_context(patch.object(source, "joint", joint_call))
        restoration.enter_context(patch.object(Joint, "__init__", joint_init))
        try:
            returned = source.admit(document)
            if returned is not joint_value:
                raise ValueError("admit return differs from its constructed Joint")
            exit_observation["returned"] = True
        except source.JointRestrictionAdmission as exc:
            # Retain the observed exception identity only after a complete
            # prefix. It is not a formal product-outcome classification.
            if parsed_rows is None or constructor is None:
                raise
            exit_observation["exception_type"] = type(exc).__module__ + "." + type(exc).__qualname__
    if (parsed_rows is None or constructor is None or len(row_calls) != len(raw_rows)
            or _manifest() != manifest or raw_snapshot(document) != before
            or bindings != (source.admit, source.joint, Config.__init__, Joint.__init__)
            or sys.getprofile() is not None or sys.gettrace() is not None
            or threading.active_count() != 1):
        raise ValueError("incomplete or unstable native admission prefix")
    packet = {"edition": EDITION, "input_rows": before["rows"], "row_calls": row_calls,
              "parsed_rows": parsed_rows, "constructor": constructor,
              "observed_admit_exit": exit_observation, "manifest": manifest,
              "calls": calls, "limits": {"rows": row_limit, "calls": call_limit, "bytes": byte_limit},
              "native_dispatch_and_denotation": "trusted/open"}
    if len(json.dumps(packet, ensure_ascii=False).encode()) > byte_limit:
        raise ObservationLimit("complete admission packet byte limit")
    return packet
