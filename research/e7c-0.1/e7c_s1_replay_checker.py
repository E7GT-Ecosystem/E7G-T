"""Separate S1 replay: no import or invocation of the S1 evaluator."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from e7c_s1_state_joint_static import EDITION, check_document
from e7c_s1_values import (CANONICAL_BLOB, FG3_BLOB, RuntimeAdmissionError,
                           admit_values, encode_value, key, resource_policy)

WITNESS_EDITION = "E7C-S1-FG3-REPLAY/0.1-provisional"


class ReplayError(ValueError):
    pass


class _Limit(Exception):
    pass


def _same(left: Any, right: Any) -> bool:
    """Compare JSON trees without treating true as 1 or false as 0."""
    if type(left) is not type(right):
        return False
    if type(right) is dict:
        return set(left) == set(right) and all(_same(left[k], right[k]) for k in right)
    if type(right) is list:
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    return left == right


def _reduce(rows: list[tuple[tuple, Fraction]]) -> tuple:
    """Independent finite formal sum and cancellation for replay results."""
    amounts: dict[tuple, Fraction] = {}
    for atoms, coefficient in rows:
        if atoms in amounts:
            amounts[atoms] += coefficient
        else:
            amounts[atoms] = coefficient
    support = [(atoms, c) for atoms, c in amounts.items() if c != 0]
    support.sort(key=lambda item: tuple(key(atom) for atom in item[0]))
    return tuple(support)


def check_witness(witness: Any) -> bool:
    fields = {"witness_edition", "calculus_edition", "canonical_blob", "fg3_blob",
              "document", "values", "resource_policy", "static", "terminal", "ledger", "progress"}
    if type(witness) is not dict or set(witness) != fields:
        raise ReplayError("wrong witness shape")
    if (witness["witness_edition"] != WITNESS_EDITION or witness["calculus_edition"] != EDITION
            or witness["canonical_blob"] != CANONICAL_BLOB or witness["fg3_blob"] != FG3_BLOB):
        raise ReplayError("wrong edition or source pins")
    doc = witness["document"]
    static = check_document(doc)
    if static["status"] != "ok" or not _same(witness["static"], static):
        raise ReplayError("static typing does not replay")
    try:
        variables = admit_values(doc, witness["values"])
        beta = resource_policy(witness["resource_policy"])
    except (RuntimeAdmissionError, ValueError) as error:
        raise ReplayError("invalid typed inputs or bounds") from error
    charges = {"steps": 0, "pair_visits": 0}
    recorded: list[dict[str, Any]] = []

    def enter() -> None:
        if charges["steps"] >= beta["max_steps"]:
            raise _Limit("max_steps")
        charges["steps"] += 1

    def examine() -> None:
        if charges["pair_visits"] >= beta["max_pair_visits"]:
            raise _Limit("max_pair_visits")
        charges["pair_visits"] += 1

    def derive(node: dict[str, Any]) -> tuple[int, tuple]:
        enter()
        if node["tag"] == "var":
            return variables[node["name"]]
        if node["tag"] == "independent":
            la, ls = derive(node["left"])
            ra, rs = derive(node["right"])
            if (la, ra) != (1, 1):
                raise ReplayError("static/runtime mismatch")
            rows = []
            for atoms_l, n_l in ls:
                for atoms_r, n_r in rs:
                    examine()
                    rows.append((atoms_l + atoms_r, n_l * n_r))
            normalized = _reduce(rows)
            recorded.append({"rule": "independent", "visits": len(ls) * len(rs), "support": len(normalized)})
            return 2, normalized
        arity, rows = derive(node["arg"])
        coordinate = node["coordinate"]
        selected = []
        for atoms, amount in rows:
            examine()
            selected.append(((atoms[coordinate],), amount))
        normalized = _reduce(selected)
        recorded.append({"rule": "marginal", "coordinate": coordinate,
                         "visits": len(rows), "support": len(normalized)})
        return 1, normalized

    try:
        rank, result = derive(doc["term"])
        expected = {"tag": "success", "value": encode_value(rank, result)}
    except _Limit as error:
        expected = {"tag": "resource_exhausted", "bound": str(error), "value": None}
    if (not _same(witness["terminal"], expected) or not _same(witness["ledger"], recorded)
            or not _same(witness["progress"], charges)):
        raise ReplayError("terminal result, ordered ledger or progress differs from replay")
    return True
