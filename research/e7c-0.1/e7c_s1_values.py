"""Shared S1 finite input admission and canonical data encoding, no dynamics.

The evaluator and checker share only this syntax/codec and the S1 static checker.
They implement product, marginal and resource accounting separately.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from e7c_s1_state_joint_static import parse_type

CANONICAL_BLOB = "a84da2c4de2ada23577cde4512a10c3369aba2b5"
FG3_BLOB = "6c624fcd49b95e473a3e80160979183e8d3b58aa"
MODULE = "E7C-EECQ-FG3-BRIDGE/0.1-provisional"
SIGNATURE = "FG3-graph"
EDGES = frozenset(("AB", "AC", "BC"))
MAX_INPUT_ROWS = 256
MAX_INTEGER_BITS = 512
RESOURCE_EDITION = "E7C-S1-RESOURCE/0.1-provisional"


class RuntimeAdmissionError(ValueError):
    pass


def graph(record: Any) -> tuple[tuple[str, ...], str | None]:
    if type(record) is not dict or set(record) != {"edges", "tag"}:
        raise RuntimeAdmissionError("graph requires edges and tag")
    edges, tag = record["edges"], record["tag"]
    if (type(edges) is not list or any(type(e) is not str or e not in EDGES for e in edges)
            or (tag is not None and type(tag) is not str)):
        raise RuntimeAdmissionError("invalid FG3 graph")
    return tuple(sorted(set(edges))), tag


def coeff(record: Any) -> Fraction:
    if type(record) is not dict or set(record) != {"numerator", "denominator"}:
        raise RuntimeAdmissionError("exact coefficient fields required")
    n, d = record["numerator"], record["denominator"]
    if (type(n) is not int or type(d) is not int or d <= 0
            or abs(n).bit_length() > MAX_INTEGER_BITS or d.bit_length() > MAX_INTEGER_BITS):
        raise RuntimeAdmissionError("bounded exact integer coefficient required")
    return Fraction(n, d)


def key(config: tuple[tuple[str, ...], str | None]) -> tuple:
    edges, tag = config
    return "graph", edges, tag is not None, tag or ""


def canonical(rows: list[tuple[tuple, Fraction]], arity: int) -> tuple:
    totals: dict[tuple, Fraction] = {}
    for atoms, amount in rows:
        if len(atoms) != arity:
            raise RuntimeAdmissionError("wrong row arity")
        totals[atoms] = totals.get(atoms, Fraction(0)) + amount
    return tuple(sorted(((atoms, n) for atoms, n in totals.items() if n),
                        key=lambda item: tuple(key(a) for a in item[0])))


def admit_values(document: Any, values: Any) -> dict[str, tuple[int, tuple]]:
    if type(document) is not dict or type(values) is not dict or set(values) != set(document["variables"]):
        raise RuntimeAdmissionError("values must exactly cover variables")
    result = {}
    for name, ty_json in document["variables"].items():
        ty = parse_type(ty_json)
        if ty.tag == "state" and ty.args == (MODULE, SIGNATURE):
            arity = 1
        elif (ty.tag == "joint" and all(a.args == (MODULE, SIGNATURE) for a in ty.args)):
            arity = len(ty.args)
        else:
            raise RuntimeAdmissionError("runtime only admits FG3 State and Joint variables")
        value = values[name]
        if (type(value) is not dict or set(value) != {"kind", "rows"}
                or value["kind"] != ("state" if arity == 1 else "joint")
                or type(value["rows"]) is not list or len(value["rows"]) > MAX_INPUT_ROWS):
            raise RuntimeAdmissionError("wrong finite value carrier or row bound")
        admitted = []
        for row in value["rows"]:
            if type(row) is not dict or set(row) != {"configs", "coefficient"}:
                raise RuntimeAdmissionError("row requires configs and coefficient")
            configs = row["configs"]
            if type(configs) is not list or len(configs) != arity:
                raise RuntimeAdmissionError("wrong graph tuple arity")
            atoms = tuple(graph(c) for c in configs)
            admitted.append((atoms, coeff(row["coefficient"])))
        result[name] = (arity, canonical(admitted, arity))
    return result


def encode_value(arity: int, rows: tuple) -> dict[str, Any]:
    return {"kind": "state" if arity == 1 else "joint", "rows": [
        {"configs": [{"edges": list(edges), "tag": tag} for edges, tag in atoms],
         "coefficient": {"numerator": n.numerator, "denominator": n.denominator}}
        for atoms, n in rows]}


def resource_policy(value: Any) -> dict[str, int]:
    if (type(value) is not dict or set(value) != {"edition", "max_steps", "max_pair_visits"}
            or value["edition"] != RESOURCE_EDITION
            or any(type(value[k]) is not int or value[k] < 0 or value[k] > 10000
                   for k in ("max_steps", "max_pair_visits"))):
        raise RuntimeAdmissionError("bounded non-negative resource policy required")
    return dict(value)
