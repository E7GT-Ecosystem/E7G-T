"""Capture the actual parser inputs of one selected normal IR execution.

Instrumentation is observer-only and restores bindings on every exit. It is
intended for an isolated verification process with stable native bindings;
the lock rejects overlapping instrumented captures, not arbitrary external
threads. No expected partition, Trace or semantic checker is consulted.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from unittest.mock import patch

import e7_ir_eecq_two_stage_b1 as ir


_capture_lock = Lock()


@dataclass(frozen=True)
class ExecutionCapture:
    result: dict
    transitions: tuple
    nested: bytes
    outer: bytes

    def __post_init__(self):
        if type(self.nested) is not bytes or type(self.outer) is not bytes:
            raise ValueError("native immutable serializer returns required")


def capture_execution(package):
    """Retain bytes returned to the exact outer/nested parse call sites.

    Identity binding is operation-local: the parser must receive the very
    bytes object returned by its serializer, exactly once. The native parser,
    codecs, scheduler, copies and emitters remain trusted host operations.
    An exceptional/interrupted execution produces no successful capture.
    """
    if not _capture_lock.acquire(blocking=False):
        raise ValueError("overlapping capture is unsupported")
    outer_returns, nested_returns = [], []
    outer_inputs, nested_inputs = [], []
    transitions = []
    native_serialize, native_parse = ir.serialize, ir.parse
    native_nested_serialize, native_nested_parse = ir.serialize_first, ir.parse_first

    def serialize(value):
        encoded = native_serialize(value)
        if type(encoded) is not bytes:
            raise ValueError("outer serializer did not return bytes")
        outer_returns.append(encoded)
        return encoded

    def serialize_nested(value):
        encoded = native_nested_serialize(value)
        if type(encoded) is not bytes:
            raise ValueError("nested serializer did not return bytes")
        nested_returns.append(encoded)
        return encoded

    def parse(encoded):
        if len(outer_returns) != 1 or encoded is not outer_returns[0] or outer_inputs:
            raise ValueError("outer parser input is not its unique serializer return")
        outer_inputs.append(encoded)
        return native_parse(encoded)

    def parse_nested(encoded):
        if len(nested_returns) != 1 or encoded is not nested_returns[0] or nested_inputs:
            raise ValueError("nested parser input is not its unique serializer return")
        nested_inputs.append(encoded)
        return native_nested_parse(encoded)

    try:
        with patch.multiple(ir, serialize=serialize, parse=parse,
                            serialize_first=serialize_nested, parse_first=parse_nested):
            result = ir.execute(package, _transition_sink=transitions.append)
        if tuple(map(len, (outer_returns, outer_inputs, nested_returns, nested_inputs))) != (1, 1, 1, 1):
            raise ValueError("incomplete or repeated parser/serializer capture")
        return ExecutionCapture(result, tuple(transitions), nested_inputs[0], outer_inputs[0])
    finally:
        _capture_lock.release()
