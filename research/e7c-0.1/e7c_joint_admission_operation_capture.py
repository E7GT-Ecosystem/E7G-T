"""Capture selected native Python call/return events in pinned ``admit``.

This is finite execution evidence. It runs the original helpers without
wrapping or replacing them and records operation arguments/results at Python
frame boundaries. The profiler, event denotation, CPython adequacy, and
all-input behavior remain trusted/open.
"""
from __future__ import annotations

import json
import sys
import threading
from fractions import Fraction

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_first_helper_sites import checked_sites

EDITION = "E7C-native-admission-operations/0.1-provisional"
EVENT_LIMIT = 12000
BYTE_LIMIT = 2_000_000


def _value(value):
    """Freeze only exact selected runtime objects; never call their repr."""
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is Fraction:
        return {"fraction": [value.numerator, value.denominator]}
    if type(value) is Config:
        return {"config": {"edges": list(value.edges), "tag": value.tag}}
    if type(value) is Joint:
        return {"joint": {"arity": value.arity,
            "terms": [[[_value(atom) for atom in atoms], _value(coefficient)]
                      for atoms, coefficient in value.terms]}}
    if type(value) is tuple:
        return {"tuple": [_value(item) for item in value]}
    if type(value) is list:
        return [_value(item) for item in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: _value(item) for key, item in value.items()}
    raise ValueError("unsupported value at captured operation boundary")


def capture(document):
    """Return a receipt for one actual normal ``source.admit`` execution."""
    checked_sites()
    if (sys.getprofile() is not None or sys.gettrace() is not None
            or threading.active_count() != 1):
        raise ValueError("isolated uninstrumented host required")
    if type(document) is not dict or type(document.get("rows")) is not list:
        raise ValueError("capture requires a raw document with a row list")
    if len(document["rows"]) > source.MAX_ROWS:
        raise ValueError("capture row limit exceeded")

    watched = {
        source.admit.__code__: "admit",
        source._graph.__code__: "_graph",
        source._row.__code__: "_row",
        source.rows.__code__: "rows",
        Config.__init__.__code__: "Config.__init__",
        Config.__post_init__.__code__: "Config.__post_init__",
        Fraction.__new__.__code__: "Fraction.__new__",
        joint.__code__: "joint",
        Joint.__init__.__code__: "Joint.__init__",
        Joint.__post_init__.__code__: "Joint.__post_init__",
    }
    events = []
    failed = False

    def observe(frame, event, arg):
        nonlocal failed
        site = watched.get(frame.f_code)
        if site is None or event not in ("call", "return"):
            return
        if len(events) >= EVENT_LIMIT:
            failed = True
            raise ValueError("admission capture event limit")
        if event == "call":
            local = frame.f_locals
            if site == "admit":
                payload = {"input": _value(local["source"])}
            elif site == "rows":
                payload = {"value": _value(local["value"])}
            elif site == "Fraction.__new__":
                payload = {"numerator": _value(local["numerator"]),
                           "denominator": _value(local["denominator"])}
            elif site == "joint":
                payload = {"rows": _value(local["rows"]),
                           "arity": _value(local["arity"])}
            elif site == "Config.__init__":
                payload = {"edges": _value(local["edges"]),
                           "tag": _value(local["tag"])}
            elif site == "Joint.__init__":
                payload = {"arity": _value(local["arity"]),
                           "terms": _value(local["terms"])}
            elif site in ("_graph", "_row"):
                names = ("g",) if site == "_graph" else ("atoms", "coefficient")
                payload = {key: _value(local[key]) for key in names}
            elif site in ("Config.__post_init__", "Joint.__post_init__"):
                payload = {}
            else:
                raise ValueError("unexpected observed Python event")
        else:
            payload = {"returned": _value(arg)}
            if site in ("Config.__post_init__", "Joint.__post_init__"):
                payload["receiver"] = _value(frame.f_locals["self"])
        events.append({"site": site, "phase": event, "payload": payload})

    old_profile = sys.getprofile()
    old_bindings = (source.admit, source._graph, source._row, source.rows,
                    source.Config, source.Fraction, source.joint)
    try:
        sys.setprofile(observe)
        result = source.admit(document)
    finally:
        sys.setprofile(old_profile)
    if failed:
        raise ValueError("incomplete admission capture")
    if old_bindings != (source.admit, source._graph, source._row, source.rows,
                        source.Config, source.Fraction, source.joint):
        raise ValueError("pinned callable binding changed during capture")
    packet = {"edition": EDITION, "python": sys.version,
              "input": _value(document), "events": events,
              "returned": _value(result),
              "adequacy": "finite CPython profiler receipt; semantics open"}
    if len(json.dumps(packet, ensure_ascii=False).encode()) > BYTE_LIMIT:
        raise ValueError("admission capture byte limit")
    return packet
