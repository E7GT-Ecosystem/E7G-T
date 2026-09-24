"""One fixture-bound FG3 configuration carried through the provisional var IR.

This bridge admits one selected graph as an opaque Sigma-A configuration. It
does not encode FG3 states or their operations in the B1 calculus.
"""

from __future__ import annotations

import copy
from fractions import Fraction

from adapters.eec_q_fg3_b1 import translate_rows
from e7_ir_var_b1 import execute, lower, parse, serialize
from e7c_b1_canonical import canonical_key, digest
from e7c_b1_evaluator import evaluate
from e7c_b1_replay_checker import check_witness
from test_wp3_i import VAR, document

BRIDGE_EDITION = "WP5-IR-FG3-SINGLE-CONFIG/0.1-provisional"
ROWS = [
    {"config": {"edges": ["AB"], "tag": None},
     "coefficient": {"numerator": 1, "denominator": 2}},
    {"config": {"edges": ["AB", "AB"], "tag": None},
     "coefficient": {"numerator": 1, "denominator": 2}},
]


def conventional_baseline(rows):
    """Plain finite rational collection; no adapter, IR or E7C imports used."""
    totals = {}
    for row in rows:
        assert set(row) == {"config", "coefficient"}
        graph, rational = row["config"], row["coefficient"]
        assert set(graph) == {"edges", "tag"}
        assert all(edge in {"AB", "AC", "BC"} for edge in graph["edges"])
        assert graph["tag"] is None or isinstance(graph["tag"], str)
        assert type(rational["numerator"]) is int
        assert type(rational["denominator"]) is int and rational["denominator"] > 0
        key = (tuple(sorted(set(graph["edges"]))), graph["tag"])
        totals[key] = totals.get(key, Fraction(0)) + Fraction(
            rational["numerator"], rational["denominator"])
    surviving = [(key, value) for key, value in totals.items() if value]
    assert len(surviving) == 1 and surviving[0][1] == 1
    (edges, tag), coefficient = surviving[0]
    return {"config": {"edges": list(edges), "tag": tag},
            "coefficient": {"numerator": coefficient.numerator,
                            "denominator": coefficient.denominator}}


def source_package(config):
    """Instantiate the existing complete B1 test package with one graph value."""
    source = document(VAR)
    old = {"id": "a", "valid": True}

    def substitute(value):
        if value == old:
            return copy.deepcopy(config)
        if isinstance(value, dict):
            return {key: substitute(item) for key, item in value.items()}
        if isinstance(value, list):
            return [substitute(item) for item in value]
        return value

    source = substitute(source)
    interpretation = source["interpretation"]
    retained = interpretation["restrictions"]["select_J"]["retained_keys"]
    retained[retained.index(canonical_key(old))] = canonical_key(config)
    for carrier in interpretation["carriers"].values():
        carrier.sort(key=canonical_key)
    for entry in ("source_family", "source_fibre"):
        source["values"][entry].sort(key=canonical_key)
    for family in ("maps", "views", "criteria"):
        for declaration in interpretation[family].values():
            declaration["cases"].sort(key=lambda case: canonical_key(case["input"]))
    interpretation["restrictions"]["select_J"]["retained_keys"].sort()
    interpretation["reconstructions"]["exact_reconstruction"]["carrier"].sort(key=canonical_key)
    return source


def build_case():
    rows = copy.deepcopy(ROWS)
    baseline = conventional_baseline(rows)
    state = translate_rows(rows)
    assert len(state.terms) == 1
    graph, coefficient = state.terms[0]
    config = {"edges": list(graph.edges), "tag": graph.tag}
    assert config == baseline["config"] and coefficient == 1
    source = source_package(config)
    result = evaluate(source)
    ir = lower(source)
    ir_result = execute(ir)
    assert check_witness(result["witness"])["status"] == "accepted"
    assert parse(serialize(ir)) == ir
    assert ir["instruction"]["source_location"]["document"] == digest(source)
    assert result["terminal_outcome"]["value"] == ir_result["terminal_outcome"]["value"] == config
    assert result["ordered_ledger"] == ir_result["ordered_ledger"]
    assert result["resource_progress"] == ir_result["resource_progress"]
    assert result["terminal_outcome"]["optional_witness"] == result["witness"]["identity"]["witness_identifier"]
    assert ir_result["terminal_outcome"]["optional_witness"] is None
    return {"bridge_edition": BRIDGE_EDITION, "profile_rows": rows,
            "conventional_baseline": baseline, "selected_config": config,
            "source_document": source, "source_result": result,
            "ir": ir, "ir_result": ir_result}
