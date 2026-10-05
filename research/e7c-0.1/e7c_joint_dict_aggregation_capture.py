"""Capture the pinned ``joint`` loop's CPython dictionary-add trace.

The original helper runs directly. ``sys.settrace`` records statement-boundary
dictionary states; ``sys.setprofile`` records actual ``dict.get``, Fraction
addition/truth, and Joint-constructor frame events. This is finite evidence,
not an interpreter or a universal CPython adequacy proof.
"""
from __future__ import annotations

import json
import sys
import threading
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint
from e7c_joint_admission_operation_capture import _value
from e7c_joint_first_helper_sites import checked_sites

EDITION = "E7C-native-joint-dictionary-trace/0.2-provisional"
EVENT_LIMIT = 20000
BYTE_LIMIT = 4_000_000
_JOINT_CODE = joint.__code__
_FRACTION_ADD = Fraction.__add__.__code__
_FRACTION_BOOL = Fraction.__bool__.__code__
_FRACTION_NEW = Fraction.__new__.__code__
_JOINT_INIT = Joint.__init__.__code__
_JOINT_POST_INIT = Joint.__post_init__.__code__


def _entries(totals):
    if type(totals) is not dict:
        raise ValueError("joint accumulator is not a built-in dictionary")
    result = []
    for key, coefficient in totals.items():
        if (type(key) is not tuple or len(key) != 2
                or any(type(atom) is not Config for atom in key)
                or type(coefficient) is not Fraction):
            raise ValueError("unsupported dictionary entry")
        result.append({"key": _value(key), "coefficient": _value(coefficient)})
    return result


def _row_locals(frame):
    local = frame.f_locals
    row = local.get("row")
    if (type(row) is not tuple or len(row) != 2
            or type(row[0]) is not Fraction or type(row[1]) is not tuple
            or len(row[1]) != 2 or any(type(atom) is not Config for atom in row[1])):
        raise ValueError("joint loop row is outside the selected binary carrier")
    return {"coefficient": _value(row[0]), "key": _value(row[1])}


def capture(terms):
    """Run pinned ``joint(terms, arity=2)`` and return its ordered event receipt."""
    checked_sites()
    if (sys.getprofile() is not None or sys.gettrace() is not None
            or threading.active_count() != 1):
        raise ValueError("isolated uninstrumented host required")
    if type(terms) is not list or len(terms) > 256:
        raise ValueError("finite binary term list required")
    # Validate the capture boundary only; the pinned function still performs
    # its own runtime checks and may reject the supplied list.
    for row in terms:
        if (type(row) is not tuple or len(row) != 2
                or type(row[0]) is not Fraction or type(row[1]) is not tuple
                or len(row[1]) != 2 or any(type(atom) is not Config for atom in row[1])):
            raise ValueError("capture accepts exact binary Joint terms only")

    events = []
    dictionary_transitions = []
    states = {}
    failed = False

    def record(event):
        nonlocal failed
        if len(events) >= EVENT_LIMIT:
            failed = True
            raise ValueError("joint trace event limit")
        events.append(event)

    def trace(frame, event, arg):
        nonlocal failed
        if frame.f_code is not _JOINT_CODE:
            return None
        key = id(frame)
        if event == "call":
            frame.f_trace_lines = True
            states[key] = {"index": 0, "pending": None}
            record({"site": "joint", "phase": "call",
                    "rows": _value(frame.f_locals["rows"]),
                    "arity": _value(frame.f_locals["arity"])})
            return trace
        ctx = states.get(key)
        if ctx is None:
            failed = True
            raise ValueError("joint frame state disappeared")
        if event == "line" and frame.f_lineno == 55:
            if ctx["pending"] is not None:
                failed = True
                raise ValueError("overlapping dictionary assignments")
            row = _row_locals(frame)
            before = _entries(frame.f_locals["totals"])
            ctx["pending"] = {"row": row, "before": before,
                              "lookup_result": None,
                              "addition_result": None,
                              "dict_get_call": False}
            record({"site": "dictionary-row", "phase": "before-update",
                    "index": ctx["index"], "row": row, "entries": before})
        elif (event == "line" and ctx["pending"] is not None
              and frame.f_lineno in (43, 56)):
            pending = ctx["pending"]
            if (pending["lookup_result"] is None
                    or pending["addition_result"] is None
                    or not pending["dict_get_call"]):
                failed = True
                raise ValueError("dictionary operation result receipt incomplete")
            after = _entries(frame.f_locals["totals"])
            dictionary_transitions.append({
                "index": ctx["index"], "row": pending["row"],
                "before": pending["before"],
                "lookup_result": pending["lookup_result"],
                "addition_result": pending["addition_result"],
                "dict_get_call": True, "after": after})
            record({"site": "dictionary-row", "phase": "after-update",
                    "index": ctx["index"],
                    "row": pending["row"], "entries": after})
            ctx["pending"] = None
            ctx["index"] += 1
        elif event == "return":
            if ctx["pending"] is not None:
                pending = ctx["pending"]
                if (pending["lookup_result"] is None
                        or pending["addition_result"] is None
                        or not pending["dict_get_call"]):
                    failed = True
                    raise ValueError("dictionary operation result receipt incomplete")
                after = _entries(frame.f_locals["totals"])
                dictionary_transitions.append({
                    "index": ctx["index"], "row": pending["row"],
                    "before": pending["before"],
                    "lookup_result": pending["lookup_result"],
                    "addition_result": pending["addition_result"],
                    "dict_get_call": True, "after": after})
                record({"site": "dictionary-row", "phase": "after-update",
                        "index": ctx["index"],
                        "row": pending["row"], "entries": after})
            record({"site": "joint", "phase": "return", "value": _value(arg)})
            del states[key]
        return trace

    def profile(frame, event, arg):
        nonlocal failed
        if event == "call" and frame.f_code is _FRACTION_NEW:
            parent = frame.f_back
            if parent is not None and parent.f_code is _JOINT_CODE and parent.f_lineno == 55:
                record({"site": "Fraction(0)-default", "phase": "call",
                        "numerator": _value(frame.f_locals["numerator"]),
                        "denominator": _value(frame.f_locals["denominator"])})
        if event in ("call", "return") and frame.f_code is _FRACTION_ADD:
            parent = frame.f_back
            if parent is not None and parent.f_code is _JOINT_CODE:
                context = states.get(id(parent))
                pending = context.get("pending") if context is not None else None
                if pending is not None:
                    if event == "call":
                        if pending["lookup_result"] is not None:
                            failed = True
                            raise ValueError("duplicate Fraction addition call")
                        pending["lookup_result"] = _value(frame.f_locals["a"])
                    else:
                        if pending["addition_result"] is not None:
                            failed = True
                            raise ValueError("duplicate Fraction addition return")
                        pending["addition_result"] = _value(arg)
                payload = {"site": "Fraction.add", "phase": event,
                           "left": _value(frame.f_locals["a"]),
                           "right": _value(frame.f_locals["b"])}
                if event == "return":
                    payload["result"] = _value(arg)
                record(payload)
        if event in ("call", "return") and frame.f_code is _FRACTION_BOOL:
            parent = frame.f_back
            if (parent is not None and parent.f_code.co_name == "<genexpr>"
                    and parent.f_back is not None and parent.f_back.f_code is _JOINT_CODE):
                payload = {"site": "Fraction.truth-filter", "phase": event,
                           "coefficient": _value(frame.f_locals["a"])}
                if event == "return":
                    payload["result"] = _value(arg)
                record(payload)
        if event in ("c_call", "c_return") and frame.f_code is _JOINT_CODE:
            method = getattr(arg, "__name__", None)
            receiver = getattr(arg, "__self__", None)
            if method == "get" and receiver is frame.f_locals.get("totals"):
                context = states.get(id(frame))
                pending = context.get("pending") if context is not None else None
                if event == "c_call" and pending is not None:
                    pending["dict_get_call"] = True
                record({"site": "dict.get", "phase": event,
                        "key": _value(frame.f_locals["atoms"]),
                        "entries": _entries(receiver)})
        if event == "call" and frame.f_code is _JOINT_INIT:
            record({"site": "Joint.constructor", "phase": "call",
                    "arity": _value(frame.f_locals["arity"]),
                    "terms": _value(frame.f_locals["terms"])})
        if event in ("call", "return") and frame.f_code is _JOINT_POST_INIT:
            payload = {"site": "Joint.validation", "phase": event}
            if event == "return":
                payload["value"] = _value(frame.f_locals["self"])
            record(payload)

    old_profile, old_trace = sys.getprofile(), sys.gettrace()
    old_joint, old_joint_cls = joint, Joint
    try:
        sys.settrace(trace)
        sys.setprofile(profile)
        result = joint(terms, arity=2)
    finally:
        sys.setprofile(old_profile)
        sys.settrace(old_trace)
    if failed or states:
        raise ValueError("incomplete joint operation trace")
    if joint is not old_joint or Joint is not old_joint_cls:
        raise ValueError("pinned Joint binding changed during capture")
    packet = {"edition": EDITION, "python": sys.version,
              "input": _value(terms), "events": events,
              "dictionary_transitions": dictionary_transitions,
              "returned": _value(result),
              "adequacy": "bounded profile/trace observation; operation semantics open"}
    if len(json.dumps(packet, ensure_ascii=False).encode()) > BYTE_LIMIT:
        raise ValueError("joint trace byte limit")
    return packet
