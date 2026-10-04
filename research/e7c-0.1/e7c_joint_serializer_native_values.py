"""Native value/host checks adapted from the #160 serializer observer.

Snapshot and runtime/code checks are trusted denotation and identity evidence,
not parser/constructor adequacy or proof of native execution provenance.
"""
import ast
import hashlib
import json
import marshal
import math
import platform
import sys
import types
from fractions import Fraction
from pathlib import Path

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_serializer_source import ROOT, check

EDITION = "E7C-native-serializer-host/0.1-provisional"
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


def validate_input_literals(rows):
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
