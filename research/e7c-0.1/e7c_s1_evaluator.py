"""Bounded S1 finite FG3 product/marginal evaluator and inline trace emitter."""

from __future__ import annotations

import copy
from fractions import Fraction
from typing import Any

from e7c_s1_state_joint_static import EDITION, check_document
from e7c_s1_values import (CANONICAL_BLOB, FG3_BLOB, RuntimeAdmissionError,
                           admit_values, canonical, encode_value, resource_policy)

WITNESS_EDITION = "E7C-S1-FG3-REPLAY/0.1-provisional"


class _Bound(Exception):
    pass


def evaluate(document: Any, values: Any, bounds: Any) -> dict[str, Any]:
    """Static and value admission precede execution; exhaustion returns no value."""
    static = check_document(document)
    if static["status"] != "ok":
        raise RuntimeAdmissionError(f"static rejection: {static['diagnostic']}")
    inputs = admit_values(document, values)
    policy = resource_policy(bounds)
    steps = visits = 0
    ledger: list[dict[str, Any]] = []

    def charge_step() -> None:
        nonlocal steps
        if steps == policy["max_steps"]:
            raise _Bound("max_steps")
        steps += 1

    def visit() -> None:
        nonlocal visits
        if visits == policy["max_pair_visits"]:
            raise _Bound("max_pair_visits")
        visits += 1

    def run(term: dict[str, Any]) -> tuple[int, tuple]:
        charge_step()
        tag = term["tag"]
        if tag == "var":
            return inputs[term["name"]]
        if tag == "independent":
            left_arity, left = run(term["left"])
            right_arity, right = run(term["right"])
            assert left_arity == right_arity == 1  # guaranteed by S1 typing
            images: list[tuple[tuple, Fraction]] = []
            for (a,), x in left:
                for (b,), y in right:
                    visit()
                    images.append(((a, b), x * y))
            answer = canonical(images, 2)
            ledger.append({"rule": "independent", "visits": len(left) * len(right), "support": len(answer)})
            return 2, answer
        source_arity, source = run(term["arg"])
        i = term["coordinate"]
        assert tag == "marginal" and 0 <= i < source_arity
        rows: list[tuple[tuple, Fraction]] = []
        for atoms, amount in source:
            visit()
            rows.append(((atoms[i],), amount))
        answer = canonical(rows, 1)
        ledger.append({"rule": "marginal", "coordinate": i, "visits": len(source), "support": len(answer)})
        return 1, answer

    try:
        arity, rows = run(document["term"])
        terminal = {"tag": "success", "value": encode_value(arity, rows)}
    except _Bound as error:
        terminal = {"tag": "resource_exhausted", "bound": str(error), "value": None}
    return {
        "witness_edition": WITNESS_EDITION,
        "calculus_edition": EDITION,
        "canonical_blob": CANONICAL_BLOB,
        "fg3_blob": FG3_BLOB,
        "document": copy.deepcopy(document),
        "values": copy.deepcopy(values),
        "resource_policy": copy.deepcopy(policy),
        "static": static,
        "terminal": terminal,
        "ledger": ledger,
        "progress": {"steps": steps, "pair_visits": visits},
    }
