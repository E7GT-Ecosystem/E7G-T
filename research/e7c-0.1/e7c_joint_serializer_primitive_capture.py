"""Capture native serializer reads, helper entries and exact list operands.

The original helper code executes. Forwarding hooks call each original read
and list operation once and retain its returned operands. Successful packets
are observations, not kernel certificates or universal CPython adequacy.
Use only in an isolated verification process; native tracing and denotation
remain trusted. No expected helper output or semantic row plan is computed.
"""
from contextlib import ExitStack
from threading import Lock
from unittest.mock import patch
import builtins
import json
import sys
import threading

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint
from fractions import Fraction
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_serializer_native_values import (
    HELPERS, NATIVE_LIST, ObservationLimit, freeze_manifest, graph_snapshot,
    joint_snapshot, raw_snapshot, row_snapshot,
)

EDITION = "E7C-native-serializer-primitives/0.1-provisional"
_lock = Lock()


def capture(value, *, row_limit=64, event_limit=1200, byte_limit=262144):
    """A normal return binds all observed helper arguments/read/copy operands.

    Limits concern retained evidence, not native allocation or EEC-Q budgets.
    An exception, missing read/call, equal-but-rebound operand or interruption
    yields no successful packet. Hooks and profiler are restored on every exit.
    """
    if not _lock.acquire(blocking=False):
        raise ValueError("overlapping primitive capture is unsupported")
    try:
        return _capture(value, row_limit, event_limit, byte_limit)
    finally:
        _lock.release()


def _capture(value, row_limit, event_limit, byte_limit):
    if (any(type(n) is not int or n < 0 for n in (row_limit, event_limit, byte_limit))
            or row_limit > 64):
        raise ValueError("invalid primitive observation limits")
    if (sys.getprofile() is not None or sys.gettrace() is not None
            or threading.active_count() != 1):
        raise ValueError("isolated uninstrumented host required")
    if builtins.list is not NATIVE_LIST:
        raise ValueError("native list binding changed")
    manifest = freeze_manifest()
    before = joint_snapshot(value, row_limit)
    if len(json.dumps(before, ensure_ascii=False).encode()) > byte_limit:
        raise ObservationLimit("input snapshot limit")
    classes = (Config, Fraction, Joint)
    originals = {cls: cls.__getattribute__ for cls in classes}
    if any(original is not object.__getattribute__ for original in originals.values()):
        raise ValueError("selected objects require ordinary attribute dispatch")
    helpers = {getattr(source, name).__code__: name for name in HELPERS}
    helper_bindings = tuple(getattr(source, name) for name in HELPERS)
    events, copies, stack, retained, tokens = [], [], [], [], {}
    muted, completed, failed = False, False, False

    def token(obj):
        identity = id(obj)
        if identity not in tokens:
            tokens[identity] = (obj, len(tokens) + 1)
        elif tokens[identity][0] is not obj:
            raise ValueError("native object token reused")
        return tokens[identity][1]

    def record(site, payload):
        nonlocal failed
        if len(events) >= event_limit:
            failed = True
            raise ObservationLimit("primitive event limit")
        events.append({"site": site, "payload": raw_snapshot(payload)})

    def current(frame, helper):
        if not stack or stack[-1]["frame"] is not frame or stack[-1]["helper"] != helper:
            raise ValueError("primitive is outside its bound helper frame")
        return stack[-1]

    def native_read(cls):
        original = originals[cls]
        selected = {Config: {"edges", "tag"}, Fraction: {"numerator", "denominator"},
                    Joint: {"arity", "terms"}}[cls]

        def read(obj, name):
            returned = original(obj, name)
            caller = sys._getframe(1)
            if muted or name not in selected or caller.f_code not in helpers:
                return returned
            helper = helpers[caller.f_code]
            expected = {Config: "_graph", Fraction: "_row", Joint: "rows"}[cls]
            if helper != expected or type(obj) is not cls:
                raise ValueError("attribute read has an unsupported receiver/site")
            ctx = current(caller, helper)
            receiver = caller.f_locals[{Config: "g", Fraction: "coefficient", Joint: "value"}[cls]]
            if obj is not receiver or name in ctx["reads"]:
                raise ValueError("repeated or rebound attribute receiver")
            if cls is Joint:
                required = "arity" if not ctx["reads"] else "terms"
                if name != required:
                    raise ValueError("Joint attribute order changed")
                if name == "arity":
                    if type(returned) is not int or returned != 2:
                        raise ValueError("binary native arity required")
                    payload = returned
                else:
                    if type(returned) is not tuple:
                        raise ValueError("native terms tuple required")
                    ctx["terms"] = returned  # exact object used by the running comprehension
                    payload = joint_snapshot(obj, row_limit)
            elif cls is Config:
                required = "edges" if not ctx["reads"] else "tag"
                if name != required or (name == "tag" and not ctx["copied"]):
                    raise ValueError("graph read/copy order changed")
                if name == "edges":
                    if type(returned) is not tuple or any(type(x) is not str for x in returned):
                        raise ValueError("exact native edge tuple required")
                    ctx["edges"] = returned
                    payload = [edge for edge in returned]
                else:
                    if returned is not None and type(returned) is not str:
                        raise ValueError("native optional string tag required")
                    payload = returned
            else:
                required = "numerator" if not ctx["reads"] else "denominator"
                if name != required or ctx["graphs"] != 2 or type(returned) is not int:
                    raise ValueError("fraction read order or representation changed")
                payload = returned
            ctx["reads"].append(name)
            retained.append(returned)
            record(helper + "." + name, payload)
            return returned

        return read

    def native_list(operand):
        frame = sys._getframe(1)
        ctx = current(frame, "_graph")
        if (type(operand) is not tuple or operand is not ctx.get("edges")
                or ctx["reads"] != ["edges"] or ctx["copied"]):
            raise ValueError("list operand is not its unique actual edge read")
        record("list.call", [edge for edge in operand])
        returned = NATIVE_LIST(operand)
        if (type(returned) is not list or len(returned) != len(operand)
                or any(a is not b for a, b in zip(operand, returned))):
            raise ValueError("native list copy did not retain every operand cell")
        copies.append({"input_refs": [token(x) for x in operand],
                       "output_refs": [token(x) for x in returned]})
        retained.extend((operand, returned))
        ctx["copied"] = True
        record("list.return", returned)
        return returned

    def profile(frame, event, returned):
        nonlocal muted, completed, failed
        if muted or failed or frame.f_code not in helpers or event not in ("call", "return"):
            return
        # The pinned helpers return containers on every normal path. Preserve
        # an exception already unwinding through a return callback.
        if event == "return" and returned is None:
            failed = True
            return
        helper = helpers[frame.f_code]
        if frame.f_globals is not vars(source):
            raise ValueError("helper global binding changed")
        muted = True
        try:
            if event == "call":
                ctx = {"frame": frame, "helper": helper, "reads": []}
                if helper == "rows":
                    if stack or completed or frame.f_locals["value"] is not value:
                        raise ValueError("repeated or rebound root call")
                    ctx.update(terms=None, rows=0)
                    payload = joint_snapshot(value, row_limit)
                elif helper == "_row":
                    if not stack or stack[-1]["helper"] != "rows":
                        raise ValueError("row call is outside rows")
                    parent = stack[-1]
                    terms, index = parent["terms"], parent["rows"]
                    if terms is None or index >= len(terms):
                        raise ValueError("row call is outside observed term iteration")
                    atoms, coefficient = frame.f_locals["atoms"], frame.f_locals["coefficient"]
                    term = terms[index]
                    if type(term) is not tuple or len(term) != 2 or atoms is not term[0] or coefficient is not term[1]:
                        raise ValueError("row arguments do not bind the next observed term")
                    parent["rows"] += 1
                    ctx.update(atoms=atoms, graphs=0)
                    payload = row_snapshot(atoms, coefficient)
                else:
                    if not stack or stack[-1]["helper"] != "_row":
                        raise ValueError("graph call is outside a row")
                    parent = stack[-1]
                    index, graph = parent["graphs"], frame.f_locals["g"]
                    if index >= 2 or graph is not parent["atoms"][index]:
                        raise ValueError("graph argument does not bind the next observed coordinate")
                    parent["graphs"] += 1
                    ctx.update(copied=False, edges=None)
                    payload = graph_snapshot(graph)
                stack.append(ctx)
                record(helper + ".call", payload)
            else:
                ctx = current(frame, helper)
                required = {"rows": ["arity", "terms"], "_row": ["numerator", "denominator"],
                            "_graph": ["edges", "tag"]}[helper]
                if ctx["reads"] != required:
                    raise ValueError("incomplete native attribute capture")
                if helper == "rows" and (ctx["terms"] is None or ctx["rows"] != len(ctx["terms"])):
                    raise ValueError("incomplete native row iteration capture")
                if helper == "_row" and ctx["graphs"] != 2:
                    raise ValueError("incomplete native graph iteration capture")
                if helper == "_graph" and not ctx["copied"]:
                    raise ValueError("missing native list operation")
                record(helper + ".return", raw_snapshot(returned))
                stack.pop()
                completed = helper == "rows"
        finally:
            muted = False

    previous_profile = sys.getprofile()
    with ExitStack() as restoration:
        for cls in classes:
            restoration.enter_context(patch.object(cls, "__getattribute__", native_read(cls)))
        restoration.enter_context(patch.object(source, "list", native_list, create=True))
        try:
            sys.setprofile(profile)
            returned = source.rows(value)
        finally:
            sys.setprofile(previous_profile)
    if stack or not completed:
        raise ValueError("no complete native normal-return capture")
    if (freeze_manifest() != manifest or joint_snapshot(value, row_limit) != before
            or any(getattr(source, name) is not old for name, old in zip(HELPERS, helper_bindings))
            or any(cls.__getattribute__ is not original for cls, original in originals.items())
            or threading.active_count() != 1 or sys.gettrace() is not None):
        raise ValueError("postflight binding/input stability check failed")
    packet = {"edition": EDITION, "input": before, "output": raw_snapshot(returned),
              "events": events, "copies": copies, "manifest": manifest,
              "limits": {"rows": row_limit, "events": event_limit, "bytes": byte_limit},
              "native_dispatch_and_capture_adequacy": "trusted/open"}
    if len(json.dumps(packet, ensure_ascii=False).encode()) > byte_limit:
        raise ObservationLimit("complete primitive packet byte limit")
    return packet
